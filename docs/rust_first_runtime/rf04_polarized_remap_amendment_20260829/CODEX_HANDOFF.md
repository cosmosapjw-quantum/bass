# Codex Handoff — RF-04 Polarized Remap Amendment A2

Use the immutable package commit/tree from `PUBLICATION_RECEIPT.json`, not the
live branch tip.

After fetching the repository:

1. materialize the ZIP and sidecar from the exact package commit;
2. verify archive SHA-256;
3. unpack into a new temporary directory;
4. run its `MANIFEST.sha256` and `validate_package.py --live --repo <clone>`;
5. verify the retained local branch/worktree/blocker:
   - branch `agent/architecture/rust-first-rf04-20260828-r1`
   - HEAD `4508cb3af776d2a058d71bbe8b95f9bfe62b35ed`
   - tree `586c4a1858d99ab9217750687489a133bf0e2051`
   - blocker SHA-256 `60f108dcb8a80307915b5af0ceef81371768ca7811dd2b96be55254ac448b014`
6. resume the same worktree at `RF04-GREEN-02`.

Do not reset, clean, stash, rebase, amend, branch-switch, force-push, recreate
the branch, rerun intake, or rerun the existing genuine RED.

The implementation is frozen to:

- native GL-theta / uniform-even-phi grid from `n_theta,n_phi`;
- `k_theta=6`, `k_phi=6`;
- reverse midpoint-RK2 characteristics and forward tensor RK2, two substeps;
- remap only `Jhat - Pi(e)/2`, componentwise, with internally generated weights;
- restore `Pi(e)/2`, screen-project, and trace-normalize;
- Liouville direction/tensor-rate RK4 full step;
- exact rank-9 collision half-steps;
- fixed Strang order from the schema;
- fixed Eulerian qhat-grid history; backtraced directions/stencils are transient;
- no standalone Kato stage.

If a new Kato operator, interpolation family, grid, tolerance, adaptive
substeps, or raw caller stencil weights are required, stop with the typed
source-contract blocker; do not invent them.

Then continue targeted proof, four diagnostic readbacks and hostile mutations,
one PHYS-MATH and one PHYS-MATH-CODE audit, at most one reproduced P0/P1
repair, native delta/restore if invalidated, ordinary push, one stacked draft
RF-04 PR against `agent/architecture/rust-first-rf03-20260828-r2`, exact
remote readback, and stop.

Candidate B/BASS-13–15, timing, GPU, Wolfram, full suite, RF-05+, merge, ready,
new formulas/EOS/tilted-temperature laws, and scientific/performance promotion
remain forbidden.
