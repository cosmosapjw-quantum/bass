# B3g actual saved cohorts; B3h native source binding; B3i geometry adapter

Unit BASS_B3G_ACTUAL_BINDING_20261025. Workflow physmath-research-loop 1.0.0.
Root freezes/adjudicates; a lower-tier worker implements; distinct scientific
reviewers inspect the source, derivation, changed code and actual raw results.

## Authority, goal and work boundary

Base bass@d6af237b66e78ca6ed4572068f6bc1a805bbb2d9, parent scientific owner
cc602e209e7deeb511ab2a1f3b2268d55206c43c. New consumer lane is this directory;
branch research/bass-b3g-actual-cohort-binding-20261025. No REC or old BASS edit.
Central contracts: rei_bianchi@641a725ada4be27473069c2c35005a94c2ab0248,
research/orchestration_expansion_20261025/contracts/{B3g-actual-cohort-binding,
B3h-native-finite-absorption,B3i-calibrated-geometry}.json.
Latest central observed 78f7ac5864d5817ceb79b48cb5e298cc30006510, AGENTS blob
429a5a13ee75b1222bc50627f8d5973d01dd21c4. BASS branch tree has no governing
root/research AGENTS; historical nested copies are provenance. Existing scratch
had no checkout; one sparse recovery checkout was created and is now reused.

Goal: bind actual saved B3c birth receipts to B3f; expose the actual REC
scalar input with its reference/owner; implement a per-sector SI-to-fixed-scale
geometry bridge and a conditional geometry-error map. This is the shortest
available input-dependent continuation. A physical finite absorption
transaction and calibrated REC geometry require the missing selected-channel
inputs listed below. Other future providers are not prerequisites.

## Exact recovered inputs and reuse

1. B3c source ZIP, first actual restore in this turn:
   /workspace/scratch/7aa4d0cea548/b3c_recovery/BASS_B3C_S2_FINAL_20261024.zip,
   7021644 bytes, SHA256
   0d3a911d7fc1b567c0e915cd655af94bff44495849bd0e7ce1bcb778a94bd1b2,
   Dropbox id:BSpOijBcT10AAAAAAD_9hw, /BASS_BACKUPS/BASS_B3C_S2_FINAL_20261024.zip.
   CRC verified. Source under restored/research/bass_b3c_bounded_f0_background_20261024.
   Use only raw/{ISO,ANISO}_N256_{PATH,SOURCE_HISTORY}.json,
   raw/VALIDATION.json, code/bounded_background.py, CONTRACT.md, THEORY.md,
   RESOURCE_LEDGER.json, ADMISSION.json and existing reviews/receipts as needed.
   All 12 old IVPs and prior angular campaigns are reused, never rerun.
2. B3f source and finite error routines are unchanged in sibling
   bass_b3f_cohort_input_error_20261025. Import its ball/compose after verifying
   file identity; do not run nominal_data or its sweep/tests. Birth R=I is an
   exact identity at the same frame/event. Birth B_T=0 in exact arithmetic
   because q=1+n^T S n and the represented Q14 rule integrates degree four.
3. REC actual history at ea89c97abeb7a663a813f00e9aadddaf0b32a6a9:
   data/pr05b2_source_history_v060.npz, 35239470 bytes, SHA256
   d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1.
   Already restored to /workspace/scratch/7aa4d0cea548/b3g_rec_recovery/.
   HISTORY_ADMISSION.json is the existing owner result with 313 queries;
   read/reuse these rows rather than recomputing KS01/PB01 interpolation/JVP.
   Physical error radii remain null. Do not replace R by Ks or photon n by nH.
4. REC native line files restored under /workspace/scratch/7aa4d0cea548/b3h_recovery/
   with RECOVERY_MANIFEST.json. Copy selected original bytes, preserve their
   source commits and hashes. Native LINE02 and standalone LINE01 conventions
   must be distinct. Native constants are not replaced by modern constants.
5. G1B and B3a/b/b2/d/e/f saved admissions, bounds, costs and failures are
   unchanged evidence. Reuse source-free G1B; no old test or trajectory replay.

## Required implementation and results

### B3g: actual birth cohort consumer

For both N256 histories, consume all 256 source receipts without re-evaluating
the source owner. A row carries original transfer key, source snapshot/hash,
tau birth/interval, fixed L, proper seconds, frame, card, closure, S, integrated
number density n_b=ledger.down_m3, E_b=the unchanged card.energy_J, R=I, detR=1.
Source is the existing manufactured cold/non-tilted/recoil-free detached
f_plus=0 Bianchi-I model, not a calibrated REC cosmology. Retain that label.
The receipt is already integrated over proper time: never multiply by dt again.
Upward counts must be zero in this selected source; reject otherwise.

Recompute birth T00=E_b*n_b, T0i=0,
Tij=E_b*n_b*(I/3+2*S/15) and signed pi=2*E_b*n_b*S/15.
Compare against saved owner delta_u_radiation, radiation_spatial_packet and
energy_PSTF_packet on the positive E_b*n_b scale. Check atomic upper loss,
total atom preservation, proper duration=L*dtau/c and number positivity.
Tolerance for representation checks: 512*binary64 epsilon; preserve signed
residuals. No rest energy may be used as a denominator for these checks.
Check roundoff on atom stocks on their declared positive stock scale separately.

Physical radius table: eR=0 with provenance R(t_b,t_b)=I; eS=en=eE=null with
source-qualified missing reasons. B3f.ball(S,I,n_b,0,eR=0,eS=None,en=None)
must return INPUT_ERROR_UNSPECIFIED. Source-energy uncertainty is a separate
field outside the inherited fixed-E B3f theorem. No total 2e-8 physical claim.

Do not invent transport R to the final endpoint. SOURCE_HISTORY stores N,H,S
at the midpoint but not midpoint beta. Nominal alpha_birth can be reconstructed
from -log(N_mid/N0)/3 with arithmetic reconstruction error kept separate;
beta_birth and its interpolation error are not stored.
Mark actual final R INPUT_DEPENDENT with exactly these missing fields.

### G1C: conditional transport-error implementation

Implement the diagonal finite bound in theory/TRANSPORT_AND_GEOMETRY.md:
Rhat_i=exp(-a_hat_i), eR=max_i[Rhat_i*expm1(e_i)]. Missing e_i returns null.
Finite inputs require real length-three arrays and nonnegative radii; reject
overflow/nonfinite results. Keep supplied physical e_i and numerical e_i in
separate records and optionally compose by their sum with explicit provenance.
For STF beta and an alpha error bound, the determinant bound is
Dhat*expm1(3*e_alpha). Do not derive it from incomplete stored samples.
Implement the optional constant-envelope Duhamel bound with physical and
numerical forcing terms separate, using stable expm1 and the m=0 limit.
This new analytic theorem is conditional on supplied interval-wide envelopes;
saved sample residuals are not such envelopes.

### B3h: native scalar source and finite donor readiness

Read exact STORED_NATIVE_LYA_STATE and SOURCE_PARTITION_FACTS. Export native
departure Dfplus_Lya and native reference identity. If a full occupation is
shown, native Wien=exp(-E21/TR)+Dfplus and standalone Planck=
1/expm1(E21/TR)+Dfplus are separately named. Their reference laws are never
interchanged. Use native E21 and existing eV-temperature units. Preserve
LYA_FACT and hPc in original native source; present any modern-constant delta
only as a source-model change, not roundoff. Native owner scope is the direct
Trr[1,1]+=r and sr[1]+=r*b pair. Copy existing instantaneous ledger; do not
recompute a new native source transaction.

Provide a typed readiness function for a finite incident donor binding. Needed
fields: source/query owner and source identity; selected species/state/isotope
mapping; frame and proper clock; spectral/angular/time support; donor inventory
and measure; actual link from donor cells to the incoming face; common volume
or an explicit local-density volume convention; atomic energy/recoil owner;
physical error radii. Distinguish structural/physical-model readiness from
uncertainty certification. A physical radius may be null with conditional
status; a missing donor/face mapping must not authorize absorption.
Current source-only row must return exact missing structural fields and
physical_finite_absorption=false. Do not invent isotopic precision or a donor
bandwidth, use B3b2 initial cell averages as a face trace, run absorption with
an infinite bath, or apply post-hoc clipping. Tests may use explicit synthetic
metadata and must label it; no synthetic result is an actual input admission.

### B3i: per-sector geometry bridge, no new trajectory

Reuse stored ISO/ANISO PATH endpoints (257 each) and validation fixture L.
At each endpoint retain three sectors: lower rest R, excitation X, radiation.
Build SI T from saved rho/alphaL and pi/alphaL, with radiation p=rho/3,
R/X p=pi=0. The selected model has exact antipodal flux=0; tag that symmetry
closure rather than interpreting the scalar flux residual as a vector.
Implement SI-to-core conversion using unmodified core.FixedScale/Source:
rho_hat=alphaL*T00, flux_hat=alphaL*T0i, p_hat=alphaL*tr(Tij)/3,
pi_hat=alphaL*(Tij-pSI*I). If requested, check symmetry/STF on an appropriate
positive sector scale, with no projection/clipping of physical stress.
cQ is an energy-equivalent four-vector rate in J m^-3 s^-1;
U,J=alphaL*(L/c)*(cQ0,cQi). A Q rate is not added to T or pi.
Stored B3c endpoints have already applied source kicks, therefore Q=0 and
all source U,J=0. Internal source test pair has opposite radiation/excitation
cQ and no rest transfer. Signed pi is kept. Never treat this as thermal heat.

For all 514 saved endpoints check conversion roundtrip and radiation trace;
for first/final ISO/ANISO endpoints call existing core.rhs once per endpoint
and compare dh/dsigma/drho to the explicit Bianchi-I equations in theory.
This is four algebraic RHS evaluations, not an IVP. Preserve the historical
G1B/B3c numerical errors separately from these representation residuals.
Use synthetic nonzero transfer/unit tests to catch c or L mistakes and an
unbalanced-transfer refusal; no synthetic finite reservoir is admitted.
The interface can be IMPLEMENTATION_VERIFIED_SCOPED while calibrated REC
geometry remains INPUT_DEPENDENT on selected B3g/B3h physical inputs.

## Outputs and validation budget

Required code: small binding/geometry/transport/readiness module(s), one focused
test file, one saved-input consumer runner, one plot/report script, metered
driver. Results: all birth rows JSON/CSV, saved-endpoint bridge JSON, native
source binding/readiness JSON, summary and tests/execution ledger; plots of
birth number/energy and sector stress/residuals. Preserve actual zeros, do not
put numerical reconstruction errors into a physical uncertainty column.
One root review of source/contract precedes execution. One independent final
review includes actual saved plots. Correct only concrete findings.

New task-specific ceiling for this user-authorized postprocessing and tests:
120 wall / 60 CPU seconds total, implementation allocation 60 wall / 40 CPU,
each child 30 wall / 20 CPU. One test, one consumer run, one plot initially.
Any substantive failure returns to root; no automatic replay or tolerance edit.
Hashing/download/copy/packaging and provider waits are recorded as I/O, not
scientific runtime. Record Python/dependency versions and actual child CPU/wall.
No IVP, old campaign, native C/full suite, NCP, finite source transaction,
merge or production activation. No budget transfer from REC PB01 or old B3f.
Historical remaining wall/CPU remain null; budget_reset=false; preserve every
old debit and UNKNOWN_NO_ACK/rejection. A prior old write is not retried.

## Delivery and completion

Create a reviewable consumer PR, fresh expected-SHA non-force update and
checked source ZIP. Use the existing /BASS_BACKUPS and Drive parent
1fFxb-qgExWbEomt3EbbOjGKcslFpGv3y, create-only names. Provider completion is
only reported from actual responses. Source ZIP includes restored selected
input bytes and reproducing dependencies; large original history may be a
separately included immutable input in the archive, not a duplicate Git blob.
Update local authoritative frontier/DAG and a central-consumer delta without
overwriting concurrent owners. Scope and missing selected-channel fields are
the completion criteria; whole BASS physical percentage stays null, L4=false.
Strong no-go NG1–NG7: not applicable; this unit is constructive and conditional.

## Preexecution C9 adjudication — 2026-10-25

The independent static review identified four representation/admission defects
before any scientific execution. Root authorizes one targeted mechanical repair
and controls, with every prior acceptance threshold and budget unchanged:

1. The producer's `source_subflow_duration_tau` is the authoritative source
   integration duration in `proper_duration_s=L*dtau/c`. The difference of
   accumulated interval endpoints is a separate clock diagnostic; it is not a
   replacement for the fixed source step. Include the last actual saved birth.
2. A positive invertible map/determinant or positive bound must not silently
   become a zero certificate through floating-point underflow. An explicit
   typed range refusal is sufficient; log-domain evaluation is optional.
   Cover diagonal, determinant and Duhamel positive-term underflow separately.
3. Metadata completeness establishes only input-candidate readiness. This unit
   executes no finite absorption transaction and must always report
   `physical_finite_absorption=false`, including for fully populated metadata
   labelled as actual. Uncertainty certification remains a separate question.
4. Evaluate each diagonal trace-free stress by the algebraically equivalent
   pairwise-difference expression
   `pi_ii=((T_ii-T_jj)+(T_ii-T_kk))/3`, retaining off-diagonal entries. This
   avoids a false inherited STF rejection near isotropy without changing the
   physical tensor by projection or clipping. Add a near-isotropic control.

The original C9 findings remain in the review record. Recheck the changed code
before the already frozen test / saved-consumer / plot execution sequence.
