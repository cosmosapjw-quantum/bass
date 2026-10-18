# Codex/NCP: BASS 등방 source 보정 후보의 제한된 compile/test

$physmath-research-loop를 사용하되 이번 실행은 준비된 Rust 후보의 컴파일·기존 5개 테스트와 재현성 기록에 한정한다. 사용자에게 파일 다운로드, ZIP, 첨부, 수동 명령이나 경로 설정을 요청하지 않는다. 현재 세션에서 GitHub와 인가된 로컬 환경을 직접 읽는다.

Repository: https://github.com/cosmosapjw-quantum/bass
Branch: research/bass-isotropy-checkpoint-recovery-20261018
검증할 연구 경로: research/bass_isotropy_response_20261018/
계보 기준: PR173, commit 4e2d1fa820d6f7baae1069b615fb82a08d53403b
원본 REI owner: 0e25846433170d0f420c4cda44a0bedbf02cd177

먼저 이 branch의 최신 remote HEAD와 현재 작업 상태를 읽고 독립 worktree를 만든다. README_KO.md, DAG.json, RETURN_TO_CHATGPT.json과 최신 게시 영수증을 읽는다. 원래 SourceLedger 58개 native 측정과 5개 negative control은 PR173에서 이미 완료됐으므로 불필요하게 반복하지 않는다. 새 `balance.rs`는 다른 코드이며 5개 작성된 테스트는 아직 실행되지 않았다.

격리 Python 환경을 직접 준비하고 requirements.txt를 설치한 뒤 `python -m unittest -v test_balance test_properties`를 실행한다. 기준은 15개 PASS다. 원본 hash를 먼저 검사한다:
- angular_balance.py SHA256 1ed6e5d9ea865684fda255055acac3c10efef5d0131118bc568260b0d55a21e9
- balance.rs SHA256 3053e69d6a501b8beb6c4640db7826af742a85693dabe9b6b8ea523790b93e8a

Rust가 있는 인가된 로컬 또는 필요할 때만 NCP에서 새로운 출력 디렉터리를 만들고 다음을 실제로 실행한다:
`rustc --edition=2021 --test balance.rs -o NEW_OUTPUT/balance_tests`
`NEW_OUTPUT/balance_tests --nocapture`
`rustc --edition=2021 -O balance.rs -o NEW_OUTPUT/balance_probe`

컴파일 exit0만 PASS로 기록하지 않고 정확히 5개 테스트가 실행됐는지 확인한다. Cargo나 native REI driver가 필요한 작업이 아니다. 최초 컴파일/실행 오류와 수정 diff를 남기고, 작은 호환성 수정 외에 물리 연산자·오차한계·테스트를 바꿔 성공시키지 않는다. Python↔Rust 입력 행렬 생성/검증을 새로 추가한다면 별도의 구현 검증으로 기록하고 실행 결과를 혼동하지 않는다.

NCP가 필요하면 사용자 Ubuntu에서 직접 `ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22`를 사용한다. 진행 중인 owner PID/affinity/디스크/메모리, `/root/.cargo/bin/rustc`와 실제 버전을 먼저 확인한다. 기본은 1 thread이며 추가 worker<=16, RAM<=16GiB, disk<=4GiB, 개별 job<=1800초. 기존 production 작업·checkpoint는 중단하거나 재시작하지 않는다.

후속 P4/응답 연구나 실제 source injection 보정은 이 compile/test 작업과 구분한다. 신규 등방 source만 대상이며 기존 photon stock, 물리적 anisotropic source 또는 native default를 바꾸지 않는다. H/He, Q^a, polarization, restart/EoR는 이번 범위 밖이다.

실제 source/HEAD/binary SHA, 명령, exit code, 5개 test 이름·결과, 환경·자원, 최초 실패와 수정 내역을 RETURN_TO_CHATGPT.json에 기록한다. 별도 결과 commit/push와 Draft PR을 만들고 Dropbox·Google Drive create-only 백업 후 재다운로드 SHA256을 검증한다. 자동 병합하지 않는다. 필요한 소스는 모두 이 Git 연구 폴더에 있고 사용자가 별도 파일을 제공할 필요 없다.
