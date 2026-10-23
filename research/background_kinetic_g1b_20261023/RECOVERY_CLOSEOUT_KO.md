# G1B 게시 복구 마감 및 다음 진입점

중단됐던 G1B의 과학 계산은 S2 안에서 이미 끝나 있었다. 이번 재개는 원본 복구, 저장된 수치 근거 확인, 누락된 실행기·유도문·결과 게시와 인계다. 새 IVP, moment 평가, 과학 시험군 재실행, 그림 재생성은 모두 0이다.

## 실제 확인

Google Drive에서 S2의 5개 part를 전체 회수했다. 각 part의 실제 Dropbox content hash를 계산해 Dropbox가 제공한 메타데이터와 일치함을 확인했다. 원본 ZIP을 순서대로 결합했고 219594596 bytes, SHA256 a2190d7eb88968278493640305304400e7c656dcab2deb2c41daf0fee077bc46, CRC, 정확한 목록 및 110 payload의 크기/SHA256가 모두 일치했다. Dropbox 전체 raw 다운로드를 수행했다고 표현하지 않는다.

원 verify_saved.py를 읽은 뒤 실행했다. 108 science-manifest hash, 정상 이력 18개, 저장된 비교 20건, source lock, 양의 가중치, 과거 실패 보존을 확인해 PASS_SAVED_EVIDENCE였다. 이는 새 적분이나 새 시험 수가 아니다. 그림 PNG3개를 직접 읽었고 재렌더하지 않았다. 별도 독립 모델 심사는 NOT_RUN이다.

원본 27개를 Git snapshot 67a0309536a7eb4e4eeb14cabe0a4c043c500ccd에 게시했고 원격 tree 687f498e7ecec0a066c2df40697f1c0d8777baef의 모든27 blob SHA1/byte size와 S2 원본이 일치했다. PR184는 부모 PR183에 대한 Draft다. main과 부모 파일을 바꾸거나 merge하지 않았다. 현재 source publication은 과학 실행시점의 commit이라고 소급하지 않는다.

## 전체 자료 복원

DELIVERY_FINAL.json의 parts를 order 순서로 읽고 같은 filename으로 다운로드한다. 임시 download URL을 저장하지 않고 provider ID로 다시 요청한다. 파일을 가진 directory에서 다음처럼 결합한다.

```sh
cat BASS_G1B_S2_a2190d7eb889.part0{1,2,3,4,5}.bin > BASS_G1B_S2_20261023.zip
printf '%s  %s\n' a2190d7eb88968278493640305304400e7c656dcab2deb2c41daf0fee077bc46 BASS_G1B_S2_20261023.zip | sha256sum -c -
mkdir restored_g1b
python -m zipfile -e BASS_G1B_S2_20261023.zip restored_g1b
cd restored_g1b
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python verify_saved.py
```

전체110 payload에는 원시 NPZ, 처음 실패한 source/traceback, reference 확인, 시험 로그와 그림이 있다. Git 선별27개를 전체 archive와 동일시하지 않는다. verify_saved.py는 raw와 SCIENCE_MANIFEST.json이 있는 전체 복구 directory에서 실행한다. Git source만으로 누락된 raw를 새 실행해 채우지 않는다.

## 연구 상태와 다음 행동

G1B S0/S1/S2 과학은 COMPLETE_SCOPED다. 원 DAG의 S2 배송 PENDING_FINAL_ACK는 동결 시점 기록이며 DELIVERY_FINAL.json이 현재 확인 수준에서 이를 마감한다. 전체 목표 완료%는 null이다.

다음은 G1C의 bounded-domain nonlinear error transport다. 공통 처방 배경의 tail bound와 두 self-consistent 해 사이의 오차를 구분하며, 저장된 18개 이력에서 source residual/sensitivity를 이용하는 경로를 구성한다. 일반 smooth tilted IC, 충돌·방출원 four-force, production/restart, 전역 정의역 인증은 별도 의무다. 현재 물리적 해석이나 code/tolerance는 수정하지 않았다.

먼저 최신 branch/PR184 댓글, DELIVERY_FINAL.json, HANDOFF_KO.md, REPORT_KO.md, THEORY.md, DAG.json을 읽고 최신 병렬 source delta를 확인한다. 완료 계산은 재사용하고, 현재 runtime은 새로 probe한다. 다음 단위의 실제 유도·구현·검증·백업을 구분해 기록한다.

## 별도 마감 패키지

BASS_G1B_CLOSEOUT_20261023_7ea2abe3d0ea.zip: 477408 bytes, SHA256 7ea2abe3d0ea838824d4a0f6ad26cdd5390b1d32de48332c99fd36c7bb7f8866. 51 payload와 manifest를 포함하며 대형 raw NPZ는 포함하지 않는다. 원본 코드·보고서·그림·manifest 및 전체 S2 복원 지도를 담는 소형 capsule이다.

Drive 1AqW3KSuUSq5NWTDnp5_oL8CzJ9knKO1v에서 저장 ACK 후 전체 raw 파일을 회수해 원본 바이트/SHA256/CRC/51 payload/정확한 목록이 일치했다. Dropbox id:BSpOijBcT10AAAAAAD_6Wg는 completed ACK와 477408 bytes가 일치했다. 이 소형 capsule의 Dropbox 전체 raw 다운로드는 NOT_RUN이다.

현재 문서의 실제 마감 시각은 2026-10-24 KST이고, 단위명과 원본 archive의 20261023 식별자는 그대로 유지한다. 생성 후 받은 provider ACK는 이 문서와 DELIVERY_FINAL 및 최종 PR 댓글에 별도 보존한다. 동결 capsule을 다시 쓰거나 그 안에 ACK를 소급 삽입하지 않는다.
