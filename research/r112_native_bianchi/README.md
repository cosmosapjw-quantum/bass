# R112 native Bianchi development, 2026-11-24

Bounded extension of R109-R111, not an independent cosmological inference result.
Inputs: htt_base 5cd174dd3d458f82deb3aa614661cdda20ab61e6;
BASS a4e06827632a43a511c746a15b7e68e0d746b3d3;
REC 5cd21dab4ed349330270d236b4c732e37da43dc3;
REI 2838dd2102c94e5b0d199464fd64809c3a78d0fc.
Dossier sources in htt_base: docs/solver_free_research_20261014/sources/dossier/volume_I.tex,
volume_II.tex. R111_LOCAL_HIGHL_NATIVE_20261124 is the prior evidence.
New dependency commits: REC 3752213099ccb35998c22f1aaf0d42fb674184e4;
REI 503508f1c82a968bebc57900d43a65135c3db185.

## Theory scope
R1 source/owner audit; R2 Jacobi and Codazzi conventions; R3 exact ray and PSTF
representation; R4 normal, material, observer frames; R5 unequal massive
species; R6 tilted Sobolev rate; R7 two-temperature pointwise TLA; R8 matched
hydrogen derivative; R9 history-owner interface; R10 limits and claims.

Use the existing generic N,A,Sigma,R characteristic, not family-specific
branches. N A=0; no special 1/(1+9h) factors. H>0 is needed by the e-fold
clock. In normal-frame rest-mass units M_b=f_b M, M_c=(1-f_b)M and
p_c=-f_b p_b/(1-f_b) for zero net flux, gamma_s=sqrt(1+p_s^2),
M=E/(f_b gamma_b+(1-f_b)gamma_c). Coflow has prescribed Codazzi q/E.
The density fraction is NOT a proper-density fraction at finite tilt.
Thomson kicks only stream zero; this is still two pressureless streams.

Photon propagation direction e, beta=v/c, D=gamma(1-beta.e).
E_u=D E_n, dOmega_u=D^-2 dOmega_n, I_u=D^4 I_n.
The normal e-fold derivative of log D is
gamma^2 beta.beta'-(beta'.e+beta.e')/(1-beta.e).
f_u=-(log E_n + log D)'/D, i.e. the material-path frequency drift in H units.
Atomic proper-time derivative conversion is 1/(gamma H), not D/H.
Negative f_u is allowed as a geometric value, but rejected by the current
Sobolev closure. Independent ray finite difference and zero-tilt test pass.
REC two-temperature TLA accepts explicit T_m. Matched derivative is
xp_ref' + R_ani/(gamma H) - R_ref/H_ref; reference and current hydrogen state
and clocks must be matched. These are pointwise APIs, not a self-consistent
stiff x_p,x_2,T_m,He solve. Bolometric angular transport alone cannot
reconstruct frequency redistribution after scattering.

REI explicit supplied low-z tail must share the exact boundary with REI
and cover z=0, with 0<=xe<=1+2f_He. The caller owns astrophysical inputs.
No physical source is inferred from the synthetic test. The REC-REI
high-z join jump remains reported. The older donor-matched placeholder is
retained by default. A deterministic C_lm^{XY}=a_lm^X conj(a_lm^Y) and
C_l=sum_m C_lm/(2l+1) are not an ensemble covariance of inhomogeneous
perturbations.

## Coding and evidence
C1 tests before new APIs (compile failures); C2 per-stream mass; C3 native
solve/CLI; C4 material rates/solid angle; C5 REC native two-temperature and
matched RHS; C6 REI exact-tail interface and CLI; C7 direct REC call and git
pin update; C8 tests and legacy regression; C9 all-family smoke and VIstar
time refinement; C10 publish scoped receipts.

Run from the repo root:
  cargo test --release --locked --manifest-path _rustcore/Cargo.toml
  cargo build --release --locked --manifest-path _rustcore/Cargo.toml --example homogeneous_sky --example sky_covariance
  python3 research/r112_native_bianchi/run_smoke.py _rustcore/target/release/examples/homogeneous_sky NEW_OUTPUT_DIR

REC cargo test --release --locked: 127 passed.
REI cargo test --release --locked --lib --tests: 271 passed.
REI unrestricted cargo test blocked by pre-existing missing
configs/rei_fastest_v1/science_scenario_v1.json in paired_history example.
Explicit bass_ionization example built and synthetic new table consumed by BASS.
BASS: 197 passed. results.json captures finite all-m, product and reality
identities, residuals, time-refinement data, baseline output hashes, and fixture
receipt. All 12 Bianchi families tested plus FLRW control and custom Lie
nonzero-Codazzi case. The initial FLRW smoke with default nonzero shear
was rejected as intended; corrected zero-shear/zero-tilt control passes.
Five output files for one legacy case were byte identical after repin.
No high-l, long-history, spectral or angular-resolution certification of new
physics. No native subagent review available; single-agent scoped verification.

References: Challinor, PRD 62 (2000), arXiv:astro-ph/9911481;
Pontzen & Challinor, MNRAS 380 (2007) 1387;
Dai & Chluba, arXiv:1403.6117. Dossier I/II conventions control code.
Next: accepted-stage coupled proper density, beta' and spectral/matter
thermal state; matched stiff hydrogen and helium history; physical late
emissivity/SED/absorber transport; then long eta, angular and spectral
convergence and independent benchmark. No R78 DAG promotion.
