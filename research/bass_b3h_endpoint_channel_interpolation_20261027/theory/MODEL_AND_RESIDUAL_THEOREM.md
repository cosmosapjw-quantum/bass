# Endpoint-channel interpolation: finite native-clock model and residual theorem

## Result and scope

The selected model interpolates the two actual saved endpoint **proper-time gross channel maps**. It keeps the exact represented native Ly-alpha clock and incoming history. It interpolates each endpoint's energy-weighted channel as a tagged positive contribution. The resulting two-state equation is nonautonomous, positive and exponentially contractive when the explicit matrix conditions below pass. A second-order slow expansion with a short initial layer gives a bounded endpoint approximation. A separate adjoint integration identity gives cumulative counts and weighted energy without asking a cosmological quadrature to resolve the initial layer.

This is a new finite model of the admitted effective source. It is not a rerun of the native history or a proof that the dynamic endpoint equals the original QSS endpoint. The prior left-ratio model, its photon results, source operands, tests, consume, plot and physical claim boundary remain immutable.

Entry readback: BASS source/delivery 1e8d7ecc90a304fcd1ddf3ea9a98ad14f88248a0; central 42cc3a909688d670200ba09c500e2ca83a94fa10; central AGENTS blob 429a5a13ee75b1222bc50627f8d5973d01dd21c4. Four existing agents were inventoried. Scientific execution is delegated; this file reports derivation, not a numerical outcome.

## 1. Definitions and actual endpoint inputs

Let p=(p_s,p_p)^T denote the two absolute interface fractions per hydrogen nucleus. The 311 virtual variables are radiation proxies, not additional atomic levels. The admitted source construction and energy ownership are in the preceding unit's theory/ENDPOINT_CHANNEL_MAPS.md and ENERGY_MOMENT_AND_DIFFUSION_COMPLETION.md.

For each non-Ly-alpha directed gross channel c and source endpoint k in {0,1}, the actual source preparation gives

j_ck(p)=a_ck+ell_ck p,   a_ck >= 0,   ell_ck >= 0.

Rates are events per hydrogen nucleus per proper second. Keep the four-stock stoichiometry nu_c (ground,2s,2p,ion), the fixed source identity, and the energy vector e_ck (atomic internal, gas, ambient radiation, selected Ly-alpha). In particular sum_s e_ck,s=0. The per-event bound-free kinetic moments are the already admitted positive source moments, not newly differenced rate-table values.

The left normalized maps are reused by multiplying by their saved left R_alpha,0. A right builder that internally normalizes must use the right endpoint's own n_H and then denormalize. The earlier left-only builder's common reference n_H is not the right local density.

Let u=eta-eta_0, 0<=u<=h. Define the new, bounded native proper-clock primitive

t(u)=integral_0^u H(v)^(-1) dv,
T=t(h),
theta(u)=t(u)/T.                                             (1)

Thus theta(0)=0 and theta(h)=1 by definition. A new bounded partial-clock calculation is required for this new model. The old saved duration is comparison evidence; it is not silently promoted from an old numerical acceptance tolerance to an exact quadrature value.

Use the same actual H, common n_H,0, source g(u)>0, and incoming alpha occupation as the completed finite tube:

n_H(u)=n_H,0 exp(-3u),
R_alpha(u)=LYA_FACT H(u)/(n_H(u) g(u)),
g(u)=g_0+(g_1-g_0)u/h.                                      (2)

Source constants lifted from saved binary64 values are fixed inputs. Tiny arithmetic differences between a source's original endpoint calculation and the shared-clock representation are numerical parity questions, not new physical uncertainty radii.

## 2. Convex channel model and the tagged energy choice

The final selected proper-time channel is

j_c(t,p)=(1-theta) j_c0(p)+theta j_c1(p).                     (3)

Preserve the two tagged counts separately:

C_c0=N_H,0 integral (1-theta)j_c0(p) dt,
C_c1=N_H,0 integral theta j_c1(p) dt,
C_c=C_c0+C_c1.                                               (4)

Their energy transfer is

U_cs=N_H,0 integral [(1-theta)e_c0,s j_c0(p)
                     +theta e_c1,s j_c1(p)] dt.             (5)

All tags have nonnegative propensities. Each tag carries its own actual endpoint moment and the established physical owner. The interpolation is a positive mixture of endpoint effective channel kernels. It does not assert an interior single-temperature detailed-balance relation or a recomputed native interior rate table.

The alternative e_c(theta)j_c(theta), with per-event moments independently interpolated, would introduce theta^2 cross terms and is not selected. When e_c0 differs from e_c1, it is not equal to (5). The conditional mean energy of the selected mixture is rate-weighted, [w0 e0 j0+w1 e1 j1]/[w0 j0+w1 j1] when the denominator is nonzero.

Because every endpoint's virtual steady identity is an affine identity in the same p, convex interpolation of its complete edge and boundary ledger preserves that identity. An interior interpolated gross map need not factor as one newly solved virtual occupation times one interpolated raw rate. No interior virtual solve is implied.

Obtain b_n,k and M_n,k by summing the same endpoint gross-map stoichiometry, then interpolate:

b_n(t)=(1-theta)b_n,0+theta b_n,1,
M_n(t)=(1-theta)M_n,0+theta M_n,1.                           (6)

Do not construct M from one interpolation convention and attach channel counts from another.

Let e_p=(0,1)^T and P=e_p e_p^T. The two real-state ODE is

dp/dt=b(t)-M(t)p,
b=b_n(t)+3 R_alpha(u)g(u) f_alpha,in(u)e_p,
M=M_n(t)+R_alpha(u)P.                                       (7)

The initial p(0) is the saved absolute population. The selected absolute-diffusion completion may relax away from it in a short layer. The right source endpoint specifies the right channel coefficients; it does not prescribe p(T).

In native activity s=int R_alpha dt, the same equation is

dp/ds=b/R_alpha-(M/R_alpha)p.                              (8)

The activity matrix is variable. No commutation of its values at different times is assumed. Proper-time differentiation is especially convenient because the non-Ly-alpha maps in (6) are affine.

## 3. Native Ly-alpha finite-measure identity

The selected upward and downward rates remain

j_alpha,down=R_alpha p_p,
j_alpha,up=3 R_alpha g f_alpha,in,
f_alpha,out=p_p/(3g).                                      (9)

For the same common volume and G=3*10^6*LYA_FACT,

N_H,0 R_alpha dt [p_p-3g f_alpha,in]
 =G exp(3u)du [f_alpha,out-f_alpha,in].                    (10)

The pulled-back energy has the additional exp(u) factor. Equation (10) is exact for the chosen common clock and g; freezing R_alpha in proper time while keeping the old face measure would break it.

The prior outgoing and incoming finite result is an immutable baseline. A new selected-model difference is a model difference, not the old result's numerical error. Old incoming count and pulled-back-energy values may be used as admitted scalar inputs, with their prior quadrature remainder still unknown. New numerical bounds are conditional on those admitted values unless an additional, explicitly authorized source uncertainty is supplied.

## 4. Positivity, contraction and finite population bounds

For every real time require the actual matrix to have M_12<=0, M_21<=0, and column sums at least gamma>0. Since M_n is affine and R_alpha is positive, a sufficient computable certificate is

gamma=min_j { min_k sum_i (M_n,k)_ij
                      +delta_jp inf_u R_alpha(u) } > 0.    (11)

The signs of M_n off-diagonal entries need only be checked at the two endpoints. The actual assembled endpoint matrices, not a source-QSS matrix with incompatible gross maps, supply this test.

For the induced one-norm, mu_1(-M)<=-gamma. Therefore its exact nonautonomous evolution U(t,s) obeys

||U(t,s)||_1 <= exp[-gamma(t-s)], t>=s.                    (12)

This follows directly from the one-norm differential inequality and does not require diagonalization or commuting matrices. Since -M is Metzler and b>=0, the exact p is nonnegative. If B>=sup||b||_1, then

||p(t)||_1 <= Pmax=max(||p(0)||_1,B/gamma).                (13)

A useful component lower bound is
p_i(t)>=min[p_i(0), inf b_i/sup M_ii] when the second entry is positive, obtained by dropping nonnegative inflows from the other component. This can certify whole-interval positivity without sampling a cosmological grid.

Finite continuum, ground, electron, gas and radiation stocks are separately checked from the integrated tagged event counts. Prepared rate coefficients are not unlimited donors. Retain the exact-count ground N_g=N_H-N_ion-N_s-N_p and the distinct source opacity g_eff=1-x_HII. Retain the source's recoil-free direct-alpha model and its explicitly owned diffusion heat.

## 5. Slow expansion with variable M

Let D=d/dt=H(u)d/du and K=M^(-1). On a segment with a fixed incoming-history affine piece, define

y_0=K b,
y_(r+1)=-K D y_r,
P_q=sum_(r=0)^q y_r.                                      (14)

For any finite q,

D P_q-b+M P_q=D y_q.                                     (15)

This telescoping identity is exact for varying, noncommuting M. The selected low-cost order is q=2 unless the actual frozen numerical contract selects otherwise. Smallness is certified by the actual remainder; it is not inferred merely from a scale-separation label.

Analytic differentiation must include

D K=-K(D M)K.                                            (16)

Repeated derivatives can be built without finite differences:

D^n K=-K sum_(k=1)^n binom(n,k)(D^k M)(D^(n-k)K).          (17)

Alternatively the triangular derivative recurrences are

D^n y_0=K[D^n b-sum_(k=1)^n binom(n,k)(D^k M)D^(n-k)y_0],

D^n y_r=K[-D^(n+1)y_(r-1)
          -sum_(k=1)^n binom(n,k)(D^k M)D^(n-k)y_r], r>0.  (18)

The non-Ly-alpha pieces have first derivatives Delta b_n/T and Delta M_n/T and zero higher proper-time derivatives. The remaining derivatives come from the explicitly represented H,g,R_alpha and incoming PL-plus-Wien function. At an incoming knot use one-sided analytic derivatives; the physical p stays continuous.

## 6. Initial layer, restart and a finite-memory remainder

At segment start t_j set M_j=M(t_j), take the carried numerical value p_hat_j, and let

z_j=p_hat_j-P_q(t_j),
h_j(t)=exp[-M_j(t-t_j)]z_j,
p_a(t)=P_q(t)+h_j(t).                                    (19)

The segment starts at p_hat_j exactly. Its residual is

r_j=D p_a-b+M p_a
   =D y_q+(M(t)-M_j)h_j(t).                              (20)

This residual is numerical error only. It is never an actual physical refill channel and never enters the event ledger as a new owner.

Let E_j>=||p_exact(t_j)-p_hat_j||_1. Let
epsilon_j>=sup||D y_q||_1,
L_j>=sup||D M||_1,
Z_j>=||z_j||_1,
and use a common contraction lower bound gamma also valid for M_j.
For tau=t-t_j,

||r_j||_1<=epsilon_j+L_j Z_j tau exp(-gamma tau).

Then a direct convolution of (12) yields

||p_exact(t)-p_a(t)||_1
 <=exp(-gamma tau)E_j
   +epsilon_j[1-exp(-gamma tau)]/gamma
   +(L_j Z_j/2)tau^2 exp(-gamma tau).                    (21)

For segment length Delta, a safe integrated error is

integral ||p_exact-p_a||_1 dt
 <= E_j[1-exp(-gamma Delta)]/gamma
  + epsilon_j[Delta/gamma
               -(1-exp(-gamma Delta))/gamma^2]
  + L_j Z_j/gamma^3
       [1-(1+gamma Delta)exp(-gamma Delta)].             (22)

The last expression bounds the integrated layer residual by dropping a positive endpoint factor in the residual convolution. It is a safe upper bound, not a claim of equality.

Carry

E_(j+1)=right-hand side of (21) at Delta
         +epsilon_restart,j+epsilon_omission,j
         +epsilon_endpoint_arithmetic,j.                (23)

Only the original selected exact IC has E_0=0. Restarting at a new incoming knot never resets accumulated error to zero. If an initial exponential is omitted at a late endpoint, add its certified norm bound Z_j exp(-gamma Delta). Use its logarithm to decide omission; underflow is not a proof.

Equation (12) also gives a finite-memory statement: any uncertainty E_old from a time L earlier contributes at most exp(-gamma L)E_old. A selected cutoff L=lambda/gamma has explicit exp(-lambda) memory loss. One may truncate a numerically represented layer only with this bound retained.

For endpoint computation this construction needs no long stiff time march. For integrated observables use the separate adjoint identity below; it includes the layer through actual endpoint terms.

## 7. Local numerical limits and physical claim boundary

The final coding contract must record endpoint residual, endpoint carry, integrated/observable remainder, new clock/quadrature remainder and arithmetic allowance separately. MP precision by itself is not a rigorous rounding certificate. If ordinary MP arithmetic is used with a declared allowance, the numerical theorem is conditional on that allowance.

A practical proposed target is an endpoint fraction bound no larger than 1e-34 and a final tiny excited-stock conservation error bound no larger than 1e-16 nuclei per common reference cubic metre. These are recommendations for the root's frozen contract, not already observed passes. The latter should also be reported relative to the actual nonzero storage, so a gross-scale cancellation test cannot conceal it. If a concrete propagated bound is larger, report that bound and its source before changing order or precision.

All physical eS/en/eE/geometry/total radii remain null, L4 remains false, and an unknown historical budget remains unknown. A successful selected finite-model computation neither supplies unselected continuum loops nor requires them as a blanket gate.

## 8. Independent symbolic and literature support

The new actual Wolfram call used a polynomial 2x2 noncommuting matrix example. It returned zero for (15), the layer residual (20), inverse derivative (16), and the two-term adjoint pointwise identity; the noncommutator witness was {{0,x},{-2x,0}}, so the check did not accidentally assume commuting matrices. The generic proofs are the explicit algebra above and in ADJOINT_MOMENT_CERTIFICATE.md. No BASS scientific data were evaluated by that call.

Primary comparison:
- Gustaf Soderlind, "The logarithmic norm. History and modern theory", BIT46 (2006)631-652, DOI10.1007/s10543-006-0069-9. Author publication page and publisher metadata were actually read. The one-norm formula and nonautonomous bound used here are also derived directly in Section4.
- Tobias Jawecki, Winfried Auzinger and Othmar Koch, "Computable upper error bounds for Krylov approximations to matrix exponentials and associated phi-functions", https://arxiv.org/html/1809.03369, published BIT with DOI10.1007/s10543-019-00771-6. The primary full-text defect representation and logarithmic-norm assumption were actually read. We reuse the residual-to-error principle, not their Krylov implementation or a claim that their constant-matrix theorem alone proves this variable-matrix construction.
- Fredrik Johansson and Marc Mezzarobba, "Fast and rigorous arbitrary-precision computation of Gauss-Legendre quadrature nodes and weights", SIAM J.Sci.Comput.40(6)(2018)C726-C747, DOI10.1137/18M1170133. Actual primary manuscript: https://inria.hal.science/hal-01705612/file/legendre.pdf. It distinguishes rigorous quadrature-node/weight enclosures from unvalidated high precision. The simple positive-Gauss/Cauchy bound in the companion note is proved explicitly for this unit.

