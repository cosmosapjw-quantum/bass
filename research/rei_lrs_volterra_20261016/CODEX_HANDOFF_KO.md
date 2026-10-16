# 외부 Codex/NCP 핸드오프: PR169 LRS retarded stress response 검증 및 REI opt-in 연결

사용자는 이 텍스트만 복사할 수 있어야 한다. 추가 ZIP 다운로드나 터미널 준비를 요청하지 말 것.

1. GitHub `cosmosapjw-quantum/bass`의 Draft PR169 (브랜치 `research/bass-pr169-lrs-volterra-response-20261016`) 최신 head와 parent PR168 commit `03a01d21ed21e7d32737ca5e5f6d889a7203aa70`을 직접 읽고 별도 worktree로 가져와. 연구 디렉터리 `research/rei_lrs_volterra_20261016/`의 `THEORY_KO.md`, `S2_CONTRACTION_KO.md`, `S3_POSITIVITY_KO.md`, `SCIENCE_REPORT_KO.md`, `DAG.json`, `lrs_retarded.py`, `reference_kinetic_tangent.py`, `reference_kinetic_equilibrium.py`, 테스트·원시 결과·`REI_RECEIVER_CONTRACT.json`을 모두 읽어. 부모 PR167 slope/b*를 중복 구현하지 말아.

2. 첫 작업은 해당 Python source-only 모델 24개 테스트 재현, 원본 FD96 q96 radial node bytes와 normalization, Wolfram kinetic identities 및 full x response 체크야. 조건 f_m=.1, x∈[0, ln(21/5)], m/Tref in {3,30,300}, A=0에서의 exact variation, signed s/H and Sigma nonnegative convention 고정. 이미 게시된 수치/증명을 다르게 확장할 때는 변경하는 가정을 별도로 표시해.

3. NCP에서 실제 Rust native source-only 진단을 구현·실행해야 하는 경우에만 SSH `ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22`를 사용해. 기존 64논리코어/125GiB 용량을 새로 검증하고, owner active jobs, 디스크 및 checkpoint를 읽기 전용 조사해. 새 연구는 CPU/메모리/디스크 충돌 없이 1/2/4/8/16 worker 실측 후 최적 batch width 사용, 추가 RAM ≤16GiB, 디스크 ≤4GiB, 개별 run ≤1800s. 필요한 Rust source from original BASS PR163 `research/rei_native_stress_ncp_20261015/kernel.rs` and REI PR159/167/171/172 owners should be source-read-only; build in isolated directory. Native PR159/REI chemistry automatically modified, resumed or merged NO.

4. `G(x,u)`의 double quadrature를 정확히 구현한 opt-in Rust reference를 만들고, BASS FD96 alpha/kappa와 signed v_A, positive retarded source kernel, q global bound, product-Simpson order, parent PR164 tangent and nonlinear small-A agreement를 independent test로 실측해. MP70 fixed binary64 nodes are rounding controls, NOT continuum quadrature certificates. Never claim REI matter callback is complete from standalone BASS stress-only evaluation.

5. Actual REI integration을 별도 승인된 scientific stage로 수행할 때만 현재 `rei_bianchi` latest `BassBackground` and `BASS_REI_CHECKPOINT_V2` source schema를 읽어. 같은 물리 소스를 두 번 shear에 더하지 마: PR159/167은 이미 prescribed BASS b(x),s(x)로 photons/HHe를 운반한다. 새 retarded linear response는 그 배경에 추가 가속항으로 누적하는 것이 아니라 기존 source-only BASS 배경에 대한 **독립 계산 대조**야. Actual gamma/nu/ionizing π_ab, gas Q^a and newborn thermal histories must have their own energy-momentum owners. 새 source/checkpoint 버전 및 이전 버전 거부를 검증한 뒤 한정 실험을 진행해.

6. 단계별 `DAG.json` 갱신, 테스트 raw stdout/stderr, command exit, hashes, commit push and Draft PR in BASS (REI change separately if any), create-only Dropbox + Google Drive backup, independent cloud readback SHA256, `RETURN_TO_CHATGPT.json`을 생성해. 작동하지 않은 NCP/cloud/CI 경로는 NOT_RUN/BLOCKED로 남겨. 기존 owner 작업과 원본 PR168/REI PR167 등을 자동 병합하지 마.

7. 첫 번째 제안 후속 연구는 광자/중성미자 response 없이 남은 물질 stress source의 retarded positivity envelope를 REI의 prescribed BASS background와 같은 (x,A,f_m)에서 matched comparison하는 것이다. 추가 source를 모델에 넣어 관측 EoR를 바로 계산하지 마. 회귀가 통과하면 full collisionless photon shear stress term and its missing covariant photon-creation/absorption source를 이론적으로 구성해 다음 DAG로 넘겨.
