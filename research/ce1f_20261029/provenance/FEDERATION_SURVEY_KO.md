# BASS 관련 저장소 현황 조사 — 2026-10-29 KST

조사 대상은 BASS가 실제로 참조하거나 최신 통합 논의에 등장한 여섯 저장소다. 읽기 전용 조사이며 외부 변경, 계산 재실행, 새 물리 입력 채택은 0이다. 캡처 시각 2026-10-28T22:56:08.407Z. 본문에 인용한 테스트·백업 결과는 해당 원격 산출물에 기록된 과거 실행이며 이 조사에서 새로 재현한 결과가 아니다.

## 조사 범위와 완전성

- BASS_HE: 현재 branch refs 119개 / 2 API pages; 전체 PR 103개, 최대 번호 #103.
- bass_cr: 현재 branch refs 197개 / 2 API pages; 전체 PR 118개, 최대 번호 #118.
- rec_bianchi: 현재 branch refs 171개 / 2 API pages; 전체 PR 153개, 최대 번호 #153.
- rei_bianchi: 현재 branch refs 302개 / 4 API pages; 전체 PR 258개, 최대 번호 #259.
- htt_base: 현재 branch refs 297개 / 3 API pages; 전체 PR 561개, 최대 번호 #564.
- WU088_HH: 현재 branch refs 163개 / 2 API pages; 전체 PR 154개, 최대 번호 #154.

합계 **1,249 현재 branch refs, 15 branch API pages, 1,347 고유 PR 기록**. PR은 created 역순으로 검색해 최종 빈 경계까지 진행했고, 번호 공백 4개는 issues endpoint를 실제 조회하여 일반 issue임을 확인했다: REI#60, HTT#1/#445/#448. 검색 결과의 두 번째 페이지부터 일부 기록이 issue_number와 null created_at 형태로 반환되는 것을 발견했다. created:<null 두 요청은 실패로 보존했고, 경계 PR의 원래 created_at을 별도 GET하여 계속 열거했다. 최종 PR 번호 범위 내 누락된 PR은 확인되지 않았다. branch와 PR 목록은 캡처 시점의 정적 현황이며 모든 커밋 전체 역사나 모든 과거 과학 실행을 검사했다는 뜻은 아니다.

원자료는 raw/의 모든 API 응답, all_branches.json 및 all_prs_completed.json. 기본 브랜치 최근 commit 검색은 연구 branch의 최신성을 나타내지 않으므로 해당 결과를 별도 표기했다. 각 저장소의 latest PR 본문 및 아래 9개 직접 관련 head commit과 handoff를 읽었다.

## 현재 중요한 heads

| 저장소 | 최신 관련 출처 | 정확한 source SHA | 확보 범위 및 남은 연결 |
|---|---|---|---|
| BASS_HE | branch research/he-nonthermal-d-birth-20261029 (PR 없음) | 9044ef53762f1985eb0be1aaa4127cc11dfc094c | source-only conservation ledger checkpoint. 직전 PAIR_COUNT15 ffe384d06e6b300d2a7ef2adbaa7a50351c4e6ce의 iid marked-count covariance를 재사용. 실제 사건 정규화와 named nonthermal D pool 미해결. |
| BASS_HE | PR103 research/orchestration-blockers-20261028 | de6bcbd95d25f9686997ad7eadbd62ea4e917d59 | 조건부 15 daughter rows, WU a3c6802c28be2207de210737940e1a847adf09c6 H–Li registry. catalog는 rate/species admission과 별도. |
| bass_cr | branch research/cr-crossbudget-frontier-20261029 (PR 없음) | bdc7bf6f4e9cc94d68c32e1752c62de5f809b0bf | conditional exact LP frontier dmax(c)=(L+M(c))/2의 증명, small-instance oracle. 실제3201 native input 재사용/재계산 없음. |
| bass_cr | PR118 research/cr-native-samebin-capacity-20261029 | 0fb1551b26cff387b947d4c5cf46e684b2453b2e | K3 conditional source bound, 315 primal events, native capacity certificate. RESOURCE_BUDGET_FAIL>=20.45/20 CPU-s, R6/C9 distinct-author 미실행. 18/20, central28/88 delta0. |
| rec_bianchi | PR153 research/rec-hd-print-precision-20261029 | 67d8baa092f18b7c1bbf8dfe9e255f8b43b45998 | printed-literal energy/frequency nearest-rounding gate 7/8 fail. CDMS-v2 raw+conversion lineage 미취득. 18/20, central28/88, physical0/313. |
| rei_bianchi | PR259 research/rei-figure-set-20261029 | 99dd121296112e93494e635a0a2469215556917d | saved17-state histories10vector figures. 새 IVP0. corrected raster QA3/10; cumulative budget overages preserved. working33/88, central28/88, physical-fast4/7. |
| rei_bianchi | PR258 review/rei-pr257-r6c9-parent-qr-20261029 | d6657071ea0e36a1b2643cb3df990e4b1faa855a | same-author independent algorithm/CAS only. receipt explicitly keeps genuine distinct-author R6/C9 NOT_RUN; textual provider backups are not source ZIP bytes. |
| htt_base | PR564 research/htt-converged-deliverables-20261028 | cab89d25af52a1b978a4da8c11eecdc25bb22759 | finite report convergence and controller queue options. Current PR metadata closed/merged at2026-10-28T14:31:39Z into research/htt-adaptive-methods-20261023; deleted head absent from current branches. Source commit accessible. Original42 acceptance nodes/six papers preserved;273 cards/600 edges are a separate operational registry. |
| WU088_HH | PR154 research/wu-hd-thermal-projection-r17b-20261029 | 31d3270ef210ef6659915105358f8fdbf8dae5a0 | GL2022 conditional exact rate projection, sum weights5. Native state-rate source rows and certified HD energies missing. WU33/48, R17B18/20, separate-author R6/C9 remain open. |

## BASS와의 실제 코드 연결

BASS main9c6506e4e2087129a8b674ff10438e5db1a55c9d와 CE1-Ea05906527d7dd5e5f6a653a0e4f7d977679d4a0c의 **전체 _rustcore/Cargo.toml을 읽어** 동일 pin을 확인했다.

- REC = d3cc6e0120061f113d28e7a3a55a2e3dd561e81e.
- REI = 1bda1e8cea7629d31f905e126ba47ec3b3c1d0d8.
- main docs/forward/rust-microphysics-20260930/CHILD_DEPENDENCY_LOCK.json은 EXACT_GIT_REV, branch_only_dependency_allowed=false와 fixed-input implementation review 범위를 명시한다.

따라서 최신 REC/REI 연구 branch 존재는 현 BASS compiled dependency의 교체를 뜻하지 않는다. HE/CR/WU 새 결과도 CE1-E collisionless massless Bianchi-I 경로의 물리 RHS에 자동 투입할 근거가 없다. 서로 다른 DAG9/15,28/88,33/88,33/48 및 local18/20은 그대로 별도 관리한다.

## 백업 수준

PR 본문과 직접 handoff/receipt를 읽어 다음 범위를 확인했다. 이 조사에서는 cloud 원본을 다시 다운로드하지 않았다.

- CR118 SOURCE/CLOSEOUT 양쪽 upload ACK, Drive full-original/member-SHA/CRC PASS 기록; Dropbox size+provider content_hash 일치, whole-byte GET 미완료. 과거 단계별 dual checkpoint gap 유지.
- REC153 새 source ZIP108154bytes SHA2562eb9d72dc3419a847c16beb3bca0065bb3a2765ea37c00af20734fbfc67e932e 양쪽 upload ACK; full-original remote SHA 재다운로드 NOT_RUN.
- REI258 R6/C9는 Google Docs+Dropbox Paper text content ACK/readback만 확보. source ZIP cloud-byte backup과 구별.
- REI259 pre-delivery snapshot 양쪽 ACK 및 후속 final receipt 존재; final report/handoff가 snapshot의 pending fields를 대체.
- WU154 original source ZIP119817bytes SHA2567c7fa69482adf455a929f64ff0a140c5a355bb2c3809c71cd7f8123d66a55627는 Library full reread 기록. Drive/Dropbox는 text-only handoff이고 source ZIP pair NOT_COMPLETE.
- HE103 source-including backups 양쪽 ACK 기록; original remote body reread NOT_RUN.

## BASS 다음 루프에 반영할 결정

CE1-E parent identity를 유지하고 scoped CE1-F 수학·구현을 진행한다. 새 연구가 필요한 angular-source uncertainty나 source-grid certificate는 CE1-E의 collisionless nonlinear Einstein geometry 계약에서 직접 유도한다. 반응률·열화·HD source choice·다른 저장소의 소진 예산은 이 단위로 이관하지 않는다. 원전·코드·독립 검토는 실제 수행 범위로 기록한다. 상위 DAG 완료수는 원래 node의 수용 조건을 충족할 때만 변경한다.

외부 서비스 mutation0, 과학 solver 재실행0, source pin 교체0. 이 조사 기록은 본 작업의 수집 근거이며 물리적 신규 성과로 세지 않는다.

