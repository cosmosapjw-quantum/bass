# 저장 native history의 원자 상태 역복원과 유한 Lyα 순 반환

## 이번 결과

원 native solver를 다시 실행하지 않고, 이미 저장된 radiation의 incoming·average·outgoing 세 trace에서 선택 구간 `[5126,5127]`의 광학깊이와 source-effective H 원자 상태를 복원했다. 저장 Lyα·Lyβ·Lyγ 행을 함께 사용하여 `x1s`, `x2s`, `x2p`와 원자 내부에너지의 두 끝점도 확보했다. 같은 공통 부피에서 새 Lyα 순 광자 교환을 계산하고 기존 B3g 운반 연산자에 연결했다.

이것은 이전의 “선택 구간 absolute stock이 미확보” 상태를 실제로 줄이는 결과다. 유한 원자 transaction 전체의 물리 채택은 별도다. QSS algebraic state의 끝점 변화가 실제 non-Lyα 보충 채널과 그 에너지 장부에 아직 결속되지 않았으므로 새 B3i RHS 소비는 0회다. 최종 과학 판정과 독립 검토의 상태는 `ADMISSION.json`과 `reviews/C9_INDEPENDENT_REVIEW.md`가 정한다.

원 중앙 DAG의 완료 수는 **27/88**, 이번 원 노드 완료 증가분은 **0**이다. R1–R10/C1–C10의 이번 선택 단위 수행과 원 DAG의 물리 완료를 혼동하지 않는다. 전체 물리 완료율은 null, L4_ready는 false다.

## 1. 고정 원전과 재사용

- REC 과학 source: `d6dbe39a4923439547c01695d9020ba39367ea90`.
- 실제 저장 history: `data/pr05b2_source_history_v060.npz`, 35,239,470 bytes, SHA256 `d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1`.
- 정확한 원 `hydrogen.c`: SHA256 `421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b`.
- 삼중 trace packet: SHA256 `7d6e85bf2e759500d3e7d7249de5892bcc34ce7af77f08de10ae1607eacf19ef`.
- 세 Lyman outgoing packet: SHA256 `5a01a3dfab10f07450c828e0ca141a8dc69f40e713a57b71aae378c41e1ed8f3`.
- 기존 incoming tube 과학 S1: `74c6e4b8df36bbc39f073548a6b51b597da167c1`; 전달 F3: `29dcf5ab94ae8b84bf8e3f31dddb31ce719929b1`.
- 기존 512-cohort 과학 A2: `af14fc72d99f6d0e396f60aedadcdb5d05213280`; 전달 F2: `009a1238c09adf889c7421132f530b960cdafb07`.

이전 512개 실제 cohort의 midpoint/최종 운반, 2개 B3i RHS, incoming tube의 적분과 그림·tests를 재실행하지 않았다. 이번에는 저장 incoming 총량과 고정 정밀도 문자열을 읽고 새 순 교환만 계산했다. 이전 누적 비용과 미상 잔여 예산을 그대로 보존했다.

## 2. 삼중 trace가 주는 구성적 역해

원 source의 exponential branch에서 departure occupation을 `i=fin`, `o=fout`, `v=favg`, `s=feq`로 두면

\[
o=i+(1-e^{-\tau})(s-i),\qquad
v=P i+(1-P)s,\quad P=(1-e^{-\tau})/\tau.
\]

따라서 해상된 `D=o-i != 0`에 대해

\[
r=\frac{v-i}{o-i}=F(\tau)
=\frac1{1-e^{-\tau}}-\frac1\tau,
\qquad
F'(\tau)=\frac1{\tau^2}-\frac1{4\sinh^2(\tau/2)}>0.
\]

`F:(0,infinity)→(1/2,1)`이므로 admissible ratio는 유일한 양의 광학깊이를 결정한다. 원 C의 `tau<=1e-6` 다항 분기는 별도다. 선택한 12개 역해는 모두 원 exponential branch에 있으며, 잘못된 ratio를 clipping하지 않았다.

주 bin 273과 비교 bin 272,267,268,269,309는 모두 원 diffusion 구간 `[100,180)` 밖이다. 이들의 Γ는 원 TR·two-photon table만으로 정해진다. 아직 모르는 Tm을 새 전제조건으로 만들 필요가 없다. 원 λ, nH, H를 사용하면

\[
x_{1s}=\frac{8\pi H\tau}{\Gamma\lambda^3 n_H}.
\]

오른쪽 저장 snapshot의 x1s·τ·Γ는 선택 조건과 검증에만 사용했다. 이 값을 inverse의 입력이나 fitted coefficient로 넣지 않았다. 모든 수는 입력의 binary64 hex에서 시작했으며, source native-z 연산 순서와 기존 tube의 exact-real affine eta 시계는 각각 보존했다.

저장된 thick Lyα departure `dα`와 Lyβ·Lyγ departures로

\[
x_{2p}=3x_{1s}(d_\alpha+e^{-E_{21}/T_R}),
\quad
y_s=d_\beta e^{E_{32}/T_R}=d_\gamma e^{E_{42}/T_R},
\quad x_{2s}=x_{1s}(y_s+e^{-E_{21}/T_R})
\]

를 얻었다. 같은 virtual bin의 `feq`와 Γ·Cs·Cp로 구한 y_s도 별도로 비교했다. C9에서 처음 사용한 heuristic 오차식을 실제 trace/tau/계수 구간 전파로 한 번 수정했다. 32-ulp 입력·계수 오차모형은 명시적인 수치 진단 가정이며 원 solver 전체의 오차 증명이나 물리 반경이 아니다.

## 3. 실제 복원값과 수치 검증

| 양 | Native knot 5126 | Native knot 5127 |
|---|---:|---:|
| z | 1100.092131270856 | 1099.9986525171403 |
| bin 273 τ | 1.1076102907893572 | 1.1076274318532282 |
| x1s | 0.8549423676545932 | 0.8550700033096545 |
| x2s | 6.568412727733193e-15 | 6.563187316112037e-15 |
| x2p | 1.9746733281751027e-14 | 1.973106092162770e-14 |
| R_Lyα [s⁻¹] | 1.0832539936116934 | 1.0832181815556692 |
| τ_Lyα 진단 | 5.783346629949324e8 | 5.783537831996193e8 |
| 6-bin x1s의 주 bin 대비 최대 상대차 | 6.441026214723226e-14 | 3.8562484596277084e-14 |

Lyα τ 진단은 보존된 REC LINE01의 `A_effective=(6.2649e8+2*6.2648e8)/3 s^-1` 정규화를 사용한다. 이는 원 thick-line outgoing을 유한-τ solver로 변경한 것이 아니며 역복원 입력도 아니다. 원 HyRec의 R_Lyα와 이 진단 정규화의 출처를 구분했다.

주 bin의 오른쪽 x1s와 원 snapshot의 상대차는 `7.920240944016569e-15`다. source Γ·TR·nH·H는 오른쪽 snapshot의 binary64 값과 일치했다. 주 bin과 독립 70-digit inverse의 τ 상대차는 두 끝점에서 약 `4.01e-16`, `6.01e-16`이다. 출력된 일부 비교 0은 binary64 비교 결과이며 exact-real identity를 의미하지 않는다. 실제 고정 정밀도 문자열은 raw JSON에 남겼다.

원 effective-H convention은 `x1s=1-xHII`다. 미소 excited population을 ground에서 다시 빼지 않기 때문에 `x1s+xHII+x2s+x2p-1`의 source 정의상 excess는 약 `2.63e-14`이다. 이를 강제로 0으로 만들면 원 closure를 바꾸게 된다. 이 normalization 근사와 아래의 유한 storage defect는 별개의 양이다.

## 4. 기존 incoming tube에 연결한 새 유한 광자 결과

공통 material volume은 `V/V0=exp(3u)`이고 `h=8.49e-5`이다. 기존 retarded incoming PL과 실제 저장 Lyα outgoing PL의 차이 `j(u)`를 직접 적분했다. 공통 Wien 항은 식에서 소거된다. source retarded knot `u=5.278877465967507e-8`에서 적분 구간을 나눴다.

\[
\Delta N_0=G\int_0^h e^{3u}j(u)\,du,
\qquad
\Delta U_0=GE_{21,J}\int_0^h e^{4u}j(u)\,du.
\]

| 유한 관측량 | 값 |
|---|---:|
| ΔN0 [m⁻³, V0 기준] | 23.46391833488862 |
| ΔU0 [J/m³, 왼쪽 시각으로 pullback] | 3.8342003535474504e-17 |
| Nout0 [m⁻³] | 9140.55668717356 |
| Uout0 [J/m³] | 1.493643353446071e-14 |
| Nout1 [m⁻³] | 9138.228883843674 |
| Uout1 [J/m³] | 1.4931361982830613e-14 |
| 국소 사건 에너지 E21·ΔN0 [J/m³ per V0] | 3.8340376110962425e-17 |
| event→right-end 전파 work [J/m³ per V0] | -1.6276734072240087e-21 |
| 공통 부피 기준 평균 cQrad⁰ [J/(m³ s)] | 2.2444227347368295e-26 |

독립 70-digit quadrature와의 차이는 **순 관측량 자신의 척도**에서 각각 `1.9834943391822266e-14`, `2.025285279780588e-14`이다. 큰 incoming/outgoing 두 적분의 차이를 수치 순 교환으로 삼지 않았다. Nout/Uout은 저장 incoming 값에 새 correction을 한 번 더한 것이다.

기존 B3g 연산자에 native `R=exp(-h)I`를 넣어 `N1=exp(-3h)N0`, `U1=exp(-4h)U0`로 운반했다. 예전 ANISO geometry를 이 scalar FLRW source에 혼합하지 않았다.

광자 stress는 `T=diag(U,U/3,U/3,U/3)`이고 공간 대각 성분은 압력이다. 이번 등방 source의 공간 four-force는 0이다. 국소 rate는 `cQrad^0=E21,J G H j`이며, 표의 값은 공통 부피로 적분한 뒤 기존 proper duration `1708251102.5026681 s`로 나눈 시간평균이다. 이 값과 endpoint T를 서로 더하거나 같은 양으로 소비하면 안 된다. 이미 유한 kick으로 처리한 교환을 뒤의 RHS rate로 다시 더하지 않는 once-only 계약도 보존한다.

## 5. 새로 측정한 유한 QSS storage defect

기존 공통 수소 정규화 `nH_ref=250250485.05511948 m^-3`에서

\[
N_p(t)=n_{H,ref}x_{2p}(t),\qquad
\Delta N_p=-D+B_p
\]

이다. 원 source QSS row는 순간적으로 `b_p^QSS=d_p`이므로 표현된 같은 경로를 적분한 채널 complement는 `B_p^QSS=D`다. 그러나 algebraic endpoint population이 변하면

\[
S_p=\Delta N_p+D-B_p^{QSS}=\Delta N_p
\]

가 남는다.

| 항 | 값 [m⁻³ per V0] |
|---|---:|
| 초기 N2p | 4.941629582012266e-6 |
| 종료 N2p | 4.937707566289445e-6 |
| ΔN2p = upper storage defect | -3.922015722821008e-9 |
| ΔN2s | -1.3076617928069534e-9 |
| Lyα net downward D | 23.46391833488862 |
| 순간 QSS에서 추론한 complement D | 23.46391833488862 |
| 유한 재고를 맞추는 데 필요한 complement D+ΔN2p | 23.463918330966607 |

전체 2s+2p 내부에너지 끝점 변화는 `-8.545367403111164e-27 J/m³ per V0`다. Lyα 직접 원자 내부에너지 변화는 `-E21*D=-3.8340376110962425e-17 J/m³`이다. 그 외 채널과 algebraic refresh를 합친 필요한 에너지 complement를 계산할 수는 있지만, 그 값만으로 물리 reservoir가 실제 제공됐다는 증거가 생기지는 않는다.

Schur 감소계의 algebraic refresh는

\[
z_1^*-z_0^*=M_1^{-1}[(s_1-s_0)-(M_1-M_0)z_0^*]
\]

와 움직이는 Wien 기준의 차이로 설명된다. 이것은 알고리즘 갱신의 정확한 식이다. 물리적 원자·에너지 보충원으로 채택하려면 대응 bath/channel ledger 또는 명시된 동역학 확장의 근거가 필요하다. 이번에는 개별 non-Lyα rate operands를 새로 export·적분하지 않았고, 그 owner는 null로 남겼다. direct selected Lyα pair의 recoil·heat·ionization 0은 원 모델의 제한된 채널 규칙이며 전체 recombination network의 모든 recoil을 0으로 단정하지 않는다.

## 6. 최신 source 조사와 병렬 결과의 종합

가시 저장소 51개 목록을 끝까지 조회했다. 중앙 일곱 공급자의 branch/PR metadata는 pagination 끝까지 조사했고, 과학적으로 관련된 최신 report·contract·source를 실제 읽었다. 모든 branch의 모든 파일 내용을 읽었다는 뜻은 아니다. 직접 conversation 검색은 이 대화에서 unavailable였으며 미열람 대화를 조사했다고 기록하지 않았다.

초기 관찰 창의 branch 수는 BASS 287, REC 157, REI 282, HE 107, CR 187, WU 159, Vigilode 217로 총 1396개다. 우리 새 BASS branch는 그 뒤 생성됐다. BASS 초기 raw PR 202행에는 중복 1개가 있어 unique 201개였고, 이후 DV2-C PR202와 이번 PR203을 추가했다. 중앙은 unique PR 239개, 최대 번호 240이다. 움직이는 ref의 관찰 시점은 각 기록에 별도로 남겼다.

- **REC**: 실제 전체 tree 7581 entries, 관련 28 branch ancestry와 6개 legacy NPZ 등을 조사했다. 정수 redshift 8001행의 원 stdout은 실제 존재한다. 다만 선택 native knot의 절대 상태와 동일한 packet은 아니다. 전역 raw-history 부재라고 표현하지 않는다.
- **BASS DV2-C**: PR202, `932bcd8f14c7f04b709007478ec9519a68457172`, expanding Bianchi-II geometry 결과다. 이번 q=1 FLRW source로 geometry를 대체하지 않는다.
- **CR**: PHYS02, T=100 K, nH=140 m^-3, proper `[0,1e10] s`의 별도 source다. finite N/E와 once-only port 원리는 유용하지만 선택 REC atomic refill은 아니다. 작업 중 중앙에 `1a38f94fa50c763bb9df6ccc8ba569f287fe97d5`가 추가됐다. 이 직접 후속은 source science `022c163726b814885805bd9a7ab988fe963cda4a`와 documents `8482ed83b14517b709ba6e801f6714cc333e720f`의 CR proper return을 보존한다. 이번 중앙 patch는 그 후속에서 만든다.
- **HE**: 최신 public conditional H/He exchange와 더 최신 STATE04 backup의 HD–H+ scalar 2↔1 edge를 구분했다. 둘 다 caller 상태를 요구하며 선택 REC 구간의 H Lyα 물리 refill은 제공하지 않는다.
- **WU**: 최신 R5 population projection은 scoped 11/26, 중앙 증가 0이다. source-state projection 수학은 참고할 수 있지만 molecular 미결속 입력을 이번 atomic inverse의 선행조건으로 붙이지 않는다. 최신 AGENTS 변경도 기록했다.
- **Vigilode**: PR보다 최신 integration/checkpoint branch를 발견하고 actual decision을 읽었다. algebraic inverse에는 새 integrator qualification이 필요하지 않다.

백업 조사에서는 지정 Dropbox 폴더 165/163/145개 entry의 terminal pagination, Drive BASS 폴더 113개 entry, 관련 107개 backup record, 제공된 프로젝트 파일 20개의 목록·archive member를 확인했다. Drive 계정 전체나 모든 archive의 모든 byte를 전수 검토했다고 주장하지 않는다. HE STATE04·CR R03/R05·REC synthesis의 실제 report/manifest를 읽어 source scope를 대조했다. 최신 다른 branch의 29/88·32/88 수치를 중앙 27/88에 합산하지 않았다.

## 7. 실행·검토·오차 의미

새 controls 1회에서 20 checks, 새 결과 실행 1회에서 82 acceptance checks, 저장 결과만 읽는 plot 1회를 수행했다. 전부 exit 0이다. 새 native solve, old campaign replay, 새 B3i RHS는 모두 0회다. 독립 reviewer는 코드를 구현하지 않았고, 한 번의 정적 검토에서 실제 interval propagation 결함을 지적했다. lower-tier 구현자가 사전 실행 수정 한 번을 적용하고 예정된 세 실행으로 검증했다.

실제 child CPU는 `5.377854 s`, wall은 `5.46034009399591 s`, wrapper CPU는 `0.029728 s`, peak RSS는 `66076 KiB`다. 새 30 CPU s/180 wall s/512 MiB 한도 안에서 종료했다. 이 새 allocation은 옛 미상 remaining budget을 복원하거나 reset한 것이 아니다. 네트워크·모델·준비 I/O 등의 미측정 비용은 0으로 만들지 않는다.

SciSpace 실제 검색, Exa primary 2편 본문 조회, Wolfram evaluator 3회 결과를 보존했다. 별도 WolframContext `-32603` 실패와 symbolic removable-singularity warning도 성공 기록과 구분했다. 논문은 QSS 근사와 effective-level 원전을 뒷받침하며 이번 저장 데이터의 새로운 수치 결과를 대신하지 않는다.

**오차 구분을 유지한다.** ANISO continuum–finite14 joint 차이는 `3.447529542803539e-5`; 기존 복원 수치 잔차는 약 `1e-11`; continuum 계산 수치 예산은 `2e-8`이다. 이번 inverse 및 net quadrature 수치 진단도 별도로 보고한다. 어느 값도 물리 `eS/en/eE/geometry/temporal/total` 반경이 아니며 이 반경들은 모두 null이다.

## 8. 다음 선택 작업

복원한 두 끝점의 x1s/x2s/x2p·native opacity와 기존 finite tube/common volume을 다시 요구하거나 재계산할 필요가 없다. 다음은 **선택된 native effective-H의 finite QSS storage와 대응 non-Lyα 에너지 owner**를 구성하는 작업이다.

필요한 새로운 증거는 선택 구간의 실제 channel/Schur source operands 및 그 물리적 energy/stock counterpart, 또는 명시적으로 선택하고 검증한 두 real-state dynamic completion이다. 기존 313차원 solve의 311개 virtual radiation unknown을 원자 준위로 취급하지 않는다. endpoint refresh를 무한 reservoir나 임의 물리 refill로 바꾸지 않는다. 선택하지 않은 CR·HE·분자·geometry 미래 공급자 전체를 선행조건으로 만들지 않는다.

해당 owner가 결속되면 B3b 유한 재고 교환으로 하나의 transaction을 만들고, 이미 확보한 B3g 운반 후 sector별 T와 four-force를 구분하여 B3i에 정확히 한 번 소비한다. 현재 원자 transaction이 미채택이라는 이유로 이번 완료된 inverse와 finite photon 결과를 다시 실행하지 않는다.

단계별 Git/백업 receipt, 정확한 최종 source 및 전달 SHA, 다음 대화용 복사문은 `STAGE_LEDGER.json`, `delivery/`, `HANDOFF_KO.md`에 저장한다. 단계들이 같은 일관된 checkpoint를 공유하면 그 사실을 명시하고, provider의 실제 ACK와 local byte hash를 서로 구분한다.

## 실제 S1 게시와 D1 전달 결속

Science S1은 `0bdbd2ad1357c4b3141d3488a94534d082d1a0cf`, tree `ea23c058c9bc40de475ffdfb0b51484c5bec8ea9`, parent S0는 `fd3524e914d6bec70f30e2a5643134e956cbba0a`다. [PR203](https://github.com/cosmosapjw-quantum/bass/pull/203)에서 expected-SHA/non-force 게시와 실제 ref readback을 확인했다. 정확한 과학 source81files/2,401,381bytes는 D1 metadata 갱신 전에 별도 scienceS1 snapshot으로 보존했다. 최종 전달 ZIP에서는 scienceS1과 deliveryD1 및 central_context의 identity를 구분한다.

후속 receipt는 `delivery/S1_PUBLICATION_RECEIPT.json`과 `delivery/SCIENCE_S1_SNAPSHOT_RECEIPT.json`을 읽는다. S1단계의 백업은 최종 하나의 source ZIP을 공유하며, 실제 Drive/Dropbox ACK 전에는 pending이다. R10/C10도 최종 D1 게시와 ACK 전까지 pending이다. ZIP을 자신의 미래 ACK 때문에 반복 재생성하지 않는다.

게시 준비에서142개 file chunk를 과도하게 병렬로 읽던 첫 code-mode host의 stdout이 닫혔다. 실패 시 Gitref 변경이나 과학 실행은 없었고6개 단위 읽기로 재개하여 게시했다. 이는 publication transport 진단이며 새 과학 비용0이다. 원 실행 원장과 허용값은 바뀌지 않는다.

Temporal 물리 반경의 null은 남지만 이미 고정한 represented PL의 다음 transaction에 모든 physical calibration을 추가 gate로 요구하지 않는다. 직접 열린 owner는 finite QSS storage/non-Lyalpha stock 및 energy counterpart다. 다음 행동의 과학 권한은 `ADMISSION.json` 원문을 따른다.

## 실제 중앙 반영 M과 최종 전달 대기

중앙 commit은 `152b82cac23fedcb75a9effe0c159bae3d800c01`, tree는 `847ed1e27812152df705a28b2651f61bb5cf8aaf`, expected parent는 `1a38f94fa50c763bb9df6ccc8ba569f287fe97d5`다. Force=false 게시와11:56:54UTC의 실제 HEAD readback MATCH를 root가 확인했다. 실제 도구 응답 및5file 기계 비교는 `delivery/CENTRAL_PUBLICATION_RECEIPT.json`에 보존한다. 원 contract, 다른87nodes,17edges와 새 CR proper return은 그대로다.

최종 source ZIP은 exact scienceS1, deliveryD1 metadata, centralM의5개 patch file, unchanged CR proper context와 이전 F3 delivery ZIP의 서로 다른 identity를 명시하여 함께 복구한다. 이전 F3 nested ZIP은 central55202663까지이므로, `CR_PROPER_INJECTION_20261027.json`의 실제 unchanged bytes도 별도 central_context에 포함한다. 이 파일을 원격에 다시 쓰는 작업은 없다.

S1 source 게시18/20단계, 실제 S0 dual-backup 확인9/20단계 상태에서 D1 및 최종 공유 ZIP ACK를 기다린다. R10/C10과 S1단계의 최종 backup은 ACK 전에 완료로 채우지 않는다. 원 DAG는27/88, 증가0이며 과학 추가 실행은0이다.

## 최종 source ZIP과 실제 저장 ACK — 2026-10-27 12:03:35 UTC

선택 R1–R10/C1–C10은 **실제 작업20/20, source·백업 coverage20/20**으로 닫았다. 원 중앙 DAG는 **27/88, 증가0**이다. S0의9개 단계는 고유 S0 archive의 실제 ACK를 유지하며, S1의9개 단계와 R10/C10은 하나의 최종 source ZIP과 post-archive receipt를 공유한다. 단계별20개 새 commit·20개 archive를 생성했다는 뜻이 아니다.

최종 ZIP `BASS_B3H_HISTORY_INVERSE_S1_DELIVERY_20261027.zip`은 **3,979,095bytes,103members**, local SHA256 `1174383fa9cbbbf8b45f0f5ccbab45f6bfad1705e16e0b495cf690e9f617876b`다. Source S1 `0bdbd2ad1357c4b3141d3488a94534d082d1a0cf`, delivery D1 `5ae9dcbc6fc0765aa1762fb8bb6f031837ae6ff4`, 중앙 M `152b82cac23fedcb75a9effe0c159bae3d800c01`을 namespace별로 구분하여 복구한다. CRC, 전체 member byte readback, 모든 member manifest 길이·SHA readback은 PASS다.

- Drive: upload success와 별도 metadata3979095bytes 확인, ID `1HJkq06HinJAuTV6urtx28JDkZmQDB5-x`. [실제 최종 source ZIP](https://drive.google.com/file/d/1HJkq06HinJAuTV6urtx28JDkZmQDB5-x/view?usp=drivesdk).
- Dropbox: completed와 별도 metadata3979095bytes 확인, ID `id:BSpOijBcT10AAAAAAEDHeg`, path `/BASS_BACKUPS/BASS_B3H_HISTORY_INVERSE_S1_DELIVERY_20261027.zip`, rev `65ed139d0c8f50af03d47`.
- 저장 파일: succeeded, `libfile_a645147c0ed4819181cc31e2ba44ee29`. [최종 저장 파일](https://chatgpt.com/library?file_id=libfile_a645147c0ed4819181cc31e2ba44ee29&account_id=personal).

실제 selected provider fields는 `delivery/FINAL_PROVIDER_ACKS.json`, 전체 결속과 단계 closure는 `delivery/FINAL_RECEIPTS.json`, `STAGE_LEDGER.json`에 있다. Local SHA와 원격 provider upload·metadata 확인은 다르다. 원격 사본 전체를 다시 내려받아 SHA를 재측정했다고 주장하지 않는다.

ZIP은 자기 자신의 ACK 전에 동결했고 **ACK 뒤 재생성하지 않았다**. ZIP 내부의 pending/null은 S1/D1 게시 당시의 역사적 snapshot이다. 위의 실제 finalACK는 ZIP 밖 후속 receipt로 결속했다. 이 최종 metadata를 포함하는 F commit의 자기 SHA를 이 문서에서 추정하지 않으며, root의 실제 최종 게시·HEAD readback·PR에서 확인한다.

과학 추가 실행0, 기존 비용·미상 잔여 한도 불변, 새 allocation은 closed다. 채택 범위·fullphysicaltransaction=false·새B3i0·physicalradii=null도 그대로다. 완료 evidence를 자동 replay하지 말고 `ADMISSION.json`의 다음 선택 owner 결속을 이어간다.
