# BASS CE1AS | 실제 에너지-monopole 일치 FLRW Einstein–Vlasov 기준해와 Bianchi 고정-z 광학 비교

**과학 범위:** 하나의 새로운, 물리적으로 자기일관적인 FLRW IVP. 원본 CE1AP/CE1AQ/CE1AR의 massless collisionless reflection-even six-cell diagonal Bianchi I 9개 IVP와 5,562개 고정 적색이동 광학 관측량은 **재사용**했으며 재구성하지 않는다. 2026-11-01 KST. 원본 BASS PR306 HEAD `edfed2152c8fc28a6c96fc59341c4d10538c2937`, 원본 six-cell SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. 회계: BASS upper **9/15 scoped/source-mapped**, CE1 PARTIAL, OB1 PARTIAL, **new fully closed upper nodes=0**.

## 1. 정의·모형·source correspondence

컨벤션: signature `(-,+,+,+)`, 원본 무차원 Einstein 정규화 `8πG=1`, `Λ=0`, `u=t/T_*`; 물리 거리는 `D_A/(c T_*)`로 표기한다. 원본 관측시각 `u_o=0.08`. 원본의 3축 초기 방향팽창률은 저장된 exact photon energy log-drift `d(ln E_γ)/du|_{0,n=e_i}=-h_i(0)`에서 읽었다. GL24에서

`(h_x,h_y,h_z)=(0.7570457790882175, 0.4270457790882174, 0.4870457790882174)`.

Bianchi I Hamiltonian constraint로 얻은 최초 법선 에너지 모멘트:

`rho_0=h_x*h_y+h_x*h_z+h_y*h_z=0.9` (전 GL8/GL16/GL24 및 eps=0,±.035의 초기 원본 source에서 최대 편차 4.66e-15).

`Hbar_Bianchi(0)=sum(h_i)/3=0.5570457790882174`, `3 Hbar_Bianchi^2-rho_0=0.03089999999999815=0.5 sum_i(h_i-Hbar_Bianchi)^2`.

**새 FLRW 물질은 원본 비등방 여섯-cell과 동일한 f(p_i)가 아니다.** 원본 초기 분포를 momentum magnitude q에서 angular-average하여 `f_F(q)=1/(4π)∫ f_B(q,n) dΩ_n`인 양의 등방 massless collisionless distribution을 정한다. 원본 *초기 에너지 monopole*은 동일하게 0.9이지만 P_i, 원본 higher angular multipoles, 원본 비등방 shear, 평균 Hubble은 **같지 않다**. `p_F=rho_F/3`, `π_ab=0`, isotropic electron/photon collision 없음. 기존 CE1AR의 같은-부피 등방 proxy는 물리적 FLRW 해가 아니었다. 따라서 이것은 물리적으로 정당화된 **initial-energy-matched alternative FLRW model comparator**이지 원본 여섯-cell source를 유지한 채 shear만 0으로 돌린 모델이 아니다.

## 2. 정의 → 유도 → 계산 형식

독립 FLRW Einstein+Vlasov radiation IVP:

`a' = a H`, `rho'=-4 H rho`, `3 H²=rho`, `a(0)=1`, `rho(0)=rho_0=0.9`, positive expanding root. 따라서

`H_F0=sqrt(rho_0/3)=0.5477225575051659`,

`a_F(u)=sqrt(1+2 H_F0 u)`, `rho_F(u)=rho_0/a_F(u)^4`,

`H_F(u_o)=H_F0/(1+2H_F0*u_o)=0.5035901297012716`.

관측자-normalized FLRW 광학은 고정 observed redshift `1+z=a_F(u_o)/a_F(u_e)`에서 `u_e`를 찾아 `D_A/(cT_*)=a_F(u_e)∫_{u_e}^{u_o}du/a_F(u)`이고, 복사 지배 평탄 FLRW에서

`D_A,F/(cT_*) = z / [ H_F(u_o) (1+z)^2 ]`.

Wolfram이 이 정확 적분식의 차이를 0으로 확인했다. 실제 구현은 `scipy.integrate.solve_ivp(DOP853)`로 미분방정식을 **독립적으로** 푼 다음 `quad`의 별도 null-ray line integral과 이 해석식의 값을 비교한다. 한 개의 새로운 FLRW IVP만 수행하며, 원본 Bianchi IVP 9개는 신규 계산 수에 포함하지 않는다.

## 3. 실물 계산: 같은 적색이동의 방향별 거리

초기 source SHA-locked 원본 CE1AP CSV 16,842행, CE1AR 고정-z Bianchi 광학 5,562행을 입력하여 6개 z-shell `(0.005,0.01,0.015,0.020,0.025,0.030)`, GL8/16/24, eps=0,±.035, 103 방향에 **새로운 FLRW 모델 거리 기준**을 결합했다. 원본 Bianchi beam은 절대로 재작성하지 않는다.

새 결과: FLRW ODE solution physical-time row **401**, 6개 self-consistent FLRW optical shells, 새로운 Bianchi–FLRW 물리 비교 **5,562행**, 54개 GL/eps/z 방향별 통계(96개 Fibonacci sky 방향 표본의 샘플 평균, 구면 연속 적분 아님), **2 PNG + 2 SVG**. 별도 새로운 Bianchi 원본 IVP 0, 새로운 FLRW 물리 IVP 1.

GL24 eps=0, z=.02:

| 대상 | D_A/(cT_*) | 초기 에너지 일치 FLRW 대비 |
|---|---:|---:|
| original Bianchi x | .028044169626674734 | -26.5333659637% |
| original Bianchi y | .048605391588600874 | +27.3303707532% |
| original Bianchi z-axis | .04260215256293194 | +11.6038304276% |
| independently evolved FLRW | .0381726616368811 | 0% (reference) |
| former equal-volume kinematic proxy | .03762296987030096 | -1.4400142484% (proxy bias) |

이는 **고정 관측 적색이동**의 원본 지오메트리 조건부 효과이며 원본처럼 편광/열화학/광학깊이/관측 SN·CMB likelihood 없음. 방향별 분포가 다른 별도 FLRW source를 비교하므로 차이 전체를 '기하만 바꾼 결과' 또는 '실제 관측 검출'로 해석하면 안 된다.

## 4. 검증·실패 분류

**Local real physics:** `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python source/ce1as_flrw_reference.py`, `python -m pytest -q source/test_ce1as_flrw_reference.py source/test_ce1as_remote.py`, `python source/plot_ce1as.py`.

실제 local 테스트 **18/18 PASS**, 원본 두 입력 SHA256 exact, negative forged-input rejection, 질량없는 등방 Vlasov angular tensor `⟨n_i n_j⟩=δ_ij/3`, Friedmann constraint, `rho*a^4`, FLRW exact `a²`와 null-ray `D_A(z)`, old equal-volume proxy not an IVP, 원본 Bianchi GL24 axes and claim ceiling checks. 독립 IVP-vs-analytic 최대 scale-factor relative **5.750955267558311e-14**; `rho*a⁴` relative **4.1866510258614653e-13**; Friedmann absolute **3.3306690738754696e-16**; analytic-vs-IVP null distance maximum absolute **1.7139067942650854e-15**; independent-replay redshift max absolute **5.062616992290714e-14**.

Test-repair incident: initial Gauss-Legendre × azimuth angular isotropic-stress trace check was set at arbitrary `<2e-15`, computed finite-sum roundoff `2.3314683517e-15`; revised *test-only* threshold to `<4e-15`, matching the already applicable tensor element acceptance and expected floating summation. No physical equation, source, scientific result or solver tolerance changed; all 18 tests rerun and PASS. Same-author calculations cannot certify independent-author review, continuum error or full observational pipeline.

The GitHub CI accepts only source-binding metadata from the original PR301 source replay and PR306 fixed-z replay, and additionally checks three frozen original GL24 source optical anchors; generated CSV bytes are **not** asserted byte-identical across Python/BLAS implementations. Local standalone S2 remains byte-locked.

## 5. Claim ceiling and actionable next physics

`COMPLETE_SCOPED_LOCAL_FLRW_RADIATION_COMPARATOR`, **not** full OB1, **not** same phase-space source, no measurement, no REI IGM bridging, no production, no merge. Science completed within this unit: independently evolved positive isotropic collisionless Vlasov matter+Einstein geometry and matched photon distance, side-by-side with frozen owner Bianchi. Remaining OB1 requires observationally meaningful source-owned opacity / visibility or a fully specified detector/likelihood plus physical parameter model. Original BASS Type-II/VI0 production critical path is unchanged; governance PR305 is separate.
