# Committee sampler evidence

Status: prepublication negative evidence for E.42; no minimum-size or bootstrap policy is ratified
here.

Protocol scope: [yellowpaper §2.3](../yellowpaper.md#23-safety--the-three-sub-proofs), E.42.

The deployed sampler draws distinct eligible identities sequentially using stake-weighted intervals;
the ideal proportional-draw model and concrete PRNG caveats are separated below. Aggregate attacker stake alone does not determine its
seat-count distribution. The reproducible counterexample has 40 attacker identities at 100,000
stake each and 61 honest identities at 300,000 each. Every identity meets the 100,000 eligibility
floor and has recent verified work. Drawing 100 of the 101 identities omits exactly one identity, so
the committee always contains 39 or 40 attacker seats. The attacker owns 40/223 (about 17.94%) of
stake, yet the probability of violating AlephBFT's strict `3f < n` premise is exactly one: failure
begins at 34 attacker seats for `n = 100`.

`scripts/research/yellowpaper_sampler_evidence.py` enumerates the exact joint distribution of the
remaining group counts after each probability-proportional-to-remaining-weight draw. Its committed
JSON output records rational probabilities, population, voting unit, threshold, and scope. This is
an exact result for homogeneous identity groups with the stated inputs. It does not establish PRNG
uniformity, the concrete seed-to-draw mapping, seed unbiasability, cross-epoch independence, or a
universal tail inequality. In deployed code, SplitMix64 expands the seed, two 64-bit outputs form a
128-bit value, and modulo maps it into the remaining aggregate-stake interval. That mapping has
modulo bias unless the interval divides `2^128`. The ideal proportional model also assumes the
aggregate `u128` stake sum does not overflow; interval addition and removal subtraction saturate.
Those implementation details need a separate quantitative bridge before an ideal-model tail can be
claimed for seed-induced deployed outcomes.

The runtime derives a rotation seed by hashing the current `Babe::randomness()` with a domain tag
and block number. The randomness is fixed within the epoch and is all-zero during early bootstrap;
the block number separates rotations but adds no entropy. A source-code link establishes wiring,
not resistance to BABE contribution withholding, grinding among eligible VRF outputs, or repeated
attempts across epochs. A defensible capture statement therefore still needs a ratified adversary
model and exposure horizon.

The implementation also returns every eligible identity when the pool has at most 100 members. If
no identity has recent verified work, it retries after dropping only the recency condition. These
are live liveness behaviors, not a ratified safety bridge. Any publication claim must state the
realized committee size and use its own strict threshold `3f < n`; a bound for `n = 100` cannot be
reused for an undersized pool. Policy work remains: define identity and delegation control,
eligibility cost, minimum safe pool size, zero-work bootstrap constraints, seed influence, and the
number of exposed rotations. Until those are ratified and analyzed, E.42 remains open.

## Reproduce

From the published bundle root (the reproducer uses only the Python standard library):

```sh
python3 evidence/reproduce-sampler.py \
  --check evidence/yellowpaper-sampler-evidence.json
```

Repository tests additionally run:

```sh
uv run pytest scripts/python/tests/test_yellowpaper_sampler_evidence.py -q
```

The first command checks the evidence file byte-for-byte against the exact enumerator.

The isolated `hp-consensus` Rust suite passed all 14 tests, including the concrete sampler
counterexample. A validator-entrypoint regression is also written, but its execution is blocked
by the existing Substrate dependency mismatch in the validator test harness. It is not a passing
conformance result. Seed influence, concrete PRNG distribution, and bootstrap policy remain open
independently of that build failure.
