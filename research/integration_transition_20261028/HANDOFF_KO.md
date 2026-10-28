# 통합 후 연구 재개 인계

REPO=cosmosapjw-quantum/bass
BRANCH=integration/bass-nonperturbative-research-20261028
PR=223
VERIFIED_CODE_COMMIT=25827103b79ae49287722e56277ef1943b562d85
SCIENTIFIC_BASE=937acea2875f199eebabaa1abcafd531a64035c3
ACTIONS_RUN=40648819416
STATUS=PASS_SCOPED_PYTHON_ORACLE_PACKAGE_INTEGRATION
SCIENCE_PROGRESS=8/15_UNCHANGED
NEXT_SCIENCE=BF3-D_NOT_EXECUTED
AUTO_NEXT=false
PRODUCTION_READY=false

현재 HEAD와 CI_VERIFICATION.json, INTEGRATION_REPORT_KO.md, PRESERVATION.json을 읽어라. 코드 검증 commit 이후 문서·영수증-only commit은 별도로 식별한다.20개 원문 보고서와 CODEGEN identity를 보존한다.

실행은 bianchi.nonperturbative.load_kernel(name,backend='python_oracle'), normal_time_collision_step(...), 실제 PolQState.collide_normal_time(...)로 연결한다. 마지막은 fixed-geometry/fixed-beta collision substep이다. 기존 model/Strang/native-default를 자동 교체하지 않는다. Normal proper seconds와 proper-density rest opacity를 사용하고 D를 미리 곱하지 않는다.

검증: package240pass; baseline19pass/1skip; research-tree-free numerical smoke와 installed-wheel import PASS. Native Rust/constructor, 독립모델심사 NOT_RUN. 과학 campaign replay0, 새 과학노드0. Runtime 상태는 다음 턴에서 새 probe로 확인한다.

게시 보고서의 known byte mismatch2개는 exact preimage에서 원본 hash로 복원됐다. 원본 archive와 예상 identity·물리식·허용오차는 바꾸지 않았다. 복구 ZIP은20개 원본 archive+20reports+exact28kernel overlay+receipts이지 전체 repo/wheel의 대체물이 아니다. 재현은 verified repo checkout 후 Python3.13에서 scripts/assemble_nonperturbative.py --check와 scripts/validate_research_integration.py를 실행한다.

다음 과학 실행은 사용자가 요청할 때 BF3-D만 진행한다. Positive periodic lapse에서 inverse phase-space mapping으로 final x의 local source를 구성하고 coordinate collision rate=N(x)n_e_star sigma_T c를 지킨다. Global coupled phase Jacobian과 local angular weight를 혼동하지 않는다. 기존 exact collisionless equilibrium과 Killing-energy balance를 재사용한다. Einstein feedback, generic tilt, spectral-domain certification, native Rust는 별도의 남은 의무다. Main/owner 및 기존 draft PR을 자동 merge하지 않는다.
