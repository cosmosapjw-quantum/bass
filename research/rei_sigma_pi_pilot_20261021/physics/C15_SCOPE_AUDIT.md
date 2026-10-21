# Independent C15 pilot scope and initial-grid audit

2026-10-21 (Asia/Seoul). Reviewer task: `physics_bridge`. This review did not implement the root's sweep. Source inspected and initialized: REI PR141 commit `80825585f9fe31d2ee0d5af545ada3fa1f52be72`, `research/rei_c15_sigma_pi_feedback_20261015/coupled.py`, SHA256 `a920d0e86c0badf395bfabc61dafaee3449a34e4cfe8ccdc28a833674c1c4b1e`.

## Decision

**The proposed 81 signed cases are admissible initial data for the declared C15 model. Proceed with the fixed near-z4 preliminary sweep.** This is `PASS_SCOPED_INITIAL_MAPPING`; this review ran constructors and initial-state evaluation only, with zero ODE, step, run, or benchmark calls. The scientific deliverable should emphasize the shear/stress response. Thermochemical differences remain fixed-discretization exploratory outputs unless a specific paired-difference check resolves them.

The scalar normalization uses half contractions, consistent with existing C15. Also emit Frobenius values (=√2 times the principal values), signed s and D, requested and achieved initial invariants. Common angular seed α_γ=α_ν=α_m specifies higher moments that Σ and Π alone would not fix.

## Actual initial-state check

Grid:

- Σ_i = [0, 0.0005, 0.001, 0.002, 0.004].
- Π_i = [0, 0.00005, 0.0001, 0.0002, 0.0004].
- Both signs for each nonzero axis, zero orientation for a zero axis: 81 unique physical initial states.
- Massive fraction 0.1, m/T=30, L=8; actual source grid 8X8.

The actual owner constructor gives H_base=1.3845102779768001×10⁻¹⁷ s⁻¹ and W=1.7330655184511486×10⁻¹¹ Pa, where D_i=αW. The smallest negative-stress cap over the grid is Π_i=0.0009742352677892767; the positive cap is twice this. The maximum requested Π_i=0.0004 requires |α|≤0.4105784436521941, strictly within [-1,2].

All 81 actual `initial()` calls preserve the intended shear norm exactly at the stored precision. Maximum |Π_achieved−Π_requested| is 2.8731357570865868×10⁻¹⁸. All massive physical quadrature weights are nonnegative. The source's initial Hamiltonian residual is zero in the evaluated expression. This is a valid implementation/initialization check, not an independent integrated Raychaudhuri check.

At α=0, actual massive quadrature leaves D=3.8492560322062353×10⁻²⁶ Pa through roundoff. Preserve this raw value. A zero-request case may have an unresolved stress orientation; do not alter physical weights or subtract this residual from every subsequent moment.

Detailed values for every signed case are in `C15_SCOPE_AUDIT.json`; the independent source calibration is in `C15_INITIAL_CALIBRATION.json`.

## What is included and what remains conditional

The source's `_physical` function **does include gas nonrest energy in the Hamiltonian H**, through `ugas = nh * EV_CM3_TO_J_M3 * ugas_H` and the `+KAPPA*ugas` term. Thus an assertion that all gas U is omitted from gravity is incorrect for this source. The saved histories show a gas-nonrest contribution to H² of up to 1.3569466942122195×10⁻⁹. Gas pressure is isotropic in the specified thermochemical model, so its contribution to D is zero by that modeling choice.

The external MD14 source injects energy without an evolved stellar donor; Case-A recombination escape has an energy ledger but no evolved escaped-radiation stress tensor. There is no specified total Qᵃ closure. The implemented C15 object is the definite model obtained from its positive source transport/chemistry, sourced shear equation, and Hamiltonian constraint. It is interpretable as a conditional short-interval feedback experiment with that forcing.

This distinction matters algebraically. If the modeled material energy obeys

\[
\dot\rho+3H(\rho+p)+2sD=Q_{\rm ext},
\]

while 3H²=K_tρ+3s²+Λc² and ṡ+3Hs=K_tD/3 are imposed, differentiation yields

\[
\dot H=-K_t(\rho+p)/2-3s^2+K_tQ_{\rm ext}/(6H).
\]

The last term disappears in a closed total stress-energy system. Its presence explains why Hamiltonian enforcement plus correct shear sourcing alone does not establish a complete Einstein–matter solution. No donor reservoir is invented in this pilot; this is an explicit model-scope limitation.

## Quantitative size of the already recorded external energy budget

The following calculation reuses the eight stored C15 histories and their ledger baselines. It performs no new dynamics. The source's exact tabulated mean birth energy is 20.276595394305048 eV. A stored history with N_src≈0.00951193 photons/H therefore injected E_src≈0.19286954 eV/H over a=.1999→.2.

For the stored cases every directional expansion rate is positive. Photon/thermal expansion work is therefore nonnegative. The exact source ledger structure gives

\[
E_{\rm esc}=E_0+E_{\rm src}-E_{\rm gas,end}-E_{\rm UV,end}-W_{\rm geom}
\le E_0+E_{\rm src}-E_{\rm gas,end}-E_{\rm UV,end}.
\]

This yields an escape-energy upper bound near 0.00460049 eV/H in the first stored case. Converting the emitted energy plus this escape bound to endpoint proper energy density and multiplying by K_c/H² gives at most 2.4400286342762874×10⁻¹¹ across the eight stored cases. At fixed remaining state the corresponding instantaneous relative H scale is at most 1.2200143171455857×10⁻¹¹, using r/[1+√(1−r)].

This is a **conditional incremental energy-budget bound**, assuming the same initial donor rest energy is already represented in the baseline and only its known emitted energy is debited. It does not bound an unspecified donor's initial anisotropic stress, neglected recoil, full Qᵃ dynamics, or errors propagated into downstream observables. It also does not replace the missing physical reservoir. The actual baseline source and each budget are retained in the JSON.

## Numerical scale relevant to the plot

Existing source evidence, `C15_STUDY_RESULTS.json`, SHA256 `40c0ae6325fdba5cf47f8240ee655769c1f236351a2c9004e7f3488d16647b7e`, records one 64→128 refinement comparison:

| Endpoint quantity | Stored adjacent-grid difference |
|---|---:|
| Σ | 1.3305564112384973×10⁻¹⁸ |
| b | 1.2260044524257629×10⁻²² |
| x_HII | 6.328815136735777×10⁻⁶ |
| T_gas | 0.0672706095429021 K |

The same source's 8X8→32X8 spectral comparison has |Δx_HII|=2.837299964419948×10⁻⁷ and |ΔT|=0.08497612348219263 K. These are empirical differences for the stored configuration, not universal bounds and not convergence evidence for each new signed case.

Paired differences at the same discretization may cancel substantial common error, but their cancellation must be checked before claiming a resolved weak thermochemical effect. A useful single check compares a selected signed corner-minus-matching-Π=0 control at 64 and 128 steps. It tests a physical difference and is unrelated to performance benchmarking. If the difference remains unresolved, retain the computed panel with that label and emphasize Σ/Π feedback; do not suppress the available preliminary result.

The source interval is a=.1999→.2 (z≈4.00250125→4) and its initial gas has T=12000 K, x_HII=0.4, helium fractions (HeI,HeII,HeIII)=(0.2,0.5,0.3). These are conditional warm initial data. They are not a primordial/recombination initialization or a full EoR history. First-plot captions should state this interval and initialization directly.

## Minimal stop condition for this review

The mapping and physical-domain questions are closed for the pinned source and proposed grid. The next action is the planned 64-step sweep using available resources, preserving raw failures, followed by independent inspection of the actual sweep outputs and plotting code. No additional normalization/positivity audit is needed unless the source, grid, norm, or initial-family contract changes.
