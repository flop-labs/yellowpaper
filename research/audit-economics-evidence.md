# Conditional audit economics and shared collateral

> Status: `[RESEARCH]` · 2026-09-05 · deterministic sensitivity analysis. The probabilities below are inputs, not observations.

Protocol scope: [yellowpaper §3.5](../yellowpaper.md#35-tier-3--independent-optimistic-re-execution--slashing), E.45/E.22.

This note closes the arithmetic and implementation-trace portion of issue #1495. Run:

```sh
UV_CACHE_DIR=/tmp/flop-yellowpaper-uv UV_NO_PROJECT=1 uv run --script scripts/research/yellowpaper_audit_evidence.py --check --verify-sources
UV_CACHE_DIR=/tmp/flop-yellowpaper-uv UV_NO_PROJECT=1 uv run pytest -q scripts/python/tests/test_yellowpaper_audit_evidence.py
```

The generated [JSON](../evidence/yellowpaper-audit-evidence.json) contains exact rational results,
scoped source-span hashes, and line references. The [CSV](../evidence/yellowpaper-audit-evidence.csv) is the
concurrent-exposure sweep. `--verify-sources` verifies named source fragments and scoped hashes. An
exported copy beside the JSON/CSV reproduces arithmetic with `--check` without private sources.

## Claim supported by this evidence

For a risk-neutral coalition, a sufficient condition under the stated model is

`incremental attack gain - bribes < P(any collectible verdict) × (discounted collectible collateral + lost future revenue)`.

Incremental attack gain is the fraud payoff above the honest baseline: avoided compute/publication costs,
fraud-only settlement revenue, and coalition external benefit. If a leg would also be earned honestly it is
excluded. Where classification is uncertain, the sensitivity input is a conservative upper bound on total
incremental attack gain, preventing revenue from being counted twice.

All profitable channels and epochs sharing a bond belong on the left. The right contains the bond once,
not once per channel. This is a falsifiable conditional bound, not a unique equilibrium or a measurement.
Risk aversion can strengthen deterrence and risk seeking can weaken it; neither is inferred here.

For one opportunity the full chain is

`P(S) P(D|S) P(C|S,D) P(I|S,D,C) P(U|S,D,C,I) P(K|S,D,C,I,U)`.

Here `S` is selection, `D` data availability, `C` a challenge, `I` timely finalized inclusion, `U` an
upheld verdict, and `K` collection. Conditional notation avoids an independence claim. The prior 5% and
2.3085% rows reproduce exactly as `1/20` and `4617/200000`; both remain illustrative. Any zero gate makes
effective collection zero. With positive fraud value, the no-data, no-challenger, and no-inclusion
boundaries cannot satisfy this sufficient condition regardless of nominal stake. That does not rule out
deterrence through other sanctions or losses outside the modeled collection event.

For repeated opportunities, the JSON sweeps two disclosed endpoints: independent detection has
`1-(1-p)^n`, while a fully correlated common failure has probability `p`; `rho` linearly interpolates
between them only as a sensitivity device. It is not an estimated copula or empirical correlation.
Delayed recovery is represented by a discount multiplier on collectible collateral. Lower recovery value
strictly weakens the bound.

## Challenger utility

A challenger acts only if its private expected utility is non-negative:

`expected reward + expected private recovery - data cost - verification cost - transaction cost - censorship/bribe cost - delay cost - false-loss probability × bond ≥ 0`.

Expected reward and recovery are outcome-weighted values conditional on the challenger information set;
they are not nominal amounts assumed certain.

The runtime sets a 100 FLOP challenger bond (`pallets/runtime/zkverify/src/lib.rs`). A valid miner response
or abandoned bisection transfers that bond to the miner; an upheld/defaulted fraud returns it. The traced
channel path pays no separate challenger bounty. Agent and active-validator standing limits who can open
the dispute. Therefore challenge probability cannot be replaced by selection probability without a
funded utility argument, particularly for a validator whose private recovery is zero.

Miner revenue at risk includes the disputed settlement, avoided inference/data-publication cost, future
channel profit lost through permanent blacklisting, and any coalition external benefit. Honest block,
PoUI, availability, or other rewards matter through future-revenue loss if blacklisting or stake loss
actually removes them. The model exposes that input and does not invent a value.

## Actual collateral path

`compute-channel::open_channel` checks `check_reservation_cap(&agent, escrow)`: this caps the **agent's**
active reservations and transfers the agent's escrow. It does not reserve miner stake against the channel's
maximum profitable exposure. Fraud resolution calls `T::Slasher::slash_fraud(miner, channel_id)`.
The runtime adapter invokes the proof-forgery path, which applies a 100% slash and blacklist. Self,
delegated, sponsored, and unbonding sponsored positions participate in that slash waterfall.

The miner-staking busy count blocks native and sponsored unbond initiation while sessions or disputes are
open, and sponsored principal already unbonding remains slashable. This closes a simple live-session exit
race. It does not establish `sum(channel exposure) ≤ miner collectible collateral`. Multiple simultaneous
frauds can reuse one bond economically. After the first full slash, the adapter explicitly maps
`NotSlashable` to a zero additional slash so later victim escrows can close. The generated unit-bond
penalty waterfall preserves this negative result: penalty demands `[1,1,1]` collect slash/burn amounts
`[1,0,0]` from the shared bond. Collection routes through the slash-proceeds path; it does not imply that
victims receive those amounts.

Forward/CRU positions have a separate bond escrow path. This evidence does not treat that mechanism as an
aggregate reservation for ordinary compute channels or silently combine collateral with incompatible
claim priority.

## Publication boundary and remaining evidence

The defensible public statement is conditional: the model certifies a negative expected fraud payoff
when net incremental gain is below the probability-weighted sum of discounted collectible collateral
and conditional future-revenue loss. The exported shared-collateral sweep sets bribes and future-revenue
loss to zero; its simpler exposure bound is scoped to that profile. The current implementation does not wire the aggregate
miner-side reservation invariant needed to claim this generally.

Publication still needs measured or conservatively justified values for DA through the challenge window,
eligible-challenger action, finalized inclusion during stalls, adjudication false negatives by attack
class, collection and recovery delay, future-revenue loss, and correlations. It also needs an integration
test opening simultaneous channels, initiating/pending unbond where allowed, resolving multiple frauds,
and recording per-victim recovery. A policy change such as a challenger bounty, claim priority, exposure
cap, or miner reservation requires separate ratification.

A runtime regression now exercises two active-session hook calls, delegated-stake unbond rejection,
and successive calls through the real channel slasher adapter. Its execution is blocked by the existing
Substrate dependency-version conflict. It does not open and resolve two actual channels, so even a
future passing result will not by itself complete the simultaneous-channel lifecycle evidence above.
