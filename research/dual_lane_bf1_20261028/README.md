# BF-1: exact fixed-gauge spatial carrier projection

Status: COMPLETE_SCOPED_FIXED_GAUGE_PHYSICAL_CARRIER_PROJECTION. Parent PR211 at1100fbb57230de2cac412c332f58ce8060210535; isolated draft PR213. No production mutation, merge, kinetic IVP or old campaign replay.

The standalone adapter averages physical P8 carrier in one common observer/coframe and matched momentum/screen labels. It does not average log intensity, enforce monopole backgrounds, clip signed fluctuations or solve Einstein constraints. Spatial weights are normalized by definition; angular quadrature weights are not renormalized.

For fixed positive weights p, P(F)=broadcast(sum p F). P^2=P and P(F-PF)=0 exactly. Physical volume weights obey pdot=p*(theta-mean(theta)), so mean_dot=mean(Fdot)+Cov(theta,F). A homogeneous Bianchi-I volume factor cancels from normalized p: Pdot=0 there. The nonzero-Pdot fixture is an explicitly inhomogeneous prescribed conformal volume on the same reference torus, not a Bianchi-I/EFE solution. The primary baseline is reference-coordinate/Haar projection; volume projection is a separately identified option.

Frame mapping is pure SO(3) on paired physical rays. Its derivative includes Rdot J R^T + R J Rdot^T. Generic angular remapping, frequency interpolation and boosted observers are not admitted. The map is linear in the carrier at fixed measure; metric-dependent volume makes the joint state map nonlinear.

## Constructive checks

13 unique tests passed. Science rows:552 angular-basis projections (all I/E/B/V through ell4;3 spatial resolutions;2 measures),6 mixed positive fields,3 frame tests,3 measure tests,4 finite-difference derivative checks,9 ADM counterexample fixtures. New IVPs0, historical campaigns0. Max idempotence1.11e-16, zero-mean1.20e-16, mixed harmonic commutator1.78e-15, frame-rate5.55e-16. Reference background I40=.3 is retained, not discarded.

For F=1+.7cos x and volume exp(.65cos x) with bdot=1.1/T_star, exact mean1.2162739424163878 and mean derivative.3304952864813792/T_star. Local Fdot=0: omitting measure derivative changes the answer. Time-dependent zero-mean condition is P xidot=-Pdot xi, not P xidot=0.

A positive spatial metric average is not an ADM constraint solution. On gamma=I at a torus initial slice, K=L_star^-1[-k0 I+alpha cos(x/L_star)diag(0,1,-1)] and16piG epsilon/c^4=L_star^-2[6k0^2-2alpha^2cos^2(x/L_star)] satisfy both constraints pointwise with positive density for the tested amplitudes. Averaging gives H_ADM=alpha^2/L_star^2. At k0=.4,alpha=.3 the residual is.09, exactly the extrinsic-curvature variance. This is an initial-data counterexample, not an evolved Einstein solution or a no-go theorem.

Full and background screen carriers are PSD under positive weights; fluctuations need not be. No positivity clipping is applied. Average of exp(plus/minus.8) is1.3374349463, not exp(mean log)=1.

## Reproduce

From this directory: `python -m pytest tests/test_projection.py -q`.

The complete immutable ZIP additionally includes the full `verify_bf1.py`, raw rows, Korean report/handoff, detailed DAG, saved-data validator, CAS source/result, figure, failure logs, execution ledger and manifest. Run full scientific regeneration from that ZIP with `python verify_bf1.py`; `python verify_saved.py` only validates saved evidence. Git contains the exact tested core/tests/vendor plus concise evidence/contract/DAG and delivery receipt, not every archive byte.

An actual implementation failure is retained: ndarray self.pdot shadowed method pdot. All science rows had already been saved. A regression reproduced it; the ndarray was renamed weight_rate; saved rows were resumed for final checks without replay. No physics or tolerance change. Native subagent and independent-model review NOT_RUN; external CAS is a separate check.

Progress7/15 counts source mapping and scoped research, not global physics completion. BF2 is the next existing node: local frame-aware collisions followed by spatial mean. No auto-next, production/Rust, general observer alignment, spatial kinetic PDE or Einstein feedback claim.
