# BASS PR167 후속 Codex 실행 프롬프트 (다운로드 없이 GitHub에서만 재개)

기본 작업은 `cosmosapjw-quantum/bass`의 Draft PR167 최신 head를 읽어 source pin을 확인하고, 11개 Bianchi class 연구에서 현재 BASS LRS→diagonal/non-LRS 확장에 적합한 별도 브랜치로 이어가는 것이다. 기존 PR166, rei_bianchi PR167/168, REI owner checkpoint/NCP 작업은 변경/병합하지 말 것.

읽어야 할 source: `research/kinetic_stress_equilibrium_20261016/STAGE1_THEOREM.md`, `DAG.json`, `kinetic_equilibrium.py`, `test_equilibrium.py`, `STAGE2_NUMERIC_EVIDENCE.json`, `einstein_stress_lag.py`, `STAGE3_DYNAMICS.md`, `GENERAL_DIAGONAL_THEORY.md`, `nonlrs_convexity.py`, 이 README 또는 로컬 백업 아카이브. 원래 FD96 `bianchi/matter/freestream.py`, `research/rei_einstein_tangent_20261016/kinetic_tangent.py`의 Git SHA를 다시 검증할 것.

**첫 타겟: BASS 물리 코드의 next incomplete C5/C7.** Local repo의 real non-LRS Einstein kinetic source에 대해 positive q_i distribution + full tensor pressure(πij) 및 tracefree Hessian 2×2를 opt-in implemented source로 구성하고, reflection/rotation/parity 및 Hamiltonian·Raychaudhuri를 exact density-work identity로 검증해. non-LRS offdiagonal T_ij의 존재를 알고 있으므로 diagonal metric compatibility를 명시. 기존 LRS sigma/signed q_ref/β chart와 양의 distribution weight는 고정. 일반 Bianchi II-IX/CMB/Thomson으로 확대하려면 별도 전역 운반 유도와 소스 증거가 필요하다.

코딩은 먼저 GitHub 최신 branch, AGENTS.md, 관련 PR, DAG를 읽고 별도 worktree를 구성해. 새 코드를 local Rust/Python에서 빌드·실행하고, 실제 heavy jobs만 승인된 NCP 64c/125GiB에서 격리하도록 해. 사용자의 파일 첨부/수동 명령은 요구하지 마. 중간마다 Git 커밋/PR 백업 및 새로운 DAG 상태를 적고, 마지막에 Dropbox+Google Drive create-only 두 클라우드 upload/readback 해시, Git bundle restore, Draft PR, RETURN_TO_CHATGPT.json을 남겨. 기존 repo/checkpoint 자동 병합/덮어쓰기 금지. 실제 미실행·실패는 NOT_RUN/HOLD, 문서·코드만 쓴 일은 실행 통과라고 부르지 마.

REI 관련 작업은 BASS LRS/non-LRS source 경계가 실제 결합 가능한 typed interface로 검증된 뒤 별도 승인 범위에서 시작해. 그때 `b_star`를 shear closure로 강제하지 말고, BASS에서 자체 계산한 DeltaP, dDeltaP/db, ∂A response, units, signed shear 그리고 original phase-space source SHA를 explicit opt-in provider로 전달한다. REI PR167의 photon-birth operator and 2048-step long-history HOLD는 독립 lane 그대로 유지한다.
