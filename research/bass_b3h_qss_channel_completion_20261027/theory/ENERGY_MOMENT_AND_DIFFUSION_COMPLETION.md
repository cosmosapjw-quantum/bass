# Finite QSS energy ownership and the native Wien approximation

Status: constructive theory checkpoint for the new native QSS owner unit. This document does not report a new numerical execution or a physical-radius certification.

## Reused state and scope

The completed history inversion is immutable evidence at BASS commit 6bf4a5d90b05f7e583be698854e521d259287837. Its two native knots 5126 and 5127, finite photon result, numerical checks, controls and plot are reused without execution. The new input packet is qss_owner_intake/NATIVE_QSS_STORED_INPUT_5126_5127.json, SHA256 c335e0273677a55a910b4ff67a1aa47a64834a19bf460b286bfe78404e9cf710. The packet supplies the actual source tables, original C formulas, 311 stored radiation traces at both knots and an independent right-knot native snapshot.

The physical eS/en/eE/geometry/temporal/total radii remain null. The original central completion count remains 27/88 at this checkpoint. A source interpolation or finite-model assumption is not converted to a physical error bound.

The calculations below concern successful effective continuum-to-interface transitions, the two real interface populations 2s and 2p, and explicitly selected radiation/thermal companions. The 311 virtual unknowns remain algebraic radiation variables. They are not atomic levels.

## 1. Effective recombination has an accessible energy moment

At fixed radiation temperature \(T_r\), express the successful effective recombination coefficient as

\[
 \alpha_i(T_m,T_r)=C T_m^{-3/2}
       \int_0^\infty W_i(\epsilon;T_r)e^{-\epsilon/T_m}\,d\epsilon,
 \qquad W_i\geq0.                                             \tag{1}
\]

Temperatures and \(\epsilon\) are in eV. The kernel includes the appropriate cross-section and phase-space factors. In the effective multilevel-atom construction,

\[
 \alpha_i^{\rm eff}=\alpha_i+\sum_K\alpha_K P_K^i,
\]

and, for the radiative interior network used here, the absorption probabilities \(P_K^i\) depend on \(T_r\), not on \(T_m\). The effective coefficient therefore has the same Maxwell integral form as each primitive recombination coefficient. This is the premise under which the moment formula is used; an arbitrary fitted rate with additional matter-temperature-dependent branching would need its extra derivative term treated explicitly.

Differentiating (1) at fixed \(T_r\) gives the mean captured electron-proton relative kinetic energy

\[
 K_{{\rm rec},i}
 =\frac32 T_m+T_m^2
   \left.\frac{\partial\ln\alpha_i(T_m,T_r)}{\partial T_m}\right|_{T_r}.
                                                               \tag{2}
\]

This is a moment identity, not an ansatz assigning an arbitrary energy to a balance residual. The source rate table can supply the derivative of its represented interpolation without running the native solver.

### 1.1 Reverse effective kernel

For a Planck radiation bath at \(T_r\), the differential Milne relation at \(T_m=T_r\) connects primitive recombination and photoionization kernels. Let \(q_i,q_K\) be the equilibrium bound-state weights and \(q_e\) the continuum weight. Let the transient interior matrix be \(\mathcal M\). Its reciprocity relation is

\[
 q_K(\mathcal M^{-1})_{KL}
 =q_L(\mathcal M^{-1})_{LK}.
\]

With the corresponding rate reciprocity \(q_iR_{iK}=q_KR_{Ki}\), the effective differential ionization kernel is

\[
 \begin{aligned}
 \beta_i^{\rm eff}(\epsilon)
 &=\beta_i(\epsilon)+
     \sum_{K,L} R_{iK}(\mathcal M^{-1})_{KL}\beta_L(\epsilon)\\
 &=\frac{q_e}{q_i}
     \left[\alpha_i(\epsilon;T_r,T_r)
       +\sum_{L,K}\alpha_L(\epsilon;T_r,T_r)
             (\mathcal M^{-1})_{LK}R_{Ki}\right]\\
 &=\frac{q_e}{q_i}\alpha_i^{\rm eff}(\epsilon;T_r,T_r).
 \end{aligned}                                                 \tag{3}
\]

Consequently the mean kinetic energy of the relative electron-proton motion created by a successful effective photoionization is

\[
 K_{{\rm ion},i}
 =\frac32 T_r+T_r^2
   \left.
     \frac{\partial\ln\alpha_i(T_m,T_r)}{\partial T_m}
   \right|_{T_m=T_r,\;T_r\ {\rm fixed}}.                         \tag{4}
\]

The derivative in (4) is the matter-temperature partial derivative evaluated on the diagonal. It is not the total derivative of \(\alpha_i(T,T)\), which also differentiates the radiation bath and branching probabilities.

### 1.2 Direct implementation in the original table interpolant

The original hydrogen.c interpolates log Alpha on the variables log \(T_r\) and \(q=T_m/T_r\). The matter-ratio grid has 40 points over [0.1,1]. Let \(\Delta q\) denote that grid spacing and \(f=(q-q_{\min})/\Delta q-i\) the local coordinate used by the source, including its original clamped stencil index. After the source log-\(T_r\) interpolation, call the four log-rate values \(h_k\). The source weights are

\[
 \begin{split}
 c_0&=f(f-1)(2-f)/6,\\
 c_1&=(1+f)(1-f)(2-f)/2,\\
 c_2&=(1+f)f(2-f)/2,\\
 c_3&=(1+f)f(f-1)/6 .
 \end{split}
\]

For the exact represented polynomial,

\[
 \left.\partial_{T_m}\ln\alpha\right|_{T_r}
 =\frac{1}{T_r\Delta q}\sum_{k=0}^3 h_k c'_k(f).                 \tag{5}
\]

At \(q=1\), use the source's upper clamped stencil and evaluate its polynomial derivative; do not introduce a new central difference outside the table. The constant fine-structure/mass prefactor contributes no \(T_m\) derivative. The source beta coefficients use the equilibrium Alpha and the Saha factor, with the 2p statistical factor 1/3.

Equations (2), (4), and (5) define a new energy-moment closure for the represented effective source rates. The original thermal evolution did not already include this closure. The new numerical unit must report the actual moments and their positivity; numerical table-interpolation accuracy and the physical approximation error remain separate.

### 1.3 Three-sector event energy identity

Let \(p_c\) be the ionized-hydrogen fraction, \(p_i\) the absolute interface fraction, \(E_I\) the ionization energy, and \(E_i=E_{21}\) for both interface levels in this source model. Define \(\chi_i=E_I-E_i\). The actual gross successful rates per hydrogen nucleus are

\[
 R_i=n_H x_e p_c\,\alpha_i,\qquad I_i=\beta_i p_i.               \tag{6}
\]

They have nonnegative rates and named finite reactant stocks. Their three energy rates, in eV per hydrogen nucleus per second, are

\[
 \begin{aligned}
 \dot E_{\rm atom}&=-\chi_i(R_i-I_i),\\
 \dot E_{\rm gas}&=-K_{{\rm rec},i}R_i+K_{{\rm ion},i}I_i,\\
 \dot E_{\rm radiation}
  &=(\chi_i+K_{{\rm rec},i})R_i
    -(\chi_i+K_{{\rm ion},i})I_i.
 \end{aligned}                                                 \tag{7}
\]

Their sum vanishes term by term. Effective cascade radiation telescopes to the endpoint binding-energy change plus the captured or released relative kinetic energy. A frequency-resolved cascade spectrum requires additional conductance information, but this selected total energy moment does not.

For a common reference-volume inventory, multiply the time integral by \(N_{H,0}\) and by the eV-to-joule conversion. Isotropic radiation has pressure \(U_{\rm rad}/3\), so the total energy suffices for its isotropic stress tensor; it does not specify a spectrum.

The kinetic owner is the shared gas relative-motion pool. Calling it electron-only energy neglects the reduced-mass correction. Center-of-mass motion is retained through capture. A recombination reduces the number of translational particles by one, so a thermal-state update must update both gas energy and particle count:
\(U_{\rm gas}=\tfrac32 N_{\rm particles}T_m\).
A temperature change inferred with a permanently fixed particle count would omit this distinction.

Continuum-to-interior-to-continuum paths that never reach a selected interface can exchange heat while leaving the successful-transition count unchanged. They are distinct unselected channels. They are not silently included in (7), and their absence is not a gate on the finite transaction of the explicitly selected successful channels. Likewise, a purely bound-bound return to the same interface can redistribute the photon spectrum while its total endpoint energy telescopes to zero in the recoil-free radiative model.

## 2. The native distortion equations omit a known Wien diffusion drive

The original solver uses departures from a radiation-temperature Wien reference:

\[
 x_r=p-q_r,\qquad q_r=g e^{-E_{21}/T_r}(1,3)^T,
 \qquad
 x_v=X_v-q_v,\qquad q_{v,b}=g e^{-E_b/T_r},                     \tag{8}
\]

where \(g=x_{1s}^{\rm eff}=1-x_{\rm HII}\). Here \(X_{v,b}=g\bar f_b\) is the source virtual radiation proxy, not a literal atomic population or a photon-number inventory.

The non-diffusive radiative source coefficients obey their reference detailed-balance identities at \(T_r\). Diffusion, however, uses matter temperature \(T_m\). When \(T_m\ne T_r\), the \(T_r\)-Wien reference is not a diffusion equilibrium. The departure-only source operator therefore differs from literal positive absolute diffusion currents by an explicitly computable thermal drive.

For an interface-core to neighboring-bin edge, write the source detailed-balance pair as

\[
 A_{pb}=\tfrac13 A_{bp}e^{(E_{21}-E_b)/T_m}.
\]

The absolute directed current and its native departure version are

\[
 J_{pb}=A_{pb}p_p-A_{bp}X_{v,b},\qquad
 J^{\rm dep}_{pb}=A_{pb}x_{r,p}-A_{bp}x_{v,b}
                 =J_{pb}-J^{W}_{pb},
\]

where

\[
 J^W_{pb}=A_{bp}g e^{-E_b/T_r}
   \left[e^{(E_{21}-E_b)(1/T_m-1/T_r)}-1\right].                \tag{9}
\]

For a virtual edge \(b\to c\), with \(A_{cb}=A_{bc}e^{(E_c-E_b)/T_m}\),

\[
 J^W_{bc}=A_{bc}g e^{-E_b/T_r}
   \left[1-e^{(E_c-E_b)(1/T_m-1/T_r)}\right].                   \tag{10}
\]

These expressions vanish when the two temperatures agree. Their signs and associated energy transfer are determined by the actual source rates and energy differences.

### 2.1 Schur form of the explicit correction

The actual source block equations and Schur complements are

\[
 \begin{aligned}
 0&=s_r-T_{rr}x_r-T_{rv}x_v,\\
 0&=s_v-T_{vr}x_r-T_{vv}x_v,\\
 M&=T_{rr}-T_{rv}T_{vv}^{-1}T_{vr},\\
 b&=s_r-T_{rv}T_{vv}^{-1}s_v .
 \end{aligned}                                                \tag{11}
\]

Construct \(T_{\rm diff}\) from the diffusion edge coefficients alone, including real-virtual edges and virtual-virtual edges, so that no edge is double counted. Define the known drive

\[
 d=-T_{\rm diff}q=(d_r,d_v),\qquad
 c_{\rm diff}=d_r-T_{rv}T_{vv}^{-1}d_v.                         \tag{12}
\]

Then the two choices are explicit:

\[
 \begin{array}{ll}
 \text{native affine dynamic completion:}&
 \dot p=b+Mq_r-Mp,\\[2pt]
 \text{absolute diffusion completion:}&
 \dot p=b+Mq_r+c_{\rm diff}-Mp.
 \end{array}                                                   \tag{13}
\]

For the second choice, the virtual departure is

\[
 x_v=T_{vv}^{-1}\{s_v+d_v-T_{vr}(p-q_r)\}.                     \tag{14}
\]

The first line of (13) retains the source's Wien-omitted distortion approximation. The second restores the literal absolute thermal diffusion currents and therefore changes that approximation by a derived term. Calling this a new physical completion is accurate; calling it an unchanged native QSS solution would not be.

The term \(c_{\rm diff}\) is independently built from source diffusion coefficients and the known reference state. It is not defined to equal an unexplained population residual. No arbitrary reservoir is introduced by this construction.

The original history.c matter-temperature equation includes expansion and Compton coupling. It has no explicit recombination or diffusion heating ledger. Accordingly the source-prepared temperature is an input bath state, while (7) and the diffusion energy transfer below are newly constructed finite energy accounts. Keeping that distinction avoids claiming that a new heat contribution was already evolved by the original native history.

## 3. Energy ownership of the actual selected source channels

Each row uses the stated forward orientation. Energies are eV per net forward event. Reverse events reverse the signed column contributions.

| Source channel | Atomic stock change | Atomic internal energy | Tracked radiation | Companion or gas owner |
|---|---|---:|---:|---:|
| Successful continuum to interface i | ion -1, i +1 | \(-\chi_i\) | \(+\chi_i+K_{{\rm rec},i}\) | gas \(-K_{{\rm rec},i}\) |
| Successful interface i to continuum | i -1, ion +1 | \(+\chi_i\) | \(-\chi_i-K_{{\rm ion},i}\) | gas \(+K_{{\rm ion},i}\) |
| Effective 2p to 2s | 2p -1, 2s +1 | 0 in equal-\(E_{21}\) model | total cascade 0 | no gas heat in selected radiative, recoil-free model |
| Direct Ly-alpha 2p to ground | 2p -1, ground +1 | \(-E_{21}\) | \(+E_{21}\) | direct source recoil/heat 0 |
| Folded Ly-beta/gamma through 2s | 2s -1, ground +1 | \(-E_{21}\) | \(+E_{31}\) or \(+E_{41}\) | radiation bath \(-E_{32}\) or \(-E_{42}\) |
| Non-diffusive two-photon/Raman channel through bin b | interface -1, ground +1 | \(-E_{21}\) | \(+E_b\) | radiation bath \(E_{21}-E_b\) |
| Diffusive core to wing bin b | 2p -1, ground +1 | \(-E_{21}\) | \(+E_b\) | gas \(E_{21}-E_b\) |
| Diffusive virtual bin b to c | none | 0 | \(E_c-E_b\) | gas \(E_b-E_c\) |

For the non-diffusive real-to-virtual channel, the absolute gross-current difference follows directly from the source coefficients:

\[
 J_{ib}=C_{ib}p_i-g_i C_{ib}e^{(E_b-E_{21})/T_r}X_{v,b},
 \quad C_{ib}=-T_{vr,ib},\quad g_s=1,\;g_p=3.                  \tag{15}
\]

Below Ly-alpha, \(E_{21}-E_b\) is emitted as a companion photon. In the Raman/upconversion regime it is negative and is withdrawn from the prepared radiation bath. The eliminated upper-state paths telescope to the same total companion energy. These companion photons are radiation ownership, not gas heating.

The diffusion rows are different: their detailed balance is at \(T_m\), and the energy difference is exchanged with gas kinetic energy. Source direct Ly-alpha recoil/heat equal to zero must not be generalized to these off-line diffusion channels.

Virtual steady elimination describes radiation flow constraints. If finite radiation storage, propagation delay or a spectrum is subsequently requested, that is an additional explicitly modeled degree of freedom. It is not obtained by treating virtual source unknowns as atoms.

## 4. Finite stock and QSS storage defect

The completed endpoints reconstruct the original effective opacity convention \(g=1-p_c\), which omits the excited-state contribution from the ground normalization. Preserve that exact source parameter in the rates. A separate finite atomic inventory can be initialized as

\[
 N_c=N_{H,0}p_c,\quad N_s=N_{H,0}p_s,\quad N_p=N_{H,0}p_p,\quad
 N_g=N_{H,0}-N_c-N_s-N_p.                                     \tag{16}
\]

This explicit mapping restores exact count conservation in the newly selected finite transaction without silently redefining the original source opacity. The distinction is of order \(p_s+p_p\), about \(2.6\times10^{-14}\) at the reused knots.

Choose atomic excitation/ionization energy relative to ground,

\[
 U_{\rm atom}=E_I N_c+E_{21}(N_s+N_p),                         \tag{17}
\]

and a common thermal inventory initially

\[
 U_{\rm gas}=\tfrac32 N_{H,0}(1+f_{\rm He}+x_e)T_m.            \tag{18}
\]

Use the same explicit reference volume for all sectors. Rest energy is a separate constant unless a chosen convention explicitly includes the tiny binding-mass change.

An instantaneous QSS row gives non-Ly-alpha refill equal to Ly-alpha removal at each source knot. Its time integral has zero excited-population storage. The stored endpoint change, however, is nonzero. If \(D\) is the integrated Ly-alpha downward count and \(\Delta N_p\) is the actual endpoint storage, a finite owner requires

\[
 F_{\rm nonLy\alpha}=D+\Delta N_p.                            \tag{19}
\]

The algebraic source supplies \(D\), while replacing its endpoint QSS population supplies an algorithmic refresh with \(\Delta N_p\). This refresh is not by itself a physical refill channel. A dynamical solution of (13), with integrated source-defined currents and actual finite stocks, provides a constructive completion. It generally does not end exactly at the stored right QSS population, and its outgoing Ly-alpha field must be corrected consistently.

## 5. Primary literature and what it supports

1. Y. Ali-Haimoud and C. M. Hirata, Effective multilevel method for the computation of the recombination history, Physical Review D 82, 063521 (2010). Primary text: https://arxiv.org/html/1006.1355 . The rate reduction, its radiation-temperature-dependent branching probabilities, interface evolution equations and detailed-balance identities justify using effective rates in a two-interface dynamical equation. Interior QSS is required for this elimination; interface QSS is not required for its equivalence. The finite energy-accounting construction above is our derivation from those rate identities.

2. Y. Ali-Haimoud, Effective conductance method for the primordial recombination spectrum, Physical Review D 87, 023526, published 25 January 2013. Primary text: https://ar5iv.labs.arxiv.org/html/1211.4031 . Official publication record: https://journals.aps.org/prd/abstract/10.1103/PhysRevD.87.023526 . The paper supplies the differential Milne relation, inverse-matrix reciprocity and temperature-derivative weighted cascade quantities. These provide the primary basis for (3)-(4). A complete spectrum would require its additional conductance information.

3. Original source hydrogen.c, history.c, hyrec_params.h and the raw Alpha/R/two-photon tables are preserved in qss_owner_intake/native_source/. The selected original hydrogen.c SHA256 is 421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b. Native statements above are source-model statements, not claims of unmodeled microphysical completeness.

SciSpace and Exa were actually queried in this node; primary texts were actually fetched. The source-specific derivations and claim limits are not copied literature conclusions.

## 6. Bounded symbolic evidence

WOLFRAM_NEW_CHECKS.json preserves both actual tool calls, source expressions and returned outputs. The first call verifies the Maxwell derivative, reverse effective-kernel reciprocity, three-sector energy sum and Wien-current expression. Its affine-forcing subcheck encountered protected-symbol naming errors; that failed subcheck is preserved rather than reported as PASS. One targeted second call, using fresh symbol names, returns zero for the affine dynamic identity, zero for the initial condition and zero for the native photon/atomic clock identity. No numerical source replay was performed.

## 7. Operational checkpoint

Readback at 2026-10-27 12:34 UTC:

- BASS inverse branch: 6bf4a5d90b05f7e583be698854e521d259287837.
- Central orchestration branch: 152b82cac23fedcb75a9effe0c159bae3d800c01.
- Central AGENTS blob: 429a5a13ee75b1222bc50627f8d5973d01dd21c4, unchanged.
- Parallel source intake completed; root and lower-tier new-unit implementation active.
- This theory agent wrote documents and performed bounded symbolic checks only. Native solver, prior result/controls/plot, B3i consume and old campaigns were not executed.

