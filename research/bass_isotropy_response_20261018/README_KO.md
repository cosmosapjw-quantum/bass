# BASS S7: 결합 Einstein–shear와 native source-age 검증

2026-10-19 Stage 3. 새 S6 결과를 양쪽 `/BASS_BACKUPS`와 Git HEAD에서 먼저 발견해 재사용한 뒤,
S7 결합·native 캠페인을 실제 실행했다. 원래 판정 R1과 사후 exact 재판정 R2를 모두 보존한다.

| 새 S7 단계 | 현재 상태 | 근거 |
|---|---|---|
| 결합 이론 | 독립 h 진화, donor closure, C′=−2C, 이산 angular equilibrium 주파수 유도 | [이론](S7_COUPLED_THEORY_KO.md) |
| 독립 대수 | Fraction 28 + Decimal 80자리 5 PASS | [독립 검산](evidence_s7/theory_review/INDEPENDENT_REVIEW.json) |
| 결합 실제 캠페인 | 36입력 중 28완료·8 support 실패, benchmark 7이력; R2 true moment FAIL 1개 | [실제 결과](S7_COUPLED_RESULTS_KO.md) |
| Native 실제 캠페인 | 51입력 중 42측정·9 support 실패; exact integrity PASS, angular accuracy FAIL 2개 | [native 결과](S7_NATIVE_COHORTS_KO.md) |
| R3 수리 | 한 이력의 내부 solver 종료 기준을 1e-15로 강화; 최종 gate는 3/10^15 유지; 실행 전 | [R3 사전등록](evidence_s7_coupled/PREREGISTRATION_R3_STRICT_MARGIN.json) |
| 게시·백업 | `2865f60b`와 `c689dcf1` 원격 readback; 양쪽 cloud identity 확인 | [DAG](DAG.json), [진척](S7_PROGRESS_KO.md) |

결합 Python의 에너지원은 양의 pressureless donor인 제조 모델이다. Native는 고정 MD14 source owner를
처방 기하에서 실행했다. Full tangent memory는 유도 계약이며 실행 검증은 없다. 높은 b0는 고정
owner ray grid의 조건성 변수이고 상수 b 자체가 gauge-invariant 전단인 것은 아니다.
기존 photon/anisotropic stock은 유지하고 새 locally isotropic birth angular quadrature만 보정했다.
양의 support가 없으면 구체적인 feasibility 실패를 남긴다. Moment 일치와 보존 ledger를 continuum
각도 정확도, native full reactive history 또는 production 승인으로 사용하지 않는다.
추가 worker≤16, RAM16GiB, disk4GiB, 개별 job1800초. REI production/full EoR/merge 승인은 없다.

## 재사용한 S2–S6 증거

아래는 S7 실행 전의 검증된 이력이다. [이전 문서](history/20261019_PRE_S7_README_KO.md)를 보존한다.

# BASS S3·native·S6: birth isotropy, 유한 d 오차, spectral 잔차

2026-10-19 S6 갱신. [S6_THEORY_KO.md](S6_THEORY_KO.md), [S6_RESULTS_KO.md](S6_RESULTS_KO.md).

| S6 결과 | 판정 | 근거 |
|---|---|---|
| 유한 d 오차의 정확한 moment 분해 \(\mathcal A_\alpha-\mathcal A_{\rm iso}=\sum k_\ell(d)M_\ell/F_\alpha\), \(\rho(d)=\sqrt{\coth(3|d|/2)}\), 비구간 30자리 quadrature 및 명시적 arithmetic floor를 사용한 tail 수치 평가 | PASS(146 저장 rule, 1460점) | [r3](evidence_s6/finite_d_r3/RETURN_S6_FINITE_D.json) |
| Refinement 수렴률 \(\rho_*=\min(\rho(b),\rho(b+d))\) | 사전 gate **FAIL 보존**(38/344, pre-asymptotic), held-out PASS | [held-out](evidence_s6/refinement_holdout_r2/RETURN_S6_REFINEMENT_HOLDOUT.json) |
| 제약 vs refinement 분리 | P2→P24 변화=ℓ=4 목표항+ℓ≥6 부수항(≤47%); 238쌍 중 44쌍 악화 | [CONSTRAINT_EFFECT](evidence_s6/finite_d_r3/CONSTRAINT_EFFECT.json) |
| Exact rank1 certificate 실행 경로 | PASS(Python, exact Fraction) | `rank1_certificate.py` |
| 5.369926725506957e-12 설명 | Simpson-32 기준값 절단 오차(GL8 native는 1e-16 이내), cps⁻⁴; native 26행 2회 PASS | [run02](evidence_s6/spectral/run02_r2prereg/RETURN_SPECTRAL_REFINEMENT.json) |
| Source-age cohort 합성(처방 기하) | PASS; 결합 Einstein feedback **미실행**(계약만) | [source_age_r2](evidence_s6/source_age_r2/RETURN_S6_SOURCE_AGE.json) |

Moment 제약만으로 보장되는 오차는 차수당 약 \(\rho(d)^2\)배만 줄어든다. d=0.2에서 이 상한으로
1e-6을 보장하는 데 충분한 차수는 P2…P24다. 현재 native n_mu≤32는 \(\max(|b|,|b+d|)\gtrsim0.6\)에서
angular 해상도가 부족할 것으로 예측된다. 독립 code/theory 검토의 지적은 모두 반영했다.

---

## (이전) S3와 native 새 source 보정: 실제 실행 완료

2026-10-19. **P2 birth isotropy와 이후 collisionless shear response는 서로 다른 조건**임을
직접 유도·검산했다. 양의 P2/P4 Python/Rust 보정, 분리된 angular 캠페인 및 고정 REI
owner에 연결한 실제 native 새 source adapter의 제한 검증을 마쳤다.

| 결과 | 근거 |
|---|---|
| D의 0~3차 Legendre 미분, 양의 반례, exact support1023개 | [S3_THEORY_KO.md](S3_THEORY_KO.md) |
| Python14, Rust16, CLI valid1/negative7, 동일 입력43, reuse guards13 PASS | [S3_RESULTS_KO.md](S3_RESULTS_KO.md) |
| 165 rule 중146 측정,1606 response points,19 구체적 지지 실패 | [S3 캠페인 receipt](evidence_s3/campaign/RETURN_S3_CAMPAIGN.json) |
| 원 native owner compile, 새 native tests7,20 측정행, runner regressions6 PASS | [NATIVE_ADAPTER_KO.md](NATIVE_ADAPTER_KO.md) |
| Python 두 review finding 수정·종결, Rust와 native adapter 별도 독립 검토 | [Python 검토](evidence_s3/INDEPENDENT_PYTHON_REVIEW.json), [native 검토](evidence_native_s3/INDEPENDENT_ADAPTER_REVIEW.json) |

`F=<R>`, `G=<D>`, `A=G/F`, `M_l=<P_l>`로 쓰면
`M2=0 => A'(0)=-8/5+(36/35)M4`이고,
`M2=M4=0 => A''(0)=16/7+(216/77)M6`다.
P4를 맞춰도 고차 moments와 유한-d angular error는 남는다.

기존 `balance.rs`의 작성된5개 테스트는 원본 무변경으로 실제 실행해 통과했다.
S2 게시 commit은 `87149cdb673c250ccbb36dda5d43a38f0f7dd7b7`, S3 게시 commit은
`a7938ad51ad0fa324c5cb680dddb5fbfc7ed218e`다. 기존 Python15 및 PR173 native58/
negative5는 원본 증거를 재사용했고 새 실행으로 세지 않는다.
실제 native source 게시 commit은 `b30a2044be1ae04a68d8319f47d15a5bed751668`,
tree는 `bf3a57343140fda867bae9ea94932d9c1475f53b`다.

## Native 결과의 범위

원 owner `cosmosapjw-quantum/rei_bianchi@0e25846433170d0f420c4cda44a0bedbf02cd177`의
57개 원 파일을 그대로 컴파일했다. 새 source를 빈 임시 state에 주입하고 그 birth에만
양의 angular 배율을 적용한 후 기존 state에 transactionally 더한다. 기존 anisotropic stock,
spectral integrals, bin 및 source frame은 유지한다. Caller는 새 locally isotropic emission과
non-tilted local orthonormal frame을 명시해야 한다.

20개 native 사례에서 old-stock photon/energy transfer ledger의 최대 상대 잔차는
각각 `8.62786e-14`, `1.43679e-13`이었다. 기존 parent ledger gate `1e-11`을 유지했다.
Measured native derivative와 실제 energy-moment 식의 차이는 최대 `1.30149e-10`이었다.
이 native quantity는 birth energy로 나눈 `G'(0)`이다. A의 현재 energy 정규화와 구별한다.

Native energy와 고정 source-cell 평균의 최대 상대 차이 `5.36993e-12`는 S6에서 owner 기준값
(Simpson-32)의 절단 오차로 설명됐다. 24/96-bin 비교만으로 spectral convergence를 인증하지 않는다.
Native job은 Rust1.94.1로14.96초, 관측된 child peak RSS339804KiB,
생성 disk16409633bytes였다. NCP는 실행하지 않았고 현재 native 범위의 미실행 의무는 없다.

## 고정 조건과 재개

Non-tilted axisymmetric Bianchi I, signature `(-,+,+,+)`, `a_perp=a exp(-b)`,
`a_parallel=a exp(2b)`, `s=dot b`, `Sigma=sqrt(3)|s|/H`를 유지한다.
새 명시적 등방 source의 angular quadrature만 보정하며 existing photons와 물리적
anisotropic source는 초기화하지 않는다. Strict positivity/reflection parity와 고정
spectral owner를 유지하고 feasibility 실패를 음의 weights나 tolerance 완화로 우회하지 않는다.

현재 상태는 [DAG.json](DAG.json), [RETURN_TO_CHATGPT.json](RETURN_TO_CHATGPT.json),
[PUBLICATION_CLOSEOUT.json](PUBLICATION_CLOSEOUT.json)을 따른다. 과거 문서는 history/에
보존한다. [Codex handoff](CODEX_HANDOFF_KO.md), [새 대화 handoff](NEW_THREAD_HANDOFF_KO.md)는
이미 완료된 캠페인을 반복하지 않고 새 백업·PR 결과를 먼저 대조하도록 한다.

S6 이후 남은 연구는 coupled Einstein/shear feedback 실행, native source-age 합성,
transport/absorption/history 범위의 spectral 수렴, native n_mu≤32의 큰 비등방 영향 측정이다.
현재 P2/P4 일치나 제한 native ledger 통과를 continuum, 전체 finite-bin 보존,
REI production 또는 full EoR 승인으로 확대하지 않는다. Draft PR174는 merge하지 않는다.

