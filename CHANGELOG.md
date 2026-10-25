# Yellowpaper changelog

The initial public release is **0.5.0 (draft)**. No version has been published yet. Prepublication
edits are folded into the initial text.
After publication, use [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), preserving released versions.

## [Unreleased]

### Changed

- State in §15.5 R15.5 that proven-fault slash proceeds at the active-set floor are confiscated and transferred to the Foundation (R9.10) rather than burned.

- Propagate the zero-burn, operator self-stake-only, and off-chain referral rulings to the normative
  spec and canonical parameters (D-0529, D-0530, D-0531; #2792, #1945, #1358): set
  `tx_fee_burn_percent_live` (`BurnFees`) to 0% with 100% of live transaction fees and tips routed to
  the block author (§9.1 R9.6, Appendix D, Appendix H); replace legacy "full-burn" slash terminology
  with 100% routing to `FLOPFoundationAccount` (§11.3, §13.2, §15.7, Appendix A); prohibit third-party
  delegated staking into validators and miners, deprecate delegation extrinsics/caps and operator
  commissions (`miner_staking::delegate`, `max_delegators_per_miner`, `miner_commission_cap_percent`),
  and formalize the 5% duration-locked community staking pool across seven lock tiers without
  slashing risk (§2.3, §6.1, §9.1 R9.12, §11.3, §15.2, E.32, E.40, G.3); and record that the
  800,000,000 FLOP `genesis_reserve` funds the off-chain explorer referral leaderboard and periodic
  lotteries in place of on-chain referral commissions (§9.1 R9.4, E.38).

- Let sponsors post an operator's whole registration bond on devnet and testnet (R6.1a; D-0528). The
  bond stays frozen in the sponsor account and is refunded only to the sponsor. It counts as miner or
  validator self-stake only on runtimes built with `sponsored_self_stake_enabled`. Narrow E.32 to its
  mainnet questions; index the new calls in G.3 and their status in H.1.

- Reconcile normative contradictions surfaced by the 2026-10-13 mirror sync (#2648): align §15.5,
  E.56 and H.5 with the implemented `validator_min_active_validators` = 4 removal/rotation floor and
  10% churn cap (#1727) while keeping the D-0507/D-0508/E.42 policy questions open; reconcile §9.3
  R9.9, §15.5 R15.5/R15.5b and Appendix G.3 on active-set entry paths (`rotate` promotion from
  `ValidatorQueue` vs direct `un_jail`/`rejoin` restoration under `validator_active_set_cap`, and
  rotation ejection thawing self-stake before re-registration); align §9, R9.2, R9.3, Appendix A and
  Appendix D cumulative emission and subsidy totals with the runtime's `era(b) = ⌊b / H⌋` boundary
  and unrewarded genesis block 0 (R9.7); define the +9%/yr validator stake baseline's annual
  `31,536,000`-block boundary, integer floor formula and 1%-of-`total_issuance` cap in §15.2; update
  §13.2 V11 and E.57 to compose `W` against R1.2a's multi-round bisection dispute lifetime (`8 d 20 h`);
  define Validator grant unlocked amount (`P − S`) and slashed-principal accounting `S` in §8.2
  R8.7/R8.8; and clarify in §11.2 R11.2b and §8.2 R8.7 that settled-session airdrop unlock/spend
  credit is private payment-denominated vesting credit distinct from public `G_n` work credit.

- Credit miner block rewards toward the Miner airdrop unlock (R8.7; D-0527, superseding D-0517
  item 1). A Miner grant now unlocks one FLOP per FLOP of the miner-leg block rewards minted to the
  grantee, counted once the distribution block is finalized, as well as per FLOP of its settled
  channel payouts after the dispute window. Other block-reward legs, the subsidy, transaction fees, refunds, penalties and
  bonds still earn nothing.

- Mark INV-M06 payout atomicity LIVE in §11.1 and H.5: channel settlement now reverts when the
  refund-penalty burn fails, as it already did for the miner and refund transfers.

- Name RTMR3 as the only accepted measurement path for the model root (§3.3 step 2), matching the
  step 3 verifier and D-0404.

- Bring Appendix E/H status, trackers and code paths up to date with landed code; no protocol rule
  changes. Index the on-chain bisection dispute calls in G.1 and correct `open_dispute`'s arguments;
  mark multi-round bisection and `G_n` overflow rejection LIVE; record the development-network
  paid-storage pallet (rent released without audit), its CI-run Quint models and its simulation as
  PARTIAL; narrow E.9, E.32, E.41, E.46, E.47, E.51 and E.54 to what remains open; and replace
  enforcement paths for code removed with the per-task path in §11.1 and H.5.

- Specify Appendix D's chain inclusion-fee terms, align the shared-collateral example with its
  generated four-claim row, and list both work-vesting grant entry points in Appendix G.3.

- Ratify slot/tranche position rent (D-0524, R5.4e/f, E.54, F.7, G.4): replacements retain
  historical earned rent, failed or forfeited deltas refund the payer, and new tariffs use separate
  funded tranches. Supersede independent provider ceilings; add seven executable balance vectors.

- Describe implemented HTLC pair directions as target-only for initial publication (E.48).
  Preserve cross-leg late-claim, finality-stall and failed-payout counterexamples, qualify the local
  formal models, and add focused pallet/contract expiry-ordering tests and a reproducible pair gate.

- Specify the Agent airdrop unlock as spend-to-unlock (R8.7, R8.8; D-0522). An Agent grant unlocks
  nothing at its start and has no end block; it unlocks one FLOP per three FLOP of its locked
  principal in the gross `payable` of settled sessions, once every fraud dispute raised in the window has
  resolved, and its locked compute spend is capped at three quarters of principal. Channel escrow
  drawn from locked principal goes to the `payable` first and is refunded first, back to the grant as frozen
  principal. E.38 no longer holds the Agent horizon.

- Make current-profile channel settlements payment-only (§11.2 R11.2b). Receipt claims no
  longer feed public work rewards or performance vesting, including unilateral/DA-void payout.
  Historical recovery and future audited credit remain open.

- Tighten the Appendix F vector schema to require canonical fields, byte widths, integer ranges,
  case identities, and coverage. Wide integers use decimal strings so JSON consumers preserve
  their exact values; the public generator also checks duplicate identities.
- Protect Ephemeral DA blobs from pruning while any usage pin remains, matching Leased blobs
  (R5.3d; D-0521). Pins do not extend expiry or admit new usage after the retention deadline.

- Replace §8.2's Miner and Validator airdrop unlock (R8.7, R8.8; D-0517). A Miner grant is a quarter
  liquid at its start and unlocks the rest one FLOP per FLOP it receives as miner from settled
  sessions once their dispute window passes, with no end block (D-0527 adds miner block rewards), and
  the performance adjustment is retired. A Validator grant stays frozen until the first halving, then grants release one per day
  without unbonding; none releases until E.38 fixes the order. Only Agent grants may still spend
  locked principal on compute; a miner may bond its locked principal as its own self-stake.
- Make block rewards and the subsidy liquid on issue (R9.13; D-0518). The miner and validator legs and
  the Labs/Foundation subsidy are never auto-compounded, force-staked or vested, and agent-leg payouts
  are liquid once E.40 ratifies; validator earnings no longer auto-compound into locked stake, and E.39
  is closed.

- Ratify §8.2's grant-landing (R8.6) and claim and locked-spend (R8.8) rules as D-0515. D-0514
  had covered only R8.3–R8.5 and R8.7; the requirement text is unchanged.

- Repoint Appendix E blockers to live trackers and refresh Appendix H implementation grades for
  fee distribution, metering overflow, session-key invariants, and collusion monitoring.

### Added

- Specify paid-storage service lanes that close at a fixed boundary with
  a funding-pinned claim deadline on the finalized prefix. Only the lane's provider redeems, with
  strict sequence, counter and amount checks, including after reassignment. Otherwise-valid
  post-close signatures remain payable within the unspent budget until the deadline; finalization
  refunds only the remainder above it. Unknown finality rejects both operations. R5.4g, R5.4j,
  E.54, F.7 and G.4 carry the rule. E.54 constrains sequential entitlement-maturity and funded-request
  timing to fit that fixed deadline and requires an actual redeem-valid dispatch opportunity under
  permitted finality behavior before affected work can be enabled. Timing arithmetic alone does not
  establish it; the numerical window and production activation remain unratified.

- Era-T conversion and airdrop vesting (§8.2, R8.3–R8.8; D-0514). Conversion draws only on the
  fixed genesis cohort pools. Agents are scored on settled compute-channel spend and miners on
  verified effective-FLOP; balance, stake, job count and active days carry no weight. Snapshot and
  evidence of record are fixed before genesis lock. Grants land as frozen genesis balances with
  linear vesting and finalized-head claims. The miner performance adjustment fails closed: without
  both performance inputs a Miner grant unlocks nothing before its end block. E.38 keeps score caps,
  the validator activity basis, the agent horizon and the remainder disposition open.

- Development-network exception to the paid-storage activation gate (D-0512, R5.4q): a valueless
  devnet may run the §5.4 extension ahead of E.54 only from a runtime built with a non-default,
  development-only flag, under an explicitly unratified profile with placeholder values kept out of
  the canonical parameters, with unaudited rent releases marked as such, and with no result citable
  as E.54/E.47 evidence. R5.4k now names R5.4q as its only exception; every other network is unchanged.

- Paid encrypted agent memory/data storage specification (D-0506): fixed-term validator storage
  revenue, metered retrieval vouchers, scoped authority, versioned memory heads, and bounded
  audit/repair/refund obligations. Activation remains gated on E.54 economics/security calibration
  and E.47 availability evidence; protocol/model DA pricing is preserved. Distinguish client encryption
  from enforceable envelope validation, price setup separately from rent, and separate provider quotes
  from protocol limits and calibration inputs. Fund storage as take-or-pay capacity reservations:
  deletion frees bytes for reuse and refunds nothing, the remaining term is transferable, and rent
  rounds once per provider. Price by one epoch tariff (stake-weighted median of capacity-declaring
  validators, bounded step, under-supply tripwire) with protocol-random assignment among declarers.
  Keep the chain footprint flat: one reservation per payer, objects and ordinary memory heads in a
  provider-group manifest with quorum receipts and one checkpoint per provider per epoch, rent
  released per epoch without claims, setup and retrieval on one service lane per provider. Advance
  the retrieval request fee before the first chunk, calibrate audit sampling by `p_a × c_r ≥ c_s`,
  count held-back rent as bond. Bound attempted traffic and retries independently of voucher billing.

- Initial normative specification of consensus, useful-inference verification, reference-work
  accounting, settlement, economics, data availability, and governance.
- Strict `< ⅓` Byzantine committee-seat premise with Lean quorum/nonforking references and explicit
  sampler, protocol-integration, and liveness assumptions.
- Reproducible committee counterexample, internal source-checked SCALE extrinsic fixtures, charged-weight
  ledger, negative capacity evidence, and conditional audit scenarios. Raw capacity-mechanism failure
  diagnostics and their reproducer remain private while E.46 is pending.
- Parameter and wire-format references, conformance status, and numbered open specification items.
- v0.5 decision D-0501 and proposed D-0502, pending ratification; D-0502 would withdraw unmeasured
  byte, throughput, and latency targets while earlier decisions retain their original IDs and history.
- D-0505 interoperable wire/rejection profile with explicit leaf and receipt versions, replay domains,
  legacy cutoffs, FCC4 transcripts, and a public Rust/TypeScript/Python vector corpus.
- D-0511 canonical compute-channel transcript/receipt definition, including per-channel decode-policy
  pinning and the path-specific `payable` derivation.
- D-0440 genesis sizing: a 4,400,000,000 FLOP genesis supply whose validator cohort is the aggregate
  1,200,000 FLOP bond across the 1,000-seat active-set cap.
- Proposed D-0507–D-0510, pending ratification: post-testnet genesis validator selection and placement,
  floor-based rotation with an on-chain performance signal, committee sessions aligned to the BABE
  epoch, and bootstrap nodes.
- E.55 open item for a canonical pre-session quote/discovery contract.
- Whole-integer `G_n` representation and full-context cache accounting for profile v1.
- Publication checks for references, parameters, source layouts, generated artifacts, and
  offline sampler reproduction independent of the surrounding Python project's dependencies.
- Public standalone claim-ledger reproduction and canonical Appendix A parameter source/generator,
  with gates for published command paths, Python floors, and lossy parameter descriptions.
- Private Lean/Quint sources, locks, axiom checks, bounded model witnesses and mutation fixtures, plus
  a summary-only **PENDING** public profile; source licensing and implementation refinement must pass
  before the runnable bundle or broader protocol claims are published.
- Curated Lean sources and axiom checks with frozen source hashes, exact committee enumeration,
  and conditional audit/shared-collateral evidence; remaining publication and runtime-test gaps stay explicit.
- HTLC pair-qualification requirements with local-safety scope and an explicit PENDING disposition
  for end-to-end cross-chain conformance.
