#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4.23,<5"]
# ///
"""Generate/check the public Appendix F interoperable wire vectors."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from hashlib import sha256
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "sdk/python/src/flop_sdk/compute_channel.py"
if not MODULE_PATH.exists():
    MODULE_PATH = Path(__file__).with_name("compute-channel.py")
SPEC = importlib.util.spec_from_file_location("_wire_compute_channel", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {MODULE_PATH}")
wire = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wire
SPEC.loader.exec_module(wire)

CHANNEL_ID_DOMAIN_V1 = wire.CHANNEL_ID_DOMAIN_V1
RECEIPT_DOMAIN = wire.RECEIPT_DOMAIN
TASK_HASH_DOMAIN_V1 = wire.TASK_HASH_DOMAIN_V1
TranscriptLeafVersion = wire.TranscriptLeafVersion
TurnRecord = wire.TurnRecord
channel_id_v1 = wire.channel_id_v1
compact_u32 = wire.compact_u32
decode_compact_u32 = wire.decode_compact_u32
decode_transcript_blob = wire.decode_transcript_blob
encode_transcript_blob = wire.encode_transcript_blob
encode_verified_turn = wire.encode_verified_turn
h_ids = wire.h_ids
leaf_preimage = wire.leaf_preimage
legacy_receipt_message = wire.legacy_receipt_message
merkle_path = wire.merkle_path
merkle_root = wire.merkle_root
receipt_message_v1 = wire.receipt_message_v1
root_from_path = wire.root_from_path
task_hash_v1 = wire.task_hash_v1
transcript_leaf = wire.transcript_leaf

OUTPUT = ROOT / "whitepaper/evidence/wire-format-v1.json"
if not OUTPUT.parent.exists():
    OUTPUT = Path(__file__).with_name("wire-format-v1.json")
SCHEMA_PATH = OUTPUT.with_name("wire-format-v1.schema.json")
ZERO = bytes(32)


def canonical_relative(path: Path, root: Path) -> Path:
    """Return a stable relative path when either spelling crosses a symlink."""
    return path.resolve().relative_to(root.resolve())


def hx(value: bytes) -> str:
    return value.hex()


def repeat(byte: int, length: int = 32) -> bytes:
    return bytes([byte]) * length


def build() -> dict[str, object]:
    genesis = bytes(range(32))
    agent, miner = repeat(0x11), repeat(0x22)
    channel_id = channel_id_v1(genesis, agent, miner, 42)
    fields: dict[str, object] = {
        "channel_id": channel_id,
        "turn_index": 0xFFFF_FFFF,
        "h_in": repeat(0x33),
        "h_out": repeat(0x44),
        "g_n": (1 << 128) - 1,
        "decode_policy_hash": repeat(0x66),
        "ids_hash": h_ids([], [0, 0xFFFF_FFFF]),
        "toploc_commitment_hash": repeat(0x77),
        "miner_recv_ms": (1 << 64) - 3,
        "miner_done_ms": (1 << 64) - 2,
        "latency_ms": 1,
    }
    leaves = {version.name: transcript_leaf(version, **fields) for version in TranscriptLeafVersion}
    tree_leaves = [leaves["V1"], leaves["V2"], leaves["V3"]]
    path = merkle_path(tree_leaves, 2)
    legacy_path = merkle_path(tree_leaves, 0)
    root = merkle_root(tree_leaves)
    assert root_from_path(tree_leaves[2], path) == root

    enclave_public_key = bytes.fromhex(
        "b41236c517514b30a4d6619f4b4354a2ce593cd4b64a7c29dd45e3de6972997a"
    )
    leaf_signature = bytes.fromhex(
        "94f2f8b99c2080051b431786b410153a928c37eff5054d6e2ab5a109f4a69148"
        "d9113049764e517c2f9a1a8122a606a8366370f59440d3aabbfc289aeea72086"
    )
    legacy_leaf_signature = bytes.fromhex(
        "f0644a3f19b6ac702d30830163401c5a037010fa97231e19295de385acad4029ac"
        "534e04ed9fc181c0de77c5f10507ed1cd90dd3b1163a6fe24de2acca572986"
    )
    record = TurnRecord(
        TranscriptLeafVersion.V3,
        fields["turn_index"],  # type: ignore[arg-type]
        fields["h_in"],  # type: ignore[arg-type]
        fields["h_out"],  # type: ignore[arg-type]
        fields["g_n"],  # type: ignore[arg-type]
        fields["decode_policy_hash"],  # type: ignore[arg-type]
        fields["ids_hash"],  # type: ignore[arg-type]
        fields["toploc_commitment_hash"],  # type: ignore[arg-type]
        fields["miner_recv_ms"],  # type: ignore[arg-type]
        fields["miner_done_ms"],  # type: ignore[arg-type]
        fields["latency_ms"],  # type: ignore[arg-type]
        leaf_signature,
    )
    blob = encode_transcript_blob(channel_id, [record])
    assert decode_transcript_blob(blob) == (channel_id, [record])
    verified_turn = encode_verified_turn(record, path)
    wrong_path = list(path)
    wrong_path[0] = (wrong_path[0][0], not wrong_path[0][1])
    wrong_path_turn = encode_verified_turn(record, wrong_path)
    wrong_version_turn = bytes([TranscriptLeafVersion.V2]) + verified_turn[1:]
    legacy_record = TurnRecord(
        TranscriptLeafVersion.V1,
        fields["turn_index"],  # type: ignore[arg-type]
        fields["h_in"],  # type: ignore[arg-type]
        fields["h_out"],  # type: ignore[arg-type]
        fields["g_n"],  # type: ignore[arg-type]
        None,
        None,
        None,
        fields["miner_recv_ms"],  # type: ignore[arg-type]
        fields["miner_done_ms"],  # type: ignore[arg-type]
        fields["latency_ms"],  # type: ignore[arg-type]
        legacy_leaf_signature,
    )
    legacy_verified_turn = encode_verified_turn(legacy_record, legacy_path)

    # hp-poui default DecodePolicy SCALE encoding.
    sampling = (0).to_bytes(4, "little") + (1_000_000).to_bytes(4, "little")
    sampling += (0).to_bytes(4, "little") + (1_000_000).to_bytes(4, "little")
    sampling += (1).to_bytes(2, "little") + (0).to_bytes(8, "little")
    decode_policy_scale = b"\x01\x00\x00" + ZERO + sampling + ZERO + b"\x00" + ZERO
    decode_policy_hash = sha256(b"FLOP_DECODE_POLICY_HASH_V1" + decode_policy_scale).digest()

    model_hash, output_hash, hardware_hash = repeat(0x02), repeat(0x03), repeat(0x04)
    payload_hash, commit_hash = repeat(0x05), repeat(0x06)
    task_hash = task_hash_v1(genesis, agent, 7, model_hash, payload_hash, commit_hash)
    task_preimage = (
        TASK_HASH_DOMAIN_V1
        + b"\x01"
        + genesis
        + agent
        + (7).to_bytes(8, "little")
        + model_hash
        + payload_hash
        + commit_hash
    )
    report_preimage = (
        task_hash
        + (42).to_bytes(8, "little")
        + (500).to_bytes(8, "little")
        + model_hash
        + output_hash
        + decode_policy_hash
        + b"\x00"
    )
    report_data = sha256(report_preimage).digest() + ZERO
    attestation_signable = report_preimage + b"\x01\x01" + hardware_hash
    validator_id = bytes.fromhex("b41236c517514b30a4d6619f4b4354a2ce593cd4b64a7c29dd45e3de6972997a")
    attestation_signature = bytes.fromhex(
        "90cdb722faea5e0a46b6a4e4e332e14b5d80cd175c9293577c9a356bd8a98d0e"
        "774333666dc04cca932742e08a56e441aa4cdbadf4dabe3af0e8644e63e60b88"
    )
    attestation_scale = attestation_signable + validator_id + attestation_signature
    data_ref_scale = repeat(0x88) + b"\x00\x00"

    signed_channel, signed_root = repeat(0x11), repeat(0x22)
    receipt = receipt_message_v1(signed_channel, signed_root, 42, 1_000)
    receipt_signature = bytes.fromhex(
        "7803f98d0297c23f5df90f4bce093492de9658045d3d2296717a1e718e8bc40d"
        "891e60e517fdc459f59140b289d9fcba90809493875b5d8e77325b0ec9572683"
    )
    legacy_receipt = legacy_receipt_message(signed_channel, signed_root, 42, 1_000)
    legacy_receipt_signature = bytes.fromhex(
        "a0f54ce7f97e6e8e76a4ddf6b8785ec5efd243b4a335b7954504a5c19faee620"
        "e881741ae3cfbb56cd503d17e91cd5406ffc1a8d7478108854cd781aade52687"
    )

    compact_values = [0, 63, 64, 16_383, 16_384, (1 << 30) - 1, 1 << 30, 0xFFFF_FFFF]
    compact_vectors = []
    for value in compact_values:
        encoded = compact_u32(value)
        assert decode_compact_u32(encoded) == (value, len(encoded))
        compact_vectors.append({"value": value, "bytes_hex": hx(encoded), "expected": "accept"})

    return {
        "$schema": "wire-format-v1.schema.json",
        "profile": "flop-wire-v1",
        "status": "public-canonical",
        "generation": {
            "vectors": "uv run --script scripts/generate_wire_format_vectors.py --check",
            "public_vectors": "uv run --script evidence/generate-wire-format-vectors.py --check",
            "signature": (
                "cargo run --quiet --manifest-path sdk/rust-compute-channel/Cargo.toml "
                "--example wire_signature"
            ),
        },
        "codec": {
            "fixed_integers": "unsigned little-endian; reject overflow; no rounding",
            "scale_bool": {"false": "00", "true": "01", "other": "reject"},
            "scale_compact_u32": compact_vectors,
            "malformed_compact": [
                {"bytes_hex": "", "expected": "reject", "reason": "truncated"},
                {"bytes_hex": "fd", "expected": "reject", "reason": "truncated mode 1"},
                {"bytes_hex": "feffff", "expected": "reject", "reason": "truncated mode 2"},
                {"bytes_hex": "0100", "expected": "reject", "reason": "overlong zero"},
                {"bytes_hex": "0301000000", "expected": "reject", "reason": "overlong big mode"},
                {"bytes_hex": "070000000000", "expected": "reject", "reason": "exceeds u32"},
            ],
        },
        "decode_policy_v1": {
            "input": "hp_poui::DecodePolicy::default()",
            "scale_bytes_hex": hx(decode_policy_scale),
            "hash_preimage_hex": hx(b"FLOP_DECODE_POLICY_HASH_V1" + decode_policy_scale),
            "sha256_hex": hx(decode_policy_hash),
            "expected": "accept",
        },
        "direct_rail_v1": {
            "task_hash": {
                "inputs": {
                    "genesis_hash_hex": hx(genesis),
                    "agent_account_id32_hex": hx(agent),
                    "nonce": 7,
                    "model_hash_hex": hx(model_hash),
                    "payload_hash_hex": hx(payload_hash),
                    "commit_hash_hex": hx(commit_hash),
                },
                "preimage_hex": hx(task_preimage),
                "hash_hex": hx(task_hash),
                "runtime_boundary": (
                    "producer-derived; runtime stores opaque H256 in ProcessedTasks"
                ),
            },
            "inputs": {
                "task_hash_hex": hx(task_hash),
                "gn_weight": 42,
                "latency_ms": 500,
                "model_hash_hex": hx(model_hash),
                "output_hash_hex": hx(output_hash),
                "decode_policy_hash_hex": hx(decode_policy_hash),
                "tee_type": {"name": "IntelTdx", "scale_tag": 0},
                "quote_verified": True,
                "event_log_verified": True,
                "hardware_id_hash_hex": hx(hardware_hash),
            },
            "report_data_preimage_hex": hx(report_preimage),
            "report_data_hex": hx(report_data),
            "validator_attestation_signable_hex": hx(attestation_signable),
            "validator_id_hex": hx(validator_id),
            "validator_signature_hex": hx(attestation_signature),
            "validator_attestation_scale_hex": hx(attestation_scale),
            "expected": "accept when pending tuple, active signer and quorum also pass",
        },
        "compute_channel_v1": {
            "domains": {
                "channel_id_ascii": CHANNEL_ID_DOMAIN_V1.decode(),
                "receipt_ascii": RECEIPT_DOMAIN.decode(),
                "deployment": "genesis_hash in channel_id",
                "session": "channel_id binds agent, miner and nonce",
                "protocol": "ASCII domain plus version byte",
                "leaf": "no prefix; the deployment/session-bound channel_id is the leading field",
                "merkle_node": "no prefix; exactly 64 bytes left_32 || right_32",
            },
            "channel_id": {
                "inputs": {
                    "genesis_hash_hex": hx(genesis),
                    "agent_account_id32_hex": hx(agent),
                    "miner_account_id32_hex": hx(miner),
                    "nonce": 42,
                },
                "preimage_hex": hx(
                    CHANNEL_ID_DOMAIN_V1
                    + b"\x01"
                    + genesis
                    + agent
                    + miner
                    + (42).to_bytes(8, "little")
                ),
                "hash_hex": hx(channel_id),
            },
            "leaf_inputs": {
                "channel_id_hex": hx(channel_id),
                "turn_index": fields["turn_index"],
                "h_in_hex": hx(fields["h_in"]),  # type: ignore[arg-type]
                "h_out_hex": hx(fields["h_out"]),  # type: ignore[arg-type]
                "g_n": str(fields["g_n"]),
                "decode_policy_hash_hex": hx(fields["decode_policy_hash"]),  # type: ignore[arg-type]
                "h_ids_hex": hx(fields["ids_hash"]),  # type: ignore[arg-type]
                "toploc_commitment_hash_hex": hx(fields["toploc_commitment_hash"]),  # type: ignore[arg-type]
                "miner_recv_ms": str(fields["miner_recv_ms"]),
                "miner_done_ms": str(fields["miner_done_ms"]),
                "latency_ms": 1,
            },
            "leaf_versions": [
                {
                    "version": version.name,
                    "scale_tag": int(version),
                    "preimage_hex": hx(leaf_preimage(version, **fields)),
                    "hash_hex": hx(leaves[version.name]),
                    "expected": "accept only under selected version and channel cutoff",
                }
                for version in TranscriptLeafVersion
            ],
            "merkle": {
                "leaf_order": ["V1", "V2", "V3"],
                "odd_node_behavior": "duplicate last",
                "node_preimage": "left_32 || right_32; no prefix (length separates nodes from leaf preimages)",
                "root_hex": hx(root),
                "path_for_index_2": [
                    {"sibling_hex": hx(sibling), "sibling_is_left": orientation}
                    for sibling, orientation in path
                ],
            },
            "v3_leaf_signature": {
                "leaf_hash_hex": hx(leaves["V3"]),
                "public_key_hex": hx(enclave_public_key),
                "signature_hex": hx(leaf_signature),
                "expected": "accept",
            },
            "verified_turn_v3_scale_hex": hx(verified_turn),
            "fcc4_transcript_blob_hex": hx(blob),
            "receipt": {
                "inputs": {
                    "channel_id_hex": hx(signed_channel),
                    "final_root_hex": hx(signed_root),
                    "aggregate_gn": 42,
                    "payable": 1_000,
                },
                "preimage_hex": hx(receipt),
                "public_key_hex": hx(enclave_public_key),
                "signature_hex": hx(receipt_signature),
                "expected": "accept",
            },
        },
        "data_ref_v1": {
            "input": {"commitment_hex": "88" * 32, "provider_id": 0, "retention": "Ephemeral"},
            "scale_bytes_hex": hx(data_ref_scale),
            "expected": "accept when registered, live and pinned as required by consumer",
        },
        "negative_cases": [
            {
                "id": "unknown_leaf_enum",
                "bytes_hex": "04",
                "expected": "reject",
                "site": "SCALE decode",
            },
            {
                "id": "unknown_retention_enum",
                "bytes_hex": "02",
                "expected": "reject",
                "site": "SCALE decode",
            },
            {
                "id": "truncated_fcc4",
                "bytes_hex": hx(blob[:-1]),
                "mutation": "drop final byte",
                "expected": "reject",
                "site": "TranscriptBlob.decode",
            },
            {
                "id": "trailing_fcc4",
                "bytes_hex": hx(blob + b"\x00"),
                "mutation": "append 00",
                "expected": "reject",
                "site": "TranscriptBlob.decode",
            },
            {
                "id": "unknown_fcc_version",
                "bytes_hex": hx(b"FCC9" + blob[4:]),
                "mutation": "FCC4 -> FCC9",
                "expected": "reject",
                "site": "TranscriptBlob.decode",
            },
            {
                "id": "duplicate_turn_index",
                "bytes_hex": hx(compact_u32(2) + verified_turn + verified_turn),
                "mutation": "repeat turn_index",
                "expected": "reject DuplicateVerifiedTurn",
                "site": "verified_work_from_turns",
            },
            {
                "id": "wrong_path_orientation",
                "bytes_hex": hx(wrong_path_turn),
                "mutation": "flip sibling_is_left",
                "expected": "reject LeafNotInRoot",
                "site": "verify_turn_proof/respond_dispute",
            },
            {
                "id": "wrong_genesis_network",
                "bytes_hex": hx(channel_id_v1(bytes([1]) + genesis[1:], agent, miner, 42)),
                "mutation": "change genesis_hash",
                "expected": "different channel_id",
                "site": "channel_id",
            },
            {
                "id": "wrong_session",
                "bytes_hex": hx(channel_id_v1(genesis, repeat(0x12), miner, 42)),
                "mutation": "change agent/miner/nonce",
                "expected": "different channel_id",
                "site": "channel_id",
            },
            {
                "id": "wrong_leaf_version",
                "bytes_hex": hx(wrong_version_turn),
                "mutation": "V3 fields with tag V2",
                "expected": "reject LeafFieldsInconsistent",
                "site": "verify_turn_proof/respond_dispute",
            },
            {
                "id": "invalid_receipt_signature",
                "bytes_hex": hx(bytes([receipt_signature[0] ^ 1]) + receipt_signature[1:]),
                "mutation": "flip signature byte",
                "expected": "reject BadReceiptSignature",
                "site": "verify_receipt",
            },
            {
                "id": "invalid_validator_signature",
                "bytes_hex": hx(bytes([attestation_signature[0] ^ 1]) + attestation_signature[1:]),
                "mutation": "flip signature byte",
                "expected": "reject BadValidatorSignature",
                "site": "submit_validator_attestations/check_one",
            },
            {
                "id": "legacy_leaf_current_channel",
                "bytes_hex": hx(legacy_verified_turn),
                "mutation": "V0/V1 tag with pinned decode policy",
                "expected": "reject UnsupportedLeafVersion",
                "site": "verify_turn_proof/respond_dispute",
            },
            {
                "id": "legacy_receipt_current_channel",
                "bytes_hex": hx(legacy_receipt + legacy_receipt_signature),
                "mutation": "remove receipt domain/version",
                "expected": "reject BadReceiptSignature",
                "site": "verify_receipt",
            },
        ],
        "coverage": [
            {
                "appendix": "F.1",
                "family": "decode_policy_v1/compute_channel_v1.channel_id",
                "consumer": "hp_poui::DecodePolicy::hash / compute_channel::channel_id",
            },
            {
                "appendix": "F.2/G.2",
                "family": "direct_rail_v1",
                "consumer": "submit_validator_attestations -> oracle::check_one/process_verified_poui_result",
            },
            {
                "appendix": "F.3/G.1 settle",
                "family": "compute_channel_v1",
                "consumer": "verify_receipt -> verified_work_from_turns -> verify_turn_proof",
            },
            {
                "appendix": "F.3/G.1 dispute",
                "family": "compute_channel_v1",
                "consumer": "respond_dispute",
            },
            {
                "appendix": "F.4/G.3",
                "family": "data_ref_v1",
                "consumer": "da_registry::register_blob/pin/is_live",
            },
            {
                "appendix": "F.5/G.1",
                "family": "compute_channel_v1.leaf_versions.V3",
                "consumer": "submit_toploc_evidence/report_toploc_mismatch/settlement gate",
            },
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    document = build()
    schema = json.loads(SCHEMA_PATH.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(document)
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            print(f"stale: {canonical_relative(OUTPUT, ROOT)}", file=sys.stderr)
            return 1
        print(f"ok: {canonical_relative(OUTPUT, ROOT)}")
        return 0
    OUTPUT.write_text(rendered)
    print(canonical_relative(OUTPUT, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
