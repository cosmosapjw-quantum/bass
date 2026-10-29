# CE1-G: positive tabulated radiation의 전체 시간구간 source/time 오차 합성

## 권위·범위

- Parent: `cosmosapjw-quantum/bass` PR239, `9de0f37955f259b5e9172ce406d1353bf7cc3695`, CE1-F scoped positive angular-cell certificate.
- Signature `(-,+,+,+)`, normal proper dimensionless clock `u=t/T_*`, `ell_i=ln a_i`, `h_i=T_*H_i`, `E,P_i=(8*pi*G*T_*^2/c^2)*(energy density, pressure)`; `Lambda=0`.
- Diagonal reflection-even Bianchi I, massless collisionless positive piecewise-constant first-octant angular-energy cells reflected into eight octants. No low-l closure, collisions, global tilt, spatial EFE, source clipping/renormalization, or constraint projection.
- Each table entry is the total angular energy over the original cell. Integer refinement preserves the physical continuum density. Numerical source `P_Q` uses exact-real interpretation of recorded binary64 rays and masses. `P` is the exact continuum angular integral.

## 1. Equation and exact source Jacobian

With `b_i=e^{-2ell_i}`, `V^{-1}=e^{-sum ell}`, and nonnegative measure `mu`,

`E(ell)=V^{-1} integral sqrt(sum b_j n_j^2) dmu`,
`P_i(ell)=V^{-1} integral b_i n_i^2/sqrt(sum b_j n_j^2) dmu`.

Then `sum_i P_i=E`, `partial_{ell_j} E=-E-P_j`, and

`partial_{ell_j} P_i=-(1+2 delta_ij)P_i+R_ij`,
`R_ij=V^{-1} integral b_i b_j n_i^2 n_j^2/(sum b_k n_k^2)^(3/2) dmu`.

For nonnegative measure, `0<=R_ij<=P_i` and `sum_j R_ij=P_i`. Hence every Jacobian entry is nonpositive and `sum_j |partial_{ell_j}P_i|=4P_i`. On `ell>=0`, `0<=P_i<=E<=E(0)`. The same identities hold for the exact-real stored positive discrete source `P_Q` with its own initial energy.

The Einstein evolution is `ell_i'=h_i`, `h_i'=-theta h_i+P_i(ell)`, `theta=sum_i h_i`. The Hamiltonian constraint `C=sum_{i<j}h_i h_j-E` propagates `C'=-2theta C`; no projection is needed. Positive initial `h_i` remain nonnegative, because at `h_i=0` one has `h_i'=P_i>=0`.

## 2. Stored Hermite trajectory and whole-panel residual

The recorded binary64 RK4 nodes/slopes define `c_{i,k}` for the cubic polynomial `tilde z_i(v)=sum_{k=0}^3 c_{i,k} v^k`, `v=(u-u_i)/(u_{i+1}-u_i)`, interpreted as an **exact real polynomial with stored binary coefficients**. This definition is not the same as assuming that the float64 solver is exact.

Define on each open panel:

`r_ell=tilde ell' - tilde h`,
`r_h=tilde h' + tilde theta tilde h - P_Q(tilde ell)`.

The existing CE1-C `residual_taylor_mpfr` encloses both residuals on the *entire* panel by a third-order Taylor polynomial around the exact-rational subcell midpoint and an analytic fourth-derivative majorant. It uses MPFR192 RNDD/RNDU and the actual stored binary ray/mass data. It is applicable here because the fourth-derivative majorant uses only positivity of the stored ray masses, the expanding geometry, and a bound on `sum mass*||ray||`, not the CE1-B angular polynomial form. This generality is checked in §4 below.

**Important knot issue:** floating-point construction of the cubic coefficients need not give exact-real interpolation at the next stored RK4 knot. At every panel endpoint define

`j_{i,k} = sum_{r=0}^3 c_{i,r,k} - y_{i+1,k}`

with each coefficient and `y` treated as exact binary rationals. MPFR outward arithmetic encloses the maximum absolute `j_ell` and `j_h`; the error comparison adds the jump before starting the next panel and at the final endpoint. The jump is small for this fixture but cannot be dropped merely because the coefficients came from a Hermite formula.

## 3. Nonlinear comparison and source/time/initial decomposition

Let `eta_Q` be the CE1-F MPFR pressure difference bound for `P(ell)-P_Q(ell)` on a shared expanding box containing the exact continuum solution and the entire reconstructed path. The exact continuum initial Hamiltonian root uses the exact binary `s_x,s_y,s_z=-(s_x+s_y)` and exact cell-energy sum; compare to the stored RK4 initial `h(0)` with outward MPFR bound `delta_0`. Choose `Emax>=max(E_cont(0),E_Q(0))` where `E_Q(0)` is the exact-real stored ray/mass energy, not the rounded NumPy sum.

For `e_ell=||ell-tilde ell||_inf`, `e_h=||h-tilde h||_inf`, both states in the nonnegative expanding octant imply the logarithmic infinity norm of `D_h(-theta h)` is `max_i(h_i-theta)<=0`. The source Jacobian above gives the Dini inequalities on each panel:

`D+ e_ell <= e_h + rho_ell`,
`D+ e_h <= 4 Emax e_ell + eta_Q + rho_h`,

where `rho` are MPFR-enclosed full-panel residual suprema. The positive comparison propagator for `k=2sqrt(Emax)` is

`Phi(t)=[[cosh(kt),sinh(kt)/k],[k sinh(kt),cosh(kt)]]`.

The forcing is split linearly into (i) initial `delta_0`, (ii) source `eta_Q`, and (iii) residuals and binary Hermite knot jumps. This yields a componentwise positive total upper bound for the continuum exact ODE versus **recorded RK4 knot**, not merely versus an idealized discrete ODE.

To avoid a circular box argument, the continuum exact expanding solution satisfies `h_i(u)<=h_i(0)+E_cont(0)u`, `ell_i(u)<=h_i(0)u+E_cont(0)u^2/2`. The actual Hermite path box is obtained independently from outward Bernstein hulls of its stored binary coefficients. Their union is passed to the CE1-F source bound; every panel's `h_i>=0` and `ell_i>=0` is checked from the hull. No inference from sampled endpoint positivity.

## 4. Fourth derivative majorant applicability

For a single positive stored ray, write its pressure contribution as `w n_i^2 A(u) B(u)` with `A=exp(-sum ell-2ell_i)` and `B=Z^(-1/2)`, `Z=sum n_j^2 exp(-2ell_j)`. The cubic Hermite `ell` has vanishing fourth derivative. Put `H_k=max_i |ell_i^(k)|` for k=1,2,3 and `G_k=max_i |h_i^(k)|` for k=1,2,3. The product rule gives a bound on the fourth derivative in terms of the first four relative derivatives of `A` and `B`. Their absolute coefficients depend on H1,H2,H3 only, and `Z` is positive for every stored nonzero ray. The source prefactor `V^{-1} b_i n_i^2/r` is bounded by `||n||` for ell>=0. Thus summing positive stored masses gives `Ecap=sum w||n||` and the CE1-C `_p4_interval` majorant applies to arbitrary positive stored ray measures, not only polynomial angular densities. For `d^4(theta h)/du^4`, the bound is `24 G3 G1+18 G2^2` because h is cubic.

Symbolic cross-checks: `D^4 exp(g)/exp(g)` and `D^4 Z^(-1/2)/Z^(-1/2)` coefficient identities both simplify to zero in independent SymPy and Wolfram evaluations. This is algebraic evidence, not an independent proof of every numerical binding.

## 5. Admission boundary

The output is an a posteriori **mathematical interval enclosure evaluated by MPFR192** for exact recorded binary input, with the analytic majorant and comparison theorem as assumptions of the software verification. It is not a formally machine-verified Python/MPFR program, not a physical input-acquisition uncertainty certificate, and not a native Einstein–Boltzmann solver. The exact physical continuum source is the declared table, not arbitrary unmeasured sky subcell structure. The `P_Q`/path numerical computation uses float64 but its rounding is captured indirectly by treating its recorded outputs as exact binary data and measuring the residual against the exact-real source.

Prior literature: Lee–Nungesser–Tod, *General Relativity and Gravitation* 52 (2020), DOI 10.1007/s10714-020-02699-7, massless Einstein–Vlasov Bianchi I under small anisotropy (not the present arbitrary-amplitude certificate); Wu–Yang, arXiv:1804.03363, Hermite residual methodology for **linear** ODEs (not a proof for nonlinear Bianchi I). The BASS comparison proof is derived here, not attributed to either paper.
