# BASS KM-2D S0 | prescribed time-varying electron tilt, actual polarized Thomson memory

**2026-10-30 · one bounded science unit · parent PR273 exact HEAD \`48e6c979c49a49ff6854a9555fe97a9690d86d16\`.**

## Original physics and source authority

Reuse *unmodified* \`research/dual_lane_km2c_20261028/code/curved_tilt.py\` Git blob \`05aade3aab7e9a32c11608882c943e4d3cb6f379\`, original \`vendor/tilted_collision.py\` \`92660768f4719d78261fed1cb44f186d2821629d\`, and KM1 \`vendor/source_memory.py\` \`9d500e36fefaa4ddc22300a2f03d9eb9cfe98403\`. Those source, tests and previous results are protected. The original finite-beta KM2A/KM2C cold-elastic Thomson P8 carrier is the source of physics, not a newly invented gain. This is a separate **KM-2D subgate of the still-PARTIAL upper KM-2 node**, not part of CE1's six-cell photon-only experiment and does not reuse its \(h\) accuracy gate. BASS top-level progress **9/15** remains unchanged.

Metric signature (-,+,+,+), photon propagation tetrad n, normal proper t, numerical \`u=t/T_star\`, \(\beta=\mathbf v_e/c\). Rest electron opacity \(\nu_0=n_e^\star\sigma_T c\) and all dimensionless rates carry \(\nu=\nu_0 T_\star\). No electron density boost. The **electron velocity \(\beta(u)\)** is a smooth externally prescribed timelike 3-vector, not solved by an electron Euler/continuity equation. Normal-frame geometry is the original KM1 prescribed, noncommuting Bianchi-I \(H(u),\sigma_{ij}(u)\) on \(u\in[0,0.25]\), not an Einstein solution. Keep exactly the initial normal-ray angular grid, its non-renormalized weights, full 2×2 per-ray field, and the original P8 transverse Hermitian \(S+iA\) carrier.

## Exact continuous finite-tilt scattering and causal representation

For each time \(\beta(u)\), \(\gamma=(1-\beta^2)^{-1/2}\), \(D_q=\gamma(1-\beta\cdot n_q)\), \(F_q=S_\beta(n_q)E_q(u)\). The existing KM2C geometry transports \(e,\mu,E,w\) independently of electron tilt. The original exact instantaneous source and loss are
\[
L_u[X]=\sum_q w_q \mu_q^4D_q^2 F_q X_q F_q^T,\quad
G_{q,u}[M]=\frac{3\nu}{8\pi\mu_q^4D_q^3}F_q^TMF_q,\quad
d_q(u)=\nu D_q(u).
\]
In the original time-dependent normal screen \(\dot X_q=-d_q(u)X_q+G_{q,u}[M]\), \(M=L_u[X]\). This equation is valid for externally prescribed \(\beta(u)\) without adding an artificial \(S_\beta'\) term: \(X_q\) is **normal-frame pullback** in the geometry screen, not the electron-frame carrier. Its exact causal equation retains all initial rays:
\[
\tau_q(u)=\int_0^u \nu D_q(s)ds,\quad
M(u)=L_u[e^{-\tau_q(u)} X_{q,0}]
+\int_0^u L_u e^{-[\tau_q(u)-\tau_q(s)]}G_s[M(s)]\,ds.
\]
The old direct IVP transports the full normal J independently; the Volterra solver reconstructs M without accessing direct-solver source histories or RHS. Variable beta modifies L,G,d at each time, not the old source definition. Numerical collocation, angle quadrature and prescribed geometry remain separately approximate.

## New acceleration-energy exchange identity (derived)

Let \(T^{00}=\rho\), \(T^{0i}=q_i\) (energy flux divided by c), \(\pi_{ij}=T_{ij}-(\rho/3)\delta_{ij}\), and \(C(u)=\gamma(u)[\rho(u)-\beta(u)\cdot q(u)]\). The original instantaneous Thomson force \(F^\mu_{\rm coll}\) satisfies \(F^0_{\rm coll}=\beta\cdot\mathbf F_{\rm coll}\). With the original KM1 homogeneous Bianchi-I normal transport, and \(\gamma'=\gamma^3\beta\cdot\beta'\),
\[
\boxed{
C'=-4HC-\gamma\,\sigma:\pi
+\gamma\,\beta\cdot(\sigma q)
+\gamma^3(\beta\cdot\beta')(\rho-\beta\cdot q)
-\gamma\beta'\cdot q .}
\]
Equivalently \(C' = [C']_{\text{KM2C fixed }\beta}+
(\gamma'/\gamma)C-\gamma\beta'\cdot q\). The last two terms are **reference-frame acceleration work**, not collision energy creation nor a matter-backreaction solution. For \(\beta'=0\), recover KM2C; for H=σ=0 with time-varying beta, generally \(C'\ne0\). Claiming C constant on an accelerating normal-time frame would be wrong. Exact symbolic product rule reduces the residual to zero (Wolfram evaluated with stateless symbolic functions, not yet an independent proof of the numerical implementation).

## Fixed science campaign (before results)

Noncommuting prescribed Bianchi-I profile unchanged. On \(0\le u\le0.25\), set
\[
\beta(u)=(0.30,-0.40,0.20)+u(0.20,-0.10,0.12),
\qquad \nu_0T_\star=1.3,
\]
with the original KM2B mixed polarization input and nθ=8 or 12 (nφ=2nθ). All endpoints are subluminal and the law is affine. Direct DOP853 full-normal-carrier IVP, independent causal source Volterra with panel counts 8/16/32, and a 24-node independent temporal work integral. Fixed nθ=12 control for force and acceleration-work balance. Explicit frozen β'=0, zero-opacity and original source-null octupole controls.

Produce actual source/collision histories \(M_{ab}(u)\), normal stress and flux \((\rho,q)\), \(C(u)\), geometric and acceleration work, integrated \(C\) balance, optical depth, endpoint direct/Volterra errors and panel refinement, plus one physics table JSON/CSV. Test raw-grid force/invariant without treating finite quadrature as exact angular integration; no post-hoc loosening of gates.

## Claim ceiling and stop

A new **physical model output** and numerical direct–Volterra comparison for *prescribed* \(\beta(u)\) and Bianchi-I geometry is admissible after actual tests. No electron Euler/continuity, self-consistent Einstein-matter coupling, finite-temperature Compton/recoil, frequency-domain validity, arbitrary time-varying velocities, generic Bianchi family, global positivity or production Rust claim. This is a model evolution in its stated effective cold Thomson domain, not an observation. Upper KM-2 PARTIAL; BASS **9/15**, zero new upper completed nodes, \`production_ready=false\`, \`merge_ready=false\`, \`auto_next=false\`; native subagent NOT_RUN if no host native delegation; genuine distinct-author R6/C9 NOT_RUN.

STOP_AFTER_ONE_BOUNDED_UNIT=true.
