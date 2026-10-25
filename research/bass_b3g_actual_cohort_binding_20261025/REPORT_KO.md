# BASS B3g/B3h/B3i 저장 입력 결합 연구 보고

## 판정 범위

고정 인계 bass@d6af237b66e78ca6ed4572068f6bc1a805bbb2d9를 이어,
기존 G1B와 B3의 완료 결과를 재사용했다. 이번 새 실행은 실제로 복구한
B3c 저장 birth 512개와 geometry endpoint 514개를 소비하는 유한 단위다.
13개 focused test와 4회의 algebraic core RHS 확인을 통과했다.
새 IVP, 기존 캠페인 재실행, native owner solve, 유한 흡수 거래는 각각 0이다.

여기서 “실제 저장 cohort”는 B3c의 이미 실행된 원자료라는 뜻이다.
그 원모델은 manufactured cold / non-tilted / recoil-free / detached
f_plus=0 Bianchi I다. 이를 calibrated REC cosmology로 승격하지 않는다.
새 admission은 출생 시점 결합과 stress/force interface의 제한된 검증이다.
최종 운반행렬, native finite donor, 실제 물리 오차 인증은 아래의 선택된
입력에 의존한다. 전체 물리 완료율은 null, L4=false다.

최종 독립 판정은 ADMISSION.json과 reviews/R9_INDEPENDENT_FINAL_REVIEW.md,
실제 게시·백업 식별자는 DELIVERY_RECEIPTS.json을 참조한다.
results/SUMMARY.json의 PENDING_ROOT_DECISION은 실행 당시 snapshot으로 보존한다.

## 1. 직접 복구한 자료와 재사용한 계산

| 자료 | 실제 복구·소비 | 유지한 한계 |
|---|---|---|
| B3c S2 원본 ZIP | 7,021,644 bytes; SHA256 0d3a911d7fc1b567c0e915cd655af94bff44495849bd0e7ce1bcb778a94bd1b2; ZIP CRC 확인 | 기존 12 IVP, 검증·수렴 자료를 재실행하지 않음 |
| B3c ISO/ANISO N256 | 각 256 birth, 각 257 endpoint; 원 transfer key와 source snapshot 보존 | midpoint beta는 저장되지 않음 |
| REC 실제 source history | 35,239,470 bytes NPZ; SHA256 d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1 | 전체 원자료는 최종 ZIP에 포함; 이미 공개된 Git blob을 중복 게시하지 않음 |
| REC HISTORY_ADMISSION | 기존 313 query row를 그대로 재사용 | 최대 3.219042386314642e-15는 기존 reconstruction의 수치 비교이며 physical epsilon은 null |
| native LINE02 snapshot/source | 원 decimal, Git source identity, hydrogen.h/c와 native 상수 보존 | incoming angular distribution과 finite donor/face 결속 미공급 |
| G1B / B3a,b,b2,d,e,f | 기존 admission, finite-count/positive-angular/finite-input-error 결과와 비용 재사용 | 기존 실패, UNKNOWN_NO_ACK, 미상 잔여 예산 유지 |

REC PB01 원 primary의 실패/exit2, 32-vector repair의 scoped pass,
repaired full primary NOT_RUN은 소유자 기록대로 유지한다.
B3c의 과거 거절된 게시 요청도 이번 신규 consumer 게시와 구별한다.
이번 작업은 그 과거 요청을 재시도한 것이 아니다.

원자료와 재사용 의존성의 exact bytes는 inputs/MANIFEST.json에 있다.
REC 원본 위치:
https://github.com/cosmosapjw-quantum/rec_bianchi/blob/ea89c97abeb7a663a813f00e9aadddaf0b32a6a9/data/pr05b2_source_history_v060.npz
native source의 고정 위치:
https://github.com/cosmosapjw-quantum/rec_bianchi/tree/a7c46fd8338971e2cefa776f5dd7b25a46974990/research/rec_line_native_owner_20261023

## 2. B3g: 출생 시점의 실제 cohort 결합

각 source receipt의 ledger.down_m3는 proper time에 대해 이미 적분된
gross downward count density다. dt를 다시 곱하지 않았다. 출생 frame과
event가 같으므로 R(t_b,t_b)=I, det R=1이다.

선택된 각도 모델 q(n)=1+n^T S n에서

```math
T^{00}=E_b n_b,\qquad T^{0i}=0,\qquad
T^{ij}=E_b n_b\left(\delta^{ij}/3+2S^{ij}/15\right),\qquad
\pi^{ij}=2E_b n_b S^{ij}/15 .
```

이는 degree-four 각도 moment이며 기존 Q14 표현과 출생 시점에 일치한다.
물질 rest energy를 분모로 삼으면 photon/source 잔차가 가려지므로,
birth energy·spatial tensor·pi 비교는 모두 양수 E_b n_b scale을 사용했다.
atom stock의 뺄셈 잔차는 별도의 양수 stock scale로 평가했다.

| 관측량 | 최대 절대 정규화 잔차 |
|---|---:|
| birth radiation energy | 0 |
| birth spatial stress | 8.954349614085686e-17 |
| birth signed pi | 2.9460247944247483e-18 |
| source proper duration / ledger duration | 0 / 0 |
| atom stock lower gain | 1.8487977597601093e-16 |
| atom total preservation | 1.5478790089972602e-16 |

표현 검증 기준 512*binary64 epsilon을 변경하지 않았다.
source clock은 producer의 source_subflow_duration_tau를 사용한다.
누적 interval endpoint의 차이는 별도의 clock diagnostic으로 남겼다.
마지막 receipt에서 이 둘을 바꾸면 누적 시각 반올림 때문에 false-FAIL이
생길 수 있어 독립 검토에서 실행 전에 교정했다.

B3f 입력에는 출생 identity의 eR=0만 정당화된다. eS, en, eE는 null이다.
모든 출생 행의 fixed-E B3f 결과는 INPUT_ERROR_UNSPECIFIED다.
표현 잔차가 작다는 이유로 total physical error 또는 원래 2e-8 목표를
인증하지 않았다. E_b의 실제 불확실성은 기존 fixed-E 정리 밖의 별도 항이다.

## 3. G1C: 입력이 주어질 때 사용할 운반 오차 경계

Bianchi I 대각 운반에서는 a_i=Delta alpha+Delta beta_i,
Rhat_i=exp(-a_hat_i)다. |a_i-a_hat_i|<=e_i가 주어지면

```math
\|R-\widehat R\|_2
\leq \max_i \left[\widehat R_i\,\operatorname{expm1}(e_i)\right].
```

beta가 정확히 trace-free이고 alpha 반경 e_alpha가 주어지면

```math
|\det R-\det\widehat R|
\leq \det\widehat R\,\operatorname{expm1}(3e_\alpha).
```

physical radius와 numerical radius를 별도 record로 받고, 둘 다 공급된
경우에만 명시적인 triangle inequality로 합친다. null을 0으로 치환하지
않는다. 극단적인 입력에서 양수 map·determinant·bound가 0으로 underflow
되면 typed range refusal을 내며, 0 상계로 반환하지 않는다.

일반 행렬의 조건부 Duhamel 경계도 구현했다. Ahat은 정확한 nominal
수학적 계수장이고, coefficient의 수치 재구성 오차는 defect
D=Rhat'+Ahat Rhat에 들어간다. physical/model mismatch eta와 numerical
defect d를 분리하여, interval-wide envelope가 주어질 때

```math
B_{\rm phys}=e^{mT}e_{0,\rm phys}+\eta M T\varphi_1(mT),\qquad
B_{\rm num}=e^{mT}e_{0,\rm num}+dT\varphi_1(mT),\qquad
\varphi_1(z)=\operatorname{expm1}(z)/z,\quad \varphi_1(0)=1 .
```

m=mhat+eta다. 유도와 가정은 theory/TRANSPORT_AND_GEOMETRY.md에 있다.
이것은 정확 산술에서의 조건부 운반행렬 오차 상계이며, 전체 비선형
geometry tube의 폐쇄를 증명한 것은 아니다. binary64 evaluator의
검증과 outward-rounded interval certificate도 구별한다.

현재 저장 자료에서는 midpoint beta_birth와 그 보간 오차 경계가 없다.
alpha_birth는 -log(N_mid/N0)/3로 nominal하게 복원했으나 원래 alpha bytes와
수치 오차 경계를 대신하지 않는다. 따라서 actual final R과 physical
determinant radius는 null이다. 저장 sample residual을 interval-wide
Lipschitz/defect envelope로 간주하지 않았다.

## 4. B3h: native source convention과 finite donor의 경계

복구한 native departure는 Dfplus_Lya=7.6643364422337378e-15다.
native LINE02는 Wien departure convention을 사용한다.

```math
f_+^{\rm native}=e^{-E_{21}/T_R}+Dfplus_{\rm Lya}.
```

standalone LINE01의 Planck/stimulated 모델은
1/expm1(E21/TR)+Dfplus다. 두 이름과 reference law를 분리했다.
이 snapshot에서는 합산한 binary64 값이 같게 보이지만, 이것은 두
convention을 교환할 근거가 아니다. focused control은 Decimal 70자리로
그 차이를 확인한다. E21=10.198714553953742 eV이며 TR도 eV라 k_B를
추가로 곱하지 않는다.

native LYA_FACT와 hPc를 그대로 사용했다. modern exact-SI hc로 교체하면
native 계수의 상대 변화는 -2.661653527580299e-7이다. 이는 source model
변경이며 roundoff가 아니다. 직접 교환 owner는 Trr[1,1]+=r와
sr[1]+=r*b의 일치하는 pair뿐이다. two-photon/Raman, virtual diffusion,
history 등의 소유권은 그대로다.

기존 instantaneous ledger의 net emission
1.372687295276845e-8 m^-3 s^-1,
photon energy rate 2.2429905539433765e-26 J m^-3 s^-1을 재사용했다.
이는 evolved stress T나 finite donor transaction의 완료를 뜻하지 않는다.

native source의 local non-tilted matter tetrad와 proper seconds 규약은
알려져 있다. 아직 없는 것은 그 source와 유한 donor를 잇는 공통 binding이다.

| 남은 선택 입력 | 필요한 의미 |
|---|---|
| donor cell → incoming face map | 실제 입사면 trace를 어느 유한 inventory에서 가져오는지 |
| spectral/angular/time support와 measure | donor 수와 occupation을 연결하는 유한 적분 영역 |
| common frame/proper clock/volume | native 규약에 donor를 결속하는 단위·시각·부피 |
| atomic internal energy/recoil owner | 선택 반응의 에너지·운동량 수지를 책임질 명시적 소유자 |
| physical radius provenance | source, inventory, support, geometry, energy의 실제 입력 오차 |

B3b2의 910 initial cell-average packet을 native incoming face로 자동
간주하지 않았다. effective hydrogen collapsed 2p/1s mapping은 유지하고
isotope-resolved 정밀도를 새로 요구하지 않았다. 선택하지 않은 미래
공급자 전체를 선행조건으로 추가하지 않았다.

readiness는 metadata/input-candidate readiness와 실제 물리 거래를
구분한다. 이번 단위의 physical_finite_absorption=false,
transaction_executed=false이며, 완전히 채운 actual-labelled metadata도
거래 완료로 승격하지 않는다.

## 5. B3i: 물질·복사 응력과 four-force의 geometry 결합

metric(-,+,+,+), x0=ct, tau=ct/L,
alphaL=(8*pi*G/c^4)L^2를 사용한다.
각 sector의 T는 J m^-3이고, cQ는 J m^-3 s^-1인 energy-equivalent rate다.

```math
\widehat\rho_s=\alpha_L T_s^{00},\quad
\widehat F_s^i=\alpha_L T_s^{0i},\quad
\widehat p_s=\alpha_L\operatorname{tr}(T_s^{ij})/3,\quad
\widehat\pi_s^{ij}=\alpha_L(T_s^{ij}-p_s\delta^{ij}),
\qquad (U_s,J_s)=\alpha_L(L/c)(cQ_s^0,cQ_s^i).
```

lower-rest R, excitation X, radiation을 세 sector로 유지한다.
R/X는 선택된 cold model의 dust이고, radiation은 p=rho/3와 signed pi를
가진다. energy flux는 c*T0i이며 Q를 T나 pi에 더하지 않는다.
저장 endpoint는 source kick을 이미 반영했으므로 재소비 시 U=J=0이다.
synthetic transfer control은 반대 부호의 radiation/excitation cQ와 단위를
검사하지만 실제 finite absorption으로 admission하지 않는다.

514 endpoint에서 SI↔fixed-scale 왕복 최대 잔차는
7.38692856273411e-17, radiation trace 잔차는
2.7425075540512394e-16이다. ISO/ANISO 처음과 마지막 endpoint에서만
4회 호출한 core RHS의 직접식 비교는 dh 2.220446049250313e-16,
dsigma 5.551115123125783e-17, drho=dflux=0이다.
이 RHS 값은 dimensionless absolute residual이며 photon birth의 상대
분모와 섞지 않는다.

SECTOR_STRESS.png의 ISO pi 패널에서 약1e-26의 값은 저장 binary64
잔차와 stress 분해 반올림이다. 수학적 등방모델의 실제 비등방 신호로
해석하지 않는다. ANISO 패널의 약1e-12 signed stress와 별도 scale이다.
실제 zero와 signed pi를 그림에서 보존했으며 clipping은 없다.

## 6. 구현·독립 검토·실제 비용

Astra 과학 계약 → 요청된 gpt-6.1-sol 구현/한정 실행 → 별도 과학 검토로
진행했다. 요청 모델명과 실제 backend 관측은 구분하며 observed model은
null이다. 현재 Python은 3.12.14이고 실제 dependency versions는
results/EXECUTION_LEDGER.json에 있다.

실행 전 C9는 clock, positive underflow, metadata-only physical admission,
near-isotropic trace cancellation의 4개 구현 결함을 찾아 한 번의
targeted repair로 닫았다. 허용 오차·모델·예산을 변경하지 않았다.
기존 finding과 교정 후 hash를 모두 보존했다.

| 새 child | wall seconds | CPU seconds | 결과 |
|---|---:|---:|---|
| focused tests | 0.5471585380000761 | 0.5412909999999999 | 13/13 PASS |
| saved-input consumer | 0.9518043909993139 | 0.95114 | PASS |
| saved-result plots | 2.240260294001928 | 2.233869 | 3 PNG |
| 합계 | 3.739223223001318 | 3.7262999999999997 | retry 0 |

새 bounded postprocessing allocation은 implementation60wall/40CPU,
task guard120wall/60CPU, child30wall/20CPU다. 이것은 과거 미상 예산의
초기화나 재배정이 아니다. historical remaining wall/CPU는 null,
budget_reset=false이며 원 debit·실패·UNKNOWN_NO_ACK를 보존했다.
download/hash/copy/archive/provider wait는 I/O로 구별한다.

## 7. 정확한 다음 실행 전선

1. B3g: 동일 B3c receipt의 midpoint beta와 검증 가능한 보간/복원 오차,
   또는 해당 source owner가 제공하는 R와 실제 radius를 결속한다.
   이미 소비한 512 birth나 G1B/B3 캠페인을 다시 적분하지 않는다.
2. B3h: 선택된 effective H Lyalpha donor의 cell-to-face map, finite support,
   measure, common clock/frame/volume, energy/recoil owner를 확보한 뒤
   기존 B3b/B3b2 finite count map으로 한 거래를 구성한다.
3. B3i: 그 한 거래의 sector별 T와 Q를 이번 adapter에 넣고, 새 실행이
   필요하면 별도 frozen command와 남은 예산을 먼저 확정한다.
4. G1C: 실제 interval-wide envelope가 공급되면 이번 조건부 식을 평가한다.
   전체 nonlinear tube 또는 전역 convergence는 별도 남은 문제다.

DAG.json은 BASS의 현재 제한된 전선을, CENTRAL_RETURN.json은 중앙
88-node DAG에 반영할 선택 변화와 immutable evidence를 나타낸다.
B4 production restart와 B5 domain validation은 NOT_RUN이다.

게시 직전 중앙 HEAD가 HE 관측 fc2c604를 거쳐 GRID044 endpoint
ad9c0e29453fcb6d66637413b51bf42f08688cf1로 이동했다. 새88개 노드와
모든 동시 관측을 보존하여 재조립했다. GRID044의 실제 z≈2 endpoint와
순간 photo-event source도 직접 읽었으나, 해당 BASS_INPUT_JOIN의
new_absorption_angular_measure와 new_absorption_stress_tensor는 null,
geometry_feedback은 OPEN이다. 이는 B3c midpoint beta/radius나 native
z≈1100 Lyalpha finite donor 결속을 채우지 않는다. 원문의 정확한 수신
결과는 provenance/CONCURRENT_GRID044_INPUT_INTAKE.md에 보존했다.

## 8. 실제 게시와 최종 소스 백업

과학 source A는 0e07ea8ca2f11901e0818c9ab9afdeff76352618 (BASS PR192),
검토용 중앙 C는 86ec7e3c84d3d0a1f521866441e1e0e2b6bac14e (PR231)다.
후속 CR 두 관측까지 보존하여 활성 중앙 분기에 반영한 M은
a5db4bac9dafadae29685bbea3cec7f43ab990b2 (기존 Draft PR222)다.
모두 expected-SHA, force=false를 사용했고 실제 원격 HEAD readback이
일치했다. PR merge와 production activation은 수행하지 않았다.

최종 BASS_B3G_S2_FINAL_20261025.zip은 38,152,861 bytes,
SHA256 0e11ce05e10d95cd9c002b719f053659ce941bb1b54fcc1c9a64e4ac4d73899d다.
124 ZIP members 중123 payload의 size/SHA256과 CRC를 확인했다.
전체 REC NPZ와 재현 의존성 및 최종 검토 과학 결과를 포함한다.
Drive1AO1I2BSbwwCgF91Flhi2bIFwGGMb1qLU와
Dropbox id:BSpOijBcT10AAAAAAEAc8w의 실제 완료 ACK 및 metadata size가
일치했다. 원격 whole-byte 재다운로드를 했다고 주장하지 않는다.
최종 upload ACK/문서 commit은 자기참조를 피하여 ZIP 밖의
DELIVERY_RECEIPTS.json과 PR192 본문에 결속한다.

