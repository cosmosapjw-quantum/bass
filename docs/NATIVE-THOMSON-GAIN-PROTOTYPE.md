# Opt-in frozen-frame Thomson gain prototype

This is a research-only primitive. Existing collision and coupled evolution routes do not call it. It is not an adaptive controller, a production-artifact admission, a conservation repair, or a boosted collision model.

## API

`bianchi_rustcore.modeb_thomson_log_gain(sph, rad, log_f, frame, order=8, tail="wien", kernel="thomson", v_b=None)` returns an independent flat array of log gain. `modeb_thomson_log_step` takes the same first four arguments, then `exposure`, and returns independent flat log occupations. `sph` and `rad` are existing `QSphere` and `QRadial` objects; `log_f` and row-major `frame` are contiguous one-dimensional float64 arrays. Tail is exactly `wien` or `powerlaw`. The latter names the high-energy extension; the low-energy extension is always affine in log energy.

The frame is fixed within both stages. Geometry is derived coherently from this one matrix: mu=|M qhat|, e=M qhat/mu, and source weight W=w det(M)/mu^3. Source b for destination i and native q_j is evaluated at log(q_j)+log(mu_i)-log(mu_b). Native shift argument is therefore log(mu_b)-log(mu_i). Occupation carries no additional mu amplitude factor.

The Thomson gain is the deterministic source sum W_b 3(1+(e_i dot e_b)^2)/(16 pi) times the interpolated occupation. Only gain is interpolated; native loss is the original cell occupation. Each complete gain reads one immutable stage, with fresh stage endpoint values for tail extension. Both gains and mixtures use log-sum-exp, with `-expm1(-exposure)` coefficients.

The stages are u=exp(-x/2)f+(1-exp(-x/2))G(f) and f_new=exp(-x)f+(1-exp(-x))G(u). Zero exposure returns the original logs bitwise in independent storage after structural and scope validation, without interpolation/gain evaluation.

## Numerical admission envelope

- Finite nonnegative exposure; finite log occupations with exactly sphere-size times radial-size elements.
- Thomson only; no velocity or exactly three finite zero components.
- Finite positive radial energies on a strictly increasing uniform logarithmic grid, at least two points at the Rust core level. Existing Python QRadial constructor requires four points.
- Interpolation orders 2 through min(16, number of radial points); no clamping.
- Finite nonsingular right-handed frame; Frobenius condition estimate ||M||_F ||M^-1||_F <= 1e8.
- Positive finite source weights and mapped norms; representable stencil offsets; finite interpolated values, sums, and outputs.

The condition cap is a deliberately conservative numerical prototype guard, not a physical Bianchi restriction or a theorem of accuracy for every admitted frame. Likewise the order cap is a bounded tested implementation envelope. Allowed input logs need not have directly representable exp(log f); finite log representation handles spectra beyond ordinary double occupation range. Any nonfinite intermediate causes an error without clipping, normalization, domain change, or fallback. Extremely large finite values can still be rejected honestly when intermediate arithmetic is unrepresentable.

## Claims and exclusions

The fixed-discretization frozen autonomous ODE f'=G(f)-f has second-order time accuracy under smoothness/stability assumptions. Native tests support exact zero identity, tiny-step continuity, cubic resolved local defects, quadratic global convergence, analytic pairwise agreement and positive finite represented logs.

This does not exactly preserve native finite-domain trapezoidal number or energy. Angular quadrature, pointwise radial interpolation and direction-dependent truncated physical-energy windows introduce separate errors. Constant physical spectra have a measurable angular equilibrium defect; it is retained, not row-normalized away. No infinite-tail convergence guarantee follows from finite-grid output.

Large x tends to G(G(f)), not the exact collision equilibrium projector. Positivity is not stiff accuracy, monotonicity, unconditional stability or a maximum principle. No boosted clock, evolving geometry, coupled Strang order, adaptive controller, or default-route replacement is admitted here.
