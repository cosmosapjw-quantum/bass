# CE1-F independent derivation review

Reviewer role: `/root/angular_certificate_review`. Date: 2026-10-29 (Asia/Seoul).

Parent source actually read: `bianchi/nonperturbative/einstein_vlasov.py`, `einstein_interval.py`, `einstein_exponential_source.py`, and `research/ce1e_20261029/REPORT_KO.md`, at inherited parent commit `a05906527d7dd5e5f6a653a0e4f7d977679d4a0c`. The reviewer did not edit the CE1-F implementation. This is a separate-agent mathematical derivation and numerical falsification review, not an independent model implementation or formal software proof.

## Admission result

The proposed barycentric squared-direction Taylor certificate is mathematically valid with the conditions below. The construction admits an arbitrary nonnegative energy table interpreted as a specified continuum piecewise-constant angular density on first-octant solid-angle cells, reflected in all three momentum signs. The radiation source remains a nonlinear metric functional of that full density. The approximation is an angular numerical discretization with a controlled discrepancy; it does not impose a physical finite-multipole closure.

The exact proof must add stored representative-direction mismatch and initialization errors. The MPFR implementation and its claimed execution results require a subsequent C9 code review.

## Continuum and mean

Let cell C be `[mu_a,mu_b] × [phi_a,phi_b]`, with `0≤mu_a<mu_b≤1` and `0≤phi_a<phi_b≤pi/2`. Here `mu=q_z`, `q_x=sqrt(1-mu²)cos(phi)`, `q_y=sqrt(1-mu²)sin(phi)`, and `dOmega=dmu dphi`. A table entry w is the exact total initial dimensionless energy across the eight reflected copies of C. Therefore `F0=w/(8 Δmu Δphi)` on each copy. Zero w is admissible; total energy must be positive for the parent's strictly positive-energy comparison primitive.

Writing x_i=q_i² gives x in the unit simplex. For uniform solid angle within a cell, the exact mean is

`m_z=(mu_a²+mu_a mu_b+mu_b²)/3`,

`c=1/2+[sin(2phi_b)-sin(2phi_a)]/(4Δphi)`,

`m_x=(1-m_z)c`, `m_y=(1-m_z)(1-c)`.

The cancellation-free quadratic expression for m_z is preferable to a quotient of nearly equal cubes.

Componentwise extrema are

`x_lo=((1-mu_b²)cos²phi_b,(1-mu_b²)sin²phi_a,mu_a²)`,

`x_hi=((1-mu_a²)cos²phi_a,(1-mu_a²)sin²phi_b,mu_b²)`.

These follow coordinatewise monotonicity on the specified octant. The resulting rectangle contains the curved simplex cell; its components need not describe one simultaneously attainable point. That overestimate is harmless.

## Independent Hessian derivation

Fix geometry `0≤ell_j≤L`, `b_j=exp(-2ell_j)`, `v=exp(-sum ell)`, and `f_i(x)=b_i x_i/sqrt(b·x)`. Let Delta=x-m, delta=b·Delta, and A(t)=b·(m+t Delta). Direct differentiation gives

`d² f_i(m+t Delta)/dt² = -b_i Delta_i delta A(t)^(-3/2) + (3/4)b_i (m_i+t Delta_i) delta² A(t)^(-5/2)`.

The first derivative term vanishes after cell averaging because `E Delta=0`. The exact remainder is the integral of `(1-t)f_i''`, so the coefficients are 1/2 and 3/8, respectively.

Define widths D_i=x_hi_i-x_lo_i, `v_i=D_i²/4`, and `V=sum_i v_i`. Popoviciu's variance inequality yields `E Delta_i²≤v_i`, `E ||Delta||²≤V`. Because `sum Delta_i=0`, one may replace b by `b-beta*1`, beta=(1+exp(-2L))/2. Its Euclidean norm is at most `(sqrt(3)/2)d`, where `d=1-exp(-2L)`. Hence

`E delta²≤(3/4)d²V = W`,

`E |Delta_i delta|≤sqrt(v_i W)`.

Along the segment, `A(t)≥exp(-2L)` and `m_i+t Delta_i≤x_hi_i`. Thus the following is a uniform per-unit-cell-energy bound:

`|E[v f_i(x)]-v f_i(m)|≤v b_i [(1/2)exp(3L)sqrt(v_i W)+(3/8)x_hi_i exp(5L)W]`.

Replacing `v,b_i` by 1 gives the proposed simpler common-box certificate. Both replacements preserve an upper bound for nonnegative ell. For cells carrying w≥0, sum w times their componentwise bounds. At L=0 the continuum-vs-exact-mean discrepancy vanishes identically because each pressure kernel is affine x_i.

## Stored representative correction

The actual binary64 ray n generally satisfies `sum n_i² != 1` as an exact real identity. Let xi_i be the exact square of the stored binary64 n_i. Let epsilon_i enclose `|xi_i-m_i|`, epsilon_1=sum epsilon_i, `s0=min(1,sum xi_i)>0`, `r0=exp(-L)sqrt(s0)`, and `M_i=max(xi_i,upper(m_i))`. The segment from m to xi has nonnegative coordinates, total mass at least s0, and therefore

`|v f_i(xi)-v f_i(m)|≤epsilon_i/r0+(1/2)M_i epsilon_1/r0³`.

This follows from `partial_j f_i=b_i delta_ij/r-(1/2)b_i x_i b_j/r³`, `v,b≤1`, followed by the line-segment mean-value bound. The absolute first-term derivative must be added, even when the requested component and displacement signs differ.

If masses are stored differently from the exact table entries, their exact-real mismatch must also be propagated; a mass normalization step cannot be silently identified with the table definition.

## Initial energy and geometry

Continuum energy is exactly `sum w`. The exact-real stored-source initial energy is `sum w*sqrt(sum xi)` if stored masses equal w. A float64 `source.energy0` additionally contains a summation/operation rounding difference. Enclose these separately, and choose `Emax` to bound both the continuum and exact-real stored-source energies.

For positive measures and all-direction nonnegative initial expansion, h_i cannot leave the nonnegative octant: at h_i=0 its rate is P_i≥0. Energy decreases because `E'=-sum h_i(E+P_i)≤0`. The log-scale box can therefore be obtained with `ell_i(u)≤h_i(0)u+Emax*u²/2` for each compared exact solution.

The inherited Dini system is applicable: the friction Jacobian has logarithmic infinity norm `max_i(h_i-theta)≤0`; pressure has `sum_j |partial_ell_j P_i|=4P_i≤4Emax`, also for a positive fixed finite measure with nonunit stored representatives. Consequently `D+x≤y`, `D+y≤4Emax*x+eta` transports the certified pressure discrepancy eta. Initial-rate mismatch must enclose the continuum Hamiltonian root using exact-binary sx,sy and exact sz=-(sx+sy), as well as the actual stored initial h.

The resulting geometry bound covers exact continuum versus exact-real stored-source ODEs. Time-integrator truncation and floating evaluation require their own certificate if included in a claimed total error budget.

## Numerical falsification performed

`CE1F_INDEPENDENT_NUMERIC.json` preserves 96 cases and the seed 182047. Each case used an independently constructed 64×64 Gauss-Legendre integral in mu and phi, not the proposed barycentric approximation. Geometry caps were L=0,.01,.08,.2,.7,1.5. Random cell endpoints, random anisotropic ell inside each box, and a full-octant cell were included.

- Maximum measured pressure gap/bound among nonzero bounds: 0.19223869417892261.
- Violations allowing a 5e-14 floating quadrature floor: 0/96.
- Analytic cell means versus quadrature maximum difference: 3.3306690738754696e-15.
- Isotropic L=0 maximum residual: 2.886579864025407e-15, consistent with floating quadrature.

This finite sample is a falsification test of the analytic calculation, not the proof of uniform validity. The differentiation, variance inequalities and exact remainder above provide that proof.

Mutation: replacing the squared-direction barycenter by the coordinate-midpoint ray invalidates the zero-geometry cancellation. A full first octant has continuum initial z pressure 1/3, whereas mu_mid=1/2 gives 1/4. The gap is 1/12 while the unchanged Taylor cell bound is zero. A regression test should distinguish this mutation and should not treat the coordinate midpoint as the mean.

## Directed-trigonometry requirements

The current inherited Interval exposes exp/sqrt/hyperbolic functions, not generic sin or cos. MPFR correctly rounded scalar trig operations must be enclosed with attention to monotonicity. A generic application of the Interval monotone-unary helper to sin on [0,pi] is invalid because sin turns at pi/2. It is also necessary to use a directed pi enclosure rather than promoting binary64 pi to an exact pi value.

For boundaries represented by exact rational fractions of pi/2, endpoint trig can exploit symmetry and exact special values. For sin(pi*r), r∈[0,1], reflect to r∈[0,1/2], treat r=0 and r=1/2 as exact 0 and1, and evaluate directed endpoints only on a certified monotonic interval. A rounding interval that straddles the critical point must include1. Cos(pi*r) is decreasing on [0,pi], with exact values at r=0,1/2,1; account for intervals that touch or cross endpoints. Do not assume sin is monotone merely because the exact midpoint lies in the first branch.

## Findings and closure contract

1. Mathematical bound: PASS_SCOPED, under the stated continuum-cell, positivity and expanding-sector assumptions.
2. Stored nonunit direction: must be included via segment norm floor; requires code review of implemented correction.
3. Initial energy: both exact continuum and exact-real sampled initial energies must enter Emax; requires code review.
4. Directed trig: generic inherited monotone-unary helper is insufficient; requires explicit endpoint/range implementation review.
5. Numerical independence: separate quadrature construction and separate-agent derivation completed; shared NumPy/SciPy libraries retained.
6. New no-go result: not proposed. The midpoint example is a localized algorithmic mutation counterexample.
7. Full software/formal correctness and native implementation: outside this review.

