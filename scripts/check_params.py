#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["PyYAML>=6.0.0"]
# ///
"""Drift checker for the canonical FLOP protocol parameters.

Reads `params/flop-protocol-params.yaml` (the single source of truth) and verifies
that every enforced parameter's `expect` snippet is present in each implementation
file. Fails (exit 1) if any implementation has drifted from the canonical value.

Usage:
    uv run --script scripts/check_params.py            # check, print report
    uv run --script scripts/check_params.py --quiet     # only print on failure

Wired into CI and the lefthook pre-commit hook so code and the canonical file
can never silently diverge.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("error: PyYAML is required; run with `uv run --script scripts/check_params.py`.")

REPO = Path(__file__).resolve().parent.parent
CANON = REPO / "params" / "flop-protocol-params.yaml"


def deployment_errors(params: list[dict]) -> list[str]:
    """Require an explicit deployment scope and change mechanism for every entry."""
    failures = []
    for p in params:
        name = p["name"]
        mutability = p.get("mutability")
        if mutability not in {
            "runtime-upgrade-only",
            "governance-settable",
            "source-only",
            "genesis-only",
        }:
            failures.append(f"[{name}] missing or invalid mutability")
        if mutability == "governance-settable" and not p.get("governance_setter"):
            failures.append(f"[{name}] governance-settable requires governance_setter")
        chain = p.get("on_chain", {})
        for field in ("constants", "storage"):
            paths = chain.get(field, [])
            if not isinstance(paths, list) or any(
                not isinstance(path, str) or not re.fullmatch(r"\w+\.\w+", path) for path in paths
            ):
                failures.append(f"[{name}] on_chain.{field} must list Pallet.Item paths")
        if chain.get("source_only"):
            if chain.get("constants") or chain.get("storage"):
                failures.append(f"[{name}] source-only cannot also have on-chain mappings")
        elif not chain.get("constants") and not chain.get("storage"):
            failures.append(
                f"[{name}] requires on-chain mappings or an explicit source_only reason"
            )
        # Canonical ahead of the deployed chain: the reason must say what deploys it.
        # Canonical ahead of the deployed chain until it runs `runtime` (a spec_version).
        if "pending_upgrade" in chain:
            pending = chain["pending_upgrade"]
            if (
                not isinstance(pending, dict)
                or type(pending.get("runtime")) is not int
                or pending["runtime"] <= 0
                or not isinstance(pending.get("reason"), str)
                or not pending["reason"].strip()
            ):
                failures.append(
                    f"[{name}] pending_upgrade needs a positive runtime spec_version and a reason"
                )
            if chain.get("source_only"):
                failures.append(f"[{name}] source-only cannot be pending_upgrade")
        # Governance moved the effective storage value; compiled constants keep `value`.
        if "governed_value" in chain:
            if mutability != "governance-settable" or not chain.get("storage"):
                failures.append(
                    f"[{name}] governed_value requires governance-settable storage mappings"
                )
            provenance = chain.get("governed_by")
            if not isinstance(provenance, str) or not provenance.strip():
                failures.append(f"[{name}] governed_value requires governed_by provenance")
        elif "governed_by" in chain:
            failures.append(f"[{name}] governed_by without governed_value")
    return failures


def _underscored(value) -> str:
    """Render an int with _ digit grouping, matching Rust literals (63_072_000)."""
    if isinstance(value, int):
        return f"{value:_}"
    return str(value)


def main() -> int:
    quiet = "--quiet" in sys.argv
    spec = yaml.safe_load(CANON.read_text())
    params = spec.get("parameters", [])

    failures = deployment_errors(params + spec.get("reference", []))
    checked = 0

    for p in params:
        name = p["name"]
        value = p["value"]
        impls = p.get("implementations", [])
        if not impls:
            continue

        # Sanity: the canonical value should appear in at least one expect, so a
        # stale `value` (updated nowhere in code) is caught too.
        value_forms = {str(value), _underscored(value)}
        if not any(any(f in impl["expect"] for f in value_forms) for impl in impls):
            failures.append(
                f"[{name}] canonical value {value!r} not found in any `expect` "
                f"snippet — update the expects to reflect the value."
            )

        for impl in impls:
            checked += 1
            fpath = REPO / impl["file"]
            expect = impl["expect"]
            want = impl.get("count")
            if not fpath.exists():
                failures.append(f"[{name}] missing file: {impl['file']}")
                continue
            text = fpath.read_text()
            n = text.count(expect)
            if want is not None:
                if n != want:
                    failures.append(
                        f"[{name}] {impl['file']}: expected {want}x `{expect}`, found {n}"
                    )
            elif n == 0:
                failures.append(f"[{name}] {impl['file']}: missing `{expect}`")

    if failures:
        print("✗ Parameter drift detected:\n")
        for f in failures:
            print(f"  - {f}")
        print(
            f"\n{len(failures)} issue(s). Reconcile code with "
            f"params/flop-protocol-params.yaml (the source of truth)."
        )
        return 1

    if not quiet:
        print(
            f"✓ All enforced parameters in sync "
            f"({checked} implementation sites across {len(params)} params)."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
