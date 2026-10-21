# Codex/NCP: BASS PR174의 기존 Rust 후보 실행

$physmath-research-loop로 아래 한정 작업을 직접 수행해. 사용자에게 다운로드, ZIP, 첨부, 수동 명령이나 경로 설정을 요청하지 마.

Repository: https://github.com/cosmosapjw-quantum/bass
Draft PR174: https://github.com/cosmosapjw-quantum/bass/pull/174
Branch: research/bass-isotropy-checkpoint-recovery-20261018
검증된 구현 commit: 930406550ce6d4d1b2e87f016c5c18fba48c4ccd
연구 폴더: research/bass_isotropy_response_20261018/
계보 PR173: 4e2d1fa820d6f7baae1069b615fb82a08d53403b

먼저 백업과 GitHub에서 더 새로운 실행결과가 있는지 확인하고 독립 worktree를 준비해. README_KO.md, DAG.json, RETURN_TO_CHATGPT.json, PUBLICATION_CLOSEOUT.json과 최신 PR 댓글을 읽어. Git-only checkout에 필요한 소스와 테스트가 모두 있으므로 별도 파일 전달은 필요 없어.

PR173의 원본 SourceLedger58행과 5개 negative control은 완료된 별개 작업이다. 새 balance.rs 실행으로 오인하거나 불필요하게 반복하지 마. PR174의 Python 테스트는 15개 통과했고 balance.rs의 5개 작성된 테스트는 아직 NOT_RUN이다. 새 실행결과가 이미 올라왔다면 그 결과부터 확인해 중복을 피하라.

격리 환경에서 requirements.txt를 설치하고 `python -m unittest -v test_balance test_properties`를 실행해. physics source SHA256은 angular_balance.py=1ed6e5d9ea865684fda255055acac3c10efef5d0131118bc568260b0d55a21e9, balance.rs=3053e69d6a501b8beb6c4640db7826af742a85693dabe9b6b8ea523790b93e8a다.

Rust가 있는 로컬에서 새 절대경로 출력 폴더를 만들어 아래를 실행해:
```bash
rustc --edition=2021 --test balance.rs -o "$OUT/balance_tests"
"$OUT/balance_tests" --nocapture
rustc --edition=2021 -O balance.rs -o "$OUT/balance_probe"
```
OUT은 Codex가 생성·설정해. 실제 5개 테스트의 이름과 결과, exit code, source/binary SHA를 기록해. Cargo 또는 전체 REI driver 빌드는 이 독립 후보에 필요 없다. 최초 실패와 수정 diff를 보존하고 작은 호환성 수선 이외의 알고리즘·tolerance 변경은 별도 연구로 구분해.

NCP가 실제로 필요할 때만 사용자 Ubuntu에서 `ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22`를 직접 사용해. 기존 PID/affinity/checkpoint와 CPU/RAM/disk, /root/.cargo/bin/rustc 버전을 먼저 확인해. 기본 1 thread, 추가 worker<=16, RAM<=16GiB, disk<=4GiB, job<=1800초이며 owner 작업을 중단하거나 재시작하지 마.

이 작업은 기존 P2-only 후보의 compile/test다. P4 연구나 native source injection 채택, 기존 광자 stock 재가중, 물리적 anisotropic source 초기화, H/He, Q^a, polarization, checkpoint/EoR를 함께 실행하지 마.

실제 결과를 RETURN_TO_CHATGPT.json에 기록하고 단계별 DAG, 별도 결과 commit/push와 Draft PR, Dropbox·Google Drive create-only 백업 및 실제 다운로드 해시 검증까지 수행해. 자동 병합하지 말고 수행하지 못한 부분은 정확한 NOT_RUN/BLOCKED로 보고해.
