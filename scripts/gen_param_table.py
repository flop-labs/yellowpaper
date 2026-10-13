#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["PyYAML>=6.0.0"]
# ///
"""Generate the yellowpaper Appendix A parameter table from the canonical params file.

Single source of truth: `params/flop-protocol-params.yaml`. This script renders every
parameter (enforced + reference-only) into one grouped markdown table and injects it into
`whitepaper/yellowpaper.md` between the GENERATED markers. Each row carries a stable anchor
`<a id="param-<name>">` so prose elsewhere can link `[name](#param-<name>)`.

Usage:
    uv run --script scripts/gen_param_table.py           # rewrite the table in place
    uv run --script scripts/gen_param_table.py --check    # fail (exit 1) if the committed table is stale

Wired into `just verify-whitepaper` so the table can never silently drift from the params file.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("error: PyYAML is required; run with `uv run --script scripts/gen_param_table.py`.")

REPO = Path(__file__).resolve().parent.parent
CANON = REPO / "params" / "flop-protocol-params.yaml"
AUTHORING_YP = REPO / "whitepaper" / "yellowpaper.md"
YP = AUTHORING_YP if AUTHORING_YP.is_file() else REPO / "yellowpaper.md"

BEGIN = "<!-- BEGIN GENERATED: param-table (source: params/flop-protocol-params.yaml via scripts/gen_param_table.py) -->"
END = "<!-- END GENERATED: param-table -->"

_SEC = re.compile(r"§\s*(\d+)(?:\.(\d+))?")
_DID = re.compile(r"\b(D-0*\d+|SPEC-\d+|GOV-[A-Z]|DEC-\d+)\b")

# Category → home yellowpaper section (anchor slug). Used as the default § link for a
# parameter whose own description does not name a section; a `§X.Y` in the description wins.
_CATEGORY_SECTION = {
    "Genesis": "sec-9",
    "Emission & Rewards": "sec-9",
    "Developer Subsidy (separate from block reward)": "sec-9",
    "Staking & Delegation": "sec-6-1",
    "Compute-channel timing bounds": "sec-12-1",
    "Sessions / capacity reservations (A1 anti-spam)": "sec-12-2",
    "Finality-stall safe mode (compute-channel)": "sec-13-0",
    "F2 supply-side governor (default OFF; governance-settable)": "sec-9",
    "Governance": "sec-14-1",
    "Consensus / finality committee": "sec-15-4",
    "Validator security policy": "sec-15-5",
    "Metering tripwire": "sec-4-2",
    "Compute-channel settlement": "sec-12-1",
    "Transaction fees (live values)": "sec-9-1",
    "Data availability": "sec-5-3",
    "Agent wallet / session keys": "sec-6-2",
}


def gh_slug(title: str) -> str:
    """Return the GitHub heading anchor without authoring-repository dependencies."""
    title = re.sub(r"!?\[([^\]]*)\]\([^)]+\)", r"\1", title)
    title = re.sub(r"<[^>]+>", "", title)
    title = re.sub(r"[`*~]", "", title)
    title = re.sub(r"(?<!\w)_{1,2}([^_]+?)_{1,2}(?!\w)", r"\1", title)
    return "".join(
        "-" if char.isspace() else char
        for char in title.lower()
        if char.isalnum() or char in "_-" or char.isspace()
    )


def _section_anchors(doc: str) -> dict[str, str]:
    """Resolve numbered sections to the anchors GitHub actually renders."""
    return {
        match.group(2): gh_slug(match.group(1))
        for match in re.finditer(r"^#{2,4}\s+((\d+(?:\.\d+)*)\b[^\n]*)$", doc, re.MULTILINE)
    }


def _anchor_link(anchor: str, sections: dict[str, str]) -> str:
    major = anchor.removeprefix("sec-").replace("-", ".")
    if major not in sections:
        raise ValueError(f"parameter home §{major} has no yellowpaper heading")
    return f"[§{major}](#{sections[major]})"


def _fmt_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return f"{value:_}"
    return str(value)


def _cell(text: str) -> str:
    """Escape a markdown table cell: no pipes, no newlines."""
    return " ".join(str(text).split()).replace("|", "\\|")


# Code-artifact / evidence references (`Foo.lean::Bar`, `x.qnt`, `y.jl`, trailing `::Sym`). The
# yellowpaper link-checker scans the whole doc for these and fails on any that don't resolve, so the
# generated table must not reproduce them — strip the tokens in place (keeping the human prose).
_ARTIFACT_FILE = re.compile(r"\b[\w/.-]+\.(?:lean|qnt|jl|rs|ts|py)\b")
_ARTIFACT_SYM = re.compile(r"::[\w.']+")


def _strip_artifacts(text: str) -> str:
    text = _ARTIFACT_FILE.sub("", text)
    text = _ARTIFACT_SYM.sub("", text)
    text = re.sub(r"\s+([.,;)])", r"\1", text)  # tidy space left before punctuation
    text = re.sub(r"\(\s*\)", "", text)  # drop emptied parens
    return " ".join(text.split()).strip(" ,;·-")


def _first_sentence(text: str) -> str:
    text = _strip_artifacts(" ".join(str(text).split()))
    # Cut at the first sentence break, but keep decimals / abbreviations intact.
    m = re.search(r"(?<=[a-z0-9)\]%])\.\s+[A-Z]", text)
    if m:
        text = text[: m.start() + 1]
    return text


def _section_link(text: str, sections: dict[str, str]) -> str:
    m = _SEC.search(text or "")
    if not m:
        return ""
    major, minor = m.group(1), m.group(2)
    anchor = f"sec-{major}" + (f"-{minor}" if minor else "")
    return _anchor_link(anchor, sections)


def _decision(param: dict) -> str:
    if param.get("decision"):
        return _cell(param["decision"])
    note = param.get("note") or param.get("description") or ""
    m = _DID.search(note)
    return _cell(m.group(1)) if m else ""


def _categories(raw: str) -> dict[str, str]:
    """Map each param `name` to the nearest preceding `# ---- Category ----` header."""
    cat = "General"
    out: dict[str, str] = {}
    for line in raw.splitlines():
        h = re.match(r"\s*#\s*-{2,}\s*(.+?)\s*-{2,}\s*$", line)
        if h:
            cat = h.group(1).strip()
            continue
        n = re.search(r"\bname:\s*([A-Za-z0-9_]+)", line)
        if n:
            out.setdefault(n.group(1), cat)
    return out


def _row(param: dict, sections: dict[str, str], category: str = "") -> str:
    name = param["name"]
    value = _fmt_value(param["value"])
    unit = param.get("unit", "")
    val = f"{value} {unit}".strip()
    desc = param.get("description") or param.get("note") or ""
    # A section named in the param's own text wins; else fall back to the category's home §.
    sec = _section_link(desc, sections) or (
        _anchor_link(_CATEGORY_SECTION[category], sections) if category in _CATEGORY_SECTION else ""
    )
    return (
        f'| <a id="param-{name}"></a>`{name}` | {_cell(val)} | {sec} | '
        f"{_decision(param)} | {_cell(_first_sentence(desc))} |"
    )


def render() -> str:
    raw = CANON.read_text()
    spec = yaml.safe_load(raw)
    cats = _categories(raw)
    sections = _section_anchors(YP.read_text())

    enforced = spec.get("parameters", [])
    reference = spec.get("reference", [])

    # Preserve YAML order; group by the category comment each param sits under.
    groups: list[tuple[str, list[dict]]] = []
    index: dict[str, list[dict]] = {}
    for p in enforced:
        cat = cats.get(p["name"], "General")
        if cat not in index:
            index[cat] = []
            groups.append((cat, index[cat]))
        index[cat].append(p)

    lines: list[str] = [BEGIN, ""]
    lines.append(
        "Enforced parameters (`params/flop-protocol-params.yaml`); every value below is mirrored into "
        "code and gated by `scripts/check_params.py`. Link a parameter anywhere in the spec with "
        "its generated `#param-<name>` anchor."
    )
    lines.append("")
    header = "| Parameter | Value | § | Decision | Description |"
    sep = "|-----------|-------|---|----------|-------------|"
    for cat, params in groups:
        lines.append(f"**{cat}**")
        lines.append("")
        lines.append(header)
        lines.append(sep)
        lines.extend(_row(p, sections, cat) for p in params)
        lines.append("")

    if reference:
        lines.append(
            "**Reference-only** — canonical documented values, single-site or not yet wired for "
            "cross-language enforcement (`enforce: false`)."
        )
        lines.append("")
        lines.append(header)
        lines.append(sep)
        lines.extend(_row(p, sections) for p in reference)
        lines.append("")

    lines.extend(_cross_language_table(enforced + reference))

    lines.append(END)
    return "\n".join(lines)


def _cross_language_table(params: list[dict]) -> list[str]:
    """Name map for any param carrying a `rust`/`lean`/`quint` spelling.

    Names diverge by language convention (yaml snake_case ⇄ Rust CamelCase ⇄ Lean camelCase/unicode ⇄
    Quint UPPER_SNAKE); this table pins the canonical concept to its per-language identifier. A `—` means
    that language has no direct equivalent (e.g. Quint uses a deliberately demo-scaled abstraction).
    """
    rows = [p for p in params if any(p.get(k) for k in ("rust", "lean", "quint"))]
    if not rows:
        return []
    out = [
        "**Cross-language names (canonical ⇄ Rust ⇄ Lean ⇄ Quint).** The same protocol value carries a "
        "different identifier per language by convention; values agree where a language pins the real "
        "(non-demo) figure. Enforced rows are value-gated against the Rust site by `check_params.py`.",
        "",
        "| Parameter | Rust (runtime) | Lean (lean-proofs) | Quint (formal-specs) |",
        "|-----------|----------------|--------------------------|----------------------|",
    ]
    for p in rows:
        name = p["name"]
        rust = f"`{_cell(p['rust'])}`" if p.get("rust") else "—"
        lean = f"`{_cell(p['lean'])}`" if p.get("lean") else "—"
        quint = f"`{_cell(p['quint'])}`" if p.get("quint") else "—"
        out.append(f"| [`{name}`](#param-{name}) | {rust} | {lean} | {quint} |")
    out.append("")
    return out


def _splice(doc: str, block: str) -> str:
    start = doc.index(BEGIN)
    end = doc.index(END) + len(END)
    return doc[:start] + block + doc[end:]


def main() -> int:
    check = "--check" in sys.argv
    doc = YP.read_text()
    if BEGIN not in doc or END not in doc:
        sys.exit(
            f"error: markers not found in {YP.relative_to(REPO)}; add {BEGIN} / {END} to Appendix A."
        )
    block = render()
    updated = _splice(doc, block)
    if check:
        if updated != doc:
            print(
                "gen_param_table: yellowpaper.md param table is STALE — run "
                "`uv run --script scripts/gen_param_table.py`.",
                file=sys.stderr,
            )
            return 1
        print("gen_param_table: param table up to date.")
        return 0
    if updated != doc:
        YP.write_text(updated)
        print(
            f"gen_param_table: wrote {sum(1 for _ in re.finditer(r'id=.param-', block))} params into "
            f"{YP.relative_to(REPO)}."
        )
    else:
        print("gen_param_table: no change.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
