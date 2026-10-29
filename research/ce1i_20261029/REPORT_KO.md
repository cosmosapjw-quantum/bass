# BASS CE1-I 연구 결과: 시간국소 압력 Jacobian 구간상계

2026-10-29 | Parent: CE1-H PR242 HEAD `99473c0e6ba8f9d7172cc3fb730f5ac32c7e4677` | Independent child: Draft PR245. Upper DAG 9/15, CE-1 PARTIAL. No automatic merge or production admission.

## 1. Physics/units, claim scope

Metric signature (-,+,+,+), Lambda=0, normal proper `u=t/Tstar`, `ell_i=ln a_i`, `h_i=Tstar H_i`, `E,P_i=(8 pi G Tstar^2/c^2)*physical energy density/pressure`. Massless collisionless diagonal Bianchi I, all-direction expanding, positive piecewise-constant physical angular cell energy in first octant with 8 reflections; no tilt, collisions, polarization, spatial Einstein constraints or stochastic CMB. Continuum energy table and stored ray/mass binaries remain distinct. Four recorded RK4 Hermite panels, u=0..0.08, fixed target `max_i |Delta h_i| < 1e-5`.

## 2. Constructive lemma and comparator

The exact positive measure obeys `ell_i'=h_i`, `h_i'=-theta h_i+P_i`, `theta=sum_i h_i`, `sum_i P_i=E`, and `partial_ell_j E=-E-P_j`. Since h_i>=0 and P_i>=0, `E'=-theta E-sum_i h_i P_i<=0`. Summation gives `theta'=-theta^2+E`. The exact Hamiltonian root with trace-free s_i gives `theta0^2=3E0+3sum_i(s_i^2)/2 >= E0`; comparison yields `theta(u)<=theta0` and `h_i(u)>=h_i0*exp(-theta0*u)`. Therefore

`ell_i(u) >= h_i0*(1-exp(-theta0*u))/theta0`.

For panel J_j=[u_j,u_(j+1)], combine the outward MPFR lower bound above evaluated at u_j with the stored binary Hermite cubic's MPFR Bernstein lower hull to certify a common `m_j>=0` for both paths. Every intermediate point on the straight segment from exact ell to Hermite ell is coordinatewise >=m_j. The positive-ray pressure Jacobian identity `partial_ell_j P_i=-(1+2 delta_ij)P_i+R_ij`, `R_ij>=0`, `sum_j R_ij=P_i` implies all derivatives <=0 and `sum_j|partial_ell_j P_i|=4P_i`. Exact diagonal homothety `P_i(ell+m*1)=exp(-4m)P_i(ell)` then gives

`L_j = 4 Pmax(0) exp(-4m_j) <= 4 Pmax(0) <= 4 Emax`.

The positive Dini error system on each J_j is `D+e_ell<=e_h+rho_ell`, `D+e_h<=L_j e_ell+eta_Q+rho_h`, with k_j=sqrt(L_j) and propagator `[[cosh(k_j dt),sinh(k_j dt)/k_j],[k_j sinh(k_j dt),cosh(k_j dt)]]`. Existing CE1-G exact-binary Hermite endpoint jumps are included at every knot. Emax stays unchanged in continuum geometry/source box. Only the homogeneous error comparison coefficient changes. All m_j are rounded down; all L_j and error envelopes are MPFR192-rounded up.

## 3. Source/code implementation reality

One opt-in module `bianchi/nonperturbative/einstein_tabulated_local.py`. It calls the existing CE1-G full-panel certificate **once**, obtains unpropagated eta and each MPFR defect/knot carrier, calls CE1-H's original-cell initial pressure moment and exact continuum Hamiltonian-root helpers, then repropagates separate initial/source/time+jump errors for CE1-H's constant coefficient and CE1-I's panel coefficients. It does NOT invert propagated error envelopes. It does NOT modify PR242 source/RK4/physical inputs/tolerance. It explicitly rejects stale inherited CE1-C stored-ray majorant on source rebinding and a Hermite cubic whose left coefficients disagree with the recorded knot (known sibling PR243/244 proof-premise defects; siblings remain unmerged).

## 4. Actual same-input numerical evidence

| refinement | rays | CE1-H total h upper | CE1-I total h upper | fixed 1e-5 |
|--:|--:|--:|--:|:--|
|1|6|7.054251335641931e-4|7.053499044958107e-4|NOT_MET|
|2|24|1.835319479813647e-4|1.835119088014217e-4|NOT_MET|
|4|96|4.6729280195691335e-5|4.672370785019027e-5|NOT_MET|
|8|384|1.227583245284329e-5|1.227390354784323e-5|NOT_MET|
|16|1536|3.675931156248731e-6|3.6749116877624083e-6|MET|

At ref16 the CE1-G original total `3.7019164499698285e-6` and CE1-H fresh total `3.675931156248731e-6` were both reproduced. CE1-I total is `3.6749116877624083e-6`, a **0.0277336120561%** decrease against CE1-H, not a throughput speedup. Contributions: initial `1.865856997285437e-16`, source `2.859081958916233e-6`, time+jumps `8.158297286595899e-7`. Time-local row coefficients are [1.3000000000000003, 1.257046869944473, 1.2168561190192664, 1.1792092149491518]. Full ref16 run 37.95 seconds on the current container; wall-time comparison against other machines/algorithms is not controlled and no performance speedup is claimed.

Ref16 source ray SHA256 `8f460f3440bed238c1901e546066552c6bf5deb14e0f0ef0360a5a027a89cda2`, source mass `5f4a578ca383cd0e1c72788344ecc28a6505b7542b9565a454d660fda8897293`, RK4 states `34c0ea11490e8e83620a137eec42882476c957614d165a2ec18c8129f48b0814`, Hermite coefficients `2ad873959c5d46b74046ec2aa94d713babcc8f7ea5864adc5054ca784203fb5f`. These match the relevant CE1-H frozen identities. JSON with complete panel evidence accompanies this report.

### Actual software/CI

Runtime PYTHON_PASS (CPython 3.13.5), CPP_PASS, native subagent NOT_RUN (no spawn tool). Inherited CE1-H original ZIP SHA256 `e4ed87dfe9fe99f9e9ce061c95cebc65b97f7884690517cb5b5a646f8f7a12d2`, 83 members, CRC PASS. Baseline 81 scoped tests PASS. New 8 + inherited 81 = **89 targeted tests PASS** locally. GitHub CI `40824526528` SUCCESS with **89 passed in 24.93s** and actual installed-wheel `CE1I_INSTALLED_WHEEL_SCOPED_PASS`. RF-BENCH-00 separate failure; RF-00 full policy acceptance not claimed. No formal MPFR/Python proof, native Rust, whole-repository suite or external independent-author review.

## 5. Mandatory dual audit

**PHYS-MATH AUDIT:** (PASS in declared domain) sign/units and initial root; h_i positive invariance, E monotone, theta upper, exact ell lower; pressure Jacobian row-sum identity, homothety; MPFR lower-for-m and upper-for-L; panel boundary and knot jump. Counterexample boundaries: if negative cell energy, h_i allowed to contract or geometry leaves positive octant, the lemma cannot be transported without rederivation. No universal non-expanding claim.

**PHYS-MATH-CODE AUDIT:** (PASS targeted, otherwise limited) exact source identity CE1-F, CE1-G source uniform eta and full-panel MPFR residuals reused, no float integration-error claim omitted; CE1-H constant comparator reconstructed as a matched positive control. 89 new/inherited tests plus held-out GL32 original-cell DOP853 (falsification only) and full ref16 current-run compare. Two inherited mutable-input/origin defects intercepted by local guards, not merged upstream. Full formal program soundness and independent author remain not verified.

## 6. Plot-based adversarial result

`CE1I_GEOMETRY_BOUNDS.png` shows near-indistinguishable CE1-G/H/I total curves; this is expected because the new coefficient changes only the propagation amplification of the much larger source/time forcing, not their size. `CE1I_RELATIVE_GAIN.png` quantifies small 0.01–0.0277% changes; `CE1I_PANEL_LIPSCHITZ.png` shows the rigorously decreasing *panel upper bounds*, not the actual continuously varying Jacobian. No mismatch between same-physics target and figure found after verifying the final panel step extends to u=.08. The effect is scientifically honest but modest; speedup/optimization and new physical completeness claims remain rejected.

## 7. Disposition and next gate

CE1-I `COMPLETE_SCOPED_TIME_LOCAL_PRESSURE_BOUND`, not upper-DAG completed node. Top-level 9/15 and CE-1 PARTIAL unchanged; `PRODUCTION_READY=false`, `MERGE_READY=false`, `AUTO_NEXT=false`. The next genuinely useful decision is to reconcile the three independently corrected CE1-G/CE1-H/CE1-I variants into a **separately reviewed canonical source with an explicit pre-merge integration test**; this is not auto-executed. Independent-author R6/C9 and MPFR software assurance remain exact admission obligations, not redundant math loops.
