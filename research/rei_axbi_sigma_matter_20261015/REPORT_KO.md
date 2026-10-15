# REI AX03: 표준 Sigma + 초기 radiation/massive matter 비등방응력의 결합 Einstein–Vlasov 배경해

2026-10-15 KST. 새 이론·코딩 연구 루프. 실제 Ubuntu에서 ChatGPT가 직접 Python·Rust·Wolfram/xAct 실행, local Codex 없음. 이전 BASS source와 REI AX03 기존 science solver/checkpoint 불변. Native subagent=NOT_RUN_UNEXPOSED.

## 1. BASS kinetic hierarchy source와 matter anisotropic stress

원래 BASS 코드: bianchi/matter/freestream.py (SHA256 b03aeed2cfcdaa5baf45fdab626941905674e2385bc06d1173a4b8c39ebf8bb4), hierarchy.py (27f81acd681acc34537ad59ad2bec923d95c0adb7ac6d52413c4e3b2e0980aa6), kinetic_einstein.py (59f1c49539d35061d17490944ace63c48addce0e44e3d1a0f39f8f40b363d93b). Covariant momentum moments rho=J^(0), p=J^(1)/3, pi_ab=J^(0)_ab. Exact Bianchi-I spatial Killing momenta are preserved. The new massive code REUSES original BASS cached FD radial nodes Q,DQ and Fermi–Dirac f0 instead of inventing phenomenological viscosity. All four source-file SHA identities plus original REI family lock 46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0 are guarded.

Matter anisotropic stress really exists, but only for imperfect/collisionless matter with a non-isotropic velocity-dispersion tensor. In a normal-comoving cold perfect CDM/dust or isotropic tightly-coupled baryon fluid the equilibrium pi_ab=0. Warm/hot collisionless massive relics, e.g. massive neutrinos, can have pi_ab!=0 through the quadrupole J^(0)_ab. Tilt and baryon viscosity are different physical lanes. This run does not claim baryon stress or realistic CMB Thomson collisions.

## 2. Requested Sigma scalar, with signed orientation

Metric (-,+,+,+), normal-frame LRS Bianchi I: axes a_perp=a exp(-b), a_par=a exp(2b), s=dot b, sigma^i_j=diag(-s,-s,2s), sigma²=sigma_ab sigma^ab/2=3s².

Public user convention: Sigma=|sigma|/H=sqrt(3)|s|/H >=0. The initial orientation=sign(s_ref) is supplied separately to preserve the distinction between positive/negative shear. Historical Wainwright–Ellis magnitude Sigma_WE=|s|/H differs by sqrt3, while original AX03 signed s/H is NOT the requested Sigma scalar.

The initial Friedmann constraint gives H_ref=H_F,ref/sqrt(1-Sigma_ref²/3) and
s_ref=orientation * Sigma_ref * H_F,ref / sqrt(3-Sigma_ref²).
Previous q_ref=s_ref/H_F,ref only appears in a non-public source-parity adapter and is never the new independent input. Old signed |q|=.01 corresponds to Sigma_ref=.017319642115231484. Wolfram15.0.1 checked both Sigma and initial constraint identities to exact zero.

## 3. Two independent source-normalized positive Vlasov sectors

Original REI source: H0=67.4 km/s/Mpc, Omega_m=.315, Omega_r=.000092, Omega_Lambda=.684908, Omega_b=.0493092305, a_ref=1/21, a_end=1/5. All time values are elapsed SI proper seconds since mean zbar20. Divide the ORIGINAL Omega_r into perfect fraction (1-eta_r) and collisionless radiation eta_r; Omega_m into perfect dust (1-f_m) and a massive Vlasov fraction f_m restricted to the nonbaryonic Omega_m-Omega_b budget. Never add extra energy without removing it from the original source budget.

Initially positive angular distributions W_r(mu)=1+A_r P2(mu), W_m(mu)=1+A_m P2(mu), P2=(3mu²-1)/2, -1<=A<=2. Their quadrupoles and eta/f_m are independent initial inputs. The source massive FD radial momentum distribution is the BASS original q² f_FD(q) dq with mass_over_Tref=m/T_ref; it is model input, NOT observed particle mass.

For x=ln(a/a_ref), r=e^(-x), kinetic physical energy E=sqrt(m²+q² r²[e^(2b)(1-mu²)+e^(-4b)mu²]). With E_ref=sqrt(m²+q²), I0=integral q² f_FD E_ref dq and normalized <W>=1, define

M_m = r³ /I0 * integral dq dmu q² f_FD W_m E,
P_perp,m = r³ /I0 * integral dq dmu q² f_FD W_m [q²r² e^(2b)(1-mu²)/(2E)],
P_par,m = r³ /I0 * integral dq dmu q² f_FD W_m [q²r² e^(-4b)mu²/E].

Massless radiation M0r(b,A), delta_r(b,A) come from existing BASS Einstein–massless–Vlasov parent PR158 (commit 68137622de0ab64cee66d9efc13b0a5336a0bd30), source unmodified.

Let F_r=H0² Omega_r eta_r/a^4, F_m=H0² Omega_m f_m/a_ref³ and F_dust=H0² Omega_m(1-f_m)/a³, F_radperfect=H0² Omega_r(1-eta_r)/a^4. The coupled Einstein system solved with DOP853 is

H²=F_dust+F_radperfect+H0² Omega_Lambda+F_r M0r+F_m M_m+s²,
ds/dx=-3s + [F_r delta_r+F_m(P_par,m-P_perp,m)]/H,
db/dx=s/H, dt/dx=1/H.

Physical anisotropic stress diagonal tensors for each species: pi^i_j=diag(-Pi,-Pi,2Pi), Pi=(P_par-P_perp)/3, SI J/m³. Thus dot s+3Hs=(8pi G/c²)(Pi_r+Pi_m). At b_ref=0, Pi_r/epsilon_r,total=eta_r*A_r/15, Pi_m/epsilon_m,total=f_m*A_m*<v²>_energy/15 where v² weight comes from BASS FD radial. Public InitialStress.from_stress_ratios supports direct independent inputs Pi_r,ref/epsilon_r,total and Pi_m,ref/epsilon_m,total and enforces positivity/allowed f_m. No post-hoc pi(t) prescription.

Species energy equations: epsilon_r'=-4epsilon_r-6(s/H)Pi_r; epsilon_m'=-3(epsilon_m+p_m)-6(s/H)Pi_m. The pointwise massive identities are partial_x E=-(p_par+2p_perp), partial_b E=-2(p_par-p_perp), with appropriate normalized physical number factors. Wolfram15.0.1 independently evaluated their exact zero residuals. Local Wolfram Engine15.0.0 / xTensor1.3.0 gave 10 exact tensor zeros for radiation and massive pi separately, shear norm and combined shear:pi.

The independently differentiated Einstein constraint matches the mean Raychaudhuri relation:
dH/dx= -(3F_dust+4F_radperfect+4F_r M0r+3F_m[M_m+(2P_perp,m+P_par,m)/3]+6s²)/(2H).
This cancellation uses the BOTH species continuity laws, not a manufactured Einstein source.

## 4. Actual source-frozen numerical histories

Fourteen scenarios x501 mean-redshift nodes: 7014 physical table rows, typed with Sigma, initial orientation, pi_r, pi_m, H,s,b,axes, proper time, matter and radiation pressure/energy, baryon H/He nuclei and source lock. evidence/SIGMA_MATTER_TABLES/AX03_SIGMA_MASSIVE_HISTORIES.csv SHA256 143044ae747b167c498bb67884420a1543f347a4504c2fbd6da04365856a083e.

Illustrative initial positive quadrupoles at Sigma_ref=0: eta_r=.5, A_r=.2, f_m=.1, A_m=.5, mass/Tref=30 produce initial Pi_r=9.147649735780715e-11 J/m³, Pi_m=1.04723022668031e-10 J/m³. Final zbar4:
- radiation only: Sigma=5.10802390569e-5, b=4.20760890558e-5;
- massive matter only: Sigma=2.88707581337e-5, b=3.30464985838e-5;
- both: Sigma=7.99318343367e-5, b=7.51205125441e-5.

With user Sigma_ref=.017319642115231484, positive orientation, baseline stressfree final Sigma=.00199990187323. Positive radiation only .00204202313857; positive massive only .00202715373384; both positive .00206925195933; both negative .00191040640847. Cold massive m/T=1000 gives .00199992672783 approaching stressfree.

The separate REI PR135 uses an isotropized frozen cold-gas stress with very small Pi_m; REI PR133 uses a phenomenological viscous matter ansatz. Neither is silently equivalent to the PRESENT positive finite-mass Vlasov distribution with freely chosen initial momentum quadrupole. This is a complementary physically distinct branch, not a claim of one universal measured matter pi.

## 5. Actually executed verification

Original BASS hierarchy.J_moment() (PYTHON original oracle) computes J0, J1 and tensor J2 with full original FD 96-radial x576-direction quadrature. New LRS reduced 96-radial x32-inclination moment agrees within 5e-12 at three anisotropic A settings and several x,b. New 23/23 physics and artifact tests PASS, source SHA locked. Energy-momentum conservation both species and Hamiltonian plus finite-difference Raychaudhuri tested; all original stressfree AX03 signed cases recovered, parent radiation-only model recovered.

Actual original REI rei_microphysics crate was compiled in an isolated temp Cargo project, source SHA 65f10dced178aa85bb1c92da0b35350a0eec2d3d3de05630c900b5df4ec1e254 and geometry SHA 0c0bb17168b36a67af6e3e2a3ada835bc77db3dbc73d06e13075f6019ec11289. Real Rust typed BackgroundPoint/GeometrySnapshot bridge accepted all 7014 rows; five original stressfree samples max b difference2.019391598384601e-14, H relative3.33e-16. Three independent corrupted inputs H+5%, massive pi and Sigma were rejected with exit3. A preliminary Rust guard wrongly assumed |Pi_r|+|Pi_m|=|Pi_r+Pi_m| for mixed signs; corrected the guard to use signed linear sum without weakening any physical tolerance and reran the full actual native Rust positive/negative tests.

Convergence actual DOP853 x angular GL16/32/64/128, tightened time tolerances, 4 physical cases. Numerical deviations recorded in evidence/CONVERGENCE.json; no continuum quadrature or interval global certificate claimed. Original time/chemistry driver NOT altered.

## 6. Measured optimization and limitations

1024 physical massive moments at fixed FD96, GL32 (3 warmed medians):
scalar loop .06328 s, NumPy full vector .05475 s (tracemalloc101.6MB), 128-chunk vector .01628 s (tracemalloc12.82MB), 128-chunk +2 actual threads .01090 s (tracemalloc25.61MB), 4 threads .01787 s. All actual numerical arrays equal to expected floating output on tested sample. Vector chunk 3.89x faster than scalar; optional 2worker moment 5.81x. For FULL 14 independent DOP853 background solutions serial .4633 s, 2workers .6473s and 4workers .7474s; use serial full background and optional 2worker per large moment batch. This is not a native coupled REI chemistry speedup or whole process RSS result.

Actual source labels and plots: evidence/AXBI_SIGMA_STRESS_HISTORY.png, AXBI_ZERO_SHEAR_GENERATION.png, AXBI_PI_COMPONENTS.png. New true native REI matter-dependent H and local proper-time increment must be source/clock-aware and checkpoint-incompatible with old zero-pi driver; the old AX08 code cannot simply use pi-coupled H without accepting new physical data. Full collisional radiation, realistic neutrinos and baryonic gas, observational posterior and native H/He history scientific admission remain unissued.

Literature: Lewis & Challinor 2002 PhysRevD66 023531 https://arxiv.org/abs/astro-ph/0203507; Lee, Nungesser & Tod 2020 Gen.Rel.Grav.52,48 https://doi.org/10.1007/s10714-020-02699-7. These references ground method but not observational calibration/novelty of chosen source family.
