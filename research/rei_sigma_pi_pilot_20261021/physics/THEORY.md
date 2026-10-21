# C15 → (Σ, Π) pilot: physical normalization and positive initial data

Date: 2026-10-21 (Asia/Seoul). Status: **derived**, with the algebra below **CAS checked**. Current code identity supplied by the independent repository inventory and directly inspected here: `rei_bianchi` PR141 head `80825585f9fe31d2ee0d5af545ada3fa1f52be72`, `research/rei_c15_sigma_pi_feedback_20261015/coupled.py`. This file describes a new pilot adapter; it does not promote a source's past execution status.

## 1. Definitions and units

Use metric signature (-,+,+,+), proper time t in seconds, and

\[
ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2,
\quad H=\dot a/a>0,\quad s=\dot b.
\]

In the orthonormal matter frame,

\[
\sigma^i{}_j=\operatorname{diag}(-s,-s,2s),\qquad
\pi^i{}_j=\operatorname{diag}(-D/3,-D/3,2D/3),
\quad D=P_\parallel-P_\perp.
\]

The C15 names `Pi_gamma`, `Pi_nu`, `Pi_massive`, and `Pi_total_source` mean **D in Pa = J m⁻³**, not the user's dimensionless Π. Store their original names/provenance and add explicitly named normalized fields.

The half-contraction convention used by existing C15 is

\[
\Sigma_h=\frac{\sqrt{\sigma_{ab}\sigma^{ab}/2}}{H}
=\sqrt3\frac{|s|}{H},\qquad
\Pi_h=\frac{K_t\sqrt{\pi_{ab}\pi^{ab}/2}}{H^2}
=\frac{K_t|D|}{\sqrt3 H^2},
\quad K_t=\frac{8\pi G}{c^2}.
\]

For the Frobenius convention, Σ_F=√2 Σ_h and Π_F=√2 Π_h. Both should be emitted; the principal plot must label which convention it uses. With the Einstein-equation coefficient κ_E=8πG/c⁴, the same Π_h is κ_E c²|π|_h/H². Omitting this c² when H is per second is dimensionally incorrect. Alternatively geometric H/c and σ/c give the equivalent inverse-length formulation.

C15's constant is K_c=8πG/(3c²)=K_t/3, so its normalized output adapter is

\[
\boxed{\Pi_h=\sqrt3\,K_c|\texttt{Pi_total_source}|/H^2}.
\]

Keep signed `s`, `D`, `shear_sign`, and `stress_sign`: norms lose the sign of the physical energy transfer

\[
\sigma_{ab}\pi^{ab}=2sD.
\]

In particular (+s,+D), (+s,-D), (-s,+D), and (-s,-D) need not produce the same evolution. At s=0 the C15 `orientation` must be exactly 0. At D=0 report stress orientation 0. A later sign change is physical and is not a case-identity change.

## 2. Einstein coupling and constraint

For flat Bianchi I and total energy density ρ and isotropic pressure p,

\[
3H^2=K_t\rho+3s^2+\Lambda c^2,\quad
\dot s+3Hs=K_tD/3=K_cD,
\]
\[
\dot H=-\frac{K_t}{2}(\rho+p)-3s^2,\quad
\dot\rho+3H(\rho+p)+2sD=0.
\]

For interacting species the last equation contains Q_A, with Σ_AQ_A=0 only after every donor/receiver reservoir has been included. Substitution gives d(3H²-K_tρ-3s²-Λc²)/dt=0. This checks the factor 1/3 and the work sign. C15 uses an external MD14 stellar source and a Case-A energy escape ledger; its existing owner statement leaves the full stellar/escaped-radiation Qᵃ closure open. The plot's science label must preserve that scope.

Let H_base be the actual source's zero-shear initial H including its fixed gas/massive energy correction. A chosen Σ_h at the initial surface maps to

\[
H_i=\frac{H_{\rm base}}{\sqrt{1-\Sigma_{h,i}^2/3}},\qquad
s_i=\epsilon_s\frac{\Sigma_{h,i}H_i}{\sqrt3},
\quad 0\le\Sigma_{h,i}<\sqrt3.
\]

At fixed positive non-shear energy, Σ_h=√3 is outside this finite-H initial-data chart. No tolerance modification is required: generate an interior grid. The actual source's existing constraint implementation should remain the authority for H_i.

## 3. Two independent initial axes without invented stress dynamics

The existing C15 distribution is a positive pure-P₂ deformation,

\[
f(q,\mu)=f_0(q)[1+\alpha P_2(\mu)],\quad
P_2=(3\mu^2-1)/2,\qquad -1\le\alpha\le2.
\]

Its monopole is independent of α, and

\[
\langle P_2\rangle=\alpha/5,\quad
\langle\mu^2\rangle=1/3+2\alpha/15.
\]

Thus for initial photons or massless neutrinos D=ρα/5. The `initial_moments` function implements precisely J₀=1, J₂=α/5. **The inverse Π→α map contains a factor of 5.**

For C15's massive particles at x=b=0, with source radial weights r_w, energies E_q=√(m²+q²), and source normalization N=Σr_w E_q,

\[
J_{0,m}^{(1)}=\frac{\sum_qr_w q^2/E_q}{N},\qquad
D_m=\frac{\alpha_m}{5}\rho_{m,\mathrm{ref}}J_{0,m}^{(1)}.
\]

This follows from the separate radial/angular measure and the same P₂ orthogonality. It uses the actual finite radial quadrature of the pinned source; no Maxwellian or cold-fluid closure is introduced.

A clean one-parameter stress family sets α_γ=α_ν=α_m=α. Empty initial UV stock contributes D_UV=0, while the gas starts isotropic. With all three corresponding feedback terms enabled, define

\[
W=\frac{\rho_{\gamma,i}+\rho_{\nu,i}+\rho_{m,\mathrm{ref}}J_{0,m}^{(1)}}5>0,
\quad D_i=\alpha W.
\]

The exact initial adapter is then

\[
\boxed{\alpha=\epsilon_\pi
 \frac{\sqrt3 H_i^2\Pi_{h,i}}{K_tW}
 =\epsilon_\pi\frac{H_i^2\Pi_{h,i}}{\sqrt3 K_cW}}.
\]

For `massive_fraction=0`, remove the last term in W and retain the same formula. A family with common α and the original default massive fraction can be used without changing the matter-budget model. The initial energy correction and H_base are α-independent because angular quadrature integrates P₂ to zero. Roundoff-level monopole residuals must be recorded, not silently treated as new energy.

The admissible requested interval depends on the chosen Σ_i through H_i²:

\[
\Pi_{h,i}^{(+)}\le\frac{2K_tW}{\sqrt3H_i^2},\qquad
\Pi_{h,i}^{(-)}\le\frac{K_tW}{\sqrt3H_i^2}.
\]

Use a rectangular grid inside the minimum cap across selected Σ and signs, or record an explicitly masked domain. Do not clamp an inadmissible Π to α=±boundary and relabel it as the requested coordinate. If a zero stress control is required, α=0 for every active species; changing only photons while retaining anisotropic massive/neutrino seeds does not give Π_i=0.

The broader nonnegative massless distribution only requires D/ρ∈[-1/2,1], from 0≤⟨μ²⟩≤1. The pure-P₂ family occupies the narrower range D/ρ∈[-1/5,2/5]. This is a chosen initial family, not a universal bound. Σ_i and Π_i alone do not determine higher angular or momentum moments; the common-P₂ family supplies that missing specification.

## 4. Scope of today's initial pilot

Pinned C15 evolves a=.1999→.2, approximately z=4.00250125→4, from its explicitly warm gas state. It includes gamma/neutrino angular transport and Thomson terms, positive finite-mass source quadrature, native MD14 UV births and H/He Case-A chemistry, plus stress-sourced shear and the Hamiltonian H. Its time interval and initial thermochemical state must be visible in figure labels/captions. The correct deliverable is a **short near-z4 preliminary 2D initial-condition sweep** in the existing model. Extending its interval to reionization onset requires independently supplied thermochemical initial conditions and closure work.

At minimum each case must store the requested Σ_i,Π_i, both signs, achieved values from `initial()`, α, H_i,s_i,D_i, W, source SHA, source grid, L, step count, the actual final a, and any failure. Useful first panels are final Δx_HII and ΔT versus the same-Σ, zero-initial-stress control, plus Σ(a),Π(a) trajectories. Include the all-zero isotropic control. Finite data should not be interpolated across masked failures without showing them.

## 5. Reusable algorithms and near-term acceleration

Today's objective favors independent case parallelism with one numerical library thread per worker, one prepared source/calibration per process, cached readonly angular operators/radial arrays/rate tables, and compact result tables. Existing C15 already has a reduced massive three-moment evaluator; preserve its source identity and reuse it. Generating parameter tangent states is unnecessary for this first direct sweep. Compile/load once, checkpoint each successful case, and plot completed cases while others run. A changing worker count must not change scientific case IDs or invalidate their successful output identities.

All of these are implementation recommendations; no speedup is claimed here. Source-hash equivalence and a small physical adapter check are appropriate, whereas an optimization benchmark campaign is outside this request.

## 6. Evidence and references

Direct inspection: C15 `Parameters`, `initial_moments`, `initial`, `massive_source_3moments`, `_physical`, `rhs`, `run`; original PR140 radial constructor/moments. Repository SHA and file hashes are in the accompanying evidence JSON.

Wolfram returned σ² contraction=6s², π² contraction=2D²/3, σ:π=2sD; normalized angular integrals 1, 1/3+2α/15, 1/5+4α/35; D/ρ=α/5; exact positivity α∈[-1,2]; and the constraint derivative 0. It emitted an undefined-global-symbol warning for symbolic variables while returning these exact expressions. That warning is preserved; no numerical runtime claim depends on it.

Literature support: Ho Lee, Ernesto Nungesser and Paul Tod, *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology*, GRG 52,48 (2020), DOI 10.1007/s10714-020-02699-7, arXiv:1911.04937. Sec.2.1 gives the shear equation and constraint with K_t=1; Sec.2.2 shows that the stress-moment hierarchy depends on higher moments. Its small-data collisionless asymptotic theorem is not a reionization result. [Primary preprint](https://arxiv.org/abs/1911.04937), [readable primary-text mirror](https://ar5iv.labs.arxiv.org/html/1911.04937).

J. Mark Heinzle and Claes Uggla, *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations*, CQG 23 (2006), DOI 10.1088/0264-9381/23/10/016, arXiv:gr-qc/0512031. Reuse: positive fixed Killing-momentum distribution and its geometry-dependent stress integrals. Its normalization differs from Σ_h and is not copied into the plot axes. [Primary preprint](https://arxiv.org/abs/gr-qc/0512031), [readable primary-text mirror](https://ar5iv.labs.arxiv.org/html/gr-qc/0512031).

Both were found using the selected Exa and SciSpace tools; primary sections were read through Exa. Source tools are discovery/verification aids; the adapter equations above were independently derived. No new no-go theorem is claimed.
