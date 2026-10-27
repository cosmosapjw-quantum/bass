# B3h native endpoint-channel 유한 transaction 결과

## 채택 결과와 범위

2026-10-28 KST, 현재 진행 중이던 `BASS_B3H_ENDPOINT_CHANNEL_INTERPOLATION_20261027`을 **PASS_SCOPED_CONDITIONAL_ENDPOINT_TRANSACTION**으로 채택했다. 실제 저장 native knots 5126·5127의 양의 gross channel을 proper time으로 보간하여 유한 atomic/gas/radiation 재고를 갱신하고, B3g 운반 뒤 구분된 다섯 sector의 T와 four-force를 B3i에 **새로 1회** 소비했다. 생산 검사 50/50과 독립 C9/R9 검토가 통과했다. 기존 원 DAG는 **28/88**, 이번 refinement의 원 노드 완료 증분은 **0**이다.

이 보고서는 선택한 유한 모델의 결과다. 저장된 QSS나 frozen-left 결과는 변경하지 않았다. 물리 eS/en/eE/geometry/temporal/total 및 global 반경은 null이고 L4는 false다. 새 노드는 자동으로 시작하지 않는다. 게시·백업의 실제 상태는 `delivery/`의 후속 ACK와 최종 전달 기록에 결속한다.

## 실제 연결한 모델

공통 기준 부피는 V0=1 m³, geometry는 scalar FLRW q=1, signature는 (−,+,+,+), 시간좌표는 x0=ct다. 입력 binary64 수를 정확히 올려 MP70으로 계산하고 source의 k_B T[eV], eV→J 및 c convention을 유지했다.

새 proper clock은 t(u)=∫₀ᵘdv/H(v), T=t(h), θ=t/T다. 저장된 왼쪽 1,414개 채널은 기존 결과에서 복원하고, 오른쪽 1,414개만 실제 source operands로 새로 구성했다. 오른쪽 normalization에는 오른쪽 proper nH를 사용한다. 각 채널의 두 endpoint tag를 유지하여

\[
j_c=(1-\theta)(a_{c0}+\ell_{c0}p)+\theta(a_{c1}+\ell_{c1}p),
\]

\[
Q_{c,s}=(1-\theta)e_{c0,s}(a_{c0}+\ell_{c0}p)
+\theta e_{c1,s}(a_{c1}+\ell_{c1}p)
\]

로 결합했다. 따라서 총 2,828개 tag가 자신의 에너지 moment와 소유자를 보존한다. 이 정의는 endpoint 에너지와 rate를 따로 보간한 뒤 곱하는 정의와 다르다. 같은 stoichiometry에서 b와 M을 조립하여 ṗ=b−Mp를 풀었다. Lyα의 실제 incoming strict-past trace, g(u), H(u)와 finite crossing measure는 공통 clock 안에서 연결된다. 311개 virtual 변수는 제거된 radiation proxy이며 원자 재고가 아니다.

초기 p만 고정하고 마지막 p는 동역학으로 계산했다. 오른쪽 native QSS 값을 boundary condition으로 강제하지 않았다. 유한한 초기 ground/2s/2p/ion/electron 재고, gas 및 ambient radiation 에너지 준비는 기존 채택 결과에서 읽었다. 완료된 spectral-owner 계산은 다시 실행하지 않았다. source의 prescribed thermodynamic driver와 실제 유한 재고는 구분한다.

## 관측값과 모델 차이

표의 수는 V0=1 m³에 정규화한 photon/event 기대수이며, 정수 표본의 개수가 아니다. 모든 행은 같은 저장 incoming count 9117.0927688386712084…를 사용한다.

| 모델 | outgoing Lyα 수 / V0 | 순 outgoing−incoming / V0 |
|---|---:|---:|
| 저장된 QSS 기준 | 9140.5566871735603 | 23.4639183348891 |
| 이전 frozen-left finite 모델 | 9144.1670256675585 | 27.0742568288872 |
| 이번 두-endpoint finite 모델 | **9140.5578708052686** | **23.4651019665974** |

이번 outgoing은 frozen-left보다 **3.6091548622898313/V0 감소**하고 QSS보다 **0.00118363170832454/V0 증가**한다. 해당 pulled-back outgoing 에너지는 **1.4936435468613864423×10⁻¹⁴ J/V0**다. frozen-left 대비 에너지 차이는 −5.8977441900746791×10⁻¹⁸ J/V0, QSS 대비 차이는 +1.9341531528249311×10⁻²¹ J/V0다.

양 끝의 실제 채널을 포함하자 이 선택 모델의 적분 결과가 QSS 기준에 가까워졌다. 이것만으로 원래 연속 native history의 정확도를 입증하지는 않는다. interior의 모든 rate table을 다시 풀지 않았고, 물리 시간보간 오차도 아직 null이다. 이전 결과와 이번 결과의 차이는 **모델 차이**로 보존한다.

최종 동적 분율은 p₂s=6.5631873161091926×10⁻¹⁵, p₂p=1.9731060921618626×10⁻¹⁴다. 유한 저장 변화는 ΔN₂s=−1.3076617935188293×10⁻⁹ nuclei/V0, ΔN₂p=−3.9220157250927287×10⁻⁹ nuclei/V0다. 연속체/전자 재고는 약 31,940.9118243/V0 감소하며 동일한 사건 수로 ground 재고가 갱신된다. 잔차를 refill이나 heat로 정의하지 않았다.

## 수치 상계와 독립 검토

새 proper duration은 **1708251102.502668856876739386… s**이며 조건부 수치 상계는 1.70825110255×10⁻⁴⁶ s다. 새 clock을 사용해 θ와 1/T의 오차를 jet·inverse·endpoint·adjoint·quadrature에 직접 전달했다. 이전 저장 duration의 미상 quadrature 잔여를 0으로 놓지 않았다.

두 실제 incoming 구간을 분리하고 q=2 slow expansion 및 frozen initial layer를 사용했다. 누적 적분은 ordered variable-M adjoint m=3와 positive Gauss24로 계산했다. 외부/내부 복소 disk 반경 0.001/0.0005에서 H², g 및 M inverse의 해석성을 확인했다. Neumann factor는 약 0.3027064와 0.3028907로 1보다 작고, contraction γ=160.889049184 s⁻¹이다. 추가 domain refinement는 0회다. 초기층 오차와 endpoint 오차를 다음 구간으로 전달했다.

| 검증량 | 실제 값 또는 상계 | 동결 기준 |
|---|---:|---:|
| 최종 분율 one-norm 오차 상계 | 1.45049981497×10⁻⁴⁸ | ≤10⁻³⁴ |
| 2s 저장 balance 오차 상계 | 5.10737835871×10⁻²⁶ nuclei/V0 | ≤10⁻¹⁶ |
| 2p 저장 balance 오차 상계 | 2.84474710858×10⁻²⁵ nuclei/V0 | ≤10⁻¹⁶ |
| 2s 상계 / 비영 저장 변화 | 3.90573341213×10⁻¹⁷ | ≤10⁻⁸ |
| 2p 상계 / 비영 저장 변화 | 7.25327818136×10⁻¹⁷ | ≤10⁻⁸ |
| outgoing count 새 수치 상계 | 6.61967046450×10⁻³¹ photons/V0 | 조건부 moment 상계 |
| outgoing energy 새 수치 상계 | 1.08279173228×10⁻⁴⁸ J/V0 | 조건부 owner 상계 |
| 오른쪽 source 최대 상대 parity 차이 | 1.45365315225×10⁻¹⁵ | ≤5×10⁻¹¹ |
| 독립 saved RHS 대수식 최대 상대차 | 1.23004027315×10⁻¹⁶ | ≤5×10⁻¹² |

2s/2p 실제 balance 잔차는 각각 약 9.4230×10⁻⁶⁴, 1.9431×10⁻⁶⁰ nuclei/V0다. 상계와 잔차는 서로 다른 값이다. 새 constant-M·affine-source control은 비영 초기층과 독립 closed convolution/moment를 포함한다. m2/m3 차이와 Gauss16/24 차이는 진단으로 보존하며, 그것만을 오차 증명으로 사용하지 않았다.

독립 검토자는 production code를 작성하지 않았고 새 trajectory·integration·RHS를 실행하지 않았다. 저장된 2,828 tag×3가중치, 총 8,484 count를 Decimal100으로 다시 조립하고 stock·energy·four-force·RHS의 대수적 연결을 확인했다. 그 결과와 실제 126개 실행 진입 파일의 확인은 `reviews/C9_INDEPENDENT_REVIEW.md` 및 관련 JSON에 있다.

모든 새 상계의 정확한 자격은 **해석적 절단오차 + 선언된 상대 MP 산술 허용량 10⁻⁵⁵, 채택된 저장 입력값에 조건부**다. validated interval arithmetic 증명이 아니다. 기존 incoming moment의 quadrature 잔여와 물리 입력 오차는 null을 유지한다.

## 에너지 소유권, B3g 운반, B3i 소비

다음 사건 에너지는 같은 common V0에서의 적분값이다. 부호는 해당 sector가 받은 에너지다.

| Sector | 사건 에너지 J/V0 | 평균 cQ⁰ J/(m³ s), 오른쪽 부피 기준 |
|---|---:|---:|
| rest dust | 0 | 0 |
| atomic internal | −6.9589205303342452×10⁻¹⁴ | −4.072673103376497×10⁻²³ |
| gas thermal | −8.6875745202502562×10⁻¹⁶ | −5.084359122650129×10⁻²⁵ |
| ambient radiation | +7.0419620445185477×10⁻¹⁴ | +4.1212727302594065×10⁻²³ |
| outgoing Lyα | +3.8342310182000528×10⁻¹⁷ | +2.2439643435912607×10⁻²⁶ |

다섯 sector 사건 에너지 합의 잔차는 1.27745891100×10⁻⁸² J/V0이며 산술 상계 8.38697932762×10⁻⁶⁵ 안에 있다. B3g common-volume geometry-work 잔차는 −1.09478981552×10⁻⁷² J/V0, 전파된 상계는 2.31196356203×10⁻⁴² J/V0다. rest/internal, gas, radiation의 팽창 가중치를 각각 유지했다. 직접 Lyα recoil=0은 기존 native 근사의 범위이며 bound-free/diffusion의 gas 및 radiation 에너지 소유자는 별도로 포함했다.

각 sector의 T는 energy density와 pressure를 포함한다. isotropic spatial four-force가 0이어도 spatial stress가 0인 것은 아니다. T와 cQ/Q를 별도 저장하고 새 duration과 exp(3h)의 오른쪽 부피를 사용하여 평균 force를 정규화했다. binary64로 전달하는 cQ와 Q⁰에는 실제 표현 차이도 오차 항에 포함했다. 모든 transaction 검사가 끝난 뒤 `core.rhs`를 정확히 한 번 호출했다. 생산 대수식 비교의 표시 상대차는 0이고, 독립 Decimal100 saved-value 비교는 위 표의 1.23×10⁻¹⁶이다. 기대되는 0 성분은 정확히 0이다. 이는 전체 Friedmann closure를 채택하는 결과가 아니다.

## 실행과 재사용 기록

최초 child는 기존 mpmath 설치 경로가 빠진 환경 연결 오류로 import 단계에서 종료됐다. driver·과학 계산·RHS 이전이었다. stderr와 CPU 0.082589 s / wall 0.117552552 s를 보존했다. root가 기존 `runtime_deps` 경로 연결만 수정하도록 한 번 승인했고, 같은 누적 예산 안에서 성공했다. QSS 비교값의 키 수정은 최초 동결 전에 끝난 보고 binding 수정이며 실패 후 모델 변경이 아니다.

성공 child는 CPU 22.551978 s / wall 22.588370317 s, 실패 포함 누적은 **CPU 22.634567 s / wall 22.705922869 s**, peak RSS는 **167,192 KiB**다. 새 한도는 CPU120 s / wall300 s / 768 MiB / 1 thread였다. 산술 잔여 97.365433 CPU s / 277.294077131 wall s는 새 실행 권한이 아니다. 예산을 닫았고 추가 계산은 승인하지 않았다. 준비·metadata 비용의 미계량 부분을 0으로 보고하지 않는다.

기존 512개 실제 cohort의 midpoint 재구성·최종 운반, 최초 두 B3i RHS, 이후 완료된 native tube·inverse·frozen-left 결과와 tests/consume/plot은 재실행하지 않았다. A2=`af14fc72d99f6d0e396f60aedadcdb5d05213280`, F2=`009a1238c09adf889c7421132f530b960cdafb07`을 보존한다. ANISO continuum–finite14 joint 차이 **3.447529542803539×10⁻⁵**, 복원 수치 잔차 **약10⁻¹¹**, continuum 수치 예산 **2×10⁻⁸**은 서로 구별한다.

이미 수행한 source survey는 관련 7개 repo의 1,406개 branch와 1,037개 PR 목록을 다뤘으며, 선택된 변경 내용은 별도 읽기 기록으로 한정한다. 모든 branch의 모든 파일을 읽었다는 뜻은 아니다. 접근할 수 없었던 다른 대화 본문은 읽은 것으로 주장하지 않는다. 재개 시점의 새로운 BASS 병렬 작업과 최신 central HEAD도 확인했다. 전체 survey를 다시 실행하지 않았다.

## 원자료와 다음 동작

과학 원자료는 `results/ENDPOINT_RESULT.json`(17,398,524 bytes, SHA256 `acf56f5aefe556d1d86e4f93f3063c5d38078cb8c7f9a627b141c4ef9582f3bd`)이다. `ADMISSION.json`, `results/ENDPOINT_SUMMARY.json`, 닫힌 `BUDGET_LEDGER.json`, 독립 검토, 원 stdout/stderr와 failed/success ledger를 함께 보존한다. 전체 유도와 clock/adjoint 증명은 `theory/`에 있다.

Git 게시 경로의 실제 단일 요청 16 MiB 제한 때문에 원자료의 저장 표현만 조정했다. GitHub의 `results/ENDPOINT_RESULT.json.gz`와 `ENDPOINT_PARTIAL.json.gz`는 검토된 원자료를 무손실 압축한 것이며, source ZIP은 원본 JSON을 그대로 포함한다. 압축 해제 후 위 원자료 SHA256과 정확히 일치한다. 대응표는 `delivery/GITHUB_RAW_REPRESENTATION.json`이다. 수치값·모델·수용 판정에는 변경이 없다.

이 결과의 S1 게시, 실제 D source 게시·Drive/Dropbox ACK와 영구 파일 저장, 최신 central DAG의 증가0 followup 반영과 최종 handoff를 완료했다. 선택된 R/C 단계는 **work20/20·published20/20·backed20/20**이며 실제 source/ACK와 후속 F receipt의 구분은 `delivery/FINAL_ROOT_ACK.json`에 있다. 원 DAG **28/88, 증가0**과 모든 과학 판정을 유지하고 `AUTO_NEXT_NODE=false`로 종료한다.
