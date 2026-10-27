# KM-2C: fixed-beta polarized collision memory on prescribed Bianchi I

Status: COMPLETE_SCOPED_FIXED_BETA_BIANCHI_I_MEMORY. This additive research subtree is not a production solver or Einstein-matter solution. Upper KM-2 and DV-2 remain PARTIAL, upper scoped/source-mapped count6/15. Next existing node BF-1, fixed-gauge periodic Bianchi-I spatial projection. No automatic next-node run or merge.

## Physical construction

Signature(-,+,+,+), propagation directions, normal proper time t. Code u=t/T_star multiplies every rate by T_star. beta=v_e/c, nu0=n_e_star sigma_T c, proper density. Fixed beta and nu0 are external prescribed inputs; electron continuity/Euler and opposite material force are not solved. Cold elastic bolometric Thomson is assumed; spectral support remains ENERGY_DOMAIN_UNVERIFIED.

Unchanged KM1 Geometry supplies photon direction n, redshift r, screen E and raw angular weights w. Set F=S_beta E and D=gamma(1-beta.n). With J_n=r^4 E X E^T:

    M_e=L_t[X]=sum w*r^4*D^2 F X F^T
    X_dot=-nu0*D(t)*X+G_t[M_e]
    G_t[M]=3nu0/(8pi*r^4*D^3) F^T M F
    tau_q(t)=int_0^t nu0*D_q(s)ds
    M_e(t)=L_t[exp(-tau_q(t))*X_i]
           +int_0^t L_t exp[-tau_q(t)+tau_q(s)] G_s[M_e(s)]ds

New causal solver: quadratic source stages, separate smooth-kernel GL quadrature,18x18 system per panel. Full initial carrier and per-ray2x2 history remain; not a nine-state Markov closure. The direct reference evolves normal Cartesian carriers with pinned P8 and KM2A collision algebra. Direct and Volterra share geometry/IC conventions, never source histories.

An initial2-test failure came from strict transverse input checks on off-screen RK predictor stages. An ambient linear collision extension is now used for intermediate stages only; same physical RHS and strict accepted-output checks are verified. No state projection, clipping, tolerance change or vendor modification. Original failure and repair logs remain in the archive.

## Scoped evidence

13 unique pytest items passed, final invocation exit0. One scientific campaign:6 geometry IVPs,8 prescribed optical-depth IVPs,8 direct IVPs,7 Volterra solves. Test calls separate; historical science reruns0. Five CAS algebra/limit checks. Native subagent and independent-model review NOT_RUN.

Main u0..0.4, beta=(.3,-.4,.2),nu0*T_star=1.3, inherited noncommuting Bianchi-I geometry.8/16/32/64-panel source differences9.4413e-8/5.9017e-9/3.6925e-10/2.3470e-11; first orders3.99980/3.99844. Angular8->12/12->20/20->28 gaps3.4733e-6/6.4965e-9/2.1746e-14. Off-grid reconstructed moment5.20e-11 and source interpolant4.60e-8 are separate outputs, not certified bounds. Raw weights are not renormalized.

Local collision obeys F0-beta.Fspatial=0. C=gamma(rho-beta.q) changes through geometry: Cdot=-4H*C-gamma*sigma:pi+gamma*beta.sigma.q. Change-14.509775047348224 matches independently integrated geometric work to4.09e-14. Keeping C flat-constant would erase real geometric work.

Initial electron I30=.1 is gain-null but returns Mzz(.4)=-.003527539389341632; Volterra=-.0035275393894433054. Initial memory=-.003076212895840466. Actually integrated positive pairs agree with signed response to1.12e-12. No general positivity theorem or speedup claim.

## Reproduce and evidence location

From this directory, after installing requirements:

    python -m pytest tests/test_curved_tilt.py -q

All seven vendors and the exact tested core/test are in Git. Git metadata and this README are concise semantic summaries. The complete39-file immutable ZIP includes verify_km2c.py, verify_saved.py, complete report/contract/DAG/handoff/source map, all raw rows, CAS source/results, failure and final logs, plots and hashes. Run these archive-only commands from the ZIP:

    python verify_saved.py
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python verify_km2c.py

The second command intentionally starts a NEW science campaign; do not run it merely for delivery or repeat historical campaigns. See DELIVERY.json for the immutable archive.

## Provenance and remaining scope

Original attached KM2B be2ee15f... was separately dual-backed before science; receipt37b00ba45d8e014cc786e48209f75ac662500ec0. Parallel remote parent af1adc... has a different archive and tilted_history module. This subtree vendors the exact attached original c04c8cd... for flat controls, not the parallel96d5f33... implementation. No whole-module equivalence is claimed.

No production Q/Rust, generic beta(t), arbitrary curved tilted history, opposite material force, Einstein feedback, spatial averaging, recoil/thermal spectra, global-tail certificate or observer-sky admission. Next BF1 preserves common-frame physical carrier averaging, projector idempotence, zero-mean complement and P_dot; it does not assume a mean metric solves Einstein constraints.
