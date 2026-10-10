# REI-ACCEL01 repo별 반환 — bass

2026-10-10. N4는 실제 z20→4 reduced history의 새로운 proper-time cell schema를 소비합니다. 전체16384개 cell CSV는 final raw archive에 포함되고, 기존 REI snapshot schema와 구별해야 합니다. native fixed_time_optical_depth/visibility adapter 실행은 다음 node이며 아직 수신 완료가 아닙니다. BASS132/136의 sibling 모듈/의존성을 정확히 조합하십시오. 같은 proper-time 경계 tau는 방향독립; observed-z 비교에는 null-covector endpoint inversion과 observer tail이 필요합니다.

실제 계산: mean-volume z20→4+, 최종14개 경우×16384steps. FLRW z50=7.32839548, z90=6.28138267, tau_segment=.03744182127. r_i=.1의 delta tau=-2.61122e-5. 독립판정 PROMOTE_SCOPED_REDUCED_HISTORY; full native CR/RCT/HH/thermal HOLD.

[중앙 보고서·DAG·재개파일](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/7530e0239a4d30e99bfeba68d4b4ddc0b78a2c18/research/broad_history_20261010) · [REI draft PR104](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/104).

본 repo의 마지막 실제 source pin: `220d765f1df3803e6d4e3e3ad92d31ff421165ec`. 이번 commit은 연구계획/입력 포인터만 additive로 게시합니다. 생산 연산자·gate나 기존 owner branch는 변경하지 않습니다. 다른 비공개 채팅 스레드의 실행 ACK가 아닙니다.

다음 node: N4. 변경 없는 옛 suite를 반복하지 말고 해당 node의 실제 source/코드/출력을4시간 단위로 checkpoint하십시오. 전체 원자 연구 완료로 해석하지 마십시오.
