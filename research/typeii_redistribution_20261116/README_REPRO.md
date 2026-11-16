# Reproduce the source TypeII redistribution experiment

Draft PR340, immutable parent PR339/0577ef0a40cf10130a5933eb52c7230d4de1f11b. Only this research subtree changes. Source BASS gamma-law1.3, parent tracer populations, thermal history and tagged excitation fates are inherited unchanged. Requirements: Python with NumPy, SciPy and SymPy; Git for parent identity checks. No native production dispatcher has been changed.

From the exact repository checkout:

```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
d=research/typeii_redistribution_20261116
python3 "$d/test_transport.py"
python3 "$d/verify_phase_and_kernels.py"
python3 "$d/verify_coupled_split.py"
python3 "$d/run_campaign.py"
python3 "$d/run_targeted_refinement.py"
python3 "$d/analyze_campaign.py"
python3 "$d/verify_final.py"
```

There are23 primary actual-source cases (17 initial+6 targeted refinements), plus a separately retained pilot. `verify_final.py` runs16 contracts in normal and optimized Python,16 invalid-input tests, two representative actual tagged histories under optimized Python, and optimized phase/coupled/analysis programs. Nine selected science outputs replay byte-exact on this environment. It does not pretend to rerun all23 cases in that final selected replay; the complete campaign commands above do so without hidden caching. All23 output-triplet identities are also stored in TRANSIENT_RESULTS.json.

`PHASE_AND_KERNEL_VERIFICATION.json`: source401 parity, exact phase invariant, 32..4608-direction full-interval sky convergence, independent neighboring-ray Jacobian, normal radiation stress-energy check, Bose pair equilibrium/entropy, frequency and angular semigroup controls.
`COUPLED_SPLIT_VERIFICATION.json`: complete192-variable constant-medium collision generator plus3 loss counters versus independent dense exponential; manufactured control, not cosmological data.
`TRANSIENT_RESULTS.json`: all23 outcomes, temporal/spectral/angular/band differences, paired evolving-versus-frozen-material effect, source output hashes.
`outputs/`: actual time histories and final tagged angular-frequency distributions. Frequency band exits are never labeled global Lyman escape.

The exact homogeneous Bianchi Liouville measure is combined with a DECLARED factorized angular-averaged frequency FP plus elastic dipole-angle collision approximation. The nonlinear induced pair is tested but source packet trajectories are dilute linear tagged solutions. No full joint angle-frequency redistribution, nonlinear photon/atom population feedback or cosmic xe/tau is claimed.

The global sky quadrature test originally failed at512 directions; refining to4608 solves the observed resolution defect without changing tolerance. The zero-time frequency-step readout lacked an energy field; a failed test was preserved and a zero-valued field added without changing positive-time physics. These are recorded in INITIAL_SKY_QUADRATURE_FAILURE.log and ZERO_TIME_READOUT_RED.log.

Every phase is pushed and host-archived by publish.sh. External disk copies are not attempted because the parent unit encountered unresolved ENOSPC twice. No user storage deletion/configuration change is performed. Host receipts are outside the repository under /home/cosmosapjw/research_backups/bass_typeii_redistribution_20261116. Read the live branch HEAD before continuing and keep the PR Draft.
