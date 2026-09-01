# Mandatory dual audit and adversarial pass

## PHYS-MATH — `PASS_SCOPED`

- Signature, orientation, explicit-c and frame ownership match the imported SSOT.
- `aB` is not physical acceleration; `OmegaTriad` is not vorticity; local boost is output-only.
- Time/ray-rate adapters are exact inverses for `c>0`.
- Wolfram gives `J^gamma_123=2 n^(gamma beta) a_beta`; the declared `n.a=0` is therefore the Jacobi condition.
- Koszul coefficients are metric compatible and reconstruct the torsion-free commutator.
- The exceptional witness obeys both displayed `VI_-1/9` constraints while preserving nonzero `Sigma13` and `Sigma23`.

Withheld: curvature, Einstein equations, constraint propagation and background evolution.

## PHYS-MATH-CODE — `PASS_DESIGN_PACKAGE`

- Every checked identity has a headless `.wl` owner.
- xAct is installed into a fresh path and hash-gated on every replay.
- All branches use one structure/connection generator; no branch-specific connection RHS is copied.
- The committed JSON is an observation; `run_stage.wl` regenerates its own receipt.
- No production Rust/Python physics path changes.

## Risks

- P0: none in the scoped witness package.
- P1: spatial curvature and Einstein/constraint systems remain unproved.
- P1: five witnesses do not establish the complete eleven-label classifier.
- P1: the evaluator is stateless, so exact xAct bootstrap remains mandatory.
- P2: selected mutations do not prove complete mutation coverage.
- P2: Rust/Python implementation parity is not yet attempted.

## Plot-driven CRAG

Declared witness residuals are all zero; invalid nearby mutations yield `1,6,1,1,3` for I, II, V, IX and `VI_-1/9`.

Surviving claim: a reusable convention and algebra-to-connection generator is symbolically verified for the five named witnesses.

Rejected stronger claim: complete background evolution or all-family solver support.
