# Claim inventory and implementation-assumption map

The private release bundle's Lean sources and Lake lock are frozen at
`da13d7c16a11aaf0aa4376ff34476010a0bb792d`. Quint sources and the implementation mappings below
are frozen at `f9c70cad1d991cbe2e6a0651a35145d8c603874b`. Implementation source is not included, so a
named consumer is a pinned review target, not a proved refinement. Every bundled Lean capstone's
axiom closure is checked by `AxiomAudit.lean`: only `propext`, `Classical.choice`, and `Quot.sound`
occur. The Quint runs are finite, seeded simulations, not unbounded proofs.

## Lean claims

### Unit-seat certificate nonforking — formal result reproduced; protocol refinement pending

Exact declaration: `Consensus.FinalCtx.nonforking`.

Hypotheses and units:

- `C.V` is a finite committee; `C.stake : C.V → ℝ` is nonnegative.
- Voting weight is specialized to one equal positive weight `w` per selected seat by
  `CommitteeSampling.equal_weight_seats_bridge`, which assumes `0 < w`,
  `∀ v, C.stake v = w`, and `faulty.card < bftFaultSeats (Fintype.card C.V)`.
- `FinalCtx.faulty_minority` supplies strict `3 · weight(faulty) < total`.
- Each certificate supplies a signer `Finset`, strict quorum
  `2 · total < 3 · weight(signers)`, and a vote from every signer.
- `conflicts b₁ b₂` is supplied, and `FinalCtx.honest_no_equiv` assumes every nonfaulty seat does
  not vote for both conflicting blocks.

`AxiomAudit.lean` checks the initial `n=100` specialization: `3·33<100`, `3·67>2·100`, and the
first safety-breaking seat count is 34. These are committee-seat counts with unit voting weight, not
stake units.

Pinned consumer: `pallets/finality-aleph/src/keychain.rs::verify_committee_multisignature` checks
distinct indexed signatures against Aleph's committee threshold. Mapping certificate admission,
committee/key ownership, honest non-equivocation, network behavior, availability, and liveness to the
complete asynchronous AlephBFT protocol remains assumed. This is finite certificate nonforking only.

### Sampler capture envelope — conditional/target-only; mechanism bridge pending

Exact declaration: `CommitteeSampling.selection_capture_le_hoeffding`.

Hypotheses: a tail function `selTail : ℕ → ℝ`; seat count `N`; fault threshold `f`; attacker fraction
`p`; margin `eps`; the mechanism contract `SelectionTailDominated selTail N p`; `0 ≤ p ≤ 1`;
`0 < N`; `0 ≤ eps`; and `p ≤ f/N - eps`. The conclusion is only
`selTail f ≤ hoeffdingBound N eps`.

Pinned target: `pallets/primitives/hp-consensus/src/committee.rs::sample_committee_weighted` draws
distinct identities with remaining-stake weights. Claim promotion is **PENDING** a
mechanism-specific proof or reproducible test establishing `SelectionTailDominated`, plus the stated
BABE seed premise, for the supported profile. No sampler-to-`3f<n` bridge is currently claimed.

### Broken-TEE fallback bound — abstract result reproduced; runtime refinement pending

Exact declaration: `VerificationStack.sessionVerifier_survives_broken_tee`.

Hypotheses: TOPLOC error `ε` and honest false-flag rate `φ` satisfy `0 ≤ ε ≤ 1` and `0 ≤ φ ≤ 1`.
`sessionVerifier` is defined as abstract TEE/TOPLOC AND-composition with product error; the theorem
sets the TEE error to one and concludes that the composite `Refines` the supplied TOPLOC tier.

Pinned targets: `pallets/verifiers/dstack` and the compute-channel TOPLOC paths. Measurement validity,
error calibration, independence/product semantics, evidence authenticity, and an implementation
refinement from those paths to `sessionVerifier` are assumptions. This does not establish a complete
TEE-independent settlement lane.

### Session acceptance gate — abstract result reproduced; runtime refinement pending

Exact declaration: `VerificationStack.sessionAccept_needs_both`.

The only theorem hypothesis is `h : sessionAccept teeVerified dev τ`; by definition this means
`teeVerified = true ∧ ¬ ToplocV1.flagged dev τ`, with `flagged dev τ := τ ≤ dev`. The conclusion is
`teeVerified = true ∧ dev < τ`. No positivity, distribution, or execution-correctness property is
derived.

Pinned targets: `pallets/pallets/compute-channel/src/lib.rs::ensure_required_toploc_evidence` and
`resolve_toploc_report`, plus `pallets/pallets/flop-poui/src/lib.rs` validator-attestation entrypoints.
Authenticity of the Boolean verification result, evidence-to-execution correctness, distinct-signer
quorum refinement, and reward-path composition remain assumptions.

### Fail-closed settlement resolver — pure result reproduced; runtime refinement pending

Exact declarations: `FailClosedSettlement.unaccountable_fails_closed` and
`FailClosedSettlement.positive_pay_requires_accountable`.

The resolver takes arbitrary `normal : Ledger`, `escrow : ℕ`, and modeled status `s`.
`unaccountable_fails_closed` assumes only `s ≠ accountableAvailable` and concludes zero accused pay
and no bond release. `positive_pay_requires_accountable` assumes only positive resolved pay and
concludes `s = accountableAvailable`. Status is a three-case pure model; balances are natural-number
ledger units.

Pinned targets: `pallets/pallets/compute-channel/src/lib.rs::ensure_attestation_fresh` and
`payout_settlement`. Runtime classification, every settlement branch, currency effects, and bond
release have not been proved to refine the pure resolver.

## Quint bounded results

The private bundle's `MODEL-CHECKS.json` is the exact machine-readable plan. Its `reproduce.py`
typechecks five frozen models, runs 15 invariants for 200 seeded traces each, and executes six
deterministic reachability/mutation witnesses under Quint 0.32.0's TypeScript simulator. The modeled
units and exclusions are:

- `consensus.qnt`: four equal-stake demo validators, stake 10 each, committee cap four; PoUI gating
  and finalized-map prefix safety. It is not AlephBFT's asynchronous protocol.
- `weak-subjectivity.qnt`: demo stake units `total=30`, `faulty=9`, `honest=21`, with strict
  `3f<n` and `3q>2n`; it models checkpoint freshness and old-key exclusion, not unit-seat sampling.
- `proof-verification.qnt`: two abstract task hashes, Boolean verification/replay state, and bounded
  integer reputation. It does not verify TEE cryptography or execution.
- `proof-soundness-gate.qnt`: abstract present/verified Booleans. `inv_repaired_sound` succeeds. The
  private mutation test confirms the detector rejects a deliberately broken presence-only variant;
  its diagnostic trace is retained internally and excluded from the pending public profile.
- `channel-settlement.qnt`: three channel IDs, escrow values 100/200, verified values 0/50/100,
  20% demo penalty, and a four-validator/three-signature demo quorum. Conservation and fail-closed
  dispute results are bounded model statements, not runtime refinement.

The successful mutation tests show the named detectors fire; they do not turn simulation into proof.
Each runtime claim remains pending until its named implementation-refinement obligation passes.
