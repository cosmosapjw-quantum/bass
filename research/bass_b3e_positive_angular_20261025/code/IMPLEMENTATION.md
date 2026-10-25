# B3e implementation facts (preexecution)

The implementation is confined to the new lane. `positive_angular.py` implements
input validation, source-aware and stated baseline first-K selection, positive
GL product rays, mapped direct moments, and unchanged kinetic packet mapping.
`run_sweep.py` reads the exact copied B3d raw file, scales its stored N64 tensors
by exp(-0.4), and retains the original Q14/Q26 errors without recalculating them.
New references have an independent ring-by-ring GL construction. The sweep has
19 main endpoint rows, two canonical orientation checks with additional
co-rotated covariance comparisons, and one positive four-cohort mixture.
Mixture Loewner checks use sum(c beta M); signed tensors are summed directly.
Frame comparison uses positive reference energy for dimensional quantities,
with exact integer K equality and absolute dimensionless residuals.

The single custom test script contains seven named check groups: degree-eight
sphere monomials; H/M identities; isotropic G5; actual zero source directions;
cap refusal; invalid inputs/undefined mixture; and positive mixture identity.
The reported counts are produced by the actual script, rather than pytest
method inference. All scripts have undergone AST parsing only; scientific
execution remains NOT_RUN pending controller GO.

The metered wrapper adapts the prior B3d subprocess receipt logic. It enforces
one BLAS/OpenMP thread, 30-second wall/20-second CPU per child and cumulative
60-wall/40-CPU implementation allocation. It records the separate 120-wall/
60-CPU scientific guard, historical null remaining budget, budget_reset=false,
prior subtotals, source/input hashes, actual Python executable and packages,
UTC times, argv/cwd, CPU/wall and raw stdout/stderr. The scientific controller
combines any separately metered symbolic work into the whole-unit accounting.

Requested execution role is lower-tier coding executor; no runtime model
observation tool is exposed, so observed model is null. This document does not
claim that a requested role proves a runtime model identity.

No scientific Python import, numerical test/sweep/summary process, old campaign,
IVP, external write or parent source edit was performed during preparation.
