# Stage 3 BASS dynamics: stress-neutral b*(x) is not an Einstein solution

Standalone light sandbox source-formula experiment using **exact BASS PR164 Git blob** `1cab2bf7eab5a306ab207206ca3a0fc793dc9163` (archival file SHA256 `153e0a3ff4546adceaa56ed74149ccefc8ade4b72265064139d72e76a28967e7`). Parent full nonlinear LRS Einstein DOP853 dynamics run with the same fd96 m,A, Omega_m mass fraction=0.1, initial signed shear zero, frozen *isotropic nonkinetic* radiation background, z20→4. No native REI/HHe or anisotropic photon/neutrino hierarchy; this is **BASS physics**.

**Actual sandbox evidence:** 12 original-BASS Einstein IVP cases (m/Tref=3,30,300 and A=-.5,0,.5,2) on 81 shared points each = 972 states; five dynamics checks PASS. Independent finite-difference source-only energy-work identity:
`d rho_kin/d ln a=-3(rho_kin+pbar_kin)-2(s/H)DeltaP` max normalized abs finite-difference residual `5.139106620253739e-10`. Source-based Raychaudhuri max normalized FD residual `1.0489418315828934e-10`. DOP853 `rtol=2e-12,atol=2e-14`. Residuals are discretized finite differences, not rigorous numerical enclosures.

At final a=.2, for A=.5, the (mass, actual b, instantaneous stress-neutral b*, actual Sigma, actual ΔP) values are:
```
m3:   0.00149040868198984 ; 0.04929762909960218 ; 0.001459375570729503 ; +6.550278408363588e-5
m30:  0.0000330464987201778; 0.04796485041158629 ; 0.000028870757715017777; +1.0904526123262557e-6
m300: 0.00000033588691766698795;0.04794719114400091; 0.0000002925007558651904 ; +1.0999859941051572e-8
```
Mass3 A=.5: actual b/b* = 0.030232867365255645, so source stress is **not** neutralized by z4. For A=0 the geometry remained exactly isotropic/s=0 in the tested IVP. Reinterpreting ΔP=0 as dynamical isotropization would be unsound.

Independent 54-digit `mpmath` re-evaluation of **the same fixed binary64 FD96 quadrature nodes**:
- m3,x=.7,A=2: b* double `0.19224316779331183`, mp54 `0.192243167793312446640537885877637358450016773635388651`, absolute difference `6.166405378858776e-16`.
- m300,x=1,A=-1: double `-0.11552540046463713`, mp54 `-0.115525400464637036177667323243723626831430638438906172`, absolute difference `9.382233267675628e-17`.

These MP54 checks verify scalar reduction precision for *fixed* binary64 quadrature rules only; they do not independently validate continuum q/mu quadrature error or cosmological model fidelity.

**Dynamical interpretation:** with ξ=b-b*(x,A,m), exactly
```
ξ' = s/H - db*/dx;  ΔP = χ_b(b*) ξ + O(ξ²),  χ_b(b*)<0.
```
The source term in the signed shear Einstein equation has restoring local sign, but there is external Hubble friction, other stress components and redshift drift b*'(x). No global Lyapunov or full Einstein stability theorem is asserted. b* is chart- and initial distribution dependent and cannot replace the gauge-aware user Σ=√3 |s|/H.

**Reproduction:** Original parent `research/rei_einstein_tangent_20261016/kinetic_tangent.py` + current BASS `kinetic_equilibrium.py` and `einstein_stress_lag.py`; run with SciPy/NumPy `OPENBLAS_NUM_THREADS=1`. Parent solver source preserved, unmodified.

Science labels: theorem `DERIVED_CAS_VERIFIED`; BASS FD96 source formula `NUMERICALLY_CHECKED`; local Python code `IMPLEMENTATION_VERIFIED`; native REI callback/NCP `NOT_RUN`; global dynamical isotropization/CMB/EoR `HOLD`.
