# KM-1: BASS-source-matched polarized source memory

Status: COMPLETE_SCOPED_SOURCE_MEMORY_CONSTRUCTION. Parent: DL2 e3e829903294f437373369420b1dff95f6592e85. Additive research only: no owner/main/production changes, merge, old campaign rerun or budget reset.

## Physical and numerical scope

Prescribed smooth finite-shear Bianchi I; geodesic normal tetrad; untilted rest electrons; cold elastic Thomson; full polarized bolometric carrier. No amplitude expansion. This is not a selfconsistent Einstein history. Time u=t/T_star, with Hbar=T_star H, sigmabar=T_star sigma, nubar=T_star n_e_star sigma_T c. Do not confuse u with Q Hubble time d tau_H=H dt. Directions are photon propagation, not observer sky -e. P8 code S+A represents Hermitian S+iA; positivity is a two-dimensional-screen property.

DirectHistory calls byte-matched P8.tensor_rate but is a new bounded reference ODE, NOT production QState/Rust. Its collision generator uses raw deformed angular quadrature alpha P(sum w J)P-J. It does not apply the continuum-eigenvalue P8.collide exponential on deformed grids; no exact discrete production-Strang equivalence is claimed.

## Exact construction

Let A_dot=-(H I+sigma)A, A(t_i)=I, mu=|A qhat|, e=A qhat/mu. Then dOmega_t=det(A)/mu^3 dOmega_i. A 3x2 screen E satisfies E^T E=I2, E^T e=0 and E_dot=(e_dot e^T-e e_dot^T)E. Arbitrary time-dependent shear generally requires chronological propagation.

With J=mu^4 E X E^T, streaming cancels exactly:

    X_dot=-nu X+nu G_t[M],  G_t[M]=alpha mu^-4 E^T M E,
    M=L_t X, L_t X=det(A(t)) integral mu(t) E(t) X E(t)^T dOmega_i,
    alpha=3/(8pi), nu=n_e_star sigma_T c.

The exact source Volterra representation is

    M(t)=b(t)+integral_{t_i}^t K(t,s)[M(s)] ds,
    b(t)=exp(-kappa(t,t_i)) L_t X_i,
    K(t,s)=nu(s) exp(-kappa(t,s)) L_t G_s.

Writing Z(t,s)=E(t)E(s)^T gives

    K(t,s)[M]=alpha nu(s) exp(-kappa(t,s)) det(A(t))
               * integral [mu(t)/mu(s)^4] Z M Z^T dOmega_i.

M has nine real components; the full initial angular X_i and geometric/angular history remain in b and K. Rank-nine gain is not a nine-state kinetic closure. Initial gain-null or high-multipole data must not be replaced by M_i alone.

For a finite smooth prescribed interval, mu bounded away from zero and bounded nu imply a continuous bounded kernel. Its norm is bounded by alpha nu(s) exp(-kappa) det(A(t)) integral mu(t)/mu(s)^4 dOmega_i. The n-fold Volterra operator is bounded by [C(T-t_i)]^n/n!, giving finite-interval existence/uniqueness without a small-shear or contraction<1 assumption. This is a derived prescribed-coefficient result, not nonlinear Einstein well-posedness or a certified numerical error enclosure.

## What was actually checked

8 scoped pytest items passed. The scientific validator uses seven NEW direct IVPs and five NEW geometry histories; these are distinct from internal test calls. Three angular grids (6x12,10x20,16x32), three times and four time-quadrature orders give36 identity rows;12 geometry,12 physical and13 signed-tail records are saved in the full archive.

Crucially, evaluate_with_source/reconstruct_with_source INSERT AN INDEPENDENTLY INTEGRATED DIRECT M(t). They check Duhamel consistency; they DO NOT solve the unknown Volterra source. KM3 and DV1 remain separate.

At order32, maximum moment identity error=1.0222933610748441e-12 and carrier error=2.2937207688755734e-13, against the pre-set3e-9 identity gate. Tightening time tolerance changes the endpoint by2.886579864025407e-14. Angular endpoint gaps6->10 and10->16 are1.5882368581882078e-5 and1.1603931149295477e-9. Relative raw collision-energy defects are3.309091456124537e-6,3.1487324628061254e-10,6.483306684147096e-15. Same-grid algebraic agreement is not continuum accuracy; these are empirical refinements, not infinite-tail certificates.

A positive paired-state difference initial Delta I=.1 Z40 has zero initial source but at u=.6 Delta Mzz=-.0012754205340920798. The initial-memory term is-.0009081657929496682 and gain-history term-.00036725474114222183. Their sum matches direct to1.90e-16. Two positive IVPs agree with the signed-difference IVP to2.98e-14.

Deliberate mutations are detected: deleting initial-tail b gives residual norm.0010014585096715378; omitting the angular Jacobian gives moment error.3975973146539924; ignoring chronological order gives momentum-map error.0008575307126771486. Source-null initial-state compression is not admissible in this finite-shear construction.

External Wolfram returned zero residuals for three diagonal-characteristic Jacobian/intensity/combined-moment identities. Its undefined-symbol warning is retained in the archive; printed static eigenvalues in that call were declarations, not new computed checks. Native subagent and independent model review NOT_RUN. No Rust/tilted/spectral/curved-Bianchi/spatial-projector/Einstein-feedback/production certification.

## Reproduce

From this directory:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest tests/test_memory.py -q
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python verify_km1.py

The vendor code hashes are checked by verify_km1.py. Raw results are regenerated in evidence/. Code, tests and validator Git blobs equal the tested archive bytes.

## Full evidence and continuation

The immutable24-file ZIP identified by DELIVERY.json includes full Korean derivation REPORT_KO.md, detailed OPERATOR_CONTRACT.json and DAG_UPDATED.json, raw rows, test/failure notes, CAS, figure and source hashes. Git contains the executable subset and concise state. Read both scopes, not this summary alone, before extending scientific claims.

Next: KM3's untilted prescribed-Bianchi-I slice, independently solve M(t) by causal product integration, preserve b and raw weights, and separate time/angular errors. The open generic tilted KM2 wiring is not a prerequisite to the untilted slice. DV1's same-physics three-path validation is not promoted by this construction. Global physical completion remains null;4/15 is source mapping plus scoped research units only.
