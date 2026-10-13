# Money-path golden vectors v1

This is **partial amount-transition conformance**, separate from Appendix F's wire-format corpus.
Passing Appendix F does not discharge money-path conformance. The machine-readable corpus is
[`money-path-v1.json`](money-path-v1.json), checked against
[`money-path-v1.schema.json`](money-path-v1.schema.json). Each vector inherits the full yellowpaper
commit in `source`, and records its requirement IDs, decision ID (or `null` pending ratification),
decision owner, initial state, calls, and, only when landed, expected balances, events and storage.
Amounts and work totals are decimal strings; money uses base units (10⁻¹⁸ FLOP). Block numbers
and ordinary counts are integers.

For the landed compute-channel fixtures, `input` describes the channel after `open_channel`
has reserved escrow and `submit_toploc_evidence` has registered evidence. The adapter constructs
this state before executing the listed calls; balances and channel state are checked at that boundary.

Run `just verify-money-path` in flop-core. It validates the schema and retained public seeds, tests
the validator, and dispatches landed fixtures through the actual compute-channel mock runtime.
The runner compares absolute balances, burned issuance, ordered pallet events, channel state,
tariff-map cleanup, and conservation/work-credit counters with the committed expectations.
Injected one-unit discrepancies in the initial agent balance and final miner balance prove that
both checkpoints reject drift.
The Rust CI test lane consumes this file, including when only the corpus changes. As with other
pallet tests, heavy CI runs on a ready transition or with `full-ci` after a subsequent push.

The five landed fixtures cover D-0422 / R12.1d: zero work, dust tariff with a non-divisible unused
remainder, full tariff use, atomic rejection above escrow, and miner non-delivery. They explicitly
use the existing mock's **zero audit split**, available published DA, one-base-unit tariff and
20% refund penalty. R11.2b keeps the historical `TotalGnCredited` counter unchanged by channel
payouts; these fixtures begin and end with zero public work credit. The source pin includes the
payment-only settlement rule landed in #2314, separately from D-0422's amount split. These are
gross-accounting fixtures, not a ratification of the live audit carve, tariff calibration,
force/cooperative dominance, or DA-loss settlement. The published
transcript avoids the separate publish-or-forfeit path. Signature and Merkle fixtures are built by
the existing runtime-test helpers; this corpus pins the amounts and transitions, not their bytes.

Ten pending fixtures preserve the unresolved alternatives without `expected` payouts:

| Family | Seeds | Decision owner |
| --- | --- | --- |
| HTLC redeem | `L=10000`, `A=6200`, `A=L`, `A>L`; fixed lock versus metered redemption/residual | [#1796](https://github.com/flop-labs/flop-core/issues/1796), from [yellowpaper#71](https://github.com/flop-labs/yellowpaper/issues/71) |
| Cooperative settle | `E=1000`, non-divisible `1001`, dust `1`; net full escrow versus gross audit carve | [#1905](https://github.com/flop-labs/flop-core/issues/1905), from [yellowpaper#79](https://github.com/flop-labs/yellowpaper/issues/79) |
| Rent ceil | `c=1,T=2,p/q=1/2,C_rent=1`; provider A serves one block, B replaces A for the second | [#1965](https://github.com/flop-labs/flop-core/issues/1965), from [yellowpaper#80](https://github.com/flop-labs/yellowpaper/issues/80) |
| Force dominance | delivered `G_n=10¹⁰`, `E=1000 FLOP`; mode/caller binding and priced tariff | [#1905](https://github.com/flop-labs/flop-core/issues/1905), rate owned by [#1610](https://github.com/flop-labs/flop-core/issues/1610) |
| DA-loss terminal | no prefix and a co-signed prefix; D-0430 full refund versus a superseding prefix rule | [#1948](https://github.com/flop-labs/flop-core/issues/1948) |

`pending` is neither a pass nor an expected test failure. Required gates stay green while reporting
pending coverage separately. In particular, rent release/replacement APIs in pending calls are
scenario placeholders: replacement entitlements cannot be inferred from repeated releases to the
same provider. D-0430 remains the baseline for DA loss; existing receipt-based runtime behavior
does not become policy by inclusion in this corpus.

To land a pending family, obtain its ratified D-id, pin the corresponding yellowpaper commit,
replace alternatives with exact post-state expectations, extend the schema and runtime adapter,
and run the named gate. The adapter rejects unconsumed landed calls/events; adding a fixture cannot
silently turn into a schema-only conformance pass. A public export can run
`uv run --script evidence/check-money-path-vectors.py` to validate the corpus structure; executable
amount conformance requires flop-core's pallet runner.
