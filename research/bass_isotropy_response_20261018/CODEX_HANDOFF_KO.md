# Codex/NCP handoff — 준비된 S12 17job만 실제 실행

이 문서는 Codex가 수행할 작업 지시다. 사용자에게 사전 명령을 실행하게 하는 요청이 아니다. 기존 owner checkout/job을 보존하고, 실제 유효한 NCP 접근이 없는 동안 아래 launcher를 실행하지 않는다.

```text
$physmath-research-loop로 BASS의 완료된 S9/S10/S11/S12를 재사용하라. 이번에 새로 준비한 S12 17job의 미실행 부분만 실제 NCP에서 수행할 수 있도록 작성된 코드와 고정 입력을 사용하라. 옛 캠페인, 자동 최적화 cycle, pointwise projection, short history, native compile-only를 다시 시작하지 마라. 사용자에게 ZIP·첨부·과거 대화·선행 compile 명령을 요청하지 마라.

[고정 repository와 source/result 역할]
Repo: https://github.com/cosmosapjw-quantum/bass
Draft PR174: https://github.com/cosmosapjw-quantum/bass/pull/174
Branch: research/bass-isotropy-checkpoint-recovery-20261018
Lane: research/bass_isotropy_response_20261018/
S12 unit: s12_birth_memory/
Original REI owner: 0e25846433170d0f420c4cda44a0bedbf02cd177
S12 Rust science source: f4cd0d53760783e6a58c3b0a98c64311ca489d28
S12 science tree: a9048818707ef3f446528631c3b5d6c8171116cc
S12 parity/PID namespace verification repair: 4e3615dd75ff1a1efc2792edb3ba5b702a8a9b06
S12 stored-support observer source: be773dbf36bbe74b42e89e51c61dcd56ef2e6687
S12 C8 execution source: 8247645d04695bdbfa48eb2fe74757dacf7d2636
S12 C8 tree: 47d90048b2fe96f05a32711209b7d52bc2c7eee1
S12 result commit: fd8a9aafeaaf29afeab04e9d2876db087e90d24b
S12 result tree: 1e29262dd8925fdd0f40fcc7e14e559c333816f6
최종 containing metadata HEAD/tree와 ZIP/JSON/provider ID는 최신 PR 최종 배송 댓글 및 실제 Git ref/full-tree/readback에서 읽는다. source·result·review·metadata를 혼동하거나 문서 안에 자기 hash를 꾸미지 않는다. 더 새 실제 결과가 있으면 identity를 대조한 뒤 재사용한다.

[첫 행동은 read-only 대조]
현재 GitHub branch ref/commit/full tree, PR174/175의 최신 댓글과 관련 branch/main, 연결된 대화 검색 및 Dropbox·Drive /BASS_BACKUPS를 먼저 대조한다. Drive folder ID=1fFxb-qgExWbEomt3EbbOjGKcslFpGv3y. provider 목록은 pagination과 관련 하위 폴더까지 관측한 범위를 기록한다. 과거 대화 전체를 보았다고 추정하지 않는다. cache된 PR summary와 direct Git ref가 다르면 actual ref/PR API를 확인한다.
Lane의 README_KO.md, DAG.json, RETURN_TO_CHATGPT.json, PUBLICATION_CLOSEOUT.json, CLOUD_READBACK_KO.md, S12_RESULTS_KO.md, NEW_THREAD_HANDOFF_KO.md 전체와 CODEX_HANDOFF_KO.md를 읽는다.
S12 THEORY_KO.md, PREREGISTRATION.json, PRIMARY_LITERATURE.json, Wolfram 실제 응답/수리 기록, 실행 BUILD/PROCESS/RETURN/SUMMARY, 독립 검토 원본, native_support certificate, ncp/JOB_TEMPLATE.json, SCIENCE_BINDING.json, DELIVERY_BINDING.json을 읽는다. 파일 위치는 현재 repo tree와 DAG를 따른다. 백업에서 복원할 때는 전체 bytes/SHA256/ZIP CRC/manifest를 대조하고 원래 실패 receipt를 남긴다.
S9_RESULTS_KO.md, S10_RESULTS_KO.md, 원 S10 C9 실행 receipt, s11_p246/RESULTS_KO.md·RESULT_LEDGER.json·CONTRACT.json·CONTRACT_ADDENDUM.json·THEORY.md 및 실행/독립 검토도 재사용한다. 오래된 handoff의 NOT_RUN·미구현·pending 문장을 새로운 증거보다 우선하지 않는다.
사용자에게 과거 대화, ZIP 다운로드, 파일 첨부, 사전 명령 실행을 요청하지 않는다. 접근 가능한 connector/repo/백업을 직접 대조한다.

[완료된 S9/S10/S11 — 재실행 금지]
S10 배송 metadata: d0c0313d6c063037fd8e067744aee66235df1a58
Tree: e62a42c3227114a5657538a75e034af5a5823703
S10 execution source: d5a173644f5c7c0dbe9eb8757dfc4ccad6c4f4c8
S10 result: 26e9e1ba8f39788d98ec33c60f6e9fd2605f8b8a
S10 independent review: 0771f0610987eb9f900674e83063912150733255
S10 final comment: https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6289844952
2026-10-20 원8ZIP+복구1ZIP=9ZIP, 4,399,983bytes, 중복 포함 payload383항목과 최종 JSON은 양쪽 provider 전체 bytes/SHA256/CRC/manifest·내용 검증 PASS로 완료다. 신규 Drive 문제로 원 완료를 취소하지 않는다. 이 배송 복구의 science/build/test/ODE/benchmark/NCP 재실행은0회다.
복구 ZIP: BASS_S10_DRIVE_RECOVERY_20261020_d0c0313d.zip
SHA256=68a36c8eea617130afe5256a9ead130147bbc26bc4f2861235ed5809af78dee4
Drive=1oUoDJ8O0Bh6W1yFzSdc3XebGNeSengfZ; Dropbox=id:BSpOijBcT10AAAAAAD_T4Q
최종 JSON: BASS_S10_FINAL_DELIVERY_20261020_d0c0313d.json
SHA256=98a88ff10828d9d6d0794237da87db76fb68875db38457c7fb18c04aedcfdb3c
Drive=1IJFuu_qDoNoMXiU-9a7wxE4E5bZeJCqm; Dropbox=id:BSpOijBcT10AAAAAAD_UAg
S9 고정8history, S10 targeted11/11·kernel108/108·RAW24/24 scientific identity·science68/68·독립 C9 155/155를 재사용한다. MF closed2.973배·FLRW4.115배는 해당 고정 workload의 결과다. closed-small1.055배(IQR0.957–1.243)의 불확실성과 changing n16/cohort2의0.9498173837599284배 성능 회귀를 보존한다.

S11 science source=7fb9b83cba01d37ce4cabbc4772527710601cd96
S11 result/review=85d5833b4486d14855b84a9d967f5819788d05e5
S11 delivery metadata=44bac536f6add11f8d2d4b3aa585a1c2f9049664
S11 delivery tree=411a427420cbf4773616a0efa3d76772548bf0bb
S11 최종 게시 복구 댓글=https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6301060073
S11 positive fixed-support P24/P246 KL projector는 Python Decimal/Fraction과 Rust로 구현했다. Main101/101, 수학 복구25/25, 독립 physics235/235, provenance152/152, 문서23/23은 서로 범위가 다르므로 합산하지 않는다. 14 projection 중12양의 성공/2예상 infeasible, 660angular response를 재사용한다. provenance152 검토자는 Rust 구현자였다는 독립성 제한을 보존한다.
S8 birth11 P24 점별 precision은 S11에서 복구했지만 원 전체 history 성공을 뜻하지 않는다. 같은 support의 P6는 실제 infeasible이며 P24_only P6도 min facet slack=-1/42다. d=k/40, k=-24..24의49점에서 P24 maxbias0.022042599461602856, P2460.03414707018952904, 비1.54913989382294의 악화를 보존한다. 유한 grid 최대값을 연속 supremum이나 full-history 오차로 바꾸지 않는다. 소실 smoke raw는 TRANSCRIPT_ONLY_NOT_DURABLE로 남기고 PASS에 포함하지 않는다.
S11 Dropbox4ZIP·3,270,286bytes·중복 포함 payload241항목 및 최종 JSON은 전체 readback PASS다. S11 새 Drive는 미완료이며 원 S10의 양쪽 PASS와 구별한다.
2026-10-15 NCP64CPU/약125GiB의 기존3massset·1213rows·21개 width1/64 benchmark row는 이미 완료한 캠페인이다. 현재 미실행 backlog나 현재 hardware identity로 바꾸지 않는다.

[S12 실제 완료 증거]
새 Rust client는 고정 birth 좌표·고정 donor amplitude, theta=y0의 full birth-memory parameter tangent를 구현했다. cohort의 B_j=d b(u_j)/d theta, mu_theta=mu_b B_j, alpha_theta=alpha_b B_j를 고정 저장한다. 현재 b_theta의 기하 미분과 과거 birth memory를 구분하며 6상태 exact augmented Jacobian의 아래 왼쪽 block, explicit-x derivative, clock7/MF6 경로를 포함한다. 기존 S9/S10 fixed-bank JVP를 오류로 규정하지 않는다.
Rust build PASS147.599956696초. Sandbox core binary SHA256=25905570282ffe68696481d82f9b6f89107c2f838e5e58dfb17de0987c324fe5, history binary SHA256=81ac86ad59d9d58bf01e0411fec807f07a05950e632ef8aa920d747f4b750518. 다른 machine에서 compile한 binary는 새 실제 hash를 receipt에 binding하며 같은 hash라고 가정하지 않는다.
Core269/269, 새 짧은 history72/72. 총14개 Rust case=11full+3omission control, 독립 Python reference 및 최종 checkpoint restore다. Python–Rust state6 scaled max3.483131098619846e-15, MF6–clock7 max1.623443460779953e-15, baseline/fused state6 binary64차이0, GL b0 gauge0. Fine Richardson h/b/y abs7.923659645081571e-11(기존 gate1e-8), finest FD scaled5.2611342089052926e-11(gate1e-6).
Full-vs-omitted 최대 차이: birth memory0.0015948771414237006, mu_b0.0011966517151371647, alpha_b0.0011963180299893739. 모두 full-vs-Richardson 오차10배보다 크며 omission의 numerical/full scientific pass는 false다. 실패한 event Pi_theta gate를 보존한다. 그림 C의 omitted-vs-Richardson 값과 위 full-vs-omitted 값은 서로 다른 비교다.
최종 checkpoint SHA256=4cef9d72e39ade7ec4ed3ed814181392fff541ec8030cd61627e8b08f54baa4b. 같은 source/input/binary의 최종 상태 restore만 검증했다. 중간 birth 경계에서 끊긴 실제 integration 재개까지 검증한 것은 아니다.
Core baseline3회 ray 순회→fused1회의 paired median1.372535191944467배, IQR[1.3680560824512806,1.4071498342403799]:24점·48ray·repeat2000·warmup2쌍+측정7쌍. Case 직렬→2worker는1.2180376690502004배, IQR[1.1874303525148253,1.4316390045734226]:4pack·repeat128·warmup1쌍+측정3쌍, subprocess/file 포함 whole-batch wall time,32개 과학 stdout의 pack별 전체bytes동일. IQR은 신뢰구간이 아니며 NCP64 속도나 보편적 가속비가 아니다.
첫 history attempt의 Python parity 실패와 이미 성공한5Rust raw를 보존했다. verifier 수리 후5개를 exact 재사용하고9Rust+1Python+1finalrestore만 새로 실행했다. R2의16logical record=5reused+11new; 전체두attempt는14Rust+2Python(실패1/성공1)+1restore다. 인프라 최초12/14, PID namespace 수리 후14/14. Case 병렬 최초 경로 오류는 core child0회, 다음 attempt만32raw다. 재사용 record를 신규 process로 더하지 않는다.
독립 physics585/585, 저장 support exact565/565, figure79/79, raw provenance23/23그룹(664파일), 결과문서31/31을 별도 범위로 읽는다. 서로 합산하여 표본수나 단일 독립 승인으로 쓰지 않는다. physics reviewer는 theory/native wrapper 작성자였지만 Rust core/history/reference/assessor 작성자가 아니며 자기 native/support 구현은 승인 범위에서 제외했다. support는 별도 root exact 검토, figure는 별도 reviewer, 문서 검토는 C8 aggregate 작성자의 own-code 승인에서 제외했다.
후속 C8 provenance5/5그룹·117파일, root C8 source/receipt13/13, 결과문서 section8 addendum12/12도 별도 범위로 완료했다. 기존 숫자와 합산하지 않는다. 각 검토의 자기 코드 승인 제외와 production 전체 chain 미실행 범위를 유지한다.
C8 aggregate 제한 검증62/62 PASS_SCOPED_SAVED_DATA_ONLY: 기존 short14case/17times의 배열 연산과 현 extended 입력 manifest, 실제 기존 upstream178file을 확인했다. verifier 내부 solver/compiler/projector/network/child0회, 외부 verifier Python1회. 실제 extended history 또는 production 전체 receipt chain 검증이 아니다.
C8 launcher 제한 검증은 19/19 PASS_BOUNDED_C8_CONTROLS다. 실제 하위 process는 Rust/Cargo version probe2개와 NCP 전용 template의 sandbox profile 거절1개다. 명시적 synthetic64CPU/128GiB fixture로 자원 축소와 봉인 worker 폭 유지·admission 보류를 확인했다. 실제 NCP hardware·full positive CLI·production resume의 검증은 아니며 actual NCP 실행은0회다.

[원 native n64 전체 case를 다시 실행하지 않는 이유]
원 S8 b9_n64_P2P4는 birth11 INNER_P2_PRECISION_LIMIT로 중단됐다. S11 점별 수리 이후 S12는 완료된 동일 schedule prior-mode raw에서 support만 읽었다. 원 failure의64개 mu가 birth11에서 bitmatch하며 geometry mode 독립성을 고정 owner/probe로 확인했다. 원 weights를 초기화·재가중하거나 새 geometry/ODE/projector를 실행하지 않았다.
z_i=mu_i^2, Z=max z_i. 정규화된 비음수 P2/P4 해는 E[z]=1/3, E[z^2]=1/5이고 z(Z-z)>=0이므로 Z>=3/5가 필요하다. birth13(u0.675,b1.0350000000000001)의 Z=0.5908471918238073이고, 기존 norm/P2/P4 gate3/10^15를 포함한 exact rational upper bound도 -0.0030509360587296598이다. 모든 finite-support moment-polygon facet을 exact 검사하여 birth0–12 strict interior, birth13–15 infeasible을 확인했다. 이는 해당 고정 native support/schedule의 obstruction이며 모든 n64 또는 새 Rust n64 history에 대한 주장이 아니다.
원 raw SHA256=fdc70eaaea45804aa16e60bba495b283eb5e4a18a576f52d5519bfd5a1f05839. Native16birth는 BLOCKED_PROVEN_FIXED_SUPPORT_INFEASIBILITY_FROM_BIRTH13이며 NCP 실행 목록에서 제외했다. Negative weights·gate 완화로 우회하지 않는다. 새 support를 택하는 연구는 별도 사전 등록을 필요로 하며 old stock/이전 birth weights는 변경하지 않는다.
Native wrapper compile-only는 C8source824에서 COMPILED_NOT_EXECUTED,13.491861557초, native histories0회로 완료했다. RAM admission/owner manifest scope/LLD thread/stale Git blob의 앞선 실패 receipt도 보존한다. 이 compile-only를 다시 할 의무는 없으며 native history 성공으로 바꾸지 않는다.

[실행 가능한 새 NCP 묶음과 접근 제한]
이번 사용자는 새 S12 준비된 연구를 위해 최대64core/128GiB NCP 활용을 승인했다. 실제 첫 DesktopCommander get_config가 monthly quota와 no retry/reconnect를 반환했다. 이번 actual NCP start_process는0회, 모든 새 S12 NCP 실제 실행은 NOT_RUN, 현재 hardware 미관측이다. 같은 거절을 재시도하거나 guessed SSH/browser/다른 경로로 우회하지 않는다. 독립적으로 유효한 서비스 접근이 제공된 뒤에만 기존 승인의 범위에서 준비된17job을 실행한다. 그때까지 코드·근거·게시·백업의 가능한 작업을 진행한다.
준비된 ncp/JOB_TEMPLATE.json은 build1 + extended history14 + 64pack serial/parallel 비교1 + ensemble1의17job DAG다. 과학 source는 f4, C8 실행 source는824다. Extended는 k16/n64, birth_end0.8, x_end1.2,49공통출력시각;11full+3omission. 이 extended14는 아직 NOT_RUN이며 short72/72로 대체 승인하지 않는다. 64pack timing은 repeat1024,warmup2쌍+측정7쌍으로 봉인돼 있다.
SCIENCE_BINDING.json:15개 불변 과학 파일, SHA256=061f9570d7d5254b97060da2599efdd95a5f993f1cbeb3d2791ed4551a6abf5f.
DELIVERY_BINDING.json:96개 실제 C8 runtime/fixedinput/template/preregistration/binding 파일, SHA256=e64930abc75d02e3b2b9d5b85a9c37e2f33e057f47c2474c1dec320d8fb3485a.
JOB_TEMPLATE.json SHA256=8c5725a8f71b36fcf13721fcf1bde76f6c1db066d59e873fbea113e7e464deb7.
DELIVERY_BINDING은 변하는 DAG/docs/results와 자기 자신을 제외한다. 전체 배송 manifest를 실행 binding으로 바꾸지 않는다. 기존 bindings/templates를 바꾸어 PASS를 재실행하지 않는다.
실제 affinity/quota, 가용RAM, owner load를 읽어 worker≤64/RAM≤128GiB에서 가능한 폭을 선택한다. 64를 무조건 강제하지 않는다. 각 job≤1800초, 측정된 전용 disk scope 전체≤4GiB, nested thread1. Build는2CPU/6GiB, history는각1CPU/2GiB이며 runner가 실제 가용 자원에 맞춰 순서를 정한다. Sandbox는 추가worker≤16/RAM≤16GiB 상한이고 관측 cgroup은8CPU/8GiB였으므로 NCP profile을 sandbox에서 실행하지 않는다.
원 owner checkout/job과 분리한 전용 scope 아래 repo와 별도 work를 둔다. Repo와 work는 둘 다 disk-root 안에 있고 work는 repo 안에 있으면 안 된다. 전체 source/dependency/toolchain/output/archive를4GiB scope로 계수한다. 소유하지 않은 process나 cache를 중단·삭제하지 않는다.
launch.py가 exact toolchain identity를 선택하거나 공식 Rust1.94.1 archive를 SHA로 확인해 private 도구를 준비하고 build dependency부터 진행한다. 사용자에게 선행 compile 명령을 요구하지 않는다. 기존 전역 Rust 설치/PATH를 변경하지 않는다. 실제 첫 실행에서 봉인한 JOB_MANIFEST.json의 width·source·경로·toolchain·dependency identity는 resume 때 유지한다. 자원이 줄면 admission을 보류하며 새 width로 재생성해 완료 성능 비교를 반복하지 않는다.
완료 PASS의 모든 declared artifact/source/input/binary/dependency identity가 맞을 때만 skip한다. 실패 attempt와 전체 raw stdout/stderr/PROCESS를 남긴다. 집계는14개 history의 source→build→binary→process→raw→assessment 연결, 실제 upstream178source와 hash, 동일한 gate를 확인한 뒤만 PASS_NEW_EXTENDED_ENSEMBLE을 낸다. Shell exit0 또는 P2/P4 일치만으로 물리 완료를 내리지 않는다.

[물리 계약·미완료 의무·배송]
Non-tilted axisymmetric Bianchi I,(-,+,+,+),a_perp=a exp(-b),a_parallel=a exp(2b),s=dot b,Sigma=sqrt(3)|s|/H를 유지한다. 새 명시적 등방 birth angular quadrature만 보정한다. 기존 photon field·physical anisotropic stock·이전 birth weights를 초기화·재가중하지 않는다. 양의 physical weights, reflection parity, source frame, 고정 owner를 보존한다. 부호가 있는 tangent derivative를 음수 physical weight와 혼동하지 않는다. Feasibility/rank/boundary/precision 실패를 구분한다.
기존 fine-reference abs1e-9, Hamiltonian/cohort-energy rel1e-11, event1e-13, donor-endpoint3e-14, clock abs1e-12 및 새 preregistration의 각 gate를 유지한다. 더 큰 tolerance, 음수 weights, 임의 support 교체로 실패를 우회하지 않는다.
남은 의무: 실제 MD14 정규화·donor closure/native Einstein/shear shared-Q 결합; evolving reactive full finite-bin spectral history; 원 S8의 전 구간을 만족하는 물리적으로 허용된 새-birth support 연구; 더 넓은 finite-d/angular 고차moment 및 P6 적용 영역/오차; 새 Rust tangent의 실제 native/reactive closure·moving event·parameter-dependent donor normalization 확장. P6 알고리즘과 manufactured short-history tangent를 미구현으로 되돌리지도, 전체 의무 해결로 확대하지도 않는다. PR17511adapter tests 역시 실제 MD14/nativefeedback 완료가 아니다.
5.369926725506957e-12는 제한된 source-deposition 설명이다. Full spectral-history 수렴 완료가 아니다. S6 rate38/344 실패·P4악화44/238, S7 실패, S8 저해상도8미달·precision1실패를 보존한다. P2/P4/P6 일치만으로 continuum/full native finite-bin 보존을 승인하지 않는다. REI production/full EoR/merge로 확대하지 않는다.
각 단계의 DAG·source/result/review·게시/readback과 provider별 백업을 보존한다. 이 metadata 직전 S12 Dropbox는 결과 fd8a9aaf까지 7ZIP·4,197,561bytes·중복 포함 payload907항목의 전체 원격 bytes/SHA256/provider hash/CRC/manifest/Git 검증 PASS다. 정확한 각 ZIP/provider ID는 s12_birth_memory/delivery/CLOUD_CHECKPOINT_INDEX.json 및 원문 readback에 있다. 이 문서를 담는 마지막 metadata ZIP과 외부 final JSON은 containing commit 게시 뒤 별도 full readback으로 확정하므로 실제 최종 총수·HEAD/tree·JSON SHA/provider ID는 최신 PR174 최종 배송 댓글을 읽는다. 아직 확인하지 않은 마지막 배송을 이 파일에서 미리 PASS로 선언하지 않으며 자기 hash를 만들지 않는다. 새 Drive는 미완료다.
새 S11/S12 Drive write는 무응답·서버 결과 불확정이며 더 이상 쓰기/재시도를 하지 않는다. 새 이중 배송은 미완료다. read-only reconcile에서 새 객체가 보이면 full-byte readback으로 검증하되 존재만으로 PASS라고 쓰지 않는다. 원 S10 양쪽 완료와 신규 미완료를 분리한다.
이 S12 단위 뒤에 완료 캠페인이나 자동 최적화 주기를 다시 시작하지 않는다. 새 물리 단위는 남은 의존성과 명시된 새 범위를 고정해 시작하며 완료 증거를 재사용한다. 실행 불가능한 서비스나 누락된 물리 계약을 완료로 꾸미지 않는다.

[Codex가 수행할 실제 준비와 단일 launcher 명령]
현재 작성 환경의 원본 repo는 /workspace/scratch/14e1021f8231/bass_work 다. 이 sandbox에서 --profile ncp를 실행하지 않는다. 아래 전용 경로는 현 workspace 기준의 구체적 배치 예시이며 아직 NCP에 존재한다고 가정하지 않는다. 유효한 NCP 접근이 독립적으로 제공된 뒤 Codex가 실제 권한/부하/용량을 관측해 NCP의 전용 경로로 바꾼다. 사용자가 이 경로 준비나 명령을 먼저 실행할 필요는 없다.

1. 기존 owner repo/jobs와 다른 새 전용 scope를 선택한다. scope/repo에는 최신 검증된 PR174 결과 checkout을, scope/work에는 이 작업의 toolchain/build/run/bundle만 둔다. dirty owner tree는 수정·reset·clean하지 않는다. 필요하면 별도 checkout/worktree를 만들고 기존 변경을 보존한다. Checkout의 current tree가 두 narrow binding의 모든 bytes/SHA/Git blob과 맞아야 한다. 결과문서가 더 최신인 것만으로 science source를 바꾸지 않는다.
2. scope 전체가 4GiB 한도에 들어가는지 관측한다. repo·work·toolchain·dependency·raw·archive를 전부 포함한다. quota/RAM/disk가 부족하면 거절 receipt를 남기며 resource cap을 늘리거나 owner 작업을 죽이지 않는다.
3. 이전 work/JOB_MANIFEST.json이 있으면 새 scope로 옮겨 경로를 재작성하지 말고 기존 절대경로의 exact resume 계약부터 검증한다. 완료 source/input/binary/dependency/artifact가 일치하는 PASS는 재사용한다.
4. 처음의 유효한 NCP 실행에서는 다음 단일 launcher를 사용한다. 기존 exact Rust1.94.1 실행 파일을 재사용하려면 관측한 실제 절대 경로를 --rustc/--cargo로 명시할 수 있다. 없으면 private official archive 준비 경로를 그대로 사용한다. 전역 rustup/install.sh를 실행하지 않는다.

BASS_S12_SCOPE=/workspace/scratch/14e1021f8231/bass_s12_ncp_8247645d
BASS_S12_REPO="$BASS_S12_SCOPE/repo"
BASS_S12_WORK="$BASS_S12_SCOPE/work"
BASS_S12_UNIT="$BASS_S12_REPO/research/bass_isotropy_response_20261018/s12_birth_memory"
python3 "$BASS_S12_UNIT/ncp/launch.py" \
  --template "$BASS_S12_UNIT/ncp/JOB_TEMPLATE.json" \
  --binding "$BASS_S12_UNIT/ncp/SCIENCE_BINDING.json" \
  --delivery-binding "$BASS_S12_UNIT/ncp/DELIVERY_BINDING.json" \
  --repo "$BASS_S12_REPO" \
  --work-dir "$BASS_S12_WORK" \
  --disk-root "$BASS_S12_SCOPE" \
  --profile ncp

위 변수 네 개는 task 전용 이름이다. 실제 NCP 전용 경로가 다르면 BASS_S12_SCOPE만 관측한 경로로 치환한다. 유효한 checkout과 disk-root 준비는 Codex가 앞 단계에서 수행하며 launcher 명령 자체가 repo clone을 수행한다고 주장하지 않는다. 정상 실행 후 동일한 절대경로·동일한 source/template/binding으로 재호출하는 경우만 exact resume 검사를 사용한다. 실패 attempt를 지우거나 existing sealed manifest를 덮어쓰지 않는다.

--preflight-only는 toolchain 준비/확인과 입력·자원 검사만 수행하며 science/build job을 실행하지 않는다. 아직 봉인하지 않은 첫 preflight는 manifest proposal만 만들므로 그 결과를 NCP 실제 실행이나 64worker 성능 결과로 게시하지 않는다. 또한 사전 점검 자체도 quota 접근 금지 우회의 수단이 아니다.

[실행 후 판정과 게시]
각 job의 PROCESS/STARTED/receipt/input/raw stdout/stderr를 보존하고, exit0와 실제 declared artifact+JSON accept를 함께 확인한다. 집계가 PASS_NEW_EXTENDED_ENSEMBLE을 내린 경우에도 이는 고정 manufactured extended14의 계약이며 full native/reactive/MD14/EoR 승인이 아니다. Omission control3개는 구조 통과와 numerical/full physics false를 유지해야 한다.
Case-parallel 결과는 실제 선택된 worker 수, affinity/quota/owner load/RAM, repeat, warmup, paired samples와 전체 scientific stdout identity를 함께 보고한다. 요청64와 실제 사용64를 구분한다. source/compiler/input/workload가 다른 과거 NCP 숫자에 직접 합쳐 가속비를 만들지 않는다.
Native b9_n64 full16birth는 exact obstruction 때문에 실행 금지이며 template에 없다. native wrapper compile-only는 이미 완료했다. 실제 MD14/shared-Q와 reactive full finite-bin은 물리 입력/계약이 없어 pending이다. 누락 case를 한꺼번에 처리한다는 이유로 이 제외 목록을 임의로 queue에 넣지 않는다.
새 결과는 source824/sciencef4와 실제 실행 receipt, 새 결과 commit, 독립 검토 commit, containing metadata를 분리해 PR174에 게시한다. 원본 실패를 포함해 DAG를 갱신하고 Dropbox 전체 bytes/SHA256/CRC/manifest readback을 남긴다. Drive는 기존 무응답 문제가 독립적으로 해결되지 않은 동안 추가 write/retry하지 않으며 새 이중 완료를 선언하지 않는다. 원 S10 양쪽 배송 완료는 유지한다.
실행 서비스가 계속 막혀 있으면 NOT_RUN과 구체적 quota 원인을 남긴 상태로 가능한 정적/게시 작업을 마무리한다. 사용자에게 precommand를 요구하거나 guessed SSH/browser로 우회하지 않는다. 이17job 뒤에 추가 최적화 cycle을 자동 시작하지 않는다.
```
