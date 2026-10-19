# BASS S7: 결합 전단·native cohort 실제 결과

2026-10-19. **새 S6 실행을 먼저 발견해 재사용한 뒤 S7 이론, 구현, 경량 실행과 수치 수리를 완료했다.** 원래 결합 캠페인 R1/R2의 FAIL을 보존하고, 한 이력을 수리한 R3만 별도로 PASS로 기록한다. Native는 exact moment와 보존 검사가 통과했지만 큰 b의 angular accuracy 목표는 실패했다.

| 작업 | 실제 결과 | 근거 |
|---|---|---|
| 새 실행 intake | Git a9704c6f와 양쪽 BASS_BACKUPS에서 S6 04a3a851 발견; Drive manifest86/86, 기존 결과 재사용 | [intake](delivery/s6_intake_20261019/INTAKE.json) |
| S7 이론 | 닫힌 donor·Einstein 전단식, 독립 h 진화, C′=−2C, 이산 angular coupled spectrum, tangent 기억항 계약 | [이론](S7_COUPLED_THEORY_KO.md) |
| 독립 검산 | Fraction28 + Decimal80자리5 PASS | [검산](evidence_s7/theory_review/INDEPENDENT_REVIEW.json) |
| 결합 R1 | 36입력 중28완주·8 support 실패, 별도 benchmark7이력 실제 실행 | [결합 결과](S7_COUPLED_RESULTS_KO.md) |
| Exact R2 | 원 trajectory 불변; native808/808 PASS; coupled640개 제약 birth 중1개의 참된 M4 초과 | [coupled R2](evidence_s7_coupled/revalidate_r2/RETURN_S7_COUPLED_REANALYSIS.json), [native R2](evidence_s7_native/revalidate_r2/RETURN_NATIVE_COHORTS_R2.json) |
| 표적 R3 수리 | 같은 한 history에서 기존 P24 내부 atol만1e−15; 최종 exact gate3/10^15 유지,64/64 PASS | [R3](evidence_s7_coupled/strict_margin_r3/RETURN_S7_STRICT_MARGIN_R3.json) |
| Native 실행 | 원 owner57파일 불변 컴파일;51입력 중42측정·9 support 실패; 큰 b 정확도 실패2개 유지 | [native 결과](S7_NATIVE_COHORTS_KO.md) |
| 게시·백업 | 사전등록→원격 readback→실행; 단계별 Git·백업·DAG와 최종 PR closeout | [진척](S7_PROGRESS_KO.md), [cloud](CLOUD_READBACK_KO.md), [DAG](DAG.json) |

## 핵심 결과

기존 S3에서 확인한

\[
M_2=0\Longrightarrow\mathcal A'(0)=-\frac85+\frac{36}{35}M_4
\]

를 재사용했다. 새 S7은 radiation-only 이산 stress-isotropic equilibrium 근처에서 \(q=s/H\), \(\mathcal A=\Delta P/U_\gamma\)에 대해

\[
q'=-q+\mathcal A,\quad\mathcal A'=-\kappa q,\quad
\kappa=\frac85-\frac{36}{35}M_4
\]

를 유도했다. 양의 weights와 M2=0은 −7/18≤M4≤7/12, 1≤κ≤2를 준다. P4 일치는 이 국소 주파수를 맞추지만 유한 d 전체 angular 응답을 보장하지 않는다. 일반 잔류 M4에 대한 별도 nonlinear spectrum 캠페인은 실행하지 않았다.

Native b0=0.6, 관측 b=0.8, n_mu=32 P24에서는 A−A_ref=−9.9452975659e−4로 고정1e−6 목표의 약995배, **FAIL**이었다. 별도 단일 frozen-opacity slab의 bin192에서는 흡수 전 inventory로 정규화한 photon/energy 오차 −2.071e−8/−1.105e−8로 고정1e−4 목표를 통과했다. 실험 조건과 판정 범위는 서로 다르다. [종합 판정](S7_RESULTS_KO.md)에 실패 분류와 남은 의무를 모았다.

## 물리 범위와 코드 identity

Non-tilted axisymmetric Bianchi I, signature(−,+,+,+), \(a_\perp=ae^{-b}\), \(a_\parallel=ae^{2b}\), \(s=\dot b\), \(\Sigma=\sqrt3|s|/H\)다. 새 **명시적 locally isotropic birth** angular quadrature만 보정한다. 기존 photon/physical anisotropic stock의 frame, rays, weights, spectral cells를 보존한다. 원 spectral owner는 `cosmosapjw-quantum/rei_bianchi@0e25846433170d0f420c4cda44a0bedbf02cd177`이다.

결합 Python은 pressureless donor 공급을 함께 계산한 제조 모델이고, native는 고정 MD14 owner를 처방 기하에서 실행했다. Native MD14와 Einstein feedback의 전체 결합은 아직 구현·실행되지 않았다. 상수 b0는 고정 ray grid의 frame 변환 조건성 변수이며 물리적 누적 shear displacement와 같지 않다.

| identity | commit |
|---|---|
| S7 원래 과학 실행 입력 | `2865f60bf0a247eaab4997c222ad82ae22a4c8fa` |
| Exact observer R2 코드·계약 | `c689dcf151a9b3a6ba830d2a7f4fe8cc6a68385a` |
| R3 한 이력 source·계약·실제 실행 | `f993bf7121af7bb6d69698244089201e28868ebc` |
| 최종 결과·handoff | 이 파일을 담은 commit 및 [PR174 최종 closeout](https://github.com/cosmosapjw-quantum/bass/pull/174) |

새 코드: coupled_cohorts.py, run_s7_coupled.py, run_s7_strict_margin.py, native_cohort_probe.rs, run_native_cohorts.py와 검증 코드. Source 확보·hash 확인·컴파일·실행·분석 pipeline을 준비해 이 샌드박스에서 실제 사용했다. NCP는 사용하지 않았다. 선택적 재현 경로는 [Codex handoff](CODEX_HANDOFF_KO.md), 다음 대화는 [handoff](NEW_THREAD_HANDOFF_KO.md)를 따른다. 새 연구 전에 새 cloud 실행과 GitHub HEAD/PR 댓글부터 확인한다.

실제 추가 native stagingworker4, 계산/BLAS thread1, native job27.36초, coupled campaign20.15초, R3한 이력3.17초였다. Worker16, RAM16GiB, disk4GiB, 개별job1800초 상한을 유지했다.

## 남은 의무와 보존한 이력

큰 b의 native angular support/refinement, R3 margin의 다른 입력으로의 일반화, full birth-memory tangent, 에너지 공급을 포함한 native Einstein feedback, 전체 reactive history와 spectral accuracy가 남았다. 양의 해가 없는 support는 실패로 남기고 음의 weights나 허용오차 완화로 우회하지 않는다. REI production/full EoR/merge 승인은 없다.

[S7 이전 README](history/20261019_PRE_S7_README_KO.md), [S3 이론](S3_THEORY_KO.md), [S3 결과](S3_RESULTS_KO.md), [native adapter](NATIVE_ADAPTER_KO.md), [S6 이론](S6_THEORY_KO.md), [S6 결과](S6_RESULTS_KO.md)를 보존했다. 원 balance.rs5테스트, S3 P24와 S5 native 도입은 이미 완료되어 반복하지 않았다. S6 pre-asymptotic rate FAIL38/344, 비구간 수치 인증의 한계, 제약 추가 후 악화된44/238쌍도 유지한다.
