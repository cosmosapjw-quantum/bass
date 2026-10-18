# BASS PR170 이후 연구: 사용자 수동 파일 처리 없이 Git에서 직접 재개

현재 Codex 세션에서 아래 저장소를 직접 읽고 필요한 실행을 수행하라. 사용자에게 ZIP 다운로드, 첨부, SSH 명령 실행 또는 경로 설정을 요청하지 않는다.

Repository: https://github.com/cosmosapjw-quantum/bass
Draft PR170: https://github.com/cosmosapjw-quantum/bass/pull/170
Branch: research/bass-pr170-source-age-photon-stress-20261016
검증된 S4 구현 기준: 8a74a891ac40a9ceae1ba8c637b2df8d78e875dd
연구 경로: research/bass_pr170_photon_age_20261016/

먼저 최신 HEAD, PR 상태와 현재 작업 트리를 확인한다. 독립 worktree에서 RECOVERY_README_KO.md, DAG.json, RETURN_TO_CHATGPT.json, SCIENCE_REPORT_KO.md, REI_RECEIVER_CONTRACT.json 및 CODEX_NCP_HANDOFF_KO.md를 읽는다. 필요한 Python 의존성을 격리 환경에 직접 준비하고 `bash RUN_GIT_REPLAY.sh`, `python -m unittest -v test_prepare_git`를 실행한다. 원시 HISTORY.csv는 prepare_git.py가 Git의 압축 자료에서 정확한 해시를 확인하며 복원하므로 외부 ZIP이나 /mnt/data 파일이 필요 없다.

기준 검증은 과학 테스트 36개와 별도의 복구 테스트 3개다. 18개 원래 BASS 경우, 1170행 passive photon 진단과 source-only conditional old-radiation feedback을 보존한다. 재생성 차이는 byte identity와 numerical/scientific identity를 구별하고 원래 허용오차를 임의로 완화하지 않는다.

다음 연구는 우선 BASS의 non-tilted axisymmetric Bianchi I 범위에 둔다. 현재 S(x)는 manufactured bolometric source이고 광자는 collisionless passive tracer다. 실제 REI 소스에 맞춘 수신 계약을 연구할 경우 source per-H/per-second를 S(x)=j_proper/H로 바꾸는 단위, H와 proper n_H, 광자 에너지·방출시각·비등방 가중치를 원본에서 확인한다. photon number와 spectrum 정보가 없는 bolometric U,M만으로 광이온화 반응률을 복원하지 않는다. DeltaP=-(8/5)(Ub-M)은 1차 근사이며 유한 비등방 exact kernel은 birth-age 이력을 유지한다.

원래 Omega_r의 일부를 collisionless old stock으로 재해석하는 진단과 새 광자 공급을 구별한다. 이미 BASS 응력으로 생성한 b,H,s에 같은 응력을 두 번 더하지 않는다. 실제 native 연결은 독립 REI owner 브랜치에서 새 source identity/checkpoint와 대조실험으로만 수행한다. 기존 production 계산·checkpoint·미병합 PR은 변경하거나 재시작하지 않는다. Gas/emitter Q^a, 흡수·Thomson, H/He, polarization, full EoR는 실제 구현·독립 검증 전까지 HOLD다.

경량 계산은 로컬에서 한다. Native Rust 비교나 큰 검증이 필요한 경우에만 사용자 Ubuntu에서 `ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22`로 직접 접속한다. CPU/RAM/disk/Rust 버전과 진행 중 owner PID를 먼저 조사한다. 추가 worker<=16, RAM<=16GiB, disk<=4GiB, 개별 job<=1800초를 기본 상한으로 두고 중복 병렬화·기존 owner 작업과 자원 충돌을 피한다. NCP를 필요 없이 강제하지 않는다.

각 완료 단계에서 코드·실제 테스트·원시 결과와 실패를 보존하고 DAG를 갱신한다. Git commit/push 및 Draft PR 게시, Dropbox와 Google Drive에 create-only 백업 후 실제 다운로드 SHA256 검증을 수행한다. RETURN_TO_CHATGPT.json에 정확한 source/head/tree, 명령·exit code, 잔차 단위·분모·오차 한계, 재현성, 미실행 범위, 백업 영수증과 다음 첫 작업을 기록한다. 자동 병합하지 말고 문서만 작성하지 않으며, 실제 수행한 범위와 blocker를 구별하여 보고한다.
