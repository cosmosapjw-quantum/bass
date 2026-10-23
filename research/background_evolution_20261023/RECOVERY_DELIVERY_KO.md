# 2026-10-23 게시 복구: 현재 상태의 진입점

중단된 원 연구의 과학 R1-R10 및 C1-C10은 이미 PASS_SCOPED였다. 이 후속 작업은 새 연구나 재적분이 아니라 게시 복구다. 원 source, raw, failure evidence 및 수용 기준을 유지한다.

## 불변 전체 패키지

- BASS_BACKGROUND_S2_20261023.zip
- 1465460 bytes, 153 payload files plus PACKAGE_MANIFEST.json
- SHA256: 2dd239da1c4e6130f2982e99b35ec2274d52f58fc99e94380a76ebc4c776119f
- Dropbox: id:BSpOijBcT10AAAAAAD_t3Q, /BASS_BACKUPS/BASS_BACKGROUND_S2_20261023.zip
- Drive: https://drive.google.com/file/d/1v6iIk8h11Zi078n5L4SsuX5idShTAk46/view
- Drive 파일은 BASS_BACKGROUND_S2_20261023.zip.b64.txt다. 원본 text를 다운로드한 뒤 base64 decode한다. native Google Doc으로 변환하지 않는다.

이번 재개에서 Drive의 전체 text를 실제 회수했고, decoded ZIP의 크기/SHA256, ZIP CRC, 모든 153 payload의 크기/SHA256 및 정확한 전체 inventory가 일치했다. 새 과학 적분, 기존 suite replay, 재렌더는 0이다. 이번 호스트의 Python/C++ 실행 probe와 원 연구의 과학 실행은 별도다.

## 게시 범위와 역사 보존

원 S2는 게시 직전 snapshot이다. 그 안의 delivery pending은 당시 기록이며 새 게시 성공을 소급해 넣지 않는다. 로컬 준비 commit 65dc7b509a1ac54218a018052ddec37d614ce9e5는 역사적 local identity다. 새로운 connector publication commit을 원 과학 execution commit으로 표현하지 않는다.

기반은 PR181의 797d66580448dad7fc41f2c2db31fe0eb37908bf이다. 다른 작업의 최신 main으로 바꾸지 않는다. 새 branch research/background-evolution-20261023의 생성 ACK를 확인했다. 현재 파일은 첫 복구 게시 checkpoint이며 후속 source/summary 및 최종 receipt를 같은 branch에 추가한다.

Git에는 직접 검토 가능한 실행 source, 이론/검증 요약과 복원 지도를 게시하고, 전체 원시 NPZ/PNG/CSV/과거 실패/조사 evidence는 위 불변 S2에서 유지한다. 따라서 Git-selected publication과 full-archive preservation을 구별한다. 원 전체 153개를 Git에 모두 게시했다고 주장하지 않는다. 파일별 실제 published inventory는 최종 receipt가 소유한다.

과거 독립 review receipt는 그대로 재사용한다. 현재 재개에서 새 독립 reviewer가 실행됐다고 주장하지 않는다. NCP/owner machine 과학 실행은 없다. main merge, force-push, 생산 default 활성화는 없다.

전체 목표의 다음 frontier는 G1 curved/tilted kinetic closure다. G2 full four-momentum exchange, G3 production/restart, G4 global physical-domain convergence는 여전히 열린 의무다. 현재 게시 복구가 이 의무들을 닫지는 않는다.
