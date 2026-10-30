# BASS KM-2G | 전하중성 전자–양성자 관성과 원본 P8 광자, Einstein–Bianchi I 실제 물리 진화

2026-10-30. 원본 PR278 고정 HEAD `29ee9114856d493dac2f5e8328c145050169c13e`에서 신규 Draft **PR279**로 분리한 한정 연구 단위. 상위 BASS DAG **9/15, 21 edges**, KM-2 **PARTIAL**, 신규 완료 상위 노드 **0**. Main, 생산 코드, 기존 CE1·KM2A/C/D/E/F 원본을 편집·병합하지 않았다. 사용자가 지정한 진전 우선 정책에 따라 **실제 광자·중성 바리온·Einstein의 6개 물리 이력**을 생산했다.

## 1. 이론 R2–R5: 무엇이 달라졌는가

이전 KM2F는 실제 전자 1종의 Thomson recoil과 총 먼지 관성을 편의적으로 동일하게 취급했고, 이를 실제 수소 플라즈마로 해석할 수 없었다. KM2G는 냉수소의 **전자와 양성자를 종별로 보존**하는 한계 모델이다. 전자와 양성자의 고유 수밀도는 `n_e*=n_p*`, 공통 4-속도 `U_e=U_p=U`를 가지며, 전자–이온 Coulomb momentum transfer는 무한히 빠른 이상적 제약으로 구현한다. 이때 4-current는 `j^a=e(n_p* U^a-n_e* U^a)=0`이지만, Maxwell equation이나 유한 slip을 풀었다는 의미는 아니다.

원본 `(-,+,+,+)`, `Λ=0`, `u=t/Tstar`, 원본 전체 P8 편광 ray, 원본 KM1 기하 coframe/screens와 KM2A cold Thomson source, 원본 KM2F Hamiltonian·운동량 제약은 그대로 두었다. 냉바리온의 정상계 텐서 `T_b^{ab}=M_b ζγ (1,β)^a(1,β)^b`에 대해

`T_e=μ_e T_b, T_p=μ_p T_b, μ_e=m_e/(m_e+m_p), μ_p=m_p/(m_e+m_p)`.

원래 광자 순간 fourforce를 `Fγ`라고 하면 electron은 Thomson에서 `-Fγ`를 직접 받고 이상 Coulomb 제약에서 `+μ_p Fγ`를 받는다. Proton은 Coulomb 제약에서 `-μ_p Fγ`만 받는다. 그러므로

`F_e,net=-μ_e Fγ, F_p,net=-μ_p Fγ, Fγ+F_e,net+F_p,net=0`, `F_e,Coul+F_p,Coul=0`.

이 힘은 모두 물질 공통 4-속도에 직교하며, 각 종의 normal-frame dust stress E/Q/P와 보존식이 독립 산출물이다. `μ_e=0.00054432057524`, `μ_p=0.99945567942476`. 틀린 전자 단독 recoil inertia를 쓰면 바리온 가속도를 약 1837배 잘못 계산하는 반례를 실제 테스트했다. 원본 finite-angle photon force와 공변 force 사이의 `δF_quad`는 별도로 유지되며 Einstein 제약 전파 `C_H'=-κ δF_quad^0`, `q_total'=-(4HI+σ)q_total+δF_quad^sp`에 반영된다.

기존 synthetic `R_b0/rhoγ0=3`, `κ=0.003`, `u∈[0,.25]`는 고정했다. SI `G=6.67430e-11 m³ kg⁻¹ s⁻²`, `c=299792458 m/s`, `σ_T=6.6524587051e-29 m²`, NIST/CODATA2022 전자질량 `9.1093837139e-31 kg`, 양성자질량 `1.67262192595e-27 kg`를 사용했다. 반응률이 이제 독립 파라미터가 아니라 다음 dimensionalization에서 결정된다.

`ρ_unit=κ c²/(8π G Tstar²) [J/m³]`,
`n_e*(0)=R_b0 ρ_unit/[(m_e+m_p)c² γ0²] [m⁻³]`,
`ν0=n_e*(0) σ_T c Tstar=R_b0 κ σ_T c/[8πG(m_e+m_p)γ0² Tstar]`.

`ν0∝1/Tstar`는 **κ와 정규화된 에너지밀도를 고정했을 때**의 관계이며 Tstar를 변화시키는 것은 동일 관측우주의 시간축을 단순 재표기하는 것이 아니라 **다른 물리 단위 정규화 실험**이다. 여기서 인공적인 `R_b0/rhoγ0=3`과 광자 source는 미관측 초기 분포로 남는다.

## 2. R7/C5–C7: 실제 생성한 물리 데이터

원본 BASS P8 광자 분포, 양의 GL ray·weights, Einstein 제약을 변경하지 않고 nθ=12/16, nφ=2nθ의 6개 풀 coupled IVP를 실제 실행했다. 새로운 시간척도는 3,000,000 / 10,000,000 / 57,883,065.06488644 Julian years, 마지막은 기존 KM2F의 `ν0=1.3`을 독립 SI 계산에서 정확히 회복하는 대조군이다. 모든 수치는 코드의 무차원 물리 변수로 해석하며 관측 우주 연령의 구간이 아니다.

| Tstar (Julian yr) | 최초 ν0 (무차원) | 실제 각 ray optical depth 범위 | H(0.25) | 최종 |β_b| | Einstein source로 생긴 shear 변화 ‖σf−ζfσ0‖ |
|---:|---:|---:|---:|---:|---:|
| 57,883,065 | 1.3 | 0.2409211104–0.3382732374 | 0.34728215455 | 0.129217064 | 0.006969833067 |
| 10,000,000 | 7.524798458 | 1.547812911–1.802015335 | 0.347385357145 | 0.0160786913 | 0.003674483788 |
| 3,000,000 | 25.08266153 | 5.440783831–5.7202395 | 0.347410330863 | 5.05486733e-05 | 0.001494009073 |

새 광자 응력과 산란이 비등방성에 실제로 다르게 작용했다. 예를 들어 `Tstar=10⁷ yr`, `GL16`에서 직접 측정한 `n_e*(0)=1,195,605.8051642766 m⁻³`, `ν0=7.524798458435237`, 최종 `H=0.34738535714548485` 및 Einstein source shear `0.0036744837876110533`이다. 같은 원본 초기 광자/기하 조건에서 `ν0=1.3` 대조군의 shear `0.006969833067281051`과 분명히 구별된다. 광학깊이는 방향별 raw positive ray에 따라 달라진다. 온도·재결합률 입력을 새로 추정했다고 주장하지 않는다.

GL16 최대 정규화 Hamiltonian, 총 momentum 제약은 각각 10⁷ yr `3.830328333850468e-12`, `1.013814258695286e-11`이고 3×10⁶ yr `4.710099424792677e-12`, `1.250407739327624e-11`이다. GL12에서는 각각 O(10⁻9)이다. 광자 force finite angular quadrature와 장시간 integration의 의미를 분리했다. GL16↔GL12 차이는 **각도 적분 수렴 관찰**이지 무한 ray continuum에 대한 MPFR 인증은 아니다. 6개 사례의 5개 epoch마다 `ρ_e,ρ_p,P_e,P_p,Q_e,Q_p,n_e,n_p,j^a,Mγ,H,σ,β,ν,δF` 원시 행과 GL24 constraint/source integration을 저장했다.

## 3. Blind referee, R6/C9 (같은 모델 자기 적대적 검산)

대상은 (i) 원본 불변 source provenance, (ii) e/p 힘 부호·수밀도, (iii) 상대론적 γ0² 정규화, (iv) 원본 Thomson 응력과 charge neutrality, (v) Einstein 제약과 극한, (vi) 가짜 전자 단독 관성. GitHub Actions #41037404278은 SciPy1.17.0, NumPy2.3.5, pytest9.0.2에서 실제 완전 재계산 **15/15 PASS**. S0 archiver가 NumPy 설치보다 먼저 실행되어 초기에 CI가 `ModuleNotFoundError: numpy`로 중단한 것은 **환경/실행 순서 문제**였으며, 물리 코드와 gate를 바꾸지 않고 워크플로 순서를 바꾼 commit `02532207a454f505c2349e54f8f2d99a2279630a`에서 재실행 성공했다. 원본 부모 KM2F 12/12 PASS는 별도 검증이었다.

별도 saved-data blind countercheck는 실제 30개 원시 물리 행으로부터 코드 RHS 호출 없이 종별 응력합, Coulomb 내부력 상쇄, photon+e+p force 합, n_e=n_p, 전하 및 전류, opacity를 재계산한다. 결과는 다음에 기재한다. 이는 독립 **코드경로 검산**이나 별도 저자가 개발한 모델의 승인을 뜻하지 않으며, native subagent와 distinct-author R6/C9는 NOT_RUN이다.

- `rho` max absolute residual = `1.4210854715202004e-14`.
- `q` max absolute residual = `1.7763568394002505e-15`.
- `pressure` max absolute residual = `4.4408920985006262e-16`.
- `force` max absolute residual = `1.1368683772161603e-13`.
- `coulomb` max absolute residual = `0`.
- `electric_charge` max absolute residual = `0`.
- `electric_current` max absolute residual = `0`.
- `number` max absolute residual = `0`.
- `opacity` max absolute residual = `3.5527136788005009e-15`.


**관찰된 실제 numerical defect:** 강한 Coulomb lock에서 electron net force를 `-Fγ+μ_p Fγ`로 직접 빼면 O(10³) 성분 사이 상쇄에 의해 O(10⁻13) 절대오차가 생기므로, 정확히 같은 물리식의 안정된 `-μ_e Fγ` 형태로 평가했다. 또한 force orthogonality의 비교척도는 `ν rho_gamma`가 만들고 있는 원래 연산의 ULP에 따라 결정해야 하며 작은 결과 force의 ULP만을 분모로 삼으면 근거 없는 false FAIL이 발생한다. 물리적 모델이나 부모 정확도 기준은 수정하지 않았다. 이 변경은 signed binary64 계산의 수치적 표현에 한한다.

## 4. 원본 source, 백업과 보호 상태

KM2F exact parent git head `29ee9114856d493dac2f5e8328c145050169c13e`, source blob `einstein_bianchi.py=457790df7aba6d82326ac6f3be5814851b970b1d`, original Thomson `tilted_collision.py=92660768f4719d78261fed1cb44f186d2821629d`, KM2C `curved_tilt.py=05aade3aab7e9a32c11608882c943e4d3cb6f379`, KM1 `source_memory.py=9d500e36fefaa4ddc22300a2f03d9eb9cfe98403`, KM2D `accelerating_tilt.py=b599d3842e843d8de1de1499b73e6849374bf8f8`, KM2E `coupled_electron_photon.py=12fbce8109fc07b1fbf60d9a066d8aa1c57ea9c1`. S0 commit `0ae2f7139a6ef4225b0f491a05778d35ee850f8c`, S1 source commit `74da3dd4d368a9e28082fa08112cdb2cc57a690b`, CI order fix `02532207a454f505c2349e54f8f2d99a2279630a`.

Actual science GitHub Actions #41037404278 **SUCCESS**: S0 #12968915944 outer 48,900 bytes SHA256 `56933f9892e019b16a335d050e312259b3036b7f20ae8e44dec95f0347934e49` (inner 12 member); S1 #12969330029 outer 144,029 bytes SHA256 `5f8edc0dd27afcfc1479617f00e0de146dce00730990d75b17ff471c993f9af6` (inner 18 member); S2 #12968129340 outer 218,878 bytes SHA256 `05a044a82d10c48e7596383176a5d4d8953340bc2786277f8490d964bceb012a` (inner 19 member). All nested member SHA/CRC PASS. Actual Google Drive create-only backups:

- S0 `1c7AcS932EE1Cj0wkAhVLiUbvU8cZJ_73`
- S1 `1dJQU0V4uSP8IDwb6DqiXFvuLO0fTWFZP`
- S2 `1LmeVEbRzbnKFVsmjcDf7QcL41bi0e9-C`

각 provider ACK 및 **원시 전체 바이트를 재다운로드해 SHA256 일치**를 확인했으며 ChatGPT Library `/BASS_KM2G_20261030`에도 S0/S1/S2와 S0 이론·S1 코드가 있다. Dropbox 신규 ZIP upload는 host-injected `source_file` 매개변수 연결이 불가능하여 **BLOCKED_NOT_UPLOADED**. 별도 성공 영수증을 만들어내지 않는다. 최종 문서 포함 ZIP 및 그 Git HEAD의 CI는 이 문서 commit 이후에 반드시 새로 확인하여 PR metadata에 영수증을 추가한다.

## 5. 과학적 결론, 기존 DAG와 남은 문제

- **Derived**: 완전 중성·공동 U ideal locking에서 전자/양성자의 종별 정상계 스트레스와 내부 반작용 정확 분배; 단위계 일관적인 `ν0(Tstar)`.
- **Implementation-verified / numerically checked**: original unchanged P8 Einstein solver를 기반으로 한 6개 실제 물리 이력과 optical depth·전하중성·Hamiltonian/momentum constraints; 15/15 GH CI.
- **Not established**: finite Coulomb slip, plasma E/B dynamics, electron temperature, Kompaneets/Compton frequency redistribution, neutral hydrogen/recombination, actual blackbody photon spectrum, observational baryon density, rigorous continuum angular convergence, future inhomogeneous Einstein–Boltzmann modes, production code, distinct-author independence.
- **No new upper DAG completion**: BASS 9/15, KM2 PARTIAL. BF1/BF2/BF3 already have scoped historical work and cannot be counted new simply by reusing its name. PR277 CE1-AB and other repos REI286 / VigilODE133 / REC169 remain **separate immutable research lines**.

References and outside data. Ma & Bertschinger, *ApJ* 455, 7–25 (1995), DOI `10.1086/176550`, arXiv `astro-ph/9506072`; Hannestad, *On the coupling between different species during recombination* (2000), arXiv `astro-ph/0008452`; Pookkillath, De Felice & Mukohyama, *Universe* **6**, 6 (2020), DOI `10.3390/universe6010006`; Cyr-Racine & Sigurdson, *Phys. Rev. D* **83**, 103521 (2011), DOI `10.1103/PhysRevD.83.103521`. Mass/σT/G: NIST CODATA2022 `https://physics.nist.gov/cuu/Constants/index.html`. To advance to actual ionization and thermal photon domain, obtain a parameter-fixed `x_e(z), T_b(z)` history from HYREC-2 `https://github.com/nanoomlee/HYREC-2` (2020, PRD102 083517) or CLASS `https://github.com/lesgourg/class_public`, along with a physically specified photon spectral initial distribution and cosmological calibration. No new user-provided PDF required for the *present* ideal cold-lock unit.

STOP_AFTER_ONE_BOUNDED_UNIT=true. `production_ready=false;merge_ready=false;auto_next=false`.
