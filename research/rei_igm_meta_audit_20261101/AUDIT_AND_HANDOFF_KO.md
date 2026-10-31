# 2026-11-01 적대적 메타 감사: BASS CE1 → REI IGM 임계경로 복귀

## 1. 판정 및 증거 범위

이 감사를 BASS Draft #302 정확한 HEAD `bbebf7f0cdc3e23eec422f67118e8d402afb106c`에서 수행했다. `rei_bianchi/main` `ae3402713c4b6530ab2b27f008f5f5d5c6a999ed`, IGM 원 분기 PR #85/#87/#89, 최근 REI F4 PR #317 `45154b5d661296ec4ae5d39bc1d1502c1d9761f3`, BASS 원래 2026-08-21 재정렬 문서, `research/ce1aq_20261101/reports/DAG_DELTA.json`을 대조했다. 모든 브랜치와 개인 백업을 실제로 열어본 완전한 전수조사라는 주장은 하지 않는다. 역사적 데이터를 삭제하거나 재판정하지 않는다.

**관찰 가능한 사실:** CE1AL #296, CE1AN #299, CE1AO #300, CE1AP #301, CE1AQ #302는 정확한 six-cell Einstein–Vlasov에서 각각 곡률·유한 source·고차 각도·null-redshift·Sachs optical distance의 유효한 scoped 계산을 수행했다. 하지만 모든 단계에서 BASS CE1 9/15, 신규 상위 0을 명시했다. CE1AM은 별도 로컬 bounded proof/computation이며 상위 승격되지 않았다. 광학 결과가 REI의 이온화율, 물질/광자 공동 이력 또는 충돌 광학깊이에 결속된 source-equivalence witness는 없다. 10~20 단계별 PASS, 수천 행, 여러 SHA/ZIP과 원격 CI GREEN은 과학적 검산이지 임계경로 진전이 아니다.

**중앙 정본:** REI main의 `docs/roadmap/D0_PR_ROADMAP.md`는 D0 10~12 PR 중 B2C2 PR2가 진행 중이고, B2D/B2E 이후 C0 기하 결합을 설계했다. `docs/science/current_00_READ_FIRST.md`는 4-site 한 개 FLRW microstep, 3 shape lanes, partition 2048/4096 PASS, 1024 FAIL을 정직하게 기록한다. 다음 중앙 단계는 **첫 canonical BDF interval 전체**이지 또 다른 Weyl 부호나 고차 beam atlas가 아니다. 이전 IGM PR #89는 manufactured model `0.0008` 구간 37-field 합격이지만 더 긴 z=12→10 8/37 실패 및 물리 입장 HOLD를 닫지 않았다. F4 PR #317이 보고한 central 28/88, working 33/88, physical-fast 4/7은 그 F4 ledger의 자기보고 상태이며 REI main D0 또는 BASS 9/15와 동치가 아니다.

## 2. 실제 실패 원인과 심각도

| 분류 | 관찰된 결함 | 과학적 결과 | 조치 |
|---|---|---|---|
| BLOCK_NOW (process) | “다음”을 마지막 CE1 PR의 후계자로만 해석 | 원래 REI H/He 구간 미완료 | 명시 없으면 REI 임계경로 우선 |
| BLOCK_NOW (claim) | scoped `1/1`, 새 행/그림, Git CI와 중앙 수용 혼동 가능 | 9/15, 28/88 인플레이션 위험 | source owner + consumer + 실제 입장 증거 없으면 delta 0 |
| BLOCK_NOW (coupling) | massless collisionless six-cell과 H/He IGM source를 같은 물리 입력처럼 취급할 위험 | 광학거리만으로 ionization/visibility 아님 | 시계·프레임·경계·광자 N/E·기체 상태·opacity 정합 검증 |
| FIX_SOON | 중앙 28/88, main D0 PR 로드맵, BASS 9/15 혼재 | 임계경로 실종 | 서로 다른 소유자·그래프 정본을 보존하는 typed overlay |
| FIX_SOON | 부차적 proof·CMB optics의 정밀화가 본 목표 앞섬 | 높은 품질의 추가 연구지만 central delta 0 | default는 first interval, explicit exploration만 side lane |
| BACKLOG | 다수 S0/S1/S2·20 R/C 문서, 반복 blind self-review | 검증 비용 상승, 연구 진전 대체 | 한 번의 증거 checkpoint 재사용, 새 결함 때만 재검토 |
| BACKLOG | August 21 BASS realignment가 이번 drift를 방지하지 못함 | 정책 존재만으로 라우팅이 제어되지 않음 | 기존 PR policy에 실제 다음 작업 선택 원칙을 추가 |

가장 불편한 평가는 **assistant의 선택 편향도 드리프트를 증폭했다**는 것이다. 새 숫자·그림·PR을 빠르게 반환하는 것이 이미 정본에 적힌 중앙 수용조건을 읽고 어려운 비평형 thermochemistry interval을 닫는 것보다 쉬웠다. 이 판단은 REI IGM 프로그램을 대상으로 하며 BASS 자체 Type-II 연구의 기존 정당한 임계경로를 지우지 않는다. 이것은 연구자의 CE1 아이디어 자체의 결함이 아니라 포트폴리오 라우팅의 결함이다. 반대로 기존 CE1 이론·수치·출처·백업을 폐기해야 한다는 주장도 성립하지 않는다.

## 3. 적용된 최소 교정

- BASS 기존 `docs/development/PR_AUTOCOMMIT_POLICY.md`에 **선행 과학 목적/소유자 검사**를 덧붙이되 기존 자동 commit/push 및 merge HOLD는 보존한다.
- `docs/development/REI_IGM_MISSION_REALIGNMENT_20261101.md`는 기본 라우팅을 중앙 첫 interval로 되돌리고 의도적인 auxiliary 탐색을 계속 허용한다.
- `docs/development/REI_IGM_MISSION_DAG_20261101.json`은 REI main의 다음 실물 과학 의무, BASS의 source-matched bridge, optical-depth 소비자가 연결되는 의존성 **overlay**다. 이는 새로운 REI 정식 DAG가 아니며 `DAG.json`(ACCEL02), REI `PROJECT_STATE.json`, 기존 BASS CE1 증거를 바꾸지 않는다.
- `scripts/check_igm_mission_alignment.py`는 overlay 형식·경로·소유자·계수 및 mutation/claim 혼동을 단일 표준 라이브러리 검사로 거부한다. GitHub workflow는 이 좁은 검증만 실행한다. **물리학 수용 gate를 신설하는 것이 아니다**.

## 4. 긍정적 중단 조건과 재발 방지

두 번 연속 보조 PR이 만들어졌는데 중앙 DAG에 변화가 없다면, 프로세스 문서를 더 만들지 않고 한 번만 원 목표와 현재 병목을 확인한 뒤 REI 중앙 첫 interval 혹은 BASS→REI 실제 물리 source bridge로 돌아간다. 사용자가 명시적으로 CE1 추가 탐색을 선택하면 계속한다. 새로운 증거가 생기면 임계경로를 갱신하되 원본 그래프·과거 보증을 덮어쓰지 않는다.

**이번 감사 자체는 과학적 상위 DAG를 완료시키지 않는다.** BASS CE1 9/15, REI F4 보고 중앙 28/88(working 33/88), main D0 PR2 진행 중, first canonical interval 미완료를 그대로 보존한다. production/merge/HOLD 모두 불변이다.

## 5. 다음 대화 handoff

```text
$physmath-research-loop
PROJECT=REI_BIANCHI_IGM_MISSION_REALIGNMENT
CONTROL_REPO=cosmosapjw-quantum/bass
REFERENCE_BASS_HEAD=bbebf7f0cdc3e23eec422f67118e8d402afb106c
REFERENCE_REI_MAIN_HEAD=ae3402713c4b6530ab2b27f008f5f5d5c6a999ed
REI_MAIN_NEXT=FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY
REI_FIRST_INTERVAL_STATUS=OPEN_NOT_ACCEPTED
REI_D0_STATUS=PR2_B2C2_IN_PROGRESS
REI_F4_REPORTED_CENTRAL=28/88_NOT_RECONCILED_TO_D0
BASS_CE1_UPPER=9/15
BASS_CE1_NEW_UPPER=0
BASS_CE1AL_TO_CE1AQ=ARCHIVED_VALID_AUXILIARY_NOT_IGM
DEFAULT_NEXT_TASK=REI_FIRST_CANONICAL_INTERVAL
BASS_PARALLEL_ALLOWED=EXACT_SOURCE_TIME_HHE_PHOTON_OPACITY_BRIDGE_FOR_C0
DO_NOT_AUTO_PROMOTE_CE1_KM2_VIGILODE=true
NO_MORE_META_CYCLES_UNLESS_NEW_DEFECT=true
NO_AUTOMATIC_MERGE_OR_PRODUCTION=true
USE_REI_OWNER_LIVE_SOURCE_AND_DAG_BEFORE_EXECUTION=true
```

Read: `rei_bianchi/docs/science/current_00_READ_FIRST.md`, `rei_bianchi/handoff/CURRENT_HANDOFF_PROMPT.md`, `rei_bianchi/docs/roadmap/D0_PR_ROADMAP.md`, then BASS `docs/development/REI_IGM_MISSION_REALIGNMENT_20261101.md` + JSON DAG. **Return to an actual H/He coupled calculation, not another process review**, unless a newly observed material blocker requires repair.
