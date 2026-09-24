# Yellowpaper changelog

The initial public release is **0.5.0 (draft)**. No version has been published yet. Prepublication
edits are folded into the initial text; there are no public errata or patch releases to record.
After publication, use Semantic Versioning and Keep a Changelog, preserving released versions.

## [Unreleased]

### Added

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
