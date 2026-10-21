# Compact33 implementation and finite verification

`vendor/rec_hheli` contains all 57 immutable donor Git blobs. The original
full62 implementation is imported unchanged as the oracle. `code/compact_system.py`
constructs the fixed lift/restriction, checks eligibility, and projects its
RHS/Jacobian. `code/compact_run.py` integrates 33 coordinates with the original
BDF controls and reconstructs the full62 arrays before running the inherited
diagnostics and scientific gate expressions. The gate expression has exact
AST identity with its donor. Both Frobenius and half-contraction observables
are explicit named arrays in the output.

`code/run_pilot.py` reuses the donor resumable runner with adapted dependency
paths and compact module. It caps this sandbox at four workers and retains
the observed larger-host cap of 63. `data/CAMPAIGN.json` preserves the 125
donor rows and appends the two prescribed zero-shear cancellation cases.
All cases explicitly use x_end=ln(7), 193 samples, and frozen tolerances.

Finite verification passed at the initial state and two positive synthetic
states. No trajectory integration has been run in Stage 1. Exact observed
errors, deterministic directions, source identities, rejection guards and
resource measurements are in `evidence/COMPACT_FINITE_VERIFICATION.json`,
`GATES_EQUIVALENCE.json`, `RUNNER_PLAN.json`, and `STAGE1_RECEIPT.json`.
The original H1/D initial fraction reconstruction residual of
2.710505431213761e-20 is retained and recorded; the compact initial state is
exactly the restriction of the unchanged donor initial vector.

The physical scope and admission authority remain those in
`FROZEN_CONTRACT.md`. Stage 2 starts only after the root finite-check gate.
