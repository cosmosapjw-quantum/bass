# Native effective-H Lyα: finite incoming tube and atomic transaction boundary

Date: 2026-10-27 (Asia/Seoul). Independent theory/source analysis.
Evidence basis: derived, with the source conventions listed below.
No scientific runtime, no old tests/consume/plot replay, no remote mutation.

## 1. Scope and read sources

The selected subunit is the actual native scalar-FLRW incoming Lyα face,
on an adjacent native arrival-time cell. Its angular factor is q=1.
Metric signature is (-,+,+,+), x0=ct, T is J/m3, and cQ is J/(m3 s).

Read identities:
- BASS F2=009a1238c09adf889c7421132f530b960cdafb07;
  preserved science A2=af14fc72d99f6d0e396f60aedadcdb5d05213280.
- Live BASS research/bass-b3g-actual-cohort-binding-20261025 still at F2.
- Live central research/orchestration-sandbox-20261022 at
  5abe0d19df95db730e3e33bae0373c81ba37ce89; its AGENTS was read,
  blob 429a5a13ee75b1222bc50627f8d5973d01dd21c4.
- REC PR139 d6dbe39a4923439547c01695d9020ba39367ea90:
  research/rec_history_boundary_20261023/code/history_boundary.py,
  directly read, blob 1aa7f134c332bc4596372df18c7c47306260ecfc.
- Preserved native_line_owner.py, its FROZEN_CONTRACT.md,
  B3b finite_exchange.py, B3g transport.py and B3i geometry.py.
- Native archive source materialized by the intake worker:
  archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip,
  SHA256 48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27.
  Extracted history.c, hydrogen.h and input.dat were directly read.
- Current subunit FROZEN_CONTRACT.md, left-reference convention, was read.

The original constants are retained:
E21=10.198714553953742 eV,
G=3e6*LYA_FACT m^-3,
LYA_FACT=4.662899067555897e15 cm^-3.
The native temperature uses kBoltz=8.617343e-5 eV/K, T_CMB0=2.728 K.
For its actual source choice fsR=meR=1,
\[
 T_R(\eta)=T_{R,\mathrm{today}}e^{-\eta},\qquad
 T_{R,\mathrm{today}}={\tt kBoltz}\,T_{\mathrm{CMB0}},
 \qquad \eta=\log a.
\]
Modern constants must not silently replace the original source values.

The native virtual faces are zero-width nodes. Finite arrival-time support
is used here; no spectral width is assigned to an individual virtual spike.

## 2. Native retarding and absolute occupation

Let E_s>E21 be the native outgoing virtual face feeding Lyα. Its index is
140=NSUBLYA. Set
\[
 \delta=\log(E_s/E_{21})>0,\qquad \eta_s=\eta-\delta.
\]
The native departure arriving at Lyα is
\[
 d_{\rm in}(\eta)=\mathcal I_{\rm PL}[d_s](\eta-\delta),
\]
where the source owns the actual strict-past interpolation rule and affine
clock. Every active stencil must belong to the past prefix at its arrival
time. A fixed endpoint iz alone does not prove this throughout the cell.
Use the positive retarding lag, shifted knots and actual prefix semantics.

The source's stored eta array and eta0+j*h affine clock can differ by floating
roundoff. Preserve source array values and use the source interpolation
clock; report that representation discrepancy rather than redefine a grid
or manufacture an uncertainty radius from it.

Choose the actual selected interval [eta0,eta1] and the **left** reference
hypersurface eta0. Write
\[
 u=\eta-\eta_0,\qquad y=e^u,\qquad b=E_{21}/T_R(\eta_0).
\]
The absolute occupation in the native Wien convention is
\[
 \boxed{f_{\rm in}(\eta)=d_{\rm in}(\eta)+e^{-b y}}.
\]
This is a source-consistent characteristic pullback, because
\[
 E_s/T_R(\eta_s)=E_s e^{\eta_s}/T_{R,\mathrm{today}}
               =E_{21} e^\eta/T_{R,\mathrm{today}}
               =E_{21}/T_R(\eta).
\]
It does not introduce the stimulated Planck convention of LINE01.

The actual represented input must verify f_in>=0 on every segment.
A sufficient lower bound on a PL segment [a,b] is
min(d(a),d(b))+min(f_Wien(a),f_Wien(b))>=0.
Because y increases, the second minimum is the right endpoint value.
If this sufficient bound fails, that does not establish a negative trace.
In the selected x=b*y>1 regime, the Wien term obeys
f_Wien''=x(x-1)exp(-x)>0. Thus a PL-plus-Wien segment is convex and has at
most one interior minimum, satisfying m=x exp(-x), with m the PL slope.
That gives a targeted refinement if the elementary lower bound is inconclusive.

## 3. Positive finite crossing measure and common volume

Use one homogeneous comoving cell and compare all counts per its reference
physical volume V0=V_phys(eta0):
\[
 J_V(\eta)=V_{\rm phys}(\eta)/V_0=e^{3u}=y^3.
\]
The native crossing measure is
\[
 d\mu_0=G H(t)q(t,\mathbf n)J_V(t)\,dt\,d\Omega/(4\pi).
\]
For the actual native scalar FLRW input, q=1 and Hdt=deta, so
\[
 \boxed{d\mu_0=G y^3\,d\eta\,d\Omega/(4\pi)}.
\]
It is positive and finite on a finite native time cell, has units m^-3, and
contains the time integration already. Its total capacity is
\[
 C_{\mu,0}=G\,\operatorname{expm1}(3\Delta\eta)/3.
\]
No arbitrary proper-time step is introduced. Taking one reference cubic
metre is a density normalization, not an observation of an external cell size.

The incoming count per reference volume is
\[
 \boxed{N_0=G\int_{\eta_0}^{\eta_1}y^3f_{\rm in}(\eta)d\eta}.
\]
No additional dt or a^-3 multiplier belongs in N0.

The native source also provides n_H(eta)=n_H0 exp(-3eta), so
J_V*n_H(eta)=n_H(eta0). This closes the common-volume normalization for
atomic fractions once their matched time history is supplied.

## 4. Incoming shell, B3g transport, and sector stress

A photon crossing Lyα at eta has line energy E21. Traced backward on the
incoming collisionless characteristic to eta0, it has
\[
 E_0(\eta)=E_{21}e^{\eta-\eta_0}=E_{21}y.
\]
The finite time tube is therefore a real pre-line incoming shell on the left
slice, with energies in [E21,E21 exp(Delta eta)]. Its energy density is
\[
 \boxed{U_0=E_{21}G\int_{\eta_0}^{\eta_1}y^4f_{\rm in}(\eta)d\eta}.
\]
E21 is converted to joules for this SI quantity. Native isotropy yields
\[
 T_0^{\hat a\hat b}
 =\mathrm{diag}(U_0,U_0/3,U_0/3,U_0/3),\quad
 q_i=0,\quad \pi_{ij}=0,\quad -T^{00}+\sum_iT^{ii}=0.
\]
For N0>0, positivity independently implies
\[
 E_{21}\le U_0/N_0\le E_{21}e^{\Delta\eta}.
\]

Use the existing B3g diagonal map on the same shell:
\[
 R=e^{-\Delta\eta}I_3,\quad \det R=e^{-3\Delta\eta},\qquad
 N_1=e^{-3\Delta\eta}N_0,\quad
 U_1=e^{-4\Delta\eta}U_0.
\]
The extra power for energy comes from photon momentum redshift.
The y^3 inside the input measure converts to V0; detR converts this entire
left stock to the right volume. They refer to distinct operations and do
not double count expansion when used as above.

This tensor is the selected incoming-shell component, not the native total
radiation tensor. The right-slice tensor is the shell's **uncollided control**,
not the actual Lyα output after a transaction. B3i's SI representation can
be checked on this component, while a B3i RHS/atomic kick stays unexecuted
until its actual matched atomic packet is supplied.

The signed crossing work is
\[
 \Delta U_{\rm prop}=E_{21}N_0-U_0\le0,\qquad
 W_{\rm prop,loss}=U_0-E_{21}N_0\ge0.
\]
A stable primary evaluation is
\[
 W_{\rm prop,loss}
 =G E_{21}\int y^3\,\operatorname{expm1}(u)\,f_{\rm in}\,d\eta.
\]
Subtracting U0 and E21*N0 is an independent consistency check. This loss is
the photons' propagation/geometry redshift, not atomic recoil or thermal heat.

T is a state stress, while cQ is an active collision source rate. The
uncollided tensor carries cQ=0. A later already-applied finite atomic kick
also cannot be added again through cQ. The existing B3g state-to-core
conversion makes this timing distinction explicitly.

## 5. Exact exponential-times-PL integral

Split the arrival interval at each source knot shifted by +delta. On one
resulting segment [a,a+h], with endpoint departures d_a,d_b and z=k*h,
\[
 \int_a^{a+h}e^{k(\eta-\eta_0)}d_{\rm in}(\eta)d\eta=W_Ld_a+W_Rd_b,
 \qquad k=3,4,
\]
\[
 W_L=h e^{k(a-\eta_0)}
       \sum_{j=0}^{\infty}\frac{z^j}{(j+2)!},\qquad
 W_R=h e^{k(a-\eta_0)}
       \sum_{j=0}^{\infty}\frac{z^j}{j!(j+2)}.
\]
Both weights are positive, and
\[
 W_L+W_R=e^{k(a-\eta_0)}\operatorname{expm1}(kh)/k.
\]
Derivation: substitute v=(eta-a)/h and integrate exp(zv)*(1-v) and
exp(zv)*v on [0,1]. The series avoid cancellation in exp(z)-1-z.
The left-series successive-term ratio is z/(j+3); the right-series ratio is
z*(j+2)/[(j+1)*(j+3)]. A next-term geometric tail gives an explicit
mathematical truncation bound once the ratio bound is below one.
This tail is not an enclosure of all binary64 arithmetic.

Signed departures should be accumulated without clipping and with a stable
sum. The positivity property belongs to the total absolute occupation.

## 6. Exact Wien integral and independent quadrature

For y_a=exp(a-eta0), y_b=exp(a+h-eta0),
\[
 I_k^{W}=\int_{y_a}^{y_b}y^{k-1}e^{-b y}dy
 =b^{-k}[\Gamma(k,b y_a)-\Gamma(k,b y_b)].
\]
For integer k, Gamma(k,x)=(k-1)!*exp(-x)*sum_{m=0}^{k-1}x^m/m!.
That is an exact formula but its short-interval difference can lose digits.

An optional stable local series uses
x0=b*y_a, s=x0*expm1(h), and
\[
 J_m(s)=\int_0^1v^m e^{-sv}dv
       =\sum_{j=0}^{\infty}\frac{(-s)^j}{j!(m+j+1)}.
\]
Then
\[
 I_k^W=b^{-k}e^{-x0}s
        \sum_{m=0}^{k-1}{k-1\choose m}x0^{k-1-m}s^mJ_m(s).
\]
For 0<=s<=1 the alternating series decreases in magnitude and its first
omitted term bounds truncation. This expression is an independent analytic
reference for the selected positive-quadrature implementation.

The frozen implementation may instead use positive Gauss quadrature for
Wien and an independent high-precision piecewise quadrature for the full
input. Primary/reference discrepancy, analytic truncation if used,
roundoff allowance, and the still-null physical history/interpolation
uncertainty remain distinct quantities.

## 7. Native proper-time duration

Directly read native history.c and input.dat give
\[
 H(\eta)=3.2407792896393\,10^{-18}
 \sqrt{0.13e^{-3\eta}+0.343+\omega_r e^{-4\eta}}\ {\rm s}^{-1},
\]
\[
 \omega_r=4.48162687719\,10^{-7}(2.728)^4
              (1+0.227107317660239\times3.04).
\]
Curvature is zero, w0=-1 and wa=0. Therefore the actual proper duration is
\[
 \boxed{\Delta t=\int_{\eta_0}^{\eta_1}H(\eta)^{-1}d\eta}.
\]
It is useful clock provenance. Do not multiply it into the crossing count,
whose integration was already completed using Hdt=deta.

## 8. Exact remaining atomic dependency

With actual tau>=0 and q>0,
\[
 A=1-e^{-\tau/q},\quad
 f_s=f_W+x_{r,p}/(3x_{1s}),\quad
 f_{\rm out}=(1-A)f_{\rm in}+Af_s .
\]
The future finite transaction uses the native gross counts
\[
 D_\uparrow=\int Af_{\rm in}d\mu_0,\qquad
 D_\downarrow=\int Af_s d\mu_0 .
\]
Its stable net is
\[
 D=D_\downarrow-D_\uparrow
 =\int A[x_{r,p}/(3x_{1s})-d_{\rm in}]d\mu_0 .
\]
Thus the Wien reference cancels analytically in the net.
The photon bounds are 0<=D_up<=N0 and
N_out=N0-D_up+D_down>=0.

Physical atomic populations use
\[
 x_{2p}=x_{r,p}+3x_{1s}e^{-E_{21}/T_R},\qquad
 N_u^{(0)}=n_H(\eta_0)x_{2p},\quad
 N_l^{(0)}=n_H(\eta_0)x_{1s}.
\]
For an isolated closed two-level stock, every chronological prefix must obey
\[
 N_u(s)=N_u(0)-D(s)\ge0,\qquad
 N_l(s)=N_l(0)+D(s)\ge0 .
\]
D_down<=N_u(0) is a sufficient nonrecycling restriction, not a necessary
condition when an atom may first absorb and later emit. Native QSS
populations can have other source-owned replenishment. In that case use
actual cumulative supplies B_u(s),B_l(s):
\[
 N_u(s)=N_u(0)-D(s)+B_u(s),\quad
 N_l(s)=N_l(0)+D(s)+B_l(s).
\]
A snapshot endpoint alone does not establish those interval relations.

The direct native source already owns
radiation +E21*D, atomic internal -E21*D,
kinetic/recoil heat=0 in its recoil-free collapsed-line model,
and electron/ion yield=0 for this selected direct event.
The unresolved input is the matched time history of x1s, xr_p, tau and
population-supply ownership on this same finite tube. This does not make
all future atomic or nuclear providers prerequisites.

B3b gross_counts is a different LINE01 thick/stimulated map and
commit_emission explicitly rejects f_plus!=0. Native D_up/D_down must be
supplied independently. Reuse its stock/packet/conservation conventions,
not its different rate law.

## 9. Admission boundary and next action

The finite native photon tube is constructive progress independent of the
atomic time-history dependency. It can be computed and tested on actual
saved inputs now. The conditional atomic transaction remains unexecuted
until the missing matched packet is supplied.

Preserve existing results:
- 512 completed cohort transports and two prior B3i RHS consumes, no reruns.
- ANISO continuum-finite14 difference=3.447529542803539e-5.
- finite14 reconstruction residual approximately 1e-11.
- continuum numerical criterion 2e-8.
- physical eS/en/eE/geometry/temporal/total radii null.
- central declared count 27/88; physical completion null; L4=false.
- historical budget unknown stays unknown; no foreign budget transfer.

No new strong no-go claim is made. The output of the current selected
subunit should be PARTIAL_NATIVE_FINITE_PHOTON_TUBE_ATOMIC_INPUT_OPEN.

