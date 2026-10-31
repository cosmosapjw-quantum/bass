# BASS KM-2I | 동적 3준위 수소 재결합과 방향별 Lyα Sobolev 탈출: 한정 물리 결과

**2026-10-31 / one bounded model.** 부모 BASS Draft PR285 HEAD `75f9dca9907cbc62af837547c2ba8591ad72bdee`는 변경하지 않았다. KM2A–H의 편광 P8, Einstein–Bianchi I 계산과 원본 광자 seed는 Git source blob으로 잠겼다. 상위 DAG **9/15**, 21 edges, KM2 **PARTIAL**, 새 상위 완료 **0**. 이번 KM2I 하위 실험만 1/1 scoped implementation-verified로 닫는다.

## 1. 원본·이론

선행 PR285는 실제 DOP853 원본 Einstein·편광광자·냉바리온 IVP에 원래 HYREC-2 FLRW `x_e(z_vol)`를 Thomson 불투명도 외부 입력으로 결합했다. 본 연구는 그 결과를 기하 배경으로만 재사용하고, 주어진 proper `H(u), sigma_ij(u), n_H(u)`에서 **별도의 수소 3준위 화학 ODE를 실제로 적분**한다. 동일한 HYREC `T_m(z_vol)`과 표준 `T_gamma=2.7255 K ×(1+z_vol)`는 아직 외부 열/복사 입력이다. CLASS user source ZIP `class_public-master.zip` SHA256 `d1b2e1ce2b49de472e2cca9a327dc51c351e75bc0a2ad37d2e6538df76b289b7`의 원본 `external/RecfastCLASS/wrap_recfast.c/.h`를 byte-identical 복사하고, 원본 파일의 αB_PPΒ, βB(T_rad), Λ2s 식/상수에 대한 SHA·원전 line 검사를 통과시켰다. Empirical recfast fudge/Gaussian을 적용하지 않았다. 복사된 source C/h는 수정하지 않았다.

- Source-verified α_B(T_m): `4.309e-19 (T_m/1e4 K)^(-0.6166) / [1+0.6703(T_m/1e4 K)^0.5300] m^3/s`.
- β_B(T_gamma) detailed balance from α_B(T_gamma), excited n=2 threshold 3.4 eV; Lyα emission energy 10.2 eV, Λ2s=8.2245809/s.
- In normal-frame **local isotropic** ray grid, directional Hubble `H_parallel(n)=H+σij n_i n_j` and Sobolev optical depth `τ_S(n)=3 λ_α³ A_21 n_1s/[8π H_parallel(n)]`, with `n_1s=(1-x_e)n_H`. `λ_α=121.567nm`, `A_21=6.265e8/s`. `P_esc(n)=(1-exp(-τ))/τ`, effective `Λα=3A21 <P_esc>`.
- Dynamical reaction source `d x_e/du = T_* C [β_B(1-x_e)exp(-10.2eV/k_B T_gamma) - α_B n_H x_e²]`, `C=(Λα+Λ2s)/(Λα+Λ2s+βB)`, `u=t/T_*`, `T_*=218601.80677272403 Julian years`. Initial `x_e(1200)=0.32208146832` from original HYREC. No chemistry→P8/Einstein feedback, no selfconsistent spectral line photon field. The normal-frame Sobolev approximation neglects baryon tilt corrections to the line transfer.

In the thick limit, ε(n)∝H_parallel(n), and for traceless σ and **isotropic line emission** `<ε>=ε(H)` while the angle-resolved escape quadrupole is exactly `Q_ij=(2/15)σ_ij/H` in the continuum angular integral. This is **not** a no-go for general anisotropic recombination: nonisotropic n=2 source/occupation, finite τ, frequency transfer, and tilted source geometry are absent.

## 2. 실제 새 물리 데이터

Original Einstein–P8 parent is **actually reintegrated** for n_theta=12 and 16 (n_phi=2*n_theta, original source), proper `u∈[0,0.25]`. On each genuine dense-output geometry, separately integrate (i) directional Lyα Peebles chemistry and (ii) same initial-value H-only escape control with full physical αB, βB, C. Each mode carries 41 actual chemical ODE samples; **4 actual reaction IVPs**, **164 chemical epochs**, **2 original full Einstein P8 IVPs**, **2×(2nθ²) initial/final directional Lyα escape maps**, and 6 original-sourced scientific PNG plots plus the physical CSV.

| Measured GL16 at u=0.25 | New Peebles chemical IVP | Original externally imported HYREC P8 parent |
|---|---:|---:|
| x_e=n_e/n_H | **0.0444789732617** | **0.1344771035276** |
| Counterfactual Thomson angular mean depth, same original geometry | **7.33171173503** | **12.8301948241** |
| Difference in depth | **-5.49848308909** | reference |

With the **new ionization solution not fed back into P8**, the depth 7.3317 is a scalar-opacity *counterfactual*, not an actual P8 photon attenuation solution. The chemical x_e differs strongly from imported HYREC because of synthetic BASS `n_H(0)=1.8890×10^9 m^-3` (~**5.73964× CLASS**) and reduced 3-level physics; this is **not a comparison between independent atomic solvers under the same cosmology**.

Direction-dependent Lyα escape is physically nonzero: at u=0 n_theta16 ||Q||_F **0.08102054467**. Measured min/max Lyα Sobolev depth **~2.115×10^9 / 5.426×10^9**. The original angular-grid 2nd moments are near isotropic; numerical max component difference from `2σ/(15H)` through 41 epochs is **1.123e-12** for GL16 and **5.267e-9** for GL12; full-angle quadratic correction from σ averages to zero in optically thick Sobolev. Thus `x_e(angular)-x_e(H only)` max **6.38e-16** GL16 and **2.33e-13** GL12, despite large directional escape anisotropy. No continuum angular interval enclosure is claimed; only two-grid numerical agreement.

Chemical binding-energy bookkeeping: the per-H ionization binding reservoir released is **3.77539393279 eV/H** over this horizon. The corresponding **missing** recombination photon energy is about **9.10×10^-9** of the parent P8 photon energy at final time (synthetic normalization). This is *not inserted* into existing radiative energy, matter thermal or Einstein equations: augmented total Einstein energy conservation is **not claimed**. The source rate `q_chem=-13.6eV n_H x_e'/Tstar` J m^-3 s^-1 is tabulated for future coupled work.

## 3. 실행 검산 및 적대적 R6/C9 self-check

- Exact source guards on original parent KM2 and copied CLASS Recfast coefficients; deliberately mutated expected SHA must fail closed.
- `11/11 pytest PASS` on fresh actual real Einstein/P8 and chemistry IVPs; fixed-source and candidate-outcome tests separate.
- `hostile_saved_rate_audit.py`: **NO import BASS RHS**; directly recomputes 164 saved chemical samples, αB, βB, C, reaction derivative, binding energy, charge and quadrupole from different formulas. Max component quadrupole-vs-shear **5.267e−9**, max relative thick-limit scalar escape **4.642e−11**; exact saved rate residual 0 (same algebra/inputs, not independent physics model). 41-sample Simpson derivative-integral mismatch **1.694e−5**, an explicitly finite output cadence error and not the internal IVP tolerance. No distinct-author reviewer was executed.
- Physical limits: x_e∈(0,1), charged proton/electron densities equal, positive directional expansion and escape, optical-thin `Pesc→1`, isoshear quadrupole→0, 12/16 angular comparison PASS.
- GitHub final CI and external S2 backup receipts **must be appended after actual run**, never presumed successful at this drafting stage.

## 4. Interpretation and next safe action

**Completed scoped** `KM2I_DIRECTIONAL_LYA_ESCAPE_LIVE_3LEVEL_CHEMISTRY`, but **not** full anisotropic recombination. Two separate physical blockers are explicit: (A) incident ionizing/line photon spectrum is unavailable in bolometric P8 so Lyα source excitation cannot yet be derived from it, and (B) chemical reactions, baryon thermal/binding energy and photon radiation must be coupled back into the Einstein stress with charge/baryon number and four-force to claim a full self-consistent solution. Realistic CLASS density and `H` normalization also remains outstanding. These are the next constructive tasks, not an excuse to falsely close upper KM2. Native subagents not available; `native_subagent=NOT_RUN`, independent-author R6/C9 NOT_RUN.

**Source bibliography:** Seager, Sasselov & Scott (1999), *ApJ* 523 L1–L5, DOI **10.1086/312250** (earlier S0 draft had a wrong DOI and is corrected in this S2 publication); Seager et al. (2000), *ApJS* 128, 407–430, DOI 10.1086/313388; Lee & Ali-Haïmoud (2020), *PRD* 102, 083517, DOI 10.1103/PhysRevD.102.083517. Primary code is byte-locked CLASS `external/RecfastCLASS/wrap_recfast.c/h`, included directly in the research folder. No new private documents are required to reproduce the scoped computation.

**DAG:** Upper **9/15** (21 edges), `KM2=PARTIAL`, `new_upper_completed=0`. Scoped KM2I physical subunit **1/1**, `PRODUCTION_READY=false`, `MERGE_READY=false`, `AUTO_NEXT=false`, STOP_AFTER_ONE_BOUNDED_UNIT.
