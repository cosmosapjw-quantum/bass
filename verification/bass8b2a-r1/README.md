# BASS-8B.2A-R1 exact E1–E4 host replay

This verification-only branch reconstructs the hash-pinned BASS-8B.2A typed
electron-state candidate, restores the exact preserved E4 host archive, and
runs the candidate plus E1–E4 predecessor gates without modifying the four
owner modules.

## Frozen inputs

- branch parent: `e4c9308af11e3234a344aeab487188a5550b1a3c`
- candidate package SHA-256:
  `caf3113fe56204652cb844f51cbce90a48e1c00cb1ffa4ff98ae80bd4a670d36`
- E4 archive SHA-256:
  `d7590182b52d7bb30f537232993f2bb954a049d530138b0325474633926ec766`

The workflow reconstructs every candidate input from content-addressed payload
files, checks its original SHA-256, restores E4 with the existing repository
script, runs the exact-host replay, checks owner hashes before and after, and
uploads an evidence artifact even on failure.

## Claim boundary

This is not an authority-row promotion, VI0 classifier, solver/runtime wiring,
production migration, merge candidate, or scientific PR. A PASS only closes
the BASS-8B.2A-R1 host-replay prerequisite; rows 7–8 and Join J1 remain blocked
until the later finite-carrier/projector/paired-left authority is adjudicated.
