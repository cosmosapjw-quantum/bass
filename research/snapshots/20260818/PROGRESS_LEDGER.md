# BASS complete progress ledger — 2026-08-18

This ledger is the durable, claim-scoped summary of the current formula-first Bianchi–Boltzmann research line and subsequent numerical/compiler research. `PASS` means the stated gate was independently reproduced in the active research environment; it does not promote later production stages unless explicitly stated.

## Formula / representation authority

### M0-A — explicit-c adapter — PASS
- `h_ij = a_V^2 tilde h_ij`, `a_V=(det h/det tilde h)^(1/6)`.
- `(1/c)d/dt=(1/a_V)d/dη`, `H_L=H_t/c`, `sigma_L=sigma_t/c`.
- `a_B,n_B,chi_e` retain physical `L^-1` units.

### M0-B1 — scalar PSTF ↔ harmonics — PASS
- `β_l=l!/(2l-1)!!`, `Δ_l=4πβ_l/(2l+1)`.
- exact scalar PSTF ↔ complex `Y_lm` normalization fixed.
- observed sky `n_hat=-e` gives the once-only `(-1)^l` parity map.

### M0-B2 — polarization / project-spin — PASS
- screen convention, `Q±iU`, E/B inversion, reflection parity and project-spin adapter fixed.
- `ProjectSpinY[s]=StandardSpinY[-s]`.
- Thomson l=2 I/E tensor matrix has eigenvalues `-1,-3/10`; slow mode `I-6E`.
- `V=0` is an invariant baseline.

### M0-B3 — real tesseral / Wigner registry — PASS
- real tesseral packing and Wigner registry sealed.
- rank selection and E/B parity/mixing rules checked.

### M0-C — spectral → bolometric → stress energy — PASS
- logarithmic-energy derivative integration rule sealed.
- spectral radiance absorbs the `ε^3` factor; bolometric mapping applied once only.
- `ρ_γ, q_a, π_ab` adapters fixed; only I contributes to `T_ab`.

## Bianchi-I clean-room authority

### BI-S1 — scalar spectral transport — PASS
- exact Bianchi-I ray energy and direction flow.
- all-rank scalar shear PSTF hierarchy derived.
- bolometric limit reproduces the corrected low-rank shear coefficient.

### BI-P1 — polarized spectral transport — PASS
- screen/dyad transport and spin-2 shear reduction derived.
- E/B sign structure fixed.

### BI-T1 — Thomson collision — PASS
- cold non-tilted electron-rest collision operator sealed for I/E/B/V.

### BI-F1 — Bianchi-I formula authority — PASS
- candidate semantic diff clean.

## Generic homogeneous Bianchi geometry/background

### M1-A1 — structure/Jacobi/covariance — PASS
- Jacobi iff `n^{ab}a_b=0`; class-A/B split sealed.
- O(3) covariance and n pseudotensor behavior fixed.

### M1-A2 — spatial connection/curvature — PASS
- exact connection and 3-Ricci/Ricci-STF formulas derived.

### M1-A3 — 11-branch curvature atlas — PASS
- all 11 public Bianchi types sealed.
- Type III remains public III with VI_h(h=-1) adapter only internally.
- exceptional VI_-1/9 retained as dynamical supplement, not a 12th algebra type.

### M1-A4 — curvature/Liouville audit — PASS
- legacy separate Ricci-STF photon term refuted for exact homogeneous Liouville.
- transport is first order in connection/structure data.

### M2-A1 — Einstein/matter closure — PASS
- Hamiltonian, momentum, Raychaudhuri and shear evolution closure sealed.

### M2-A2 — 11-branch background dynamical atlas — PASS
- class-B aligned gauge and exceptional constraints preserved.

## Generic rays / Liouville / hierarchy

### M3-A1 — null ray + screen — PASS
- `d ln ε/dλ=-H-σee`.
- exact `V(e)` and screen rate derived.

### M3M4-SA-002 — screen commutator sign repair — PASS
- distribution commutator uses `omega_dist=-omega_dyad`.

### M4-A1 — polarized distribution Liouville — superseded by sign repair
- original sign superseded; repaired continuum theorem retained.

### M5-A1 — generic scalar all-rank PSTF — PASS
- exact shear/A/N/Ω structure and rank shifts sealed.
- no independent Ricci-STF photon term.

### M5-A2 — generic polarized all-rank PSTF — PASS
- screen-complete N0/NJ operators sealed.
- polarized trace-screen term retained.

### M6-A1 — all-m Wigner / tesseral crosswalk — PASS
- Wigner ordering and selection rules sealed.

### M7-A1 — cold Thomson all-m binding — PASS
- state lmax=8 reference: I81/E77/B77/V81 = 316 states.
- collision spectrum and slow I/E mode sealed.

### M8-A1 — finite electron tilt continuum pullback — PASS
- exact finite Doppler/aberration/screen map.
- bolometric `D^4` boost; angular Jacobian `D^-2`.
- collision shape is `B_-v T_rest B_v`; collision *rate* must remain explicit and direction dependent.
- finite boost is not finite-bandlimit preserving.

### M9-A1 — characteristic + observed sky LoS authority — PASS
- exact characteristic/Duhamel representation.
- electron tilt, FLRW representation pullback and observed-sky endpoint map kept distinct.
- sky parity map fixed for I/E/B/V and P±.

### M10-A1 — numerical discretization design — PASS DESIGN / IMPLEMENTATION NOT STARTED
- primary coherency/distribution state, log-energy grid, collocation and uniformization design.
- later research amended two assumptions: degree-4 quadrature is only a low-rank Thomson gate; Strang is not stiff-uniform by default.

## Solver research and legacy source audit

### G-SOURCE — PASS
- actual legacy/experimental Python + Rust source became available and was audited.

### G-BOOST — P0 FAIL in legacy finite-v moving collision
- legacy Python/Rust/polarized moving wrappers Lorentz-remap state/screen but pass one scalar collision-clock increment to all outgoing directions.
- missing relative-flux rate is first order in electron velocity.
- exact-v vs O(v) legacy tests were common-mode blind because both paths shared the omission.

### G-BOOST-REF — PASS independent scalar reference
- normal-frame gold generator constructed independently.
- legacy/gold error is `O(v Δτ)`, survives independent quadratures, vanishes at v=0.

### G-BOOST-POL-REF — PASS independent polarized reference
- rest polarized Thomson spectrum and closed-form exponential independently reproduced.
- screen boost and V=0 survive; finite-v legacy rate semantics fail in the polarized lane too.

### G-COLLISION-ARCH — PASS frozen collision action
- uniformization, Al-Mohy–Higham exponential action and restarted Krylov all reproduce dense `exp(hC)` to ~1e-13 on reference systems.
- restarted Krylov is the leading conditional matrix-free candidate; uniformization retained as positivity auditor.

### G-STIFF — FAIL current C–A–C Strang
- uses an actual BASS Bianchi-I transport restriction, not a random matrix.
- fixed finite q: classical second order survives.
- strong collision: exact q→∞ projection proves global first-order reduction.
- collision substep accuracy is not the root cause.

### G-AP-ARCH — PASS frozen-coefficient AEM2
- damped exponential midpoint (AEM2) developed.
- generic noncommuting second-order condition and frozen q→∞ projected midpoint limit verified.
- scalar/polarized frozen lanes remain ~second order through extreme stiffness.

### G-AP-TIMEDEP — FAIL midpoint-frozen AEM2 for moving equilibrium
- actual tilted Type-II background + actual Saha/RateSchedule used.
- collision equilibrium projector P(t) moves with electron tilt.
- midpoint freezing leaves an O(h) endpoint-manifold defect.

## Dynamical-manifold research

### G-DYN-MANIFOLD-II — PASS quantitative Type-II lane
- current gamma=1.3 tilted Type-II trajectory lies on an exact aligned 5-state invariant slice.
- late `v2` and `Sigma13` decay with the physical Collins–Stewart tilt eigenvalue `3(7γ-10)/8 = -0.3375`.
- P(t) motion is >99.97% one-dimensional by SVD.
- adiabaticity `epsilon_P = ||Pdot||/(ν λ_gap) < 0.0033` over the tested opacity window.
- cross-type atlas remains research guidance, not a production dispatch table.

## Symbolic-numeric compiler research

### G-SYMBOLIC-IR — PASS prototype
- language-neutral typed Continuum SymIR introduced.
- exact Type-II branch specialization mechanically reduces 11 source variables to 5 and matches source RHS/JAX Jacobian to roundoff.
- pointwise angular collision rate is a typed diagonal operator and cannot be silently scalarized.
- once-only endpoint/bolometric maps represented as compile-time tokens.
- continuum IR and discretization IR must remain separate: a fixed normal grid can violate a continuum boosted-equilibrium null while a paired rest-native grid preserves it.

### G-SYMBOLIC-MOVING-MANIFOLD-II — PASS reference architecture
- continuum scalar equilibrium projector `P(v2)` generated from exact finite boost.
- `Pdot=(∂P/∂v2) v2'` generated from the exact 5-state Type-II RHS.
- Kato connection `K=[Pdot,P]` generated and checked against the discrete spectral bundle.
- reduced strong-collision slow generator is `K + P A P`.
- Kato/co-moving AEM2 restores ~second-order stiff convergence in scalar and polarized Type-II lanes where midpoint-frozen AEM2 showed order reduction.
- dense eigensolves/matrix exponentials remain reference-only; production lowering is not done.

## Toolchain/compiler architecture decision

### Rust backend — READY FOR LOWERING WORK
- new lockfile-exact offline vendor bundle verified by hash/CRC.
- uploaded durable log reports Rust/Cargo 1.94.1 `cargo metadata/tree/test --locked --offline` all PASS with 122/122 Rust unit tests.
- sandbox independently reproduced offline metadata/tree resolution; full cold rebuild exceeded the current execution window.

### Wolfram/xAct + Python/SymPy vs Julia/ModelingToolkit
- no Julia/ModelingToolkit core dependency is planned.
- required MTK-style structural compiler features will be implemented in a BASS-owned neutral compiler layer using Wolfram/xAct for mathematical/tensor authority and Python/SymPy for graph transforms, CSE, Jacobian/JVP/sparsity and Rust lowering.
- target parity: component/equation graph, dependency/stage extraction, exact alias/specialization, matching/SCC/BLT/tearing, residual/mass-matrix DAE form, owned index-reduction/init pass, analytic Jacobian/sparsity, content-addressed compile cache, generated Rust kernels.
- Wolfram `NDSolve` high-index DAE/index reduction is an oracle/reference, not an internal private compiler API dependency.
- Wolfram C codegen is explicitly outside the core path; it is treated like installing a second backend/toolchain and requires separate approval.

## Current DAG

Primary path:
1. WSC-0 Wolfram 15 capability seal.
2. WSC-1 neutral SymIR v1.
3. WSC-2 structural compiler passes.
4. WSC-3 DAE/index/init parity.
5. WSC-4 Jacobian/sparsity/JVP parity.
6. G-SYMBOLIC-LOWERING-II.
7. generated matrix-free Rust Type-II Kato kernel.
8. isolated production branch only after generated-vs-reference gates pass.

Parallel research:
- G-DYN-MANIFOLD-CROSS: VI0 -> VII0 -> VIII -> class B -> IX/exceptional.

After both converge:
- cross-branch SymIR/dispatch,
- G-CONSERVATION and G-QUAD long-run gates,
- only then optimization/performance work.

**Production migration status: BLOCKED.**
