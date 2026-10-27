# Saved native radiation traces identify endpoint effective-H populations

## Scope and result

This is a constructive theory return for the native HyRec cell `[5126,5127]`. It derives an inverse of the **already stored** incoming, bin-average, and outgoing virtual-radiation traces. A nonzero resolved jump identifies the bin optical depth; an independently known source coefficient then identifies `x1s`. The stored optically thick Ly-alpha trace identifies the absolute source-effective `2p` population. A non-diffusing virtual bin or the stored Ly-beta/gamma traces also identifies the source-effective `2s` population.

These are endpoint state reconstruction claims. They do not by themselves identify a continuously evolved excited-state storage term, turn the original thick-line closure into an exact finite-tau solver, or supply a physical non-Ly-alpha refill energy owner. The finite QSS storage defect is derived below so that the next executable unit can report it rather than silently absorb it into a reservoir.

No native solver, prior test, prior consume, prior plot, or old 512-cohort calculation was rerun by this theory work. The original central DAG remains **27/88** before root admission of any new unit. Physical `eS`, `en`, `eE`, geometry, temporal, and total radii remain `null`. Unknown remaining budgets remain unknown.

## 1. Source and preflight

Live refresh at `2026-10-27 10:37:26 UTC` found:

| Surface | Observed identity |
|---|---|
| BASS `research/bass-b3h-native-tube-20261027` | `29dcf5ab94ae8b84bf8e3f31dddb31ce719929b1` |
| REC `research/rec-source-synthesis-20261027` | `d6dbe39a4923439547c01695d9020ba39367ea90` |
| Central `research/orchestration-sandbox-20261022` | `55202663275cd0607c968129b33de805d06f5d8b` |
| Central `AGENTS.md` blob | `429a5a13ee75b1222bc50627f8d5973d01dd21c4`, unchanged from the fully read policy |

The root, source-intake agent, and this theory agent were active; the backup inventory agent had completed its read-only inventory. The current central commit must be preserved, including the earlier CR_N5 result. Root owns subsequent expected-SHA non-force publication and actual backup ACKs.

The original `HyRec/hydrogen.c` was extracted from the stored original archive, not inferred from a later derivative. The exact local copy is `hydrogen_original.c`, 37,471 bytes, SHA256 `421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b`. The derivative vendor copy has one extra trailing byte; its mathematical source content through the original EOF agrees. This is a typed packaging difference, not a scientific discrepancy.

The history is `data/pr05b2_source_history_v060.npz`, SHA256 `d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1`. The source-intake packet `NATIVE_VIRTUAL_TRIPLE_TRACE_5126_5127.json`, SHA256 `7d6e85bf2e759500d3e7d7249de5892bcc34ce7af77f08de10ae1607eacf19ef`, contains the exact selected traces and original tables. Its right snapshot `x1s` is validation-only, never an inversion input. The separate all-Lyman endpoint packet has SHA256 `5a01a3dfab10f07450c828e0ca141a8dc69f40e713a57b71aae378c41e1ed8f3`.

## 2. What the original virtual-bin equations imply

Write native departure occupations in one bin as

\[
i=\Delta f_{\rm in},\qquad o=\Delta f_{\rm out},\qquad
v=\overline{\Delta f},\qquad s=\Delta f_{\rm eq}.
\]

The common Wien reference cancels in all differences below. In the original standard exponential branch, define

\[
A(\tau)=1-e^{-\tau},\qquad P(\tau)=A(\tau)/\tau.
\]

`populateTS_2photon` sets `Tvv_diag = Gamma/(1-P)` and `sv = Tvv_diag*x1s*i*P`. The solved virtual row and the outgoing update therefore imply

\[
o=i+A(s-i),\qquad v=P i+(1-P)s. \tag{1}
\]

This relation also holds in a diffusion bin if the effective source `s` includes the actual neighboring terms. The selected non-diffusion bins avoid the additional unknown matter-temperature dependence of their opacity coefficients.

For `D=o-i != 0`, eliminate the source `s`:

\[
r\equiv\frac{v-i}{o-i}
=F(\tau)\equiv\frac{1}{1-e^{-\tau}}-\frac1\tau
=\frac12+\frac12\coth\frac\tau2-\frac1\tau. \tag{2}
\]

The derivative is

\[
F'(\tau)=\frac1{\tau^2}-\frac1{4\sinh^2(\tau/2)}>0\quad(\tau>0), \tag{3}
\]

because `sinh(tau/2)>tau/2`. Together with `F(0+)=1/2` and `F(infinity)=1`, this proves that a consistent `r` strictly between `1/2` and `1` determines exactly one positive optical depth. This is an elementary inverse-transfer identity specialized here to the actual native saved arrays; no claim of a new general radiative-transfer theorem is needed.

If `D=0`, all three traces may equal the source for every optical depth. An unresolved jump therefore fails this particular inverse, not every possible source reconstruction. If `r` lies outside its admissible range, do not clip it into the range. Check trace convention, original interpolation arithmetic, floating-point error, and source identity.

### Exact small-tau branch qualification

The original C code uses, for `0<tau<=1e-6`,

\[
A_C=\tau-\tau^2/2,\qquad (1-P)_C=\tau/2-\tau^2/6.
\]

Consequently its idealized arithmetic ratio on that branch is

\[
F_C(\tau)=\frac{1/2-\tau/6}{1-\tau/2},
\]

not exactly (2). For `tau<=1e-30` the outgoing update simply preserves the incoming trace. The chosen primary bin `273` has saved right-endpoint `tau=1.1076274318532195`, far above these branches. All selected right-endpoint cross-check bins also use the exponential branch. The inferred left endpoint must be checked to use the same branch before applying (2).

## 3. Stable inversion and its numerical meaning

For moderate optical depth evaluate `A=-expm1(-tau)` and `F=1/A-1/tau`. Near zero use the expansion

\[
F(\tau)=\frac12+\frac\tau{12}-\frac{\tau^3}{720}
+\frac{\tau^5}{30240}-\frac{\tau^7}{1209600}
+\frac{\tau^9}{47900160}+O(\tau^{11}). \tag{4}
\]

Its derivative starts `1/12-tau^2/240+tau^4/6048-tau^6/172800`. For small `s=r-1/2`, an initial inverse estimate is

\[
\tau=12s+\frac{144}{5}s^3+\frac{19008}{175}s^5
+\frac{393984}{875}s^7+O(s^9). \tag{5}
\]

For large optical depth,

\[
F(\tau)=1-\frac1\tau+\frac{e^{-\tau}}{1-e^{-\tau}}, \tag{6}
\]

so `1/(1-r)` supplies an asymptotic inverse estimate. A bracketed monotone root solver avoids branch ambiguity. The small-tau formulas (4)-(5) are analytic formulas for (2), not permission to replace the original C small-tau branch when reproducing that branch.

The absolute inverse condition number is `1/F'(tau)`, approaching `12` at small tau and growing like `tau^2` at large tau. The relative condition number with respect to `r` is

\[
\kappa_r=\frac{|r|}{\tau F'(\tau)},
\]

which grows like `6/tau` near zero and like `tau` at large tau. The raw jump matters independently of this scalar condition number. If measured `Bhat=v-i`, `Dhat=o-i` have certified arithmetic uncertainty bounds `epsilon_B`, `epsilon_D`, and `|Dhat|>epsilon_D`, then

\[
|r-\hat r|\le
\frac{\epsilon_B+|\hat r|\epsilon_D}{|\hat D|-\epsilon_D}. \tag{7}
\]

On an enclosing optical-depth bracket whose minimum derivative is `m>0`, the propagated inversion bound is `epsilon_tau<=epsilon_r/m`. Equivalently invert the two ratio interval endpoints, using monotonicity. The interval must state which uncertainties it encloses: trace rounding, scalar inverse error, and coefficient arithmetic. It does not automatically enclose original linear-solver backward error, the QSS approximation, between-knot evolution, or physical modeling error.

A high-precision inverse should start from the exact binary64 input values, not rounded printed decimal strings. Its purpose is an independent numerical representation check. A final accepted value is the primary bin's reconstruction; the other bins remain independent diagnostics, not samples to average away disagreement or bad conditioning.

## 4. Mapping the inverse to absolute effective-H state

The original source defines

\[
\tau_b=\Gamma_b x_{1s}\,K_b,\qquad
K_b=\left(\frac{h_Pc}{E_b f_{\alpha}^2m_e^R}\right)^3
\frac{n_H}{8\pi H},\qquad
x_{1s}=\frac{\tau_b}{\Gamma_bK_b}. \tag{8}
\]

Here `hPc` has units eV cm, `nH` is in cm^-3, and `H` in s^-1. `TR` is the original rescaled radiation temperature in eV. At the selected native cosmology `fsR=meR=1`. Retain the original operation order and constants when reproducing the source background.

For the selected non-diffusion bins define

\[
C_s=\frac{f_{\alpha}^8m_e^R A_{2s,b}}
 {|e^{(E_b-E_{21})/T_R}-1|},
\]

\[
C_p=\frac{f_{\alpha}^8m_e^R}{3}
\left[\frac{e^{-E_{32}/T_R}A_{3s3d,b}}
 {|e^{(E_b-E_{31})/T_R}-1|}
+\frac{e^{-E_{42}/T_R}A_{4s4d,b}}
 {|e^{(E_b-E_{41})/T_R}-1|}\right].
\]

Then `Tvr_s=-Cs`, `Tvr_p=-Cp`, and

\[
\Gamma_b=e^{(E_b-E_{21})/T_R}(C_s+3C_p). \tag{9}
\]

The source-intake selection is primary `b=273`, with independent checks `272,267,268,269,309`. All are outside the source diffusion range `[100,180)`. Source A2s normalization changes only bins below 140; it does not change these raw table rows. At primary bin 273 the right snapshot reports `Gamma=6.084185653162193 s^-1`, `i=3.0794164835544322e-18`, `v=3.481839162529577e-18`, and `o=3.760947705334913e-18`. These saved numbers motivated selection before inversion. The source-intake agent independently reconstructed the right incoming traces with the original native clock/query operation order and obtained bit-for-bit agreement with the stored snapshot for all six bins.

The original native Ly-alpha closure explicitly assumes an optically thick line:

\[
d_\alpha\equiv\Delta f_{\alpha,\rm out}
=\frac{x_{r,p}}{3x_{1s}}.
\]

Thus the recovered absolute source-effective upper fraction is

\[
x_{2p}=3x_{1s}\left[d_\alpha+e^{-E_{21}/T_R}\right]. \tag{10}
\]

Its finite optical depth can now be diagnosed from

\[
R_\alpha=\frac{\mathrm{LYA\_FACT}\,H}{n_Hx_{1s}},\qquad
\tau_\alpha=\frac{A_{\rm effective}}{R_\alpha}.
\]

This diagnostic does not change the fact that the stored outgoing Ly-alpha history was generated with the original thick-line update.

### The same bin also identifies 2s

With no neighboring diffusion term, the effective source recovered from (1) is

\[
s=i+\frac{o-i}{A},\qquad
\Gamma_b s=C_s\frac{x_{r,s}}{x_{1s}}+
C_p\frac{x_{r,p}}{x_{1s}}.
\]

Let `yp=3*d_alpha`. If `Cs!=0`,

\[
y_s\equiv\frac{x_{r,s}}{x_{1s}}
=\frac{\Gamma_b s-C_p y_p}{C_s},\qquad
x_{2s}=x_{1s}\left[y_s+e^{-E_{21}/T_R}\right]. \tag{11}
\]

The numerator in (11) may suffer cancellation; record its condition separately. For example, with independently bounded factors, an absolute uncertainty estimate before division includes `|Gamma| epsilon_s + |s| epsilon_Gamma + |Cp| epsilon_yp + |yp| epsilon_Cp`, plus product cross terms. A small `Cs` or cancellation can make this a poor numerical route without changing the algebraic identity.

There is also an independently stored source relation:

\[
y_s=d_\beta e^{E_{32}/T_R}=d_\gamma e^{E_{42}/T_R}. \tag{12}
\]

It follows directly from the original Ly-beta/gamma outgoing assignments. These two estimates can validate (11), with their own floating-point propagation. The all-Lyman endpoint extraction supplies both traces without rerunning the source.

### Population convention must remain explicit

The source defines `x1s=1-xHII`, without subtracting the tiny excited-state fractions. Therefore `x1s+xHII+x2s+x2p` is not exactly one. The recovered numbers are the absolute populations in the source's **effective-H convention**, not an exact microscopic normalized population partition. The excess of this sum and the finite QSS storage defect below are different quantities. Redefining `x1s` to force exact normalization would change the source closure and must not be hidden inside reconstruction.

## 5. The finite QSS storage defect

Use the already admitted common material volume: `V(t)/V0=exp(3u)`. Its total effective-H normalization per reference volume is constant, `N_H0=nH_ref` in m^-3. Let

\[
N_p^*(t)=N_{H0}x_{2p}^*(t)
\]

be the algebraically reconstructed upper inventory. Let `D(t)` be cumulative net Ly-alpha downward events per `V0`, and `B_p(t)` cumulative non-Ly-alpha contribution to the same upper inventory. An actual finite population balance would obey

\[
N_p(t)-N_p(t_0)=-D(t)+B_p(t). \tag{13}
\]

The native real-state algebraic row instead sets its instantaneous source terms to balance. In the original departure notation, the non-Ly-alpha upper fraction rate is

\[
\begin{aligned}
b_p^*={}&n_H(s_{\rm Saha}x_{1s}\,\Delta\alpha_p
+\alpha_p\Delta x_e^2)-\beta_p x_{r,p}\\
&+R_{ps}(3x_{r,s}-x_{r,p})
+\sum_b\left(T_{vr,pb}x_{r,p}-T_{rv,pb}x_{v,b}\right).
\end{aligned} \tag{14}
\]

The QSS row gives

\[
b_p^*=d_p^*\equiv
R_\alpha(x_{r,p}-3x_{1s}d_{\alpha,\rm in}). \tag{15}
\]

Equation (14) names actual source-network terms. They may be exported or reconstructed when their actual operands are available; this formula does not license arbitrary rates. Integrating (15) predicts zero change from the net balanced channels. The exact residual for the algebraic endpoint inventory is therefore

\[
\begin{aligned}
S_p(t)&\equiv N_p^*(t)-N_p^*(t_0)+D^*(t)-B_p^*(t)\\
&=N_{H0}\left[x_{2p}^*(t)-x_{2p}^*(t_0)\right]
\quad\text{when (15) is used pointwise}. \tag{16}
\end{aligned}
\]

This is a finite storage defect of the QSS elimination. It is not a physical refill simply because it has units of atom count. In particular, `x2p=xr_p+3*x1s*exp(-E21/TR)` means the storage change includes the moving Wien reference. Differentiating or differencing `xr_p` alone would omit a real part of the absolute source-effective inventory change.

For an explicit finite algebraic bookkeeping complement, the signs are

\[
B_p^{\rm alg}=\Delta N_p^*+D,
\qquad B_{1s}^{\rm alg}=\Delta N_{1s}^*-D. \tag{16a}
\]

In the upper row, `B_p^alg=B_p^QSS+DeltaN_p*` when the represented instantaneous QSS channel balance is used. The first term is the named native network contribution; the second is the source algebraic refresh. Equations (16) and (16a) are useful finite diagnostic outputs even before channel energies are available. They must not be advertised as an independently measured physical source solely because the total closes. With the ground state as zero internal-energy reference, the selected direct line gives `-E21,J*D` to atomic internal energy. The upper algebraic refresh adds `E21,J*DeltaN_p*` to bookkeeping; its physical energy counterpart remains an owner question. Inclusion of `2s`, continuum, or thermal sectors requires their corresponding energy accounting rather than reusing this one upper-state expression for the whole matter sector.

The endpoint defect can now be measured constructively from recovered states. Identifying the full physical refill energy still requires either actual source channel energy accounting or a declared dynamic extension. There is no need to require unrelated future providers before doing endpoint recovery or the net radiation subunit.

## 6. A derived algebraic refresh owner and a conditional dynamic extension

The 313-dimensional original solve contains two real atom states and 311 virtual radiation states. It must not be promoted wholesale into a 313-level atomic ODE. Eliminating its virtual block gives

\[
M=T_{rr}-T_{rv}T_{vv}^{-1}T_{vr},\qquad
s_{\rm eff}=s_r-T_{rv}T_{vv}^{-1}s_v,
\]

\[
z^*=M^{-1}s_{\rm eff},\qquad
p^*=z^*+q,\qquad
q=x_{1s}e^{-E_{21}/T_R}(1,3)^T. \tag{17}
\]

The update between two source parameter states is explicitly

\[
z_1^*-z_0^*=M_1^{-1}
\left[(s_1-s_0)-(M_1-M_0)z_0^*\right], \tag{18}
\]

and `p1*-p0*` includes `q1-q0`. Equation (18) identifies an **algebraic parameter refresh** that is more informative than merely naming a balance residual. If an algorithm chooses to carry algebraic populations as inventories, this update contributes `N_H0*(p1*-p0*)` and, for fixed level energies epsilon, `N_H0*epsilon dot (p1*-p0*)` to its storage bookkeeping. These are finite, computable algorithmic increments. They are not evidence for a physical reservoir that actually supplied those atoms or that energy. Such an owner must be labeled as an approximation/projection owner, not silently admitted as physical matter four-force.

A constructive alternative is to declare a dynamical extension of the reduced real-state system. Conditional on a valid frozen-bath kinetic interpretation, stable invertible `M(t)`, and a specified initial state, take

\[
\dot p=s_{\rm phys}-Mp,\qquad
s_{\rm phys}=s_{\rm eff}+Mq.
\]

The difference `y=p-p*` then satisfies

\[
\dot y+My=-\dot p^*. \tag{19}
\]

For the fundamental propagator `U(t,s)` this has the exact representation

\[
y(t)=U(t,t_0)y(t_0)-\int_{t_0}^{t}U(t,s)\dot p^*(s)\,ds. \tag{20}
\]

The first slow-variation correction is

\[
p^{(1)}=p^*-M^{-1}\dot p^*,\qquad
\dot p^{(1)}-(s_{\rm phys}-Mp^{(1)})
=-\frac{d}{dt}\left(M^{-1}\dot p^*\right). \tag{21}
\]

An initial layer, positivity, omitted bath feedback, and a bound on the residual in (21) matter for physical admission. This is a possible new controlled model, not a statement that the original source already evolved these storage variables. No dynamic extension was run here.

## 7. Net radiation and energy can be advanced with a narrower claim

The stored thick-line outgoing occupation is `fout=fWien+PL(d_alpha)` on the chosen represented cell. The admitted incoming history supplies `fin=fWien+PL(din_retarded)`. Thus

\[
j(u)=d_\alpha^{\rm PL}(u)-d_{\rm in}^{\rm retarded,PL}(u)
\]

contains no Wien cancellation error. With the admitted `G=3e6*LYA_FACT` and reference `u=0`,

\[
\Delta N_0=G\int_0^h e^{3u}j(u)\,du,\qquad
\Delta U_0=G E_{21,J}\int_0^h e^{4u}j(u)\,du. \tag{22}
\]

Split at the already identified retarded incoming knot. Reuse prior incoming integrals; compute only the new net correction and add it once. In the native scalar geometry,

\[
\Delta T_0=\operatorname{diag}(\Delta U_0,\Delta U_0/3,
\Delta U_0/3,\Delta U_0/3),\qquad
\Delta N_1=e^{-3h}\Delta N_0,\quad
\Delta U_1=e^{-4h}\Delta U_0. \tag{23}
\]

The local event energy per reference volume is `E21,J*DeltaN0`, not the pulled-back `DeltaU0`. Define `I3=integral exp(3u)j du` and `I4=integral exp(4u)j du`. The event-to-end redshift work is

\[
W_1=G E_{21,J}(e^{-h}I_4-I_3),\qquad
e^{3h}\Delta U_1-E_{21,J}\Delta N_0-W_1=0. \tag{24}
\]

Likewise the left-pullback work is `W0=G*E21,J*(I4-I3)`. When `j>=0`, `0<=W0<=(exp(h)-1)*E21,J*DeltaN0`, and `-(1-exp(-h))*E21,J*DeltaN0<=W1<=0`. If `j` changes sign, retain the signed identity without those positivity bounds.

The local isotropic source is `cQ_rad^0=E21,J*G*H*j`, with spatial components zero. This is a source rate, whereas (23) is a finite stress increment. A finite committed kick must not be re-applied as an additional rate in the post-kick B3i RHS. Reuse the existing B3b packet/stock bookkeeping semantics and B3g transport, not LINE01's different stimulated-bath absorption law. The complete physical atomic transaction remains a distinct admission from this source-representation radiation subunit.

For comparison, with only two boundary traces one can choose any `0<A<=1` and set `fs=fi+(fo-fi)/A`; all such choices share the same net exchange but have different gross absorption/emission counts. That limited-information observation no longer prevents endpoint opacity reconstruction once the average trace and source coefficient are supplied. In particular, the present three-trace construction supersedes a blanket nonidentifiability claim.

## 8. Frozen coding recommendation and stopping rule

Root should implement this theory through the already planned lower-tier coding role. The finite target is the two knots and the six selected bins, using the exact extracted packets. No new native solve or old campaign is needed.

1. Reproduce source background coefficients and incoming arithmetic; invert each of the 12 triples with a bracketed binary64 method and an independent 70-digit reference. The right snapshot population is excluded from solver inputs.
2. Return each bin's `r`, tau, Gamma, x1s, root residual, jump size, condition number, and explicitly scoped propagated numerical interval. Retain the primary bin as the returned value and every cross-bin result separately.
3. Derive x2p, tau_Ly-alpha, and x2s by (11) and independently by (12). Return absolute source-effective endpoint stocks on the already fixed common volume. Report the source normalization excess separately from finite storage changes.
4. If the net radiation subunit is included, evaluate only (22) and its independent reference; reuse admitted incoming totals and transport formulas. Do not replay previous consume/plot/test evidence.
5. Report the endpoint storage defect and the named owner distinction. A physical refill or complete B3i atomic admission requires actual owner evidence; an algorithmic refresh is labeled as such.

Recommended predeclared acceptance thresholds are relative `x1s` agreement with the validation-only right snapshot <=`2e-10`, cross-bin agreement <=`2e-10` at each knot, net photon quadrature error <=`2e-11` on the **net result's own scale**, and transport relative residual <=`2e-13`. Require nonzero resolved jumps, admissible ratio intervals, the correct source exponential branch, positive reconstructed populations, and no hidden averaging. More demanding numerical claims must be justified by the actual propagated interval, not these acceptance ceilings.

One implementation review pass is sufficient. A concrete failure returns for one targeted authorized repair; no recursive process expansion. A scientifically valid endpoint reconstruction remains useful even if physical refill admission is pending. Keep all physical radii null and the previous ANISO difference `3.447529542803539e-5` distinct from its approximately `1e-11` reconstruction residual and `2e-8` continuum numerical budget.

## 9. Primary literature comparison and symbolic checks

SciSpace was actually queried once for HyRec/EMLA QSS assumptions. Exa performed a five-result focused search and fetched the two primary papers below. Some indexed arXiv records carry ingestion dates; use the original 2010 and 2011 publication dates.

- Y. Ali-Haimoud and C. M. Hirata, *Ultrafast effective multilevel atom method for primordial hydrogen recombination*, Physical Review D **82**, 063521 (2010), [DOI](https://doi.org/10.1103/PhysRevD.82.063521), [primary full text](https://arxiv.org/html/1006.1355). Its Section III, especially Eqs. 12–14, explicitly imposes the steady-state excited-state equations. Effective atomic elimination and cosmological evolution are separated. This supports retaining QSS as an approximation when discussing time-dependent excited-state storage.
- Y. Ali-Haimoud and C. M. Hirata, *HyRec: A fast and highly accurate primordial hydrogen and helium recombination code*, Physical Review D **83**, 043513 (2011), [DOI](https://doi.org/10.1103/PhysRevD.83.043513), [primary article HTML](https://ar5iv.labs.arxiv.org/html/1011.3758), [arXiv record](https://arxiv.org/abs/1011.3758). Its effective interface-state equations and radiative-transfer construction support the two-real-state/virtual-radiation distinction. Exact algebraic elimination within that approximation does not establish exact finite excited-state storage accounting.

The new work here is applying the stored-trace inverse to this source state and defining the finite ledger boundary. The storage and inverse identities are derived above; the papers are contextual primary support, not purported sources for an unperformed numerical result.

Three Wolfram Language evaluator calls checked: the scalar adiabatic residual and two-boundary family; the constant-matrix adiabatic identity and event-to-end energy identity; and the triple-trace identity, derivative form, series, inverse series, endpoint limits, and large-tau form. The third evaluator returned correct symbolic identities with two `Power::infy` messages during removable-singularity handling; retain that diagnostic. The separate WolframContext request failed with internal error `-32603` and is recorded as a tool failure, not a successful scientific check. Exact returned outputs are retained in `WOLFRAM_CHECKS.json`. No Python scientific fallback was run.
