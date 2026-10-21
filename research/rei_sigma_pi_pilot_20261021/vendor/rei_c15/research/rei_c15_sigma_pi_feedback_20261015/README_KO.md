# REI C15: Einstein shear-stress feedback, Sigma and real BASS Boltzmann/Vlasov sources

2026-10-15 KST. Scientific scope: a=0.1999→0.2 conditional short interval, prescribed warm H/He initial xHII=.4, xHeII=.5, xHeIII=.3, T=12000 K. This is actual local Einstein-sourced numerical research, not the full physical zbar20→4 EoR history, polarized CMB or observational inference. Native AX08 checkpoints and existing dirty root checkout are untouched.

## 1. Exact physical variables and new dynamics

Metric signature (-,+,+,+), light speed c retained:
\[
ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2,\quad s=\dot b,\quad
\sigma^i{}_j=\operatorname{diag}(-s,-s,2s).
\]
\[
\Sigma=\sqrt{\sigma_{ab}\sigma^{ab}/2}/H=\sqrt3|s|/H\ge0,\qquad
\varepsilon_s=\operatorname{sgn}(s).
\]
The user-facing calculation takes Sigma_initial and independent orientation, NOT q_ref. An explicit legacy_reference_adapter maps historical stress-free q_ref to Sigma and orientation only for comparison. A tiny numerical shear with Sigma below 3e-13 is labeled orientation=0, NUMERICALLY_UNRESOLVED without mutating the underlying real s. This prevents a false physical - sign for an isotropic control.

Physical stress difference Pi_A=P_parallel-P_perpendicular has pi^i_j=diag(-Pi_A/3,-Pi_A/3,2Pi_A/3). The actually integrated Einstein dynamics is
\[
\dot s+3Hs=\kappa(\Pi_\gamma+\Pi_\nu+\Pi_{\rm massive}+\Pi_{\rm ion}),
\quad\kappa=8\pi G/(3c^2).
\]
\[
H^2=H_{\mathrm{FLRW}}^2+s^2+\kappa[(\varepsilon_\gamma-\varepsilon_{\gamma,\mathrm{iso}})
+(\varepsilon_\nu-\varepsilon_{\nu,\mathrm{iso}})
+(\varepsilon_{m,\mathrm{kin}}-\varepsilon_{m,\mathrm{replaced\,dust}})
+u_{\mathrm{gas,nonrest}}+u_{\mathrm{UV}}].
\]
The original PR137 Einstein source Pi/3 multiplied by three is algebraically the same physical pressure difference Pi; C15 never mistakes Pi/3 for Pi itself.

## 2. Actually invoked source code, physics separation

(a) Native rei_microphysics::axbi_sources::AxbiSource MD14 stellar 50k BB, originally pinned source ID MD14_Z002_FESC_BB50K_13P6_100_V1, photon energy threshold segments 13.6/24.59/54.42/100 eV; source proper rates checked on 17 z samples. BASS true clock and Killing photon energy/direction source; real C11 H/He Grackle Case-A RR/DR and photoheating, thermal energy and e density on same time step. The original C13 two-node positive source-cohort H/He reaction-conditioned compression is used with its fixed holdout budget.

(b) Original PR137 photon and massless neutrino Legendre/PSTF l≤8, separate intensity and number towers, with gamma-only unpolarized Thomson damping, original source Git blob e15e1875fba7fcc4a42e257e291c54d9b540a3f0. Gamma and nu stress are independently sourced; neutrinos never Thomson scatter. Initial source W_gamma,nu=1+A_gamma,nu P2 is positive for -1≤A≤2. Polarized E2 feedback and baryonic Thomson momentum recoil are NOT active.

(c) Original PR140 BASS finite-mass Fermi–Dirac radial × angular Vlasov with independent nonbaryonic massive fraction f_m and positive initial W_m=1+A_m P2. The exact vendor source Git blobs are 0eec2880c9d0d5675938ad516e00039b994ba18a and cc5094ba28f1da371d50cb9a854d7460c2dcec3f, derived from BASS PR160. Physical massive kinetic Pi_m = E_m,ref J2^(0); source J0^(0) and J0^(1) supply matter energy and mean pressure. f_m Omega_m is REMOVED from original cold-dust background before this independently kinetic dark component is introduced; chemically reacting baryon gas is NOT counted as the same collisionless massive distribution. Initial radial mass/T is chosen at a=.1999; it is not a fabricated primordial z20 value.

C15 uses a bounded two-pass predictor/corrector: integrate Einstein shear and PR137 gamma/nu Boltzmann with actual BASS massive moments; propagate source rays on this evolving metric and proper clock; inject authentic stellar UV; apply C11 H/He events and recombination radiation escape ledger; update n_e and ionizing Pi for a second geometry solve. This computes a real feedback loop but does NOT certify convergence of a fully implicit source/chemistry/Raychaudhuri solver.

## 3. Rigorous closed-subsystem checks and open total-Q obligation

When external emission, escape and reacting warm gas are removed, original BASS Vlasov moments satisfy
\[
d\varepsilon_{\gamma,\nu}/d\ln a
=-4\varepsilon_{\gamma,\nu}-2(s/H)\Pi_{\gamma,\nu},
\quad
d\varepsilon_m/d\ln a
=-3(\varepsilon_m+\bar p_m)-2(s/H)\Pi_m.
\]
Then the independent mean Raychaudhuri constraint is
\[
\dot H=-\kappa[3\varepsilon_{\rm dust}+4(\varepsilon_\gamma+\varepsilon_\nu)
+3(\varepsilon_m+\bar p_m)]/2-3s^2.
\]
The numerical finite-difference closed Einstein/Vlasov Raychaudhuri relative error was 1.47e-10; original massive energy-moment derivative residuals ~1e-10 at sampled points. A Wolfram algebra identity gives zero for cancellation of the shear-work stress terms. PR140 source physical positivity cone and independence of matter and radiation stress verified.

For the real MD14 source, external stellar energy injection is NOT compensated by an explicitly evolving star/dust emitter; Case-A escaping recombination photon is currently an energy-only reservoir without spectral angular transport; Thomson/Compton recoil and fully covariant matter/radiation Q^a=0 are not closed. Accordingly, neither Einstein H reconstructed from these conditional reservoirs nor photochemical source-energy ledger implies a complete globally covariant stress conservation law. These are meaningful physics limitations, not mere verification-policy gates.

## 4. Actual local C15 results and separate orientation

Same a=.1999→.2, nsteps64, initial Sigma=0:

| Active source Pi | Final Sigma | Final Pi_gamma+nu [Pa] | Final Pi_massive [Pa] |
| --- | ---: | ---: | ---: |
| Isotropic control | 2.46e-32 (orientation unresolved=0) | ~0 | 0 |
| Gamma+nu positive A=.2, no massive fraction | 4.96571312485e-8 | +1.76385004809e-12 | 0 |
| Only massive f_m=.1,A_m=+.5 | 1.19292296964e-7 | ~0 | +4.23631291224e-12 |
| Only massive f_m=.1,A_m=-.5 | 1.19292296966e-7 | ~0 | -4.23631291252e-12 |
| Combined gamma+nu+massive | 1.68949453867e-7 | +1.76385004683e-12 | +4.23631291157e-12 |
| Gravity Pi OFF (explicit unphysical control) | 0 | real quadrupoles remain | real quadrupoles remain |

If initial Sigma=.002, positive orientation yields Sigma_end=.0019986449652946623; negative orientation yields .0019983070668367943. Signs of s remain distinct; Sigma magnitude cannot replace orientation. Combined real source yields x_HII_end≈.408818188749, Tgas≈12193.42821 K, in this particular near-z4 conditional warm cell.

Actually emitted/transported stellar UV pressure Pi_ion was included in the Einstein shear RHS. It remains tiny relative to background stress: roughly -3e-31 Pa at Sigma_init=0 with gamma+mass seed and -4.24e-27 Pa at Sigma_init=.002 positive, versus gamma+nu and massive ~1e-12 Pa. Therefore this short source does NOT support a claim of detected UV-induced global shear backreaction.

H/He chemical+photonic number ledger on actual C15 trajectories is ~1e-16 per H, thermal+binding+escape+work relative energy ledger ~1e-14 eV/H and gamma/nu number monopoles ~0. Original stellar source ID, cgs/SI and photon group support unchanged.

## 5. Spectral, temporal, vectorized, parallel and memory evidence

Original native MD14 photon spectrum at 4,8,16,32 bins per threshold interval, 64 time steps: Tgas_end [12193.6906866,12193.4282118,12193.3603481,12193.3432357] K. Observed 2nd-order spectral approach; not yet polarization angular convergence. Empirical temporal grid 8,16,32,64,128: Sigma order 1.36→1.71→1.91, x_HII 1.48→1.76→1.92, temperature 1.80→1.95→1.99. These are self-convergence observations, not strict global error enclosures.

The original BASS Fermi–Dirac positive q²dq × Gaussian angular formula is unchanged. C15 evaluates only the 3 Einstein-needed quantities J0^(0),J0^(1),J2^(0) with precomputed positive 2-D weights, not full unused J4 and higher i. Verified against original PR140 output over 2048 independent (eta,b): max relative error below 5e-16, ~2.53× moment source microkernel speedup. The original source files stay immutable.

The C13 positive two-node cohort compression conditionally keeps 384 instead of 49,152 UV packets after 128 steps, a 128× photon array saving only, ~2.47× warm whole scoped C15 interval median speedup. Eight independent source/feedback scenarios parallelized over 3 Python workers show 2.54× wall time improvement, with bitwise-identical science output. No production AX08 whole-RAM/run speedup asserted.

## 6. Reproducibility and exact next physical work

At C15 branch repo root (Python3 NumPy SciPy matplotlib):
- export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
- python3 -m unittest discover -s research/rei_c15_sigma_pi_feedback_20261015 -p 'test_*.py' -v
- python3 research/rei_c15_sigma_pi_feedback_20261015/study.py

C15_STUDY_RESULTS.json contains 8 actual sampled 64-step Einstein trajectories, matched controls, all source identities, time/spectrum convergence, BASS radial optimized source and parallel/compressed timings. SIGMA_PI_HHE_COUPLED_HISTORY.csv/png provide 512 actual trajectory rows and a multi-panel result. BASS_HE warm P01 tau, rec_bianchi HyRec FULL z20 donor, WU088_HH PHYS46 rate-unadmitted Coulomb advances remain scientifically distinct source lanes; they are preserved in earlier immutable C12 manifests, not silently injected into native astro MD14 chemistry.

NEXT physics: eventwise closed Q^a_{matter}+Q^a_{radiation}=0 across stellar emissivity, Case-A spectral angular escaping photons and Thomson/Compton recoil, with genuine CMB polarized E/B hierarchy. Then integrate full native H/He and ionizing RT from original cold z20 (the 10000–24000 K Grackle C11 interpolant cannot be extrapolated to ~8 K) to z4, with AX11 source-matched global convergence and observational optical-depth/sky checks. Old stress-free checkpoints cannot be resumed as solutions to this new Einstein geometry.

## 7. Durable release status

The immutable Git source+evidence ZIP, independently restored Python tests, Git blob identities, and BOTH Dropbox + Google Drive full-byte SHA readback must be recorded in BACKUP_RECEIPT.json only AFTER they actually succeed. GitHub PR alone is not remote two-cloud preservation.

## Independently verified dual-cloud immutable release

The immutable source/science archive commit f6a1c10aa6d3f7252a9e68a77c2c4b62c41e77f0
has filename REI_C15_EINSTEIN_SIGMA_PI_20261015_f6a1c10a_v2.zip,
1,680,554 bytes, 327 entries, CRC PASS, SHA256
 a159546829ff963b354b2c8feaa5da8b5536363f870ce6a4d3a966746d9c06a4.
Both Dropbox and Google Drive byte-stream readbacks are IDENTICAL to that source.
A fully clean extracted directory passed Python C15/C14/C13/C12/C11/C10/C9: 66 tests,
and newly compiled native Rust axbi_sources/background/igm_rates/igm_thermal:
23 tests, **89 PASS total**. Two original PR140 blobs, original PR137 gamma/nu blob,
and 16 external supplier input blobs were reverified exactly, and original
Sigma/Pi H/He coupled source replayed. The first local ZIP v1 had omitted
two existing Rust include_str compile-time contracts and is archived as a
packaging-failure receipt, NOT the final restorable delivery; the corrected v2
contains the original same-byte Rust contracts and passed fresh compilation.
Cloud IDs, source SHA256, detailed restore limitations and original checkout
identity are in BACKUP_RECEIPT.json, committed AFTER the immutable science
payload archive, therefore intentionally not inside the same ZIP.
