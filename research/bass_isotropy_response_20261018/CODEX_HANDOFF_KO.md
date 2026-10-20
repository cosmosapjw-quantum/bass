# Codex / NCP handoff — 검증된 S10을 보존하는 다음 구현

아래 단일 블록은 local/Codex/NCP 실행자에게 전달할 수 있다. 현재 S9/S10 실행을 다시 돌리는 지시가 아니며, 고정 결과를 읽어 사용자가 선택한 새 물리 의존성의 구현 계약을 준비한다.

```text
$physmath-research-loop를 적용해 BASS의 이미 완료한 S9/S10 증거를 재사용하고 사용자가 선택한 후속 물리 구현만 진행하라. 사용자에게 과거 대화·ZIP 다운로드·첨부·사전 명령을 요청하지 않는다. 이 handoff로 새 자동 최적화 cycle 또는 과거 build/test/ODE/benchmark 재실행을 시작하지 않는다.

[repo·source·결과 identity]
Repo=https://github.com/cosmosapjw-quantum/bass
Draft PR174=https://github.com/cosmosapjw-quantum/bass/pull/174
Branch=research/bass-isotropy-checkpoint-recovery-20261018
Lane=research/bass_isotropy_response_20261018/
S9 원 실행source=4b30957cb008aad8019bb1a673937fc67bd017e8
S9 실제 결과=a40311796f9aac5ea5e0e58c630bee2a78443353
S10 실행source=d5a173644f5c7c0dbe9eb8757dfc4ccad6c4f4c8
S10 sourcetree=95785be65c196c68d61b79dafb32f4cedfd7702d
Source/input manifest SHA256=4ac631dced7e1d4fdc8ce63d076dfe15bb38bde7040029644e2c34f30b1ebc17
C6 checkpoint=477eca7d13bba4f69e063ad9b024225ee06cc395
C7/C8 result=26e9e1ba8f39788d98ec33c60f6e9fd2605f8b8a
C7/C8 tree=925f3cf75683b83c8b292cea4ce596059b36265d
C9 review=0771f0610987eb9f900674e83063912150733255
C9 tree=1c93fb37dce78cbd54691d072aaf35209a94894c
VigilODE=a21d573980f66fe02891bd216153443b5352f921
REI spectral owner=0e25846433170d0f420c4cda44a0bedbf02cd177
Parent PR173=4e2d1fa820d6f7baae1069b615fb82a08d53403b
SourceID=MD14_Z002_FESC_BB50K_13P6_100_V1
최종 metadata HEAD: 이 파일이 포함된 최종 metadata HEAD는 PR174 최종 배송 댓글/Git ref와 postcommit tree/blob readback을 대조하라. 위 source/result/review identity는 고정값이다.
Timing binary SHA256=375d95ae4dfdd96fef96c8b96a17fa966e0cd6b14063b14a79d867c2233f8265
Allocation-probe binary SHA256=4ab9bf3013f0ef599a9bd06b5e6458f04ca697c727250e58bc8750ca6f8474b3
두 binary는 서로 다른 계측 목적이며 timing 표본에 allocation 계측을 섞지 않았다.

[첫 행동: read-only identity 대조]
현재 Git ref/commit/full tree, PR174 최종 배송 댓글과 Dropbox /BASS_BACKUPS·Drive /BASS_BACKUPS의 저장 결과를 읽는다. Drive folder ID=1fFxb-qgExWbEomt3EbbOjGKcslFpGv3y. PR 요약 HEAD의 원 stale 관측은 보존하고 실제 Git Data ref/commit/tree 검증을 따른다.
README_KO.md, DAG.json, RETURN_TO_CHATGPT.json, PUBLICATION_CLOSEOUT.json, CLOUD_READBACK_KO.md, S10_OPTIMIZATION_KO.md, S10_THEORY_KO.md, S10_RESULTS_KO.md를 읽는다.
s10_optimization/SOURCE_MANIFEST.json, evidence_s10/c4/BENCHMARK_PROTOCOL.json, s10_optimization/provenance/RUNNER_COPY_PROVENANCE.json 및 RUNNER_CALLBACK_DIFF.patch를 읽어 원 source·input·실제 변경 범위를 확인한다.
실행 증거는 evidence_s10/c6/tests_r1_PROCESS.json와 tests_r1.log, evidence_s10/run_20261020_r1/EXPERIMENT_POSTCHECK.json, measurements/*, evidence_s10/analysis_r1/S10_ASSESSMENT.json이다.
독립 검토는 evidence_s10/c9_review_r1/C9_REVIEW_RECEIPT.json, C9_REVIEW_KO.md, source_contracts_note.md, INDEPENDENT_RECOMPUTATION.json, C9_CLOSEOUT.json이다. Receipt SHA256=1b63d46ebe2b576acacd828b77ac5fdf85e3461de84991305f708b2ea5513c29.
S9_RESULTS_KO.md와 evidence_s9/run_20261020_r1/CAMPAIGN_RETURN.json, 실제 독립 dual review를 읽어 원 완료 범위를 확인한다. S6–S8 원 evidence도 재사용한다. 역사적 NOT_RUN/source-only/prior-build 문장을 현재 상태로 승계하지 않는다.

[완료된 코드와 범위]
원 s9_vigilode, balance_p24.rs, 고정 VigilODE/REI owner는 변경하지 않았다. 새 isolated opt-in crate s10_optimization에서 baseline/stream/prepared/cache/simd/simd_cache 여섯 mode를 비교했다.
Baseline run은 원 S9 run을 직접 호출한다. Candidate runner는 원 birth/P24/exact certificate/event/observation/solver-counter 처리에서 선언된 다섯 callback/mode 치환만 적용한 provenance가 있다.
원 성분별 Neumaier 순서·괄호를 보존한 streaming accumulator, immutable mu²/weight SoA(1-z는 평가 중 계산), private Arc bank, full(x,h,b,y).to_bits key, RHS/Ft와 JVP-base 각각1slot을 사용한다. 새 v마다 Jv를 다시 계산하고 새 birth/segment에는 새 bank/cache/workspace다.
SIMD는 stable std::arch의 ray별 packed f64 연산과 보수적 AVX2 runtime guard, scalar tail/fallback을 사용한다. Ordered scalar reduction, 원 multiply/divide 괄호, scalar exp를 유지한다. Symbol 범위의 no-FMA 근거를 upstream binary 전체에 확대하지 않는다.
Rayon1.12.0은 독립history만 workers1/2/4로 실행하고 입력 순서로 결과를 모은다. Birth 내부 합산·시간 적분 내부의 병렬 reduction은 없다.
S9는 고정8history 8/8완료·140gate assertion PASS이며 현재 scope의 NCP 재실행 의무가 없다.
S10 release C6 targeted11/11, kernel proof108/108, 전체 대표RAW24/24 scientific bytes 동일, serial/parallel digest 동일, science68/68 PASS다. 실제 benchmark496history 호출은 기존 네 입력의 반복이다.
C9 단일 독립 pass155/155 checks와 science68/68 PASS_SCOPED, code/science finding0, 문서 finding1closed다. 수정은 prepared 데이터 표현뿐이며 code/tolerance 변경·solver/benchmark 재연0이다. 다른 host/compiler 재현은 아니다.
MF simd_cache paired median은 closed2.973배·FLRW4.115배였다. Closed small/clock4는1.055배(IQR0.957–1.243)로 일관된 이득을 승인하지 않는다. Changing n16/cohort2의0.949817은 실제 성능 회귀다. 평가 구간 최적화 allocation/reallocation0은 setup·caller clone·whole-history 전체 할당0이 아니다.
Rust1.94.1/LLVM21.1.8, release opt-level2/codegen-units1/LTOoff, locked/offline, fast-math/RUSTFLAGS없음에서 얻은 제한 결과다. 원 source/lock/owner 보존과 runtime hash는 receipt를 재사용한다. 현재 결과 확인을 위한 추가 compile/test/benchmark/적분은 필요 없다.

[새 코드가 보존해야 할 입력·gate]
Non-tilted axisymmetric Bianchi I, (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b, Sigma=sqrt(3)|s|/H.
새 명시적 isotropic birth quadrature만 보정하며 기존 photon/physical anisotropic stock·birth weights는 초기화하거나 재가중하지 않는다. 양성·reflection parity·source frame·고정 spectral/balance owner를 유지한다.
현재 exact normalization/P2/P4 gate3/10^15, fine reference abs1e-9, Hamiltonian/cohort energy rel1e-11, event energy1e-13, donor endpoint3e-14, clock abs1e-12를 임의 완화하지 않는다. Feasibility와 numerical precision 실패를 음수 weight나 tolerance 변경으로 우회하지 않는다.
같은 point exact-cache를 approximate Jacobian reuse로 바꾸거나 exp(x-u)를 별도 지수곱으로 분해하면 별도 수치 계약이다. P2/P4 일치만으로 continuum/full finite-bin 보존을 승인하지 않는다. 전체 scientific receipt 동등성은 elapsed_seconds만 제외한 관측·event·segment·최종cohort·counters·failure까지 포함한다.

[보존할 실패·배송 상태]
신규 compile/strict identity/science 실패0, C6 예상입력실패7, 위 성능 회귀/불확실성을 구분한다. 고정 VigilODE dead-code경고4개와 문헌 취득 실패, 과거 환경/runner/Drive 실패 receipt를 삭제하지 않는다.
S6 rate38/344 실패·P4악화44/238, S7원실패, S8낮은해상도8미달 및 b0=.9/n64/P24 STRICT_INTERIOR의 INNER_P2_PRECISION_LIMIT를 보존한다.
S9 실제 결과와 S10 C1/R2·C2/C3·C5/C6/C7·C8/C9/C10의 봉인 원8ZIP은 Dropbox와 Google Drive 양쪽의 전체 원격 bytes/SHA256/CRC/manifest 검증을 완료했다. 총4,189,549bytes·317manifest payload 항목이며 checkpoint 중복을 포함한다. 단계별 객체·hash·원 commit/tree는 delivery/s10/CLOUD_CHECKPOINT_INDEX.json, Drive 실제 증거는 delivery/s10/drive_recovery_20261020/EIGHT_ARCHIVE_DRIVE_READBACK.json, Dropbox 실제 복구 증거는 delivery/s10/dropbox_restore_20261020/EIGHT_ARCHIVE_RESTORE_READBACK.json을 읽는다.
원 C10 판정 metadata=a85605302bb0317022eb06b498eb05b9d621de6a, tree=e1d04268e647b6cb6d33374b64598fa3ec0d4131. 이는 실행 source나 이번 배송 복구 containing commit과 구별한다. 이번 복구 metadata의 정확한 commit/tree·별도 postcommit 보충 ZIP·마지막 이중 readback은 최신 PR174 배송 댓글과 postcommit receipt에서 확인한다. 자기 commit/hash 또는 미확인 보충본 성공을 꾸미지 않는다.
과거 connector 무응답과 승인 후 browser 보안 로그인/runtime timeout은 역사적 실패로 남긴다. 브라우저 인증 성공·업로드는 관측하지 않았다. 사용자가 명시한 Google Drive 플러그인 재시도가 성공해 원8ZIP의 현재 Drive blocker는 해소됐다. 사용자 업로드 승인을 다시 요구하지 않는다. 실패 receipt와 빈 Docs/Sheets를 완료 백업으로 세지 않는다.
배송 복구를 위한 과학/build/test/ODE/benchmark 재실행은0회이며 추가 NCP 의무도 없다. 과학 source·owner·남은 physics 의무·원 실패를 그대로 보존한다.

[다음에 구현할 실제 의무]
새 optimization cycle을 자동으로 열지 말고 사용자가 선택한 후속 물리 단위의 식·data·owner 의존성을 먼저 정식화한다. 남은 범위는 실제 MD14의 source time/체적/energy supply/stress normalization과 native Einstein/shear의 shared-Q 결합, 미구현P6, evolving reactive full finite-bin spectral-history 보존/수렴, S8 precision failure, 더 넓은 finite-d/angular accuracy, 새 Rust client의 full birth-memory parameter tangent다.
S6 fixed-owner source-deposition 차이5.369926725506957e-12 설명은 원 범위로 재사용한다. 이를 실제 reactive/full-history spectral 수렴이나 MD14 feedback 완료로 바꾸지 않는다.
가능한 유도·코드·입력·negative control·고정 gate를 샌드박스에서 먼저 완성하고 변경된 의존성만 검증한다. 새 NCP가 필요하면 검증 가능한 source/input/prereg와 게시/provider별백업상태를 먼저 남겨 compile·작은 호환수정·등록실행만 맡긴다. 현재 완료범위의 NCP의무는 없다.
추가worker≤16/RAM≤16GiB/disk≤4GiB/개별job≤1800초. 현재관측은8CPU/8GiB, 기본build2, 이번 workload의 독립history 후속권장2workers다. 새 환경의 compiler·실제quota·disk를 읽고 기존 owner 작업·사용자변경·실행중job을 보존한다.
결과 경로와 원RAW를 덮어쓰지 않는다. source/result/review/metadata identity, 실제 command/exit/binary/input hash, gate, resource 관측범위, 실패종류, 남은일, GitHub/PR, provider별readback과 두handoff를 반환한다. REI production/full EoR/merge로 확대하지 않는다.
```
