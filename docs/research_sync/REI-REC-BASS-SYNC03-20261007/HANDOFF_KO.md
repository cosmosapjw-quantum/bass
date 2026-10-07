# BASS 수신 반환 — SYNC03

실제 F08 T0/T1/T2 × FLRW/BI 여섯 이력의 **112,000 셀**을 기존 BASS `frame`·`visibility`·`visibility_clock` 원문 모듈로 소비했다. Decimal70의 **784,054개 scalar 비교**가 통과했다. 이는 전체 BASS build가 아니라 정확한 source pin을 사용하는 별도 native 수신 실행이다. 이전 F08 receiver-pending 표시는 이 범위에서 완료로 갱신한다.

Loop1 검토·동기화 후 Loop2에서 T2의 `Δτ(BI−FLRW)=3.44222649358×10^-12`, conditional 구간 `[3.25112367913,3.63332930801]×10^-12`를 얻었다. 양의 부호는 고정된 binary stage density와 inherited gas boxes 아래 endpoint 선형 함수에만 해당한다. 연속체·물리적 EoR·관측 redshift 방향성을 인증하지 않는다.

소비 API pin은 `1e45e0f48cd83dcb21c23d4087fa5526195331d7`이다. 새 PR133 `1c5db6ddc32c16cacf4ef548f0f6839415ee950a`의 native Codazzi/import·zero-tilt frozen-frame gain·현재 build/CI 작업은 기존 담당자 영역이다. 이 반환은 그 코드와 전체 build를 건드리지 않았다. PR133의 로컬 scoped 결과와 fmt 단계에서 막힌 CI 이후 미실행 stage를 구분한다.

proper `cm^-3→m^-3` 변환은 한 번, normal-time `q=cσ_T n_e D`의 D도 한 번이다. 이 입력의 D는 1이다. finite slab tail 0과 외부 진단 tail 0.1을 명시했으며 실제 우주 observer tail은 주어지지 않았다. finite-temperature Thomson tail과 편광 operator admission은 별도다.

병렬로 준비할 일은 기존 short IGM 표의 단위·normal time·observer 경계를 명시한 read-only export 계약과 기존 slab 결과의 caller-owned tail 민감도다. PR133 gain/core·boosted clock·adaptive 연결은 기존 owner에게 남긴다. 변하지 않은 SYNC02 clock 검산이나 이번 여섯 이력 수신 실행은 반복하지 않는다.

중앙 패킷: https://github.com/cosmosapjw-quantum/rei_bianchi/tree/34765f5cc35169b5e8718571f3c01777cd28aec7/docs/research_sync/REI-REC-BASS-SYNC03-20261007

수신 실행과 저장소 게시 ACK는 별도 기록이다. 이 문서는 직접 채팅 thread에 썼다는 증거가 아니며 recipient ACK는 아직 확인되지 않았다.
