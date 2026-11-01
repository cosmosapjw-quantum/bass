# R5–R7 | Exact physical VI0 null Liouville, area Jacobian and scalar oblique Kato

## Real result and source identity

The source is BASS PR #311 HEAD `8d15551c2e0127ede4344f0969f8b7e251a09e3e`, file `research/vi0_manifold_20261101/vi0_dynamics.py` exact Git blob SHA1 `aa3c7d5ba4e3aca62efe0c8651df73b5d29ea8f9`. PR #310 original constrained 7D geometry and original BASS main 7 formulas are not changed. This is an independent positive collisionless non-gravitating photon *test field*, initialized `I(0,n)=1`, not the coupled original BASS KM2 photon/Peebles/CMB radiation, not a newly gravitating Einstein component.

## R5 exact geometric calculation

Source frame `epsilon123=+1`, class A `C^a_bc=epsilon_bcd N^da`, principal VI0 `N=diag(0,p,-r)`, p,r>0; `sigma/H=Sigma`, W antisymmetric frame angular-velocity matrix, `dτ=Hdt`. Koszul gives `Gamma^a_bc = (C^a_bc-C^b_ca+C^c_ab)/2`. Contracted with unit null direction `n^b n^c` it gives `Gamma(n,n)=n×(Nn)` independently of the fluid tilt equation. Hence the original source-owned future-directed photon characteristics are

`n' = -Sigma n + S n - n×(N n) + W n`, `S=n.Sigma.n`, `ln E'=-1-S`.

For diagonal VI0 the curvature-only part is explicitly `((p+r)n2 n3, -r n1 n3, -p n1 n2)`. Both `n.n=1` and the intrinsic-curvature-only invariant `(1/2)n.N.n` survive under their appropriate limits. The gamma-law fluid source tilt equation's extreme-speed limit has `T=S` for 0<gamma<2; this provides a non-identical source-level consistency check.

The collisionless bolometric Liouville equation for physical intensity is `d ln I/dτ=-4(1+S)` along characteristics. For the transported solid-angle patch Jacobian, `d ln w/dτ = div_S² n' =3S`. Exact derivation: `F_shear=-1/2 grad_S² S`, and for tracefree Sigma, `Delta_S² S=-6S` because it is a degree-two spherical harmonic. `F_curvature=-n×Nn` is divergence-free by symmetry of N and the antisymmetry of epsilon; `Wn` is a Killing flow. This is an exact geometric statement; no fixed finite quadrature is thereby guaranteed to preserve sum w=1.

For **moving** patches and collisionless bolometric intensity, `rho=∑ w I`, `P_ab=∑ w I n_a n_b` obey exactly `rho'=-4rho-Sigma_ab P_ab`, including at finite quadrature resolution as an algebraic moment identity. Omitting `w'=3S w` yields the wrong integrated energy law. This does not make the test photons gravitate in the background Einstein system.

## Covariant source-dependent moving scalar projector

Use original BASS Type-II scalar convention `q_alpha=1-v.n_alpha`, `r_alpha=(1-v²)^2/q_alpha^4`, `a_alpha=w_alpha q_alpha`, `d=a.r>0`, `P=r a^T/d`. Common weight normalization cancels only for P (not for radiation moments). Define `X_alpha=v'.n_alpha+v.n'_alpha`, `r'_alpha/r_alpha=-4(v.v')/(1-v²)+4X_alpha/q_alpha`, `a'_alpha=w'_alpha q_alpha - w_alpha X_alpha`. Then `P'=[r'a^T+ra'^T]/d - P (a'.r+a.r')/d`, and `K=[P',P]`, `[K,P]=P'` exactly. This oblique connection need not be anti-Hermitian.

For pure frame rotation W: `v'_W=Wv`, `n'_W=Wn`, `w'_W=0` so `X_W=0`, `v.v'_W=0` and `P'_W=0`. The physical shear and VI0 connection terms in `n'` are **not** zero; the actual moving sky angle and `w'` are necessary. Polarized coherency screens, collisions, real spectral bands and Liouville full phase-space transport outside homogeneous test photons are not calculated here.

## Real calculation

Reuse the exact PR311 seed 12 positive tilted gamma-law VI0 geometries (gamma 1,1.1,4/3,1.65 repeated), normal time τ in [0,.2], 41 epochs. Independently integrate source-owned gravity 12 seeds under 3 grids each (reintegrations only; zero *new distinct gravitating backgrounds*). Three photon angular grids have 6, 26, 128 nodes. Total **36 new null transport integrations**, **78,720 actual ray physical states** and **1,476 sky moment rows**. Parent background original 12 IVPs are not counted twice. Independent source labels, u, n, E, w, I, fluid v, Omega preserved in data.

Saved data maxima: |n.n−1| 3.559652572704408e−11; |I/E^4−1| 1.9984014443252818e−15; moment identity absolute gap 1.7763568394002505e−15; P²−P and K commutator max 2.220446049250313e−16; pure W projector residual max 1.1539877807039334e−17. The integration unit norm gap is a **numeric integration** effect at DOP853 rtol=2e−11, not exact angle geometry failure.

Case0 at τ=.2: rho AXIS6=0.4512183897897247, Lebedev26=0.4508872649581908, GL8x16=0.45088737918781674; the isotropic no-shear reference exp(−.8)=0.44932896411722156. The GL8x16 difference from that reference is +0.3468316523189019%, conditional on the source-owned VI0 geometry and test photons, **not observed cosmology**. For that case, 6-axis transported ∑w=0.98908373961, Lebedev26 1.00002232302, GL8x16 1.0000000002050. Across twelve cases GL128-vs-Leb26 rho abs difference max 9.769146802729445e−6 and GL128-vs-Axis6 max 0.0017285106620045787; 6-axis weight-sum drift max 0.05704448533038897, GL128 max 6.597116135598213e−7.

## R6 hostile referee

1. Original VI0 structure constant orientation vs normal ray cross sign: direct 3D Koszul tensor contraction across 70 random symmetric N witnesses, negative sign mutation fails by O(10^-1); zero-tilt and N=0 Bianchi I analytic source comparison retains sign.
2. Frame gauge W not physical curvature: wrong frozen rays while W rotates v generate nonzero spurious P'_W. Correct corotation pure-gauge P'_W below 1.2e−17 across 36 physical-grid endpoint witnesses.
3. Angular measure omission: `w'=0` produces a momentum-integral source error 0.0407657 for a real case, and the moving P' changes by as much as 0.3583. This is a scientific defect, not output formatting.
4. Independent constant diagonal Bianchi I conserved coordinate momentum null-redshift test, pure class-A curvature Hamiltonian, spherical-coordinate finite-difference divergence versus 3S, exact Wolfram rational witnesses, rank-one projector and nonunitary Kato limit checked.
5. Mesh convergence: 6-axis is not an adequate propagated full-sky integration rule despite exact initial low moments. Lebedev26 and GL8x16 partly agree, but no rigorous continuum enclosure and no claim of uniform angle/ODE error bounds.
6. Photon initial isotropic normalization is synthetic. No collision, no Einstein backreaction, no electron bath / frequency / CMB; no production right to join PR #311.

## R7 actual evidence

Normal Python **15/15 pytest PASS**; `python -O` pytest displays 15 results but Python assert statements are suppressed and cannot constitute independent optimized verification. Instead `verify_saved_physics.py` uses *explicit exceptions*, no RHS imports, and was run in both normal and `python -O`: **PASS**; 78,720 original rays, 1,476 moment rows, independent recomputed angular pressure and energy RHS max gaps ~1e−15. Independent 3-point finite differences of saved derivative clocks find max gaps log E 4.539114843948866e−5, log I 1.815645936726895e−4, log w 1.3617344509242457e−4, consistent with finite sampled timestep h=0.005; not mistaken for instantaneous ODE errors. One independent stateless Wolfram rational true-geometry check found `{sphere_divergence_residual=0, n.F=0, n.(n×Nn)=0, n.(Wn)=0}`.

**DAG** throughout R1–R7: BASS upper original 9/15 **scoped/source-mapped**, new fully completed upper 0; `G-DYN-MANIFOLD-VI0=PARTIAL`, `P-MIG-II-PREFLIGHT=OPEN`, Join J1 `0/2_FULL_PASS_HOLD`. Genuine physical null direction and angular Jacobian component DERIVED/NUMERICALLY_CHECKED_SCOPED, but complete polarized and source-matched production VI0 still open.
