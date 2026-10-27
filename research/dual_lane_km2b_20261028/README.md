# KM-2B: fixed-beta normal-time polarized Thomson evolution

Status: COMPLETE_SCOPED_FIXED_BETA_FINITE_TIME_NORMAL_CLOCK. Additive research only. Parent PR209 / 68bcb3e956d3c6c4c9c60aa485c7c4c8187e8030. No production edits or merge. Full evidence and original source lock are in the immutable KM2B ZIP identified by DELIVERY.json.

## Physics and implementation

Flat/frozen normal tetrad, constant prescribed beta=v_e/c and nu0=n_e_star sigma_T c. Code time can be u=t/T_star with nu0 multiplied by T_star. Bolometric P8 real S+A encodes physical Hermitian S+iA. Cold Thomson energy-domain validity remains unverified.

Y=J_e=D^4 S J_n S^T, dOmega_e=D^-2 dOmega_n, D=gamma(1-beta.n). In normal time:

    Ydot=nu0 D (B[M]-Y), B[M]=(3/(8pi)) Pe M Pe, M=int Y dOmega_e.

TiltedDirect invokes the pinned KM2A normal-frame RHS. TiltedVolterra independently solves unknown M with quadratic left/mid/end source interpolation, EXACT exponential loss weights, and an18x18 causal system. It never calls direct histories or their RHS. It retains the entire initial angular field and angle-dependent history, not a9-state Markov closure. A separate all-past kernel sum checks the recurrence. Arbitrary-time reconstructed moment and source_polynomial are distinct outputs.

A small independent pairwise Jones screen matrix exponential uses four-vector boost/gauge maps, not the rank9 gain assembly. No operator arrays may be mutated during a fixed-coefficient history.

## Invariant and conditional continuum relaxation

C=int tr(Y)/D dOmega_e=gamma(rho_n-beta.q_n) is conserved on the normal-time slice. q=energy_flux/c. Electron rho_e is NOT separately conserved on this slice. Stationary intensity Iinf=C/(4pi gamma); J_n,inf=Iinf P_n/(2D^4).

With exact angular integration, the generator is self-adjoint in the Hilbert-Schmidt inner product weighted by1/D. The rest Thomson spectrum gives norm_w(Y-Yinf)<=exp[-.3 nu0 Dmin t]norm_w(Y0-Yinf), Dmin=sqrt((1-|beta|)/(1+|beta|)). Full proof and assumptions are in REPORT_KO.md inside the archive. This is not a spectral/thermal H theorem, not an unconditional numerical-positivity theorem, and not automatically inherited by raw coarse quadrature.

## Actual verification

12 unique pytest items passed. Scientific campaign1:14 direct IVPs,1 deliberate wrong-rate IVP,8 Volterra solves,1 dense pairwise reference. Tests separate; historical scientific reruns0. Same mapped16x32 angular grid, beta=(.3,-.4,.2),nu0=1.3,T=1.2: normalized source errors at8/16/32/64/128 panels=3.8546e-9,2.4138e-10,1.5030e-11,8.7562e-13,3.4789e-14. The last is at the direct-reference sensitivity scale, not a certified continuum error. Off-grid reconstructed source and interpolating polynomial are separately recorded.

At beta=.85 on raw normal8/16/32/64 polar grids the invariant drifts .00922974,6.6288e-6,4.2683e-13,5.0189e-14. Same coarse N16 direct/Volterra agreement1.4558e-11 does NOT remove the2.7949e-5 angular source difference vsN64.

Electron I30=.1 initially has M=0, but Mzz(.8)=-.007844595900356573 direct and-.007844595900394387 Volterra. Initial-memory contribution-.005895918832020086 is retained. Two physical positive initial states were separately evolved; their source difference matches the signed response to3.12e-13. Omitting or duplicating ray D gives finite-time invariant defects .00376875/.00261997.

Long-time direct beta=.6x,T=60 approaches invariant-selected equilibrium, weighted relative distance1.0442e-8 below the derived bound8.2938e-6; invariant drift4.27e-14. Neither this test nor positive sampled fixtures proves positivity/stiff accuracy for every step size.

## Reproduce

From this directory:

    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest tests/test_history.py -q

The complete ZIP additionally includes verify_km2b.py, verify_saved.py, all raw rows, full Korean derivation/contract/DAG/handoff, CAS, logs, figures and manifest. Run full science only from that archive, and not merely to republish saved evidence:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python verify_km2b.py
    python verify_saved.py

## Boundaries and next

Upper KM2 remains PARTIAL: production Q/Rust, changing beta/current schedules, curved-plus-tilted transport, matter/Einstein feedback and spectral validity are OPEN. Native subagent and independent-model review NOT_RUN; CAS is symbolic verification only. Upper count6/15 is scoped/source mapping, not physics completion. Next existing node BF-1: physical-carrier spatial projection on fixed-gauge Bianchi-I torus with full nonlinear local collision correlations. No automatic next node execution.
