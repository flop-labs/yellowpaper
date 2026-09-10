"""Canonical compute-channel encoders for the Appendix F wire profile."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from hashlib import blake2b

Hash = bytes
CHANNEL_ID_DOMAIN_V1 = b"FLOP/COMPUTE_CHANNEL/ID"
RECEIPT_DOMAIN = b"FLOP/COMPUTE_CHANNEL/RECEIPT"
TASK_HASH_DOMAIN_V1 = b"FLOP/POUI/TASK"
TRANSCRIPT_BLOB_MAGIC = b"FCC4"


class TranscriptLeafVersion(IntEnum):
    V0 = 0
    V1 = 1
    V2 = 2
    V3 = 3


def _fixed(value: bytes, length: int, name: str) -> bytes:
    if len(value) != length:
        raise ValueError(f"{name} must be {length} bytes")
    return value


def _uint_le(value: int, length: int, name: str) -> bytes:
    if not isinstance(value, int) or value < 0 or value >= 1 << (length * 8):
        raise ValueError(f"{name} does not fit u{length * 8}")
    return value.to_bytes(length, "little")


def blake2_256(value: bytes) -> Hash:
    return blake2b(value, digest_size=32).digest()


def compact_u32(value: int) -> bytes:
    """Canonical SCALE Compact<u32>."""
    _uint_le(value, 4, "compact value")
    if value < 1 << 6:
        return bytes([value << 2])
    if value < 1 << 14:
        return ((value << 2) | 1).to_bytes(2, "little")
    if value < 1 << 30:
        return ((value << 2) | 2).to_bytes(4, "little")
    return b"\x03" + value.to_bytes(4, "little")


def decode_compact_u32(data: bytes, offset: int = 0) -> tuple[int, int]:
    if offset >= len(data):
        raise ValueError("truncated compact integer")
    first = data[offset]
    mode = first & 3
    size = (1, 2, 4, (first >> 2) + 5)[mode]
    end = offset + size
    if end > len(data):
        raise ValueError("truncated compact integer")
    if mode == 0:
        value = first >> 2
    elif mode in (1, 2):
        value = int.from_bytes(data[offset:end], "little") >> 2
    else:
        payload = data[offset + 1 : end]
        value = int.from_bytes(payload, "little")
        if size != 5 or value > 0xFFFF_FFFF:
            raise ValueError("compact integer exceeds u32")
    if data[offset:end] != compact_u32(value):
        raise ValueError("non-canonical compact integer")
    return value, end


def channel_id_v1(genesis_hash: Hash, agent: bytes, miner: bytes, nonce: int) -> Hash:
    return blake2_256(
        CHANNEL_ID_DOMAIN_V1
        + b"\x01"
        + _fixed(genesis_hash, 32, "genesis_hash")
        + _fixed(agent, 32, "agent")
        + _fixed(miner, 32, "miner")
        + _uint_le(nonce, 8, "nonce")
    )


def task_hash_v1(
    genesis_hash: Hash,
    agent: bytes,
    nonce: int,
    model_hash: Hash,
    payload_hash: Hash,
    commit_hash: Hash,
) -> Hash:
    return blake2_256(
        TASK_HASH_DOMAIN_V1
        + b"\x01"
        + _fixed(genesis_hash, 32, "genesis_hash")
        + _fixed(agent, 32, "agent")
        + _uint_le(nonce, 8, "nonce")
        + _fixed(model_hash, 32, "model_hash")
        + _fixed(payload_hash, 32, "payload_hash")
        + _fixed(commit_hash, 32, "commit_hash")
    )


def h_ids(prompt_ids: list[int], generated_ids: list[int]) -> Hash:
    preimage = _uint_le(len(prompt_ids), 4, "prompt length")
    preimage += b"".join(_uint_le(token, 4, "token id") for token in prompt_ids)
    preimage += _uint_le(len(generated_ids), 4, "generated length")
    preimage += b"".join(_uint_le(token, 4, "token id") for token in generated_ids)
    return blake2_256(preimage)


def leaf_preimage(
    version: TranscriptLeafVersion,
    channel_id: Hash,
    turn_index: int,
    h_in: Hash,
    h_out: Hash,
    g_n: int,
    decode_policy_hash: Hash,
    ids_hash: Hash,
    toploc_commitment_hash: Hash,
    miner_recv_ms: int,
    miner_done_ms: int,
    latency_ms: int,
) -> bytes:
    value = (
        _fixed(channel_id, 32, "channel_id")
        + _uint_le(turn_index, 4, "turn_index")
        + _fixed(h_in, 32, "h_in")
        + _fixed(h_out, 32, "h_out")
        + _uint_le(g_n, 16, "g_n")
    )
    if version >= TranscriptLeafVersion.V2:
        value += _fixed(decode_policy_hash, 32, "decode_policy_hash")
    if version == TranscriptLeafVersion.V3:
        value += _fixed(ids_hash, 32, "h_ids")
        value += _fixed(toploc_commitment_hash, 32, "toploc_commitment_hash")
    if version >= TranscriptLeafVersion.V1:
        value += _uint_le(miner_recv_ms, 8, "miner_recv_ms")
        value += _uint_le(miner_done_ms, 8, "miner_done_ms")
        value += _uint_le(latency_ms, 8, "latency_ms")
    return value


def transcript_leaf(version: TranscriptLeafVersion, **fields: object) -> Hash:
    return blake2_256(leaf_preimage(version, **fields))  # type: ignore[arg-type]


def receipt_message_v1(
    channel_id: Hash, final_root: Hash, aggregate_gn: int, payable: int
) -> bytes:
    return (
        RECEIPT_DOMAIN
        + b"\x01"
        + _fixed(channel_id, 32, "channel_id")
        + _fixed(final_root, 32, "final_root")
        + _uint_le(aggregate_gn, 16, "aggregate_gn")
        + _uint_le(payable, 16, "payable")
    )


def legacy_receipt_message(
    channel_id: Hash, final_root: Hash, aggregate_gn: int, payable: int
) -> bytes:
    return (
        _fixed(channel_id, 32, "channel_id")
        + _fixed(final_root, 32, "final_root")
        + _uint_le(aggregate_gn, 16, "aggregate_gn")
        + _uint_le(payable, 16, "payable")
    )


def hash_pair(left: Hash, right: Hash) -> Hash:
    return blake2_256(_fixed(left, 32, "left") + _fixed(right, 32, "right"))


def merkle_root(leaves: list[Hash]) -> Hash:
    if not leaves:
        return bytes(32)
    level = [_fixed(leaf, 32, "leaf") for leaf in leaves]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [hash_pair(level[i], level[i + 1]) for i in range(0, len(level), 2)]
    return level[0]


def merkle_path(leaves: list[Hash], index: int) -> list[tuple[Hash, bool]]:
    if index < 0 or index >= len(leaves):
        raise ValueError("leaf index out of range")
    level = [_fixed(leaf, 32, "leaf") for leaf in leaves]
    path: list[tuple[Hash, bool]] = []
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        sibling = index - 1 if index % 2 else index + 1
        path.append((level[sibling], index % 2 == 1))
        level = [hash_pair(level[i], level[i + 1]) for i in range(0, len(level), 2)]
        index //= 2
    return path


def root_from_path(leaf: Hash, path: list[tuple[Hash, bool]]) -> Hash:
    current = _fixed(leaf, 32, "leaf")
    for sibling, sibling_is_left in path:
        current = hash_pair(sibling, current) if sibling_is_left else hash_pair(current, sibling)
    return current


@dataclass(frozen=True)
class TurnAckRecord:
    agent_send_ms: int
    agent_recv_ms: int
    agent_sig: bytes


@dataclass(frozen=True)
class TurnRecord:
    leaf_version: TranscriptLeafVersion
    turn_index: int
    h_in: Hash
    h_out: Hash
    g_n: int
    decode_policy_hash: Hash | None
    h_ids: Hash | None
    toploc_commitment_hash: Hash | None
    miner_recv_ms: int
    miner_done_ms: int
    latency_ms: int
    enclave_sig: bytes
    agent_ack: TurnAckRecord | None = None


def _check_record(record: TurnRecord) -> None:
    ids_nonzero = record.h_ids is not None and any(record.h_ids)
    toploc_nonzero = record.toploc_commitment_hash is not None and any(
        record.toploc_commitment_hash
    )
    if record.leaf_version in (TranscriptLeafVersion.V0, TranscriptLeafVersion.V1):
        if record.decode_policy_hash is not None or ids_nonzero or toploc_nonzero:
            raise ValueError("V0/V1 fields are inconsistent")
    elif record.leaf_version == TranscriptLeafVersion.V2:
        if record.decode_policy_hash is None or ids_nonzero or toploc_nonzero:
            raise ValueError("V2 fields are inconsistent")
    elif record.decode_policy_hash is None or not ids_nonzero:
        raise ValueError("V3 fields are inconsistent")


def encode_transcript_blob(channel_id: Hash, turns: list[TurnRecord]) -> bytes:
    value = TRANSCRIPT_BLOB_MAGIC + _fixed(channel_id, 32, "channel_id")
    value += _uint_le(len(turns), 4, "turn count")
    for turn in turns:
        _check_record(turn)
        value += bytes([turn.leaf_version]) + _uint_le(turn.turn_index, 4, "turn_index")
        value += _fixed(turn.h_in, 32, "h_in") + _fixed(turn.h_out, 32, "h_out")
        value += _uint_le(turn.g_n, 16, "g_n")
        value += bytes([turn.decode_policy_hash is not None])
        if turn.decode_policy_hash is not None:
            value += _fixed(turn.decode_policy_hash, 32, "decode_policy_hash")
        value += _fixed(turn.h_ids or bytes(32), 32, "h_ids")
        value += _fixed(turn.toploc_commitment_hash or bytes(32), 32, "toploc_commitment_hash")
        value += _uint_le(turn.miner_recv_ms, 8, "miner_recv_ms")
        value += _uint_le(turn.miner_done_ms, 8, "miner_done_ms")
        value += _uint_le(turn.latency_ms, 8, "latency_ms")
        value += _fixed(turn.enclave_sig, 64, "enclave_sig")
        value += bytes([turn.agent_ack is not None])
        if turn.agent_ack is not None:
            value += _uint_le(turn.agent_ack.agent_send_ms, 8, "agent_send_ms")
            value += _uint_le(turn.agent_ack.agent_recv_ms, 8, "agent_recv_ms")
            value += _fixed(turn.agent_ack.agent_sig, 64, "agent_sig")
    return value


def decode_transcript_blob(data: bytes) -> tuple[Hash, list[TurnRecord]]:
    """Decode FCC4 with exact consumption; legacy blobs require migration tooling."""
    offset = 0

    def take(length: int) -> bytes:
        nonlocal offset
        end = offset + length
        if end > len(data):
            raise ValueError("truncated transcript blob")
        value = data[offset:end]
        offset = end
        return value

    if take(4) != TRANSCRIPT_BLOB_MAGIC:
        raise ValueError("unsupported transcript blob version")
    channel_id = take(32)
    count = int.from_bytes(take(4), "little")
    turns: list[TurnRecord] = []
    for _ in range(count):
        try:
            leaf_version = TranscriptLeafVersion(take(1)[0])
        except ValueError as error:
            raise ValueError("unsupported leaf version") from error
        turn_index = int.from_bytes(take(4), "little")
        h_in, h_out = take(32), take(32)
        g_n = int.from_bytes(take(16), "little")
        has_policy = take(1)[0]
        if has_policy not in (0, 1):
            raise ValueError("invalid option tag")
        policy = take(32) if has_policy else None
        ids = take(32)
        toploc = take(32)
        miner_recv_ms = int.from_bytes(take(8), "little")
        miner_done_ms = int.from_bytes(take(8), "little")
        latency_ms = int.from_bytes(take(8), "little")
        enclave_sig = take(64)
        has_ack = take(1)[0]
        if has_ack not in (0, 1):
            raise ValueError("invalid option tag")
        ack = None
        if has_ack:
            ack = TurnAckRecord(
                int.from_bytes(take(8), "little"),
                int.from_bytes(take(8), "little"),
                take(64),
            )
        record = TurnRecord(
            leaf_version,
            turn_index,
            h_in,
            h_out,
            g_n,
            policy,
            ids if any(ids) else None,
            toploc if any(toploc) else None,
            miner_recv_ms,
            miner_done_ms,
            latency_ms,
            enclave_sig,
            ack,
        )
        _check_record(record)
        turns.append(record)
    if offset != len(data):
        raise ValueError("trailing transcript blob bytes")
    return channel_id, turns


def encode_verified_turn(record: TurnRecord, path: list[tuple[Hash, bool]]) -> bytes:
    """SCALE encoding of the runtime VerifiedTurn struct."""
    value = bytes([record.leaf_version]) + _uint_le(record.turn_index, 4, "turn_index")
    value += _fixed(record.h_in, 32, "h_in") + _fixed(record.h_out, 32, "h_out")
    value += _uint_le(record.g_n, 16, "g_n")
    value += _fixed(record.decode_policy_hash or bytes(32), 32, "decode_policy_hash")
    value += _fixed(record.h_ids or bytes(32), 32, "h_ids")
    value += _fixed(record.toploc_commitment_hash or bytes(32), 32, "toploc_commitment_hash")
    value += _uint_le(record.miner_recv_ms, 8, "miner_recv_ms")
    value += _uint_le(record.miner_done_ms, 8, "miner_done_ms")
    value += _uint_le(record.latency_ms, 8, "latency_ms")
    value += _fixed(record.enclave_sig, 64, "enclave_sig") + compact_u32(len(path))
    for sibling, sibling_is_left in path:
        value += _fixed(sibling, 32, "path sibling") + bytes([sibling_is_left])
    return value
