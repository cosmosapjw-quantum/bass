# PLAN-NEXT-v5.1 — 도구 보완판 (2026-08)

> v5 (52차) 의 확장 계획에 **설치 도구 전수조사와 운용 규정**을 보탠 판.
> 이번 세션 실증: Wolfram MCP 가 새로 연결되어 v5 §L'1 의 "미설치 — 권고" 를
> **"연결 완료 — 실증 5건"** 으로 갱신한다 (아래 §11.1).
>
> ★ 이 파일은 저장소 밖에서 작성됐다 — 이번 턴에 컨테이너가 회수되어 작업트리와
> 업로드가 모두 소멸했고 (V16 산출물 재적용 대기), 그 사건 자체가 §11.5(mem0)의
> 근거다.  다음 복원 시 이 파일과 V16 재적용을 함께 커밋할 것.

---

## §0–§10 : v5 본문 그대로 (변경 없음 — 티어 F/J/H'/I/G/K'/L', DAG, 위험표)

v5 의 착수 순서 권장(F→J→H'→I→G)과 위험표는 그대로 유효하다.  아래 §11 이
각 티어에 도구를 **구체적으로 배선**한다.

---

## §11. 도구 운용 규정 (전수조사 2026-08-03)

### 11.1 Wolfram MCP — 연결 완료, 이번 세션 라이브 실증 5건 ★★

| 실증 | 결과 |
|---|---|
| class A Gauss 전파 dΩ/dτ−Ω(2q−(3γ−2)) | **0** (sympy 와 독립 엔진 합치) |
| 교환항등 K̇−(2qK+2Σ·S), 반증된 옛 식의 잔차 | **0**, 잔차 = 정확히 6Σ·S (V15 반증기록 재확인) |
| class B Codazzi Ċ−4(q+Σ₊−1)C | **0** |
| D1c λ 적분 ∫2ln(1/x)dμ_G − π²/(6ln2) | **0** (닫힌형을 Wolfram 이 독립 유도) |
| Wigner 3j 5표본 20자리 vs sympy | **최대차 0.00e+00** — J1 이중대조 파이프라인 가동 확인 |

운용 규정:
- **V15 항등의 이중 엔진화**: 새 기호 항등은 sympy(테스트 게이트) + Wolfram(감사
  스크립트에 기록) 둘 다 통과해야 "닫혔다" 고 적는다.  CAS 자체 버그까지 교차검증.
- **J1 (계수공간 PSTF)**: 3j/CG 표를 sympy 로 생성 → Wolfram 20자리로 대조 후 Rust
  codegen (g_* 표 방식 재사용).  부호규약(Condon–Shortley) 불일치는 dense 대조가
  최종 심판 (v5 위험표 유지).
- **F2 (정확해 매트릭스)**: Taub/NUT/Collins–Hawking 닫힌형을 Wolfram 로 재유도해
  수치 게이트의 참조값 생성.
- **주의**: 커널은 무상태(stateless) — 정의 재사용 불가, 한 평가에 자족적 코드로.
  긴 유도는 sympy(로컬)로, 스팟 대조만 Wolfram 으로 (토큰·왕복 절약).

### 11.2 caveman — 토큰 경제 규율 ★★

| 도구 | 편입 지점 |
|---|---|
| `cavecrew-investigator` | "어디에 정의/호출되나" 류 위치탐색 전부 위임 (본선 토큰 ~60% 절감, read-only). 예: R-계열 포트 전 호출자 지도, F1 라우팅 지점 조사 |
| `cavecrew-builder` | 1–2파일 기계적 편집 (bootstrap 기대값 갱신, 상수 교체, 주석 정리). 3+파일이면 자동 거부 — 본선이 직접 |
| `cavecrew-reviewer` | 커밋 전 diff 훑기 (한 줄/발견, 칭찬 없음) — §11.3 의 과학 리뷰와 **병렬** |
| `caveman-compress` | PR-STATUS 가 비대해질 때 압축 (단, 반증 기록은 압축 금지 — 원문 보존) |

규율: 본선(main thread)은 설계·물리 판단·게이트 작성에만 토큰을 쓰고, 탐색·기계
편집은 서브에이전트로 내린다.  단, **오라클 대조·반증 판정은 위임 금지** (판단이
본선의 일이다).

### 11.3 physmath-coding-harness — 기존 방법론의 공식화 ★★

이 프로젝트가 손으로 유지해 온 관례(오라클 확정·두 경로·반증 기록·게이트)와 같은
구조가 에이전트/스킬로 설치되어 있다.  채택:

- **대형 증분 (J1, I1, G1)**: `research-code-task` 골격 (계약→기준선→국소화→최소
  패치→층상 검증→독립 리뷰→마감).  기존 PR-STATUS 관례와 병합 — 대체가 아니라
  집행기로.
- **소형 증분**: `ultralight-code-run`.
- **커밋 전 독립 리뷰 상설화**: `scientific-diff-reviewer`(읽기 전용) — V16 에서
  "수정이 또 구멍을 내는" 사고를 잡은 2차 공격을 **에이전트 관례**로 승격.
- **수치 변경 시**: `numerical-validator` 로 수렴차수·허용오차·시드 재현 스윕
  (D2c/D3 방법론과 동형).
- `coding-harness-init` 은 다음 복원 때 저장소에 1회 설치 (CLAUDE.md·검증행렬 —
  기존 문서와 충돌 없게 기존 관례를 계약문서로 옮겨 적는 방향).

### 11.4 core 과학 스킬 — 문헌 CRAG 의 1급 경로 ★

`core:arxiv`(전문 검색·취득), `core:inspire`, `core:ads` → F2 정확해·G 충돌항·I2
BKL 물질보정의 문헌 대조를 WebFetch 임시방편 대신 전용 스킬로.  `core:hepdata` 는
현재 범위 밖(명시), `core:zenodo` 는 논문화(§11.7) 시 재현 패키지 배포.

### 11.5 mem0 — 컨테이너 회수 대비 (조건부 채택) ★

이번 턴의 사건이 근거다: 작업트리 + 업로드 디렉토리가 **동시 소멸**해 V16 산출물
재적용이 필요해졌다.  mem0 는 현재 스킬만 있고 MCP 백엔드는 미탐지 — **1회 가용성
검증**(`mem0:health`) 후 채택.  채택 시 저장 규격:
```
(증분 ID, pytest/cargo 기대값, 최신 타르볼 계보, 미적용 diff 목록, 다음 착수 항목)
```
불채택 시 대안: 스냅샷 말미에 `STATE.md` 한 장 (같은 규격) — 타르볼에 실려 다니게.

### 11.6 ecc 선별 + 훅 운용 노트

- 채택: `rust-reviewer`/`rust-build-resolver`(커널 증분), `python-reviewer`,
  `silent-failure-hunter`(V16 의 침묵실패 사냥과 동형 — 정기 감사에 편입),
  `pr-test-analyzer`(게이트 품질 점검), `benchmark-methodology`(R-계열 측정 규율).
- **GateGuard 훅 활성 확인**: 세션 첫 Bash·신규 Write 에 사실게이트가 걸린다 —
  턴 서두에 ①요청 요약 ②명령 목적(Write 는 호출자·중복·데이터·지시원문)을
  선언하고 진행 (이번 턴 실측 2회).
- 무관 플러그인 명시 제외: twilio/sendgrid/sanity/common-room/datarobot/qdrant/
  brightdata(스크래핑 — CRAG 는 §11.4 로 충분) 등 — 호출하지 않는다.

### 11.7 논문화 티어 신설 (P) — academic-research-skills

`report_v2.tex` 가 이미 있다.  F2/J/I 가 결과를 쌓으면: `ars-lit-review`(선행연구),
`ars-citation-check`(claim-source-audit 병행 — 인용이 주장을 실제로 지지하는지),
`ars-reviewer`(투고 전 자체 심사 — 사용자 REFEREE 모드 관례와 접합), `core:zenodo`
(재현 패키지).  **P 티어는 G1 이후** — 결과 없이 논문 틀부터 잡지 않는다.

### 11.8 기타

- **Mermaid MCP**: 계획 DAG·모듈 의존도 렌더 (이번 턴 §12 다이어그램).
- **dataviz**: 결과 그림 규율 (M11 CMB 지도, D1c 히스토그램).
- **ds:statistical-analysis**: D1c-류 앙상블 통계의 방법 점검(KS·부트스트랩 오차).
- **Hugging Face MCP**: 사전계산 표(g_*, 3j, Lebedev) 데이터셋 호스팅 후보 — 보류.
- **Gmail/Calendar/Drive**: OAuth 미승인 — 비대화 세션에서 인가 불가.  필요 시
  claude.ai 커넥터 설정에서 승인해야 열린다 (현재 계획에는 불필요).

---

## §12. 세션 턴 프로토콜 (도구 반영 개정판)

```
0. (훅) GateGuard 사실게이트 응답 → 컨테이너 생존 확인
1. 복원 필요 시: 타르볼 추출 → bootstrap (백그라운드) → 그동안 문헌/기호 작업
2. 위치탐색: cavecrew-investigator │ 설계·물리: 본선 │ 기호 이중검증: sympy+Wolfram
3. 구현: (대) research-code-task / (소) ultralight-code-run — 게이트·반증기록 관례 유지
4. 커밋 전: scientific-diff-reviewer + cavecrew-reviewer 병렬 → 수치 변경 시 numerical-validator
5. 전체 스위트 → PR-STATUS → 커밋 → 스냅샷 (+STATE.md) → SendUserFile
```

---

## §13. 이번 턴에 이미 실증된 것 (요약)

1. Wolfram 5건 (표 §11.1) — v5 L'1 의 약속이 계획이 아니라 **가동 중인 사실**이 됐다.
2. sympy↔Wolfram 3j 이중대조 0.00e+00 (20자리) — J1 의 검증 파이프라인 조립 완료.
3. GateGuard 훅 실측 (Bash·Write 2회), mem0 백엔드 부재 실측, Gmail/GCal/GDrive
   미인가 실측.
4. 컨테이너 이중 소멸 실측 → §11.5 의 근거.  V16 재적용 목록:
   `tests/test_v16_adversarial.py`, `_rustcore/src/lib.rs` 경계검증 3종
   (th_check/th_geo/state_len), `PLAN-NEXT-v5.md`, PR-STATUS 52차,
   bootstrap 1148/70 — 전문이 대화 기록에 보존되어 있어 즉시 재적용 가능.
