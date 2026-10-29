# CE1-J hostile R6/C9: default-runner boundary clarification

The original reported witness remains an **exact MPFR source-premise contradiction for the directly callable certification API**, plus a strong numerical endpoint falsifier. It is **not** proof that the standard `run_local_tabulated_rk4` factory will emit the same invalid certificate.

Current-turn control: For the isotropic single-cell `E0=.9` plus appended positive stored ray `(1,0,0)` with mass 1, calling `run_local_tabulated_rk4(source,steps=4,end=.08,shear=(0,0,0),backend='python_oracle')` raises `ValueError("Constraint-admissible expanding initial geometry with a_i=1 required")` via its `rk4_path` preflight. In contrast `certify_local_tabulated_path(source, independently reconstructed HermitePath,` same original physical initial state) returns a falsely small certificate, because the direct certificate path only checks the original source initial state and misses cell/ray shape/cardinality.

**Refined impact:** `P0` for soundness of directly callable source/time certifier on unchecked re-bound topology; `P1` / current merge gate for enforcing this contract. The standard RK4 runner's Hamiltonian preflight provides a separate guard in the demonstrated witness. The immutable physical 1536-ray result is not refuted. A simple shape check at `_stored_data` closes this specific API failure and does not change physical equations or tolerances.

No original PR #246 or production source was changed. This addendum is the current-use qualification over any broader language in the initial report.
