# 비섭동 연구의 실제 BASS 패키지 통합: 재개 완료

2026-10-28, 중단된 integration/bass-nonperturbative-research-20261028 브랜치를 재개했다. Draft PR223, 검증된 코드 commit25827103b79ae49287722e56277ef1943b562d85. 이 보고서를 추가한 후속 commit은 문서·영수증만 바꾸며 수치 코드 검증 commit과 구별한다.

## 보존과 실제 연결

20개 연구 원문은 reports/01_DL1.md부터20_BF3C.md까지 연구 순서대로 보존했다. 순서: DL1, DL2, KM1, KM3, DV1A, DV1B, DV2A, DV2B, DV2C, DV2D, DV2E, DV2F, KM2A, KM2B, KM2C, BF1, BF2, BF3A, BF3B, BF3C. 기존 연구 디렉터리와 PR은 삭제하거나 merge하지 않았다. 별도 variant가 있던 단위의 원본 authority는 CODEGEN.json과 original_overrides에 명시한다.

28개 모듈을 bianchi/nonperturbative/_core로 import 구조만 바꾸어 이동했고,26개를 공개 catalog에서 명시적으로 선택한다.19개 원본 회귀 테스트 파일도 package import로 옮겼다. sys.path 변경이나 global module alias를 사용하지 않는다. 원문을 패키지화했다고 과거의 scoped 결과를 production 검증으로 승격하지 않는다.

실제 bianchi.q.polstate.PolQState에 collide_normal_time(dt_s,rest_rate_s,*,beta,panels=32,backend=None)를 추가했다. 반드시 backend='python_oracle'를 명시해야 한다. dt_s는 normal proper seconds, rest_rate_s=n_e_star*sigma_T*c는 electron proper-density opacity다. D를 미리 곱하지 않는다. Geometry와 beta를 고정한 collision-only substep이며 기존 collide/Strang/model/native-first 경로를 자동 교체하지 않는다. 모든 기존 PolQState 메서드와 보호된 backend/model/polarization/pyproject 소스의 identity는 유지된다.

배열 입력에는 bianchi.nonperturbative.normal_time_collision_step을 사용하고, 개별 기능은 load_kernel(name,backend='python_oracle')로 선택한다. Raw 각도 측도와 exact-vacuum(-inf) log intensity, scaled amplitude를 유지하며 출력 물리 검사 완료 후에만 state를 갱신한다. 일반 positivity/stiffness 또는 spectral Thomson validity를 보장하지 않는다.

## 중단 원인과 현재 검증

기존 Actions40644679209는 테스트 전 보고서 바이트 검사에서 실패했다. 원본 ZIP과 대조한20개 보고서 중18개는 같았다. KM2C의 추가 '인자 '와 BF3C의 추가 공백을 정확한 알려진 preimage에서 원본 hash로 복원했다. 예상 hash, 원본 archive, 물리식과 tolerance는 바꾸지 않았다. 복원·멱등성·알 수 없는 훼손 거절의3개 로컬 검사가 통과했다.

수정 commitde803b2060ca724ed56e930c6c4d25cbd49bfc98의 Actions40648819416/job122683844848가 SUCCESS로 끝났다. Python3.13.5에서 integration/regression240개 통과, fail/error/skip0. 기존 backend/route 검사는20개 중19개 통과와1개 skipped, fail/error0. 모든260개가 통과한 것으로 표시하지 않는다.

20개 원문·28개 생성 소스 identity를 검사했고, research 디렉터리 없는 package의 수치 smoke test와 별도 설치한 wheel에서26개 공개 kernel 및 실제 PolQState 메서드 import가 통과했다. 그 뒤에만 generated outputs를 commit하고 exact remote-SHA 확인 후 non-force push했다. CI_VERIFICATION.json이 실제 결과를 보존한다.

Native Rust와 native constructor 실행, native subagent와 독립 모델 심사는 NOT_RUN이다. 원본 과학캠페인 replay0, 새 과학노드0, scientific DAG8/15 unchanged, production_ready=false. 통합 테스트는 새 package 연결의 검증이지 전체 production solver의 과학 검증이 아니다.

## 보존 범위와 재현

PRESERVATION.json의 복구 ZIP은 원본 archive20개, 원문20개, 게시 생성 hash와 일치하는28개 kernel 및 init overlay, 복원기·CI·identity 영수증을 포함한다. 전체 base repository, public API/bridge 전부, wheel/CI raw logs를 대신하지 않는다. Overlay만 독립 설치하지 않는다.

전체 통합 코드 재현은 verified commit25827103b79ae49287722e56277ef1943b562d85 checkout 후 수행한다. Hosted artifact12799115766은 source.tar.gz, wheel, JUnit/environment/logs를 포함하며2026-11-27T07:16:00Z 만료다. 이 artifact 전체는 현재 container로 다운로드해 재해시하지 않았고 provider digest만 기록했다. Git의 source와 CI_VERIFICATION.json은 별도로 남는다.

```sh
python scripts/assemble_nonperturbative.py --check
OPENBLAS_NUM_THREADS=1 python scripts/validate_research_integration.py --output /tmp/bass-integration-recheck
```

## 이후 연구

새 과학 요청에서 BF3-D를 시작하되 통합 package API를 사용한다. Static periodic lapse의 inverse phase-space map으로 final-x local angular source를 구성해야 하고, global coupled phase Jacobian을 local angular quadrature weight로 쓰면 안 된다. Coordinate collision rate=N(x)*n_e_star*sigma_T*c를 지킨다. 원본 과학 scope와 남은 Einstein/matter/native/spectral 의무를 유지한다. BF3-D 실행과 main/owner/기존 draft PR의 merge는 이번 전환에 포함되지 않는다.
