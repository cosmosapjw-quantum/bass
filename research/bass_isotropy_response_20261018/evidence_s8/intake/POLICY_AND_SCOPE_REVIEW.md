# S8 재개: 정책·범위 독립 검토

이 문서는 **read-only 복구 감사**다. 새 유도·수치 캠페인·컴파일을 하지 않았고 S7 source, 원시 결과, 그림, DAG, RETURN, CLOSEOUT, handoff를 수정하지 않았다. 대응 machine record는 `POLICY_AND_SCOPE_REVIEW.json`이며 실제 읽은 문서·receipt의 경로와 SHA-256을 담는다.

## 1. 복구한 위치와 identity

S7의 현재 과학 source는 `f993bf7121af7bb6d69698244089201e28868ebc`이고, 저장된 최종 metadata는 `fe083a28e066a95e2191bcc6a090adf53605453f`, tree는 `6fb0f5fb693318cb9476a635817a4ea7025127ba`다. 실제 읽은 `delivery/s7/S7_STAGE4_CLOUD_READBACK.json`이 이를 기록한다. 로컬 폴더는 hydrated source이며 `git rev-parse HEAD`는 exit128이었다. 따라서 이 감사는 로컬 Git HEAD를 확인했다고 주장하지 않고 파일 hash를 고정한다.

부모 agent는 새 Git/PR HEAD가 위 identity와 같고 두 `/BASS_BACKUPS` root·하위 폴더에서 더 새 결과가 없음을 보고했다. 최신 comment는6265614481이다. Fresh Drive197742B/SHA/CRC를 확인했고 메시지 시점에는 manifest 대조가 진행 중이었다. 이 감사 자체에서는 클라우드 connector를 호출하지 않았다. 과거 Drive raw ZIP proof와 Dropbox provider content-hash proof를 같은 raw readback으로 부르지 않는다.

## 2. 적용해야 할 정책

| 근거 | 이번 연구의 필수 적용 |
|---|---|
| `05` Phase0–2, `04` Phase0–2 | 현재 DAG와 실제 선행 evidence를 먼저 복구한다. 완료·부분 검증·실패·unknown·blocked를 분리한다. 완료한 campaign의 retained FAIL을 미실행으로 바꾸지 않는다. |
| `01` Phase1–2, `04` Phase1–5 | 식–변수–단위–부호–frame–실제 call path–observable를 먼저 연결한다. 문서나 test 개수 자체는 물리 검증 증거가 아니다. |
| `04` Phase7, `05` Phase4 | 변경 단계마다 **PHYS-MATH → PHYS-MATH-CODE** 순서로 감사한다. 정의·부호·차원·known limit·양성·숨은 가정 뒤, equation-to-code·활성 경로·reference·conditioning·회귀 위험·최소 검증을 기록한다. |
| `04` Phase8, `05` Phase5 | 필요한 Python 그림을 실제로 읽고 정확성·reference·구간/격자 변화·예측 범위를 재감사한다. 가능한 sign/normalization/grid/alternative-reference 반례를 제한적으로 사용한다. |
| `08` → `07` | 의미 감사와 P0–P3 ledger 후 첫 수정을 하고, 약90mm·180mm의 overlap/clipping/축소 가독성을 최종 확인한다. 실패점·단위·caption·패널 비교 의미를 보존한다. |
| `01` Phase4–7, `04` Phase10, `05` hard bans | smoke test, 더 작은 한 residual, moment 일치만으로 continuum/full-history/production을 승인하지 않는다. 성능·큰 refactor는 현 물리 검증에 필요한 다음 단계가 아니다. |
| 사용자 지시·handoff | 새 단계마다 게시·백업·DAG와 독립 readback을 남긴다. scientific source와 metadata commit, fresh proof와 historical proof를 구분한다. |

일반 `01`의 11 family/global tilt/local boost/polarization/statistics 전체 감사 및 고정8역할 요구는 이 **non-tilted axisymmetric Bianchi I** 단위로 축소 적용한다. 사용자가 명시한 `cosmosapjw-quantum/bass`와 pinned REI owner가 권위 있는 작업 범위다. 원문에 있는 옛 repository 명칭으로 사용자 범위를 바꾸거나 새 승인 절차를 만들지 않는다.

물리 표기는 signature(-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b, Sigma=sqrt(3)|s|/H를 유지한다. 새 명시적 locally isotropic birth의 angular quadrature만 보정하며 기존 photons와 physically anisotropic stock의 분포·frame·birth weights를 보존한다. 양의 해가 없는 지지는 witness 실패로 남긴다. 음의 weights나 tolerance 확대는 허용하지 않는다.

## 3. 완료 상태: 재실행하지 않을 것

S2–S6의 기존58+5 native ledger, Python15, Rust5, S3P24, S5 adapter, S6 finite-d/rank1/spectral/source-age는 각 receipt 범위로 재사용한다. S7 actual receipt도 직접 읽었다.

- Coupled R1은36시도·28완주·8 support 실패와7 benchmark를 실행했고 원래 FAIL은 보존된다.
- R2는 원시41파일·1968birth rule·56old-stock digest를 대조한 재분석이다. Trajectory/benchmark 재실행이 아니다. M2는640/640, P24 M4는255/256이며 진짜 한 초과를 발견했다.
- R3는 `b03_n32_P24_K64` 한 이력의64birth만 더 엄격한 내부 atol1e−15로 수리했다. 최종 exact gate3/10^15는 그대로이며64/64 PASS다. 전 입력 보장은 아니다.
- Native R2는51행·42측정·9 support 실패, integritytrue/accuracyfalse다. 큰 fixed-grid offset의 두 각도 목표 실패9.9453e−4는1e−6 기준으로 남는다.
- 단일 frozen-opacity slab의 bounded PASS는 전체 reactive history가 아니다. S7를 마치기 위해 NCP 실행을 남겨 둘 이유는 없다.

## 4. 독립 확인한 미완료와 다음 단위

**Full birth-memory tangent**는 S7 이론6절의 식(S7.16)–(S7.17)에 계약만 있다. 실제 `coupled_cohorts.py::forcing_comparison`은 두 완성 nonlinear history에서 측정한 forcing의 Duhamel identity임을 명시한다. 현재 geometry, birth geometry memory, source-frame μ와 양의 KL α의 미분을 포함한 tangent solver PASS로 사용할 수 없다. 새 smooth parameter family와 독립 finite-difference/제약·event 검증을 갖춘 한 bounded implementation이 직접적인 다음 leaf다.

**Native high-b angular refinement** 역시 미실행이다. `native_cohort_probe.rs::Case::parse`는8/16/32만 받는다. n>32가 이미 가능한 CLI라고 가정할 수 없다. 단, active CovariantTransport 경로와 다른 owner grid API의 cap을 혼동하지 말아야 한다. 부모가 배정한 별도 native agent가 실제 source constructor/public angular-cell 경로를 감사한다. 새 grid에서 기존 stock을 resample하지 않고 원래 grid의 immutable stock을 보존해야 한다. 같은 support에서 prior/P2/P24, 같은 spectral/birth 설정에서 n 변화를 분리한다.

후보는 위 두 leaf와 **R3 margin의 새 입력 범위 검증** 세 가지다. 부모는 앞의 두 의무를 분리된 gate와 prereg를 갖춘 **S8 한 연구 단위**로 선택했다. Margin 검증은 새 입력에 필요한 범위만 수행하고 옛36-case campaign은 반복하지 않는다. Native MD14 energy-supply/Einstein closure, evolving reactive chemistry·spectral history, 장시간/큰 finite-d 일반 continuum bound는 별도 남은 의무다. 이 S8에 자동 편입하지 않는다.

## 5. 발견한 metadata 혼동

1. `RETURN_TO_CHATGPT.json#/checks/coupled_shear_evolution`의 `not_run`은 현재 S7 actual receipt와 충돌하는 legacy 요약이다. `S7_coupled_native`와 actual receipt를 따른다. 이를 근거로 S7를 다시 실행하지 않는다.
2. `DAG.json#/S7_publication_closeout`는 이름과 달리08:07의 S2/S3/S5/b69 recovery 범위를 담는다. S7 stage1–4 proof 및 최종10:56 receipt와 분리해야 한다.
3. 로컬 Git checkout 부재는 source 미복구를 뜻하지 않는다. 실제 blob/manifest/hash와 원격 HEAD로 확인한다.

부모에게 세 항목을 전달했다. 이 감사는 root metadata를 수정하지 않았다. 새 metadata 정리에 필요한 provenance 수리이며 새 물리 검증을 요구하는 결함으로 취급하지 않는다.

## 6. 감사 결과와 다음 단계

정책·복구 감사는 완료했다. 이 단계에 새로운 과학 그림은 해당하지 않으며, S7 그림은 불변으로 재사용한다. S8의 새 결과가 나온 뒤08→07 figure 감사를 수행해야 한다. 추가 worker≤16, RAM16GiB, disk4GiB, 개별 job1800초 상한은 두 leaf를 합쳐 지킨다. Compiler·06 archive의 존재가 새 과학 결과는 아니며 이 감사에서는 실행·압축 해제를 하지 않았다.

다음은 부모가 확인한 fresh intake와 source identity를 바탕으로 **S8 tangent 및 native angular 설계에 대한 독립 수학·코드 계약 감사**를 수행하는 것이다. REI production/full EoR/merge는 승인하지 않는다.
