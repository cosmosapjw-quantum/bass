# REI background: 초기 Σ와 광자·중성미자·massive kinetic π_ab의 통합 Einstein 해

2026-10-15 KST. 사용자 요청은 초기 sigma/H 이외에 초기 pi_ab도 독립적으로 지정해 rei_bianchi의 실제 배경 계산에 공급하고, 다른 repo의 최신 BASS 결과를 활용하라는 것. 이번 선택된 작업은 기존 BASS PR160의 massive Einstein–Vlasov와 REI PR137의 감마/뉴트리노 Thomson 볼츠만 계층을 실제로 연결하는 constructive 물리+코딩 연구이다. 중복된 이전 초기 π 단독 연구를 재실행하거나 local Codex를 사용하지 않았다. 이 대화에서 사용자 Ubuntu에서 실제 프로그램을 실행했으며 native ChatGPT subagent는 호스트에 노출되지 않아 NOT_RUN.

## 1. Original frozen provenance and physical inputs

- BASS PR160 HEAD 9e50f936f3289cb0c7c8127772cf9fb8d172d7a8; uses original bianchi.matter.freestream FD96 positive collisionless distribution, original massive J^(i) and kinetic_einstein, and BASS anisostress Einstein radiation source.
- REI PR137 HEAD 5d41df647c4fd624d8a1b574f67fdd0b82ff5102; source exact copy of species_hierarchy.py SHA256 ced7906b35c26d8d0374ee8ce7f67ceb957b51a63d44e5a2661997b7e46983c5 and lrs_boltzmann.py SHA256 06ef834e4cd7adacf01f0ad6e3becc5aea9a493b5b99fd398be82610543984cc. This project pins and reuses both exact source files in source_refs/ without reinterpretation.
- AX03 frozen source BACKGROUND_FAMILY_LOCK SHA256 46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0; cosmology H0=67.4km/s/Mpc, Om=.315, Or=.000092, OL=.684908; mean a=1/21 to1/5; elapsed SI proper time; metric signature (-,+,+,+), nontilted axisymmetric Bianchi I.
- User-defined initial Sigma_ref=sqrt(sigma_ab sigma^ab/2)/H_ref=sqrt3 |s_ref|/H_ref and **independent sign** (orientation), not the old scalar signed q masquerading as public Sigma. q_legacy is only the original q=±0.005/±0.01 compatibility adapter.
- Independent positive initial angular sources W_gamma=1+k_gamma P2, W_masslessnu=1+k_nu P2, W_massive=1+A_m P2, with positivity -1<=A<=2 (REI γ,ν source currently deliberately narrowed to [-.5,.5]).
- Gamma radiation energy fraction f_gamma=0.5917144338784673 of rounded original Omega_r (source Tcmb0=2.7255K), neutrino remaining0.4082855661215327. Only photons scatter Thomson. Original q=0 AX08 saved composed history has 312238 rows and exact history SHA 4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f. Frozen one-way ne(a) C2 log-positive 8193-node interpolation maximum saved-data relative difference 1.975500059e-4. The donor is not republished and not updated by this new background.
- Massive kinetic fraction f_m is taken *out of* the original total Omega_m, must satisfy f_m≤(Omega_m−Omega_b)/Omega_m. Remaining Omega_m(1−f_m) is isotropic cold dust. Source uses original 96-node FD radial distribution and massive exact Killing-momentum solution with m/Tref=30 as a **controlled exploratory collisionless nonbaryonic reference**, not realistic calibration of DM.

## 2. Einstein + kinetic physics (consistent normalizations)

The mean axis scale factors are a_perp=a exp(−b), a_parallel=a exp(2b), shear sigma^i_j=diag(−s,−s,2s). With LRS anisotropic stress pi^i_j=diag(−Pi,−Pi,2Pi), Π=(P_parallel−P_perp)/3 and physical J/m³ units, the Einstein system is

  H² = H0²{ Omega_m(1−f_m)/a³ + OmegaLambda
            + [Omega_gamma Eg0+Omega_nu En0]/a⁴
            + Omega_m f_m M_m(x,b)/aref³ } + s².

  db/dx = s/H;
  ds/dx = −3s + 3 H0² [ Pi_r^normalized+Pi_m^normalized ]/H;
  dt/dx = 1/H, x=ln(a/aref).

The radiation kinetic shear source is
  Pi_r^normalized=(Omega_gamma Eg2+Omega_nu En2)/(3a⁴);
the massive BASS FD source is
  Pi_m^normalized=[Omega_m f_m/aref³] (p_m_parallel−p_m_perp)/3.
Thus 8πG Pi_total/c²=3H0² Pi_total^normalized. The actual gamma and massless-neutrino energy/number normalized Legendre matrices are those byte-pinned to REI PR137; gamma collision C_gamma_l=−GammaT d_l J_l with d0=0,d2=.9,d_l>=3=1, neutrino collision=0. These are **unpolarized** and elastic Thomson; no polarized E2 term, Compton energy transfer or photoinizing UV source.

Massive energy source continuity is NOT ignored: its original exact collisionless FD integral satisfies
   rho_m' = −3(rho_m+pbar_m) −6(s/H)Pi_m.
The gamma and nu monopoles separately satisfy E0'=−2(s/H)E2, N0'=0; neutron star unrelated. The composite Raychaudhuri consistency identity is
  2HH' = −H0²[3 Omega_dust/a³ +4 rho_r^norm+3(rho_m^norm+pbar_m^norm)]−6s²,
which exactly cancels anisotropic stress work between kinetic sectors and Einstein shear. Mathematica/Wolfram15.0.1 independently simplifies this cancellation to zero. Native xAct/xTensor1.3.0 Wolfram15.0.0: 8 exact zero 4D tensor checks including sigma*pi=6sPi, both traceless tensors and angular source/normal-frame conventions.

## 3. Actual source-compared physical results

Eight true independent source-locked backgrounds × 401 physical a nodes = 3208 historical samples, source CSV in evidence/JOINT_CAMPAIGN, per case endpoint and settings in RESULTS.json. Each case solves full coupled Sigma/b/H(t) with independent gamma/nu Boltzmann and exact BASS massive collisionless integrals. Representative Sigma_ref=0, kγ=kν=.2, f_m=.1, A_m=.5, m/Tref=30:

| Initial kinetic stress | Sigma(zbar=4) |
|---|---:|
| Radiation only, f_m=0 | 0.00010207032208826826 |
| Massive FD only, Aγ=Aν=0 | 0.000028796093446350806 |
| Radiation and massive, no electron collision | 0.00013090270361223693 |
| Same both plus **original q0 HHe ne donor Thomson** | 0.00013032405726396863 |

The positive and negative legacy |q|=.01 orientations produce Sigma endpoint0.0021112691676852414 and0.0018493192719963329 respectively when radiation+massive stress is initially positively biased. This signed difference is a physical sourced stress/shear orientation result, not a q^2 null that would hold without anisotropic stress.

Independent source reuse limits:
- For massive_fraction=0 and identical RK tolerance, all original REI gamma/nu states match to max3.5527136788e-15 in this model; independent RHS source difference O(5.4e-20).
- For kappa_gamma=kappa_nu=.2 and no Thomson, FULL original BASS massive+massless exact Killing background versus new gamma/nu/FD finite L8 at q=0,+.01,−.01, max abs endpoint Sigma discrepancy4.36e-13. This is source-parity convergence, not a rigorous all-grid error bound.
- C8-style L/GL/tolerance sampled refinement: representative L8,GL32, rtol3e-11 gives endpoint Sigma difference3.55e-13 vs L12,GL64, rtol2e-12 reference. Source/ODE numerical error remains a separate AX11 obligation.
- Initial gamma and neutrino N0 remain 1 to tighter than5e-12, their energy monopoles separately balance shear work, massive collisionless continuity from local finite differences normalized discrepancy about6e-10 and Raychaudhuri derived H'(x) finite difference1.4–1.6e-10. Finite-difference residual is not an interval proof.
- Full 3208-row REI original Rust AXBI BackgroundPoint/GeometrySnapshot cargo reference bridge PASS: Hamiltonian relative residual max3.33066907e-16, Sigma exactly matches sqrt3|s|/H, gamma and neutrino number, Pi species sum and physical positivity PASS; four **physically tampered negative controls** H, Pi_massive, Sigma and N_gamma0 all reject with exit3.

## 4. Actually measured local vectorization, memory, parallelism

12 same-source independent CMB+massive DOP853 backgrounds with distinct signed Σ, γ/ν P2 and massive A:
- Serial 12-case median wall .6644043s (three warmed repetitions).
- 2-process parallel .4707043s = **1.41x** vs serial, source endpoints numerically identical.
- 4-process parallel .2917243s = **2.28x** vs serial, source endpoints identical.
This is local Python CPU workload only, not full native REI HII/He chemistry speed.

Original BASS massive radial FD96 moments at 1024 input x,b:
- Scalar .073576s with tracemalloc peak0.323MB.
- Unchunked full NumPy array .098728s with traced peak101.600MB.
- Chunk128 .019297s with traced peak12.817MB.
- Chunk64 .019355s with traced peak6.472MB.
All source output matches within3e-12. Large-array vectorization is counterproductive for this radial×angular contraction; bounded chunks preserve good speed and reduce temporary pressure. Threads not silently treated as ChatGPT native subagents (which were not exposed).

## 5. Main scientific limitations and owner integration

This research provides a **real combined Einstein kinetic background solution and typed data provider** but NOT full cosmological reionization solution. Thomson sees the original q0 electron history in **one-way** form; new H, s and species radiation do not recompute native HHe xe,Tgas/emissivity. Neutrino distribution stays collisionless. The massive FD matter source is a controlled nonbaryonic collisionless reference with chosen fraction and mass/T, not measured cosmological cold DM stress. Full polarized E/B Thomson, original BASS massive hierarchy with independent high-l collision terms, ionizing radiation anisotropic stress, causal photon thermal/Compton ledger, non-LRS Bianchi geometry, AX11 error certification, observational inference and positive native history admission remain unresolved.

**Delivery:** BASS new source branch is stacked on BASS PR160 without mutating its original byte-pinned BASS FD or Einstein components. REI native intake is intended as additive typed BackgroundPoint + CSV evidence, not a silent replacement of original AX03 Rust or AX08 checkpoints. Per-row source SHA and negative controls permit an owner-controlled scenario-selection integration later. A new native REI chemistry/Einstein pilot must run with new source identity, not resume historical q-ref checkpoints. The existing later REI PR137 one-way gamma/nu donor result is preserved and matched.

Literature context: Lee, Nungesser and Tod, “On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology”, General Relativity and Gravitation (2020), DOI 10.1007/s10714-020-02699-7, emphasizes conserved Bianchi-I spatial Killing momenta and anisotropic kinetic stress; this does not establish novelty of our model or authorize full EoR inference. Original BASS exact FD96/moment code, REI actual PR137 split collision and the frozen AX03 parameters are the dominant source authorities.

**Selected current stage executed:** cross-repo constructive theory+actual C5/C6/C7/C8-local science checks around initial Sigma and pi. This is not a forced ten-stage research completion; hold external third-party peer review and full EoR AX11 admission.
