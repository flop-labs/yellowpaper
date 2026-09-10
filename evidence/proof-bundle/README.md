# Formal evidence publication status

Status: **PENDING**

The frozen Lean statements and bounded Quint checks were reproduced in an isolated private release
bundle. Those results apply only under the hypotheses and modeled bounds in `CLAIMS.md`; they do not
establish deployed protocol refinement.

The public mirror exports this summary, the claim inventory, license inventory, and their hashes.
The Lean/Quint sources, toolchain locks, reproducer, deliberately broken mutant, and its diagnostic
trace remain in the private regression bundle while the FLOP software-license grant is unresolved.
The mutation check passed by detecting the presence-only mutant; `inv_repaired_sound` passed its
bounded seeded run. The mutant is not the proposed mechanism.

Public source/run evidence becomes eligible only after both of these gates pass:

1. The release owner attaches an explicit software license covering the FLOP Lean and Quint sources,
   then an empty-cache reviewer reproduces the exact manifest-hashed bundle.
2. A claim promoted beyond its stated mathematical/model scope has a passing refinement witness:
   certificate admission and committee premises for consensus; mechanism-specific tail domination
   and seed assumptions for sampling; evidence authenticity and runtime composition for TEE/TOPLOC;
   or runtime classification, payout, and bond-release correspondence for settlement.

Until then, implementation refinement and the runnable public source bundle remain pending.
