# Codex handoff — sandbox H–Li LRS sweep

## Current authoritative work

- Branch: research/rei-hheli-compact-pilot-20261022
- Lane: research/rei_hheli_compact_pilot_20261022
- BASS PR: https://github.com/cosmosapjw-quantum/bass/pull/180
- REI PR: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/220
- Base: completed ACCEL03 branch research/rei-sigma-pi-sweep-analysis-20261021
- Physical source base: ee7e9ae76c852079ce86cdd5165624ab2b7fc7a9c672016501ed5da5fb4341d3
- Immutable REC119 owner: a949529872eb5ba0e20c7e206fe893e5d544e48c
- Latest remote commit / full backup locator: delivery/FINAL_PUBLICATION.json and delivery/STAGEC_BACKUP_VERIFIED.json. Read actual ACKs; archive snapshots do not contain their own future upload ACK.

Read REPORT_KO.md, FROZEN_CONTRACT.md, THEORY_KO.md, DAG.json,
LOOP_RECORD.json, evidence/ROOT_ADMISSION_C.json,
evidence/independent_review/, delivery/ and this file before changing code.
Independent review and the current publication state are evidence-bound there;
do not infer a later ACK from the presence of this handoff.

## What has actually run

127 compact33 cases (125 grid +2 initial-cancellation) ×193 samples from z=20
to z=2, 24,511 history rows. All inherited gates pass.
Two unchanged full62 trajectories, s04_m04_r04 and cancel_positive_matter,
also pass. Paired implementation errors are below all frozen thresholds.
The complete successful raw is results/pilot_v2, plus results/full62_oracles.
Four PNG/PDF families and exact plot-source arrays are under figures/ and
results/analysis/. Every one of the adopted 21 heavy-state columns is retained.
The default dispatcher now points to pilot_v2 and has been checked to resume
127 COMPLETE cases with zero new integrations.

Original results/pilot contains 127 completed numerical arrays with failed JSON
metadata from a NumPy-bool serialization error. It is preserved locally and is
not an authoritative campaign. Checkpoints retain its failure logs/receipts,
not a duplicate of its 33 MB raw. The repair only converts NumPy scalar metadata
to native scalars; no dynamics/tolerance/gate alteration occurred.

Git carries all individual successful trajectory NPZ files, source, receipts
and figures at final C publication. The two large redundant aggregated files
all_histories.csv.gz and all_histories_plot_source.npz are in full checkpoint C
and can also be recreated with analyze_pilot.py. Consult
delivery/GIT_PAYLOAD_SCOPE.json for the exact division.

## Minimal commands in an existing authorized checkout

Do not reset or discard another session's files, change its branch in place,
kill another process, or make another clone merely for this handoff. Inspect
current status and use the existing checkout/export under the project's AGENTS
policy. Fetch is permitted, but integrate the published branch only in a
workspace where that does not disrupt other work.

Use Python 3.12 with requirements.txt. Set thread counts before Python starts:

~~~~bash
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
REI_LANE=research/rei_hheli_compact_pilot_20261022
python -m pip install -r "$REI_LANE/requirements.txt"
python "$REI_LANE/code/run_pilot.py" --plan
~~~~

To reuse complete output, these default commands are sufficient:

~~~~bash
python "$REI_LANE/code/run_pilot.py" --execute --workers auto --max-workers 4
python "$REI_LANE/code/verify_paired.py"
python "$REI_LANE/code/analyze_pilot.py"
~~~~

The first command should verify all 127 COMPLETE cases and skip their
integration. The latter two read existing arrays and reconstruct analysis.
They write their declared analysis/evidence paths, so preserve any separately
edited output before choosing alternate --output/--figures destinations.
Do not rerun the whole campaign merely to reconfirm this handoff.

On NCP, use actual observation rather than assuming the target is available:

~~~~bash
python "$REI_LANE/code/run_pilot.py" --plan --workers auto --max-workers 63
~~~~

A new, explicitly intended run uses a new path:

~~~~bash
python "$REI_LANE/code/run_pilot.py" --execute \
  --workers auto --max-workers 63 \
  --output "$REI_LANE/results/ncp_new_run"
~~~~

For paired full62 regeneration only when it is actually required:

~~~~bash
python "$REI_LANE/code/run_full62_oracles.py" --execute \
  --output "$REI_LANE/results/full62_new_run"
~~~~

The delivered model is Python and already runs entirely in this sandbox.
No C++ compile is needed for this pilot path. Existing native BASS/REI work is
not replaced, merged or declared numerically equivalent by this branch.

## Resource policy

Actual execution: quota8 CPUs /8 GiB, affinity9, four case workers with one
numerical thread each. Target: NCP64 CPUs /128 GiB, not a current live host
measurement. CPU admission samples cgroup usage and affinity idle; host load
average is diagnostic only. Reserve one CPU, honor actual memory and peer
reservations without double-counting observed work. Large observed hosts can
admit at most63 workers, but only real available resources determine the count.
Do not stop simply because other Codex sessions exist. Do not run detailed
performance benchmarks unless the user later requests them.

## Frozen physical meaning

Full Frobenius Sigma_F=|sqrt(6)s/H| and
Pi_total,F=|P_m,F+P_r,F|, P_A,F=sqrt(6)kappa_t p_A/H².
Half-contraction coordinates equal full/sqrt(2) and are saved separately.
pi_m is a nonbaryonic collisionless massive component; baryonic common-T gas
has pi_b=0. pi_r=pi_gamma+pi_nu. Atomic electrons feed photon Thomson scattering.

Adopted inventory: n; H1I–II; DI–II; TI–II; He3I–III; He4I–III;
Li6I–IV; Li7I–IV, plus reconstructed electrons. Initial n=T=0.
Electronic rates are equal within an element's isotopes. UV is prescribed,
local isotropic,5–200eV, and T(z)=100+11900Q K with a prescribed tanh Q.
Photoionization and RR/DR are active. This is test-fluid baryonic energy and
does not close the full thermal/radiative Q^a system. CI/CX, molecules,
secondary electrons, thermal fusion and isotope-specific corrections remain
outside this run. Nuclear photo rates vanish only for the specified finite UV
support below every included photodisintegration threshold.

33-variable reduction requires reflection-even geometry, zero n/T and common
isotope fractions/rates. Nonzero n/T, nuclear transmutation or isotope-specific
evolution requires full62 or a new justified reduction.

## Results to preserve and next scope

The two zero-shear initially cancelling cases end at signed S_F approximately
-5.08317e-5 and +5.08293e-5; q approximately0.7378. The zero-seed control
max|S_F| is3.189e-20. These are finite-model results, not full-model uncertainty
or continuum convergence claims.

Completed 30-node ACCEL04/PHYS04/PILOT04 progression and actual backup/publication
status are in DAG.json. After delivery, the next node is selection and freezing
of the user's next physical scope, not another reproduction of the same pilot.
Candidate priorities: thermal/UV energy coupling and Q^a contract, justified
CI/CX/secondary-electron additions, then separate numerical/model convergence.
Keep every new stage's backup/publication/progress/next-node entry.

Preserve the older warm729:729 cases,243 PASS groups,47,385 rows,
a=0.1999→0.2. It uses its own contract and norm convention.

