# BASS_B3B2_LOCKED_CELL_BRIDGE_20261024 — frozen implementation contract v1, R6 clarification

## Authority and scope

Parent BASS `research/bass-b3b-finite-line-exchange-20261024` at
`78a4e7a4a36fa826c2e3d196254f77109d5ae5be` (PR186, Draft/open/unmerged).
Central current AGENTS blob `429a5a13ee75b1222bc50627f8d5973d01dd21c4` applies;
fixed central authority and handoff remain unchanged. Apply the explicit
physmath-research-loop 1.0.0 workflow. This is an opt-in research snapshot adapter.

Implement a reversible, labelled conversion of the actual REC locked discrete
photon inventory into BASS massless packets. Preserve the represented number
four-current and stress-energy tensor. Include explicit state boost covariance.
Do not evolve an IVP or collision operator. The source-conditioned saved REC
occupation is an input state, not a validated full trajectory or LINE01 f_plus.
Its actual builder evaluates a scalar history at COM arithmetic centres, restores
Planck plus distortion, and repeats the result under an explicit scalar,
unpolarized isotropy axiom in the hydrogen tetrad. This is bootstrap INITIAL-DATA
from the validated Bianchi-II builder, with `coupled_macro_endpoint=false`.
General anisotropic tests of the bridge are separately labelled synthetic
diagnostics on the actual grid, not recovered native angular information.

## Source inputs and ownership

REC current owner HEAD `ae189694c15e09c6f96c44ef6b74b48afc2632ac` supplies three
byte-verified NPZs at `b3b2_work/rec_intake/inputs/data/`; exact identities are in
`rec_intake/NPZ_INPUT_IDENTITY.json`. Load with `allow_pickle=False`:

* `z1100_direct_network_node.npz`: `mode_measure_m3` G_i, `momentum_scale` p_i,
  `state_labels`, `state_intervals`.
* `pr01c_background_snapshots_v048.npz`: `directions` n_j and `angular_weights`.
* `pr05c2c1b2b1e0_source_derived_parent_v073.npz`: `occupation` f_ij.

G is in m^-3, p in kg m s^-1, f dimensionless, and angular weights A sum to one.
Reproduce the actual REC HarmonicGrid normalization A=raw_weights/sum(raw_weights)
in the data-loading adapter and record raw sum. The general bridge requires an
already normalized angular grid and never silently normalizes invalid inputs.
Hydrogen local tetrad is the source frame. No rate clock is assigned to a snapshot.
The physical energy owner is **E_i=c p_i**, from the saved network. Recomputed
geometric frequency centroids, line-centre energies and target-energy arrays in
the parent payload are diagnostic inputs only; none replaces momentum_scale.

## Equations

Use metric (-,+,+,+), physical c=299792458 m/s. Let ell_j=(1,n_j) and
alphaL=kappa L^2. Require finite real positive kappa,L,Pstar and finite positive
G_i,p_i,A_j, unit n_j, finite nonnegative f_ij including exact vacuum.

n_ij = G_i A_j f_ij,
N^a = c sum_ij n_ij ell_j^a,
T^ab = sum_ij c p_i n_ij ell_j^a ell_j^b.

BASS k_ij = (p_i/Pstar) n_j, mass=0,
w_ij = alphaL c Pstar n_ij.
Existing unchanged kinetic.tensor must yield alphaL T. Existing kinetic.moments
yields rho_hat, energy-flux/c hat, mean pressure_hat and **state pi_hat**.
There is no U, J, PiRate_hat or Source construction in this adapter.
Number current recovered from packets is N^a=(1/(alphaL Pstar)) sum w ell^a.

Fixed-grid inverse: f_ij=w_ij/(alphaL c Pstar G_i A_j). Preserve cell/angular
labels and input identity; require original frame and matching k/mass/grid.
Reject an incompatible packet frame/grid instead of guessing a rebinning.
For an explicitly inverted boost with original labels, floating roundtrip may
be checked against the same original grid within the frozen tolerance.

State boost convention is existing kinetic.boost: active plus-sign beta,
Lambda00=gamma, Lambda0i=Lambda_i0=gamma beta_i.
D=E'/E>0, number-density n_ij'=D n_ij, w_ij'=D w_ij,
ell_j'=Lambda ell_j/D. The spatial direction n_j instead transforms as the
spatial part of ell_j'; the number-density rule is not a direction rule.
Then N'=Lambda N, T'=Lambda T Lambda^T. This state-density reweighting is correct
here; it is not the B3a invariant event-rate dR transformation.

## Implementation and allowed paths

Create only `bass_source/research/bass_b3b2_locked_cell_bridge_20261024/` with
`code/`, `tests/`, `vendor/`, `inputs/`, `artifacts/` and concise implementation
documentation. Copy unchanged existing B3b vendor/core.py and kinetic.py plus
their required local dependencies (inspect imports; no rewrite). Copy the exact
three NPZ inputs. Root owns contract/theory/intake/stage/backup/publication docs.
Do not edit existing lanes, the core solver, project policies or external repos.

Use small explicit data structures, finite-real validation before conversion,
strict positivity where mathematically required and nonnegative weights/f.
Preserve zeros; no epsilon seed, clipping, fake donor, bath, width or rate.
Detect nonfinite arithmetic and positive inputs erased by underflow rather than
silently declaring vacuum. No broad serialization or security framework.

## Acceptance and meaningful experiments

Use direct physical sums independent of BASS packet formulas as the oracle.
Relative residuals use an L1 absolute-contribution scale, not division by a
vanishing tensor component. At most 512 machine eps for 910-packet sums/boosts;
roundtrip individual positive f at most 128 eps relative, exact-zero preservation.
These are floating checks, not interval certificates. Record actual residuals.

Cover actual 35x26 input, true vacuum, isotropic and angularly anisotropic
diagnostics, scalar unit rescaling (L and Pstar), exact synthetic rational oracle,
boost beta=(3/5,0,0) plus a non-axial beta, explicit inverse boost, and invalid
complex/negative/nonfinite data. Add only tests addressing real contract risks.
Tests must detect wrong G normalization, geometric/line energy substitution and
omitting state boost weight factor. No full old suite rerun.

Produce a real figure and machine-readable data with:
1. actual source photon stock by locked cell label/energy;
2. N and T covariance residual versus beta, plus deliberately omitted weight
   reweighting as a clearly labelled rejected mutation;
3. photon-number/energy residual from one explicit energy-owner mutation, using
   the actual competing target-energy data if meaningful, or a labelled synthetic
   perturbation (do not invent a Doppler width).
State what plotted exact zeros mean; don't fabricate a log floor as measured data.

## Execution, failures, review and stopping

Use Python/NumPy and matplotlib already available. Scientific per-command guard:
wall <=30 seconds, CPU <=20 seconds, one thread. New-unit aggregate prospective
guard wall <=120 seconds, CPU <=60 seconds; root maintains observed accounting.
This guard is separate from historical campaign remaining wall/CPU=null and
budget_reset=false. New IVP=0; old campaign replay=0; old archive download=0.
New specific source-input downloads=3 / 746322 bytes, already completed.

Record exact argv/cwd, exit codes, elapsed wall and CPU, stdout/stderr, code/input
hashes, package versions and all failed attempts. Implementation agent may repair
plain implementation defects without changing equations or acceptance thresholds;
return substantive ambiguity or failure interpretation to the controller.
No remote writes or git operations by implementer. Fresh Astra review must read
actual diff/raw results and figure before scoped admission/publication. A concrete
finding receives one targeted repair and affected regression; stop optional testing
when the claim is sufficiently verified.

## Claim boundary and next edge

Successful bridge closes actual locked finite photon inventory -> BASS state
representation and observer covariance. It does not close LINE01 incident-boundary
reconstruction, native atomic-source replacement, gross absorption/emission event
ownership, or a time-dependent coupled background. Geometric continuum cell
moments and arbitrary unresolved spectral moments are not reconstructed.
B3b finite f=0 source result, B3a event/state distinction, B1 exact historical
pytest argv/cwd gap and B2 scoped evidence remain intact. No new strong no-go
theorem is claimed. No merge or production activation.
