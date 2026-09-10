# Prepublication claim evidence

> Status: `[RESEARCH]` · 2026-09-07 · deterministic SCALE fixtures, charged-weight ledger, and
> negative benchmark/network evidence. This is not a dispatch, latency, throughput, or empirical
> assurance result.

This note records five analyses supporting the initial yellowpaper draft. The generated
JSON preserves the complete field ledger, exact
binomial fraction, source fragments, assumptions, and open inputs. The
CSV provides the main rows for independent analysis.
The byte-for-byte [wire-format corpus](../evidence/wire-format-v1.json) separately covers the canonical
Rust/TypeScript/Python encoders, signatures, Merkle paths, and malformed-input rejection profile.

## Reproduce

From a `flop-core` checkout:

```sh
uv run --script scripts/research/yellowpaper_claim_evidence.py --check --verify-sources
```

Regenerate after an intentional input change by omitting `--check`. In the public yellowpaper bundle,
where implementation sources are not required:

```sh
uv run --script evidence/reproduce.py --check
```

The script uses only the Python standard library. Its ledger fingerprint covers the expected declarations,
runtime pallet/call indices, ordered call fields, transaction extensions, limits, and charged-weight
fragments rather than a Git commit, so unrelated changes do not stale the evidence. A core checkout also
parses the complete ordered fields and call signatures, checks the unit-only enums, and verifies the other
embedded source fragments before accepting the generated artifacts.

## Evidence worksheet

| Analysis | Verified input/result | Assumed input | Open / not established |
|---|---|---|---|
| Committee | 40 bad identities at stake 1; 61 honest at stake 3; 100 distinct seats imply 39–40 bad seats; `Pr[bad seats ≥ 34] = 1` | All identities pass eligibility; the comparison binomial uses `p = 40/223` | No conflicting-finalization exploit, seed analysis, or general capture distribution is claimed |
| Direct rail | Source-checked v5 bare extrinsics are 18,434 B at active=100/q=67 and 36,859 B at supported max active=200/q=134 | Deterministic field/signature bytes | Signatures are not validated; the charged weight is an unbenchmarked stub; no throughput inference |
| Session rail | Source-checked v4 signed fixtures cover open, cooperative/unilateral settle, limits, duplicate-last, DA reference, TOPLOC evidence, and disputes | Deterministic signer/signature/field bytes and equal path length per turn | Fixtures are not dispatched; charged weights are estimates; no runtime or network benchmark |
| Capacity disposition | The runtime envelope is 5 MiB/75% Normal and 750,000,000,000 ref-time/75% Normal | None | Withdrawing the former byte, tx/block, lifecycle/s, and finality targets is proposed but unratified; none is validated |
| Audit exposure | Conditional probability chain and arithmetic | Every probability in the scenarios | Data availability, challenger behavior, inclusion, adjudication error, collateral reservation, and collectibility need measurement/modeling |

“Verified” here means reproduced from source-checked SCALE rules/declarations or exact finite arithmetic.
It does not mean a fixture passed dispatch or an end-to-end protocol property was formally proved.

## 1. Unequal-stake committee counterexample

The implemented sampler draws distinct eligible identities with probability proportional to remaining
stake, then removes the selected identity
(`committee.rs`). Consider this eligible set:

| Type | Identities | Stake each | Aggregate stake |
|---|---:|---:|---:|
| Byzantine | 40 | 1 | 40 |
| Honest | 61 | 3 | 183 |

Stake is expressed in common units at least as large as the eligibility floor; multiplying every weight
by that unit leaves selection probabilities unchanged. All identities are assumed to pass the work gate.
The Byzantine stake fraction is `40/223 = 17.9372%`. Selecting 100 distinct identities from 101 omits
exactly one identity. Therefore every possible committee has either 39 or 40 Byzantine seats, or
39%–40% of seats. The corresponding Byzantine share of committee stake is 39/222 = 17.5676% when a
Byzantine identity is omitted, or 40/220 = 18.1818% when an honest identity is omitted. Every outcome is
below one third by stake and above one third Byzantine by seats. AlephBFT's strict `3f < n` premise
permits at most 33 Byzantine seats in a 100-seat committee; every outcome exceeds that limit.

For the paper's comparison model, let `X ~ Binom(100, 40/223)`. Exact rational summation gives:

```text
Pr[X >= 34] = sum(x=34..100) C(100,x)(40/223)^x(183/223)^(100-x)
            = 0.0000887246916442207...
```

The actual distinct-identity draw has `Pr[bad seats >= 34] = 1`, regardless of which type is omitted.
Thus it violates the Lean model's `SelectionTailDominated` premise at threshold 34
(`CommitteeSampling.lean`). This arithmetic
refutes that tail-domination claim for this population. It does not prove that AlephBFT can be exploited.

[Hoeffding's Theorem 4](https://repository.lib.ncsu.edu/server/api/core/bitstreams/d0e6ed15-3e1c-432f-8419-e55ffb6f3171/content)
gives a convex-expectation comparison for a uniform sample without replacement and an independent
sample with replacement from the same fixed finite population. It transfers the paper's exponential
deviation bounds; it does not state pointwise domination by the corresponding binomial tail. It also
does not cover this probability-proportional-to-stake draw over distinct, unequal-weight identities.

## 2. Direct attestation rail

`ValidatorAttestation` currently contains five `H256` values, two `u64` values, a unit-enum discriminant,
two booleans, a 32-byte validator ID, and a 64-byte signature
(`hp-poui`). Under the fixed SCALE encodings used by these
types, its encoded size is:

```text
5*32 + 2*8 + 1 + 2*1 + 32 + 64 = 275 bytes
```

A SCALE `Vec` adds a compact element-count prefix. The runtime call is
`[pallet=86, call=15] || compact_len(n) || attestations`. Because this call requires `None` origin, its
extrinsic uses the current v5 bare format:
`Compact(body_len) || 0x05 || RuntimeCall`.

The default threshold is `666,666,666` parts per billion and the pallet uses `ceil(active × threshold)`
(runtime,
`flop-poui`).

| Active validators | Required signatures | SCALE Vec | Runtime call | Complete extrinsic | Charged ref-time |
|---:|---:|---:|---:|---:|---:|
| 100 | 67 | 18,427 B | 18,429 B | 18,434 B | 3,350,000,000 |
| 200 (runtime maximum) | 134 | 36,852 B | 36,854 B | 36,859 B | 6,700,000,000 |

The seven bytes beyond the vector are the two runtime-call indices, v5 bare preamble, and four-byte
outer length prefix. Embedded signature fields are populated with deterministic bytes; this serializer
does not validate them or dispatch the call. The direct charged weight is
`50,000,000 × signatures`, with zero proof-size charge, from a file labeled “auto-generated stub - to
be benchmarked.” It is not measured weight. The finality committee has a separate 100-seat cap and its
network messages are not runtime extrinsics. A 1,000-validator row is excluded because the runtime caps
the active set at 200.

SCALE rules are maintained by the
[parity-scale-codec project](https://github.com/paritytech/parity-scale-codec). The generated JSON
records each complete fixture's SHA-256 digest, source constraints, and byte/weight components.

## 3. Session settlement wire growth

The current `VerifiedTurn` fixed fields total 269 B, including its mandatory one-byte leaf-version tag.
Each Merkle membership entry `(H256, bool)` adds
33 B, and the path has its own SCALE compact length prefix:

```text
VerifiedTurn(L) = 269 + compact_len(L) + 33L
```

The cooperative `settle` arguments add 176 fixed bytes, `Option<DataRef>` (35 B for `Some`, including
the option tag), the outer compact vector length, and each turn
(compute-channel,
`DataRef`):

```text
settle_args(N,L,Some(DataRef)) = 176 + 35 + compact_len(N) + N*VerifiedTurn(L)
```

| Turns | Path 0 | Path 8 | Path 32 | Path 64 |
|---:|---:|---:|---:|---:|
| 1 | 590 B | 854 B | 1,646 B | 2,703 B |
| 16 | 4,640 B | 8,864 B | 21,538 B | 38,450 B |
| 128 | 34,883 B | 68,675 B | 170,051 B | 305,347 B |
| 1,024 | 276,803 B | 547,139 B | 1,358,147 B | 2,440,515 B |

These are complete v4 signed `settle`/`force_settle` extrinsics, not argument-only estimates. Each row
includes `MultiAddress::Id`, `MultiSignature::Sr25519`, mortal era, nonce, zero tip, disabled metadata
hash, both runtime-call indices, `Some(DataRef)` with sovereign-validator provider and `Ephemeral`
retention, and the outer compact length. Signature bytes are deterministic fixtures whose validity is
not asserted. Cooperative and unilateral calls have identical field shapes and therefore equal byte
sizes, but different call indices and hashes.

`VerifiedTurn.leaf_version` selects exactly one V3/V2/V1/V0 signed preimage, whose fixed lengths are
respectively 236, 172, 140, and 116 B; signature failure never retries another version. Current channels
accept V2/V3, while pre-policy channels retain explicit V0/V1 migration support. These preimages are hashed;
they are not separately appended to the settlement argument. Verification loops over turns and path
entries, and duplicate detection scans preceding turns, so the work is not constant in turn count.

The private generated bundle also records exact fixtures for `open_channel` (338 B), TOPLOC evidence publication
(172 B), `open_dispute` (144 B), maximum-path `respond_dispute` (2,523 B), permissionless `finalize`
(140 B), and a 128-turn duplicate-last settlement (34,883 B). Their charged weights are source-derived
admission metadata, not fresh benchmark output. Settlement weight varies with turn count only; Merkle
path length does not change it, and a duplicate-last call receives the same charge as a unique-index
call despite worst-case duplicate scanning.

## 4. Capacity and latency disposition

**Mechanism status: PENDING (partial encoding evidence only).** E.46 remains open. The target is a
benchmarked runtime profile plus a disclosed network matrix covering admission, serving, and finality;
the fixtures below do not complete that mechanism.

The runtime configures a 5,242,880 B block maximum, with 3,932,160 B for Normal dispatch. Its maximum
ref-time is 750,000,000,000 per block, with 562,500,000,000 for Normal dispatch. These ceilings do not
account for base work, proof-size competition, state-dependent failure, DA/checker traffic, execution,
serving, propagation, or finality. They are not divided by fixture size or charged weight to infer
transactions per block.

The supported runtime-benchmark build remains blocked by an internal dependency inconsistency (#550).
Therefore no benchmark output, runtime WASM hash, or benchmark hash exists, and no charged weight is
presented as benchmarked. No network run was performed, so there are no workload-qualified throughput
or latency results to publish. Raw failure diagnostics and the private reproducer remain gated in the
authoring repository; they are not public evidence that E.46 is complete.

The required future matrix covers realized committee sizes up to 100; single-/multi-region latency and
loss; node/GPU/TEE hardware; sustained offered load below/at/above
admission; turn/path/duplicate boundaries; DA/checker and Normal/Operational co-load; below-one-third
faults; partitions and recovery; and at-/above-one-third non-liveness boundaries. A conforming run must
retain admissions, rejections, backlog, stalls, and recovery, and report duration, warm-up, repetitions,
uncertainty, finalized lifecycle throughput, inclusion/finality p50/p95/p99, resource saturation, serving
capacity, and client-perceived latency.

D-0502 proposes withdrawing the former 125,000-byte, 96/128 transaction, 48/64 lifecycle, and sub-second
finality figures from the v0.5 profile. That proposal remains unratified. E.46 remains PENDING until #550
and the full measurement matrix are complete.

## 5. Conditional audit exposure

For one fraud opportunity, define the effective collection probability by the probability chain:

```text
p_effective
  = P(selected)
  * P(data available | selected)
  * P(challenger acts | selected, data available)
  * P(included in time | selected, data available, challenger acts)
  * P(upheld | selected, data available, challenger acts, included in time)
  * P(collateral collectible | all prior gates succeeded)
```

Because each factor is conditional on every prior gate succeeding, multiplication is the probability
chain rule; it does not assume statistical independence. A risk-neutral deterrence condition under the
stated payoff model is
`total profitable exposure < p_effective × collectible slashable collateral`.

| Scenario | Selected | Data | Challenger | Included | Upheld | Collectible | `p_effective` |
|---|---:|---:|---:|---:|---:|---:|---:|
| Configured-selection-only | 5% | 100% | 100% | 100% | 100% | 100% | 5% |
| Conditional stress | 5% | 90% | 80% | 95% | 90% | 75% | 2.3085% |
| Data outage boundary | 5% | 0% | 100% | 100% | 100% | 100% | 0% |

These percentages are scenarios, not observed rates. The first row isolates the configured sampling rate;
it does not assert the remaining gates are perfect. Empirical deterrence or assurance requires measured or
conservatively justified conditional inputs, an explicit challenger utility model, and collateral reserved
against aggregate concurrent exposure.
