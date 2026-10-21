# S9 연구 전 관련 GitHub·클라우드 새 결과 확인

확인 종료: 2026-10-19 12:54 UTC. `physmath-research-loop`의 사용자가 직접 지정한 내장 규약 1.0.0을 적용했다. 실제 연구 실행은 0회이며, 이 문서는 읽기 전용 intake의 완료 기록이다.

## 결론

**BASS PR174에는 알려진 S8 Stage2 게시본 이후 새 외부 실행 결과가 발견되지 않았다.** 현재 branch/PR HEAD는 `2e6b4a150559b0bea52938896a901f6d438f3582`, draft/open/unmerged이고, 최신 댓글은 [6267055749](https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6267055749)이다. GitHub와 두 provider의 최신 archive 이름·크기·ID가 기존 Stage2 receipt와 일치한다. 이 intake에서 기존 S8 계산이나 archive 복원을 반복하지 않았다.

관련 REI 저장소에는 새로 완료된 연구 결과가 있으므로 다음과 같이 읽고 분리했다. 고정된 실제 BASS spectral owner `rei_bianchi@0e25846433170d0f420c4cda44a0bedbf02cd177`와 57개 owner 파일의 교체는 없다.

| 관련 연구 | 확인한 실제 결과와 현재 상태 | BASS에 전달하는 내용 |
|---|---|---|
| [REI PR206 BR05](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/206) | HEAD `00e89bce3060516083d63edb857f1294ee560ea0`; scientific source `3588027e41937f331680ab3e5c09de2f327db524`. 새 native history 1회, 16/16 steps, 41.917961863 s. | 기존 cohort·birth geometry·spectrum·direction·weight identity를 보존하는 관측 monitor와 time/birth refinement를 분리하는 비교 설계. |
| [REI PR199 age envelope](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/199) | HEAD `0ae749e9fdb179729c018706dbd59c4f61732b6a`. age64는 완료된 NCP 근거를 재사용하며 새 age32는 READY이다. 새 age32 완료 결과는 발견되지 않았다. | 고정 양의 support에서의 subnormal 정수 단위 장애를 물리적 infeasibility와 구별한다. 해당 lane의 48-thread NCP 설정은 BASS에 가져오지 않는다. |
| [REI PR198 V14](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/198) | HEAD `fa9615a565a10a770eb1768d8f10cd503b0e1336`; 새 SSPRK2 targeted tests 14개, transport 52 rows, coupled 16 settings. | stage CFL과 gas solve admissibility를 분리하며, 짧은 구간의 `log1p((a_end-a_begin)/a_begin)` clock과 ledger의 실제 accepted dt 결합을 참고한다. |
| [VigilODE PR71](https://github.com/cosmosapjw-quantum/vigilode/pull/71) | 별도 intake agent가 새 benchmark publication `ac1cd2a4738c2441c92e5fdae5f70aba35e53544`와 두 run의 source/CSV SHA를 확인했다. | 정확한 실행 source와 benchmark 내용을 별도 VigilODE intake에 연결한다. 현재 CI의 `C2_RED`는 새 solver benchmark 실행으로 세지 않는다. |

BR05의 r4→8 crossed differences는 앞선 r2→4에 비해 photon number/mean age/second age moment/q2에서 각각 약 0.09604/0.07751/0.08561/0.08282로 줄었다. 이는 정해진 한 rectangle의 결과다. 동시에 별도 photon geometry-work discrepancy 약 `2.435e-6`가 남으며, native 전체 energy ledger의 작은 residual로 이를 승인하지 않는다. 이 내용은 `SCIENCE_RESULTS.json`, `VERIFICATION.json`, 다음 handoff와 final receipt의 실제 원문에서 읽었다.

V14의 짧은 physical GL2 구간에서는 finest self-difference 지수 약 2가 보고되며 HeIII order는 numerical-resolution HOLD이다. 이 결과를 BASS의 현재 collisionless source나 full reactive/Einstein accuracy로 이전하지 않는다. V14 최종 archive의 Dropbox raw restore는 upstream receipt에서 확인되지만 Drive 상태는 `UNKNOWN_NO_ACK`이다. 새 exact filename query에서도 indexed object를 찾지 못했으므로 그 상태를 유지했다.

## 클라우드 확인 범위

Dropbox `/BASS_BACKUPS`의 descendant 포함 48 entries는 `has_more=false`였다. 새로 발견한 관련 REI backup roots, `/ode_solver`, VigilODE bootstrap 및 28개 관련 cosmology dossier 하위 폴더를 실제로 목록 조회했다. Dossier root 자체도 6 pages, 3,238 entries까지 cursor를 소진했다. 전체 관련 folder receipt는 Dropbox 42개이며 275개 고유 object ID를 기록했다.

Drive `/BASS_BACKUPS` root 46 entries와 모든 관련 하위 폴더를 읽었다. 관련 REI root의 첫 100개 포화는 `top_k=1000`으로 다시 조회하여 실제 112개 전체를 확보했다. 관련 folder receipt는 Drive 54개이며 397개 고유 object ID를 기록했다. 별도 dossier root는 modified-time 내림차순 최신 1,000개를 확인했고 마지막 시각은 2026-09-26이다. 순서와 신선도 cutoff 통과를 검증했다. 이 별도 root의 모든 오래된 archive를 열거나 전체 계정의 역사적 목록을 소진했다고 주장하지 않는다.

두 provider에서 발견한 BR05 full archive는 76,033,888 bytes, SHA256 `53fa8c74664213b369449b9676c41969f0dda9ff6f22e3d738a24ebf59dc42bd`이다. Drive ID는 `1ZUwhKjkBe6mYy34QywzHTjh5Hm4E5SOh`, Dropbox ID는 `id:BSpOijBcT10AAAAAAD_QzQ`다. 이번에는 fresh metadata와 Git 원문 receipt를 읽었으며 이 76 MB ZIP을 다시 내려받지 않았다.

새 age-v5 delivery confirmation JSON은 Drive `1KC915g-cLYx38fAGssxPPOhDmBoV0kh1`에서 **실제 전체 17,287 bytes를 읽어** SHA256 `d7d7745af7ec85c90df2cba5bd033b691ee28d069db8364d03c02d84e19c4c51`, JSON과 final HEAD를 검증했다. 원 raw base64는 intake JSON에 보존했다. 관련 Git 원문 7개, 190,198 bytes의 SHA256과 Git blob SHA도 독립 계산하여 일치했다.

VigilODE cloud 검색에서 Dropbox의 2026-10-16 `/ode_solver` dump와 2026-08-19 bootstrap만 발견했고, 현재 PR71에 대응하는 새 archive는 찾지 못했다. Drive의 정확한 name filter도 결과가 없었다. 별도 BASS_HE HE29 metadata는 발견했으나 다른 atomic lane이므로 content나 owner를 가져오지 않았다.

## 실패와 종료

일시적으로 read-only local command가 실행 전 `/tmp` sandbox marker 생성의 ENOSPC로 종료101을 반환했다. 한 번의 진단 재시도는 exit0이었으며 파일 삭제나 권한 변경은 하지 않았다. Drive의 최대 page size 1000 오류는 해당 범위로 교정했다. Dropbox 검색이 file/date filter를 충족하지 않은 반환을 보여 부재 결론에는 직접 folder listing만 사용했다. 이들 환경·도구 의미론 문제는 과학적 실패로 세지 않았다.

기존 정책 attachment 5개는 원 SHA256과 일치하여 S8의 실제 정책 검토를 재사용했다. 새 native 실행·옛 테스트 재실행·외부 게시·owner 수정은 모두 0이다. **열거한 관련 source/backup 범위의 fresh intake가 완료되었으므로, parent는 이 근거를 사용해 S9 유도·구현을 시작할 수 있다.** BASS 추가 worker≤16, RAM16GiB, disk4GiB, job1800s와 draft/production 범위는 유지한다.

상세 ID·파일명·크기·pagination 범위·읽은 원문·SHA256은 `FRESH_RELATED_INTAKE.json`에 있다. 기존 S8 final publication의 마감은 parent가 이어서 처리한다.
