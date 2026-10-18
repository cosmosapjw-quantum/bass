# SourceLedger Git-only Codex handoff

이 프롬프트와 GitHub만으로 진행하라. 사용자에게 ZIP 다운로드, 파일 첨부, SSH 명령 실행이나 경로 설정을 요청하지 않는다. 실제 필요한 source-only 검증을 실행하고 결과를 게시한다.

Repository: https://github.com/cosmosapjw-quantum/bass
Branch: research/bass-sourceledger-publish-retry-20261018
기준 parent: 9c264c0a21fbc4d0c3d111ed83bf0ad826a2a904
연구 폴더: research/bass_sourceledger_20261018/
고정 native REI owner: 0e25846433170d0f420c4cda44a0bedbf02cd177

먼저 GitHub/로컬 실제 HEAD, 기존 작업 tree와 진행 중 owner 작업을 확인하고 별도의 worktree를 만들어라. README_KO.md, DAG.json, RETURN_TO_CHATGPT.json, source_oracle.py, native_runner.py, native_probe/src/main.rs를 읽는다. 주 계산 코드와 tests는 이미 작성되어 있으므로 새 solver를 구현하는 작업으로 확대하지 않는다.

1. 격리된 Python 3.11+ 환경에 requirements.txt를 설치한다. 새 worktree의 연구 폴더에서 `python generate_fixtures.py --out fixtures`를 실행한다. 이어 `bash RUN_LOCAL.sh`를 실행하여 51 tests, 58 input cases, 1090 births를 확인한다. 생성기는 create-only다. 기존 fixtures가 있으면 manifest를 검증하고 보존하며, 불일치 자료를 덮어쓰지 않는다. 별도 ZIP이나 과거 /mnt/data 경로는 필요 없다.
2. 기존 인가된 사용자 Ubuntu에서 `ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22`로 NCP를 사용할 수 있다. 실제 연결, rustc/cargo 버전, PID/affinity, 메모리/디스크, owner checkpoint를 먼저 확인한다. 새 작업은 기본 Cargo jobs2, 측정기1 thread, 추가 workers<=16, RAM<=16GiB, disk<=4GiB, wall<=1800s다. 기존 owner 작업을 종료·재시작하거나 재생성하지 않는다. 가벼운 native 검증이 로컬에서 충분하면 NCP를 강제하지 않는다.
3. 고정 native commit을 가진 원래 rei_bianchi Git 저장소 또는 별도 read-only object store를 직접 확보한다. 사용자의 현재 checkout을 변경하지 말고 필요한 commit만 fetch한다. 패키지와 fixtures를 별도 경로에 옮기고 `bash RUN_NATIVE.sh /absolute/path/to/rei_git /absolute/new/output`을 실행한다. RUN_NATIVE가 committed source, literal include dependency, Cargo artifact, source hash, 58 result rows와 5 negative cases를 직접 검사한다. 출력 경로는 반드시 절대경로와 신규 디렉터리로 지정한다.
4. Cargo exit0 또는 0 tests를 native PASS로 기록하지 않는다. 실제 native owner/probe identity, 완료 marker, 모든 case/per-ray 수치, 광자수·에너지 수지와 5개 입력 거부를 확인한다. 원본 허용오차를 임의로 넓히지 않는다. 경로·컴파일 수정이 필요하면 최초 오류를 보존하고 최소 수정만 한다. 물리 연산자 변경은 원인과 새 검증 계획이 없으면 하지 않는다.
5. 이 probe는 original CovariantTransport::inject/inventory/validate_state를 호출하는 source-only 측정이다. Python predictor를 native 실측으로 바꾸어 기록하지 않는다. 광자 stock은 photons/H와 eV/H이고 proper volume은 n_H0/a^3를 한 번만 곱한다. signed s와 Sigma, 방출시각, spectral/angle quadrature 및 source-frame Jacobian을 보존한다. Reactive HHe, opacity, Einstein feedback, Qa, polarization, restart와 full EoR를 이번 실행에 추가하지 않는다.
6. 결과의 stdout/stderr/명령/exit code/source SHA/binary SHA/원시·정규화 잔차·자원을 보존하고 DAG와 RETURN_TO_CHATGPT.json을 갱신한다. 별도 결과 branch를 commit/push하고 Draft PR을 게시하되 자동 병합하지 않는다. Dropbox와 Google Drive에 create-only로 백업한 후 양쪽 raw download의 SHA256을 검증한다. 컴파일이나 수치대조 실패는 실제 BLOCKED/FAIL로 남기고 가짜 native 승인을 하지 않는다.

최소 성공조건: 기존 51 Python checks, 실제 native 58 rows 및 완료 marker, 5 native negative-control rejections, source-matched number/energy/ray parity. 코드 작성 계획이나 새로운 handoff만 반환하지 말고 실제 실행 결과와 미완료 의무를 보고한다.
