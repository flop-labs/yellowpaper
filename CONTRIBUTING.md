# Contributing

**Issues are the current contribution channel. Pull requests are not currently open for general
contribution.**

This repository is a generated mirror: `yellowpaper.md` is built from FLOP's engineering repository,
where the spec is gated against parameter drift (Appendix A is generated from the canonical
parameter YAML) and citation drift. Changes cannot be merged directly into this mirror without being
overwritten by the next publish. A maintainer instead carries accepted corrections into the upstream
source of truth and republishes them here.

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

Pull requests are not currently open for general contribution, including typos, grammar, broken
links, malformed tables, and rendering fixes.

To submit one of these small mechanical corrections, open an **Erratum** issue and paste the exact
change into the issue body as a fenced diff:

```diff
-text with the typo
+corrected text
```

For anything that changes a requirement, parameter, bound, or argument, use the matching issue
template and describe the consequence. A maintainer will handle accepted changes upstream, where the
decision record and drift gates are available.

## Security

Do not open an issue for a vulnerability. See [`SECURITY.md`](SECURITY.md).

## Attribution and license

Contributions to the text are accepted under [CC BY 4.0](LICENSE). An accepted report keeps its credit
in its issue, where the resolution is recorded.
