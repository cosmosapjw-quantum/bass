# BF-2: spatially averaged polarized collision correlations

Status: COMPLETE_SCOPED_COMMON_FRAME_COLLISION_CORRELATIONS. Parent BF1 PR213, commit30b229ed99337ed2f846badf75538abf8b4c3c8e. Additive research only; no production edits or merge.

All cells use the same normal observer, physical directions and screen. The physical P8 carrier is averaged with the unchanged BF1 projector. The unchanged KM2A generator uses proper-density opacity nu=n_e_star*sigma_T*c and exactly one relative-flux factor D. No amplitude expansion or weight/positivity correction.

For Jbar=mean(J), xi=J-Jbar, nubar=mean(nu), and a chosen unit-opacity L_ref:

    mean(nu L_beta J) = nubar L_ref Jbar
        + L_ref mean((nu-nubar)xi)
        + mean(nu(L_beta-L_ref))Jbar
        + mean(nu(L_beta-L_ref)xi).

The reference defaults to the mean-electron-current velocity. Its density norm differs from nubar and is handled separately. These are exact bookkeeping terms, not a closed mean-state solver. Pdot J is a separate measure term.

Two opposite cold electron velocities in two equal-volume spatial cells have mean current velocity zero, but normal-isotropic radiation gives mean energy transfer (4/3)nu*rho*gamma^3*beta^2. At beta=.6 the ratio to nu*rho is15/16. Local elasticity holds; mean force need not be elastic in the mean-current frame. A prescribed bath supplies the energy; no material feedback is evolved.

A distinct exact reaction-only example with two static opacities gives a spatial memory term after eliminating their difference. For mean rate r, rate contrast d and rest generator L, the kernel is d^2 L^2 exp[rL(t-s)], plus the full initial-complement contribution. This identity is checked against known exact local P8 semigroups, NOT an independent spatial Volterra solve or a spatial PDE.

## Reproduce

From the complete immutable archive:

    OPENBLAS_NUM_THREADS=1 python -m pytest tests/test_mean_collision.py -q
    python verify_saved.py

For an explicitly requested new science run:

    OPENBLAS_NUM_THREADS=1 python verify_bf2.py

The selected Git publication contains the exact core/tests/vendor plus this summary and concise metadata. The full ZIP additionally contains the scientific runner, saved-data validator, full Korean report, detailed DAG/contract, raw results, CAS records, logs, figures and manifest. Commands needing omitted files must run from the ZIP. Preserve the original archive; do not rerun historical science just for delivery.

14 unique pytest items passed. One successful numerical campaign,351 raw rows plus1 fine mixed diagnostic,251 analytic semigroup evaluations,new IVPs0,historical reruns0. A first Python invocation failed at parse time before any numerical work; one parenthesis was repaired. CAS first call used protected symbol Up; corrected symbol names yielded exact residuals. Original failure evidence retained. A covariance label was clarified to correlation without numerical rerun, since the current-frame velocity need not equal mean(beta).

Maximum covariance/decomposition/fine force/frame/pairwise/spatial-memory residuals are3.54e-17/4.89e-15/1.35e-14/5.77e-15/7.11e-15/6.60e-15. Algebra and continuum quadrature gates are separate; coarse normal grids at large beta are not promoted.

Fixed-gauge periodic reference domain, prescribed electron bath, cold bolometric Thomson only. No generic observer remap, spatial streaming PDE, Einstein feedback, spectral validity, production Rust, global positivity/tail theorem or mean-state closure. Native subagent and independent-model review NOT_RUN. Progress8/15 is scoped/source-mapped, not whole-project physical completion. Next BF3 first periodic spatial transport slice; no automatic execution.
