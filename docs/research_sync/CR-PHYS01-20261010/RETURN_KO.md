# CR-PHYS01 수신·후속 연구 연결

2026-10-10. 실제 CR provider 부재를 조건부 성분 범위에서 해소했습니다. 이 저장소에는 동기화 문서만 추가하며 기존 물리 연산자와 gate는 변경하지 않습니다.

새 CR 성분을 받아 실제 REI history가 생성된 뒤 BASS136의 electron snapshot receiver에 새 source identity로 전달할 수 있습니다. 지금은 새로운 CR history나 Thomson/optical-depth 적분을 실행하지 않았습니다. 기존 CR-off warm17epoch receipt를 새 CR 결과에 재사용하지 마십시오.

공급원: [bass_cr PR24](https://github.com/cosmosapjw-quantum/bass_cr/pull/24), scientific commit `0522fac6dcaf1874974e2a59979aef88408a81e6`.
수신기: [rei_bianchi PR102](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/102), scientific commit `2fd4c5bd8a9cd5ada7718c179294c73dc6c0a1da`.

[연구보고서와 실제 source](https://github.com/cosmosapjw-quantum/bass_cr/tree/0522fac6dcaf1874974e2a59979aef88408a81e6/research/cr_phys01_20261010), 같은 경로의 HANDOFF.json/DAG.json/CODEX_START_KO.md를 참조하십시오.

선택 모델: 전체10keV–1PeV SN proton injection, 일정H/s Bianchi 수송, 실제1–4MeV H/He ionization channel, FS10 xi=.01 terminal yields, REI source·gas·geometry-bound local derivative. 실제 H/He 사건·heat·excitation이 비영이며 독립 리뷰는 PROMOTE / CONDITIONAL_PHYSICAL_COMPONENT_AVAILABLE입니다.

미해결 확장: secondary cascade delay, 임의 ionization fraction/temperature/helium abundance, 미포함 proton losses와 에너지 tail, state-dependent receiver 및 실제 IGM history. 원 FS10 생성YHe는 미복원이며 nominal.248 transplant는 근사입니다. 현재317year turn-on에 즉시 침적된 history를 주장하지 않습니다.

병렬 작업: CR-PHYS02-DELAY, CR-PHYS03-COMPOSITION, CR-PHYS04-LOSSES. 실제 history 뒤 BASS snapshot 전달. 원 정밀 원자/핵 lane은 별도 보존합니다. 이 파일은 repo handoff이며 다른 비공개 채팅에 직접 메시지를 전송했다는 영수증이 아닙니다.
