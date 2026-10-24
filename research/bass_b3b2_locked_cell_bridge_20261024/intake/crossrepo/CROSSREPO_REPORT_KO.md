# BASS B3b2 외부 네 저장소 조사 — runtime loss 이후 새 관측

**이 파일은 08:xx UTC의 새 관측이다. 잃어버린 05:03 UTC의 전체 inventory를 같은 바이트로 복구한 파일이 아니다.**

기존 공유 scratch 경로가 사라진 뒤 2026-10-24 08:29:10 UTC의 실제 probe에서 이전 crossrepo_intake/reviews 디렉터리가 모두 없음을 확인했다. 이 child의 이전 census store도 남아 있지 않았다. 부모가 별도 read-only full metadata 재조사를 승인했고, 원래 조사와 구분하여 수행했다. 원인은 이 조사에서 확정하지 않는다. 과학 실행·IVP·과거 campaign replay·archive 재다운로드·외부 쓰기는 모두0이다.

원래 05:03:24 UTC 조사에서 관측한697refs/562PR, 정책 및 HEAD, source10/10 byte identity 확인 기록은 PRE_LOSS_OBSERVATION_WITNESS.json에 transcript witness로 남긴다. 기존 전체 행 바이트는 NOT_RECOVERED다. 이번 전체 현재 행은 CROSSREPO_CENSUS.json에 새로 보존했다.

## 완전한 현재 metadata 범위

메타데이터 관측 종료: 2026-10-24 08:32:17 UTC. 선택 source 읽기 종료: 2026-10-24 08:33:05 UTC. KST는 UTC+9다.

| 저장소 | 현재 branch | 현재 PR | Open / closed | Branch 페이지 | PR 페이지 |
|---|---:|---:|---:|---|---|
| BASS_HE |101|96|96 /0|100,1|50,46|
| rei_bianchi |266|224|210 /14|100,100,66|50,50,50,50,24|
| bass_cr |180|102|101 /1|100,80|50,50,2|
| WU088_HH |152|143|143 /0|100,52|50,50,43|
| 합계 |699|565|550 /15|모두 소진|모두 소진|

각 저장소의 이름/PR번호 중복0, API실패0이다. 이는 현재 provider-visible branch와 open/closed PR 전수 metadata이며 모든 branch의 모든 파일·비공개 대화·백업 내용을 전수 열람했다는 주장이 아니다. 앞선 관측보다 branch2개, PR3개가 늘었다.

## 최신 중앙 정책과 변하지 않은 BASS 계약

- 현재 중앙 PR222 / research/orchestration-sandbox-20261022 HEAD: 9f410bf0f4b5d14d1e6b7c17cd2e23a916f241c9.
- 현재 AGENTS blob429a5a13ee75b1222bc50627f8d5973d01dd21c4: 원래 관측과 동일.
- fixed authority0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17의 BASS handoff와 현재 같은 파일: blob55c86aabe97702d6b64631c5f24a9d1a9563820e로 동일.
- 현재 중앙 DAG blob3394c4da9836e3a4e8418165dc2324e3f7ccc833,40개 node. BASS B1–B5 plan_status는 여전히PROPOSED다. 이 저자 계획 상태가 최신 BASS owner의 완료된 결과를 취소하는 것으로 해석해서는 안 된다.
- 현재 BASS_HE AGENTS blob8119a57e3c9f7b8c22a3532c9f88e430df1cebbf도 이전과 동일하다.

중앙 최신 본문은 이전 N4 caloric admission 서술을 유지한다. 최신 HEAD에 담긴 HE/CR 관측은 실제 DAG를 별도로 읽어 확인했다. 원래 author contract, 다른 owner의 reservation 또는 중앙 state를 수정하지 않았다.

## 실제 새로 읽은 관련 결과

| Owner / HEAD | 이전 관측 이후 진전 | 과학 수용 범위와 남는 결손 |
|---|---|---|
| HE96 /32f9227a9abef814bb009a87272c44be74941163 | Jones–Madison54.4eV TDCS의2개 located joint coordinates와 exact normalization/contrast diagnostics. Science60cacdb740fa4dadcdcbff43b7ffcb52566e077d. PR body와 실제 CLAIM_GATE 읽음 | COMPLETE_SCOPED,14testmethods 및16printingcontrols PASS 보고. 부모HE-ANG SOURCE_INPUT_PENDING, physical_provider_admitted=false, full joint/event sigma/recoil 미공급 |
| HH143 /f4a6d5505c845a046e3b81d33a2992a239ab4c8b | S1 준비 상태에서2개 actual projected Wolfram certificate와 scientific PASS_SCOPED로 진전. 실제 current CONTRACT/EXECUTION_LEDGER 읽음 | Recovery1017+moments82=1099assertions 보고. Manufactured finite-family/reference 범위이며 physical nuclear kernel/rate/stopping 미공급. HH_R10OFF, productionNOT_ISSUED |
| CR102 /3acb6beca5de4f82fccff1673dbcac010c53cf24 | Native-knot CE killed-generator first-event8matrices/72RHS/24source rows와 독립C9 PASS 보고. Science896800b4511f323ad3f0b5372b4912fb4770ea98 | Conditional finite chain. FullN4/N5PARTIAL/OPEN, final bath heat/Maxwellization/global error가 아님. 초기 variable-shadow failure 및 v2의18probability failures 보존 |
| REI225 /47abc82646d0f92b12d4843abb770be9b3593a37 | REC133 stored h/2-h/4 history envelope 결과의 중앙 observation |759commoncells/314channels 범위. 원313targetquery coverage0/313, 독립 physical-reference uncertainty없음. REC-HISTORYPARTIAL/H5uncalibrated 유지 |
| REI222 /9f410bf0f4b5d14d1e6b7c17cd2e23a916f241c9 | HE/CR 등 중앙 observations 진전, CR N5 M2 delivery binding | 제한된 owner admission만 수용. 전체 coupling·production 완료가 아님 |

HE95의 이전2cb9f9176c2a1764bb8ceaf2392531a100eb6820와 CR101의b65befa5187d3e1e11574a98dcadd2032831de72는 그대로다. 이전 동일b65commit을 가리키던 CR resolvent branch는 이제3acb6...로 진전했고 PR102가 생겼다. 두 branch가 항상 같은 과학 결과라고 최신 상태를 오기하지 않는다.

HH의 이전 고정280ef... S1 ledger는 당시 공개된 preexecution 상태였으며, 새 f4a6... ledger는 실제 실행 결과를 담는다. 최초 미완료 PHYS85 2calls와 새2calls를 구분하고 cumulative4/remaining allowance0을 유지한다. Undefined-symbol/general warning과 Infinity::indet2건도 owner가 보존했다. Warning-free 실행으로 고쳐 쓰지 않는다.

HE96의 실제 CLAIM_GATE 파일에는 containing commit 시점의 D/E/B3 pending이 남아 있다. 최신 PR96 본문의 FINAL_B3_ACK_COMPLETE는 그 이후 실제 upload/readback 관측이다. 역사적 immutable file 상태와 후속 publication receipt를 같은 시점으로 합치지 않는다.

## Backup·publication ACK와 독립 과학 검증의 구분

| Owner | 게시 상태 | 최신 owner-reported backup | 별도 과학 경계 |
|---|---|---|---|
| HE96 |Draft/open/unmerged|B1/B2/B3 Drive+Dropbox upload 및 별도 metadata-size ACK. Local uploaded archive SHA는 제시되나 independent remote SHA256검증false|2 sparse TDCS 입력·정확대수만 수용, full physical providerfalse|
| HH143 |Draft/open/unmerged|Dropbox final ZIP/JSON 실제 GET 및 byte/SHA/CRC/payload/Git readback PASS 보고. Drive final ZIP NOT_DISPATCHED, 외부JSON UNKNOWN_NO_ACK|SciencePASS와 전달미완료를 구분;18/20scopedstage, 전역물리완료율null|
| CR102 |Draft/open/unmerged|Library+Dropbox canonical ZIP 및terminal actual-byteR3PASS 보고. Drive UNKNOWN_NO_ACK, terminalDriveNOT_ATTEMPTED|Finite-chainPASS와fullstoppingOPEN을 구분|
| REI225 /REC133관측 |Draft/open/unmerged|REC S1/S2 89/146payload의size/SHA/Git/CRC복원PASS 보고, 최종S3는REC별도receipt|Stored-historyenvelope와물리uncertainty/targetcoverage를구분|
| 이번 조사 |로컬 parent 통합용|외부 upload/publish0|새 metadata/source 읽기이며 타owner 과학·archive 독립재검증0|

위 시험수·Wolfram 결과·archive 복원수는 실제 검색한 PR 본문과 source ledger에 기록된 다른 owner의 보고다. BASS가 새로 그 계산이나 복원을 수행했다는 의미가 아니다.

## 실제 소스와 frozen bridge 영향

현재 중앙9f410...에서 axbi_q_advance.rs와 igm_state.rs를 다시 읽었다. Blob836e5b4e5587e86a32a8734d01b6989c3447343e 및437365fbe329a10afe292f9dd7eebf549fef804c로 이전과 동일하다. 전자는 frozen gas의 HI/HeI/HeII continuum absorption이며 후자는 gas fraction/thermal energy와 photon-count adapter다. 새로운2-level LINE01 bath 또는 occupation capacity를 공급한 것으로 읽지 않는다.

새 HE sparse joint anchors, HH reaction-selected moments, CR finite-chain CE, REC stored-history refinement는 다음 source-supplier 상태를 개선한다. 그러나 이미 고정한 BASS actual locked-cell snapshot bridge의 입력·단위·frame·N/T 역변환식을 변경하거나 그 완료 결과를 preparation-only로 되돌릴 근거는 발견하지 않았다.

HE96 본문은 REI L1의 HI photon-summary/isotropic/NO_DEPOSITION/zero-recoil 수용도 보고한다. 이 항목은 해당 본문의 타owner 관측으로만 취급한다. 실제 current central DAG의 REI-L1 원계획은PROPOSED이며, 본 조사에서 별도 L1 source acceptance를 재심사한 것은 아니다.

다음 finite LINE01 coupling에는 line-side boundary/history와 clock의 실제 결속, native/COM atomic-source ownership, gross emission/absorption과 실제 내부에너지 귀속을 별도 계약으로 닫아야 한다. 임의 donor, phase-space width, reservoir capacity 또는 clipping을 만들지 않는다. 새 직접 LINE01 finite absorption supplier가 이 네 저장소의 선택된 변경에서 완전히 수용됐다고 주장하지 않는다.

## 복구·진척·정지

현재 조사 DAG는 runtime probe → 손실/기존증거 구분 → 4repo terminalmetadata → changed5PRbody → exact10source → byteidentity → 다음edge판정 순서다. 본 단계들은 완료됐다. 원래697/562row snapshot의 raw복구는미완료이며, 현재699/565row census는완료다. 이 구분을 전체 조사완료나 과학완료율과 혼합하지 않는다.

remaining_campaign_wall_seconds=null, remaining_campaign_cpu_seconds=null, budget_reset=false를 유지한다. 34.1262904040002초는 부분 과거 합계라는 기존 해석을 보존한다. 전체 물리목표 완료율은null, merge0/productionactivation0이다. 새 관측 이후 futureHEAD를 반복 추격하지 않는다. 최종 expected-SHA 게이트는 부모가 해당 게시 직전에 수행한다.

별도 복구된 코드/그림 review와 probe는 reviews/RECOVERY_PROVENANCE.json에 원문 재구성 상태를 표시했다. 원래 승인codeSHA d88571cc...와 원래 probe wall/CPU를 보존하며, 복구 행위를 새 과학검증으로 집계하지 않는다.

