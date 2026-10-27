# B3g 실제 최종 운반 복원 → 선택 유한 흡수·geometry 후속 인계

작성일: 2026-10-27 (Asia/Seoul). 원자료·실행 ledger의 UTC는 그대로 보존한다.

## 여기까지 실제 완료한 것

고정 출발 인계서는 BASS d6af237b66e78ca6ed4572068f6bc1a805bbb2d9의
research/program_expansion_20261025/HANDOFF_KO.md다. 직전 완료 source는
0e07ea8ca2f11901e0818c9ab9afdeff76352618, 전달 HEAD는
d7dcd731de1a0c59e5e65db5038c333f5abae0bd다. 그 결과를 재실행하지 않고 재사용했다.

이번 단위는 실제 저장 B3c ISO 256개와 ANISO 256개, 총 512개 출생에 대해
누락된 midpoint alpha/beta를 classical RK4 좌표 항등식과 유한 stage
나머지로 재구성하고, 최종 R 및 detR를 계산했다. 원래 midpoint의
binary64 바이트를 복구한 것은 아니다. exact-arithmetic 유한 stage
나머지와 경험적 산술 여유, 아직 없는 물리 입력 반경을 구분했다.

실행은 tests → consume → plot 각 한 번으로 완료했다. 10개 테스트 PASS,
512개 운반 map, 2회 algebraic core RHS, 2개 PNG가 실제 산출되었다.
독립 R6/C9/R9 검토와 root 과학 admission이 완료되었다. 과학 판정은
`PASS_SCOPED_RECONSTRUCTED_FINAL_TRANSPORT_AND_GEOMETRY_CONSUMER`다.
새 IVP/native solve/흡수 transaction/과거 campaign replay는 0이다.

| 결과 | ISO | ANISO |
|---|---:|---:|
| 복원 finite14 대 저장 응력 joint 상대 차이 | 1.0446478827350775e-11 | 1.0653175742913758e-11 |
| 같은 비교의 수치 상계 | 2.0328860752328997e-11 | 2.1426296174718444e-11 |
| continuum 혼합의 operational 수치 예산 | 3.020869003168952e-11 | 1.846001725178548e-9 |
| 기존 2e-8 수치 기준을 통과한 cohort | 256/256 | 256/256 |

모든 비교는 광자 에너지 scale을 사용한다. 큰 원자 정지 에너지로 오차를
희석하지 않는다. 물리 eS/en/eE와 geometry/temporal 반경은 여전히 null이다.

## 다음 작업이 반드시 보존할 해석

ANISO의 continuum−finite14 joint 상대 차이는 **3.447529542803539e-5**다.
약 1e-11의 finite14 복원 일치는 continuum과 finite14의 일치가 아니다.
2e-8 통과는 continuum 적분기의 numerical budget이다. 고차 각도 결과는
finite14로 진화했던 geometry를 고정한 후처리이며, 새 continuum feedback
궤적이 아니다. 다음 geometry 연구는 각도 모델과 그 모델 오차를 명시한다.

lower-rest R, excitation X, radiation의 T를 각각 보존한다. T [J/m3]와
x0=ct에서의 cQ [J/(m3 s)]를 구분한다. 이번 저장 최종 상태에는 source
kick이 이미 반영되었으므로 cQ=U=J=0이다. birth의 ledger.down_m3는 이미
proper-time 적분되었으므로 dt를 다시 곱하지 않는다. signed pi를 유지하고
excitation 교환을 임의 열 가열로 바꾸지 않는다.

## 지금 남은 선택 입력과 실행 가능한 다음 방향

B3h는 native REC effective-H Lyalpha 채널을 유지한다. 실제 HISTORY01의
f_out=(1-A)f_in+A*f_s, A=-expm1(-tau/q)를 사용하면 양의 유한 crossing
measure dmu에 대해 D_up=integral(A*f_in dmu)<=N_in=integral(f_in dmu),
D_down=integral(A*f_s dmu), N_out=N_in-D_up+D_down>=0가 성립한다.
이 경로에 실제 finite time tube, cell/history에서 incoming face로의
대응, 공통 부피, atomic stock/internal-energy/recoil owner를 결속한다.
임의 dt나 무한 bath를 유한 photon stock으로 선언하지 않는다.

최신 REC PR138의 313개 query 결속에는 물리 반경이 없다. REI PR235의
moving electron reservoir와 PR236의 PW19 HeII open signed energy ledger는
선택 Lyalpha의 유한 incoming photon stock이 아니다. PR233–236의 성과는
source 관측으로 재사용하되, 중앙 canonical에 병합되었다고 쓰거나 그
예산을 BASS로 이전하지 않는다. 실제 source identity와 구체적인 남은
입력은 provenance/B3H_SELECTED_INPUT_INTAKE_KO.md에 기록했다.

다음 단위는 최신 AGENTS·HEAD·병렬 작업부터 다시 확인한다. 선택 채널의
위 실제 입력이 확보되면 기존 B3b 유한 교환과 B3g 운반을 이용해 한 번의
유한 transaction을 구성하고 B3i의 sector별 T/Q 입력으로 연결한다.
입력 확보 전에도 이번 유한 복원 정리와 저장 모델의 tensor consumer는
완료된 결과로 재사용한다. 선택하지 않은 미래 공급자 전체를 새
선행조건으로 요구하지 않는다. 전체 물리 완료율 null, L4=false,
B4/B5 NOT_RUN은 유지한다.

## 비용·실행 보존

이번 새 배정은 20 CPU초 / 60 wall초, child별 10 CPU초 / 20 wall초다.
실측 child CPU 7.177914초, child wall 7.245837689002656초, 별도 wrapper
CPU 0.130123초다. 새 측정 CPU 합은 7.308037초다. 실행 retry는 0이다.
직전 child CPU 3.7263초 / wall 3.739223223001318초를 보존했다.
두 단위의 알려진 child 합은 CPU 10.904214초 / wall 10.985060912003973초다.
오래된 남은 예산과 계측하지 않은 I/O·metadata 비용은 unknown/null이며
0으로 채우거나 예산을 초기화하지 않았다. frozen 실행 stage는 재실행하지 않는다.

구현은 gpt-6.1-sol을 요청한 별도 하위 coding agent에 위임했다. 실제
runtime model identity는 관측되지 않아 null이다. 독립 검토자는 구현과
분리했으며, 추가 과학 재실행 없이 실제 raw와 PNG를 확인했다.

## 직접 복구·게시·백업

직전 전체 소스 ZIP BASS_B3G_S2_FINAL_20261025.zip의 SHA256은
0e11ce05e10d95cd9c002b719f053659ce941bb1b54fcc1c9a64e4ac4d73899d다.
실제 복구·CRC 검증과 원래 B3c source archive의 identity는 provenance에
보존한다. 새 ZIP에는 이 단위와 소비한 sibling 의존성을 넣고, 이번에
소비하지 않은 35 MB REC NPZ는 원본 ZIP의 불변 locator로 결속한다.

실제 science commit, 중앙 DAG commit, source ZIP size/SHA256,
Drive/Dropbox upload ACK와 readback은 성공한 뒤 DELIVERY_RECEIPTS.json에
기록한다. 이 인계서의 초기 버전에 ACK가 없다는 이유로 게시 성공을
추정하지 않는다. source ZIP을 먼저 고정하고 이후 ACK는 최종 metadata
commit에 결속하여 자기 참조를 피한다. PR192와 중앙 PR222는 Draft 상태로
이어가며 expected-SHA와 force=false를 사용한다.

## 먼저 읽을 파일

1. ADMISSION.json, REPORT_KO.md, results/SUMMARY.json
2. theory/RK4_MIDPOINT_RECONSTRUCTION_LEMMA.md, FROZEN_CONTRACT.md
3. reviews/R9_RAW_FIGURE_REVIEW.md, results/EXECUTION_LEDGER.json
4. provenance/B3H_SELECTED_INPUT_INTAKE_KO.md, CENTRAL_RETURN.json, DAG.json
5. DELIVERY_RECEIPTS.json 및 그 실제 commit/backup locator

기존 G1B/B3 유한 결과를 다시 증명하거나 재실행하기 전에 완료 근거를
재사용한다. 이 인계는 중단 복구와 다음 과학 실행을 위한 것이며,
문서·검토만 계속 늘리는 새 연구 선행조건이 아니다.
