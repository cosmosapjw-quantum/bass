# ACCEL04 → PHYS04 → PILOT04: full sandbox H–Li preliminary sweep

Contract owner: root Astra. Frozen 2026-10-21 UTC / 2026-10-22 KST.
Requested executor: gpt-6.1-sol; observed runtime model identity is not exposed.

## Objective and adopted scientific model

Finish the authorized optimization, physics, and coding sequence with actual
z=20→2 trajectories and figures in the current 8 CPU / 8 GiB sandbox. Preserve
the completed warm729 and ACCEL01–03 evidence. New results have a separate
campaign identity and are not replacement warm729 results.

The primary executable donor is rec_bianchi commit
`a949529872eb5ba0e20c7e206fe893e5d544e48c`, directory
`research/rec_rei_hheli_sandbox_20261021`. Its 62-state finite model couples
LRS Einstein/Vlasov/massless multipoles, 21 isotope/ion abundances, and optical
depth. BASS_HE commit `e8bb035d31f59e34734947b9082bdbd60128b799` supplies the
independently documented reflection-even reduction. Selected original files
and source manifests remain unchanged under `vendor/rec_hheli/`.

Adopt exactly the donor's 100–12000 K prescribed temperature and local
isotropic 5–200 eV UV reservoir, photoionization plus case-A RR/DR coefficients,
single-electron photo yield, and isotope electronic equality. Evolving electrons
feed photon Thomson opacity; the resulting photon stress feeds shear. Gas
thermal/ionization and external UV energy remain a monitored test-fluid
contribution. The thermal history and UV field are specified inputs, not solved
thermal/radiative energy closure. The massive anisotropic matter component is
collisionless nonbaryonic matter; baryons have common isotropic pressure.

## Explicit species and reaction scope

State inventory (21): n; H1 I–II; D I–II; T I–II; He3 I–III;
He4 I–III; Li6 I–IV; Li7 I–IV. The free electron density is reconstructed from
charge. This covers the uploaded primordial diagram and adds Li6 and fully
ionized lithium. It is not a catalogue of every short-lived nuclear resonance.

The initial n and T abundances are zero. Correct spectator-electron beta maps
remain in the unreduced owner: n→HII+e, TI→He3II+e, TII→He3III+e.
For the prescribed finite UV support, nuclear photodisintegration channels
have zero rate because even the Li6→alpha+D threshold is 1.4743 MeV.
The diagram's 19 reactions will have an explicit stoichiometric/source/status
catalogue. Thermal fusion, charge exchange, collisional ionization, molecules,
secondary-electron ionization, and full energy closure are outside this
adopted preliminary model. No zero omission error is asserted for these.

## Conventions and parameter coverage

Use orthonormal tensors sigma=diag(-s,-s,2s) and pi_A=diag(-p_A,-p_A,2p_A).
Time H is in s^-1; energy density in J m^-3; kappa_t=8 pi G/c^2.
Full Frobenius signed coordinates are S_F=sqrt(6)s/H and
P_A,F=sqrt(6) kappa_t p_A/H^2. Half-contraction values are these divided by
sqrt(2), matching the earlier warm pilot convention. Both must be saved and
unambiguously labelled. Total stress is the signed sum before taking a norm.

Adopt the donor's 125 point physical grid:

- Sigma_F: 0, 0.003, 0.03, 0.15, 0.6.
- P_m,F: -0.0005, -0.00025, 0, 0.0005, 0.001.
- P_r,F: -0.0012, -0.0006, 0, 0.0006, 0.0012.

Add two zero-initial-shear cancellation cases with
(P_m,F,P_r,F)=(0.0005,-0.0005) and (-0.0005,0.0005).
Total: 127 cases, 193 saved epochs each, x=ln(a/a_ref) from 0 to ln(7),
a_ref=1/21, a_end=1/3. Initial stress amplitudes must satisfy the donor's
positive-distribution domain. Visibility comes from broad valid seeds and
appropriate signed/log plots, not from violating pressure realizability.

## New optimization: 62 → 33 coordinates

Preserve the four energy/number towers through L=8. Reflection symmetry removes
odd multipoles; the gas-energy placeholder is identically zero. Geometry has
23 coordinates. For the frozen equal-electronic-rate, equal-initial-fraction,
zero-n/T model, H1/D share two charge fractions, He3/He4 share three, and
Li6/Li7 share four. Chemistry has nine coordinates; optical depth adds one.

Let P lift these 33 coordinates to the owner 62-vector and R select the
representatives. R P=I, f_c(x,v)=R f_o(x,Pv), J_c=R J_o P. Each isotope's
physical abundance is its actual inventory times the corresponding charge
fraction. Its complete 21-state equation is retained through this invariant
subspace, and all 21 states are saved. The original 62-state solver is the
independent implementation comparison. Floating quadrature parity leakage is
assessed by numerical residuals, not byte identity.

The compact path must reject nonzero n/T, unequal isotope initial fractions,
changed electronic equality, or nonzero odd/placeholder initial states. It
must not silently apply this reduction to an expanded nuclear model.
Initial isotope fractions refer to the common physical input, with an
8*machine-epsilon absolute allowance for binary64 inventory division. The
observed H1/D difference 2.710505431213761e-20 is this rounding effect. Preserve
the original donor initial vector and record the lift residual; do not clip or
renormalize it. This follows the existing numeric-versus-byte identity policy.

## Numerical design and bounded acceptance

Preserve BDF, analytic Jacobian, rtol=2e-8, geometry atol=2e-11,
scaled-ion atol=2e-10, tau atol=2e-11, and max_step=0.025.
Preserve all donor trajectory gates without loosening their thresholds.

1. Finite-coordinate checks: R P exact identity; lifted RHS residual at three
   admissible states <=2e-12 after scaling each entry by max(1,|f_owner|);
   projected-Jacobian directional finite difference <=2e-6 under the
   documented scale; reconstructed charge/baryon algebra <=2e-14.
2. Guard checks: a nonzero tritium initial inventory and unequal isotope
   initial charge fractions reject the compact path.
3. Two targeted full-interval comparisons: the high-shear grid corner and the
   positive-matter cancellation case. Require signed observable absolute
   differences <=3e-7, isotope charge fractions <=3e-5, tau absolute <=3e-7.
   These are implementation equivalence checks at the retained discretization,
   not a continuum convergence certificate or performance benchmark.
4. Actual campaign: all requested cases/epochs present; all owner scientific
   gates pass; raw values retained without clipping/renormalization.
5. Figures: true z=20→2 time histories, signed matter/radiation/total stress,
   cancellation/control comparison, initial-axis endpoint slices, and every
   isotope/ion including explicitly zero n/T. Plot-source arrays are saved.

If a gate fails, preserve the original result and diagnose it. Root authorizes
any model, tolerance, or convention repair. One fresh independent review is
required before scientific admission. Detailed performance benchmarking is
not requested and will not be run.

## Resource, publication, and DAG contract

Numerical libraries use one thread per worker. Start at no more than four
sandbox workers, bounded by observed CPU quota, load, memory, and peer work.
CPU admission uses a short actual cgroup CPU-use and affinity-idle observation;
system load average is diagnostic only. A root 0.63 s observation found only
0.074 CPU used and 8.46 affinity-idle CPUs despite load average 5.57. This
corrects the inherited load-as-usage rule, which had incorrectly admitted zero
workers in an otherwise available sandbox. Keep one CPU reserve and account
for peer reservations without counting their already observed use twice.
The same dispatcher can admit more independent cases on an observed NCP
64 CPU / 128 GiB host; it must not assume those resources in this sandbox,
kill peer processes, or stop just because other sessions exist.

Publication branch: `research/rei-hheli-compact-pilot-20261022` in bass and
rei_bianchi, based on the respective verified ACCEL03 head. Draft PRs only.
Every DAG node records progress, its checkpoint publication/backup status,
and its next executable dependency. Checkpoint A preserves optimization;
checkpoint B preserves the adopted physics and execution-ready source;
checkpoint C preserves actual trajectories, figures, review, and handoffs.
Actual provider acknowledgements and Git identities determine saved status.

Code changes, actual verification, and execution are authorized. No NCP
execution is needed to finish this sandbox pilot.
