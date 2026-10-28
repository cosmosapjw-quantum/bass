# CE1-F: positive tabulated angular radiation

Scope: arbitrary nonnegative finite cell-energy table on the first-octant solid-angle coordinates mu in [0,1], phi/(pi/2) in [0,1], reflected into eight coordinate octants. Within each cell the continuum angular energy density is constant. The table is physical input; each cell energy includes all reflected copies. Refinement divides these exact energies and leaves this physical function unchanged.

Parent: BASS PR237, a05906527d7dd5e5f6a653a0e4f7d977679d4a0c. Source branch research/bass-ce1e-exponential-angular-certificate-20261029. Current child branch research/bass-ce1f-tabulated-angular-certificate-20261029. Original top-level DAG 9/15; CE-1 PARTIAL. Preserve its fifteen IDs and edges.

Conventions: metric (-,+,+,+), c,hbar,k_B retained in dimensional interpretation; u=t/Tstar, ell_i=ln(a_i), h_i=Tstar H_i, E,P=(8 pi G Tstar^2/c^2) times physical energy density/pressure. Lambda=0, homogeneous diagonal coordinate-reflection-even collisionless massless Bianchi I; all three directional expansions initially nonnegative. No angular harmonic closure or small-amplitude dynamical expansion.

Construct a positive numerical quadrature from the mean squared directions of each cell. Prove an MPFR-directed, uniform continuum-versus-stored-binary-source pressure error using a centered second-order Taylor estimate on the simplex x_i=q_i^2. Include stored mean/ray rounding and exact-real initial energy. Propagate that source discrepancy and initial Hamiltonian discrepancy with the inherited nonlinear Dini comparison. The certificate compares exact ODE solutions; time-integrator rounding and truncation require a separate certificate.

Completion: (1) constructive derivation and independent R6 review; (2) executable input/source/bound/geometry APIs; (3) independent cell quadrature, isotropic limit, same-input refinement, coupled-IVP and mutation checks; (4) plots read and audited; (5) C9 independent code review; (6) each R/C stage committed and pushed with snapshot hash; (7) final reproducible source, evidence and handoff archived. No parent/main merge or production admission.

Runtime current-turn probes: PYTHON_PASS (3.12.14, numpy/scipy/matplotlib), CPP_PASS (g++ compiled/executed). SymPy/pytest/mpmath initially PACKAGE_MISSING; installing task-local dependencies. MPFR6 scalar interval probe PASS. Rust compiler missing in this host; no Rust source changes in this unit.

Policy correction: parent handoff AUTO_NEXT=false is an operational default, superseded for this bounded next unit by the current explicit user request to execute the next theory/coding loops. Original no-merge and physical-scope limits remain effective. Earlier assistant R6/C9 NOT_RUN is historical; current host exposes independent agents and this unit uses them.
