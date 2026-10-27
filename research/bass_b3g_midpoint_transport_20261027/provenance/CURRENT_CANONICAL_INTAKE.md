# 중단 후 현재 중앙 상태와 과학 결과 복구 확인

판정: **기존 과학 결과와 게시된 BASS 중앙 연결을 재사용하고 백업 전달을 계속한다.** 이 확인은 자료 복구 및 메타데이터 확인이며, 새로운 과학 실행이나 admission을 만들지 않는다. 관측 시각과 파일별 식별자는 동반 `CURRENT_CANONICAL_INTAKE.json`에 기록했다.

## 현재 중앙 상태

현재 중앙 HEAD는 `5abe0d19df95db730e3e33bae0373c81ba37ce89`이며, 기존 BASS 연결 커밋 `12f6007a83a40d76f80574e41a5402676e81fc7a`의 직접 자식이다. 두 커밋 사이의 변경은 CR_N5의 HeIII ground RR 부분 반환 연결에 필요한 다섯 경로뿐이다. BASS midpoint 반환 파일은 M2와 Git blob `e96c3a25bf93243f2545902c08adf0cf9d62bd8a`가 같다. 최신 AGENTS도 다시 읽었으며 blob `429a5a13ee75b1222bc50627f8d5973d01dd21c4`가 유지된다.

현재 DAG의 88개 노드, 15개 authority, 17개 integration edge를 확인했다. B3g, B3i, B2-G1C의 `status_observation`은 올바른 반환 파일과 JSON pointer를 가리키며, 관측값·계약·노드 계획·CURRENT_STATUS가 일치한다. 세 노드 모두 실제 BASS A2 커밋 `af14fc72d99f6d0e396f60aedadcdb5d05213280`에 연결되어 있다. 물리적 총오차는 `null`, L4_ready는 `false`로 유지된다.

**기존 선언 완료 수는 27/88이며 이번 복구나 BASS 부분 결과로 증가시키지 않는다.** 근거는 현재 `CR_HEIII_GROUND_RR_20261027.json`의 `/original_DAG/declared_deliverable_count`, `/original_DAG/nodes`, `/documents_checkpoint/central_completed_total`이다. 이는 기존 선언값의 재사용이며 88개 산출물을 새로 완료 심사한 값은 아니다. 현재 상태 문자열의 `COMPLETE` 접두사 개수 18과도 별도 지표다.

새 CR_N5 반환은 원소 He를 He4로 해석하는 조건부 He4III→He4II(1s) 복사 재결합 한 채널의 결과다. 부모 N5는 PARTIAL_OPEN이고 새 완료 수 효과는 0이다. 이를 다른 소유자의 부분 결과로 보존하며 BASS 예산이나 물리 admission으로 전용하지 않는다.

병렬 [PR237](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/237)은 draft/open/unmerged이며 HEAD는 `ee6746ab172f862dddfdec63b59e5e3707b59eaa`이다. 실제 저장 배경과 manufactured fast moments, 독립적으로 지정한 stopping frequency를 사용하는 조건부 25행 thermal source/JVP 결과이며 native finite Lyα 공급자가 아니다. 해당 분기의 32/88을 현재 중앙 27/88에 합산하지 않는다.

## 복구한 자료와 실행 예산

현재 HEAD에서 중앙 DAG, 다섯 계약, 다섯 노드 계획, CURRENT_STATUS, 두 BASS 반환의 **14개 파일**을 `central_b3g_20261027`에 복구했다. 모든 파일의 실제 Git blob을 검증했다. 1,592,174바이트 DAG에 대한 connector 응답은 내용이 비어 있었으므로, 고정 커밋의 raw URL에서 직접 읽어 기대 blob `a3963c01a11a72cb82cec9450c4dabfb4afccd18`을 확인했다. 이는 자료 크기에 따른 전달 공백이었으며 원본 소실이나 과학적 불일치가 아니다.

복구 담당자가 A2의 41개 파일과 동결된 다섯 코드·테스트 해시를 검증했고, 본 검토자는 과학 코드·계약·admission·원시 결과·그림·ledger·R9 기록 중 **21개 파일**의 SHA256 및 Git blob 일치를 독립적으로 확인했다. 이미 실행 완료된 tests/consume/plot 세 단계와 반환 코드 0을 그대로 보존한다. 원래 child CPU는 7.177914초, child wall은 7.245837689002656초, wrapper CPU는 0.130123초이다. 역사적 잔여 예산은 미상(`null`)이며 재설정하지 않았다. 이번 복구에서 새 과학 child 실행은 **0**이고, 복구 I/O 비용은 측정하지 않았으므로 0으로 주장하지 않는다.

기존에 사라진 ZIP은 원격 ACK 전에 소실된 별도 전달물이다. 그 ZIP 자체를 복원했다고 주장하지 않으며, 검증한 게시 원본과 현재 중앙 자료로 새 전달물을 만든다. 이 intake에서 중앙 원격 변경은 0회이다. 선택하지 않은 미래 공급자를 일괄 선행조건으로 추가하지 않는다.

## 고정 출처

- [현재 중앙 DAG](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/5abe0d19df95db730e3e33bae0373c81ba37ce89/research/orchestration_expansion_20261025/DAG.json)
- [현재 BASS midpoint 반환](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/5abe0d19df95db730e3e33bae0373c81ba37ce89/research/orchestration_expansion_20261025/returns/BASS_B3G_MIDPOINT_TRANSPORT_20261027.json)
- [완료 수와 새 CR_N5 반환](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/5abe0d19df95db730e3e33bae0373c81ba37ce89/research/orchestration_expansion_20261025/returns/CR_HEIII_GROUND_RR_20261027.json)
- [게시된 A2 연구 단위](https://github.com/cosmosapjw-quantum/bass/tree/af14fc72d99f6d0e396f60aedadcdb5d05213280/research/bass_b3g_midpoint_transport_20261027)

추가 증거: 동반 JSON의 파일별 복구 proof, `delivery/RECOVERY_INVENTORY.json`, 보존된 `results/EXECUTION_LEDGER.json`. 과학 범위 및 오차 해석은 기존 ADMISSION과 R9 검토를 그대로 따른다.
