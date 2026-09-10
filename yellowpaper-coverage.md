<!-- GENERATED FILE - DO NOT EDIT BY HAND.
     Regenerate: uv run --script scripts/check_yellowpaper_links.py --matrix
     Stale check: ... --matrix --check -->
# Yellowpaper evidence-coverage matrix

Existence-resolved per-section citations for each top-level `##` section of `yellowpaper.md`: research doc · Lean4 proof · Quint model · Julia sim. Counts only references whose artifact path/symbol resolves; see the assurance and public-availability limits below.
| Section | research | Lean4 | Quint | Julia-sim |
|---|:--:|:--:|:--:|:--:|
| 0. Conformance & Reading Guide | · | · | · | · |
| 1. Notation, Conventions & Glossary | · | · | · | · |
| 2. Consensus | ✓ | ✓ | ✓ | · |
| 3. Proof of Useful Inference — Verification Architecture | ✓ | ✓ | ✓ | · |
| 4. Effective-FLOP Metering | ✓ | ✓ | · | · |
| 5. On-chain / Off-chain Architecture & Sizing | ✓ | ✓ | ✓ | · |
| 6. Base-Layer Primitives & Agent Autonomy | ✓ | ✓ | · | · |
| 7. Hardware Calibration & Drift | ✓ | ✓ | ✓ | · |
| 8. Performance-Locked Vesting | ✓ | ✓ | ✓ | · |
| 9. Emission & Supply | ✓ | ✓ | ✓ | ✓ |
| 10. HTLC Atomic Swap | ✓ | ✓ | ✓ | · |
| 11. Security Invariants | ✓ | ✓ | ✓ | · |
| 12. Agents as Market Actors — Sessions & Settlement | ✓ | ✓ | ✓ | ✓ |
| 13. Failure Semantics — Actor × Failure Matrix | ✓ | ✓ | ✓ | · |
| 14. Governance & Protocol Upgrades | ✓ | ✓ | ✓ | · |
| 15. Validators — Onboarding, Duties, Selection & Rotation | ✓ | ✓ | ✓ | · |
| Appendix A — Parameter Reference | · | · | · | · |
| Appendix B — Sources | ✓ | · | · | · |
| Appendix C — Miner Lifecycle (End-to-End) | ✓ | · | · | · |
| Appendix D — Fee & Revenue Map | ✓ | · | · | · |
| Appendix E — Open Specification Items | ✓ | · | · | · |
| Appendix F — Message & Storage Formats | · | · | · | · |
| Appendix G — Extrinsic Index | · | · | · | · |
| Appendix H — Conformance & Implementation-Status Matrix | · | ✓ | · | · |
| Appendix I — Runtime Composition | · | · | · | · |
| **TOTAL (resolved)** | **18** | **15** | **12** | **2** |

**Legend:** `✓` the cited path exists in the authoring repository and, when a symbol is named, that symbol resolves in the cited file · `~` referenced-but-dangling (path/symbol not found — a `--check` failure) · `·` absent. This is an artifact-existence and citation-integrity matrix. A `✓` does **not** establish that a theorem's assumptions hold for the protocol, that a proof covers the full implementation, that a modeled gate is wired in settlement, or that an empirical claim has been reproduced.

**Public availability:** the public mirror includes this matrix, the curated prepublication evidence ledger, its data, and its reproducer. The full internal research, Lean, Quint, Julia, and implementation source trees are not exported by this matrix. A resolved cell therefore does not by itself mean its underlying artifact is public. The matrix is a *prioritization surface*, not a hard per-type assurance gate: some sections legitimately need only prose/params. `--check` gates the research↔yellowpaper direction, stale internal section/fragment links, and any dangling (`~`) reference.
