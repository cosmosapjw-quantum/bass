# Exact endpoint channel maps for the absolute-diffusion completion

Theory-only companion to the completed Phase A operands. No source coefficients or scientific results were recomputed for this note.

The active source branch was read back at 2026-10-27 12:59 UTC: research/bass-b3h-qss-channel-20261027 at b581ad6f9ab92ee2efac816e2f2d2a63994c77c6; central 152b82cac23fedcb75a9effe0c159bae3d800c01; AGENTS blob 429a5a13ee75b1222bc50627f8d5973d01dd21c4. All four existing agents were inventoried. The Phase A source arrays and old results remain unchanged.

## 1. Matrix orientation and the full absolute source

At one saved endpoint write

- \(A=T_{rr}\), shape 2 by 2.
- \(R=T_{rv}\), shape 2 by 311, stored as Trv.
- \(W=T_{vr}\), shape 311 by 2. The stored Tvr array has shape 2 by 311 and must be transposed for this matrix notation.
- \(V=T_{vv}\), shape 311 by 311, reconstructed from the source's diagonal/lower/upper arrays.

Let \(p=(p_s,p_p)^T\), \(g=x_{1s}^{\rm eff}\), and

\[
 q_r=g e^{-E_{21}/T_r}(1,3)^T,\quad
 q_{v,b}=g e^{-E_b/T_r},\quad
 x_r=p-q_r,\quad x_v=X_v-q_v.
\]

Build \(d=-T_{\rm diff}(q_r,q_v)^T=(d_r,d_v)\) from the actual diffusion edges alone. Then

\[
 0=s_v+d_v-W(p-q_r)-V(X_v-q_v).
\]

Hence the exact affine virtual map is

\[
 \boxed{X_v=a+Bp,\quad
 a=q_v+V^{-1}(s_v+d_v+Wq_r),\quad B=-V^{-1}W.}                \tag{1}
\]

The equivalent absolute source is

\[
 S_v=s_v+d_v+Wq_r+Vq_v,\qquad a=V^{-1}S_v.                    \tag{2}
\]

The real source and reduced operator are

\[
 \begin{aligned}
 S_r&=s_r+d_r+Aq_r+Rq_v,\\
 b_{\rm abs}&=S_r-Ra,\\
 M&=A+RB=A-RV^{-1}W,\\
 \dot p&=b_{\rm abs}-Mp.
 \end{aligned}                                               \tag{3}
\]

Thus \(s_r\) enters the real source \(b_{\rm abs}\), not the virtual intercept \(a\). Omitting either the external \(q_v\) in (1) or \(Wq_r\) inside the inverse gives the wrong absolute radiation map.

### 1.1 Construct \(d\) by directed edges

For a core \(p\to b\) edge with forward coefficient \(F_{pb}\) and reverse coefficient \(D_{bp}\), evaluate the known reference current

\[
 J^W_{pb}=F_{pb}q_{r,p}-D_{bp}q_{v,b}.
\]

Add \(-J^W_{pb}\) to \(d_{r,p}\) and \(+J^W_{pb}\) to \(d_{v,b}\).

For a virtual \(b\to c\) edge, use

\[
 J^W_{bc}=A_{bc}q_{v,b}-A_{cb}q_{v,c}.
\]

Add \(-J^W_{bc}\) to \(d_{v,b}\) and \(+J^W_{bc}\) to \(d_{v,c}\). Count every undirected edge once. There is no virtual diffusion edge directly from bin139 to140; both couple to the real core.

### 1.2 Positive boundary-source form

Define the source escape probability \(P_b\) by

\[
 1-P_b=\texttt{one\_minus\_P}[b],\qquad
 C_b=V_{bb}-\Gamma_b
     =\frac{\Gamma_bP_b}{1-P_b}.
\]

The source arrays retain their original small-optical-depth branch. With absolute incoming occupation

\[
 f_{{\rm in},b}=\Delta f_{{\rm in},b}+e^{-E_b/T_r},
\]

all non-diffusive equilibrium terms cancel and the explicitly restored diffusion terms cancel in (2), leaving

\[
 \boxed{S_{v,b}=C_b\,g f_{{\rm in},b},\qquad
 a=V^{-1}[C\odot g f_{\rm in}].}                              \tag{4}
\]

This is the independent positive-source interpretation of (1). In floating arithmetic, compare (1)/(4) at the appropriate gross scale; the source's independently rounded energy constants and arithmetic can leave small numerical cancellation residuals. Do not relabel such roundoff as a new physical channel.

Similarly, the positive real source is

\[
 S_r=
 \begin{pmatrix}
 n_Hx_ex_{\rm HII}\alpha_s
 +3R_\alpha g[c_\beta f_{\beta,\rm in}
              +c_\gamma f_{\gamma,\rm in}]\\
 n_Hx_ex_{\rm HII}\alpha_p+3R_\alpha g f_{\alpha,\rm in}
 \end{pmatrix},                                               \tag{5}
\]

where \(c_\beta=1.664786871919931\), \(c_\gamma=1.953125\), and
\(f_{\gamma,\rm in}=e^{-E_{41}/T_r}\) is the original source assumption of no incoming distortion blueward of Ly-gamma. The source calls this a blackbody boundary while its high-frequency equations use the Wien value. Preserve that convention explicitly.

## 2. Every endpoint gross event map

All rates below are per hydrogen nucleus per proper second. Substitute \(X_b=a_b+B_bp\) to obtain each affine map. Forward and reverse rates are individually nonnegative; signed net rates are their differences.

Let the atomic inventory order be ground, 2s, 2p, ion. Photons associated with a virtual proxy are not additional atoms.

### 2.1 Successful bound-free transitions

For interface \(i\),

\[
 j_{{\rm rec},i}=n_Hx_ex_{\rm HII}\alpha_i,\qquad
 j_{{\rm ion},i}=\beta_i p_i.
\]

Recombination transfers one ion to \(i\). Ionization reverses that transfer. For recombination, the energy vector (atomic internal, gas, total radiation) is
\((-\chi_i,-K_{{\rm rec},i},\chi_i+K_{{\rm rec},i})\).
For ionization it is
\((+\chi_i,+K_{{\rm ion},i},-\chi_i-K_{{\rm ion},i})\).
The coefficients and moments are the existing Phase A values. No continuum-return null cycle is implicitly added.

### 2.2 Effective 2p/2s mixing

\[
 j_{p\to s}=R_{2p2s}p_p,\qquad
 j_{s\to p}=3R_{2p2s}p_s.
\]

This only transfers interface stock. In the source's equal-\(E_{21}\), radiative, recoil-free effective model, total atomic, gas and radiation energy changes are all zero. Spectral redistribution may remain nonzero but is outside this total-moment ledger.

### 2.3 Direct Ly-alpha and effective Ly-beta/gamma

\[
 \begin{array}{lll}
 j_{\alpha,+}=R_\alpha p_p,&
 j_{\alpha,-}=3R_\alpha g f_{\alpha,\rm in},&
 \text{atom }p\leftrightarrow g,\\
 j_{\beta,+}=3R_\alpha c_\beta e^{-E_{32}/T_r}p_s,&
 j_{\beta,-}=3R_\alpha g c_\beta f_{\beta,\rm in},&
 \text{atom }s\leftrightarrow g,\\
 j_{\gamma,+}=3R_\alpha c_\gamma e^{-E_{42}/T_r}p_s,&
 j_{\gamma,-}=3R_\alpha g c_\gamma e^{-E_{41}/T_r},&
 \text{atom }s\leftrightarrow g.
 \end{array}                                                  \tag{6}
\]

For positive downward events, direct Ly-alpha carries atom \(-E_{21}\), hard radiation \(+E_{21}\), direct gas heat0. Ly-beta carries atom \(-E_{21}\), hard radiation \(+E_{31}\), companion radiation \(-E_{32}\). Ly-gamma replaces31/32 by41/42. Reverse events reverse these signed energy entries.

The companion radiation is an actual selected radiation-bath owner; it is not gas heat. These are the original effective thick-line rates. No finite-\(\tau_{\rm Ly}\) replacement has been introduced.

### 2.4 Non-diffusive two-photon/Raman interfaces

Use the stored pre-diffusion matrices, not the full arrays at bins139/140:

\[
 F_{ib}=-T^{\rm pre}_{vr,ib},\qquad
 D_{bi}=-T^{\rm pre}_{rv,ib}.
\]

Then

\[
 j_{i\to b}=F_{ib}p_i,\qquad j_{b\to i}=D_{bi}X_b.             \tag{7}
\]

The forward event transfers interface \(i\to\) ground, creates one tracked hard photon at \(E_b\), and has energy
atom \(-E_{21}\), tracked hard \(+E_b\), companion radiation \(E_{21}-E_b\), gas0.
Eliminated upper-state absorption/emission sequences telescope to that companion total.

### 2.5 Core/wing diffusion

The only real-core diffusion links are

\[
 \begin{array}{lll}
 p\leftrightarrow139:&j_+=A2p_{\rm dn}p_p,&j_-=Aup_{139}X_{139},\\
 p\leftrightarrow140:&j_+=A2p_{\rm up}p_p,&j_-=Adn_{140}X_{140}.
 \end{array}                                                  \tag{8}
\]

Forward transfers 2p to ground, creates a hard photon at \(E_b\), and contributes
atom \(-E_{21}\), hard radiation \(+E_b\), gas \(E_{21}-E_b\).
This differs from the companion-radiation owner in (7).

### 2.6 Virtual diffusion links

For \(b=100,\ldots,138\) and \(b=140,\ldots,178\),

\[
 j_{b\to b+1}=Aup_bX_b,\qquad
 j_{b+1\to b}=Adn_{b+1}X_{b+1}.                              \tag{9}
\]

There is no atomic change. For a positive \(b\to c=b+1\) event, hard radiation changes by \(E_c-E_b\) and gas by \(E_b-E_c\).

## 3. Virtual boundaries: algebraic exposure versus actual face crossing

The virtual steady row is equivalent to

\[
 \sum(\text{real/neighbor photon injections})
 -\sum(\text{real/neighbor photon removals})
   = C_b[X_b-g f_{{\rm in},b}].                              \tag{10}
\]

The positive pair \(C_bX_b\) and \(C_bgf_{{\rm in},b}\) is an effective boundary-exchange representation of the mean-field equation. Its difference is the boundary net. Its gross pair is not the literal incoming/outgoing photon-face measure.

To construct literal face quantities, define

\[
 \kappa_b=\Gamma_b/\tau_b
 =\frac{8\pi H}{g n_H(hPc/E_b)^3},\qquad
 S_b=-(Wp)_b-\sum_{c\ne b}V_{bc}X_c,\qquad
 f_{{\rm eq},b}=\frac{S_b}{g\Gamma_b}.
\]

For the exponential branch,

\[
 f_{{\rm out},b}
 =f_{{\rm in},b}+(1-e^{-\tau_b})
       (f_{{\rm eq},b}-f_{{\rm in},b}),
\]

\[
 j_{{\rm face,in},b}=\kappa_bg f_{{\rm in},b},\quad
 j_{{\rm face,out},b}=\kappa_bg f_{{\rm out},b},
\]

\[
 j_{{\rm face,out},b}-j_{{\rm face,in},b}
 =C_b(X_b-gf_{{\rm in},b}).                                  \tag{11}
\]

At zero optical depth use the geometric expression for \(\kappa_b\) and the continuous limit; do not divide zero by zero.

The native small-\(\tau\) branches use two separately truncated expressions:

\[
 P_b=1-\tau_b/2+\tau_b^2/6,\qquad
 A_b^{\rm native}=\tau_b-\tau_b^2/2 .
\]

Thus \(A_b^{\rm native}/\tau_b\ne P_b\) by \(-\tau_b^2/6\). For \(\tau_b\le10^{-6}\), this is a known source truncation discrepancy, not a physical refill. An exactly conservative face representation of the preserved virtual operator uses
\(A_b^{\rm op}=\tau_bP_b=\tau_b-\tau_b^2/2+\tau_b^3/6\).
If used, label it as the new operator-consistent face convention. Do not claim it is byte-identical to the original saved outgoing formula. Keeping (10) as the finite boundary net and reporting this source-order distinction is also sufficient when no new all-bin face cohort is claimed.

### 3.1 Energy accounting without double counting

At virtual steady state,

\[
 \sum_b E_b C_b(X_b-gf_{{\rm in},b})
 =\sum_{i,b}E_b J_{ib}
  +\sum_{\rm core,b}E_bJ_{pb}
  +\sum_{\rm virtual\ edges}(E_c-E_b)J_{bc}.                  \tag{12}
\]

Use the left side as the external hard-radiation return, or use the internal contributions on the right as its equivalent event accounting. Do not add both sides as separate radiation production.

Add bound-free total radiation, direct Lyman radiation, and the companion-radiation terms once. Together with the atomic and gas entries above, the selected total energy sums to zero. Virtual boundary exchange is radiation ownership, not an invented thermal owner.

## 4. Constant-left source ratios with the native Ly-alpha activity clock

The parent's smaller finite choice is consistent. Freeze the above non-Ly-alpha endpoint maps at the left knot and divide every one by the same \(R_{\alpha,0}\). Multiply them in proper time by the actual
\(R_\alpha(u)={\rm LYA\_FACT}H/[n_Hg(u)]\).

Let \(ds=R_\alpha dt\), define

\[
 \bar b=b_{{\rm nL},0}/R_{\alpha,0},\qquad
 \bar M=M_{{\rm nL},0}/R_{\alpha,0}+e_pe_p^T .
\]

Then

\[
 \frac{dp}{ds}=\bar b+3g(u)f_{\alpha,\rm in}(u)e_p-\bar Mp.
\]

For total activity \(S\), \(I_p=\int_0^S p\,ds\), and the preserved actual Ly-alpha incoming count,

\[
 \boxed{\bar M I_p
 =\bar b S+e_p\,N_{\alpha,\rm in}/N_{H,0}
       -[p(S)-p(0)].}                                       \tag{13}
\]

Every unweighted non-Ly-alpha gross count follows as
\(N_{H,0}[(a_c/R_{\alpha,0})S+(\ell_c/R_{\alpha,0})I_p]\).
Ly-alpha emission is \(N_{H,0}(I_p)_p\), and its incoming count is reused. This identity preserves finite storage without subtracting independently integrated nearly equal gross quantities.

The exact endpoint is the constant-matrix convolution. A short final-activity window plus an explicit \(e^{-\gamma L}\) tail bound is appropriate when the actual reduced M-matrix contraction is available. The right native operators remain diagnostic; this frozen-left model is not asserted to reproduce them. Source conversion, diffusion completion and boundary conventions are stated model choices.

The associated non-Ly-alpha boundary profile is also explicit. Scaling \(V,W,\Gamma,C\) together by \(R_\alpha(u)/R_{\alpha,0}\), while retaining the actual \(H,n_H,g(u)\) relation, leaves each virtual \(\tau_b\) at its left value. A frozen intercept \(C_{b,0}g_0f_{{\rm in},b,0}\) scales as a fixed \(X\)-bath source. Expressed as an occupation it corresponds to \(f_{{\rm in},b}^{\rm model}(u)=g_0f_{{\rm in},b,0}/g(u)\). It is a positive profile derived from the saved left input, not a claim that the entire original native virtual incoming history was replayed or reproduced. The same distinction applies to non-Ly-alpha line boundary maps frozen in this manner. The selected actual Ly-alpha incoming history remains the separate preserved input.

## 5. A finite radiation owner and the selected-shell subtraction

A Planck reservoir at the actual left source temperature is a legitimate finite prepared radiation owner for the channels whose coefficients use that thermal bath. Let \(\mathcal C_\nu\) be the photon phase-space normalization consistent with the source constants and the preserved Ly-alpha measure. With energies in eV,

\[
 U_{{\rm BB},0}
 =\mathcal C_\nu\,{\rm eV_J}\,
      \frac{\pi^4}{15}T_{r,0}^4
\]

per reference volume. Match \(\mathcal C_\nu E_{21}^3=G\) if the frozen packet's exact Ly-alpha normalization is authoritative, and report the source-constant convention rather than silently mixing modern constants.

The actual incoming Ly-alpha cohort is an explicit prepared stock already given by the completed finite result. In the left-reference phase-space representation its shell is \(E=E_{21}e^u\), \(0\le u\le h\). Therefore a Planck-background-plus-actual-cohort initial inventory is

\[
 U_{{\rm rad},0}
 =U_{{\rm BB},0}
 -GE_{21}{\rm eV_J}\int_0^h
       \frac{e^{4u}}{\exp(E_{21}e^u/T_{r,0})-1}\,du
 +U_{\alpha,\rm in}^{\rm actual}.                            \tag{14}
\]

This replaces the Planck shell by the source-derived actual cohort; it does not add a duplicate shell. The source's Wien-versus-Planck convention in the actual cohort remains explicit.

Nonthermal virtual incoming occupations cannot all be renamed Planck photons. Two workable finite representations are:

1. Keep a single shared source-prepared spectral radiation bath and debit/credit the net boundary currents (10). The 311 positive gross exposure pairs are not 311 new copies of its initial stock. A finite spectral representation is available from the saved left average departures: first convert them to absolute occupations \(\bar f_b=\Delta\bar f_b+e^{-E_b/T_r}\) at the actual \(E_b\) nodes, then interpolate those occupations with nonnegative weights between nodes, retain Planck outside that represented frequency interval, and declare this finite interpolation as part of the new model. This conversion is not an absolute-value operation or clipping. Its number and energy moments are finite integrals with the same \(\mathcal C_\nu\). Replace the selected Ly-alpha shell in that represented field, rather than subtracting a second Planck copy if the shell was already replaced. Check the finite selected donor inventories under the proposed update.

2. If explicit virtual incoming/outgoing cohorts are desired, use the face coefficients in (11), with the stated small-\(\tau\) convention, and a common phase-space ownership map. Different frequency faces may be crossed by the same photon during the tube. Do not count every face fluence as an independent initial photon stock. Internal face transfers are ownership transfers within the shared radiation sector.

The first choice is the smaller total-moment completion and needs no new external supplier. It is an explicitly prepared finite radiation model using actual source occupations; it is not a claim that the original native code evolved the new radiation/heat inventory self-consistently. The successful bound-free suboperator can instead be selected on its own if the parent chooses a smaller completed claim. This is a scope choice, not a blanket requirement for all future channels.

Physical radii remain null. No source history, previous inverse, previous finite-photon calculation, previous controls/plot or B3i function was executed to produce this theory note.

