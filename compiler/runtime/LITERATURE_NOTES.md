# Exponential/phi-action literature notes

- Al-Mohy & Higham (SIAM J. Sci. Comput. 33, 2011): matrix-exponential action
  and augmented-matrix representation of combinations of phi-functions.
- Niesen & Wright, Algorithm 919 / `phipm`: adaptive Krylov evaluation of
  phi-functions for exponential integrators.
- KIOPS (JCP 2018): adaptive Krylov/incomplete-orthogonalization method for
  exponential-integrator phi combinations.

The current PR intentionally uses a full-dimensional reference Arnoldi path and
fails closed for truncated bases. These papers motivate the next adaptive
backend gate rather than being claimed as already implemented.
