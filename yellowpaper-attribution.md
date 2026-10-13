# Yellowpaper — Statement Attribution (companion index)

**Non-normative. Not part of the spec.** This file maps each numbered requirement (`R-id`) and key
invariant in [`yellowpaper.md`](yellowpaper.md) to its **formal witness** (Lean theorem / Quint
invariant) and **Rust code path**. It deliberately lives outside the yellowpaper: it exposes
implementation and proof-artifact detail that the normative spec keeps out of its body (the spec
describes the *target protocol*, not where it is proved or coded).

**How to read it.** A cell names the artifact that backs the requirement:
- **Lean** — a theorem in `lean-proofs/FlopSpecs/<File>.lean` (`File::theorem`).
- **Quint** — a legacy invariant in `formal-specs/<path>.qnt` (`file::inv_*`), or a property of a Quint
  Studio component model marked **Studio** (`quint-specs/<component>.qnt::property`, registered in
  `quint-specs/quint.lock`; Studio replays the component's Rust tests against it). A Studio property is
  bounded-sampled and oracle-replayed evidence, not a proof. A registered property is not by itself an
  executed result; its current oracle result lives in Studio.
- **Rust** — the enforcing pallet / module (`pallets/pallets/<pallet>`; a named `fn`/const where useful).
- **—** — no artifact of that kind; the requirement is code-enforced only, prose, or an open item
  (see the yellowpaper's Appendix E). A `—` in the Lean/Quint columns is not a defect: most operational
  requirements are enforced in code without a dedicated proof.

An artifact reference proves only its stated theorem/model property under its explicit assumptions. It
does not establish that deployed code satisfies those assumptions or that a composed protocol is proven
end to end. Rows below label material limits as **conditional**, **empirical**, **assumed**, or **open**.
The review's reproducible calculations, source extracts, and classification table are in
[`research/prepublication-evidence.md`](research/prepublication-evidence.md). The hypothesis-scoped
claim inventory and current **PENDING** public-export status are in
[`evidence/proof-bundle/README.md`](evidence/proof-bundle/README.md). The full Lean/Quint source and
run bundle remains in private release review pending a FLOP software-license grant. Its Consensus
result is finite certificate nonforking for unit voting seats; it is not a proof of the complete
AlephBFT protocol.
The private Quint subset has a pinned check plan and deterministic witnesses. Its mutation test passes
by detecting an intentionally broken presence-only variant; the raw diagnostic trace stays internal.
Those seeded runs are bounded simulations, not runtime refinement or exhaustive proofs.

**Maintenance.** Unlike the yellowpaper's inline `<!-- cite:… -->` comments (covered by the
authoring repository's link gate), this file is **not** machine-checked. Symbols and paths were
verified to exist when written; treat it as a maintained index and re-verify on rename. The gated,
section-level evidence view is [`yellowpaper-coverage.md`](yellowpaper-coverage.md); the parameter
cross-language names (canonical ⇄ Rust ⇄ Lean ⇄ Quint) are the yellowpaper's Appendix A; per-mechanism
build status is its Appendix H.

---

## Bidirectional Studio alignment — prepared 2026-09-28

This review uses the working tree based on `de4ee251e76f13fbade19ee53e49288eeef871b7`.
It extends this attribution index; it does not create another evidence registry. The normative
clarifications below preserve existing rules. The two proposed replacements are **not ratified**
and do not supersede the current yellowpaper or any merged decision.

### Clarifications applied to the yellowpaper and models

- **R7.2, each renewal:** compare the effective cap with the immediately preceding accepted version,
  not only the original benchmark. The Studio transition already takes `min(previous, current
  discounted ceiling)`; its old property missed `450 → 360 → 400` because `400 ≤ 450`.
  `hw-calibration.qnt`::`renewal_never_raises_cap` now records
  actual pre/post renewal values independently of the inequality. A new initial benchmark may
  increase capacity. `hw-calibration-renewal_test.qnt`
  has four directed runs: tighten/raise, a mutation that the original bound misses, fresh acceptance,
  and a stale renewal pack with enough work to isolate the freshness guard. All four ran successfully
  with the TypeScript backend; they are finite witnesses, not a refinement proof.
- **R15.4a, selection time:** eligibility is evaluated when selecting the committee. Later exit,
  slashing, or recency expiry does not rewrite that historical result. The Studio property now checks
  an independently saved eligible pool; it does not derive that pool from the chosen members.
  `validators-committee_test.qnt` has three successful
  directed runs covering later exit, a new selection, and an injected ineligible member. The existing
  bootstrap fallback and prover-fed recency still conflict with the target duty gate (E.42/E.52).
  This model does not establish AlephBFT safety or the distribution of the weighted sampler.
- **R6.4a, accounting:** the prose equation now includes net miner transfers, refunds, penalties,
  cumulative audit earmarks and unsettled channel escrow. Audit fees paid are part of cumulative
  earmarks, not a second escrow outflow. Forward collateral has a separate ledger. Rust's
  `compute_channel::{distribute_from_escrow,audit_pool_available}` and Appendix F.3 distinguish
  gross payable from net miner payment. The Studio model still needs matching payout and pool
  accounting corrections; its present `no_double_disbursement` is not evidence for the clarified
  equation.

### R5.3b — proposed obligation-based liability (pending decision)

**Why consider a yellowpaper change:** membership in the current validator set and responsibility
for a particular stored shard are different facts. A rotation must not erase a still-live serving
obligation, nor make a successor liable for its predecessor's missed audit. The Studio model's
`slash_only_while_obligated` makes that distinction explicit, but `enact_one` does not enforce it:
a missed audit can still be slashed after the blob/assignment disappears. Do not claim the model or
Rust already satisfies the proposed rule.

**Proposed replacement, not current requirements:**

> A serve-or-slash penalty MUST identify the provider assigned to the audited shard and its serving
> obligation at the audit deadline. A change in active-validator membership alone MUST NOT create or
> erase that obligation. Reassignment MUST record when the old obligation ends and the new obligation
> begins; an audit MUST NOT charge a successor for a predecessor's failure. A timely accepted response
> MUST prevent the corresponding miss. Detection MUST occur strictly after the response deadline;
> fund-moving enforcement MUST wait until the finalized prefix reaches that deadline.

Before adopting this text, specify handoff, cancellation and stake-exit liability in E.47/E.57 and a
new decision superseding the live-set clause of R5.3b. Reproduce rotations before issuance, before
expiry, and between miss detection and finalization, plus prune/reassign and an on-time response at
the exact deadline. Check both `da-registry.qnt` and
`da_registry::process_expired_audits` through the runtime slasher adapter; the adapter is part of the
claim. Existing `DaProviderRotation::repaired_no_stale_slash` concerns a different repaired policy and
must not be relabeled as proof of this proposal.

### R13.0c — receipt preservation after DA loss (pending decision)

**Mismatch:** the current yellowpaper/D-0430 requires a fail-closed escrow refund and challenger-bond
return without a fraud slash. Rust's `compute_channel::resolve_unrecoverable_transcript_inner` pays
up to the stored co-signed tariff and credits the claimed work; a signed receipt proves agreement,
not execution correctness or availability. The current Studio transition mirrors this implementation.
That match does not justify weakening R13.0c.

**Candidate wording if a receipt-preserving policy is ratified:**

> Unrecoverable transcript loss MUST return the challenger bond without a miner fraud verdict. A
> previously co-signed amount MAY be paid only under a separately specified evidence predicate that
> remains checkable after the loss and is bound to the exact channel, transcript root, work and
> payable. A signature alone MUST NOT satisfy that predicate or authorize public work rewards.
> Otherwise the remaining session escrow MUST be refunded. Forward-bond disposition and already-paid
> availability MUST be accounted for separately.

Keep R13.0c in force until E.31/E.44 defines that predicate, evidence custody, reward disposition and
all forward-channel outcomes, with a superseding D-id. The alternative is to retain the full-refund
rule and correct Rust. Required discriminating runs: zero/non-zero receipts, unavailable versus
unrecoverable data, an open challenge, normal versus forward channels, and prior availability/audit
payments. Preserve `DegradedSettlement::unrecoverable_transcript_voids_payment` as evidence for the
current rule, not the proposed alternative.

### Findings and remaining composition checks

- **R7.1a → Rust:** Studio's `cap_is_positive` run found ceiling `1` discounting to `0`; its ignored
  Rust reproduction `smallest_sku_ceiling_must_not_accept_a_zero_hard_cap` failed because the cap was
  accepted and the miner was registered. Studio reported 1,000 samples, 20 steps, seed
  `1790575148465317676`. The finding is retained; no runtime fix is included here.
- **R12.1f/R13.0b → model and runtime boundary:** bound the absolute response deadline against the
  transcript's actual retention/pin horizon, including every bisection round and the single extension.
  `respondBy - challengeEnd ≤ 2 × responseWindow` is not a DA-retention property. Retention-class or
  registry existence alone is not reconstructability. Keep this as an unresolved composition check.
- **R10.1/R10.3:** the yellowpaper already distinguishes local conservation from conditional
  cross-chain completion. Correct Studio's unconditional “either both legs settle or neither” group
  statement and add finalized refund-boundary witnesses; do not weaken the yellowpaper to match it.
- **Runtime wiring:** include the finality-node boundary, runtime receipt-verifier adapter,
  calibration-to-staking/credential issuers, DA-to-validator slasher, and SDK/relayer assumptions in
  Studio's map and system checked sets. Model properties alone do not discharge those connections.

### Validation receipt for this batch

The two directed Quint test modules ran with `quint test --backend typescript`: **7 passing**.
Removing only the renewal action's freshness guard in a temporary copy made
`scenario_stale_pack_is_rejected` fail with `QNT511`, as expected; the live model was unchanged.

`just yellowpaper-regen` and the native-Chrome HTML build completed. The links, coverage/map freshness,
requirement IDs, parameter table, heading anchors, rendered-source stamps, claim evidence and sampler
checks passed. `just verify-whitepaper` then stopped on the audit source ledger; the remaining HTLC
source check also reports drift. The documentation test suite returned **108 passed, 2 failed**, both
source-ledger freshness tests. The affected compute-channel, miner-staking, miner-slashing, BTC/NEAR
relayer and NEAR-contract spans differ in the existing working tree; their recorded ledgers match
`HEAD`. This batch does not refresh those receipts to endorse unrelated instrumentation edits.
A temporary 41-file public export passed freshness and embedded evidence reproduction; nothing was
published. Studio resync/oracle results for changed models remain separate from these directed tests.

## Studio contract review — 2026-09-29

This pass inspected the Studio checkout at `25defc056be84f5c000e2c5e1b34bb4548899487`
(`/Users/svidyuk/me/flop-core`). The Lean sources below are tracked in that checkout at the
same revision. They were read, not rebuilt. Studio's supported operator MCP reframed and
confirmed the four existing system analyses; confirmation authorizes checking, **not a passing
result**. The current checked sets and subsequent results belong to `systemAnalyses` in
`quint.lock`.

| Requirement / interaction | Checked properties and source links | Remaining obligation |
| --- | --- | --- |
| R6.4a, R12.1f, R13.0b/c — Compute-channel money-path gate | `settlement_ledger_balances`, `retention_through_all_legal_disputes`, `unrecoverable_transcript_refunds_escrow_in_full`; channel model, degraded settlement, settlement composition | Net payment accounting, actual transcript identity/expiry, full receipt inputs and structured attestation binding are missing from the channel model. These full checks are not-driven; partial ID/work or Boolean claim checks cannot discharge them. `SettlementScenario` assumes challenges, fraud and DA availability; `DisputeBisection.covers` bounds rounds, not wall-clock retention. |
| R15.4a/c, E.42/E.52 — AlephBFT PoUI-gated finality | `selection_time_eligibility`, `deterministic_session_snapshot`, `recency_from_accepted_duty`; validators model, committee sampling | Eligibility uses the independently captured selection-time pool. Later expiry does not invalidate history; recency can expire within a session even with a longer recency window. Root rotation remains inside the actual session and may violate unconditional stability. `selection_capture_le_hoeffding` requires `SelectionTailDominated`; bounded committee examples do not establish that distributional premise. |
| R7.2 and proof/reward provenance — PoUI proof-to-reward pipeline | `production_credit_provenance`, `credited_miner_capacity_bonded`, `credit_cap_from_valid_calibration`, `credit_cap_units_preserved`, `recorded_weight_matches_credit`; calibration fast path, integer reward arithmetic | `renewal_never_raises_cap` assumes an accepted renewal. `stake_covers_settlement_exposure` assumes bounded work/caps/elapsed time, stake rate at least one and sufficient stake. Neither proves the Rust adapters or units. `SettlementInt.BlockRewards.conservation` covers the fixed pot split and rounding, not per-miner decay weighting. WorkVesting and compute-channel callbacks remain outside this five-component span. |
| R2.3 — AlephBFT node finality loop | `justified_finality`, `certified_finality_nonforking`, `served_prefix_within_bft_finality`; node model, finality gadget, consensus theorem | `Consensus.FinalCtx.nonforking` requires certificates from the same voting context, a faulty minority and honest non-equivocation; runtime vote weight is one per seat. Distinct committee accounts alone do not discharge these premises. Root reports, honest-node finalized-head inherents and best-head movement are separate paths. No BFT liveness claim is made. |

**R12.1f correction:** Rust now checks `now <= dispute.respond_by` in both
`respond_bisection` and `challenge_bisection`; the current Quint channel model lacks
these guards. Its old late-response counterexample is model drift, not evidence that the
current Rust lacks the check. Runtime retention arithmetic is
`604800 + 22 * 7200 = 763200 < 1209600`, with a strict settle-time check against the
transcript's actual expiry. Repeated TOPLOC freezes and actual shard availability remain
separate composition obligations. R13.0c still requires full refund, no miner payment,
no work credit and no fraud slash; the receipt-preserving implementation divergence and both
pending policy proposals above remain unresolved.

### Current component evidence

Studio published revision **1** reports at the inspected revision for:

- **HW calibration:** fingerprint `fnv1a64:f2b57069c083f87a`, 20 tests, all matched, test exit 0.
  The separate `cap_is_positive` finding remains violated (1,000 samples, 20 steps,
  seed `1790659174004996650`). Thirteen replay-pick warnings and coverage gaps remain;
  workflow Ready is not complete coverage or proof of correctness.
- **Attest:** fingerprint `fnv1a64:7a3ba7e6a8c71eda`, 13 tests, all matched, test exit 0.
  `registered_profiles_are_satisfiable` remains violated. The existing ignored reproduction
  `upsert_rejects_threshold_above_claim_signature_cap` demonstrates the configurable
  8-member/4-signature-cap case; that particular mismatch is absent from the runtime's
  100/100 configuration. Six observations remain untested.
- **Finality gadget:** fingerprint `fnv1a64:16fc9b8b9bb1e515`, revision 1, 27 tests,
  all matched, test exit 0. Studio completed guard-gap review and reports Ready/current
  with no drift. Three replay-pick warnings and seven findings remain; the component's
  duplicate-key findings are distinct from the composed relay path, which rejects duplicate
  committee keys before calling the gadget.

The finality gadget's pure Core extraction preserved machine, action and property names.
Studio typechecked it and compared all **53 witness counts** before and after with 100
samples and the same input seed `0x5ab150ec9b24e8b6`: counts were identical. Both receipts
printed replay seed `0x5ab150ec9b26367b`; `orphaned_target_detected` was unreached in both.
This is a structural equivalence check under those bounds, not a full finality proof.

### Registered system results

Studio registered revision **1** for both analyses below and re-executed their evidence.
Counts are property rows, including inherited findings and overlapping guarantees; they are
not counts of distinct new runtime bugs.

| Analysis | Broken | No sampled counterexample | Not tested | Not driven |
| --- | ---: | ---: | ---: | ---: |
| PoUI proof-to-reward pipeline | 16 | 33 | 3 | 2 |
| AlephBFT node finality loop | 13 | 19 | 0 | 0 |

The PoUI composed model
contains 16 passing reproductions. Particularly useful cases are
`staleQuorumSnapshotCreditTest` (submission-time denominator versus live attester membership),
`creditRecordedAtZeroWeightTest` (the default decay factor), and
`slashedDeviceCreditedAgainTest` (no device binding before the first accepted proof).
Studio reproduced all 58 sampled claims. Production provenance is conditional on matching
attestation payloads and the stated external callback assumptions; standing message checks
largely hold by construction. Three unreached scenarios and the units obligation remain open.
The five component wrappers rename state variables to avoid Quint namespace collisions and
were compared against their originals using the same seeds; this is bounded alignment evidence.

The node-finality composed model
contains 13 passing reproductions, with all 44 sampled claims reproduced by Studio.
`forkTargetJustifiedByBestBranchCommitteeTest` checks the justification against a different
branch's committee; `disjointBranchCommitteesForkFinalityTest` exposes the missing common
committee premise under the model's signing assumptions. These are action-level model
counterexamples for implementation review, not an end-to-end execution of AlephBFT.
Root head writes and mid-session rotation are explicitly privileged cases.
The honest inherent and distinct-signature import checks had no sampled counterexample;
the report marks the fully imported proposal scenario as thin evidence.
Neither registered report proves an unrestricted deployment-level guarantee.

The committee analysis has 12 passing reproduction runs but its report registration is
still blocked by Studio's combined-check runner fault. The settlement analysis remains in
progress. Their files are not represented here as completed system results.

### Local verification receipt

Before the new system analysis artifacts were generated, `just verify-quint-studio` passed
**29 files, 0 failures**; it excludes generated coverage replay modules. Explicit scenario
selection then passed **19 runs**: four renewal scenarios/mutations, three committee scenarios/
mutations, four degraded-settlement cases and eight finality/restart cases. The latter used
10,000 randomized trials per run; these are bounded checks, not exhaustive verification.
The yellowpaper link checker passed
**25 sections, 97 research docs and 25 matrix cells**. No fresh Lean build or full whitepaper
gate is claimed by this receipt. See the Studio execution handoff
for supported operations and remaining metadata limitations. After the eight system files
were generated, `just verify-quint-studio` passed **37 files, 0 failures**, and the full
`just verify-pallets` lane passed with the installed rustup toolchain first in PATH
(storage compatibility, formatting, clippy, workspace tests, simulator tests, documentation
tests and the paid-storage feature tests). The DA oracle logging fix changes no storage type
or protocol predicate.

## §2 — Consensus

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R2.1 | BABE authoring, 1 s blocks | — | — | runtime BABE config; `pallets/pallets/aleph` |
| R2.2 | Finality read via `FinalizedPrefix`, never tip | — | — | `pallets/primitives/hp-consensus`; `pallet_aleph::LastFinalized` |
| R2.3 | Strictly `< ⅓` Byzantine committee seats (`3f < n`; sampler bridge open E.42) | `Consensus::Committee.quorum_inter_gt_third`; `Consensus::FinalCtx.nonforking` (**unit weights**, quorum certificates, honest non-equivocation); `CommitteeSampling::selection_capture_le_hoeffding` (**conditional** on `SelectionTailDominated`) | `consensus/weak-subjectivity::inv_honest_quorum` | equal-seat signatures: `pallets/pallets/aleph`; `finality-aleph::verify_committee_multisignature` |
| R2.4 | PoUI committee gate = stake + accepted verification duty, never proof production (**runtime still keys recency on prover credit, E.52; zero-duty fallback drops recency; conformance gap E.42**) | `CommitteeSampling::selection_capture_le_hoeffding` | `consensus/consensus::committee_poui_gated` | `hp_consensus::select_committee`; `validators::poui_committee_sampled` |
| R2.5 | Up-to-100 weighted VRF sample (**undersized pools return all; capture bound open E.42**) | `CommitteeSampling::selection_capture_le_hoeffding` (**does not discharge the sampler hypothesis**) | — | `hp_consensus::sample_committee_weighted` (`committee.rs`); `validators::poui_committee_sampled` |
| R2.6 | Engine isolation (pallets depend only on `FinalizedPrefix`) | — | `consensus/consensus::finalized_within_head` | `pallets/primitives/hp-consensus` |
| R2.7 | Disclosed and benchmarked byte/weight profile (**PENDING: benchmark open E.46; 125,000 B is an assumption**) | — | — | runtime block-length / weight config supplies limits, not measured throughput |
| §2.4 | Sybil cost (triple moat) | — | `sybil-mitigation::inv_sybil_cost_bounded` | `pallets/pallets/sybil-resistance`; `miner-staking` |

## §3 — Verification architecture

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R3.1 | TOPLOC commitment required (**presence enforced; execution-correctness bridge open E.43/E.44**) | `VerificationStack::sessionAccept_needs_both` (**abstract**) | `verification/proof-verification.qnt` | `flop-poui: hp_poui::toploc`, `report_toploc_*` |
| R3.2 | TEE optional; fallback bound survives broken TEE (**conditional on supplied fallback**) | `VerificationStack::sessionVerifier_survives_broken_tee` (**abstract AND-combinator**) | — | `pallets/verifiers/dstack` (optional HARD path) |
| R3.3 | Independent re-execution deterrence (**conditional payoff model; open E.45**) | `Security::deterred`; `DisputeBisection::covers`; `DisputeCost::bond_covers_dispute` | — | `pallets/pallets/miner-slashing` |
| R3.5a,c | Dispute preconditions (**theorem assumes every fraud challenged and data available**) | `DisputePrereqs::fraud_not_finalized` | — | `compute-channel`; `da-registry` |
| R3.5d | Re-execution checker lane: 3 bonded distinct-operator checkers, unanimous, VRF-assigned; TEE-attested verdict = OPTIONAL tier that never lowers the floor; validators verify + co-sign (**PLANNED E.53**) | `VerificationStack::sessionVerifier_survives_broken_tee` (TEE-optional floor) | — | `compute_channel::report_toploc_mismatch` (validator-recomputed today); `toploc-checker.ts` · #1553 |
| R3.6 agg | Aggregate verifies ⇒ every leaf statement verifies (knowledge-soundness, abstract) | `DisputePrereqs::aggregate_sound` | — | `flop-poui` aggregate root |
| R3.4 | Settlement gate = validator BFT quorum | `ToplocSession::sessionMiss_full_sample` | `verification/proof-verification.qnt` | `flop-poui: submit_validator_attestations` |
| R3.5 | Binding of `task_hash`/`gn_weight`/`model_hash`/`output_hash` (**producer-side task derivation open E.51**) | `TeeAttestationFlow::blacklisted_not_verified` | — | `flop-poui` (`report_data`/`output_hash` checks) |
| R3.6 | Replay: each `task_hash` credited once | — | — | `flop-poui: ProcessedTasks` |
| R3.4a–c | TOPLOC commitment/fail-closed cell (**empirical detector + conditional formula; bridge open E.43**) | `VerificationComparison::interchangeable_of_eq_errors` (**assumes equal supplied errors**) | — | `flop-poui: hp_poui::toploc`; `model-registry` band constants |
| R3.6a–c | Quorum: distinct active-validator sigs ≥ `ceil(active×θ)` | — | `verification/proof-verification.qnt` | `flop-poui: submit_validator_attestations`, `oracle.rs` |

## §4 — Metering

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R4.1 | Unit `F_eff`; precision-invariant **reference-work accounting** | `OpCountModel::precision_invariant`, `opCount_additive`; `Computable::classAdjustedCeiling` | — | `flop-poui: hp_poui::flop_meter` |
| R4.2 | Deterministic reference formula, not bare `2·P·N` (**not physical instruction measurement**) | `Calibration::Bp_le_worstMean` | — | `flop-poui: effective_flops_exact` |
| R4.3 | Reject-only throughput tripwire (never clamps) | `Computable::classAdjustedCeiling` | — | `flop-poui: GnThroughputCeilingGflopsPerSec` |
| R4.4 | Canonical `G_n` unit taxonomy (**extreme meter-overflow rejection remains #588**) | — | — | `hp_poui::flop_meter`; direct `u64`; compute-channel `u128` + checked aggregation |
| R4.5 | Profile-v1 cache accounting charges full prompt/context | — | — | `hp_poui::flop_meter::effective_flops_exact`; proof-bound discount open E.22/#1153 |

## §5 — Data availability

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R5.1/R5.2 | On-chain footprint payload-independent; block size budget | `Sizing::footprint_payload_independent`, `block_within_limit` | — | runtime block-length config; `compute-channel` |
| R5.3a | RS rate-½ on deterministic subset (**availability/anti-grinding assumptions open E.47**) | `DataAvailability::retrievable_until_window` (**conditional threshold model**) | `da/da-retrievability::inv_retrievable_until_window` | `pallets/pallets/da-registry` |
| R5.3b | Serve-or-slash; penalty from the live set | `DaProviderRotation::repaired_no_stale_slash` | `da/da-retrievability::inv_loss_implies_slash` | `da-registry` |
| R5.3c | No per-byte DA fee (validator duty) | — | — | `da-registry` |
| R5.3d | Retention classes; pins block prune; recoverable | — | `da/da-retrievability::inv_no_early_prune`, `inv_pinned_never_pruned`, `inv_no_prune_in_grace` | `da-registry` |
| R5.3e | Indexer serves only the finalized prefix | `IndexerReorgSafety::repaired_served_canonical` | — | `indexer/` |
| R5.3f | Publisher-only lease withdrawal; pins block it, `lease_end` does not; full deposit refund | — | — | `da-registry: withdraw_lease` |

### §5.4 — Paid storage unbounded proof contract

Draft #1570 contracts are **not composed into System/GrandComposition**. Their
assumption inventory separates the
accounting projection from exact rent/voucher, authority, resource and fault
adapters. All counts and monetary quantities are nonnegative; denominators are
positive. Concrete witnesses are model vectors, not calibrated protocol values.
The future predicates below are conformance obligations for #1566/#1567 and
**remain pending for #1569**, including checks against the development pallet.
No row proves deployed cipher security, physical availability or a truthful market.

`S` = `PaidStorageSettlement`; `M` = `PaidMemoryAuthority`; `L` =
`PaidStorageLiability`; `A` = existing `PaidStorageArithmetic`. Helpers belong to
their caller's requirement: `fund_valid`, `earn_valid`, `pay_valid`, `settle_valid`,
`initial_inv` and `next_inv` support `S.reachable_invariants`; `initial_deadline_inv`
and `next_deadline_inv` support `S.reachable_deadline`.

| R-id / claim | Lean statements | Exact future enforcing predicate | Quint actions / registered witness or mutation |
|---|---|---|---|
| R5.4d/e/f/g — separate accounts, conservation, zero terminal escrow | `S.reachable_invariants`, `terminal_zero_escrow`, `close_refunds_lane_escrow`, `fault_refund_valid`, `replacement_savings_refunded`, `honest_lifecycle` | For each disjoint hold: `funded = paid + refunded + remaining`; `paid <= earned`, `earned-paid <= escrow`; settle accepted rent before surplus; lane close refunds the remaining escrow and unredeemed setup/voucher entitlements lapse; Closed/Aborted escrow zero; deposits/collateral/fees excluded; issuance/work credit unchanged | `paid-deal-model::releaseRent/refund/abortReservation`, `paid-storage-lanes::redeemLane/finalizeLane`; `w_honest_expiry_surplus_pin_prune`, `w_mutation_money`, `w_mutation_terminal` |
| R5.4d/f — concurrent collateral/capacity and live bytes | `S.fresh_lock_total`, `assignment_capacity`, `reachable_invariants`, `post_term_rejects_work`, `unknown_clock_rejects_work` | New reservation ID absent from lock set; `sum(all concurrent locks)+new <= held collateral/declared bytes`; `live+encodedFootprint <= reserved` before write; checkpoint deletion subtracts only live bytes | `declareCapacity/protocolAssign/writeObject/checkpoint`; `w_two_concurrent_owners_capacity`, `w_mutation_capacity`, `w_mutation_collateral` |
| R5.4f/j — take-or-pay delete and consented transfer | `S.delete_preserves_settlement`, `transfer_preserves_liability`, `post_term_rejects_work`, `unknown_clock_rejects_work` | At checkpoint reclaim: rent, escrow, setup earnings and historical assignment map equal their pre-state; signed transfer changes payer only; no cancellation settlement | `deleteObject/checkpoint/transfer`; `w_delete_checkpoint_write_transfer_race` |
| R5.4d/f/n — activation and one-time setup | `S.failed_activation_no_setup`, `setup_cannot_repeat`, `repair_cannot_earn_setup`, `failed_placement_full_refund`, `unwritten_key_not_activated`, `reachable_activation_written` | Custody and encoding accepted for bound write/provider/object before activation; activation needs an admitted write of the key's object; setup key absent from earned set; challenge closed; reserve setup outside rent; failed activation earns zero; repair/replay/delete preserve earned setup | `activate/earnSetup`, `service-lane::reserveSetup/activateSetup/failedActivation`; `w_success_activation_setup_rent`, `w_mutation_setup_before_activation`, `w_mutation_setup` |
| R5.4e/f — integer epoch rent and disjoint intervals | `S.rent_release_only_new_delta`, `honest_split_rent`, `rent_counter_monotone`, `duplicate_rent_interval_rejected`, `unproved_rent_rejected`, `rent_only_within_term`; `A.cumulative_releases_telescope`, `cumulative_releases_le_term` | One slot/tranche accumulator across segments; bound each historical interval by its assignment and tranche; accepted audit/checkpoint and elapsed challenge; exact `R_k(b)-R_k(a)`; consume term positions once; rent accrues on reserved bytes independent of occupancy | `respondAudit/releaseRent`; `w_reserved_empty_bytes_earn_rent`, `w_partial_claim_delta_and_replay`, `w_mutation_unproved_interval`, `w_mutation_delta` |
| R5.4f/n — slot/tranche position rent (D-0524) | `A.slot_counter_releases_le_term`, `slot_interval_fairness`; `S.aggregate_segment_bound`; historical counterexamples `A.audit_1965_standalone_ceil_overdraws`, `audit_1965_residual_cap_underpays` | One accumulator per slot/tranche; pay historical holders only for credited positions; preserve pending entitlements across replacement; failed/unserved/forfeited deltas refund payer; no independent provider ceiling or release-order clipping | `handoff/releaseRent`; `paid-storage-counterexamples::inv_slot_entitlement`; seven vectors; counterexample A=1, B=0, refund=0; per-provider-ceiling mutation fails conservation |
| R5.4e/f — consent and renewal tranche | `S.renewal_does_not_reprice_old`, `renewal_full_term`, accounting `S.ReservationNext.renew` | Added term/funds <= signed consent; new tranche uses its funding tariff; cumulative old-term amount unchanged; no repeated setup; replacement cannot debit beyond signed remaining budget | `renew/handoff`; `w_mutation_reprice_old_counters`, renewal/expiry witnesses |
| R5.4g/h — vouchers, splitting, domain binding and pinned rates | `S.checked_lane_exact`, `checked_lane_inclusive_max`, `redeemed_amount_checked`, `overflowing_voucher_rejected`, `invalid_tariff_rejected`, `non_provider_redemption_rejected`, `lane_amount_mono`, `cumulative_payments`, `lane_claims_telescope`, `lane_redemption_delta`, `honest_lane_redemption`, `duplicate_payment`, `replay_redemption_rejected`, `wrong_binding_rejected`, `cross_lane_redemption_rejected`, `old_lane_not_repriced`, `naive_per_message_rounding_inflates` | Signed complete chain/reservation/lane/provider/payer/object/version/request/range domain and sequence; monotone counters; exact `W*F+ceil(B*r/s)+N*f` at pinned tariff; fresh sequence and amount > paid; transfer amount-paid only; redemption consumes the checked amount, so product/sum width overflow fails closed | `validVoucher/redeem`, D-0519 `canRedeem/redeemLane`; `w_paid_reads_delta_duplicate_redeem`, `w_mutation_duplicate_or_cross_provider_payment`, wrong-binding witnesses |
| R5.4g/h — request nonce/range billing | `S.billing_nonce_scope` | Bill a range once within `(requestNonce,range)`; every fresh authorized nonce adds repeated bytes again; invalid/unacknowledged data does not change acknowledged-byte counters | `advanceRequest/ack`; fresh request and dedup witnesses |
| R5.4h/i — attempted resources, advanced fee and restart | `S.attempted_resource_bound`, `delivery_counts_every_attempt`, `no_delivery_without_advance`, `quota_consumed_monotone`, `quota_caps_invariant`, `quota_restart_countermodel`, `unpaid_exposure_bound` | Advance fee voucher before first chunk; atomically reserve work/egress/concurrency/credit across all lanes; charge every attempt; `outstanding <= cap`; risk `max(0,ceil(cap*r/s)-fee)`; durable consumed totals unchanged by refund/new lane/identity/restart; refill requires bounded monotonic time | `advanceRequest/deliver/monotonicRefill/crash/replay`; `w_unpaid_last_ack_bounded`, `w_mutation_request_without_advanced_fee`, `w_mutation_infinite_free_retry`, `w_mutation_restart_resets_provider_quota`, `w_mutation_fresh_lane_credit_harvesting` |
| R5.4b/h — attenuation and aggregate wallet/parent caps | `M.attenuation_transitive`, `authorization_scope`, `widening_delegation_counterexample`; `S.parent_wallet_budget_invariant` | Same namespace/policy, child operations subset, child limit/expiry <= parent; possess subject key and bind method/body/resource/nonce; atomically increment shared parent/wallet totals by cost only if both caps fit; adding/revoking children cannot reset totals | `authorize/delegate/authenticated/request`; `w_mutation_attenuation`, `w_mutation_parent_budget`, `w_mutation_cross_namespace_request` |
| R5.4b/j — finalized revocation and retained exposure | `M.policy_epochs_monotone`, `finalized_revocation_rejects`, `finalize_revokes_prior_authorization`, `expired_capability_rejected`, `expiry_persists`; `S.revocation_blocks_new_service`, `revoked_reservation_rejects_writes`, `revoked_writes_frozen`, `revoked_setup_needs_prior_write`, `prior_write_setup_after_revocation`, `revoked_claim_preserved`, `naive_revoke_refund_counterexample` | Finalized policy epoch never decreases; new authorization requires exact current epoch; a revoked reservation admits no write, so setup after revocation pays only for objects written before it; already approved funded vouchers remain payable within original cap/window; revoke does not zero escrow | `revoke/finalizePolicy/redeem`; `w_authorized_revoke_preserves_voucher`, `w_mutation_refund_before_claim` |
| R5.4c — sequencing, quorum and objective equivocation | `M.ordered_head_step`, `receipt_quorum`, `committed_head_has_signers`, `stale_cas_rejected`, `parallel_stale_writer_rejected`, `conflicting_receipts_detectable`, `equivocation_witness`, `honest_head_lifecycle` | Exact predecessor, next sequence, finalized generation and sequencer ordinal; distinct assigned signer count >= quorum; failover next ordinal after deadline; two authentic signatures by same provider for same namespace/key/predecessor and distinct successor constitute fault | `sequencerCAS/receipt/failover/advanceGeneration/equivocate`; `w_mutation_stale_parallel_cas`, `w_mutation_failover_generation_race`, `w_mutation_quorum` |
| R5.4c — authoritative chain pin **first import open #1966** | `M.chain_pin_dominates`, `naive_first_pin_rollback` | Resolve same key from finalized chain pin when present, otherwise quorum receipt; first import must authenticate current predecessor, not just supply a signed stale head | `predecessor/pin`; `w_cas_receipt_pin_checkpoint`, `w_mutation_first_pin_without_predecessor` |
| R5.4b — confidentiality acceptance limit | `M.envelope_confidentiality_countermodel` | Envelope bounds/suite/commitment/signature checks accept the public envelope too; confidentiality separately requires client encryption, fresh nonces/keys, secret keys and cipher assumptions | `paid-storage-types::wellFormed/PUBLIC_ENVELOPE`; public-byte admission witness; no encryption theorem |
| R5.4i/j/n — historical attribution, collectibility and partial fault | `L.reachable_liability`, `liability_conservation`, `assignment_attribution`, `pre_exit_collectible`, `replacement_not_charged`, `no_early_unlock`, `collection_does_not_restore_bytes`, `loss_before_detection_and_exit_collection`, `naive_loss_implies_slash_false`; `S.innocent_provider_entitlement` | Keep immutable reservation/provider/generation record; observe objective evidence within liability window; adjudicate once; collectible debt <= collateral+held-back rent; collection decrements debt and held value; unlock only after deadline and debt zero; membership is no collection guard; update faulty account only | `lose/challenge/adjudicate/handoff/exitProvider/releaseCollateral`; `w_loss_precedes_detection_and_collection`, `w_repair_historical_fault_exit_no_replacement_blame`, `w_mutation_historical_blame` |
| R5.4j/n — no early prune, terminal claims and progress | `S.claim_refund_disjoint`, `unknown_clock_blocks`, `deadline_equality_claim_only`, `reachable_deadline`, `close_pins_deadline`, `close_never_backdates`, `early_close_deadline`, `resolved_claims_freeze_rent`, `unknown_clock_freezes_lane`, `known_clock_persists`, `finalize_lane_refunds_escrow`, `early_lane_finalizes_before_expiry`, `non_payer_close_rejected`, `closed_lane_keeps_claim_window`, `zero_window_cannot_close_lane`, `unknown_clock_cannot_close_lane`, `reachable_epoch_window`, `lane_keeps_epoch_claim_window`, `late_close_matches_open_deadline`, `closed_lane_rejects_writes`, `finalized_lane_rejects_activation`; `L.no_premature_prune`, `bounded_paid_pin_prune`, `readiness_from_progress`, `eventual_close_refund`, `honest_terminal_step`, `fair_terminal_trace`, `conditional_eventual_retrieval`, `fair_retrieval_trace` | Fixed `D=min(inclusion,reservationEnd)+fundingWindow`, window at least one paid-storage epoch; a late close of a never-closed lane pins the same `D`; known F<=D claim, known F>D refund; all claims/repair/adjudication close before reservation surplus/deposit return; prune only Closed and past deadline; paid pin cannot extend it. Close needs finality/inclusion/adjudication progress and fairness; retrieval additionally authentic reachable reconstructing shards and repair capacity | `close/refund/prune`, D-0519 `closeLane/finalizeLane`; `w_honest_expiry_surplus_pin_prune`, `w_mutation_refund_before_claim`, `paid-storage-progress` fair projection and negative finality/custody runs |
| R5.4e/i — tariffs and conditional economic payoffs | `A.medianComponent_in_governance_band`, `median_in_step_band_of_overlap`, `tripwire_raises`; `L.retaining_shard_no_worse`, `forfeitable_value_deters`, `coalition_external_loss`, `reimbursed_penalty_not_deterrence` | Clamp capacity-declarer stake median to step/governance bands under validated overlap; sustained shortage tripwire uses upper step. Audit `0<=p_a<=1`, `p_a*c_r>=c_s`; expected collectible `(collateral+heldBack)` >= one-shot gain. External coalition loss excludes reimbursements; quantile/traffic-cost claims additionally need weight/enforcement/nonrecycling premises | `voteTariff/computeTariff/declareCapacity`; vote/update/buy and colluding-provider/rebooking witnesses. Probability/cost calibration and any stronger traffic theorem remain #1565/#1572 |
| R5.4e/g/j — executable integer boundaries | `S.integer_boundary_vectors`; `A.clamp_vectors`, `disjoint_band_vector`, `rustRent_eq_some`, `rustCeilDiv_eq_quint` | Reject denominator zero, intermediate/final width overflow; strict refund equality; preserve integer ceiling order. No machine wraparound or implicit repricing | Shared `ceilDiv/laneAmount`; #1569 must run these vectors through actual dispatch/provider adapters; not a runtime receipt |

## §6 — Base-layer primitives

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| §6.1 | Capacity-proportional miner self-stake (linear, no cap) | — | — | `pallets/pallets/miner-staking` |
| R6.2a | Delegate acts with no per-action consensus | — | — | `pallets/pallets/session-keys`, `agent-wallet` |
| R6.2b | Owner revoke; caps + circuit breaker bound a captured key | — | — | `agent-wallet`, `session-keys` |
| R6.4a | Escrow conserves; payout on verdict/timeout only | `TxStateModel::transfer_conserves`, `pool_compose` | `channel/channel-settlement::inv_conservation` | `pallets/pallets/compute-channel` |
| R6.5b,c | Existential deposit; monotonic-nonce anti-replay | `AccountModel::below_ED_reaped`, `nonces_strictly_increase` | — | `frame_system` account/nonce |

## §7 — Hardware calibration & drift

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R7.1 | Entry via correctness-verified burst; per-credential binding, consumed once | `CalibrationFastPath::accept_initial_requires_capacity_bond` | `verification/hardware-calibration::inv_usable_is_bonded` (continuous-bond form is **not** pallet policy: the bond is an accept/renew gate); Studio `hw-calibration`: `bonded` guard only | `pallets/pallets/hw-calibration: accept_benchmark_burst` |
| R7.1a | `accept_benchmark_burst` fail-closed conditions; deposit before activation | `Calibration::Bp_le_worstMean` | `verification/hardware-calibration::inv_active_is_usable`; Studio `hw-calibration::cap_never_exceeds_empirical`, `tier_matches_attestation` | `hw-calibration` |
| R7.1b | HARD-tier inventory: missing SKU ceiling fails closed, no SOFT downgrade | `Computable::classAdjustedCeiling` | `verification/hardware-calibration::inv_accepted_cap_uses_versioned_ceiling`; Studio `hw-calibration::tier_matches_attestation`, `hard_cap_within_discounted_ceiling` | `hw-calibration` |
| R7.1c | `C_emp` counted once; never multiplied by GPU/channel/session/batch | `Calibration::Gn_le_max` | `verification/hardware-calibration::inv_cap_le_empirical`; Studio `hw-calibration::cap_never_exceeds_empirical` | `hw-calibration: flop_meter` |
| R7.2 | Renewable cap: lease-frozen; renewal never raises cap; SKU change no silent alter | `CalibrationFastPath::renewal_never_raises_cap` | `verification/hardware-calibration::inv_renewal_never_raises_cap`; Studio `hw-calibration::renewal_never_raises_cap` (per renewal, ≤ the value stored immediately before it; cumulative, ≤ initial cap), `hard_cap_within_discounted_ceiling`, `registration_ends_at_expiry`; scenarios + mutation witnesses in `quint-specs/hw-calibration_test.qnt`, and the four directed renewal runs above in `quint-specs/hw-calibration-renewal_test.qnt` | `hw-calibration: renew_benchmark_cap` |
| R7.3 | Restart/reconnect renewal; fingerprint change invalidates; drift≠cheat by signature | `CalibrationDrift::cheat_detected`; `DriftDetection::breach_on_large_deviation`, `no_breach_in_tolerance` (EWMA statistical layer) | `verification/hardware-calibration::inv_hardware_identity_bound`; Studio `hw-calibration::cap_bound_to_current_identity` (renewal triggers are off-chain, `miner-worker`) | `hw-calibration`; `miner-worker` |

## §8 — Performance-locked vesting

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R8.1 | Finalized non-zero `B_p` for `create_grant`; Root-only `force_create_grant` bypass; convex `R_p²` unlock (`R_p² ≤ R_p`) | `Vesting::unlock_le_ratio` | — | `work-vesting::{create_grant,force_create_grant}`; runtime `HwCalibrationAdapter::pledge_baseline` |
| R8.2 | Blackout revocation (1.0× slash) | — | — | `work-vesting` |
| R8.1a–b | Ghost-Task known-answer canary; bounded escrow slash | `GhostTaskAudit::bounded_slash_payoff` | `verification/statistical-sampling::invariant_checker_quorum_before_slash`, `invariant_no_self_checked_slash` | `pallets/pallets/synthetic-tasks` |

## §9 — Emission & supply

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R9.1 | Block reward sourced from params, bounded `≤ 96` | — | `economics/tokenomics-supply::inv_reward_le_initial` | `pallets/pallets/block-rewards` |
| R9.2 | Geometric floored halving; supply monotone | `HalvingBoundary::halving_no_exodus` | `economics/tokenomics-supply::inv_reward_non_increasing`, `inv_supply_monotone`, `inv_reward_floored` | `block-rewards` |
| R9.3 | Separate subsidy: 5 eras (8→4→2→1→0.5 per recipient), zero from era 5 | — | — | `pallets/pallets/flop-subsidy` |
| R9.4 | Work-first genesis (airdrops only) | — | — | genesis config |
| R9.5 | Committee premium inside the validator pool (no second mint) | — | — | `validators::distribute_consensus_reward` |
| R9.6 | Tx-fee split: 10% burn / 100% remainder to author | — | `economics/tokenomics-supply::inv_burn_tier_monotone` | `pallets/pallets/transaction-fees`; runtime `DealWithFees` |
| Appendix D | Chain inclusion-fee terms: base + encoded length + adjusted weight; tip separate | — | — | runtime `TransactionPayment` (`WeightToFee`, `LengthToFee`, `ZKVFeeUpdate`) |
| R9.7–R9.11 | Fixed genesis/allocation; current-runtime de-sudo (**arbitrary `set_code` outside model**) | `Genesis::valid_genesis_is_airdrop_only`, `premint_not_valid`, `airdrop_le_total`, `baseUnit_pos`, `desudo_irreversible` (**modeled transitions only**) | — | genesis chain-spec; `pallet_sudo` removal |
| §9.2 demand | Payer-authorized demanded/settled work (**does not establish independent demand; open E.49**) | — | — | work-crediting paths; synthetic-task floor |

## §10 — HTLC atomic swap

All implemented hashlock pair directions are **target-only** for initial publication. The
pair evidence preserves cross-leg loss/stall outcomes; the shared-clock
Quint model reveals on FLOP first and has stronger refund guards than the implemented counter-first
direction. Its invariants and the Lean premises do not establish deployed pair conformance.

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R10.1 | FLOP-leg conservation/no double-claim supported; end-to-end pair completion **target-only, conformance PENDING E.48** | `Temporal::htlc_atomic` (**supplied abstract trace premises**) | `economics/htlc-atomic-swap::inv_no_double_claim`, `inv_no_stuck_funds` | `pallets/pallets/has-station` |
| R10.2 | Pair-specific timelock margin target; pair conformance **PENDING E.48** | — | `economics/htlc-atomic-swap::inv_flop_timeout_longer` | `has-station::validate_timelock_symmetry` |
| R10.3 | Refund gated on the finalized head | `HtlcRefundFinality::refund_final_safe` | — | `has-station` |
| R10.4 | Permissioned FLOP relayer gate; end-to-end participant binding **PENDING E.48** | — | — | `has-station: RegisteredRelayers`, `relay_preimage` |
| R10.5 | Multi-block settlement (lock max, settle actual) | — | `economics/htlc-atomic-swap::inv_refund_within_timeout` | `has-station` |
| §10.3 | Pair-level fee/inclusion deterrence target **PENDING E.48** | `HtlcIncentives::collusion_deterred` (**conditional premise**) | — | — |

## §11 — Security invariants

| Invariant / R-id | Requirement | Lean | Quint | Rust |
|------------------|-------------|------|-------|------|
| INV-02 | Session spend ≤ session cap | — | — | `agent-wallet: agent_transfer` (`SessionCapExceeded`) |
| `fail_task` | Authorized, rate-limited only | — | — | `flop-poui` (`FailTaskAuthority`) |
| INV-S01 | Monotonic session nonce | `Sessions::replay_rejected` | — | `agent-wallet: SessionInfo.nonce` |
| INV-M06 | Payout atomicity | — | — | `distribute_from_escrow` (`with_storage_layer`) |
| R11.2 | `GnSink::validate_session_gn` plausibility gate | `CalibrationFastPath::session_settlement_capped` | — | `compute-channel: validate_session_gn` |
| R11.2a | Authenticated submitted-turn sum equals claimed `aggregate_gn` (**not execution/completeness**) | — | `channel/session-gn-integrity::inv_no_overclaim` | `compute-channel: verified_work_from_turns` |
| R11.2b | Current-profile channel receipts issue no public work credit | — | `channel/session-gn-integrity::inv_no_public_credit` | `compute-channel` payout helpers; runtime `cooperative_work_credit` regressions |
| §11.3 slashing | Single-authority slash table; value-coupled floor | `CoCVoC::CoCVoC.value_coupled_security` | — | `validators: do_slash` |
| §11.3 curve/waterfall | Correlated equivocation curve; delegated-loss order (operator→delegators→sponsors) | `DelegatedSlashing::waterfall_conserves`, `equivPenalty_mono` | — | `validators: do_slash` |
| INV-02 / fail_task / INV-M06 | Session cap; fail-task authority; payout atomicity | `SessionEnforcement::transfers_within_cap`, `fails_within_rate`, `distribute_atomic` | — | `agent-wallet`; `flop-poui`; `distribute_from_escrow` |

## §12 — Sessions & settlement

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R12.1a | Reserved capacity; no under-use refund | — | `channel/channel-settlement::inv_conservation` | `pallets/pallets/compute-channel` |
| R12.1b | Per-turn signed transcript/receipt (**agreement, not execution correctness; open E.44**) | `Sessions::accept_increments` | — | `compute-channel` |
| R12.1c | HARD measured-root binding; SOFT predicate open E.33 | — | — | `model-registry: verify_measured_root`; `compute-channel` |
| R12.1d | Failed/early close split (`P`, `φ`) conserves | `RefundPenalty::conservation` | — | `compute-channel` |
| R12.1e | Over-use → abort or `top_up_escrow` | — | — | `compute-channel: top_up_escrow` |
| R12.1f | Disputes fraud-only; non-response → fraud | — | `channel/channel-settlement::inv_dispute_fails_closed`, `inv_dispute_upheld_is_closed` | `compute-channel`; `miner-slashing` |
| R12.1g | Freeze economic deadlines; recover through restored/ratified finalized prefix | `ChannelPayoutLiveness::escape_safe` (**prior best-head model; not a witness for current R12.1g**) | — | `compute-channel` (conformance gap until aligned) |
| R12.1h | Session bounds + re-attestation cadence | — | — | `compute-channel` (open: Appendix E.27) |
| R12.2 | Per-identity in-flight reservation cap | — | — | `compute-channel: ActiveReservationCount` |
| R12.3 | Demand-side Sybil cost; perturb, don't punish | `DemandSideSybil::demand_sybil_tacit_collusion_bound` | — | `indexer/` gauges (monitoring) |
| §12 MEV | Settlement ordering bounded | `SettlementOrdering::settlement_ordering_mev_bound`, `settlement_path_ordering_exposure` | — | `compute-channel` |

## §13 — Failure semantics

The actor×failure rows (M1–M16, V1–V12, O1–O4, F1–F5, A1–A10, P1–P4, I1–I3) are their own row-level IDs;
§13.0 is the normative degraded-state settlement policy.

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R13.0 | Liveness repair never converts missing/stale evidence into payout | `DegradedSettlement::positive_payment_requires_available_transcript` | `channel/settlement-degraded-window::inv_liveness_patch_not_safety_bypass` | `compute-channel` |
| R13.0a | Finality stall → freeze finality-clocked deadlines | `DeadlineFailClosed::extend_is_failclosed` | `consensus/finalized-deadlines::inv_final_le_best` | `compute-channel`; `pallet_aleph` |
| R13.0b | DA temporarily unavailable → extend window once | `DegradedSettlement::positive_payment_requires_available_transcript` | `da/da-provider-rotation::inv_repaired_no_stale_slash` | `da-registry`; `compute-channel` |
| R13.0c | DA unrecoverable → fail-closed refund + bond return, no fraud slash | `DegradedSettlement::unrecoverable_transcript_voids_payment` | `channel/settlement-degraded-window::inv_terminal_da_loss_refunds_or_waits` | `compute-channel` (E.31 split residual) |
| R13.0d | Attestation freshness elapsed → reject settlement until re-attested | `FailClosedSettlement::positive_pay_requires_accountable` | `cryptography/tee-attestation-flow` | `compute-channel: AttestationStale` |
| R13.0e | Quorum/service unavailable → pause only attestation clocks within 4 h cap | `QuorumOutagePause::unrelated_continue`, `attestation_paused`, `no_indefinite_pause`, `pause_bounded` | `attestation/attest-quorum` | `flop-poui`; `compute-channel` |
| R13.0f | Governance gate paused/rejected → preserve state; no implicit fallback | `Governance::GovernanceTransition.governance_reachable_safe` | `governance/governance.qnt` | runtime bounds |

## §14 — Governance

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R14.1 | `protocol_upgrade` track: 67% + turnout floor + 14 d timelock | `Governance::GovernanceTransition.governance_reachable_safe` | `governance/governance.qnt` | `governance/tracks.rs`; `pallet_referenda` |
| R14.2 | Foundation submit gate through first halving; FIP enact binds ratified value | `UpgradeSafety::nonFoundation_preHalving_rejected`, `gate_sunsets`, `enactGated_binds` | — | `EnsureFoundationProtocolSubmit` |
| R14.3 | De-sudo precondition | — | — | `pallet_sudo` removal (genesis) |
| R14.4 | Forkless vs. coordinated enactment | — | — | `system.set_code`; node release |
| R14.5 | Current-runtime parameter safety envelope (**arbitrary `set_code` outside model; open E.50**) | `Governance::GovernanceTransition.governance_reachable_safe`; `UpgradeSafety::enactGated_in_envelope`, `migrate_conserves` | `governance/governance.qnt` | runtime bounds |
| R14.6 | Circuit-breaker protected set; auto-expire | — | — | `pallets/pallets/emergency-pause`, `emergency-override` |

## §15 — Validators

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R15.4a | PoUI gate (stake + verification liveness, R15.4c) then weighted distinct sample of 100 (**seat-capture bridge open E.42**) | `CommitteeSampling::selection_capture_le_hoeffding` (**conditional**) | `quint-specs/validators.qnt::poui_committee_only_admits_eligible` (selection snapshot only; three directed witnesses above) | `validators::poui_committee`; `hp_consensus::sample_committee_weighted` |
| R15.4b | BABE-VRF seed, one epoch old, per-rotation domain-sep (**unbiasability not proven**) | `CommitteeSampling::selection_capture_le_hoeffding` (**assumes seed model**) | — | `validators::poui_committee_sampled` (BABE `randomness()`) |
| R15.4c | Verification liveness: recency refreshed only by accepted duties (attestation-bundle signer, TOPLOC/escalation quorum signer, DA audit response, validator dispute opening); prover credit excluded; ≥1 protocol-issued duty per window (**PLANNED E.52**) | — | — | `validators::note_verified_work` (prover-fed today); runtime `ValidatorWorkRecorder` (to be removed) · #1552 |
| R15.5 | Rotation by stake, min-performance floor; eject/promote 50 | — | — | `validators: do_rotate` |
