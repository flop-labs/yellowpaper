# Money-path golden vectors v1

This is **partial amount-transition conformance**, separate from Appendix F's wire-format corpus.
Passing Appendix F does not discharge money-path conformance. The machine-readable corpus is
[`money-path-v1.json`](money-path-v1.json), checked against
[`money-path-v1.schema.json`](money-path-v1.schema.json). Each vector inherits the full yellowpaper
commit in `source`, and records its requirement IDs, decision ID (or `null` for a pending seed),
decision owner, initial state, calls, and, only when landed, adapter-specific expectations.
Amounts and work totals are decimal strings; money uses base units (10⁻¹⁸ FLOP). Block numbers
and ordinary counts are integers.

For the landed compute-channel fixtures, `input` describes the channel after `open_channel`
has reserved escrow and `submit_toploc_evidence` has registered evidence. The adapter constructs
this state before executing the listed calls; balances and channel state are checked at that boundary.

Run `just verify-money-path` in flop-core. It validates the schema and retained public seeds, tests
the validator, dispatches five landed fixtures through the actual compute-channel mock runtime,
and checks seven D-0524 fixtures through the pallet's shipped rent arithmetic helper.
Unknown adapters fail; all seven rent fixture IDs must execute. Arithmetic coverage does not
count as runtime conformance. The compute-channel runner compares absolute balances, burned
issuance, ordered pallet events, channel state,
tariff-map cleanup, and conservation/work-credit counters with the committed expectations.
Injected one-unit discrepancies in the initial agent balance and final miner balance prove that
both checkpoints reject drift.
The Rust CI test lane consumes this file, including when only the corpus changes. Retained Rust
verification jobs run on draft and synchronize pushes under shared verification admission.

The five `compute-channel` fixtures cover D-0422 / R12.1d: zero work, dust tariff with a non-divisible unused
remainder, full tariff use, atomic rejection above escrow, and miner non-delivery. They explicitly
use the existing mock's **zero audit split**, available published DA, one-base-unit tariff and
20% refund penalty. R11.2b keeps the historical `TotalGnCredited` counter unchanged by channel
payouts; these fixtures begin and end with zero public work credit. The source pin includes the
payment-only settlement rule landed in #2314, separately from D-0422's amount split. These are
gross-accounting fixtures, not a ratification of the live audit carve, tariff calibration,
force/cooperative dominance, or DA-loss settlement. The published
transcript avoids the separate publish-or-forfeit path. Signature and Merkle fixtures are built by
the existing runtime-test helpers; this corpus pins the amounts and transitions, not their bytes.

The seven `paid-storage-arithmetic` fixtures land
[D-0524](../decisions/v0.5.md#d-0524--slot-and-tranche-position-rent) / R5.4e/f/n expectations.
Their flop-core sources are the regression table `formal-specs/da/paid-storage-rent-vectors.md`,
the witnesses in `formal-specs/da/paid-storage-counterexamples.qnt`, and the position-delta
contract in `lean-proofs/FlopSpecs/PaidStorageArithmetic.lean`. Their source pin includes the
ratified decision and §5.4 text.

| Fixture | Final provider earnings (base units) | Payer refund |
| --- | --- | --- |
| `rent-provider-replacement` | A=1, B=0 | 0 |
| `rent-multiple-replacements` | A=1, B=1, C=0, D=1, E=0, F=3 | 0 |
| `rent-failed-block` | A=0, B=1 | 1 |
| `rent-repeat-assignment` | A=1, B=0 | 0 |
| `rent-partial-epochs` | A=3 (split deltas 2+1 equal unsplit 3) | 0 |
| `rent-extension-new-tariff` | A=2, B=0 | 0 |
| `rent-close-partial-service` | A=1, B=0 | 1 |

These balances are rent accounting totals, with zero initial provider earnings and refund;
every case ends with zero reservation escrow. Each `rent_interval` entry in `extrinsics` is an
arithmetic probe over supplied term positions and acceptance, **not a dispatchable extrinsic**.
`at_block` is the interval's end position. The runner splits probes across supplied funding
tranches, checks every interval earning and final balance, and compares split/unsplit epochs.
Tranche funding, historical assignments, acceptance and close/refund bookkeeping are inputs or
test-side accounting. Replacement authorization, challenge holds, release order and real currency
transfers are not exercised. The pallet currently implements fixed-assignment rent; replacement
and extension runtime conformance remain separate work. Independent per-provider ceilings and
residual-cap clipping are superseded, not pending alternatives.

Nineteen pending fixtures have no `expected` payouts. `alternatives` records open rules;
`pending_reason` records decided requirements awaiting executable corpus coverage:

| Family | Seeds | Decision owner |
| --- | --- | --- |
| HTLC redeem | `L=10000`, `A=6200`, `A=L`, `A>L`; fixed lock versus metered redemption/residual | [#1796](https://github.com/flop-labs/flop-core/issues/1796), from [yellowpaper#71](https://github.com/flop-labs/yellowpaper/issues/71) |
| Cooperative settle | `E=1000`, non-divisible `1001`, dust `1`; net full escrow versus gross audit carve | [#1905](https://github.com/flop-labs/flop-core/issues/1905), from [yellowpaper#79](https://github.com/flop-labs/yellowpaper/issues/79) |
| Force dominance | delivered `G_n=10¹⁰`, `E=1000 FLOP`; mode/caller binding and priced tariff | [#1905](https://github.com/flop-labs/flop-core/issues/1905), rate owned by [#1610](https://github.com/flop-labs/flop-core/issues/1610) |
| DA-loss terminal | no prefix and a co-signed prefix; D-0430 full refund versus a superseding prefix rule | [#1948](https://github.com/flop-labs/flop-core/issues/1948) |
| R12.2 slot release | settle / expire / timeout / fraud release once; finalize release versus retention remains open in the cited rule | [#2649](https://github.com/flop-labs/flop-core/issues/2649), from [yellowpaper#48](https://github.com/flop-labs/yellowpaper/issues/48) |
| R5.3f lease withdrawal | unpinned before expiry, pinned rejection, nonpublisher rejection, third-party top-up, outstanding audit | [#2649](https://github.com/flop-labs/flop-core/issues/2649), from [yellowpaper#70](https://github.com/flop-labs/yellowpaper/issues/70) |

`pending` is neither a pass nor an expected test failure. Required gates stay green while reporting
pending coverage separately. New pending calls are scenario placeholders, not complete signed
extrinsic arguments. R12.2 decides settle/expire/timeout/fraud release; its enumeration omits
finalize. R5.3f already decides publisher-only withdrawal, the pin guard, eligibility independent
of `lease_end`, full publisher deposit refund and no extender refund. Only resolution of an
already-issued audit remains open (E.47); the seeds do not reopen those decided withdrawal rules.
HTLC residual and cooperative carve seeds remain pending on #1796 / #1905.
D-0430 remains the baseline for DA loss; existing receipt-based runtime behavior
does not become policy by inclusion in this corpus.

To land a pending family, identify its ratified D-id, pin the corresponding yellowpaper commit,
replace alternatives with exact post-state expectations, extend the schema and runtime adapter,
and run the named gate. The adapter rejects unconsumed landed calls/events; adding a fixture cannot
silently turn into a schema-only conformance pass. A public export can run
`uv run --script evidence/check-money-path-vectors.py` to validate the corpus structure; executable
amount checks require flop-core's pallet runners, with their runtime/arithmetic limits above.
