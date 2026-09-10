# Contributing

**Issues are the contribution channel. Pull requests are for typos.**

That asymmetry is worth stating plainly before you spend time on a patch. This repository is a
generated mirror: `yellowpaper.md` is built from FLOP's engineering repository, where the spec is
gated against parameter drift (Appendix A is generated from the canonical parameter YAML) and
citation drift. A substantive change here cannot carry the decision record, the regenerated
parameter table, or the gate run that a spec change requires — so it cannot be merged as written,
however correct it is.

## Open an issue

Pick the template that fits ([new issue](../../issues/new/choose)):

| Template | Use it for |
|---|---|
| **Erratum** | A typo, broken formula, wrong cross-reference, or internal inconsistency. |
| **Ambiguity** | A requirement that admits two implementations. The highest-value class of report. |
| **Challenge** | A disputed claim, bound, proof sketch, or incentive argument. |
| **Question** | Understanding, not a defect. |

Two things make a report actionable:

1. **Cite version and section** — *v0.5 §3.4*, or a requirement ID. The templates ask for this.
   Feedback that says "the slashing section" ages badly across releases.
2. **State the consequence** — for an ambiguity, the two implementations that both satisfy the text;
   for a challenge, the assumption you think fails and what it costs the protocol if it does.

Appendix E already tracks the open items we know about. Checking it first avoids re-filing a known
gap — though "E.22's placeholder does not work because…" is very much worth filing.

## Pull requests

**Accepted:** typos, grammar, broken links, malformed tables, rendering fixes. Small, mechanical,
no change in meaning.

**Not accepted here:** anything that changes a requirement, a parameter, a bound, or an
argument — including changes that are clearly right. These are closed with a pointer back to the
issue templates, and the substance is then handled upstream where the decision record and the drift
gates live. This is not a judgment on the patch; it is where the merge is possible.

A workflow closes substantive PRs automatically. It is not a bot brushing you off — the explanation
above is the whole of it.

## Security

Do not open an issue for a vulnerability. See [`SECURITY.md`](SECURITY.md).

## Attribution and license

Contributions to the text are accepted under [CC BY 4.0](LICENSE). Accepted reports are credited in
[`CHANGELOG.md`](CHANGELOG.md) by GitHub handle unless you ask otherwise.
