<!-- GENERATED FILE - DO NOT EDIT BY HAND.
     Regenerate: uv run --script scripts/check_yellowpaper_links.py --matrix
     Stale check: ... --matrix --check -->
# Yellowpaper evidence-coverage matrix

Existence-resolved per-section backing for each top-level `##` section of `yellowpaper.md`: research doc · Lean4 proof · Quint model · Julia sim. Counts only references whose artifact actually resolves.
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
| 14. Governance & Protocol Upgrades | · | ✓ | ✓ | · |
| 15. Validators — Onboarding, Duties, Selection & Rotation | ✓ | ✓ | ✓ | · |
| Appendix A — Parameter Reference | · | · | · | · |
| Appendix B — Sources | ✓ | · | · | · |
| Appendix C — Miner Lifecycle (End-to-End) | ✓ | · | · | · |
| Appendix D — Fee & Revenue Map | ✓ | · | · | · |
| Appendix E — Open Specification Items | · | · | · | · |
| Appendix F — Message & Storage Formats | · | · | · | · |
| Appendix G — Extrinsic Index | · | · | · | · |
| Appendix H — Conformance & Implementation-Status Matrix | · | ✓ | · | · |
| Appendix I — Runtime Composition | · | · | · | · |
| **TOTAL (resolved)** | **16** | **15** | **12** | **2** |

**Legend:** `✓` artifact resolves · `~` referenced-but-dangling (path/symbol not found — a `--check` failure) · `·` absent. The matrix is a *prioritization surface*, not a hard per-type gate: some sections legitimately need only prose/params. `--check` gates the research↔yellowpaper direction **and** any dangling (`~`) reference.
