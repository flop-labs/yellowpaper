# FLOP Network — Yellow Paper

**A research-draft normative specification of the FLOP protocol**, published for open technical
review.

The paper specifies a proposed inference-metering and settlement layer on a Substrate/FRAME runtime,
with BABE block authoring and AlephBFT finality. Its assurance claims have different evidence levels:
some are protocol requirements, some are conditional mathematical results, some have empirical
measurements, and some remain open or lack publicly reproducible evidence. Read each claim with its
stated assumptions and status.

| | |
|---|---|
| **Read** | [`yellowpaper.md`](yellowpaper.md) |
| **Version** | 0.5.0 (draft) — initial public draft |
| **Changes** | [`CHANGELOG.md`](CHANGELOG.md) |
| **Claim evidence** | [`research/prepublication-evidence.md`](research/prepublication-evidence.md) |
| **Wire-format vectors** | [`evidence/wire-format-v1.json`](evidence/wire-format-v1.json) · [`schema`](evidence/wire-format-v1.schema.json) |
| **Formal claims and publication status** | [`evidence/proof-bundle/README.md`](evidence/proof-bundle/README.md) · [`yellowpaper-attribution.md`](yellowpaper-attribution.md) |
| **Give feedback** | [Open an issue](../../issues/new/choose) |
| **Report a vulnerability** | **Not** an issue — see [`SECURITY.md`](SECURITY.md) |

## What this repository is

A **read-only mirror**. The spec is authored in FLOP's engineering repository, where it is gated
against parameter drift (Appendix A is generated from the canonical parameter YAML) and against
citation drift. Corrections land upstream and are re-published here; see
[`CONTRIBUTING.md`](CONTRIBUTING.md) for what that means for pull requests.

Three transforms are applied at publish time, noted at the top of the spec itself: Appendix H's
code-path/tracker column is removed, local links are retargeted to published paths/anchors or
flattened when their file is unpublished, and machine-readable citation comments are stripped.
**No normative text is altered.**

The mirror also publishes a curated claim-evidence ledger. Raw mechanism-failure diagnostics and their
reproducer remain in the private engineering repository until the pending mechanism work is complete.
The mirror does not imply that every cited Lean, Quint, Julia, research, test, or implementation artifact
is publicly available.

## How to interpret evidence

- **Artifact exists** means the authoring-repository path and any named symbol resolved when the
  coverage matrix was generated. It does not show that assumptions hold or that code enforces the
  result.
- **Conditional proof/model result** means the stated conclusion follows under listed assumptions.
  Check whether the ledger marks those assumptions as discharged for the implemented protocol.
- **Empirical evidence** means a recorded experiment supports a claim for its stated workload,
  hardware, model, precision, sample, and uncertainty. It is not a universal proof.
- **Unavailable evidence** means a cited internal artifact is not in this public mirror. Treat the
  corresponding assurance as unverified here unless the curated ledger provides public evidence.

The [prepublication evidence ledger](research/prepublication-evidence.md) covers the committee
counterexample, direct/session encoding arithmetic, and illustrative audit exposure. It is not a complete
proof or empirical-evidence ledger for the paper.

The [sampler analysis](research/committee-sampler-evidence.md) adds exact population enumeration and
scopes the real-code regressions. The [audit analysis](research/audit-economics-evidence.md) exposes
conditional payoffs and shared collateral. Both include standalone reproducible data. The
[formal evidence status](evidence/proof-bundle/README.md) records the reproduced, hypothesis-scoped
Lean and Quint results and the concrete gates still required. The runnable source bundle, mutation
fixture, and raw diagnostic trace remain private while the
[source-license requirement](evidence/proof-bundle/LICENSES.md) and implementation refinements are
pending.
The [recorded clean-room check](evidence/yellowpaper-proof-validation.json) identifies the exact
proof-bundle hash, toolchain, commands, and remaining limitations.

The [wire-format corpus](evidence/wire-format-v1.json) freezes Appendix F's positive and rejection
cases. Check it without the private repository using
`uv run --script evidence/generate-wire-format-vectors.py --check`; the adjacent
`evidence/compute-channel.py` is the standalone Python implementation used by that command.

## Where the interesting problems are

This is a draft, and it is explicit about what is not settled. If you are looking for something to
attack, start here rather than at §1:

- **[Appendix E — Open Specification Items](yellowpaper.md#appendix-e--open-specification-items)** —
  numbered stubs for every unresolved value and mechanism, each with a placeholder to model against,
  its home section, and what blocks it. These are the questions we know we have.
- **[Appendix H — Conformance & Status Matrix](yellowpaper.md#appendix-h--conformance--implementation-status-matrix)** —
  which mechanisms are implemented, partial, or designed-not-wired. These labels report
  implementation status; they do not report formal-proof coverage or empirical validation.
- **[`yellowpaper-coverage.md`](yellowpaper-coverage.md)** — per-section citation existence for
  research, Lean 4, Quint, and Julia artifacts. A checkmark records resolution in the authoring
  repository; it is not proof applicability, implementation coverage, or public availability.
- **[`decisions/v0.5.md`](decisions/v0.5.md)** — the initial-release decision record. It states which
  earlier decisions remain applicable and links their [v0.4 provenance](decisions/v0.4.md).
  Each entry lists assumptions and alternatives; disagreements are useful feedback.

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
