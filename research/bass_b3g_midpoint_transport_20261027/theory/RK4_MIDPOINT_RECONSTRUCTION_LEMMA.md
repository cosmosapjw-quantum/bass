# B3g midpoint reconstruction from saved B3c receipts

## Decision and exact scope

The saved B3c inputs support a new, bounded reconstruction of birth geometry
without replaying an IVP, a source transaction, or an old campaign. For each
classical-RK4 first transport half-step, a trapezoid using the saved starting
velocity and the saved source-entry velocity differs from the actual RK4
coordinate by an explicitly bounded stage-acceleration correction.

The lemma below is an exact-arithmetic statement about the declared finite
RK4/positive-packet model. It is not a bound on the error of that model relative
to a calibrated cosmology or a continuous nonlinear solution. Binary64 source
representation and the old implementation's arithmetic require a separately
labelled numerical reserve; the existing 512-epsilon representation allowance
is not a directed-rounding proof. All physical input radii remain null unless
an independent owner supplies them.

No scientific program, tests, IVP, old campaign, or source solve was executed
for this source/theory intake. The root controller owns the frozen numerical
contract, execution budget and final admission.

## Source and current-work observations

- Fresh BASS task ref: `d7dcd731de1a0c59e5e65db5038c333f5abae0bd` on
  `research/bass-b3g-actual-cohort-binding-20261025`.
- Fresh canonical central ref: `a5db4bac9dafadae29685bbea3cec7f43ab990b2`
  on `rei_bianchi:research/orchestration-sandbox-20261022`.
- Current central AGENTS blob:
  `429a5a13ee75b1222bc50627f8d5973d01dd21c4`, read in full.
- The BASS recursive tree is complete, 6349 entries; it has no governing
  root/research AGENTS file. Historical copied AGENTS files are provenance.
- BASS open-PR listing returned PR192 as the latest BASS task, updated
  2026-10-25T14:01:43Z. PR191 remains the program-expansion parent. The root
  controller is separately inspecting newer REI PR235/236; their different
  source models do not supply the missing B3c midpoint coordinate bytes.
- Restored B3c S2 contains 160 members, including the original source code and
  N032/N064/N128/N256 PATH/SOURCE_HISTORY files. It contains no saved final
  per-cohort packet NPZ or RunState array. Thus direct extraction of each
  transport matrix from final packet momenta is not available in this archive.
- The original `reference_runner.py` writes source histories and diagnostic
  paths but keeps `final_state` only in memory for figure construction.

Primary pinned source links:

- [B3c producer](https://github.com/cosmosapjw-quantum/bass/blob/d7dcd731de1a0c59e5e65db5038c333f5abae0bd/research/bass_b3g_actual_cohort_binding_20261025/inputs/b3c/code/bounded_background.py),
  Git blob `b04e1c757cd62f57429640f3de138c74aafc5a4e`, SHA256
  `1917f49c45cbd637f4d951a21d6e377c3cc3c58798c5e75690317eacabe68044`.
- [B3c contract](https://github.com/cosmosapjw-quantum/bass/blob/d7dcd731de1a0c59e5e65db5038c333f5abae0bd/research/bass_b3g_actual_cohort_binding_20261025/inputs/b3c/CONTRACT.md),
  Git blob `d18226d2e369f8231e3d28a72c8279e9b2333f88`.
- [Immutable input manifest](https://github.com/cosmosapjw-quantum/bass/blob/d7dcd731de1a0c59e5e65db5038c333f5abae0bd/research/bass_b3g_actual_cohort_binding_20261025/inputs/MANIFEST.json).
- Original B3c S2 ZIP: SHA256
  `0d3a911d7fc1b567c0e915cd655af94bff44495849bd0e7ce1bcb778a94bd1b2`,
  7021644 bytes, Dropbox `id:BSpOijBcT10AAAAAAD_9hw`.

## 1. Actual finite source placement

`integrate_fixture` composes

\[
T(\Delta\tau/2)\;\longrightarrow\;S(\Delta\tau)
\;\longrightarrow\;T(\Delta\tau/2).
\]

`transport` advances the six coordinates
\(q=(h,\sigma_1,\sigma_2,\alpha,\beta_1,\beta_2)\) using classical RK4.
`source_kick` leaves `run.q` unchanged and saves source-entry N, H and S.
Therefore the receipt's top-level `midpoint_H_s_inv` and `midpoint_S` describe
the first half-step endpoint, although its alpha/beta coordinates were omitted.

The half-step duration is

\[
\delta=\tfrac12\,\texttt{source\_subflow\_duration\_tau}.
\]

Do not derive it by subtracting accumulated path timestamps. The receipt's
source duration, deposition epoch, and global interval are distinct quantities.

For the selected Bianchi-I model, metric signature is (-,+,+,+),
\(\tau=ct/L\), and the geometry equations during transport are

\[
\alpha'=h,\qquad \beta_i'=\sigma_i,
\]
\[
h'=-h^2-\frac{\|\sigma\|_F^2}{3}
    -\frac{\rho_m+2\rho_\gamma}{6},\qquad
\sigma_i'=-3h\sigma_i+\pi_{\gamma,ii}.
\]

Here \(\rho_m=\rho_R+\rho_X\) contains the two energy terms of the same cold
atoms. The radiation stress is the positive massless packet moment at that
stage. U=J=0 during this transport; the finite source kick is already applied
once at its own stage. No four-force rate is added to an accumulated stress.

## 2. Exact RK4 coordinate identity

Let \(x'=v\), \(v'=f\) be one coordinate/velocity pair within an arbitrary
coupled classical-RK4 system. Write its stages A,B,C,D and its complete
half-step endpoint as 1. Then

\[
v_B=v_0+\frac\delta2 f_A,\quad
v_C=v_0+\frac\delta2 f_B,\quad
v_D=v_0+\delta f_C,
\]
\[
v_1=v_0+\frac\delta6(f_A+2f_B+2f_C+f_D).
\]

Substitution into the coordinate update gives

\[
x_1-x_0=\delta v_0+\frac{\delta^2}{6}(f_A+f_B+f_C)
       =\frac\delta2(v_0+v_1)+\frac{\delta^2}{12}(f_A-f_D).
\]

Thus, with the nominal reconstruction

\[
\widehat x_1=x_0+\frac\delta2(v_0+v_1),
\]

any bound \(|f_D-f_A|\le A_f\) implies

\[
|x_1-\widehat x_1|\le\frac{\delta^2}{12}A_f.
\]

This uses the fourth-stage acceleration, not acceleration at the completed
half-step or immediately after the source kick. Replacing f_D by either of
those quantities would change the identity.

For alpha use v=h; for beta1,beta2 use v=sigma1,sigma2. Set
\(\widehat\beta_3=-\widehat\beta_1-\widehat\beta_2\) and
\(e_{\beta_3}=e_{\beta_1}+e_{\beta_2}\), preserving the declared STF chart.

## 3. A closed finite-stage box from saved starting moments

The root-selected candidate box is

\[
|h|\le H=1.01,\qquad |\sigma_i|\le B=0.2\quad(i=1,2,3),
\]

with coordinate displacements \(|\Delta\alpha|\le\delta H\) and
\(\max_i|\Delta\beta_i|\le\delta B\). These are assumptions to verify by
the following four-stage induction, not sampled evidence of a continuous tube.

The exact packet map within a transport subflow is

\[
k_i=k_{i0}e^{-\Delta\alpha-\Delta\beta_i},\qquad
w=w_0e^{-3\Delta\alpha}.
\]

For a positive massless measure, every ray's energy-density multiplier is
between \(e^{-4|\Delta\alpha|-\|\Delta\beta\|_\infty}\) and its reciprocal.
Consequently, writing saved starting values m0=rho_m0 and g0=rho_gamma0,

\[
m_{\max}=m_0e^{3\delta H},\qquad
g_{\max}=g_0e^{\delta(4H+B)}.
\]

Also \(0\le P_{ii}\le\rho_\gamma\), \(p=\rho_\gamma/3\), and hence
\(|\pi_{ii}|\le2\rho_\gamma/3\). Valid acceleration bounds are therefore

\[
M_h=H^2+B^2+\frac{m_{\max}+2g_{\max}}6,\qquad
M_\sigma=3HB+\frac23g_{\max}.
\]

For each saved starting row verify

\[
|h_0|+\delta M_h\le H,
\qquad |\sigma_{i0}|+\delta M_\sigma\le B\quad\text{for all i},
\]

and \(h_0-\delta M_h>B\). The last condition ensures h>0 and every directional
expansion h+sigma_i>0 throughout this stage box. The inherited x remains
constant during transport and must remain in its saved non-inverted domain.

Stage A is inside by hypothesis. Stage B changes h/sigma by at most half of
these displacement bounds, and alpha/beta by at most deltaH/deltaB. Its
characteristic moments obey the displayed moment envelopes. The same argument
places C inside, then places D inside with full displacement bounds. This is a
finite induction over the four explicit stages, requiring no IVP replay and
no unprovided continuous curvature or time-interpolation bound.

## 4. Acceleration differences and coordinate radii

Define

\[
d_h=\delta M_h,\qquad d_s=\delta M_\sigma,
\qquad d_{s,F}=\sqrt3\,d_s.
\]

Then a bound for the alpha acceleration difference is

\[
A_h=(2|h_0|+d_h)d_h
  +\frac{(2\|\sigma_0\|_F+d_{s,F})d_{s,F}}3
  +\frac{m_0\operatorname{expm1}(3\delta H)
          +2g_0\operatorname{expm1}(\delta(4H+B))}{6}.
\]

For each independent shear component, a sufficient bound is

\[
A_{\sigma_i}=3\bigl(|h_0|d_s+|\sigma_{i0}|d_h+d_hd_s\bigr)
  +|\pi_{\gamma,ii,0}|+\frac23g_{\max}.
\]

If one wants a formula requiring only positive scalar radiation energy, replace
the final two terms by \(2(g_0+g_{\max})/3\). This coarser pressure bound is
sufficient in the present small-radiation fixture. It is intentionally not
advertised as a sharp Lipschitz estimate for the packet pressure.

The exact-arithmetic reconstruction radii are

\[
e_{\alpha,\mathrm{stage}}=\delta^2A_h/12,
\qquad e_{\beta_i,\mathrm{stage}}=\delta^2A_{\sigma_i}/12.
\]

Expected magnitudes are not execution results. The lower-tier implementation
must evaluate these bounds on all selected saved rows and report maxima,
stage-box checks and any refusal under the frozen numerical contract.

## 5. Recovering midpoint velocities and separating floating representation

In exact arithmetic, the saved source conventions imply

\[
\widehat h_b=H_{b,\mathrm{SI}}L/c,\qquad
\widehat\sigma_{b,i}=\widehat h_b S_{b,ii}.
\]

The actual binary64 producer computes H as `h*c/L`. Its `LineState` then calls
`angular.validate_inputs`, which symmetrizes S and subtracts its trace within
the frozen `64*eps*max(1,||S||F)` input band. This means the receipt's top-level
`midpoint_S` is a source-normalized representation, not bitwise original
`sigma/h`. The later `ledger.owner_map.S` may have passed the validator again
and can differ by one ULP; use the top-level field consistently.

If velocity recovery errors are bounded by omega_h and omega_sigma_i, their
coordinate contributions are delta*omega/2 in addition to the stage radii.
The complete numerical record must also keep the old RK4 arithmetic and new
arithmetic reserve separate. A chosen binary64 reserve may support a scoped
numerical reconstruction check; without directed rounding or a full operation
bound it is not an interval certificate for the old numerical trajectory.

The independent relation

\[
\alpha_b^{(N)}=-\tfrac13\log(N_b/N_0)
\]

can diagnose consistency of the bounded alpha reconstruction. The saved N_b is
the sum of lower/upper populations constructed from N and x, so this logarithm
also includes producer multiplication/addition and inverse-log rounding. It
does not restore the missing original alpha bytes.

## 6. Coupling reconstructed births to the saved final geometry

Treat the final saved coordinates as the selected nominal endpoint. For each
cohort define

\[
\widehat a_i=(\alpha_f-\widehat\alpha_b)
             +(\beta_{f,i}-\widehat\beta_{b,i}),\qquad
\widehat R_i=e^{-\widehat a_i}.
\]

If e_alpha and e_beta_i are the numerical reconstruction radii, use
\(e_{a_i}=e_\alpha+e_{\beta_i}\). Then

\[
\|R-\widehat R\|_2
\le \max_i\left\{\widehat R_i\operatorname{expm1}(e_{a_i})\right\}.
\]

The STF chart permits the independent determinant bound

\[
\widehat D=e^{-3(\alpha_f-\widehat\alpha_b)},\qquad
|D-\widehat D|\le\widehat D\operatorname{expm1}(3e_\alpha).
\]

This is uncertainty in a recovered finite transport map with the selected
saved endpoint held fixed. It does not include the temporal discretization
error of that endpoint relative to a continuous self-consistent solution.

The existing B3d/e/f positive angular and cohort-error components can consume
these maps, with their existing tolerances and distinct numerical-error
labels. Q14 transported moments should be compared with the old finite14
saved endpoint; a continuum angular rule addresses a different angular model
on the same prescribed geometry. A continuum moment change is not a new
self-consistent geometry solution. Neither calculation supplies B3h absorption
nor a physical total-error radius.

## Minimal executable acceptance conditions

1. Select exact saved N256 PATH/SOURCE_HISTORY/VALIDATION identities and reuse
   the completed birth bindings and old tests. Pair rows by fixture/index/key.
2. Use the receipt's explicit source duration. Check first-half timing and
   source placement; preserve accumulated-clock residuals separately.
3. Validate finite positive matter/radiation inputs, diagonal STF chart,
   positive packet-model provenance and frozen source domain.
4. Evaluate every stage-box closure inequality before accepting that row's
   reconstruction radius; refuse rows outside the box without widening it.
5. Preserve stage radius, representation reserve and physical radius as
   distinct fields. Physical errors eS/en/eE remain null.
6. Hold saved final geometry fixed, preserve signed pi, and keep T separate
   from Q. Reusing already-kicked endpoints requires U=J=0.
7. No IVP, source solve, native REC solve, old test suite or old campaign
   replay is required for this saved-data calculation.

No no-go theorem is proposed. The missing source coordinate bytes are a
reconstruction problem, and this lemma supplies a concrete finite-stage
recovery path under stated, executable conditions.
