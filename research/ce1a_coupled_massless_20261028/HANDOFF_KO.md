# CE1-A 이후 재개

REPO=cosmosapjw-quantum/bass
BRANCH=research/bass-ce1a-coupled-massless-20261028
PR=228
VERIFIED_CODE_COMMIT=465cf9daaa8c720038d6d4cbf3e7ceea68d0ec33
PARENT=90b600519712939e3db123191dcaea0361fdea9e
CURRENT=CE1-A_COMPLETE_SCOPED
UPPER_CE1=PARTIAL
UPPER_DAG=9/15
NEXT=CE1-B_ONLY
AUTO_NEXT_NODE=false
PRODUCTION_READY=false
MERGE_READY=false

먼저 현재HEAD,README_KO,REPOSITORY_CI_STATUS,PRESERVATION을 읽고 불변ZIP의 REPORT_KO,OPERATOR_CONTRACT,DAG_UPDATED,SOURCE_MAP과raw evidence를 확인한다. Code commit 이후 closeout은 문서·요약6개만 추가한다. 실제 package bianchi.nonperturbative.einstein_vlasov를 사용하고 backend='python_oracle'를 명시한다.

Signature(-+++),u=t/Tstar,ell=ln a,h=Tstar H,E=8piG*Tstar²*rho_energy/c². Radiance는 c로 나누어 angular energy로 변환한다. Massless collisionless diagonal reflection-symmetric Bianchi I,Lambda0. 전체 초기 angular 분포를 보존하며 constraint를 매 스텝 사영하지 않는다. Direct P8는 reduced source를 호출하지 않는다.

Constraint C'=-2theta C; pressure-only injection이면 추가sum_i(theta-h_i)eta_i. Nonlinear error envelope는 directional h_i>=0의 invariant region과 실제 source upper bound가 필요하다. Fine-grid difference를 certified bound로 부르거나 contracting Kasner에 적용하지 않는다.

검증:15개 targeted tests 및 actual repo CI40676017862/job122774500345 PASS,installed-wheel coupled check PASS. Science1회,reduced14/directP8 2/constraint quadrature3. Replay0. 기존 결과 확인은 archive validate_saved.py를 사용한다. 과학driver는 기존 raw file이 있으면 implicit replay를 거절한다.

Current policy CI RF00 40676128349와 RF-BENCH40676128240 FAILURE. Root cause는 이번에 재감사하지 않았다. 부모의 export-contract/corpus-digest 의무도 보존하며 expected hash 변경/검사 비활성화로 통과시키지 않는다. Native CE1-A미구현,native subagent/독립모델심사NOT_RUN. Runtime는 다음 턴 실제 probe로 확인한다.

CE1-B는 같은채널의 continuous angular source 오차를 controlled bound와 연결해 nonlinear propagation 및 분리된 time-error budget을 구성한다. Arbitrary quadrature TV나 단순 finer-grid gap을 certificate로 쓰지 않는다. Generic collisions,tilted matter,full inhomogeneous Einstein,native production은 별도다. Main/owner/parent를 보호한 child branch에서 매단계 실제백업·게시와9/15 기준진척을 보고한다. 이 인계문은 자동 실행 지시가 아니다.
