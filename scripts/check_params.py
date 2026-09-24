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

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("error: PyYAML is required; run with `uv run --script scripts/check_params.py`.")

REPO = Path(__file__).resolve().parent.parent
CANON = REPO / "params" / "flop-protocol-params.yaml"


def _underscored(value) -> str:
    """Render an int with _ digit grouping, matching Rust literals (63_072_000)."""
    if isinstance(value, int):
        return f"{value:_}"
    return str(value)


def main() -> int:
    quiet = "--quiet" in sys.argv
    spec = yaml.safe_load(CANON.read_text())
    params = spec.get("parameters", [])

    failures: list[str] = []
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
                        f"[{name}] {impl['file']}: expected {want}x " f"`{expect}`, found {n}"
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
