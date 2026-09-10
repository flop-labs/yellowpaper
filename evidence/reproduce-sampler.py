# Copyright 2026 FLOP Network
# SPDX-License-Identifier: Apache-2.0
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Exact evidence for sequential weighted sampling without replacement.

This enumerates count states for populations made of homogeneous identity groups. It models the
sampler's ideal weighted interval draws, not its PRNG or the origin of its seed.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


@dataclass(frozen=True)
class Group:
    name: str
    count: int
    weight: int
    attacker: bool


def exact_seat_distribution(groups: tuple[Group, ...], draws: int) -> dict[int, Fraction]:
    """Return the exact attacker-seat distribution for sequential PPSWOR draws."""
    if draws < 0 or draws > sum(group.count for group in groups):
        raise ValueError("draws must be between zero and the population size")
    if any(group.count < 0 or group.weight <= 0 for group in groups):
        raise ValueError("group counts must be nonnegative and weights positive")

    initial = tuple(group.count for group in groups)
    states: dict[tuple[int, ...], Fraction] = {initial: Fraction(1)}
    for _ in range(draws):
        following: dict[tuple[int, ...], Fraction] = defaultdict(Fraction)
        for remaining, probability in states.items():
            total_weight = sum(n * group.weight for n, group in zip(remaining, groups, strict=True))
            for index, (n, group) in enumerate(zip(remaining, groups, strict=True)):
                if n == 0:
                    continue
                next_remaining = list(remaining)
                next_remaining[index] -= 1
                following[tuple(next_remaining)] += probability * Fraction(
                    n * group.weight, total_weight
                )
        states = dict(following)

    distribution: dict[int, Fraction] = defaultdict(Fraction)
    for remaining, probability in states.items():
        attacker_seats = sum(
            group.count - n for n, group in zip(remaining, groups, strict=True) if group.attacker
        )
        distribution[attacker_seats] += probability
    return dict(sorted(distribution.items()))


def bft_failure_seats(committee_size: int) -> int:
    """Smallest integer f for which strict AlephBFT premise 3f < n fails."""
    return (committee_size + 2) // 3


def fraction_record(value: Fraction) -> dict[str, str | float]:
    return {
        "exact": f"{value.numerator}/{value.denominator}",
        "decimal": float(value),
    }


def counterexample_report() -> dict[str, object]:
    groups = (
        Group("attacker", count=40, weight=100_000, attacker=True),
        Group("honest", count=61, weight=300_000, attacker=False),
    )
    draws = 100
    threshold = bft_failure_seats(draws)
    distribution = exact_seat_distribution(groups, draws)
    failure_probability = sum(
        probability for seats, probability in distribution.items() if seats >= threshold
    )
    return {
        "model": "ideal sequential probability-proportional-to-remaining-weight draws without replacement",
        "scope": (
            "Exact for the stated two homogeneous groups. It does not prove PRNG uniformity, "
            "the concrete seed-to-draw mapping, BABE-VRF seed unbiasability, independence across "
            "epochs, or another population."
        ),
        "implementation_mapping": {
            "status": "not represented by the exact enumerator",
            "prng": "SplitMix64 expands the 32-byte seed into paired 128-bit values",
            "interval_mapping": "next_u128 modulo remaining aggregate stake",
            "caveats": [
                "modulo mapping is not exactly uniform unless the bound divides 2^128",
                "aggregate u128 stake sum must not overflow",
                "interval accumulation saturates at u128::MAX and removal subtraction saturates",
                "seed availability and adversarial influence are separate assumptions",
            ],
        },
        "voting_unit": "one distinct eligible identity per committee seat",
        "groups": [group.__dict__ for group in groups],
        "eligibility_floor": 100_000,
        "draws": draws,
        "strict_engine_premise": "3 * attacker_seats < realized_committee_size",
        "failure_threshold_seats": threshold,
        "distribution": {
            str(seats): fraction_record(probability) for seats, probability in distribution.items()
        },
        "failure_probability": fraction_record(failure_probability),
        "attacker_stake_fraction": fraction_record(Fraction(40, 223)),
        "claim_disposition": (
            "Counterexample: aggregate attacker stake does not determine a binomial seat tail for "
            "unequal-weight distinct-identity sampling."
        ),
        "open_policy": [
            "attacker identity-control, delegation-control, and eligibility-cost model",
            "ratified minimum eligible-pool and zero-work bootstrap behavior",
            "BABE-VRF withholding/grinding budget and repeated-epoch exposure horizon",
            "a bound connecting the concrete PRNG/modulo/overflow behavior to the ideal draw model",
        ],
    }


def render_report() -> str:
    return json.dumps(counterexample_report(), indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    rendered = render_report()
    if args.check:
        if args.check.read_text() != rendered:
            raise SystemExit(f"stale sampler evidence: {args.check}")
        print("sampler evidence: OK")
    elif args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
