# S12: Rust 출생 기억 접선과 제한된 계산 최적화

2026-10-20 UTC / 2026-10-21 KST. 기존 S9/S10/S11 증거를 재사용한 새 C1–C10 한 단위다. 새 Rust 과학 source는 `f4cd0d53760783e6a58c3b0a98c64311ca489d28`, 검증 수리 source는 `4e3615dd75ff1a1efc2792edb3ba5b702a8a9b06`이다. 이후 orchestration·관측기·배송 commit을 이 과학 source와 혼동하지 않는다.

## 현재 관측 결과

| 단계 | 실제 상태 |
|---|---|
| C1 최신 대조·계약 | e48e0d56. 최신 PR/refs/대화와 Dropbox·Drive의 관측 범위를 대조하고 중단된 S11 최종 게시를 복구 |
| C2–C3 유도·수치 map | full birth-memory tangent와 exact augmented Jacobian, Wolfram51개 항등식, SciSpace·Exa 원문 대조 |
| C4–C5 구현 | 사전 등록한 물리 gate·실패·자원 정책, Rust build147.60초 PASS |
| C6 새 샌드박스 검증 | core269/269, history72/72, 수리 후 infrastructure14/14 |
| C7 동일 정확도 성능 | fused paired median1.372535배; 4case/2worker1.218038배,32개 raw output identity |
| C8 확장 실행 준비 | 고정81개 입력 파일,17job NCP DAG, 게시 후 launcher19/19·집계기62/62; 실제 NCP NOT_RUN |
| C9 독립 검토 | 물리585/585, support565/565, 그림79/79, provenance23그룹+별도5그룹; 범위별 보고서 보존 |
| C10 배송 | 단계별 Git·Dropbox 전체 readback; 최종 containing metadata는 외부 배송 댓글, 새 Drive pending, 실제 NCP NOT_RUN |

자세한 결과·실패·수치·그림은 상위 `S12_RESULTS_KO.md`와 `evidence/`, `independent_review/`를 따른다. 현재 DAG와 provider별 배송 상태는 상위 `DAG.json`, `RETURN_TO_CHATGPT.json`, `PUBLICATION_CLOSEOUT.json`이 요약한다.

## 물리 계약과 구현

Non-tilted axisymmetric Bianchi I, `(-,+,+,+)`, `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, `s=dot b`, `Sigma=sqrt(3)|s|/H`를 유지한다. owner는 `0e25846433170d0f420c4cda44a0bedbf02cd177`으로 고정한다. 새 명시적 등방 birth quadrature만 보정하고 기존 photon field·physical anisotropic stock·old birth weights를 보존한다. 음수 물리 weights와 tolerance 완화는 허용하지 않는다.

기존 S9/S10 state JVP는 고정 bank 계약에서 유효하다. 새 Rust client는 각 출생에서 `B_j`, `mu_theta`, `alpha_theta`를 저장하고, 현재 기하 미분과 과거 birth-memory forcing을 분리한다. 아래 왼쪽 block을 포함한 전체6상태 Jacobian과 explicit-x/자율 clock 열을 구현했다. 현재 theta는 초기 shear y0이며 event 좌표·donor amplitude는 고정한다. source-frame GL b0 gauge를 별도로 검증했다. moving event와 parameter-dependent donor normalization까지 승인하지 않는다.

## 원 native case의 실행 admission 변경

원 `CONTRACT.json`의 single native16birth 실행 계획은 C1 당시 사전 등록 기록이다. 이후 완료된 raw support의 exact 검토에서 **birth13–15가 기존 P2/P4·정규화 gate에도 불가능**함을 증명했다. birth13의 `max(mu^2)=0.5908471918238073`은 양의 P24에 필요한3/5보다 작다. 모든 finite-support moment-polygon facet도 exact rational로 검사했다. 원 birth11의64개 mu는 실패 raw와 bit 단위로 일치하며 weights를 다시 계산하지 않았다.

따라서 원 고정 `b9_n64_P2P4`16birth case는 NCP 실행 목록에서 제외했다. `native_followup/run.py`는 archival verification/compile-only 용도로만 남기고 일반 history 실행을 거절한다. birth11 precision repair가 뒤쪽 support 불가능성을 없애지 않는다. 새 support refinement는 별도 물리 계약이 필요한 다음 연구다. 이 결론을 모든 n64 또는 새 Rust extended history의 불가능성으로 확대하지 않는다.

## NCP와 백업

`ncp/launch.py`는 `SCIENCE_BINDING.json`과 별도의 `DELIVERY_BINDING.json`, `JOB_TEMPLATE.json`을 확인하고 자동 private toolchain/build·실행·exact-PASS resume·return ZIP을 처리한다. 한 번 봉인한 worker 수와 source/input identity를 재개 시 변경하지 않는다. 실제 affinity/quota·가용 RAM·기존 부하를 관측하며, 기존 owner 작업에 signal하지 않는다. 최대 요청64CPU/128GiB, 개별 job1800초, 전체 작업 disk4GiB다. 실행 주체용 안내는 `ncp/README_KO.md`를 따른다.

현재 원격 도구의 첫 config 호출은 월 quota와 명시적 재시도 금지를 반환했다. 새 NCP remote process는0회이며 현재 hardware identity도 관측하지 못했다. 2026-10-15의 완료 NCP64 결과를 새 결과로 쓰거나 미완료 작업으로 재실행하지 않는다.

S10의 양쪽9ZIP+최종 JSON 검증은 그대로 완료다. S11/S12의 새 Dropbox readback은 별도로 기록한다. Drive write의 응답과ID를 받지 못했으므로 새 이중 배송을 완료라고 쓰지 않는다. 추가 write 또는 우회 재연결을 하지 않는다.

## 남은 의무

실제 MD14 정규화/native Einstein·shear shared-Q, evolving reactive full finite-bin spectral history, 더 넓은 finite-d/angular 고차 moment와 P6의 적용 범위는 남아 있다. 새 Rust short manufactured full birth-memory 검증을 이 native 의무의 완료로 바꾸지 않는다. `5.369926725506957e-12`는 제한된 source-deposition 설명이다. P2/P4 일치만으로 continuum/full native finite-bin 보존을 승인하지 않는다. REI production·full EoR·merge로 확대하지 않으며 다음 최적화 단위를 자동 시작하지 않는다.
