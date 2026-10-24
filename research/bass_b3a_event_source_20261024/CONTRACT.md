# BASS_B3A_EVENT_SOURCE_20261024 — frozen source-only contract

## Authority and bounded work
Current user request and physmath-research-loop built-in 1.0.0.
Central handoff: rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17,
research/orchestration_longterm_20261023/assembly/HANDOFF_bass_KO.md.
BASS source base: 28b7705cbb236c26e1b273335f6da7e9da4d1aaf, PR184 Draft/open.
Scope: independent B3a local event-source reference adapter and source-only
connection to one explicitly detached REC line owner. No IVP, old campaign
replay, stock update, native history substitution, merge or production activation.
B1 historical pytest argv/cwd remains unresolved. B2 finite evidence is reused.
The original remaining campaign wall/CPU budgets stay null; budget_reset=false.
The central 120 s NEW scoped local unit ceiling is not a reset of that campaign.
This unit's new measured calculations have a separate cumulative receipt.
At most 60 s for implementation tests/reference/plot combined; stop a scientific
subprocess at 30 s. These are upper bounds, not a new historical balance.

## Source identity
REC current PR130: 93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa.
Select its existing research/rec_line_source_20261023/ LINE01 API, owner_mode
standalone_detached and native_line_owner_active=false. The latest history
boundary's signed net line_ledger is NOT an interchangeable gross event API.
Vendor unchanged line_source.py, escape_moments.py, hyrec_spike_transfer.py
and its license with original relative directory layout. Include the small
STORED_NATIVE_LYA_STATE.json extract and source pins. Never fetch S1/S2 archives.

For actual native scalar inputs reconstruct x2p=xr[1]+3*x1s*exp(-E21/TR),
n_l=nH_cm3*1e6*x1s, n_u=nH_cm3*1e6*x2p,
f_plus=1/expm1(E21/TR)+Dfplus_Lya, H=H_sInv.
Use the frozen effective 2p card. This is a detached full-Planck/stimulated
reference with native scalar inputs, NOT native LINE02 or history parity.
Angular S is an explicitly constructed fixture, not an observed native angular state.

## Physics and units
Signature (-+++), u.u=-1, p=(E/c)(1,n), c=299792458 m/s.
dR is per invariant dt_proper*dV_proper=dV4/c; weights are m^-3 s^-1.
Q^a=int p^a dR. K^ab(u)=c int p^a p^b/(-u.p) dR.
For target-frame u=(1,0,0,0), use r=c*p=(E,E*n):
cQ=sum(rate*r), K=sum(rate*outer(r,r)/r0).
K has units J m^-3 s^-1. PiRate=K_spatial-I*trace(K_spatial)/3.
Changing frame uses r_new=Lambda(beta)r; event-rate weights remain unchanged.
The positive off-diagonal boost convention matches the existing kinetic.py.
For fixed observer, K'(Lambda*u)=Lambda*K(u)*Lambda^T; changing observer
requires the new denominator. Never call kinetic.boost for event weights.

Keep two nonnegative effective escaping-reservoir channels:
dR_down=A*n_u*(1+f_plus)*beta_escape(n)*dOmega/(4pi);
dR_up=A*g*n_l*f_plus*beta_escape(n)*dOmega/(4pi).
This owner eliminates quasi-stationary resonance radiation; these are not
all microscopic trapped-line events. Net=down-up retains its sign.
beta_escape=(1-exp(-t/q))/(t/q), q=1+n.S.n, t=A*lambda^3*(g*n_l-n_u)/(8*pi*H).
Call unchanged owner validate_inputs/_principal_rule/beta_vector.
_principal_rule returns n_i^2 in one octant: restore ALL EIGHT signs of sqrt(n2),
rotate using eigenvectors, assign each sign weight/8, then boost.
No renormalizing weights to force agreement.

Opposite source is the upstream atomic excitation-energy ledger:
du_atomic_internal=-E_line*R, du_radiation=+E_line*R, du_thermal=0.
No ionization/free-electron yield, recoil, new donor bath or thermal source.
In a boosted frame the energy and momentum four-force partners remain equal
and opposite. This does not determine the matter's pressure-rate tensor.

## BASS connection
kappa=8*pi*G/c^4; tau=c*t/L.
U=kappa*L^3*E_dot/c, J=kappa*L^3*force_density.
PiRate_hat=kappa*L^3*PiRate_phys/c.
Only U/J map to Source.energy_transfer/momentum_transfer.
Source.pressure and Source.pi are CURRENT STATE stresses, explicitly supplied
by the caller and copied unchanged; PiRate_hat stays a separate return value.
Use actual unchanged BASS core.py from background_kinetic_g1b_20261023/vendor.
A pure attachment function may create Source from explicit state p/pi and
balanced two-sector transfers, with owner/epoch/frame/clock identity and
duplicate-transfer refusal. Require an explicit positive-domain callback for
nonzero binding; reject missing/false callbacks and never clip populations,
rates, state density or signed net rates. Callback fixtures are synthetic
tests, not certification of a real finite photon reservoir.
No integration or kinetic packet injection is in scope.

## Implementation contract
Use Python stdlib unittest + installed numpy/scipy; pytest/sympy are absent
from default Python and not required. Keep modules small and separate
event-rate representation from kinetic density weights.
Expose typed photon event measure, gross down/up bundle, moment result and
BASS rate pair. Record source owner, epoch, frame, clock and provenance.
Domain rejection: nonfinite/complex/bool arrays as appropriate, E<=0,
negative gross rate, non-unit directions, beta^2>=1, incompatible donor owner,
invalid shear/opacity state, stale epoch/duplicate transfer, callback refusal.
The code must not silently choose a new donor or reinterpret native net rates.

Tests: exact analytic A/B at beta0 and (3/5,0,0), wrong-density-weight
negative control, oblique direction counterexample, non-axis covariance,
gross>=0 and net emission/absorption/LTE, actual donor-call parity at identical
quadrature, full eight-sign restoration (odd moment zero at rest),
BASS equal/opposite U/J and unchanged supplied pi, callback/duplicate refusal.
Local normalized discrepancy gate 5e-12, normalized by gross source scale
near detailed balance; fixed historical B2 2e-8 gate stays untouched.
Do not claim angular continuum convergence from same-grid donor parity.

One NEW diagnostic figure: finite A/B exact boost curve and numeric residual,
with oblique point distinguished and zero correctly displayed. Inspect it.
This figure is a current adapter diagnostic, not a rerender of any old figure.

Required outputs: code, unittest raw log/exit/resource receipt; small current
reference JSON and plot CSV/PNG; source pin/index; README run commands.
Record any failures and targeted repairs, including initial environment gaps.
Independent scientific/code review follows implementation before publication.

