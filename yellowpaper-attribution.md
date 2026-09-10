# Yellowpaper — Statement Attribution (companion index)

**Non-normative. Not part of the spec.** This file maps each numbered requirement (`R-id`) and key
invariant in [`yellowpaper.md`](yellowpaper.md) to its **formal witness** (Lean theorem / Quint
invariant) and **Rust code path**. It deliberately lives outside the yellowpaper: it exposes
implementation and proof-artifact detail that the normative spec keeps out of its body (the spec
describes the *target protocol*, not where it is proved or coded).

**How to read it.** A cell names the artifact that backs the requirement:
- **Lean** — a theorem in `formal-specs/lean/FlopSpecs/<File>.lean` (`File::theorem`).
- **Quint** — an invariant in `formal-specs/<path>.qnt` (`file::inv_*`).
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

**Maintenance.** Unlike the yellowpaper's inline `<!-- cite:… -->` comments (gated by
`scripts/check_yellowpaper_links.py`), this file is **not** machine-checked. Symbols and paths were
verified to exist when written; treat it as a maintained index and re-verify on rename. The gated,
section-level evidence view is [`yellowpaper-coverage.md`](yellowpaper-coverage.md); the parameter
cross-language names (canonical ⇄ Rust ⇄ Lean ⇄ Quint) are the yellowpaper's Appendix A; per-mechanism
build status is its Appendix H.

---

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
| R7.1 | Entry via correctness-verified burst; per-credential binding, consumed once | `CalibrationFastPath::accept_initial_requires_capacity_bond` | `verification/hardware-calibration::inv_usable_is_bonded` | `pallets/pallets/hw-calibration: accept_benchmark_burst` |
| R7.1a | `accept_benchmark_burst` fail-closed conditions; deposit before activation | `Calibration::Bp_le_worstMean` | `verification/hardware-calibration::inv_active_is_usable` | `hw-calibration` |
| R7.1b | HARD-tier inventory: missing SKU ceiling fails closed, no SOFT downgrade | `Computable::classAdjustedCeiling` | `verification/hardware-calibration::inv_accepted_cap_uses_versioned_ceiling` | `hw-calibration` |
| R7.1c | `C_emp` counted once; never multiplied by GPU/channel/session/batch | `Calibration::Gn_le_max` | `verification/hardware-calibration::inv_cap_le_empirical` | `hw-calibration: flop_meter` |
| R7.2 | Renewable cap: lease-frozen; renewal never raises cap; SKU change no silent alter | `CalibrationFastPath::renewal_never_raises_cap` | `verification/hardware-calibration::inv_renewal_never_raises_cap` | `hw-calibration: renew_benchmark_cap` |
| R7.3 | Restart/reconnect renewal; fingerprint change invalidates; drift≠cheat by signature | `CalibrationDrift::cheat_detected`; `DriftDetection::breach_on_large_deviation`, `no_breach_in_tolerance` (EWMA statistical layer) | `verification/hardware-calibration::inv_hardware_identity_bound` | `hw-calibration`; `miner-worker` |

## §8 — Performance-locked vesting

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R8.1 | Convex `R_p²` unlock (`R_p² ≤ R_p`) | `Vesting::unlock_le_ratio` | — | `pallets/pallets/work-vesting` |
| R8.2 | Blackout revocation (1.0× slash) | — | — | `work-vesting` |
| R8.1a–b | Ghost-Task known-answer canary; bounded escrow slash | `GhostTaskAudit::bounded_slash_payoff` | `verification/statistical-sampling::invariant_checker_quorum_before_slash`, `invariant_no_self_checked_slash` | `pallets/pallets/synthetic-tasks` |

## §9 — Emission & supply

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R9.1 | Block reward sourced from params, bounded `≤ 96` | — | `economics/tokenomics-supply::inv_reward_le_initial` | `pallets/pallets/block-rewards` |
| R9.2 | Geometric floored halving; supply monotone | `HalvingBoundary::halving_no_exodus` | `economics/tokenomics-supply::inv_reward_non_increasing`, `inv_supply_monotone`, `inv_reward_floored` | `block-rewards` |
| R9.3 | Separate subsidy, era 1 only | — | — | `pallets/pallets/flop-subsidy` |
| R9.4 | Work-first genesis (airdrops only) | — | — | genesis config |
| R9.5 | Committee premium inside the validator pool (no second mint) | — | — | `validators::distribute_consensus_reward` |
| R9.6 | Tx-fee split: 10% burn / 100% remainder to author | — | `economics/tokenomics-supply::inv_burn_tier_monotone` | `pallets/pallets/transaction-fees`; runtime `DealWithFees` |
| R9.7–R9.11 | Fixed genesis/allocation; current-runtime de-sudo (**arbitrary `set_code` outside model**) | `Genesis::valid_genesis_is_airdrop_only`, `premint_not_valid`, `airdrop_le_total`, `baseUnit_pos`, `desudo_irreversible` (**modeled transitions only**) | — | genesis chain-spec; `pallet_sudo` removal |
| §9.2 demand | Payer-authorized demanded/settled work (**does not establish independent demand; open E.49**) | — | — | work-crediting paths; synthetic-task floor |

## §10 — HTLC atomic swap

| R-id | Requirement | Lean | Quint | Rust |
|------|-------------|------|-------|------|
| R10.1 | FLOP-leg conservation/no double-claim supported; end-to-end pair completion **PENDING E.48** | `Temporal::htlc_atomic` (**abstract/local state model**) | `economics/htlc-atomic-swap::inv_no_double_claim`, `inv_no_stuck_funds` | `pallets/pallets/has-station` |
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
| R15.4a | PoUI gate (stake + verification liveness, R15.4c) then weighted distinct sample of 100 (**seat-capture bridge open E.42**) | `CommitteeSampling::selection_capture_le_hoeffding` (**conditional**) | — | `validators::poui_committee`; `hp_consensus::sample_committee_weighted` |
| R15.4b | BABE-VRF seed, one epoch old, per-rotation domain-sep (**unbiasability not proven**) | `CommitteeSampling::selection_capture_le_hoeffding` (**assumes seed model**) | — | `validators::poui_committee_sampled` (BABE `randomness()`) |
| R15.4c | Verification liveness: recency refreshed only by accepted duties (attestation-bundle signer, TOPLOC/escalation quorum signer, DA audit response, validator dispute opening); prover credit excluded; ≥1 protocol-issued duty per window (**PLANNED E.52**) | — | — | `validators::note_verified_work` (prover-fed today); runtime `ValidatorWorkRecorder` (to be removed) · #1552 |
| R15.5 | Rotation by stake, min-performance floor; eject/promote 50 | — | — | `validators: do_rotate` |
