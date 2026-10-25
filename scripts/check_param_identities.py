#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["PyYAML>=6.0.0"]
# ///
"""Arithmetic-identity checker for the canonical FLOP protocol parameters.

`check_params.py` answers "does literal X appear in file Y?". It cannot answer
"do these params still add up?", so cross-param drift is invisible to it — the
`reference:` block is not checked at all, and derived constants (cohort sums,
emission totals, the Lean/TS `total_issued_end_era6` twin) are hand-maintained
literals that can silently diverge from the params they are derived FROM.

This script closes that gap: every identity below is recomputed from the
canonical `value:` fields in `params/flop-protocol-params.yaml` and compared
against the derived constant the repo ships. It reads BOTH `parameters:` and
`reference:`.

Exact rational arithmetic throughout — no float tolerance on protocol values.

Usage:
    uv run --script scripts/check_param_identities.py           # check, print report
    uv run --script scripts/check_param_identities.py --quiet    # only print on failure
"""

from __future__ import annotations

import re
import sys
from fractions import Fraction
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit(
        "error: PyYAML is required; run with `uv run --script scripts/check_param_identities.py`."
    )

REPO = Path(__file__).resolve().parent.parent
CANON = REPO / "params" / "flop-protocol-params.yaml"


def load() -> dict[str, object]:
    spec = yaml.safe_load(CANON.read_text())
    out: dict[str, object] = {}
    for section in ("parameters", "reference"):
        for p in spec.get(section, []) or []:
            out[p["name"]] = p.get("value")
    out["_meta"] = spec["meta"]
    return out


def main() -> int:
    quiet = "--quiet" in sys.argv
    params = load()
    meta = params["_meta"]

    r0 = Fraction(params["initial_block_reward"])
    halving = Fraction(params["halving_interval_blocks"])
    n_halvings = int(params["max_halvings"])
    sub_rate = Fraction(params["subsidy_per_block_per_recipient"])
    blocks_yr = Fraction(365 * meta["blocks_per_day"])

    def reward(era: int) -> Fraction:
        return r0 / 2 ** min(era, n_halvings)

    def subsidy_total_rate(era: int) -> Fraction:
        # both recipients; terminates (no floor) at the same boundary the reward floors
        return (2 * sub_rate) / 2**era if era < n_halvings else Fraction(0)

    # Era 0 is blocks 1..=H-1 (H-1 rewarded blocks, since genesis block 0 is unrewarded per R9.7),
    # while each subsequent era e >= 1 is e*H..=(e+1)*H-1 (H rewarded blocks).
    def emission(n: int) -> Fraction:
        return halving * sum(reward(e) for e in range(n)) - (reward(0) if n > 0 else Fraction(0))

    subsidy_lifetime = halving * sum(
        subsidy_total_rate(e) for e in range(n_halvings)
    ) - subsidy_total_rate(0)

    checks: list[tuple[str, Fraction, Fraction]] = [
        # --- genesis conservation: the four cohorts must exhaust the pool ---
        (
            "genesis cohorts sum to genesis_supply",
            Fraction(params["genesis_miner_airdrop"])
            + Fraction(params["genesis_validator_airdrop"])
            + Fraction(params["genesis_agent_airdrop"])
            + Fraction(params["genesis_reserve"]),
            Fraction(params["genesis_supply"]),
        ),
        # --- block-reward split must exhaust the block ---
        (
            "reward split sums to 1000 ppt",
            Fraction(params["miner_share_ppt"])
            + Fraction(params["validator_share_ppt"])
            + Fraction(params["agent_share_ppt"])
            + Fraction(params["staker_share_ppt"]),
            Fraction(1000),
        ),
        # --- halving ladder endpoints ---
        (
            "floor_reward == r0 / 2^max_halvings",
            Fraction(params["floor_reward"]),
            r0 / 2**n_halvings,
        ),
        # --- subsidy: rate, duration and lifetime total must agree ---
        (
            "subsidy_total_per_block == 2 x per-recipient",
            Fraction(params["subsidy_total_per_block"]),
            2 * sub_rate,
        ),
        (
            "subsidy_duration_blocks == max_halvings eras",
            Fraction(params["subsidy_duration_blocks"]),
            halving * n_halvings,
        ),
        (
            "subsidy lifetime total == 1,955,231,984",
            subsidy_lifetime,
            Fraction(1_955_231_984),
        ),
        # --- emission milestones quoted in the yellowpaper and mirrored in Lean/Quint/TS ---
        (
            "emission_through_halving_eras == r0.halving.63/32 - r0",
            Fraction(params["emission_through_halving_eras"]),
            emission(n_halvings + 1),
        ),
        (
            "emission_at_end_of_era6 == 2.r0.H - r0",
            Fraction(params["emission_at_end_of_era6"]),
            emission(n_halvings + 2),
        ),
        (
            "floor_annual_emission == floor_reward x blocks/yr",
            Fraction(params["floor_annual_emission"]),
            Fraction(params["floor_reward"]) * blocks_yr,
        ),
        # --- timing params derived from block time ---
        (
            "blocks_per_day == 86400 / block_time",
            Fraction(meta["blocks_per_day"]),
            Fraction(86_400) // Fraction(meta["block_time_seconds"]),
        ),
        (
            "halving_interval_blocks == halving_interval_days x blocks/day",
            halving,
            Fraction(meta["halving_interval_days"]) * Fraction(meta["blocks_per_day"]),
        ),
    ]

    # Inequalities, kept separate from the equalities above.
    bounds: list[tuple[str, bool, str]] = [
        (
            "da_shard_count >= da_min_replication_factor",
            Fraction(params["da_shard_count"]) >= Fraction(params["da_min_replication_factor"]),
            f"R={params['da_shard_count']} < k={params['da_min_replication_factor']} would be unreconstructable",
        ),
    ]

    # --- derived constants mirrored OUTSIDE the params file (Lean / Quint / TS twins) ---
    # These literals live in proof statements and test assertions, so `check_params.py` never
    # sees them. Recompute each from the params above and read the shipped literal back out of
    # its file: a reminder in the success path is not a gate, and would leave the Lean
    # `norm_num` proof to discover the drift by breaking the build.
    #
    # total_issued_end_era6 = genesis + (2.r0.halving - r0) + the whole subsidy schedule (less block 0).
    total_era6 = Fraction(params["genesis_supply"]) + emission(n_halvings + 2) + subsidy_lifetime
    genesis = Fraction(params["genesis_supply"])

    mirrors: list[tuple[str, str, str, Fraction]] = [
        (
            "session_key_expiry_days × blocks_per_day",
            "pallets/runtime/zkverify/src/lib.rs",
            r"pub const SessionKeysMaxDuration:\s*u32\s*=\s*([\d_]+)",
            Fraction(params["session_key_expiry_days"]) * Fraction(meta["blocks_per_day"]),
        ),
        (
            "total_issued_end_era6",
            "lean-proofs/FlopSpecs/HalvingBoundary.lean",
            # Anchored on the theorem name: the file has other `= NNN := by` closures
            # (e.g. subsidyTotal_numeric), and an unanchored pattern silently checks one
            # of those instead.
            r"theorem total_issued_end_era6\b.*?=\s*([\d_]+)\s*:=\s*by",
            total_era6,
        ),
        (
            "total_issued_end_era6",
            "ai-agent-simulator/tests/unit/halving-boundary.spec.ts",
            # Anchored on the assertion's `it(...)` title for the same reason.
            r"no hard cap\).*?expect\(ts\)\.toBe\(([\d_]+)\)",
            total_era6,
        ),
        (
            "genesisSupply",
            "lean-proofs/FlopSpecs/Genesis.lean",
            r"def genesisSupply\s*:\s*\S+\s*:=\s*([\d_]+)",
            genesis,
        ),
        (
            "genesisSupply",
            "lean-proofs/FlopSpecs/HalvingBoundary.lean",
            r"def genesisSupply\s*:\s*\S+\s*:=\s*([\d_]+)",
            genesis,
        ),
        (
            "GENESIS_MICRO",
            "formal-specs/economics/halving-boundary.qnt",
            r"GENESIS_MICRO\s*:\s*int\s*=\s*([\d_]+)",
            genesis * 1_000_000,
        ),
    ]

    mirror_failures: list[str] = []
    mirrors_checked = 0
    for label, rel, pattern, expected in mirrors:
        path = REPO / rel
        if not path.exists():
            mirror_failures.append(f"{label} mirror\n        missing file: {rel}")
            continue
        match = re.search(pattern, path.read_text(), re.DOTALL)
        if match is None:
            mirror_failures.append(
                f"{label} mirror\n        no literal matched in {rel} "
                "— the site moved or was renamed; update the pattern in this script"
            )
            continue
        mirrors_checked += 1
        shipped = Fraction(int(match.group(1).replace("_", "")))
        if shipped != expected:
            mirror_failures.append(
                f"{label} mirror in {rel}\n"
                f"        params imply {int(expected):,}, file says {int(shipped):,}"
            )

    failures = [f"{n}\n        params imply {w}, file says {g}" for n, g, w in checks if g != w]
    failures += [f"{n}\n        {why}" for n, ok, why in bounds if not ok]
    failures += mirror_failures

    if failures:
        print("✗ param identity failures:", file=sys.stderr)
        for f in failures:
            print(f"    {f}", file=sys.stderr)
        return 1

    if not quiet:
        print(
            f"✓ All {len(checks) + len(bounds)} param identities hold; "
            f"{mirrors_checked} external mirrors match."
        )
        print(
            "  derived constants mirrored outside params/, verified against their shipped literals:"
        )
        print(
            f"    total_issued_end_era6 = {int(total_era6):,}"
            "   (HalvingBoundary.lean, halving-boundary.spec.ts)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
