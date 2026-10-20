# S11 C9 저장 증거·실행 provenance 감사

## 판정과 독립성

**PASS_SCOPED — 152/152 감사 항목 PASS.** 이는 저장된 S11 r1 실행 증거를 읽고 대조한 감사 결과다. 원 실행의 101/101 검증과 별도의 집계이며, 두 수를 하나의 과학 검증 분모로 합산하지 않는다.

검토자 `/root/new_branch_intake`는 Rust projector/CLI를 작성했다. Root의 Python reference와 validation runner는 작성하지 않았다. 따라서 이 감사의 독립 범위는 root Python runner의 증거 구성, source/process/output 연결, 그리고 반환된 weights의 별도 정확 다항식 검산이다. **단독의 독립 Rust 구현 승인을 주장하지 않는다.** Rust 소스에 대한 별도 이론 검토자의 검토와 함께 사용해야 한다.

이 감사는 `projector.py`나 `run_validation.py`를 import하지 않는다. 두 solver, compiler, 원래 history를 호출하지 않는다. 저장된 weights 검산에는 두 구현이 사용한 Legendre recurrence 대신 factorial 계수의 닫힌 다항식을 사용했다. 외부 OS 실행 자체를 재현한 감사는 아니며, 보존된 실제 command/stdin/stdout/stderr/exit 기록을 대조했다.

## Source와 Git 연결

| 항목 | 확인값 |
|---|---|
| S11 실행 source | `7fb9b83cba01d37ce4cabbc4772527710601cd96` |
| Source tree | `963a43f26df1f9c6f462b9df9a2c34cf99f525c9` |
| Parent | `e9f8eccc8d86764ebebe9bb98cc68ecb9aad09d8` |
| Git source 게시 시각 | 2026-10-20 17:47:51 UTC |
| Main process 시작 | 2026-10-20 17:49:10.887911 UTC |
| 실제 연결한 execution-source files | 18/18 |
| 게시 manifest 항목 | 44/44 |
| 저장된 recursive tree 항목 | 2,972 |
| 직접 다시 해시한 Git tree objects | 351 |

GitHub에서 source commit과 최상위 tree를 read-only로 새로 읽었다. 새 최상위 tree를 Git object 형식으로 다시 해시하고, 저장된 전체 recursive tree의 351개 tree object도 각각 다시 해시하여 같은 root와 연결했다. 이로써 실행에 사용된 18개 파일의 전체 bytes/SHA256/Git blob이 source tree에 실제 연결됨을 확인했다. Source manifest → execution binding → Git readback의 SHA256 연결도 일치한다.

Stage2 변경 경로 목록은 지정 lane의 DAG와 S11 파일로 제한되고 삭제가 없음을 확인했다. 이 변경 범위 확인은 보존된 stage2 목록의 감사이며, parent tree 전체를 다시 내려받아 만든 새 diff는 아니다.

Source: https://github.com/cosmosapjw-quantum/bass/commit/7fb9b83cba01d37ce4cabbc4772527710601cd96

## Process와 출력 집계

| 저장된 기록 | 확인 개수 |
|---|---:|
| Main runner 검증 | 101/101 |
| 하위 process 기록 | 26 |
| Compiler probe + build | 2 |
| Projection CLI 호출 | 14 |
| Positive Python/Rust pair | 12 |
| 예상 infeasible pair | 2 |
| Domain CLI control | 10 |
| 독립 certificate domain control | 5 |
| 별도 정확 다항식으로 검산한 output certificate | 24 |
| 저장된 angular response 값 | 660 |

Main process는 exit 0, stderr 0 bytes, timeout false다. 벽시계 시간은 2.3758596949919593초다. 기록된 maximum individual child RSS는 238,364 KiB이며, 동시 process tree 전체의 최대 메모리로 해석하지 않는다. Root가 기록한 main timeout 1,750초와 address-space 6 GiB는 사용자 상한 이내다.

Compiler probe는 Rust 1.94.1, commit `e408947bfd200af42db322daf0fadfe7e26d3bd1`을 기록한다. Build는 `--edition=2021 -O -D warnings`, exit 0, 빈 stdout/stderr다. Binary SHA256은 `b1c9690f84de3b9fc52290b7e27417750256fa5fe653134af30b48012f55ced1`이다.

14개 projection 호출의 raw stdin을 다시 파싱해 order, cardinality, mu/prior의 binary64 bits를 고정 입력 및 게시된 4개 archived-input 파일과 대조했다. Raw stdout은 PROJECTIONS에 보관된 객체와 일치한다. Positive 호출은 정확 provisional status, 해당 order, exit 0을 확인했다. Expected infeasible 호출은 `INFEASIBLE_SUPPORT`, exit 3, 빈 stderr와 음의 slack 증거를 유지한다. Domain controls는 사전 지정 status/exit 및 raw process record의 일치를 확인했다. 중복 방향 control은 distinct mu²가 네 개인 9-ray 입력으로, 단순 rank 거부가 중복 계약을 가릴 수 없다.

## 정확 weights와 유리수 control

모든 positive output은 재정규화 없이 양수 weights, exact reflection, normalization 및 해당 P2/P4/P6 gate `3/1000000000000000`을 통과했다. 저장 certificate에 기록된 정확 유리수 잔차와 별도 닫힌 다항식 계산이 모두 일치한다.

| 검산 지표 | 최대값 |
|---|---:|
| Rust exact residual | 1.0280045769226785e-16 |
| Python exact residual | 4.163336342344337e-17 |
| 두 구현의 weight 차이 | 6.938893903907228e-17 |

고정 dyadic support의 exact orbit masses는

`(286/945, 32/105, 2048/6615, 61/735)`

이다. Orbit mu²는 `(0, 1/4, 9/16, 1)`이며, normalization과 첫 세 monomial moments가 정확히 `(1, 1/3, 1/5, 1/7)`임을 별도로 확인했다. 두 dyadic prior에 대한 저장 output과의 최대 차이는 Python 1.650649047194016e-17, Rust 3.900466075931767e-17이다.

예상 실패도 결과에 남아 있다.

- `P24_only_support_P6`: 최소 exact slack `-1/42`, negative facet 1개.
- `b9_n64_P6`: negative facet 30개. Rust의 첫 negative upper-facet enclosure는 약 -0.0189552409897이다. 저장 exact 최소 slack와 raw 실패 문구는 AUDIT_R1.json에 있다.

660개 response는 12개 positive 입력 각각의 55개 strain 값으로 완전하고 중복이 없다. 저장된 reference 연결, signed difference, small-strain coefficient ratio, slope 산술 및 M2–M12의 저장값도 대조했다. **새 continuum 적분이나 native spectral history는 실행하지 않았다.**

## 파일과 다음 사용 범위

- `audit_stored_run.py`: 감사 소스. SHA256 `94ad28a5181a7c7a8c937a425840d73c94d80546aa2ef3c8775f04ed8e5c5c1f`.
- `AUDIT_R1.json`: 152개 항목, 24개 정확 certificate, 42개 감사 입력 파일의 bytes/SHA256.
- `AUDIT_R1_PROCESS_RECEIPT.json`, `audit_r1.stdout`, `audit_r1.stderr`: 감사 실행의 실제 command, stdout/stderr, exit와 시간.
- `commit_fresh.json`, `tree_fresh.json` 및 `*_tool_result.json`: 새 GitHub readback과 원 도구 응답.
- `FILE_MANIFEST.json`: 이 감사 묶음의 파일 identities.

감사 process도 exit 0, 빈 stderr, 0.3437540459999582초다. 이번 감사에서 solver/compiler/ODE/NCP/history 실행과 S9/S10 캠페인 재실행은 모두 0회다. 기존 S8 실패, 전체 spectral-history 의무, 물리 MD14/native shared-Q 결합 및 full birth-memory tangent 의무는 이 감사로 닫히지 않는다.
