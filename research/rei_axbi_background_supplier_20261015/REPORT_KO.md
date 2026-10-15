# REI AX03 background solution supplier: 이론, 실제 로컬 구현과 물리 교차검증

2026-10-15 KST. 별도 local Codex 없이 ChatGPT에서 직접 코드를 작성하고 사용자 Ubuntu에서 실행했다. 목적은 FA03-C10 종료가 아니라 실제 REI AX03 배경해 공급을 위한 constructive R5 및 C5 구현과 C6/C7 stage-local 물리 검산이다. 원래 rei_bianchi checkout, 과학 solver, Rust production 코드는 변경하지 않았다. Native subagent 도구가 없어 NOT_RUN (Rust 스레드 실행과 혼동 금지).

## 1. Exact frozen source and equations

Copied the actual original REI background family lock without modifications: source/REI_BACKGROUND_FAMILY_LOCK.json SHA256 46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0.

- Rust AX03 source SHA256: 65f10dced178aa85bb1c92da0b35350a0eec2d3d3de05630c900b5df4ec1e254.
- Rust Bianchi geometry SHA256: 0c0bb17168b36a67af6e3e2a3ada835bc77db3dbc73d06e13075f6019ec11289.
- Rust IGM density/FLRW source SHA256: ebe5d4ba0a61133512cecfe50791794a50aa22132bcc5189170e5668cbf1871f.

Frozen cosmology H0=67.4 km/s/Mpc, Omega_m=.315, Omega_r=.000092, Omega_Lambda=.684908, Omega_b=.0493092305, YHe=.2454, Tcmb0=2.7255 K. Mean scale a_ref=1/21 and a_end=1/5; the time coordinate is elapsed proper seconds from mean redshift zbar=20 to zbar=4, NOT absolute cosmic time. Signature (-,+,+,+), no tilt, aligned z-axis, no rotation.

Physical density-fixed background:
- H_F(a)^2=H0^2 (Omega_m/a^3+Omega_r/a^4+OmegaLambda).
- s(a)=q_ref H_F(a_ref)(a_ref/a)^3.
- H(a)=sqrt(H_F(a)^2+s(a)^2).
- dt/dln(a)=1/H, db/dln(a)=s/H.
- a_perp=a exp(-b), a_parallel=a exp(2b), H_perp=H-s, H_parallel=H+2s; sigma^2=(1/2)sigma_ab sigma^ab=3s^2.
- q_ref=0,+/-0.005,+/-0.01 with one separate SAME_H at q=.01, clearly labelled counterfactual.

Use a dimensionless ODE time tau=H_F(a_ref)*t and independent x=ln(a/a_ref). The source-locked DOP853 integration evolves tau and b once and evaluates an array of 501 x nodes per family. Physical hydrogen and helium nucleus densities share the real Rust FlatFlrwBackground convention and constants, n_H=n_H0 a^-3, n_He=n_He0 a^-3. Tbar_CMB_K=T0/a is an *isotropic reference* temperature. Direction-dependent CMB temperatures require a photon Killing map.

**Independent analytic closed form in matter-only, nonzero signed shear:** let A=H0^2 Omega_m, C=s_ref a_ref^3, u=a^3. Then
t(a) = [2/(3A)](sqrt(Au+C^2)-sqrt(A a_ref^3+C^2)),
b(a)-b_ref = (2/3)[asinh(C/sqrt(A a_ref^3))-asinh(C/sqrt(Au))].
Wolfram15.0.1 checked a H dt/da -1=0 and a H db/da -s=0 with exact 0 residual. This is a physical nonzero-shear analytic reference rather than just the q=0 FLRW limit.

The exact conserved spatial Killing momentum for any photon implies, with early point i, receiving face f and B=b_i-b_f,
R^2=e^(2B)(1-mu_f^2)+e^(-4B)mu_f^2,
E_i/E_f=(a_f/a_i)R, mu_i=mu_f e^(-2B)/R, and dOmega_i/dOmega_f=R^(-3).
Therefore (E_i/E_f)^3 (dOmega_i/dOmega_f)=(a_f/a_i)^3. The local directional redshift obeys d ln E/dt=-(H+s(3 mu^2-1)); tested by finite differencing and exact Killing map. Reference: Fleury, Pitrou & Uzan, PRD91 (2015) 043511, DOI https://doi.org/10.1103/PhysRevD.91.043511.

## 2. Actual physical numerical results

Five physical-density-fixed cases plus the separate SAME_H diagnostic all integrated to mean redshift 4. Physical endpoint table:

| q_ref | proper-time elapsed seconds | b_end | (s/H)_end |
|---:|---:|---:|---:|
| 0 | 4.279489144154456e16 | 0 | 0 |
| +.005 | 4.279482918207676e16 | +.002946499991410212 | +.000577322231060198 |
| -.005 | 4.279482918207676e16 | -.002946499991410212 | -.000577322231060198 |
| +.01 | 4.279464240896685e16 | +.005892916695356878 | +.001154643884854670 |
| -.01 | 4.279464240896685e16 | -.005892916695356878 | -.001154643884854670 |

Delivered files AX03_SUPPLIER_TABLES/AX03_BACKGROUND.csv: 3006 rows (6x501), metric rates, t proper seconds, H/n_H/n_He, mean Tbar. AX03_PHOTON_KILLING.csv: 7530 source-bound ray rows for mu_f=-1,-.6,0,.6,1 with exact directional energy, angle Jacobian and phase-volume identity. Original CSV SHA and column units in AX03_SUPPLIER_CONTRACT.json. Plot AX03_B_Z20_TO_Z4.png, AX03_H_SHEAR_VS_FLRW.png and AX03_PROPER_TIME_GYR.png.

## 3. Independent host execution and source parity

- 70dps mpmath.quad independent source integral 30 fixed cases x checkpoints: maximum time relative difference 8.347725503181228e-13, maximum b absolute difference 2.203098814490545e-16. This is scientific numeric comparison, not an interval enclosure.
- Actual original Rust rei_microphysics::AxbiBackground compiled via temporary external Cargo manifest with a path dependency; owner source and build target never modified inside REI. Same six cases, 4096 Simpson panels, 30 matched points. Max time relative 1.2477217022568674e-12, max b absolute 2.654126918244515e-16; mean H matched at observed nodes, metric component difference 8.326672684688674e-17.
- Actual original rei_microphysics::igm_background::FlatFlrwBackground independently compiled, 11 scale nodes: maximum relative H, n_H, n_He, Tbar, dt_dln_a difference 4.440892098500626e-16, under original IGM source SHA.
- Native stdlib-only rust_bridge/src/table_consumer.rs compiled and directly consumed the full CSV. 3006 rows passed source model volume, positivity, constraint H^2=HF^2+s^2, source q membership, instantaneous s/H and proper-time monotonicity; negative mutated H_mean +5% rejected with exit code3 HAMILTONIAN_SHEAR_CONSTRAINT, original CSV checksum unchanged.
- Local Wolfram Engine15.0.0 xAct/xTensor1.3.0, actual 7 exact-zero checks: trace-free sigma, sigma^2/2=3s^2, sigma_ab n^a n^b=s(3mu^2-1), screen rank/idempotence, null photon, observer energy sign.
- New background supplier 33/33 tests PASS. This is scoped background/data-provider validation, not an actual HII/HeII/HeIII + thermal chemistry run.

## 4. Benchmarks with honest scope

At identical 6 cases x501 a nodes, original Rust 4096-panel Simpson point_at_scale 3 warmed runs median 0.35304799 seconds. Python DOP853 preintegrated dense-output and vectorized 501-node batches 5 repeat median 0.00327972 seconds. QUERY-ONLY speed ratio 107.65x. Python six-family one-time initialization 0.0474616 seconds excluded from that ratio. Algorithms are different and numerical equivalence tested at 30 physical points; they are NOT bitwise equivalent at every one of 501. The existing REI Rust background_table_001 cached optimization is a separate earlier optimization: we DO NOT claim 108x versus the already cached Rust table or whole native REI scientific run. No speculative GPU or 2/4-thread boost; small vector batches are fast single-thread and the Rust CSV consumer is streaming O(1) per-row scratch.

## 5. Missing stress diagnostic: conditional initially-isotropic free streaming

As a first quantitative test of the original AX03 feedback ceiling, approximate the entire effective Omega_r stress as free streaming from an isotropic radiation reference at zbar20. Use the actual derived Killing angular map, NumPy 128-point Gauss inclination, and the original Rust feedback diagnostic kernel delta_s(a)=a^-3 integral a^3 (8piG/3c^2) DeltaP dt, with actual elapsed proper seconds. The original source integrates initial mu, not the evolved angular measure. Only a conditionally prescribed radiation stress, not a self-consistent CMB Boltzmann + ionizing radiation feedback.

q_ref=+.005, -.005, +.01, -.01 yield max |delta_s|/H=5.08052405e-6,5.09706221e-6,1.01443257e-5,1.02104782e-5, respectively. At the endpoint |delta_s/s|=0.00866952,0.00869934,0.00865447,0.00871411. The tentative ceiling 1e-4 on |delta_s|/H and extra energy fraction passes for this *conditional proxy*, but a ~0.87 percent shear correction is not zero. Actual ionizing gas/radiation quadrupole, prior CMB anisotropy and coupled backreaction cannot be inferred from the assumed initial isotropy or treated as universally bounded by this proxy. Hence scientific admission for actual REI ion history remains NOT_ISSUED.

## 6. Actual consumer contract and next action

Use AX03_SUPPLIER_TABLES/AX03_BACKGROUND.csv and AX03_PHOTON_KILLING.csv with exact SHA checks from AX03_SUPPLIER_CONTRACT.json and the frozen family lock. All scalar time columns in SI proper elapsed seconds; zbar is a mean-scale chart and not necessarily a directly observed photon redshift. Follow the source Rust name + original hash and source gamma metric conventions. The native consumer gives the exact failsafe physical checks; do not replace the original production Rust AX03 solver silently or infer fast short-step interpolation from a 501-node plot. Any owner adoption requires a scoped background-table error bound for interpolation of t, b, short increments and exact physical clock. Missing source stress feedback and actual H/He abundance remain a separate native science task.

Run commands and machine-readable source/input hashes are in README_KO.md and the JSON evidence. Direct production REI branch untouched, no PR auto-merged. Neighbor research REC Bianchi I Killing phase-volume PR89 and HyRec primordial chemistry PR91 are source-distinct in redshift and matter physics; methodology only was reused.
