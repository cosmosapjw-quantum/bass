# Conditional extension: convex kinetic energy in diagonal non-LRS Bianchi I

**BASS theoretical extension only.** This is a constructive positive-source Hessian identity, not a claim that the current LRS FD96 Python evaluator supports non-LRS dynamics or off-diagonal stress.

For fixed conserved diagonal Bianchi-I canonical spatial momenta (q_i), take (a_i=a e^{\beta_i}), (sum_i\beta_i=0), metric signature (-,+,+,+), (w_i=q_i^2a^{-2}e^{-2\beta_i}\ge0), and (E=\sqrt{m^2+\sum_i w_i}). Directly:
```
∂_{beta_i} E = -w_i/E.
H_{ij} = ∂_{beta_i}∂_{beta_j}E = 2 delta_ij w_i/E - w_i w_j/E^3.
For any v, v^T H v = 2 sum_i w_i v_i²/E - (sum_i w_i v_i)²/E³.
Cauchy: (sum_i w_i v_i)² <= (sum_i w_i)(sum_i w_i v_i²).
So v^T H v >= [2-(sum_i w_i)/E²] (sum_i w_i v_i²)/E
                >= (sum_i w_i v_i²)/E >=0.
```
Thus the energy is convex in the three logarithmic scale directions and strictly convex on the physical tracefree 2-plane after integration over a positive distribution with full directional momentum support. The density derivative at fixed comoving volume is `δrho= -sum_i P_i δbeta_i`. On the tracefree plane, the unique convex minimum corresponds to isotropic *diagonal* principal pressures `P1=P2=P3`. Existence/coercivity needs a positive source with support in all three directions; do not assert existence for singular distributions confined to axes or pathological source tails. Off-diagonal stresses need reflection-even f0 or a consistent general tetrad/frame, otherwise a diagonal Einstein metric is not a consistent truncation.

Independent Wolfram symbolic 3×3 Hessian entry-by-entry returned nine exact zeros.

Manufactured numerical control only: finite positive reflection-even 3-axis photon/matter weight set [1.2,.8,1], mass m=3; 300 random 3D anisotropies in [-1,1], minimum sampled eigenvalue of constrained Hessian `0.10306462419936606 >0`. 2D constrained minimizer `beta=[0.1030087824801313,-0.11053199268847806,0.007523210208346759]`, `max|P_i-P_mean| projection=7.756015718562992e-09` (numerical BFGS accuracy), `rho_min=9.480082594771012` versus isotropic-coordinate `rho(0)=9.486832980505138`. The first finite-difference derivative probe with an overly strict absolute 2e-10 tolerance failed at 3.05e-10; a diagnosed binary64 finite-difference allowance 1e-9 passed. Neither this toy source nor its eigenvalues are PR164 physical FD96 outputs; the rigorous Hessian identity is source-independent.

Next BASS-only DAG: develop source-preserving non-LRS actual FD96 3-direction quadrature with tensor pressure, offdiagonal parity checks and 2D constrained convex minimization, **without** transplanting toy numbers into REI native production. Revisit BASS non-LRS original source before authorizing a 3D solver or general Bianchi class extrapolation.
