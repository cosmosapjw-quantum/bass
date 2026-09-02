# PHYS-MATH-CODE audit — SYNC-MAP-01C

## Verdict

`PASS_WITH_PUBLICATION_AND_RUNTIME_LIMITS`

## Source and ancestry

The branch is a direct child of canonical BASS PR #83. W2/W3 sources are
traceable to PR #82 tested donor commit
`5d3e8ecce2a40a1bc2b43af7daa985e042d9815f`. Formula-composition bytes were
committed at `fd022fdb43ac73ae8977494f7b61959f4ea600ac`; later commits extend only
source-packet publication and documentation.

## TDD and execution

The exact RED commit omitted W2 and curvature sources and failed as intended.
The GREEN composition passed its six Python contract tests. The first source
packet was rejected as insufficient for independent replay because it omitted
parent Authority/IR/Bianchi files. The workflow was repaired without changing
physics source and emitted a complete 34-file packet.

Fresh connected-Wolfram replay of that exact packet produced:

```text
158 succeeded
0 failed
0 not evaluated
```

The replay used Wolfram 15.0.1, xTensor 1.3.0 and xCoba 0.8.6 from the pinned
xAct archive. The source artifact SHA-256 is
`b1f60fb518300e99c1321f3da0840a69d5478ecdbdb1d7602a6b77259d5b2fc1`.

## Software-contract checks

- Loader order is connection before curvature before xCoba witness.
- Curvature calls `LeviCivitaConnection` through
  `ConnectionToLockedGammaOrder`.
- A source-level guard rejects an embedded second Koszul implementation.
- Parent and donor commits are literals in the composition test.
- Public JSON schemas parse.
- Dimension-registry schema 1.1.0 is tested.
- Branch head and pull-request synthetic merge have the same tree while their
  commit identities are recorded separately.

## Backup and residual limits

The Dropbox stage is append-only. It copies exact parent and donor backup trees
and adds composition-specific overlay, manifest, replay receipt and restore
map. It is not a Git identity or automatic reverse-sync source.

GitHub-hosted CI cannot execute licensed Wolfram; the exact Wolfram replay used
the GitHub source artifact in the connected Wolfram evaluator. All-type
curvature, Einstein–matter evolution and Rust/Python production parity remain
unimplemented.

No P0 or P1 software-contract defect remains within this bounded composition
scope.
