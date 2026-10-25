#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema>=4.23,<5"]
# ///
"""Validate money-path fixtures; only the pallet runner establishes conformance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "whitepaper/evidence/money-path-v1.json"
if not CORPUS.exists():
    CORPUS = Path(__file__).with_name("money-path-v1.json")

# Retain the public discharge seeds even while their decisions are pending.
REQUIRED_SEEDS = {
    "htlc-below-lock",
    "htlc-equal-lock",
    "htlc-above-lock",
    "cooperative-1000",
    "cooperative-nondivisible",
    "cooperative-dust",
    "rent-provider-replacement",
    "force-dominance",
    "da-loss-no-prefix",
    "da-loss-cosigned-prefix",
    "reservation-slot-settle",
    "reservation-slot-expire",
    "reservation-slot-timeout",
    "reservation-slot-fraud",
    "reservation-slot-finalize",
    "lease-withdraw-unpinned",
    "lease-withdraw-pinned",
    "lease-withdraw-nonpublisher",
    "lease-withdraw-after-top-up",
    "lease-withdraw-outstanding-audit",
}

RENT_VECTORS = {
    "rent-provider-replacement",
    "rent-multiple-replacements",
    "rent-failed-block",
    "rent-repeat-assignment",
    "rent-partial-epochs",
    "rent-extension-new-tariff",
    "rent-close-partial-service",
}


def validate(corpus: dict, schema: dict) -> tuple[int, int]:
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(corpus)
    vectors = corpus["vectors"]
    ids = [vector["id"] for vector in vectors]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate money-path vector ID")
    missing = REQUIRED_SEEDS - set(ids)
    if missing:
        raise ValueError(f"missing public seeds: {sorted(missing)}")
    landed = [vector for vector in vectors if vector["status"] == "landed"]
    if not landed:
        raise ValueError("money-path corpus has no landed vectors")
    rent = {vector["id"] for vector in landed if vector["adapter"] == "paid-storage-arithmetic"}
    if rent != RENT_VECTORS:
        raise ValueError("money-path corpus must retain all seven D-0524 arithmetic vectors")
    for vector in landed:
        calls = [call["call"] for call in vector["extrinsics"]]
        if vector["adapter"] == "paid-storage-arithmetic":
            continue  # Schema constrains every call; the pallet rent helper checks amounts.
        if calls not in (["force_settle", "finalize"], ["force_settle"], ["timeout"]):
            raise ValueError(f"unsupported landed call sequence: {vector['id']}")
    return len(landed), len(vectors) - len(landed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CORPUS)
    args = parser.parse_args()
    corpus = json.loads(args.corpus.read_text())
    schema = json.loads(args.corpus.with_name("money-path-v1.schema.json").read_text())
    landed, pending = validate(corpus, schema)
    print(f"money-path schema: {landed} landed; {pending} pending (not conformance passes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
