# FLOP Network — Yellow Paper

**The normative specification of the FLOP protocol**, published for open technical review.

FLOP is a verified-inference settlement layer: AI inference is metered in effective FLOP, proven,
and settled on-chain at 1-second block times on a Substrate/FRAME runtime, with BABE authoring and
AlephBFT finality under a stake-weighted, PoUI-gated committee.

| | |
|---|---|
| **Read** | [`yellowpaper.md`](yellowpaper.md) |
| **Version** | v0.5 (draft) — see [`ERRATA.md`](ERRATA.md) for post-publication corrections |
| **Give feedback** | [Open an issue](../../issues/new/choose) |
| **Report a vulnerability** | **Not** an issue — see [`SECURITY.md`](SECURITY.md) |

## What this repository is

A **read-only mirror**. The spec is authored in FLOP's engineering repository, where it is gated
against parameter drift (Appendix A is generated from the canonical parameter YAML) and against
citation drift. Corrections land upstream and are re-published here; see
[`CONTRIBUTING.md`](CONTRIBUTING.md) for what that means for pull requests.

Three transforms are applied at publish time, noted at the top of the spec itself: Appendix H's
code-path/tracker column is removed, links into unpublished internal documents are flattened to
plain text, and machine-readable citation comments are stripped. **No normative text is altered.**

## Where the interesting problems are

This is a draft, and it is explicit about what is not settled. If you are looking for something to
attack, start here rather than at §1:

- **[Appendix E — Open Specification Items](yellowpaper.md#appendix-e--open-specification-items)** —
  numbered stubs for every unresolved value and mechanism, each with a placeholder to model against,
  its home section, and what blocks it. These are the questions we know we have.
- **[Appendix H — Conformance & Status Matrix](yellowpaper.md#appendix-h--conformance--implementation-status-matrix)** —
  which mechanisms are implemented, partial, or designed-not-wired. Requirements marked `PARTIAL` or
  `PLANNED` are specified but unproven in practice.
- **[`yellowpaper-coverage.md`](yellowpaper-coverage.md)** — per-section formal-evidence coverage
  (Lean 4 · Quint · Julia simulation). A section with sparse backing is a section whose argument
  rests on prose.
- **[`decisions/v0.4.md`](decisions/v0.4.md)** — the decision record. Each entry is MADR-shaped and
  lists the alternatives rejected. Disagreeing with a rejection is useful feedback.

Areas where adversarial review is most valuable: the verification tiers and their trust domains
(§3), effective-FLOP metering and the throughput tripwire (§4), miner and validator economics
including the stake floor and slashing curves (§7–§9, §11, §15), the session/dispute game (§12), and
the sovereign DA serve-or-slash construction (§5).

## How to read it

Read [§0 — Conformance & Reading Guide](yellowpaper.md#0-conformance--reading-guide) first. In
short: section bodies are **normative** and use RFC 2119 keywords; rationale, prior art, and
decision provenance are confined to a non-normative trailer at the end of each section;
implementation status is out of band in Appendix H; parameter values of record are in Appendix A.

## Citing

Cite by **version and section**, e.g. *FLOP Yellow Paper v0.5 §3.4*. Section numbering and
requirement IDs are stable within a version; a release tag pins the exact text.

## License

The text is licensed [CC BY 4.0](LICENSE). You may share and adapt it with attribution.
