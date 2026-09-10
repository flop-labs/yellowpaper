# /// script
# requires-python = ">=3.11"
# ///
"""Reproduce conditional-audit and shared-collateral sensitivity evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve()
IN_CORE_CHECKOUT = HERE.parent.name == "research" and HERE.parent.parent.name == "scripts"
REPO = HERE.parents[2] if IN_CORE_CHECKOUT else HERE.parent
OUT = REPO / "whitepaper" / "evidence" if IN_CORE_CHECKOUT else HERE.parent
FACTORS = ("selection", "data", "challenge", "inclusion", "upheld", "collection")
SOURCES = {
    "pallets/pallets/compute-channel/src/lib.rs": (
        "pub fn open_channel(",
        "pub fn top_up_escrow(",
        ("Self::check_reservation_cap(&agent, escrow)?;",),
    ),
    "pallets/pallets/compute-channel/src/lib.rs#dispute": (
        "pub fn resolve_timeout_dispute(",
        "pub fn resolve_unrecoverable_transcript(",
        ("T::Slasher::slash_fraud(&ch.miner, channel_id)?;",),
    ),
    "pallets/runtime/zkverify/src/lib.rs": (
        "impl pallet_compute_channel::ChannelSlasher",
        "pub struct ChannelDaAvailability",
        ("slash_proof_forgery_with_amount(", "Error::<Runtime>::NotSlashable", "Ok(0)"),
    ),
    "pallets/pallets/miner-slashing/src/lib.rs": (
        "pub fn slash_proof_forgery_with_amount(",
        "pub fn slash_audit_forfeit(",
        ("Perbill::from_percent(100)", "true, // permanent blacklist"),
    ),
    "pallets/pallets/miner-staking/src/lib.rs": (
        "pub fn unbond(",
        "pub fn claim_unbonded(",
        ("Self::miner_busy_count(&miner) == 0",),
    ),
    "pallets/pallets/miner-staking/src/lib.rs#sponsor": (
        "pub fn slash_sponsor_positions(",
        "pub fn slash_delegator_positions(",
        ("SponsorPositionStatus::Active | SponsorPositionStatus::Unbonding",),
    ),
}

# Embedded so arithmetic reproduction does not require the private implementation checkout.
# --verify-sources recomputes these scoped span hashes and line references when sources exist.
SOURCE_LEDGER = [
    {
        "path": "pallets/pallets/compute-channel/src/lib.rs",
        "span": ["pub fn open_channel(", "pub fn top_up_escrow("],
        "sha256": "d8e8167836b0b5894d2468668956762cf72c64f49222733f3e64000420bae4ce",
        "references": [{"fragment": "Self::check_reservation_cap(&agent, escrow)?;", "line": 2882}],
    },
    {
        "path": "pallets/pallets/compute-channel/src/lib.rs",
        "span": ["pub fn resolve_timeout_dispute(", "pub fn resolve_unrecoverable_transcript("],
        "sha256": "8405c248d2c37445337b7598a945dead757230df5c2bdbf62266541c0a79b54c",
        "references": [
            {"fragment": "T::Slasher::slash_fraud(&ch.miner, channel_id)?;", "line": 4011}
        ],
    },
    {
        "path": "pallets/runtime/zkverify/src/lib.rs",
        "span": ["impl pallet_compute_channel::ChannelSlasher", "pub struct ChannelDaAvailability"],
        "sha256": "a0a03e190685a10defb5e67389eea9d0ffbf610c3ef070db58f1e1033115910e",
        "references": [
            {"fragment": "slash_proof_forgery_with_amount(", "line": 1567},
            {"fragment": "Error::<Runtime>::NotSlashable", "line": 1579},
            {"fragment": "Ok(0)", "line": 1582},
        ],
    },
    {
        "path": "pallets/pallets/miner-slashing/src/lib.rs",
        "span": ["pub fn slash_proof_forgery_with_amount(", "pub fn slash_audit_forfeit("],
        "sha256": "4ceddce058635dd23b4672ba772891d7d42d2c859b817f59197b601fabccae77",
        "references": [
            {"fragment": "Perbill::from_percent(100)", "line": 503},
            {"fragment": "true, // permanent blacklist", "line": 505},
        ],
    },
    {
        "path": "pallets/pallets/miner-staking/src/lib.rs",
        "span": ["pub fn unbond(", "pub fn claim_unbonded("],
        "sha256": "e4750cf9015afcc1310d017f049b7cc331ba3297332c16744ee09f1a9a201ebf",
        "references": [{"fragment": "Self::miner_busy_count(&miner) == 0", "line": 744}],
    },
    {
        "path": "pallets/pallets/miner-staking/src/lib.rs",
        "span": ["pub fn slash_sponsor_positions(", "pub fn slash_delegator_positions("],
        "sha256": "ab955d31a837564a2d0f3935e214ea1cb01cf2b1553e088e69164ec22bbc7998",
        "references": [
            {
                "fragment": "SponsorPositionStatus::Active | SponsorPositionStatus::Unbonding",
                "line": 1457,
            }
        ],
    },
]

SCENARIOS = {
    "selection_only": {
        "selection": "1/20",
        "data": "1",
        "challenge": "1",
        "inclusion": "1",
        "upheld": "1",
        "collection": "1",
    },
    "illustrative_stress": {
        "selection": "1/20",
        "data": "9/10",
        "challenge": "4/5",
        "inclusion": "19/20",
        "upheld": "9/10",
        "collection": "3/4",
    },
    "no_data": {
        "selection": "1/20",
        "data": "0",
        "challenge": "1",
        "inclusion": "1",
        "upheld": "1",
        "collection": "1",
    },
    "no_challenger": {
        "selection": "1/20",
        "data": "1",
        "challenge": "0",
        "inclusion": "1",
        "upheld": "1",
        "collection": "1",
    },
    "finality_stall": {
        "selection": "1/20",
        "data": "1",
        "challenge": "1",
        "inclusion": "0",
        "upheld": "1",
        "collection": "1",
    },
}


def frac(value: str | int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def effective_probability(factors: dict[str, str | Fraction]) -> Fraction:
    result = Fraction(1)
    for name in FACTORS:
        result *= frac(factors[name])
    return result


def challenger_utility(
    *,
    expected_reward: Fraction,
    expected_private_recovery: Fraction,
    bond: int,
    false_loss: Fraction,
    data_cost: int,
    verify_cost: int,
    tx_cost: int,
    censorship_cost: int,
    delay_cost: int,
) -> Fraction:
    return (
        expected_reward
        + expected_private_recovery
        - frac(data_cost + verify_cost + tx_cost + censorship_cost + delay_cost)
        - false_loss * bond
    )


def coalition_payoff(
    *,
    exposures: list[int],
    avoided_costs: list[int],
    collateral: int,
    p_effective: Fraction,
    future_revenue_loss: int = 0,
    bribes: int = 0,
    recovery_discount: Fraction = Fraction(1),
) -> Fraction:
    """Risk-neutral incremental fraud payoff; one shared bond is collectible once."""
    gross = sum(exposures) + sum(avoided_costs)
    loss = p_effective * (collateral * recovery_discount + future_revenue_loss)
    return frac(gross - bribes) - loss


def any_detection_probability(p: Fraction, opportunities: int, correlation: Fraction) -> Fraction:
    """Sensitivity interpolation: rho=0 iid opportunities; rho=1 one common event."""
    independent = 1 - (1 - p) ** opportunities
    return correlation * p + (1 - correlation) * independent


def penalty_collection_waterfall(collateral: int, claims: list[int]) -> list[int]:
    remaining = collateral
    paid = []
    for claim in claims:
        amount = min(remaining, claim)
        paid.append(amount)
        remaining -= amount
    return paid


def source_ledger(repo: Path = REPO) -> list[dict[str, object]]:
    rows = []
    for key, (start, end, needles) in SOURCES.items():
        rel = key.split("#", 1)[0]
        text = (repo / rel).read_text()
        start_at = text.index(start)
        end_at = text.index(end, start_at)
        span = text[start_at:end_at]
        refs = []
        for needle in needles:
            if needle not in span:
                raise ValueError(f"missing source fact: {rel}: {needle}")
            offset = start_at + span.index(needle)
            refs.append({"fragment": needle, "line": text[:offset].count("\n") + 1})
        rows.append(
            {
                "path": rel,
                "span": [start, end],
                "sha256": hashlib.sha256(span.encode()).hexdigest(),
                "references": refs,
            }
        )
    return rows


def build_report() -> dict[str, object]:
    scenarios = []
    for name, values in SCENARIOS.items():
        p = effective_probability(values)
        scenarios.append(
            {
                "scenario": name,
                "factors": values,
                "p_effective": str(p),
                "p_effective_decimal": float(p),
            }
        )

    # A unit bond is reused across equal unit-value channels. Exact arithmetic exposes
    # the break-even boundary without assigning empirical meaning to scenario inputs.
    concurrency = []
    for scenario in scenarios:
        p = frac(scenario["p_effective"])
        for channels in (1, 2, 4, 8, 16):
            payoff = coalition_payoff(
                exposures=[1] * channels, avoided_costs=[0] * channels, collateral=1, p_effective=p
            )
            concurrency.append(
                {
                    "scenario": scenario["scenario"],
                    "channels": channels,
                    "exposure": channels,
                    "collateral": 1,
                    "exposure_per_collateral": channels,
                    "deterrence_margin": str(-payoff),
                    "fraud_payoff": str(payoff),
                    "deterred": payoff < 0,
                }
            )

    waterfall = []
    for claims in ([1], [1, 1], [1, 1, 1, 1]):
        collected = penalty_collection_waterfall(1, list(claims))
        waterfall.append(
            {
                "penalty_demands": list(claims),
                "penalties_collected": collected,
                "uncollectible_penalty": sum(claims) - sum(collected),
                "note": "Collected slash/burn; no victim payout is implied.",
            }
        )

    correlation = []
    base_p = effective_probability(SCENARIOS["illustrative_stress"])
    for opportunities in (1, 2, 4, 8, 16):
        for rho in (Fraction(0), Fraction(1, 2), Fraction(1)):
            detected = any_detection_probability(base_p, opportunities, rho)
            correlation.append(
                {
                    "opportunities": opportunities,
                    "correlation_input": str(rho),
                    "probability_any_detection": str(detected),
                    "probability_any_detection_decimal": float(detected),
                }
            )

    return {
        "schema_version": 1,
        "scope": "Deterministic sensitivity model; probabilities are labeled inputs, not measurements.",
        "conditional_chain": "P(S)*P(D|S)*P(C|S,D)*P(I|S,D,C)*P(U|S,D,C,I)*P(K|S,D,C,I,U)",
        "payoff_inputs": {
            "exposures": "Fraud-only revenue or external benefit above the honest baseline; use a conservative total attack-gain upper bound when classification is uncertain.",
            "avoided_costs": "Compute, data-publication, or other costs avoided only by attacking; exclude costs also avoided honestly.",
            "future_revenue_loss": "Expected future honest revenue lost only after a collectible verdict; multiplied by the verdict probability.",
            "bribes": "Attack costs paid regardless of detection in this model.",
        },
        "sources": SOURCE_LEDGER,
        "scenarios": scenarios,
        "shared_collateral": concurrency,
        "collection_waterfall": waterfall,
        "correlated_failure_sensitivity": correlation,
        "challenger_examples": [
            {
                "name": "positive",
                "utility": str(
                    challenger_utility(
                        expected_reward=Fraction(3),
                        expected_private_recovery=Fraction(0),
                        bond=2,
                        false_loss=Fraction(1, 10),
                        data_cost=1,
                        verify_cost=1,
                        tx_cost=0,
                        censorship_cost=0,
                        delay_cost=0,
                    )
                ),
            },
            {
                "name": "no_reward_high_cost",
                "utility": str(
                    challenger_utility(
                        expected_reward=Fraction(0),
                        expected_private_recovery=Fraction(0),
                        bond=2,
                        false_loss=Fraction(1, 10),
                        data_cost=1,
                        verify_cost=1,
                        tx_cost=1,
                        censorship_cost=1,
                        delay_cost=1,
                    )
                ),
            },
        ],
        "ratified_or_wired": [
            "selection rate is configured",
            "fraud verdict routes to full-stake forgery slash",
            "busy count blocks unbond while sessions/disputes remain open",
            "unbonding sponsor principal remains slashable",
        ],
        "not_established": [
            "empirical values for downstream conditionals",
            "challenger reward funding",
            "miner-side aggregate exposure reservation across ordinary channels",
            "pro-rata recovery after the first full-stake slash",
            "independence across channels or epochs",
        ],
        "falsification": "In the exported sweep, bribes and future-revenue loss are zero: exposure >= p_effective * discounted collateral fails the modeled sufficient condition. In the general model compare net incremental gain against p_effective * (discounted collateral + conditional future-revenue loss). A failed sufficient condition does not rule out deterrence through sanctions outside this model.",
    }


def render_json(report: dict[str, object]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_csv(report: dict[str, object]) -> str:
    out = io.StringIO()
    fields = (
        "scenario",
        "channels",
        "exposure",
        "collateral",
        "exposure_per_collateral",
        "fraud_payoff",
        "deterred",
    )
    writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(report["shared_collateral"])
    return out.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--verify-sources", action="store_true")
    args = parser.parse_args()
    if args.verify_sources:
        if not IN_CORE_CHECKOUT:
            raise SystemExit("--verify-sources requires a flop-core checkout")
        if source_ledger(REPO) != SOURCE_LEDGER:
            raise SystemExit("source ledger drift")
    report = build_report()
    files = {
        OUT / "yellowpaper-audit-evidence.json": render_json(report),
        OUT / "yellowpaper-audit-evidence.csv": render_csv(report),
    }
    if args.check:
        stale = [
            str(path)
            for path, content in files.items()
            if not path.exists() or path.read_text() != content
        ]
        if stale:
            raise SystemExit("stale: " + ", ".join(stale))
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        for path, content in files.items():
            path.write_text(content)
    print(
        f"audit-evidence: {len(report['scenarios'])} scenarios, {len(report['shared_collateral'])} exposure rows; OK"
    )


if __name__ == "__main__":
    main()
