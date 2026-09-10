# Licenses

- In the private release bundle, mathlib4, plausible, LeanSearchClient, importGraph, ProofWidgets4,
  aesop, quote4, and batteries are Apache-2.0. lean4-cli (`Cli` in the lock) is MIT. These identifiers
  were checked against each pinned checkout's root `LICENSE`; every exact revision and license path
  is recorded in the private bundle manifest.
- Quint 0.32.0 is Apache-2.0. The private `pnpm-lock.yaml` pins its complete npm closure by version
  and registry integrity; `QUINT-LICENSES.json` inventories all 79 locked package/version pairs. Their declared
  licenses are Apache-2.0, BSD-3-Clause, BlueOak-1.0.0, ISC, or MIT.
- The FLOP proof source files retain FLOP Labs copyright. The public release owner must attach an
  explicit software license before publication. The yellowpaper's CC-BY-4.0 text license does not by
  itself grant a software license for these Lean or Quint files.

This unresolved source-license grant is a publication blocker, not a proof failure.
The pending public profile therefore excludes proof/model source, locks, executables, and raw traces.
