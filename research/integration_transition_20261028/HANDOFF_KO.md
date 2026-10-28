# 통합 브랜치 재개 인계

BRANCH=integration/bass-nonperturbative-research-20261028
BASE_SCIENCE=937acea2875f199eebabaa1abcafd531a64035c3
OBJECTIVE=20개 연구보고서의 원문 보존 + 실제 bianchi 패키지로 커널 통합 + opt-in PolQState normal-time 충돌 연결
SCIENCE_PROGRESS=8/15_UNCHANGED
AUTO_NEXT=false

먼저 현재 branch HEAD와 CI_VERIFICATION.json/Actions 결과를 읽는다. 원본과 생성물의 identity는 CODEGEN.json으로 검증한다. 원문 보고서 20개는 reports/에서 순서대로 읽고, 당시 scoped 한계를 지운 채 production 완료라고 승격하지 않는다.

실행 경로: bianchi.nonperturbative.load_kernel(name, backend='python_oracle'); normal_time_collision_step(...); 실제 PolQState.collide_normal_time(dt_s,rest_rate_s,beta=...,panels=...,backend='python_oracle'). 마지막 경로는 fixed-geometry fixed-beta collision substep이며 기존 Strang/model/native-default 경로를 대체하지 않는다. rest_rate_s에는 D가 포함되지 않아야 한다.

재현: Python3.13에서 scripts/assemble_nonperturbative.py --check, 이어 scripts/validate_research_integration.py. Optional dependency 부재와 물리 실패를 구별한다. 현재 native Rust/constructor 검증은 NOT_RUN이다. 원본 과학캠페인은 전환 작업에서 재실행하지 않았고 regression tests만 패키지 연결에 맞춰 실행했다.

다음 과학 연구는 BF3-D 후보만 유지한다. Inverse phase-space mapping으로 final x의 local angular source를 구성해야 하며 BF3-C의 global coupled Jacobian을 local angular weight로 대체하지 않는다. 좌표시간 collision rate는 N(x)*n_e_star*sigma_T*c다. 새 연구 요청 전에는 실행하지 않는다.

이 별도 브랜치를 main/owner에 merge하거나 기존 draft PR을 자동 merge하지 않는다. 수정은 package API와 focused tests를 통해 진행하고 원본 reports/archive를 소급 변경하지 않는다. 임의 runtime 실패는 다음 세션으로 상속하지 말고 실제 probe한다.
