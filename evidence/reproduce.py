# /// script
# requires-python = ">=3.12"
# ///
"""Reproduce prepublication claim arithmetic and SCALE fixtures without dependencies.

The embedded field ledger makes the public evidence bundle self-contained.  In a
flop-core checkout, source needles are also checked so wire-size results fail on
relevant source drift.  This is serialized-byte evidence and charged-weight
analysis, not a dispatch, runtime benchmark, network measurement, or theorem.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
from fractions import Fraction
from pathlib import Path

PERBILL = 1_000_000_000
THRESHOLD_PARTS = 666_666_666
RUNTIME_PALLET_INDICES = {"FlopPoui": 86, "ComputeChannel": 103}
RUNTIME_MAX_ACTIVE_VALIDATORS = 200
FINALITY_COMMITTEE_CAP = 100
NORMAL_MAX_BYTES = 5 * 1024 * 1024 * 75 // 100
OPERATIONAL_MAX_BYTES = 5 * 1024 * 1024
MAX_BLOCK_REF_TIME = 750_000_000_000
NORMAL_MAX_REF_TIME = MAX_BLOCK_REF_TIME * 75 // 100
WEIGHT_REF_TIME_PER_NANOS = 1_000
RUNTIME_DB_WEIGHT_SOURCE = "pallets/runtime/zkverify/src/weights/db.rs"
RUNTIME_DB_WEIGHT_SCHEMA = {
    "read_ref_time": 9_372_000,
    "write_ref_time": 71_631_000,
}

SOURCE_FACTS = {
    "pallets/primitives/hp-poui/src/lib.rs": [],
    "pallets/pallets/flop-poui/src/lib.rs": [
        "pub fn submit_validator_attestations(",
        "attestations: Vec<ValidatorAttestation>,",
        "T::WeightInfo::submit_oracle_attestation()",
        ".saturating_mul(attestations.len().max(1) as u64)",
    ],
    "pallets/runtime/zkverify/src/lib.rs": [
        "PouiDefaultValidatorAttestationThreshold: Perbill = Perbill::from_parts(666_666_666)",
        "pub const ChannelMaxSettlementTurns: u32 = 1024;",
        "pub const ChannelMaxMerklePathLen: u32 = 64;",
        "FlopPoui: pallet_flop_poui = 86,",
        "ComputeChannel: pallet_compute_channel = 103,",
        "pub const MAX_ACTIVE_VALIDATORS: u32 = 200;",
        "pub const AlephMaxCommittee: u32 = 100;",
        "::max_with_normal_ratio(5 * 1024 * 1024, NORMAL_DISPATCH_RATIO)",
        "const NORMAL_DISPATCH_RATIO: Perbill = Perbill::from_percent(75);",
        "Weight::from_parts(WEIGHT_REF_TIME_PER_SECOND * 3 / 4, u64::MAX)",
        "pub type TxExtension = (",
        "frame_system::CheckNonZeroSender<Runtime>,",
        "frame_system::CheckSpecVersion<Runtime>,",
        "frame_system::CheckTxVersion<Runtime>,",
        "frame_system::CheckGenesis<Runtime>,",
        "frame_system::CheckEra<Runtime>,",
        "frame_system::CheckNonce<Runtime>,",
        "frame_system::CheckWeight<Runtime>,",
        "pallet_transaction_payment::ChargeTransactionPayment<Runtime>,",
        "frame_metadata_hash_extension::CheckMetadataHash<Runtime>,",
        "pub type Address = sp_runtime::MultiAddress<AccountId, ()>;",
        "generic::UncheckedExtrinsic<Address, RuntimeCall, Signature, TxExtension>;",
        "type DbWeight = weights::db::constants::RocksDbWeight;",
    ],
    RUNTIME_DB_WEIGHT_SOURCE: [],
    "pallets/runtime/zkverify/src/types.rs": [
        "pub type BlockNumber = u32;",
        "pub type AccountId = <<Signature as Verify>::Signer as IdentifyAccount>::AccountId;",
        "pub type Signature = MultiSignature;",
        "pub type Balance = u128;",
    ],
    "pallets/pallets/compute-channel/src/lib.rs": [
        "verified_turns: Vec<VerifiedTurn>,",
        "!verified_turns[..idx]",
        ".any(|prev| prev.turn_index == turn.turn_index)",
        "turn.merkle_path.len() as u32 <= T::MaxMerklePathLen::get()",
    ],
    "pallets/pallets/compute-channel/src/weights.rs": [
        "fn settle(n: u32) -> Weight {",
        "fn force_settle(n: u32) -> Weight {",
        "Weight::from_parts(35_000_000, 0).saturating_mul(n as u64)",
    ],
    "pallets/pallets/flop-poui/src/weights.rs": [
        "auto-generated stub - to be benchmarked",
        "Weight::from_parts(50_000_000, 0)",
    ],
    "pallets/pallets/da-registry/src/lib.rs": [
        "pub type ProviderId = u8;",
        "pub const PROVIDER_SOVEREIGN_VALIDATORS: ProviderId = 0;",
    ],
    "pallets/primitives/hp-consensus/src/committee.rs": [
        "VRF-seeded, stake-weighted, without-replacement committee sampler",
        "let (stake, who) = pool.swap_remove(hit);",
    ],
    "lean-proofs/FlopSpecs/CommitteeSampling.lean": [
        "def SelectionTailDominated (selTail : ℕ → ℝ) (N : ℕ) (p : ℝ) : Prop :=",
        "∀ f, selTail f ≤ binomialTail N f p",
    ],
}

CALL_SCHEMAS = {
    ("pallets/pallets/flop-poui/src/lib.rs", "submit_validator_attestations"): (
        15,
        [("attestations", "Vec<ValidatorAttestation>")],
    ),
    ("pallets/pallets/compute-channel/src/lib.rs", "open_channel"): (
        0,
        [
            ("miner", "T::AccountId"),
            ("model_hash", "H256"),
            ("measured_root", "H256"),
            ("decode_policy_hash", "H256"),
            ("precision", "ModelPrecision"),
            ("enclave_key", "[u8; 32]"),
            ("agent_key", "[u8; 32]"),
            ("sla", "Sla<BlockNumberFor<T>>"),
            ("escrow", "BalanceOf<T>"),
            ("nonce", "u64"),
            ("settlement_class", "SettlementClass"),
        ],
    ),
    ("pallets/pallets/compute-channel/src/lib.rs", "settle"): (
        2,
        [
            ("channel_id", "H256"),
            ("final_root", "H256"),
            ("aggregate_gn", "u128"),
            ("claimed_measured_root", "H256"),
            ("agent_receipt_sig", "[u8; 64]"),
            ("transcript_ref", "Option<DataRef>"),
            ("verified_turns", "Vec<VerifiedTurn>"),
        ],
    ),
    ("pallets/pallets/compute-channel/src/lib.rs", "force_settle"): (
        3,
        [
            ("channel_id", "H256"),
            ("final_root", "H256"),
            ("aggregate_gn", "u128"),
            ("claimed_measured_root", "H256"),
            ("agent_receipt_sig", "[u8; 64]"),
            ("transcript_ref", "Option<DataRef>"),
            ("verified_turns", "Vec<VerifiedTurn>"),
        ],
    ),
    ("pallets/pallets/compute-channel/src/lib.rs", "finalize"): (
        4,
        [("channel_id", "H256")],
    ),
    ("pallets/pallets/compute-channel/src/lib.rs", "open_dispute"): (
        6,
        [("channel_id", "H256"), ("contested_turn", "u32")],
    ),
    ("pallets/pallets/compute-channel/src/lib.rs", "respond_dispute"): (
        7,
        [
            ("channel_id", "H256"),
            ("leaf_version", "crate::TranscriptLeafVersion"),
            ("turn_index", "u32"),
            ("h_in", "H256"),
            ("h_out", "H256"),
            ("g_n", "u128"),
            ("decode_policy_hash", "H256"),
            ("h_ids", "H256"),
            ("toploc_commitment_hash", "H256"),
            ("miner_recv_ms", "u64"),
            ("miner_done_ms", "u64"),
            ("latency_ms", "u64"),
            ("enclave_sig", "[u8; 64]"),
            ("merkle_path", "Vec<(H256, bool)>"),
        ],
    ),
    ("pallets/pallets/compute-channel/src/lib.rs", "submit_toploc_evidence"): (
        21,
        [("channel_id", "H256"), ("commitment_ref", "H256")],
    ),
}

WEIGHT_SCHEMAS = {
    ("pallets/pallets/flop-poui/src/weights.rs", "submit_oracle_attestation"): {
        "parameter": None,
        "base_ref_time": 50_000_000,
        "proof_size": 0,
        "per_unit_ref_time": 0,
        "reads": 0,
        "writes": 0,
    },
    ("pallets/pallets/compute-channel/src/weights.rs", "open_channel"): {
        "parameter": None,
        "base_ref_time": 86_740_000,
        "proof_size": 27_132,
        "per_unit_ref_time": 0,
        "reads": 10,
        "writes": 9,
    },
    ("pallets/pallets/compute-channel/src/weights.rs", "settle"): {
        "parameter": "n: u32",
        "base_ref_time": 77_180_000,
        "proof_size": 61_416,
        "per_unit_ref_time": 35_000_000,
        "reads": 24,
        "writes": 8,
    },
    ("pallets/pallets/compute-channel/src/weights.rs", "certificate_settle"): {
        "parameter": None,
        "base_ref_time": 85_000_000,
        "proof_size": 67_152,
        "per_unit_ref_time": 0,
        "reads": 28,
        "writes": 7,
    },
    ("pallets/pallets/compute-channel/src/weights.rs", "force_settle"): {
        "parameter": "n: u32",
        "base_ref_time": 83_910_000,
        "proof_size": 31_184,
        "per_unit_ref_time": 35_000_000,
        "reads": 16,
        "writes": 6,
    },
    ("pallets/pallets/compute-channel/src/weights.rs", "finalize"): {
        "parameter": None,
        "base_ref_time": 55_440_000,
        "proof_size": 59_378,
        "per_unit_ref_time": 0,
        "reads": 21,
        "writes": 11,
    },
    ("pallets/pallets/compute-channel/src/weights.rs", "release_forward_bond"): {
        "parameter": "n: u32",
        "base_ref_time": 80_000_000,
        "proof_size": 34_384,
        "per_unit_ref_time": 35_000_000,
        "reads": 14,
        "writes": 5,
    },
    ("pallets/pallets/compute-channel/src/weights.rs", "timeout"): {
        "parameter": None,
        "base_ref_time": 45_000_000,
        "proof_size": 22_788,
        "per_unit_ref_time": 0,
        "reads": 10,
        "writes": 9,
    },
    ("pallets/pallets/compute-channel/src/weights.rs", "open_dispute"): {
        "parameter": None,
        "base_ref_time": 52_460_000,
        "proof_size": 16_560,
        "per_unit_ref_time": 0,
        "reads": 4,
        "writes": 3,
    },
    ("pallets/pallets/compute-channel/src/weights.rs", "respond_dispute"): {
        "parameter": None,
        "base_ref_time": 131_520_000,
        "proof_size": 20_328,
        "per_unit_ref_time": 0,
        "reads": 7,
        "writes": 3,
    },
    ("pallets/pallets/compute-channel/src/weights.rs", "submit_toploc_evidence"): {
        "parameter": None,
        "base_ref_time": 30_000_000,
        "proof_size": 4_000,
        "per_unit_ref_time": 0,
        "reads": 2,
        "writes": 1,
    },
}

STRUCT_SCHEMAS = {
    ("pallets/primitives/hp-poui/src/lib.rs", "ValidatorAttestation"): [
        ("task_hash", "H256"),
        ("gn_weight", "u64"),
        ("latency_ms", "u64"),
        ("model_hash", "H256"),
        ("output_hash", "H256"),
        ("decode_policy_hash", "H256"),
        ("tee_type", "TeeType"),
        ("quote_verified", "bool"),
        ("event_log_verified", "bool"),
        ("hardware_id_hash", "H256"),
        ("validator_id", "[u8; 32]"),
        ("signature", "[u8; 64]"),
    ],
    ("pallets/pallets/compute-channel/src/lib.rs", "VerifiedTurn"): [
        ("leaf_version", "crate::TranscriptLeafVersion"),
        ("turn_index", "u32"),
        ("h_in", "H256"),
        ("h_out", "H256"),
        ("g_n", "u128"),
        ("decode_policy_hash", "H256"),
        ("h_ids", "H256"),
        ("toploc_commitment_hash", "H256"),
        ("miner_recv_ms", "u64"),
        ("miner_done_ms", "u64"),
        ("latency_ms", "u64"),
        ("enclave_sig", "[u8; 64]"),
        ("merkle_path", "Vec<(H256, bool)>"),
    ],
    ("pallets/pallets/da-registry/src/lib.rs", "DataRef"): [
        ("commitment", "H256"),
        ("provider_id", "ProviderId"),
        ("retention", "RetentionClass"),
    ],
}

ENUM_SCHEMAS = {
    ("pallets/primitives/hp-poui/src/lib.rs", "TeeType"): [
        "IntelTdx",
        "NvidiaHopperCc",
        "NvidiaRubinCc",
        "Simulator",
    ],
    ("pallets/pallets/da-registry/src/lib.rs", "RetentionClass"): [
        "Ephemeral",
        "Leased",
    ],
}

VALIDATOR_FIELDS = [
    ("task_hash", "H256", 32),
    ("gn_weight", "u64", 8),
    ("latency_ms", "u64", 8),
    ("model_hash", "H256", 32),
    ("output_hash", "H256", 32),
    ("decode_policy_hash", "H256", 32),
    ("tee_type", "unit enum discriminant", 1),
    ("quote_verified", "bool", 1),
    ("event_log_verified", "bool", 1),
    ("hardware_id_hash", "H256", 32),
    ("validator_id", "[u8; 32]", 32),
    ("signature", "[u8; 64]", 64),
]

VERIFIED_TURN_FIXED_FIELDS = [
    ("leaf_version", "TranscriptLeafVersion", 1),
    ("turn_index", "u32", 4),
    ("h_in", "H256", 32),
    ("h_out", "H256", 32),
    ("g_n", "u128", 16),
    ("decode_policy_hash", "H256", 32),
    ("h_ids", "H256", 32),
    ("toploc_commitment_hash", "H256", 32),
    ("miner_recv_ms", "u64", 8),
    ("miner_done_ms", "u64", 8),
    ("latency_ms", "u64", 8),
    ("enclave_sig", "[u8; 64]", 64),
]

AUDIT_SCENARIOS = [
    {
        "scenario": "configured-selection-only",
        "p_selected": 0.05,
        "p_data_given_selected": 1.0,
        "p_challenger_given_selected_and_data": 1.0,
        "p_included_given_selected_data_and_challenge": 1.0,
        "p_upheld_given_selected_data_challenge_and_inclusion": 1.0,
        "p_collectible_given_all_prior": 1.0,
        "status": "illustrative assumptions",
    },
    {
        "scenario": "conditional-stress",
        "p_selected": 0.05,
        "p_data_given_selected": 0.90,
        "p_challenger_given_selected_and_data": 0.80,
        "p_included_given_selected_data_and_challenge": 0.95,
        "p_upheld_given_selected_data_challenge_and_inclusion": 0.90,
        "p_collectible_given_all_prior": 0.75,
        "status": "illustrative assumptions",
    },
    {
        "scenario": "data-outage",
        "p_selected": 0.05,
        "p_data_given_selected": 0.0,
        "p_challenger_given_selected_and_data": 1.0,
        "p_included_given_selected_data_and_challenge": 1.0,
        "p_upheld_given_selected_data_challenge_and_inclusion": 1.0,
        "p_collectible_given_all_prior": 1.0,
        "status": "boundary scenario",
    },
]


def compact_u32_size(value: int) -> int:
    """SCALE Compact<u32> byte length."""
    if value < 0 or value > 0xFFFF_FFFF:
        raise ValueError("expected u32")
    if value < 1 << 6:
        return 1
    if value < 1 << 14:
        return 2
    if value < 1 << 30:
        return 4
    return 5


def compact_u32(value: int) -> bytes:
    """SCALE-encode Compact<u32>."""
    if value < 0 or value > 0xFFFF_FFFF:
        raise ValueError("expected u32")
    if value < 1 << 6:
        return bytes([value << 2])
    if value < 1 << 14:
        return ((value << 2) | 1).to_bytes(2, "little")
    if value < 1 << 30:
        return ((value << 2) | 2).to_bytes(4, "little")
    return b"\x03" + value.to_bytes(4, "little")


def repeated(byte: int, size: int) -> bytes:
    return bytes([byte]) * size


def encode_validator_attestation(index: int) -> bytes:
    return b"".join(
        [
            repeated(1, 32),
            (1_000 + index).to_bytes(8, "little"),
            (10 + index).to_bytes(8, "little"),
            repeated(2, 32),
            repeated(3, 32),
            repeated(4, 32),
            b"\x00",  # TeeType::IntelTdx
            b"\x01",  # quote_verified
            b"\x01",  # event_log_verified
            repeated(5, 32),
            index.to_bytes(4, "little") + repeated(6, 28),
            repeated((0x80 + index) % 256, 64),
        ]
    )


def encode_verified_turn(index: int, path_len: int) -> bytes:
    path = b"".join(repeated(0x40 + depth, 32) + bytes([depth % 2]) for depth in range(path_len))
    return b"".join(
        [
            b"\x03",  # TranscriptLeafVersion::V3 precedes turn_index in SCALE.
            index.to_bytes(4, "little"),
            repeated(11, 32),
            repeated(12, 32),
            (1_000 + index).to_bytes(16, "little"),
            repeated(13, 32),
            repeated(14, 32),
            repeated(15, 32),
            (10 + index).to_bytes(8, "little"),
            (20 + index).to_bytes(8, "little"),
            (10).to_bytes(8, "little"),
            repeated(0x77, 64),
            compact_u32(path_len),
            path,
        ]
    )


def encode_data_ref() -> bytes:
    # Some(DataRef { commitment, provider_id=0, retention=Ephemeral }).
    return b"\x01" + repeated(20, 32) + b"\x00\x00"


def signed_extensions() -> bytes:
    # Mortal(64, phase=1), nonce=1, zero tip, metadata-hash mode disabled.
    # The other five extensions in TxExtension encode no explicit bytes.
    return b"\x15\x00" + compact_u32(1) + compact_u32(0) + b"\x00"


def encode_extrinsic(call: bytes, *, signed: bool) -> bytes:
    if signed:
        body = b"".join(
            [
                b"\x84",  # legacy v4, signed
                b"\x00" + repeated(0x11, 32),  # MultiAddress::Id
                b"\x01" + repeated(0x99, 64),  # MultiSignature::Sr25519 fixture
                signed_extensions(),
                call,
            ]
        )
    else:
        body = b"\x05" + call  # current v5 bare preamble
    return compact_u32(len(body)) + body


def encoded_row(
    scenario: str,
    call: bytes,
    *,
    signed: bool,
    dimensions: dict,
    charged_weight: dict,
) -> dict:
    extrinsic = encode_extrinsic(call, signed=signed)
    body_len = len(call) + (104 if signed else 1)
    return {
        "scenario": scenario,
        "dimensions": dimensions,
        "origin": "signed" if signed else "none",
        "runtime_pallet_index": call[0],
        "pallet_call_index": call[1],
        "call_bytes": len(call),
        "extrinsic_bytes": len(extrinsic),
        "extrinsic_length_prefix_bytes": compact_u32_size(body_len),
        "extrinsic_sha256": hashlib.sha256(extrinsic).hexdigest(),
        "charged_call_weight": charged_weight,
    }


def compute_weight(name: str, turns: int = 0) -> dict:
    weight = WEIGHT_SCHEMAS[("pallets/pallets/compute-channel/src/weights.rs", name)]
    base = weight["base_ref_time"] + weight["per_unit_ref_time"] * turns
    return {
        "ref_time": base
        + weight["reads"] * RUNTIME_DB_WEIGHT_SCHEMA["read_ref_time"]
        + weight["writes"] * RUNTIME_DB_WEIGHT_SCHEMA["write_ref_time"],
        "proof_size": weight["proof_size"],
        "class": "Normal",
        "status": "charged estimate; not freshly benchmarked",
    }


def direct_weight(signatures: int) -> dict:
    weight = WEIGHT_SCHEMAS[
        ("pallets/pallets/flop-poui/src/weights.rs", "submit_oracle_attestation")
    ]
    return {
        "ref_time": weight["base_ref_time"] * signatures,
        "proof_size": weight["proof_size"],
        "class": "Normal",
        "status": "placeholder charged weight; dedicated benchmark absent",
    }


def required_quorum(active: int) -> int:
    return max(1, (active * THRESHOLD_PARTS + PERBILL - 1) // PERBILL)


def binomial_tail(n: int, threshold: int, p: Fraction) -> Fraction:
    q = 1 - p
    return sum(
        (Fraction(math.comb(n, x)) * p**x * q ** (n - x) for x in range(threshold, n + 1)),
        start=Fraction(0),
    )


def validator_attestation_size() -> int:
    return sum(field[2] for field in VALIDATOR_FIELDS)


def validator_bundle_size(count: int) -> int:
    return compact_u32_size(count) + count * validator_attestation_size()


def verified_turn_size(path_len: int) -> int:
    if path_len < 0:
        raise ValueError("negative path length")
    return (
        sum(field[2] for field in VERIFIED_TURN_FIXED_FIELDS)
        + compact_u32_size(path_len)
        + path_len * 33
    )


def settle_call_arguments_size(turns: int, path_len: int, transcript_ref: bool = True) -> int:
    # channel_id + final_root + aggregate_gn + measured_root + receipt signature
    fixed = 32 + 32 + 16 + 32 + 64
    # SCALE Option<DataRef>: tag + H256 + ProviderId(u8) + RetentionClass(unit enum).
    data_ref = 1 + (32 + 1 + 1 if transcript_ref else 0)
    return fixed + data_ref + compact_u32_size(turns) + turns * verified_turn_size(path_len)


def ledger_digest() -> str:
    canonical = json.dumps(
        {
            "source_facts": SOURCE_FACTS,
            "struct_schemas": [
                [path, name, fields] for (path, name), fields in sorted(STRUCT_SCHEMAS.items())
            ],
            "enum_schemas": [
                [path, name, variants] for (path, name), variants in sorted(ENUM_SCHEMAS.items())
            ],
            "call_schemas": [
                [path, name, index, fields]
                for (path, name), (index, fields) in sorted(CALL_SCHEMAS.items())
            ],
            "weight_schemas": [
                [path, name, fields] for (path, name), fields in sorted(WEIGHT_SCHEMAS.items())
            ],
            "runtime_db_weight": RUNTIME_DB_WEIGHT_SCHEMA,
        },
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def declaration_body(text: str, kind: str, name: str) -> str:
    marker = f"pub {kind} {name}"
    start = text.find(marker)
    if start < 0:
        raise ValueError(f"missing {kind} {name}")
    opening = text.find("{", start)
    if opening < 0:
        raise ValueError(f"missing body for {kind} {name}")
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[opening + 1 : index]
    raise ValueError(f"unterminated {kind} {name}")


def parse_struct_fields(text: str, name: str) -> list[tuple[str, str]]:
    fields = []
    for line in declaration_body(text, "struct", name).splitlines():
        stripped = line.strip()
        if stripped.startswith("#[codec"):
            raise ValueError(f"{name} field encoding now has a codec override: {stripped}")
        if not stripped.startswith("pub "):
            continue
        declaration = stripped.removeprefix("pub ").rsplit(",", 1)[0]
        field_name, rust_type = declaration.split(":", 1)
        fields.append((field_name.strip(), rust_type.strip()))
    return fields


def parse_unit_enum_variants(text: str, name: str) -> list[str]:
    variants = []
    for line in declaration_body(text, "enum", name).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        if stripped.startswith("#[codec"):
            raise ValueError(f"{name} variant encoding now has a codec override: {stripped}")
        if stripped.startswith("#["):
            continue
        if not stripped.endswith(",") or any(char in stripped for char in "({"):
            raise ValueError(f"{name} is no longer a unit-only enum: {stripped}")
        variants.append(stripped[:-1])
    return variants


def parse_call(text: str, name: str) -> tuple[int, list[tuple[str, str]]]:
    marker = f"pub fn {name}("
    start = text.find(marker)
    if start < 0:
        raise ValueError(f"missing call {name}")
    attribute = text.rfind("#[pallet::call_index(", 0, start)
    if attribute < 0 or start - attribute > 1_000:
        raise ValueError(f"missing call index for {name}")
    index_text = text[attribute + len("#[pallet::call_index(") :].split(")]", 1)[0]
    signature = text[start + len(marker) :].split(") -> DispatchResult", 1)[0]
    fields = []
    for line in signature.splitlines():
        stripped = line.strip().rstrip(",")
        if stripped.startswith("origin:") and "," in stripped:
            stripped = stripped.split(",", 1)[1].strip()
        if not stripped or stripped.startswith("origin:"):
            continue
        field_name, rust_type = stripped.split(":", 1)
        fields.append((field_name.strip(), rust_type.strip()))
    return int(index_text), fields


def parse_weight(text: str, name: str, parameter: str | None) -> dict:
    marker = f"fn {name}({parameter or ''}) -> Weight {{"
    start = text.find(marker)
    if start < 0:
        raise ValueError(f"missing weight {name}")
    opening = text.find("{", start)
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                body = text[opening + 1 : index]
                break
    else:
        raise ValueError(f"unterminated weight {name}")
    body = re.sub(r"//[^\n]*", "", body)
    parts = re.compile(
        r"Weight::from_parts\(\s*([\d_]+),\s*([\d_]+)\s*\)"
        r"(?:\s*\.saturating_mul\(([^)]*)\))?"
    )
    totals = {"base_ref_time": 0, "proof_size": 0, "per_unit_ref_time": 0}
    part_count = 0

    def weight_part(match: re.Match) -> str:
        nonlocal part_count
        part_count += 1
        ref_time, proof_size = (int(match[index].replace("_", "")) for index in (1, 2))
        multiplier = match[3]
        if multiplier is not None:
            expected = f"{parameter.split(':', 1)[0]} as u64" if parameter else None
            if multiplier.strip() != expected or proof_size:
                raise ValueError(f"unsupported per-unit weight for {name}")
            totals["per_unit_ref_time"] += ref_time
        else:
            totals["base_ref_time"] += ref_time
            totals["proof_size"] += proof_size
        return "PART"

    expression = parts.sub(weight_part, body)
    if not part_count:
        raise ValueError(f"missing Weight::from_parts for {name}")
    db_counts = {"reads": 0, "writes": 0}

    def db_part(match: re.Match) -> str:
        db_counts[match[1]] += int(match[2])
        return "PART"

    expression = re.sub(
        r"(?:T::DbWeight::get|RocksDbWeight::get)\(\)\.(reads|writes)\((\d+)\)",
        db_part,
        expression,
    )
    expression = re.sub(r"\s+", "", expression)
    if not re.fullmatch(r"PART(?:\.saturating_add\(PART\))*", expression):
        raise ValueError(f"unsupported weight expression for {name}")
    return {"parameter": parameter, **totals, **db_counts}


def parse_runtime_db_weight(text: str) -> dict[str, int]:
    values = {}
    for operation in ("read", "write"):
        match = re.search(
            rf"\b{operation}:\s*([\d_]+)\s*\*\s*constants::WEIGHT_REF_TIME_PER_NANOS",
            text,
        )
        if not match:
            raise ValueError(f"missing runtime RocksDbWeight {operation} cost")
        values[f"{operation}_ref_time"] = (
            int(match.group(1).replace("_", "")) * WEIGHT_REF_TIME_PER_NANOS
        )
    return values


def verify_source_facts(repo: Path) -> list[str]:
    errors: list[str] = []
    texts: dict[str, str] = {}
    for relative, needles in SOURCE_FACTS.items():
        path = repo / relative
        if not path.is_file():
            errors.append(f"missing source: {relative}")
            continue
        text = texts.setdefault(relative, path.read_text())
        for needle in needles:
            if needle not in text:
                errors.append(f"stale source fact: {relative}: {needle}")
    for (relative, name), expected in STRUCT_SCHEMAS.items():
        try:
            text = texts.setdefault(relative, (repo / relative).read_text())
            actual = parse_struct_fields(text, name)
            if actual != expected:
                errors.append(f"stale struct schema: {relative}:{name}: {actual!r}")
        except (OSError, ValueError) as error:
            errors.append(f"cannot verify struct schema: {relative}:{name}: {error}")
    for (relative, name), expected in ENUM_SCHEMAS.items():
        try:
            text = texts.setdefault(relative, (repo / relative).read_text())
            actual = parse_unit_enum_variants(text, name)
            if actual != expected:
                errors.append(f"stale enum schema: {relative}:{name}: {actual!r}")
        except (OSError, ValueError) as error:
            errors.append(f"cannot verify enum schema: {relative}:{name}: {error}")
    for (relative, name), expected in CALL_SCHEMAS.items():
        try:
            text = texts.setdefault(relative, (repo / relative).read_text())
            actual = parse_call(text, name)
            if actual != expected:
                errors.append(f"stale call schema: {relative}:{name}: {actual!r}")
        except (OSError, ValueError) as error:
            errors.append(f"cannot verify call schema: {relative}:{name}: {error}")
    for (relative, name), expected in WEIGHT_SCHEMAS.items():
        try:
            text = texts.setdefault(relative, (repo / relative).read_text())
            actual = parse_weight(text, name, expected["parameter"])
            if actual != expected:
                errors.append(f"stale weight schema: {relative}:{name}: {actual!r}")
        except (OSError, ValueError) as error:
            errors.append(f"cannot verify weight schema: {relative}:{name}: {error}")
    try:
        text = texts.setdefault(
            RUNTIME_DB_WEIGHT_SOURCE, (repo / RUNTIME_DB_WEIGHT_SOURCE).read_text()
        )
        actual = parse_runtime_db_weight(text)
        if actual != RUNTIME_DB_WEIGHT_SCHEMA:
            errors.append(f"stale runtime DB weight schema: {actual!r}")
    except (OSError, ValueError) as error:
        errors.append(f"cannot verify runtime DB weight schema: {error}")
    return errors


def committee_analysis() -> dict:
    bad_count, honest_count, bad_stake, honest_stake, committee_size = 40, 61, 1, 3, 100
    population = bad_count + honest_count
    omitted = population - committee_size
    min_bad_seats = max(0, bad_count - omitted)
    max_bad_seats = min(bad_count, committee_size)
    eligible_bad_stake = Fraction(
        bad_count * bad_stake, bad_count * bad_stake + honest_count * honest_stake
    )
    minimum_committee_bad_stake = Fraction(39, 39 + 183)
    maximum_committee_bad_stake = Fraction(40, 40 + 180)
    threshold = 34
    comparison = binomial_tail(committee_size, threshold, eligible_bad_stake)
    return {
        "status": "exact finite-population arithmetic; counterexample, not an exploit theorem",
        "population": {
            "stake_unit": "common scale at least the eligibility floor; all identities assumed work-eligible",
            "bad_identities": bad_count,
            "bad_stake_each": bad_stake,
            "honest_identities": honest_count,
            "honest_stake_each": honest_stake,
            "total_identities": population,
            "total_stake": 223,
            "bad_stake_fraction": f"{eligible_bad_stake.numerator}/{eligible_bad_stake.denominator}",
            "bad_stake_percent": float(eligible_bad_stake * 100),
        },
        "draw": {
            "distinct_identities": committee_size,
            "omitted_identities": omitted,
            "possible_bad_seats": [min_bad_seats, max_bad_seats],
            "possible_bad_seat_percent": [39.0, 40.0],
            "possible_bad_committee_stake_percent": [
                float(minimum_committee_bad_stake * 100),
                float(maximum_committee_bad_stake * 100),
            ],
            "probability_bad_seats_at_least_34": 1.0,
            "reason": "Any 100-subset of 101 omits one identity, hence omits at most one of 40 bad identities.",
        },
        "binomial_comparison": {
            "model": "Binom(100, 40/223), independent with-replacement seats",
            "threshold_bad_seats": threshold,
            "tail_exact_numerator": str(comparison.numerator),
            "tail_exact_denominator": str(comparison.denominator),
            "tail_probability": float(comparison),
            "scope": "Comparison model only. It does not describe the unequal-weight distinct-identity draw in this counterexample.",
        },
        "conclusion": "The actual tail is 1, so SelectionTailDominated at f=34 is false for this population and p=40/223.",
    }


def direct_rail_analysis() -> dict:
    encoded = validator_attestation_size()
    rows = []
    for active in (100, RUNTIME_MAX_ACTIVE_VALIDATORS):
        quorum = required_quorum(active)
        attestations = b"".join(encode_validator_attestation(index) for index in range(quorum))
        call = bytes([RUNTIME_PALLET_INDICES["FlopPoui"], 15]) + compact_u32(quorum) + attestations
        rows.append(
            encoded_row(
                "direct_validator_attestation_quorum",
                call,
                signed=False,
                dimensions={"active_validators": active, "required_signatures": quorum},
                charged_weight=direct_weight(quorum),
            )
        )
    return {
        "status": "deterministic SCALE serialization from a source-checked runtime wire ledger",
        "validator_attestation_fields": [
            {"name": name, "type": typ, "bytes": size} for name, typ, size in VALIDATOR_FIELDS
        ],
        "validator_attestation_bytes": encoded,
        "call_formula": "runtime_pallet_index + pallet_call_index + compact_len(n) + 275*n",
        "extrinsic_format": "v5 bare: Compact(body_len) || 0x05 || RuntimeCall",
        "rows": rows,
        "active_set": {
            "supported_sizes_exercised": [100, RUNTIME_MAX_ACTIVE_VALIDATORS],
            "runtime_max": RUNTIME_MAX_ACTIVE_VALIDATORS,
            "unsupported_boundary": {
                "active_validators": 1_000,
                "status": "not a supported active-set state; excluded from capacity rows",
            },
        },
        "finality_committee": {
            "runtime_cap": FINALITY_COMMITTEE_CAP,
            "relationship": "separate from the direct-rail active-validator quorum",
            "serialized_call": "none; finality messages are network traffic, not RuntimeCall extrinsics",
        },
        "limits": [
            "Fixture attestation signature fields are populated but not cryptographically validated by this serializer.",
            "The charged direct weight is explicitly a placeholder and has zero proof-size charge.",
            "No count is divided into a byte budget or reported as throughput.",
        ],
    }


def session_analysis() -> dict:
    matrix = []
    for turns in (1, 16, 128, 1_024):
        for path_len in (0, 8, 32, 64):
            verified_turns = b"".join(
                encode_verified_turn(index, path_len) for index in range(turns)
            )
            arguments = b"".join(
                [
                    repeated(10, 32),
                    repeated(24, 32),
                    (1_000 * turns).to_bytes(16, "little"),
                    repeated(22, 32),
                    repeated(0x66, 64),
                    encode_data_ref(),
                    compact_u32(turns),
                    verified_turns,
                ]
            )
            dimensions = {
                "turns": turns,
                "merkle_path_entries_per_turn": path_len,
                "transcript_data_ref": "Some(Ephemeral sovereign-validator ref)",
                "turn_indices": "unique",
            }
            for scenario, call_index in (
                ("cooperative_settle", 2),
                ("unilateral_force_settle", 3),
            ):
                call = bytes([RUNTIME_PALLET_INDICES["ComputeChannel"], call_index]) + arguments
                matrix.append(
                    encoded_row(
                        scenario,
                        call,
                        signed=True,
                        dimensions=dimensions,
                        charged_weight=compute_weight(
                            "settle" if call_index == 2 else "force_settle", turns
                        ),
                    )
                )

    duplicate_turns = b"".join(encode_verified_turn(index, 0) for index in range(127))
    duplicate_turns += encode_verified_turn(0, 0)
    duplicate_arguments = b"".join(
        [
            repeated(10, 32),
            repeated(24, 32),
            (128_000).to_bytes(16, "little"),
            repeated(22, 32),
            repeated(0x66, 64),
            encode_data_ref(),
            compact_u32(128),
            duplicate_turns,
        ]
    )
    duplicate = encoded_row(
        "cooperative_settle_duplicate_last",
        bytes([RUNTIME_PALLET_INDICES["ComputeChannel"], 2]) + duplicate_arguments,
        signed=True,
        dimensions={
            "turns": 128,
            "merkle_path_entries_per_turn": 0,
            "turn_indices": "duplicate_last",
        },
        charged_weight=compute_weight("settle", 128),
    )

    open_arguments = b"".join(
        [
            repeated(0x44, 32),
            repeated(21, 32),
            repeated(22, 32),
            repeated(23, 32),
            b"\x01",  # ModelPrecision::FP16
            repeated(0x33, 32),
            repeated(0x55, 32),
            (1_024).to_bytes(4, "little"),
            (3_600).to_bytes(4, "little"),
            (64).to_bytes(4, "little"),
            (10**18).to_bytes(16, "little"),
            (1).to_bytes(8, "little"),
            b"\x00",  # SettlementClass::Standard
        ]
    )
    controls = [
        encoded_row(
            "open_channel",
            bytes([RUNTIME_PALLET_INDICES["ComputeChannel"], 0]) + open_arguments,
            signed=True,
            dimensions={},
            charged_weight=compute_weight("open_channel"),
        ),
        encoded_row(
            "toploc_evidence_publication",
            bytes([RUNTIME_PALLET_INDICES["ComputeChannel"], 21])
            + repeated(10, 32)
            + repeated(25, 32),
            signed=True,
            dimensions={},
            charged_weight=compute_weight("submit_toploc_evidence"),
        ),
        encoded_row(
            "open_dispute",
            bytes([RUNTIME_PALLET_INDICES["ComputeChannel"], 6])
            + repeated(10, 32)
            + (127).to_bytes(4, "little"),
            signed=True,
            dimensions={},
            charged_weight=compute_weight("open_dispute"),
        ),
        encoded_row(
            "respond_dispute_max_path",
            bytes([RUNTIME_PALLET_INDICES["ComputeChannel"], 7])
            + repeated(10, 32)
            + encode_verified_turn(127, 64),
            signed=True,
            dimensions={"merkle_path_entries": 64},
            charged_weight=compute_weight("respond_dispute"),
        ),
        encoded_row(
            "finalize_unilateral_settlement",
            bytes([RUNTIME_PALLET_INDICES["ComputeChannel"], 4]) + repeated(10, 32),
            signed=True,
            dimensions={},
            charged_weight=compute_weight("finalize"),
        ),
    ]
    return {
        "status": "deterministic SCALE serialization plus charged runtime weights; not dispatch or benchmark results",
        "encoding": {
            "extrinsic_format": "v4 signed: Compact(body_len) || 0x84 || MultiAddress || MultiSignature || TxExtension || RuntimeCall",
            "signed_extension_order": [
                "CheckNonZeroSender",
                "CheckSpecVersion",
                "CheckTxVersion",
                "CheckGenesis",
                "CheckMortality",
                "CheckNonce",
                "CheckWeight",
                "ChargeTransactionPayment",
                "CheckMetadataHash",
            ],
            "signed_extension_fixture_hex": signed_extensions().hex(),
            "outer_signature": "MultiSignature::Sr25519 field populated with deterministic fixture bytes; validity not asserted",
        },
        "verified_turn_fixed_fields": [
            {"name": name, "type": typ, "bytes": size}
            for name, typ, size in VERIFIED_TURN_FIXED_FIELDS
        ],
        "fixed_bytes_per_turn": sum(field[2] for field in VERIFIED_TURN_FIXED_FIELDS),
        "merkle_entry_bytes": 33,
        "verified_turn_formula": "269 + compact_len(path_len) + 33*path_len",
        "settle_argument_formula_with_data_ref": "176 + 35 + compact_len(turns) + turns*verified_turn_bytes",
        "settle_argument_formula_without_data_ref": "176 + 1 + compact_len(turns) + turns*verified_turn_bytes",
        "leaf_preimage_bytes": {"v0": 116, "v1": 140, "v2": 172, "v3": 236},
        "version_note": "VerifiedTurn carries an explicit V0-V3 tag. Verification selects exactly that fixed preimage and never retries another version.",
        "work_note": "Verification loops over turns and path entries; duplicate detection scans prior turns, giving O(turns^2) comparisons in the worst case.",
        "caps": {"turns": 1_024, "path_entries_per_turn": 64},
        "matrix": matrix,
        "duplicate_scan": duplicate,
        "control_calls": controls,
        "limits": [
            "Rows include pallet/call indices, signatures, signed extensions, length prefixes, and Some(DataRef).",
            "Encoded fixtures are not dispatched and signature fields are not validated.",
            "Charged weights are source values, not fresh measurements; path length and duplicate-scan work are not weight parameters.",
        ],
    }


def audit_analysis() -> dict:
    rows = []
    keys = [key for key in AUDIT_SCENARIOS[0] if key.startswith("p_")]
    for scenario in AUDIT_SCENARIOS:
        p_effective = math.prod(float(scenario[key]) for key in keys)
        rows.append(
            {
                **scenario,
                "p_effective": p_effective,
                "max_profitable_exposure_per_unit_collectible_collateral": p_effective,
            }
        )
    return {
        "status": "conditional scenarios; inputs are illustrative, not measurements",
        "formula": "p_effective = P(S)*P(D|S)*P(C|S,D)*P(I|S,D,C)*P(U|S,D,C,I)*P(K|S,D,C,I,U)",
        "exposure_condition": "total_profitable_exposure < p_effective * collectible_slashable_collateral",
        "interpretation": "Each factor conditions on every prior gate succeeding; this is the probability chain rule and does not assert independence.",
        "rows": rows,
        "open_inputs": [
            "Data availability over the full challenge window",
            "Challenger participation and cost/reward model",
            "Transaction inclusion before deadline",
            "Adjudication false-negative rate for the specified attack class",
            "Collateral reservation across concurrent exposure and collectibility at slash time",
        ],
    }


def capacity_evidence_status() -> dict:
    return {
        "claim_disposition": {
            "status": "removed from the v0.5 conformance profile",
            "removed_claims": [
                "125,000-byte propagation budget",
                "96 steady / 128 burst session-control transactions per block",
                "48 steady / 64 burst cooperative lifecycles per second",
                "sub-second finality latency",
            ],
            "replacement": "No capacity or latency guarantee. Runtime admission remains jointly byte-, weight-, state-, and validity-gated.",
        },
        "runtime_envelope": {
            "normal_max_bytes": NORMAL_MAX_BYTES,
            "operational_max_bytes": OPERATIONAL_MAX_BYTES,
            "normal_max_ref_time": NORMAL_MAX_REF_TIME,
            "operational_max_ref_time": MAX_BLOCK_REF_TIME,
            "scope": "configured maxima, not serving/finality measurements; base block/extrinsic work and competing traffic consume the envelope",
        },
        "runtime_benchmark_build": {
            "status": "blocked; no benchmarked weight is claimed",
            "command": "WASM_BUILD_WORKSPACE_HINT=$PWD/pallets cargo check --manifest-path pallets/Cargo.toml -p zkv-runtime --features runtime-benchmarks",
            "diagnosis": "The runtime mixes incompatible Polkadot SDK generations (including sp-runtime 39/45/47, sp-core 34/41/43, and sp-io 38/48).",
            "failures": [
                "host and WASM compilation hit cross-version KeyTypeId and crypto/hash API errors",
                "WASM crates link multiple sp-io implementations and abort on duplicate lang item panic_impl",
            ],
            "tracking": "#550",
            "runtime_wasm_hash": None,
            "benchmark_output_hash": None,
        },
        "network_workload_matrix": {
            "status": "not run; no throughput or latency sample exists",
            "raw_log_paths": [],
            "runtime_hash": None,
            "workload_generator": None,
            "seeds": [],
            "hardware_resource_profile": None,
            "required_dimensions": {
                "finality_committee": "all supported realized sizes up to the runtime cap of 100",
                "topology": ["single-region", "multi-region"],
                "latency_loss": "disclosed latency and packet-loss sweep",
                "node_gpu_hardware": "CPU, memory, disk, NIC, GPU, driver, and TEE profile",
                "offered_load": "sustained below, at, and above admission",
                "settlement": "turn counts 1/16/128/1024; path lengths 0/8/32/64; duplicate-last",
                "co_load": ["DA/checker", "ordinary Normal", "Operational"],
                "faults": [
                    "below one-third seats",
                    "partition/recovery",
                    "at one-third",
                    "above one-third",
                ],
            },
            "required_outputs": [
                "admission failures, backlog, and stalled runs",
                "sustained finalized lifecycle throughput",
                "inclusion and finality p50/p95/p99 plus tail stalls",
                "resource saturation, duration, warm-up, repetitions, and uncertainty",
                "chain capacity, serving capacity, and client-perceived latency",
            ],
        },
    }


def build_report() -> dict:
    return {
        "schema_version": 2,
        "generated_by": "evidence/reproduce.py",
        "scope": "Deterministic SCALE fixtures, charged-weight ledger, and claim disposition; no runtime execution, empirical security assurance, or network benchmark.",
        "embedded_ledger_sha256": ledger_digest(),
        "wire_ledger_assumptions": [
            "parity-scale-codec primitive/container encoding",
            "sp-runtime 47 UncheckedExtrinsic: current v5 bare and legacy v4 signed preambles",
            "runtime RocksDbWeight read=9,372,000 and write=71,631,000 ref-time",
        ],
        "source_inputs": [
            {"path": path, "required_fragments": facts}
            for path, facts in sorted(SOURCE_FACTS.items())
        ],
        "source_schema_constraints": [
            {"path": path, "declaration": name, "ordered_fields": fields}
            for (path, name), fields in sorted(STRUCT_SCHEMAS.items())
        ]
        + [
            {"path": path, "declaration": name, "unit_variants": variants}
            for (path, name), variants in sorted(ENUM_SCHEMAS.items())
        ]
        + [
            {"path": path, "call": name, "index": index, "ordered_fields": fields}
            for (path, name), (index, fields) in sorted(CALL_SCHEMAS.items())
        ]
        + [
            {"path": path, "weight": name, **fields}
            for (path, name), fields in sorted(WEIGHT_SCHEMAS.items())
        ],
        "capacity_evidence": capacity_evidence_status(),
        "committee_counterexample": committee_analysis(),
        "direct_attestation_rail": direct_rail_analysis(),
        "session_settlement": session_analysis(),
        "audit_exposure": audit_analysis(),
    }


def render_json(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_csv(report: dict) -> str:
    output = io.StringIO(newline="")
    fields = ["analysis", "scenario", "metric", "value", "unit", "status", "notes"]
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    committee = report["committee_counterexample"]
    for metric, value, unit in (
        ("eligible_bad_stake_fraction", committee["population"]["bad_stake_fraction"], "fraction"),
        ("minimum_bad_seats", committee["draw"]["possible_bad_seats"][0], "seats"),
        ("maximum_bad_seats", committee["draw"]["possible_bad_seats"][1], "seats"),
        ("actual_probability_bad_seats_ge_34", 1.0, "probability"),
        (
            "binomial_probability_bad_seats_ge_34",
            committee["binomial_comparison"]["tail_probability"],
            "probability",
        ),
    ):
        writer.writerow(
            {
                "analysis": "committee",
                "scenario": "40x1_bad_61x3_honest_k100",
                "metric": metric,
                "value": value,
                "unit": unit,
                "status": committee["status"],
                "notes": committee["conclusion"],
            }
        )
    for row in report["direct_attestation_rail"]["rows"]:
        dimensions = row["dimensions"]
        for metric, unit in (
            ("call_bytes", "bytes"),
            ("extrinsic_bytes", "bytes"),
            ("ref_time", "weight ref_time"),
            ("proof_size", "weight proof bytes"),
        ):
            value = row[metric] if metric in row else row["charged_call_weight"][metric]
            writer.writerow(
                {
                    "analysis": "direct-rail",
                    "scenario": f"active_{dimensions['active_validators']}_quorum_{dimensions['required_signatures']}",
                    "metric": metric,
                    "value": value,
                    "unit": unit,
                    "status": report["direct_attestation_rail"]["status"],
                    "notes": row["charged_call_weight"]["status"],
                }
            )
    session = report["session_settlement"]
    session_rows = session["matrix"] + [session["duplicate_scan"]] + session["control_calls"]
    for row in session_rows:
        for metric, unit in (
            ("call_bytes", "bytes"),
            ("extrinsic_bytes", "bytes"),
            ("ref_time", "weight ref_time"),
            ("proof_size", "weight proof bytes"),
        ):
            value = row[metric] if metric in row else row["charged_call_weight"][metric]
            writer.writerow(
                {
                    "analysis": "session",
                    "scenario": row["scenario"]
                    + "_"
                    + "_".join(f"{key}_{value}" for key, value in row["dimensions"].items()),
                    "metric": metric,
                    "value": value,
                    "unit": unit,
                    "status": session["status"],
                    "notes": row["charged_call_weight"]["status"],
                }
            )
    for row in report["audit_exposure"]["rows"]:
        writer.writerow(
            {
                "analysis": "audit-exposure",
                "scenario": row["scenario"],
                "metric": "p_effective",
                "value": row["p_effective"],
                "unit": "probability",
                "status": row["status"],
                "notes": "conditional chain; inputs are not empirical estimates",
            }
        )
    return output.getvalue()


def discover_repo(script: Path) -> Path | None:
    for parent in script.resolve().parents:
        if (parent / "pallets/primitives/hp-poui/src/lib.rs").is_file():
            return parent
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if committed artifacts differ")
    parser.add_argument(
        "--verify-sources", action="store_true", help="require and check flop-core sources"
    )
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args(argv)

    script = Path(__file__)
    repo = args.source_root or discover_repo(script)
    if args.verify_sources and repo is None:
        parser.error("--verify-sources requires a flop-core source root")
    if repo is not None:
        errors = verify_source_facts(repo)
        if errors:
            raise SystemExit("\n".join(errors))

    if args.out_dir:
        out_dir = args.out_dir
    elif repo is not None:
        out_dir = repo / "whitepaper/evidence"
    else:
        out_dir = script.resolve().parent

    report = build_report()
    artifacts = {
        "yellowpaper-claim-evidence.json": render_json(report),
        "yellowpaper-claim-evidence.csv": render_csv(report),
    }
    if args.check:
        stale = [
            name
            for name, content in artifacts.items()
            if not (out_dir / name).is_file() or (out_dir / name).read_text() != content
        ]
        if stale:
            raise SystemExit("stale generated evidence: " + ", ".join(stale))
        print(f"claim evidence: OK ({ledger_digest()[:12]}; {len(artifacts)} artifacts)")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    for name, content in artifacts.items():
        (out_dir / name).write_text(content)
    print(f"wrote {len(artifacts)} artifacts to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
