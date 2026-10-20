# S12 독립 물리 검토 — 저장된 실제 C6/C7 결과

**최종 범위 내 판정은 PASS_SCOPED, 독립 점검 585/585다.** 검토자는 Rust core/history/birth, root의 Python reference와 assessment 코드를 작성하지 않았다. 새 직접식으로 실제 stdout을 읽어 검토했으며 solver, compiler, projector, 기존 캠페인 호출은 모두 0회다. 검토자가 작성한 native followup wrapper와 native support observer는 이 독립 승인에 포함하지 않는다.

## 원 실행과 검토를 구분한다

원 Rust/core source는 `f4cd0d53760783e6a58c3b0a98c64311ca489d28`, 수정 Python reference/validation source는 `4e3615dd75ff1a1efc2792edb3ba5b702a8a9b06`이다. Rust binary를 새 reference source로 잘못 표시하지 않았다. 고정 REI owner `0e25846433170d0f420c4cda44a0bedbf02cd177`, VigilODE `a21d573980f66fe02891bd216153443b5352f921`를 유지한다.

원 core 검증 269/269, ensemble history 검증 72/72, primary 한 receipt의 내부 검사 470/470, 이번 독립 readback 585/585는 서로 다른 집합이다. 이를 합쳐 독립 실험 수로 세지 않는다. History의16개 process records는 원래 완료된 Rust5개 재사용 + 새9history + Python1 + final-checkpoint restore1이다. 재사용5개를 다시 적분하지 않았다. 첫 Python reference의 strict derivative parity 실패 기록도 유지된다.

[검토 원본 결과](run02/REVIEW.json)는 224개 읽은 입력의 bytes/SHA256, 개별 판정과 수치를 담는다. Primary 입력 SHA256은 `e169031742099823107d3dd50a23a7666035845d0b4b42625048c93779e128a1`, 원 stdout은 `e2c80e311ac1f518dd8d8029448b8f1f795ada4684250722184468f2aa1eaf09`다. 원 자료를 수정하지 않았다.

## 직접식과 확인한 물리

검토 코드는 Q=A+(B−A)μ², A=exp(2d), B=exp(−4d), T=3Bμ²−Q, R=sqrt(Q)에서 photon energy와 pressure numerator를 직접 구성한다. 고정 birth memory와 μθ, αθ를 넣어 Qθ와 Tθ를 직접 미분하며 Rust의 ME/MP/L 분해를 호출하지 않는다. 이 직접 RHS에 complex step을 적용해 24점 모두의6-state Jacobian36성분, JVP6성분, partial_t6성분을 확인했다. 생성된 새 weight나 ODE trajectory는 없다.

| 독립 core 비교 | 최대 scaled 차이 | 기존 gate |
|---|---:|---:|
| RHS | 5.775907956921328e−17 | 2e−11 |
| 전체6×6 Jacobian | 1.9022612648095884e−16 | 2e−11 |
| JVP | 1.466316543802134e−16 | 2e−11 |
| partial_t | 1.1945399381045238e−16 | 2e−11 |
| 직접 energy/pressure와 parameter differential | 6.8214314042416775e−18 | 2e−11 |
| baseline/fused | 0 | 2e−13 |

14개 저장 history에서는 기존 physical stock의 완전한 입력 객체와 physical/memory digest, 양의 physical weights와 반사대칭, 새 birth의 고정좌표와 저장된 parameter memory, 원 exact norm/P2/P4 gate를 검토했다. 실제 binary64 입력을 Fraction으로 바꾼 새 birth 잔차의 전체 최대는 9.074886033988066e−16으로 원 3e−15 gate 안이다. 이 값은 source-frame GL 대조군을 포함한 전체검토의 최대이며 primary P24 한 case의5.4508345007816687e−17과 혼동하지 않는다. 기존 stock에 새 P24 moment gate를 소급 적용하지 않는다.

각 저장 관측점에서 C와 Cθ를 다시 계산하고, 각 cohort의 energy와 parameter energy를 흐름 방향으로 직접 complex-step 미분했다. E′와 Eθ′를 conservation 식으로 정의한 뒤 같은 식에 넣는 검사는 아니다. 총합 최대는 C relative1.1520676650209054e−13, Cθ relative1.4434151163064282e−15, cohort energy law1.4153438806537209e−15, tangent energy law1.8106271579076636e−16, 직접 Cθ propagation2.6790916670079437e−17이다. 모두 원1e−11 gate 안이다. 이들은 저장점의 순간 관계이며 독립적인 연속시간 오차 한계나 전체 spectral history 수렴 증명은 아니다.

고정 event에서 donor와 photon의 총 energy 연속성, Eθ 연속성 및 full controls의 Pθ 연속성을 따로 계산했다. 최대 relative 값은 각각2.4057894941535117e−16,2.085095887803736e−18,4.7742297158330715e−18이다. 기존 birth의 weights/source frame을 바꾸거나 donor amplitude를 parameter-dependent로 만들지 않았다.

## 교차 검증과 실패 대조군

요청한17개 출력 시각에서 Python/Rust scaled 차이는3.483131098619846e−15, MF6/clock7 차이는1.623443460779953e−15, baseline/fused는0이다. Source-frame b0 gauge의 |Sh|,|Sb−1|,|Sy| 최대는0으로 기존 absolute1e−11 gate를 유지한다.

세 고정 paired-primal step1e−4,5e−5,2.5e−5의 저장 결과에서 centered derivative와 fine Richardson을 다시 만들었다. Full tangent와의 최대 절대 차이는7.923659645081571e−11로 원 absolute1e−8 gate 안이다. 첫 S8 tangent campaign을 다시 실행한 결과가 아니다.

| 의도적으로 뺀 항 | fine Richardson과 최대 절대 차이 | 필요한 하한 |
|---|---:|---:|
| birth memory | 0.0015948771401851358 | 7.923659645081571e−10 |
| μ의 birth 미분 | 0.0011966517163757295 | 7.923659645081571e−10 |
| α의 birth 미분 | 0.001196318028750809 | 7.923659645081571e−10 |

세 control 모두 event Pθ 연속성 실패를 드러내며, `full_scientific_pass=false`, `numerical_gates_pass=false`로 남는다. 검증은 이 실패를 구별했다는 의미에서 통과한다. 누락된 물리식이 통과했다는 뜻으로 표시하지 않는다.

## 성능 범위와 최종 restore

원 core benchmark의 모든18개 timing stdout을 해당 mode의 diagnostic 값과 다시 비교했다. 24점·48ray·callback48,000평가, warmup2쌍 제외 paired7쌍의 median1.372535191944467배를 재계산했다. 이는 그 고정 full augmented callback workload에만 해당한다.

별도 C7 sandbox4case/2worker benchmark는32개 stdout 전체 bytes와 각 input/binary hash를 검토했다. 1warmup+3measured pairs의 median1.2180376690502004배가 원 기록과 일치한다. NCP64 실행이나 whole-history 가속률로 쓰지 않는다. 첫 manifest 인자 경로 오류 시도는 core child0의 실패로 보존되어야 한다.

Final checkpoint는 동일 source/input/binary에서 마지막 경계의 observation/event/cohort identity가 일치했다. 중간 event를 끊었다가 복구한 시험을 수행했다는 주장은 하지 않는다.

## 검토자 오류도 보존한다

첫 [run01](run01/REVIEW.json)은501개 검사까지 성공했지만 Python의 event 포함21행과 요청17행을 직접 비교한 검토자 코드의 `ARRAY_SHAPE` 오류로 FAIL 종료했다. 501을 완료 PASS로 세지 않는다. [수정 기록](REVISION_R2.json)은 Python도 같은17개 x로 선택하는 한 줄 변경과 전후 source SHA를 남긴다. 원 source는 run01 안에 보존되어 있고, [최종 실행 receipt](run02.PROCESS.json)에 실제 명령·exit0·빈stderr·source/result hash가 있다. 물리 원자료, gate, solver는 바꾸지 않았다.

실제 MD14 정규화/native Einstein·shear shared-Q, evolving reactive full finite-bin spectral history, 고차 finite-d/angular 오차의 일반적 해소, full EoR/production/merge는 이 검토로 닫히지 않는다. Native 한 case의 compile 여부와 뒤쪽 birth support 가능성은 별도 결과를 따른다.
