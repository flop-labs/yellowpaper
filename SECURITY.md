# Security Policy

**Do not open a public issue for a vulnerability.**

This repository holds a protocol specification, and the most valuable findings against it are
exactly the ones that must not be published first: a break in the verification tiers, an economic
attack that makes cheating profitable, a consensus safety or liveness violation, a way to extract
rewards without performing the work. Filing one of those as an issue publishes an exploit against a
network that people will run.

## How to report

1. **GitHub private vulnerability reporting** — [open a private
   advisory](../../security/advisories/new). Preferred: it keeps the report, the discussion, and the
   eventual disclosure in one place.
2. **Email** — `security@flop.finance`, if you would rather not use GitHub.

Please include the version and section, the assumption or requirement you believe fails, and a
concrete attack: who deviates, what it costs them, and what they gain. A worked adversary model is
worth more than a suspicion, and we would rather receive a rough one than nothing.

## What counts

Report privately:

- Consensus safety or liveness attacks (§2, §15) — equivocation, committee capture, finality stalls.
- Breaks in the verification architecture (§3) — forging attestations, defeating TOPLOC, evading
  sampled re-execution, TEE trust-domain assumptions that do not hold.
- Metering attacks (§4) — inflating effective FLOP, under-reporting work, evading the tripwire.
- Economic attacks (§7–§11) — profitable cheating, stake-floor or slashing-curve breaks, griefing
  with asymmetric cost, emission or vesting exploits.
- Session, escrow, dispute, and HTLC exploits (§6, §12) — theft, unfair settlement, refund races.
- Data-availability attacks (§5) — withholding without slashing, audit evasion.

Open a public **Challenge** issue instead for: disagreement with a design tradeoff, a bound you
think is loose, a modeling assumption you find unrealistic, or an incentive argument you find
unconvincing — where the finding is "this may not work well", not "this can be exploited". When it
is genuinely unclear which one you have, report privately and we will move it into the open together.

## What to expect

- **Acknowledgement within 3 business days.** If you do not hear back, please re-send — a missed
  report is our failure, not a rejection.
- **An assessment within 14 days**, saying whether we agree it is exploitable and what we intend to
  do about it.
- **Credit** in the advisory and in [`CHANGELOG.md`](CHANGELOG.md), unless you prefer to stay anonymous.
- **Coordinated disclosure.** We will agree a timeline with you rather than impose one.

## Scope and honesty about it

FLOP is **pre-mainnet**. There is no live network holding user funds, and **no bug bounty program at
this time** — we will not pretend otherwise to attract reports. What we can offer is a real
technical response, public credit, and a decision record showing what your finding changed.

Findings against the *specification* are in scope here. Findings against deployed devnet
infrastructure or client code should also come through the channels above; note which you mean.
