# Yellowpaper changelog

The initial public release is **0.5.0 (draft)**. No version has been published yet. Prepublication
edits are folded into the initial text; there are no public errata or patch releases to record.
After publication, use Semantic Versioning and Keep a Changelog, preserving released versions.

## [Unreleased]

### Added

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
- Whole-integer `G_n` representation and full-context cache accounting for profile v1.
- Publication checks for references, parameters, source layouts, generated artifacts, and
  offline sampler reproduction independent of the surrounding Python project's dependencies.
- Private Lean/Quint sources, locks, axiom checks, bounded model witnesses and mutation fixtures, plus
  a summary-only **PENDING** public profile; source licensing and implementation refinement must pass
  before the runnable bundle or broader protocol claims are published.
- Curated Lean sources and axiom checks with frozen source hashes, exact committee enumeration,
  and conditional audit/shared-collateral evidence; remaining publication and runtime-test gaps stay explicit.
- HTLC pair-qualification requirements with local-safety scope and an explicit PENDING disposition
  for end-to-end cross-chain conformance.
