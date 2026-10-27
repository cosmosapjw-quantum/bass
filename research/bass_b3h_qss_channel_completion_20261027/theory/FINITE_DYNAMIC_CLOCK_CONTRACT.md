# Finite two-interface completion: source-channel maps, clock and bounded propagator

Theory selection for the new unit; no numerical experiment is reported here. Read ENERGY_MOMENT_AND_DIFFUSION_COMPLETION.md for the energy-moment derivation and explicit diffusion/Wien drive.

## 1. Recommended finite approximation

Use the two actual source endpoints to prepare a time-dependent, finite, two-interface channel model. Interpolate the non-Ly-alpha channel maps in proper time. Keep the Ly-alpha coefficient and its incoming field tied exactly to the native cosmological clock and the preserved finite-tube incoming measure.

This choice retains both actual endpoint meanings. Freezing all rate ratios to a common Ly-alpha activity clock is a valid smaller alternative, but it changes every non-Ly-alpha time profile. The proper-time construction is preferable when both endpoint operands are already available.

It is a finite completion of the effective source model, not a rerun of the original native history, a full de-eliminated atomic calculation, or an exact claim about the QSS right endpoint.

### 1.1 Construct channel maps before interpolation

At each endpoint, eliminate the 311 virtual radiation variables once, retaining their dependence on the two absolute real populations:

\[
 X_v(p)=a_v+B_vp.
\]

For an absolute-diffusion completion, obtain this map from the actual source blocks and the explicitly derived \(d=-T_{\rm diff}q\) correction. If the native Wien-omitted affine approximation is retained instead, label that choice and do not call its diffusion departure currents literal positive absolute microscopic currents.

Every selected gross physical channel at an endpoint is then an affine map

\[
 j_c^\pm(p)=a_c^\pm+\ell_c^\pm p.
\]

Here the signs identify the two event orientations, not positive/negative values of a single residual. Actual elementary propensities and the positive inverse of the virtual M-matrix produce the gross maps. Keep their atomic stoichiometry \(\nu_c\), bound-state energy change, radiation moment and gas/companion owner.

For non-Ly-alpha channels, interpolate \(a_c^\pm,\ell_c^\pm\) between the actual endpoints in proper time. With \(\theta=(t-t_0)/(t_1-t_0)\),

\[
 a_c^\pm(t)=(1-\theta)a_{c,0}^\pm+\theta a_{c,1}^\pm,\qquad
 \ell_c^\pm(t)=(1-\theta)\ell_{c,0}^\pm+\theta\ell_{c,1}^\pm.
                                                                  \tag{1}
\]

Because interpolation commutes with summation,

\[
 \sum_{c\ne\alpha}\nu_c[j_c^+(p)-j_c^-(p)]
       =b_{\rm nL}(t)-M_{\rm nL}(t)p.                              \tag{2}
\]

Constructing only interpolated Schur \(M,b\), and independently assigning incompatible interpolated channel rates afterward, would break this identity. Preparing the endpoint channel maps first avoids that inconsistency. It also preserves positivity by convex interpolation when the endpoint gross-map coefficients are nonnegative.

This reduced-map interpolation is the selected finite approximation. It need not equal recomputing every original raw rate at every interior time. Endpoint matches, positivity, stoichiometric identity and energy identity state what is actually preserved.

For the bound-free injection, the original \(n_Hx_ex_{\rm HII}\alpha_i\) background is a prepared coefficient over the step. The finite continuum and electron stocks are explicitly debited and checked; they are not unlimited reservoirs. Updating the rate's density feedback continuously would be a different nonlinear model. The prepared-coefficient step is meaningful only while its integrated finite inventories stay positive.

## 2. Native Ly-alpha clock identity

Let \(u=\eta-\eta_0\), \(a/a_0=e^u\), \(n_H(u)=n_{H,0}e^{-3u}\), and \(dt=du/H(u)\). Use the same defined effective opacity parameter \(g(u)>0\) in the atomic coefficient and the outgoing occupation:

\[
 R_\alpha(u)=\frac{{\rm LYA\_FACT}\,H(u)}{n_H(u)g(u)},\qquad
 f_{\alpha,\rm out}(u)=\frac{p_p(u)}{3g(u)}.                      \tag{3}
\]

The source input is the absolute incoming occupation, with the original distortion/background convention converted explicitly. The Ly-alpha atomic net downward current per hydrogen nucleus is

\[
 j_\alpha=R_\alpha[p_p-3g f_{\alpha,\rm in}].                    \tag{4}
\]

The two-state equation is

\[
 \frac{dp}{dt}
 =b_{\rm nL}(t)+3R_\alpha g f_{\alpha,\rm in}\,e_p
 -[M_{\rm nL}(t)+R_\alpha e_pe_p^T]p.                           \tag{5}
\]

The effective opacity \(g(u)\) can use an explicitly frozen endpoint interpolation; it remains distinct from the exact finite ground inventory defined in the companion report. Both sides of (3)-(5) must use that same \(g\).

With \(N_{H,0}=10^6n_{H,0}\) nuclei per reference cubic metre and \(G=3\times10^6{\rm LYA\_FACT}\),

\[
 N_{H,0}R_\alpha\,dt\,[p_p-3g f_{\alpha,\rm in}]
   =G e^{3u}\,du\,[f_{\alpha,\rm out}-f_{\alpha,\rm in}].         \tag{6}
\]

Equation (6) is exact for the chosen finite \(g(u)\). It prevents an inconsistent mixture of a frozen proper-time escape coefficient and the old expanding-face photon measure.

Do not freeze \(R_\alpha\) in proper time while retaining an unrelated \(G e^{3u}du\) measure. The small fractional coefficient variation does not make a broken clock identity exact.

### 2.1 Reuse the completed photon calculation as a baseline

Let \(f_{\alpha,\rm out}^{0}(u)\) be the exact represented outgoing occupation used in the completed finite result. Preserve its actual interpolation and conversion conventions. Define only the new correction

\[
 \delta f_{\rm out}(u)
 =p_p(u)/(3g(u))-f_{\alpha,\rm out}^{0}(u).
\]

Then

\[
 \delta N_0=G\int_0^h e^{3u}\delta f_{\rm out}(u)\,du,\qquad
 \delta U_0=G E_{21}\int_0^h e^{4u}\delta f_{\rm out}(u)\,du.    \tag{7}
\]

The \(e^{4u}\) factor transports event energy back to the left endpoint in the same convention as the completed tube. The new results are the preserved baseline plus (7); old tests, old quadrature and old transport need not be rerun.

At the right endpoint, transport the correction using the same already-defined B3g relation. Distinguish event energy \(E_{21}\delta N\) from energy after cosmological redshift transport and its geometry-work term.

## 3. A small stiff propagator with a controlled remainder

Write (5) as \(\dot p=b(t)-M(t)p\). The coefficients vary over a cosmological cell, while the two-interface relaxation is very fast. A direct explicit integrator over the full proper duration is inappropriate. A low-cost alternative exposes the quasi-steady solution and its finite-memory correction:

\[
 p_*(t)=M^{-1}(t)b(t),\qquad
 v(t)=-M^{-1}(t)\dot p_*(t).                                    \tag{8}
\]

On each smooth segment beginning at \(t_j\), set \(M_j=M(t_j)\). Let \(\widehat p_j\) be the carried numerical endpoint from the previous segment, with \(\widehat p_0=p_0\) at the original exact selected-model initial condition:

\[
 \begin{split}
 z_j&=\widehat p_j-p_*(t_j)-v(t_j),\\
 p_a(t)&=p_*(t)+v(t)+e^{-M_j(t-t_j)}z_j.
 \end{split}                                                   \tag{9}
\]

The segment initial condition is exactly \(\widehat p_j\); it need not equal the unknown exact trajectory at a restart. The computed trajectory has the explicit residual

\[
 r(t)=\dot p_a-[b-Mp_a]
      =\dot v+(M(t)-M_j)e^{-M_j(t-t_j)}z_j.                     \tag{10}
\]

This residual is a numerical approximation remainder. It is never entered as a physical refill channel.

If \(M\) is an M-matrix and its column sums are bounded below by \(\gamma>0\), then the induced one-norm logarithmic contraction satisfies \(\mu_1(-M)\le-\gamma\). For the exact selected-model solution and \(e=p_{\rm exact}-p_a\), carry an actual upper bound \(E_j\geq\|p_{\rm exact}(t_j)-\widehat p_j\|_1\), with \(E_0=0\) for the exact selected initial state. Then

\[
 \|e(t)\|_1
 \le e^{-\gamma(t-t_j)}E_j
       +\int_{t_j}^{t}e^{-\gamma(t-s)}\|r(s)\|_1ds.             \tag{11}
\]

and

\[
 \begin{split}
 \int_{t_j}^{t_{j+1}}\|e(t)\|_1dt
 &\le \frac{1-e^{-\gamma\Delta t_j}}{\gamma}E_j
   +\frac1\gamma\int_{t_j}^{t_{j+1}}
       [1-e^{-\gamma(t_{j+1}-s)}]\|r(s)\|_1ds\\
 &\le \frac{1-e^{-\gamma\Delta t_j}}{\gamma}E_j
   +\gamma^{-1}\int_{t_j}^{t_{j+1}}\|r(s)\|_1ds ,
 \qquad \Delta t_j=t_{j+1}-t_j .
 \end{split}                                                   \tag{12}
\]

For continuous numerical restart \(\widehat p_{j+1}=p_a(t_{j+1}^{-})\), propagate

\[
 E_{j+1}=e^{-\gamma\Delta t_j}E_j+
       \int_{t_j}^{t_{j+1}}
           e^{-\gamma(t_{j+1}-s)}\|r(s)\|_1ds .
 \tag{12a}
\]

If storing or resetting the endpoint introduces a known numerical mismatch bounded by \(\epsilon_{{\rm restart},j}\), add that quantity to the right side of (12a). The restart error is not set to zero merely because a new local initial-layer expression is used. Inherited physical/model uncertainty remains a separate object.

A selected channel row with \(\|\ell_c(t)\|_\infty\le L_c\) therefore has an integrated count error bounded by \(N_{H,0}L_c\) times the full segment bound (12), including the carry-in term. Sum these segment bounds with recurrence (12a). State, energy and photon-weighted bounds follow with their own explicitly bounded weights. A weighted norm can be used if ordinary column sums are not positive; do not assume a contraction constant that the actual matrix does not support.

These are bounds for the selected finite numerical model. They do not create a continuum physical uncertainty radius.

For coefficient profiles represented in \(u\), use \(\dot p_*=H p_{*,u}\) and \(\dot v=H v_{,u}\). Derivatives should follow the explicitly represented coefficient functions rather than differencing a near-cancelling RHS.

### 3.1 Resolve the initial layer without thousands of steps

The initial exponential is narrow in proper time. A cosmological-width quadrature can miss it completely. For a constant matrix \(M_j\), its first two moment integrals are

\[
 K_0(T)=M_j^{-1}(I-e^{-M_jT}),
\]

\[
 K_1(T)=M_j^{-2}[I-(I+M_jT)e^{-M_jT}].                          \tag{13}
\]

An affine proper-time channel coefficient \(L_0+L_1t\) thus integrates against the initial layer using \(L_0K_0+L_1K_1\), avoiding cancellation and missed support.

For the non-affine native Ly-alpha weight, use a small properly scaled initial-layer interval, for example a cutoff of \(80/\gamma\) or the full segment if shorter, with its explicit exponential tail bound. The actual numerical contract may choose an equivalent bounded method. Do not use cosmological-grid agreement as evidence that the fast layer has been integrated.

Incoming-history interpolation knots make derivatives piecewise smooth. Split at the preserved knots, enforce continuity of \(p\), and restart (9) with the incoming left limit as the next initial value. A jump in \(v\) must not be allowed to make the physical population jump.

### 3.2 Exactly affine forcing as an independent local identity

For constant nonsingular \(M\) and \(b(t)=b_0+b_1t\),

\[
 \begin{split}
 K&=p_0-M^{-1}b_0+M^{-2}b_1,\\
 p(t)&=M^{-1}(b_0+b_1t)-M^{-2}b_1+e^{-Mt}K,\\
 \int_0^T p\,dt
 &=M^{-1}(b_0T+\tfrac12b_1T^2)-M^{-2}b_1T
   +M^{-1}(I-e^{-MT})K.
 \end{split}                                                   \tag{14}
\]

The actual Wolfram repair call verified both the ODE identity and its initial condition. Equation (14) is an independent local propagator/control, not a claim that a varying \(R_\alpha(u)\) is constant.

## 4. Finite conservation and source-model distinctions

Integrate actual selected gross channel counts and their energies. Debits and credits use the same event count and endpoint energy/moment convention. Compute

\[
 \Delta N_{\rm atom}=\sum_c\nu_c(C_c^+-C_c^-)
\]

alongside the integrated trajectory. Finite storage is thereby tied to source-defined events. The residual from (10) is a separately bounded numerical discrepancy, not an invented source.

Large gross recombination/photoionization counts can cancel to a much smaller finite excited-storage change. Use high-precision accumulation or an equivalent compensated, analytically reduced formula. A balance tolerance scaled only by the largest gross count would not by itself demonstrate the tiny storage correction. Conversely, requiring byte equality of independently evaluated cancellation-prone outputs is inappropriate.

The selected dynamic endpoint generally differs from the original QSS endpoint. Preserve and display both. The original finite photon result remains an immutable baseline; (7) gives the new selected-model correction.

Ground and continuum stocks remain finite. The prepared background \(g_{\rm eff}=1-x_{\rm HII}\) is retained as the original opacity parameter, while exact atomic count conservation uses \(N_g=N_H-N_c-N_s-N_p\). These are named distinct quantities, not a hidden redefinition.

A complete selected event ledger can assign sector stress tensors and four-forces consistently. Gas/internal energy, radiation pressure, geometrical transport work and the four-force time component have distinct units and meanings. Their B3i representation must use the actual interface convention chosen by the parent contract. The successful bound-free operator can also be consumed as its own finite selected subunit; unrelated unselected continuum return loops do not become blanket prerequisites.

## 5. Stop rule and handoff to implementation

The new source/table construction, finite model choice, channel energy ownership, clock relation, bounded numerical method and one independent review are sufficient for this scoped research unit. No native rerun, old 512-cohort replay, old B3i consume, previous inverse/controls/plot, or added supplier census is implied by this note.

If actual coefficients fail positivity or a chosen error bound fails, classify that concrete failure and make one targeted repair or narrow to the successful bound-free finite operator. Do not turn an unselected spectral process into a permanent generic blocker.

Physical radii remain null. A finite-model numerical PASS is reported with its selected model and its actual remainder bounds.

