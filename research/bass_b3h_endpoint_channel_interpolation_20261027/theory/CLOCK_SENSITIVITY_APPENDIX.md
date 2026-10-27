# Implementation appendix: propagation of the new clock uncertainty

This requested implementation clarification adds no physical assumption, source gate, numerical run or review cycle. It closes the error propagation already required by the coding contract. Readback for this node: own branch research/bass-b3h-endpoint-channel-20261027 at6d66e0082da7120a844ea3538f51103ce5a5ce86; central7de02b3e05705ead4eeb313c8487a21d4e6876a6; AGENTS429a5a13ee75b1222bc50627f8d5973d01dd21c4. Existing agent status was inventoried.

## 1. Value and derivative errors are distinct

Let T_hat have a bound eps_T, T_-=T_hat-eps_T>0, and let a newly bounded partial primitive have value t_hat(u), error eps_t(u). For the exact selected theta=t/T,

eps_theta,0(u)
 <=eps_t(u)/T_-+|t_hat(u)|eps_T/(T_hat T_-).                (C1)

The exact selected endpoints theta(0)=0 and theta(h)=1 may be set directly. Their value error is zero; this does not make the derivative's denominator T exact.

The inverse-denominator error is

eps_(1/T)=eps_T/(T_hat T_-).                              (C2)

For ordinary-u Taylor coefficients (derivatives divided by n!),

theta_n=(1/H)_(n-1)/(n T), n>=1,

eps_theta,n <= |(1/H)_hat,(n-1)| eps_(1/T)/n
                 +eps_(1/H),(n-1)/(n T_-).              (C3)

The second term is the separately declared H/arithmetic evaluation allowance. Proper-time derivatives are simpler: D theta=1/T and D^n theta=0 for n>=2. Thus the nonzero clock-parameter derivative error is exactly (C2), not eps_theta,0 divided by an invented mesh spacing.

Pointwise quadrature error does not by itself bound derivatives of an arbitrary noisy interpolant. The implementation's analytic 1/H jets supply those derivatives; they are not finite differences of quadrature values.

## 2. Observable sensitivity to an analytic clock-profile perturbation

For a defined comparison profile theta_tilde with uniform value error eps_theta, write

C_M=||Delta M_n||_1, C_b=||Delta b_n||_1,
gamma_*=gamma-eps_theta C_M>0,
Q_theta=eps_theta(C_b+C_M Pmax).                         (C4)

Here gamma and Pmax bound the exact selected model. The logarithmic norm is Lipschitz in the matrix norm, so the comparison operator contracts at least at gamma_*. The comparison state and exact state share their initial condition. Their difference satisfies

E_clock(t)<=Q_theta[1-exp(-gamma_* t)]/gamma_*,

J_clock:=integral_0^T E_clock(t)dt
 <=Q_theta[T_+/gamma_*
        -(1-exp(-gamma_* T_+))/gamma_*^2],               (C5)

where T_+=T_hat+eps_T. This proof uses the exact p in the forcing perturbation delta b-delta M p; it does not require interpreting a balance residual as a source. For a simpler safe evaluation use J_clock<=T_+ Q_theta/gamma_*.

Since the interval is fixed in u, changing the numerical normalization T does not change H, dt=du/H, g, R_alpha or the integration endpoints. It only perturbs the non-Ly-alpha interpolation and the theta-dependent observable.

For k>=0 the population-moment perturbations obey

eps_I,k0 <=exp(kh) J_clock,

eps_I,k1 <=exp(kh)[(1+eps_theta)J_clock
                         +eps_theta Pmax T_+],

eps_I,alpha,k <=exp(kh) R_alpha,max J_clock.             (C6)

The direct-alpha row has no theta multiplier, so there is no separate delta-q term. Multiply the last line by N_H,0 for its downward photon-count contribution.

The scalar theta-weighted integral has a direct profile bound
eps_F,k1<=exp(kh)eps_theta T_+.
When using the exact selected identities F_00=T and F_01=T/2 instead, their new numerical errors are eps_T and eps_T/2; do not add the same normalization uncertainty again as a profile bound for those two identities.

The tagged-count sensitivities in A8 then propagate the chosen scalar/population moment bounds to counts and energy. The same endpoint energy factor is applied to the count and its error.

## 3. Two sound implementations; select one and avoid duplicate error

### A. Direct true-clock jet enclosure

Use (C1)-(C3) as value/jet evaluation enclosures for the exact selected theta. Propagate them through M,b,K,y_r,Psi_r and the observable integrands. Bound the analytic slow/adjoint remainder for the exact clock using the same T interval and complex-domain margins. Add the resulting evaluation errors at endpoint/boundary terms and at positive quadrature nodes.

This directly bounds the requested exact-clock formulas. Do not add (C5) as another contribution for the same already propagated T uncertainty. It may be recorded as an independent conservative sensitivity diagnostic.

### B. Analytic nominal normalization plus one model sensitivity

Define the auxiliary analytic profile theta_A(u)=t_exact(u)/T_hat. Its uniform distance from the exact theta=t/T is at most eps_T/T_hat on the actual interval. Use this epsilon in (C4)-(C6). Its analytic higher jets divide by T_hat exactly, so denominator error is part of this model sensitivity and is not separately charged to those jets.

Pointwise quadrature introduces only eps_t(u)/T_hat in theta_A's value at a node; carry that evaluation error through the computed jet algebra. Higher theta_A jets are the analytic 1/H jets/T_hat, not derivatives of pointwise quadrature noise.

If the implementation sets theta(h)=1 while differentiating with T_hat, the value1 is exact for the selected model but differs from theta_A(h) by at most eps_T/T_hat. Treat this as a bounded endpoint evaluation difference in routeB. It cannot be declared zero error relative to the nominal analytic profile.

Use gamma_* (and an enlarged forcing bound) for any auxiliary-profile residual certificate. It may extend slightly beyond theta in[0,1]; its purpose is error analysis, not a new physical positive-mixture definition. No clipping or extra physical channel is needed.

Either route closes the clock error. RouteA is the most direct match to exact theta endpoint shortcuts already in the code. RouteB offers the concise state/moment sensitivity in(C5)-(C6). Combining both as independent error contributions would be conservative but would double count the same parameter uncertainty; do not present that as two independent physical uncertainties.

## 4. Minimal finite jet-error algebra for routeA

No interval ODE solve is required. Track, for each Taylor coefficient, its nominal value and a nonnegative error in a compatible norm.

For products, with nominal coefficient norms B and errors eps,

eps_(FG),n <=sum_(i=0)^n [
 B_F,i eps_G,n-i+eps_F,i B_G,n-i
                    +eps_F,i eps_G,n-i].                (C7)

Addition sums errors. A u derivative multiplies coefficient(n+1) and its error by n+1. Proper differentiation is the already implemented product H*partial_u; use(C7).

Clock-only coefficient errors are

eps_M,n=C_M eps_theta,n,
eps_b,n=C_b eps_theta,n.                                (C8)

The direct Ly-alpha parts have no theta dependence. For q=exp(ku)theta I, use the same product rule. For q=exp(ku)I or exp(ku)R_alpha e_p^T, its clock-normalization error is zero.

For the inverse zeroth coefficient, if K_hat,0=M_hat,0^(-1) and
beta_0=||K_hat,0|| eps_M,0<1, then

eps_K,0 <=||K_hat,0||^2 eps_M,0/(1-beta_0).               (C9)

For n>=1 retain the existing ordered inverse recurrence

K_n=-K_0 sum_(i=1)^n M_i K_(n-i).                        (C10)

Use(C7) for its inner sum and final product to obtain eps_K,n. This is a finite recurrence through order3. Apply the same operations to the slow-state and adjoint recurrences; no new scientific evaluation is involved.

For a positive Gauss rule, pointwise integrand evaluation errors contribute

eps_Q,eval <=sum_l w_l eps_G(u_l),                        (C11)

with the actual positive, interval-scaled weights. Add its analytic truncation bound separately. Endpoint and adjoint boundary errors use the same product rule, including the carried p error. Constants/weights evaluated in ordinary MP retain their declared arithmetic allowance rather than being called exact interval values.

When a Neumann disk is centred at numerically evaluated M_hat(c), include the centre evaluation error:
beta_disk=||K_hat(c)||[eps_M,0(c)+Delta_M_disk]<1.
The corresponding inverse sup is ||K_hat(c)||/(1-beta_disk). This folds the clock uncertainty into the existing domain certificate; it is not an extra gate.

## 5. Interpretation of inherited input uncertainty

These new bounds apply to the newly computed T, theta and their use in the selected model. They do not certify the old saved incoming count/energy quadrature. That inherited remainder stays null and the relevant final count/energy bound remains conditional on the admitted saved values. The new clock error is finite and propagated; no physical eS/en/eE/geometry/total radius is thereby created.

