# S8 진행: full birth-memory tangent와 native angular refinement

## 선택한 작업과 복구 지점

사용자의 이론·코딩 연구 루프 재개, 실제 경량 실행, 가능한 코드 수정·push 및 단계별 백업 요청을 이어서 수행한다. 이번 선택 범위는 미완료인 **출생 이력의 전체 접선 응답**과 **고정 spectral owner의 큰-b native 각도 세분화** 두 leaf다. 이 S8의 결과·게시·handoff까지 완성하며 다른 연구 cycle은 자동 시작하지 않는다.

재개 전 GitHub HEAD/PR174와 양쪽 `/BASS_BACKUPS` 및 하위 폴더를 확인했다. 최신 HEAD는 `fe083a28e066a95e2191bcc6a090adf53605453f`, tree `6fb0f5fb693318cb9476a635817a4ea7025127ba`, 최신 comment6265614481이다. 더 새로운 실행은 발견하지 않았다. 로컬 tracked461개 blob이 일치한다. 누락된 과거15-test 로그2개는 Git에서 원바이트로 복구했고 테스트는 재실행하지 않았다. 최신 Drive ZIP197742B는 SHA256/CRC/manifest22개와 Git blob 모두 일치했다. Dropbox는 이번 fresh metadata와 원래 providerhash proof를 연결한다.

## 현재 작업

| 보존 단계 | 실제 작업·판정 | 다음 행동 |
|---|---|---|
| S8 Stage0 | `2d5d2348` 게시·원격 readback, 양쪽 클라우드 백업 완료; Drive raw ZIP manifest10/10 및 Dropbox provider hash 일치 | post-upload receipt를 Stage1에 포함 |
| S8 Stage1 | `4508e5de` source·prereg 게시, 원격21파일 원바이트 대조, Drive35/35 payload·Dropbox provider hash 일치 | 새8적분·18native 입력 실행 |
| S8 Stage2 | native18입력17측정, finest6 PASS·저해상도8목표 미달·수치 실패1; tangent7적분 저장 후 JSON 직렬화 실패 | 원자료·실패·최소 재개 사전등록 게시·백업 후 미실행 gauge1개만 수행 |
| S8 Closeout | 미완료 | 실제 결과·실패·그림·DAG·복사 가능한 인계·이중 readback |

Tangent 구현은 초기 `y0=s0/H*`를 섭동한다. `h0`의 도함수, 현재기하, 각 출생의 `b(u)`, source-frame `mu`, 양의 KL weights의 implicit derivative를 포함한다. 저장된 두 nonlinear history의 forcing을 접선식 입력으로 쓰지 않는다. 고정 출생시간·donor에서 event sensitivity를 처리하고 중앙차분 nonlinear history 세 쌍 및 항 누락 negative controls와 비교한다. 고정된 실행 수는 tangent 적분8개와 native 새 case18개다. Stage1 게시·이중 readback 후 원래18 native 입력과 tangent7적분을 실제 수행했다. 남은 gauge1개는 아래 재개 사전등록을 따른다.

Native 경로는 원 `AxbiSource.angular_cells`와 `CovariantTransport`의 공개 인터페이스를 이용한다. 새 source의 GL64/128/256만 추가하고 spectral cell/rate/integral 소유자는 원본 그대로 유지한다. 기존 n32 stock은 원래 block에서 보존하며 새 grid로 remesh하지 않는다. 동일 새 support의 prior/P2/P24와 고정 birth/bin/panel에서의 n 변화는 별도 비교다. S7의 n32 오차와 feasibility 실패는 불변 기준으로 재사용한다.

## 고정 조건과 기록

Non-tilted axisymmetric Bianchi I, signature(-,+,+,+), `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, `s=dot b`, `Sigma=sqrt(3)|s|/H`. 양성/reflection/source-frame/fixed spectral owner를 유지한다. 내부 projection margin은 새 입력에 한해 더 엄격하게 설정할 수 있고, admission은 exact `3/10^15` 그대로다. Infeasible support와 실제 각도 정확도 실패를 보존한다.

Source owner: `cosmosapjw-quantum/rei_bianchi@0e25846433170d0f420c4cda44a0bedbf02cd177`, source ID `MD14_Z002_FESC_BB50K_13P6_100_V1`. Original owner 및 완료 S7 source는 수정하지 않는다. Native physical MD14 에너지 공급/Einstein closure와 전체 reactive history는 이번 두 leaf의 완료 주장에 들어가지 않는다.

추가 workers16/RAM16GiB/disk4GiB/개별 job1800초. 설치된 Rust1.94.1을 재사용한다. 선택한 구현자2명과 상보적 독립 검토자1명은 실제 host collaboration으로 배정되었다. 원래 policy의 8-role/11-family 요구는 사용자가 고정한 두 leaf의 PHYS-MATH→PHYS-MATH-CODE 감사로 대응한다. Preferred plugin1.3.0의 선택 범위·유한 검토·typed identity를 적용한다.

`RETURN.checks.coupled_shear_evolution=not_run`은 S7 actual receipt와 충돌한 오래된 요약이라 원값을 역사 필드에 보존하고 현재 설명을 교정했다. `DAG.S7_publication_closeout`의08:07 기록은 과거 recovery 범위라고 명시했다. 이 metadata 교정으로 과학 계산을 반복하지 않는다.

상세 근거: `evidence_s8/intake/FRESH_CLOUD_GITHUB_INTAKE.json`, `POLICY_AND_SCOPE_REVIEW.json/.md`, `evidence_s8/WOLFRAM_PARTIALS.json`, `evidence_s8/PRIMARY_LITERATURE.json`, `DAG.json`.

## Stage1 source freeze

`evidence_s8_tangent/PREREGISTRATION.json` SHA256 `6f88cac768b78c324705590bf6a7e5b2912311f3a4c9494d958a1e4ed2c2ba58`; `evidence_s8_native/PREREGISTRATION.json` SHA256 `df1752714e285ffff797e531fc4c5104e9b129266458f746ff0741a3aeff225c`. Pin된 소스8개/14개를 각각 대조했다. 독립 검토의 publication receipt path binding 및 finest feasibility 분류 finding2개는 고정 전에 닫았다. `S8_THEORY_REVIEW_KO.md`는 prepublication 검토 PASS이고 과학 campaign PASS가 아니다.

## Stage2 실제 실행과 제한된 수선

Native 원 owner57개 불변,17측정의 native kernel/discrete 응답 차이는 수치 정밀도 범위였고 기존32-ray block SHA가 보존됐다. 그러나 `b9_n64_P2P4`는 엄밀한 내부 support에서 `INNER_P2_PRECISION_LIMIT`로 중단돼 campaign integrity는 FAIL이다. 256-ray 여섯 목표의 PASS와 구분한다. 미증명 solver 변경이나 재실행으로 덮지 않는다.

Tangent는 원7개 이력의 byte hash와 exit1 로그를 고정했다. `gate_results.richardson_accuracy`의 NumPy boolean이 JSON serializer에 걸린 구현 오류다. 새 `run_s8_tangent_resume.py`와 사전등록은 기존7raw를 SHA-bound로 재사용하고 bool 값의 의미만 유지해 직렬화하며, 미실행 gauge1개만 적분한다. 원 source·원 prereg·물리식·gate는 변경하지 않는다. serializer 회귀2개 PASS, gauge는 재개 사전등록의 게시·백업 전까지0회다.
