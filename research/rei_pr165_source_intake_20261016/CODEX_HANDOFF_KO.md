# Codex Handoff: BASS PR165 → rei_bianchi native geometry source gate → NCP bounded trial

## 지시와 실행 범위

이 메시지는 코드 구현과 실제 실행 요청이다. 문서만 생성하지 말고, 먼저 저장소의 실제 커밋·작업 트리·NCP 프로세스·checkpoint를 읽고, 충돌 없는 독립 worktree에서 실행 가능한 경로를 구현하고 테스트하라. 현재 표준은 BASS PR164의 Einstein–Vlasov source-only background와 본 PR165의 엄격한 geometry intake/clock interpolation이다. 원래 REI production driver를 바로 바꾸거나 오래된 AX08 checkpoint를 새 배경으로 재개하지 않는다. 테스트/빌드가 실제 통과하지 않았으면 PASS를 주장하지 않는다.

1. **SSOT:** `cosmosapjw-quantum/bass` PR164 branch `research/bass-einstein-tangent-20261016`, exact commit `3c39bbbf46b6663e7c40277e194fd0ef48118472`. 부모 PR163 `9ea46052358ba3e190317347d7f0001bab23c398`. 원래 FD96 Python `bianchi/matter/freestream.py` Git blob `8467932c3281f9d426712b3a582f2aae3a484692`, AX03 lock Git blob `7bfd190fe4cc722c2813c70e036d0279a0d83641`. PR164는 source-formula reconstruction이지 원천 파일의 byte copy가 아니다.
2. **REI owner:** `cosmosapjw-quantum/rei_bianchi` PR150 `research/flrw-production-integration-20261015` head `fe789b0b13b1883c5a74cbc907f72f6f963a5d66` (확인 시점 기준). Rust `rust/rei_microphysics/src/axbi_background.rs` Git blob `6e92f6456525dd10c0e9d800d329ffc511ac75dd`; `src/bianchi_i.rs` blob `81dc54583b76e9dcba94c5bbc867243b04ad76b1`; `Cargo.toml` blob `0771ae64cf1e4c8f51a9fb7f23f216c4056e423b`. `BackgroundPoint::sigma`는 signed `s/H`이고 공개 물리량 `Σ=sqrt(3)|s|/H`와 다르다. REI PR152/153/154 Verner/chemistry 결과는 원자·광원 측의 독립 lane이며 PR150의 현재 운용 코드에 자동으로 합쳐지지 않는다. BASS_HE PR67 및 bass_cr PR72도 독립 공급원이다.
3. **현재 패키지:** `source_table.py`는 producer manifest/CSV source SHA256, row count, case order, finite values, pressure positivity, Hamiltonian, Raychaudhuri, native signed shear, proper time monotonicity를 검사한다. Geometry interpolator는 `ln H`와 `b`를 `x=ln(a/aref)`에서 cubic Hermite로 보간한다. `s(x)=H(x) db/dx`를 정의하고 proper elapsed seconds를 `integral dx/H`로 재구성한다. 원본 PR164 968개 node와 source-only native geometry 968개를 별도로 보존한다. 기존 PR164 14 Python tests 및 새 PR165 15 Python tests는 ChatGPT container에서 통과했으나 원래 REI Rust crate 빌드는 **NOT_RUN**.

## NCP 운용상 필수 사전 점검

원격 Desktop Commander가 월간 사용 한도에 도달했으므로 본 대화 환경에서 Ubuntu/NCP 원격 명령을 새로 실행한 것으로 주장하지 않는다. Codex는 사용자 Ubuntu의 실제 SSH 경로를 사용한다.

```bash
ssh -i "${NCP_KEY:?set NCP_KEY}" root@"${NCP_HOST:?set NCP_HOST}" -p 22
```

NCP_HOST와 NCP_KEY는 사용자가 제공한 기존 SSH 대상/키를 Codex 세션의 비공개 환경 변수로 지정한다. 공개 GitHub에 원격 주소나 개인 키 위치를 새로 게시하지 않는다. 첫 작업은 NCP에서 `hostname; nproc; free -h; df -h /; /root/.cargo/bin/rustc --version; /root/.cargo/bin/cargo --version; ps -eo pid,etime,%cpu,rss,args | grep -E 'REI_FLRW_COVARIANT|axbi|full_campaign|rux'`를 **읽기 전용**으로 실행하는 것이다. PR150/source005 `full_campaign001`의 Q512/Q1024 장시간 계산과 watcher가 마지막 확인 시점에 실행 중이었으니 종료·덮어쓰기·epoch 리셋·동일 run 재시작을 금지한다. 실제로 실행 중인지 읽은 뒤 겹치지 않는 CPU affinity와 여유 디스크만 사용할 것. `df`/RAM/CPU 여유가 없다면 이 작업의 무거운 실험은 `DEFERRED_RESOURCE_CONFLICT`로 보존하고 원본 run을 우선한다.

## 구현 목표와 순서

1. BASS PR165 branch(첨부 handoff/ZIP의 소스 경로 포함)를 fresh isolated worktree로 확인하고 PR164 exact parent를 고정한다. `python -m unittest discover -s tests -v`와 `python -m unittest -v test_kinetic_tangent test_export_bridge`에서 현재 baseline을 재검증한다. BASS PR164 source `source_pr164/PROPOSED_REI_BACKGROUND.csv` SHA256 `5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133`, producer receipt SHA256 `98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed`을 검사한다. 값이 달라지면 새 source identity로 재기준화하되 조용히 바꾸지 않는다.
2. `python export_native_geometry.py --source-csv source_pr164/PROPOSED_REI_BACKGROUND.csv --source-receipt source_pr164/PRODUCER_RECEIPT.json --out NEW_DIR`로 source-versioned native geometry를 별도 생성한다. 제공된 `evidence/NATIVE_GEOMETRY_INPUT/NATIVE_GEOMETRY.csv` SHA256 `b406e60184d68fd4014dbee42250b8cf4645f48d1580caf44b336eac0fd93037`은 **현재 상태의 고정 기준**이다. 생성물은 절대 기존 checkpoint와 합치지 않는다.
3. 원래 REI PR150 소스(독립 detached clone 또는 isolated worktree, 깨끗한 원본)를 읽기 전용 Cargo dependency로 연결한다. `native_rust/Cargo.toml`의 `REPLACE_WITH_PINNED_REI_MICROPHYSICS_PATH`를 해당 실제 absolute path로 치환한 새 Cargo manifest를 **별도 임시 폴더**에서 생성한다. 원본의 파일을 수정하지 않는다. `cargo test --offline --manifest-path STAGING/Cargo.toml`, 이어 `cargo run --offline --release --manifest-path STAGING/Cargo.toml -- NEW_DIR/NATIVE_GEOMETRY.csv`를 실행해 원래 Rust `BackgroundPoint.geometry()` 자료형과 volume, signed shear, proper-clock 순서, 968row case completeness 검증을 수행한다. 제공된 Rust 파일은 이 세션에서 빌드되지 않았으므로 컴파일 실패하면 정확한 에러를 기록하고 **한 차례 구성적 수정** 후 재실행한다. 현재의 `Rust native = NOT_RUN` 상태를 코드만 보고 통과로 바꾸지 않는다.
4. Rust adapter 통과 후에만 REI owner native chemistry와 **동일한 초기 시각·같은 H/He/UV source/event**를 사용한 소규모 source-only trial을 별도 branch로 구성한다. `GeometryBackground`의 proper-time 호출과 log-a chart 역변환을 일관되게 하며, epoch/restart/checkpoint/source SHA identity를 새로 발급해야 한다. 종전 AX08/PR150 checkpoint를 새 Einstein source identity 아래에서 재사용하지 않는다. initial FLRW control과 kinetic warm isotropic control을 구분하고, 원래 표준 FLRW와 다르다는 이유로 수치 오류 판정을 하지 않는다.
5. Mandatory tests: signed Sigma/s/H, Hamiltonian source energy budget Ω_m subdivision, dρ/dx+3(ρ+pbar)+2(s/H)DeltaP, proper-time positive integration/roundtrip, b'=s/H, independent Raychaudhuri, no negative kinetic pressure, source SHA/case/row/clock tamper negatives, byte-identical Rust input readback, `same-event` gas/photon/thermal/ionization ledgers, new checkpoint restart rejection of old schema. 비교는 비자명한 양에 정량적 tolerance와 refinement (121→241→481 at matched input)를 적용하고, 추가 통과를 위해 임의로 tolerance를 넓히지 않는다.
6. Scientific claim stop: source-only native type/geometry passing does **not** imply native H/He, polarized Thomson, stellar momentum/recoil, full EoR or observation fitting passing. Native full chemistry pass에는 실제 proper-time, H/He(D if available), temperature, photon number/energy/heat/binding, Einstein constraint, geometry and source ledger를 모두 개별적으로 요구한다. Unresolved stellar/gas Q^a는 명시적 open reservoir로 유지한다.

## NCP 자원 상한과 독립성

먼저 geometry/proper time standalone은 Ubuntu/NCP에서 1-4 core로 충분하다. 이후 121/241/481 reference refinement와 독립 입력 계열을 병렬화할 때만 사용 가능한 CPU를 사용한다. 원래 64논리코어 중 다른 REI 장시간 작업이 사용 중인 CPU를 침범하지 않고, 새 작업은 **최대 16 workers, 추가 RAM≤16GiB, 추가 디스크≤4GiB, 전체 추가 wall≤1800s**로 제한한다. 이 상한은 승인 없이 상향하지 않는다. 기존 production process를 중지하거나 preexisting pool/affinity, checkpoint, configs, logs를 덮지 않는다. 수치 시뮬레이션은 반드시 NCP에서 수행한다. 가벼운 한정 테스트만 사용자 Ubuntu에서 허용한다.

## 게시, 이중백업, 반환

성공 또는 부분 실패 시에도 독립 worktree의 새 branch에 실제 코드·수정·테스트·프로파일·수치 자료를 commit/push하고 **draft PR**로 게시한다. auto-merge 금지. source-conditional REI native driver 변경은 BASS side PR과 다른 rei_bianchi PR로 분리한다. 가능한 경우 지정된 rclone `dbx:`와 `gdrv:`에 동일한 SHA manifest 포함 archive를 create-only 업로드하고, 두 provider에서 실제 재다운로드해 SHA-256을 비교한다. 어느 한쪽이 불가하면 GitHub/Drive 등 성공한 provider만 보고하고 이중백업을 허위로 인정하지 않는다.

`RETURN_TO_CHATGPT.json`에는 exact commit, changed files, cargo/rustc version, origin SHA256, tests with exit code, physical and numerical residuals, NCP command/host/affinity/wall/RSS/source identity, archive/hash, Dropbox/GDrive readback identities, production nonclaims, next action을 포함하고, 현재 대화에 붙여넣을 간결한 한국어 보고를 제공한다. 성공적으로 유도·실행한 사실만 `DERIVED / NUMERICALLY_CHECKED / IMPLEMENTATION_VERIFIED`; 아직 실행하지 않은 단계는 `NOT_RUN`, 환경 문제는 `BLOCKED_RUNTIME_QUOTA`로 유형을 분리한다.

**현재 최소 gate:** PR164 source readback → PR165 Python contract → native offline Cargo typed intake → same-clock **fresh** REI mini-trial. 이 순서 외의 full production run은 사용자 승인과 과학 source ownership이 허용하는 별도 DAG로 수행한다.
