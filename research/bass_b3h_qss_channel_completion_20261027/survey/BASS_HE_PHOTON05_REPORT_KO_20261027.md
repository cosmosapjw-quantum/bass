# BASS_HE 연구 재개 보고 — PHOTON05

**새 조건부 수치 검증은 24/24 PASS다. 저장자료 그림은 생성됐지만 CPU 한도 초과로 FAIL이며 전체 workflow는 partial이다.** 기존 STATE04와 HE101의 완료·실패·예산을 그대로 보존했다. 실제 raw outcome은 `evidence/validation/` 및 `evidence/plot/`, 독립 판정은 `review/`를 따른다.

## 새로 제공하는 계산

정지 bare ground-state alpha에 광자가 입사하여 두 bare ground-state deuteron을 만드는 exclusive 사건에 대해, 두 생성물의 lab 에너지·운동량·상대론적 응력 및 단일 에너지 원장을 구현했다. 입력은 NIST의 2022 CODATA nuclear rest-energy 중앙값과 기존 EXFOR M0475002의 12개 native 에너지·CM 각도 좌표다.

질량 입력은 alpha `3727.3794118 ± 0.0000012 MeV`, deuteron `1875.61294500 ± 0.00000058 MeV`이며 MeV 표기가 canonical이다. 공분산을 확보하지 않았으므로 두 오차를 독립이라고 가정하거나 결합 physical error band를 만들지 않았다. 원문은 [NIST allascii](https://physics.nist.gov/cuu/Constants/Table/allascii.txt), 관측·해시는 `sources/SOURCE_MANIFEST.json`과 `PHOTON05_SOURCE_OBSERVATIONS.json`에 있다. EXFOR 원전은 [고정 IAEA-NDS M0475](https://github.com/IAEA-NDS/exfor_master/blob/939a14d7bba1ddce51975cb5e8711ce96b3b0871/exforall/M04/M0475.x4)다.

이 계산은 선택한 질량값과 bare-nuclear·stationary-target 계약에 조건부인 운동학 사상이다. 측정의 liquid-He 표적, 전자 spectator, 표적 운동·beam response·angular acceptance·polarization·particle/event normalization을 실제 소비자에 결속하는 일은 남아 있다. Native DCS 및 통계 ERR-S는 그대로 보존하고 사건 flux로 사용하지 않았다. phi=0은 명시적인 대표 평면이다.

## 문턱과 사건의 에너지 소유권

에너지 단위의 4-vector를 `q=(E,c p)`로 쓰고, target rest energy를 A, 각 daughter rest energy를 M, 광자 에너지를 e라 하면

\[
s=A^2+2Ae,\qquad
\Delta=2M-A,\qquad
e_{\rm th}=\Delta+\frac{\Delta^2}{2A}.
\]

저장된 중앙값 계산은 `Delta=23.846478200000092 MeV`, `e_th=23.922758940396797 MeV`다. 단순 정지에너지 결손 외에 약 76.281 keV의 문턱 반동이 있다. 합성 대조군 A=M=2, e=3에서는 CM momentum이 0이어도 각 daughter의 lab E=2.5, cp_z=1.5, K=0.5가 남는다. 이 검사는 photon momentum을 지우는 잘못된 문턱 모델을 구분한다.

한 사건의 원장은

\[
-e+\Delta+(K_++K_-)=0
\]

이다. Nuclear binding은 이미 물리 rest mass에 포함되어 있으므로 `population_rest_energy_witness`만 rest/binding을 소유한다. 별도 binding RHS를 추가하지 않는다. Photon count −1, alpha count −1, deuteron count +2이며 baryon number와 nuclear charge가 보존된다. 물질 핵의 수는 +1이지만 `Gamma_thermal`, Cv, species heating, thermal deposition은 null이고 birth pool은 UNASSIGNED다.

Adapter의 사건 flux는 호출자가 명시하는 유한·비음수 입력이다. Native 저장 예제의 flux0은 입력 검증과 per-event 출력 보존을 위한 예시값으로, 실제 물리 사건률0을 의미하지 않는다. 데이터로부터 physical rate를 산출하거나 승인한 적이 없다. SI 경계에서 1 MeV=1.602176634e−13 J와 cp/c를 명시적으로 적용한다.

## Native 12좌표의 저장 결과

아래 수치는 `evidence/validation/SAVED_PLOT_DATA.json`에서 읽었다. 두 딸핵의 +/−는 수학적 label이다.

| 입사 MeV | CM 도 | K+ MeV | K− MeV |
|---:|---:|---:|---:|
| 213 | 46 | 116.899871154 | 72.253650646 |
| 213 | 61 | 110.156301960 | 78.997219840 |
| 213 | 73 | 103.972236543 | 85.181285257 |
| 213 | 87 | 96.258596708 | 92.894925092 |
| 258 | 46 | 146.841333031 | 87.312188769 |
| 258 | 61 | 137.849779013 | 96.303742787 |
| 258 | 73 | 129.604240686 | 104.549281114 |
| 258 | 87 | 119.319240673 | 114.834281127 |
| 330 | 46 | 195.890497988 | 110.263023812 |
| 330 | 61 | 182.956932941 | 123.196588859 |
| 330 | 73 | 171.096446303 | 135.057075497 |
| 330 | 87 | 156.302372173 | 149.851149627 |

12좌표의 저장된 4-momentum residual은 모두0이다. 가장 큰 normalized mass-shell residual은 `6.094243921453634e-17`로, 고정된 256epsilon scale 기준 안에 있다. 이 수치는 source physical uncertainty가 아니라 구현 수치 검사다.

공간 응력은 `S_ij=q_i q_j/E`이며 raw momentum second moment와 다르다. 첫 좌표의 net stress에는 photon loss가 포함되어 zz가 약 −29.3538853 MeV이므로 net source에 양의 준정부호성을 요구하지 않는다. 각 daughter의 stress와 trace, 모든 성분의 공간 회전 및 daughter 교환을 확인했다. 이 가중치는 선택 lab의 equal-time moment weight이며 전체 kinetic tensor의 Lorentz 변환에는 분포·측도도 함께 필요하다.

같은 정확한 운동량에 비상대론적 에너지식을 대입한 상대 초과 `(K_NR-K)/K=K/(2M)`는 저장 좌표에서 약 **1.926–5.222%**다. 별도 비상대론 solver를 실행한 결과가 아니다.

## 검증·그림·실패의 구분

독립 Decimal80 reference는 literal masses와 각도, 별도 삼각함수 급수, 직접 Lorentz matrix로 구성했다. Native 전체, mass shell·보존·회전·교환·azimuth, 정확한 synthetic threshold와 작은 excess, 숫자·벡터·표현 범위, SI 및 count/energy ownership을 검사했다. Photon momentum·threshold recoil·두 번째 daughter를 누락하거나 binding을 중복하는 잘못된 모델의 판별 잔차도 기존 24 methods 안에 두었다.

실행 전 발견한 여섯 사항은 첫 START 전에 교정했다. 초기 HOLD와 교정 이력은 `review/CODE_REVIEW_PREEXEC.json`에 남아 있다. 이는 실행 실패나 repair reserve 사용으로 세지 않는다.

| 실행 | 판정 | CPU s, child+runner | wall s | cap CPU/wall | 새 science 호출 |
|---|---|---:|---:|---:|---|
| 24-method 검증 1회 | PASS | 0.241060162 | 0.239336358 | 4 / 15 | 새 조건부 검증만 |
| 저장자료 그림 1회 | **FAIL, CPU 초과** | **4.407265040** | 4.406950156 | 4 / 15 | 0 |

그림 child는 exit0으로 PNG·SVG를 만들었으나 CPU cap을 초과했다. `PLOT_DATA.json`은 검증 saved data와 byte-identical이다. Root는 실제 PNG를 열어 판독했고 `evidence/PLOT_READ_KO.md`에 해석과 한계를 기록했다. 생성 파일·START·FINISH·stdout·stderr를 보존하며 plot의 FAIL을 PASS로 바꾸지 않는다. Matplotlib의 쓰기 불가능한 기본 config/임시 cache 경고는 관측됐으나 초과의 확정 원인을 측정한 것은 아니다. 재실행·추가 profiling·검증 잔여 예산의 전용은 없다.

원 INTAKE runner와 EVENT03의 ContractError/product를 그대로 재사용했다. EVENT03 비상대론 fixed-mass kernel은 호출하지 않았다. 기존 과학 suite·HE101·physical campaign START는 모두0이며, 준비·모델·네트워크 I/O 비용은 UNKNOWN_NOT_ZERO다. End-to-end CPU cap을 주장하지 않는다.

## 최종 연구 상태와 전종 의무

이번 단위는 4개 scoped product node 완료, 검증 종합 node 1개 partial, 물리 입력 3개 open이다. Partial의 이유는 생성된 plot의 CPU resource gate 실패다. 수치 참조는 독립 검토 후 수용했으나 clean full-unit PASS를 주장하지 않는다. 기존 STATE04의5/8 및 WU source-only104 IDs/138 variants/155 event references는 그대로다. 신규 global species ID나 완전한 physical differential provider를 등록하지 않았다.

이전 H1–He4 finite-drift 결과, EVENT03 조건부 반응 모멘트, STATE04 HD–H+ state edge와 LiH source correction을 재사용했다. 원HE101의 C8 PARTIAL_EXPORT19/20, reserve0, PASS/FAIL/FAIL 및 과거 소진 예산을 보존했다. 기존 science/plot/export 재실행과 예산 reset·transfer는0이다. 모든 isotope/charge/state·source-selected molecule의 의무는 소스 ZIP의 ALL_SPECIES_PROGRESS_KO.md와 이전 군별 계획에 연결했다.

남아 있는 PHOTON05 물리 입력은 M0475002 실험의 liquid-He electronic/target-motion 및 beam/acceptance/normalization 사영, 동일 source의 complete angular law와 실제 photon encounter flux, exact global IDs 및 named nonthermal/deposition consumer다. 공분산과 누락 채널을 만들어 넣지 않는다. Thermal count·Cv·binding/rest·nonthermal kinetic energy는 각각의 소유권을 유지한다. Production은 NOT_APPROVED, activation과 L4_ready는 false, global physical completion은 null이다.

## 실제 소스·전달 commit

| 구분 | 실제 commit | 실제 tree |
|---|---|---|
| S05 과학 소스 | 251c6baa6c3359b1d6997dbce51cea65500b53d6 | 80c880cc3881e1e539156d8e077d443f7bd945a5 |
| D05 전달 metadata | 4db5ce7297a7ded4624b93721873aacc9b4ebf30 | 0716e170bdd6caf4d8995daae602d330e1cf8d33 |

S05의 parent는 D04 30924d902187777fbff02687639c91d65cf53191이며 D05는 S05의 직접 자식이다. S05는65 paths, D05는 metadata-only32 paths이고 D05의 삭제는0이다. 최종 관측에서 tracked worktree/index는 clean이었다. 기존 STATE04 central/reapplied의 untracked13파일은 원인 UNKNOWN 상태로 손대지 않았고 두 committed archive에 포함하지 않았다.

## ZIP·Git bundle·이중 백업

### 소스 묶음

[BASS_HE_HE_EXP_PHOTON05_SOURCE_20261027_251c6baa.zip](https://drive.google.com/file/d/1IyO2X5mAfHA4y7aC9oi-iIR5ECccRJxc/view?usp=drivesdk)

- 크기20,425,864 bytes,434 members.
- SHA256: `d3b574ec5d4b2657d63cc23afd221d1ce6aec59b79192676ffb54fb43af26a90`
- Full program expansion, root AGENTS, 원179 dependency filename set과 실제 Git bundle을 포함한다. Source PDF는 제외한다.
- Bundle `BASS_HE_ac6042_to_251c6baa.bundle`:1,675,063 bytes, SHA256 `8ee6352df88cde7d66425025d8ba02aeb92ca3d7890896be6b727cdd1319b2b5`; prerequisite는 public base ac6042a6b0610b09d0576538767ee0299389a5eb다.
- Dropbox ID `id:BSpOijBcT10AAAAAAEDHdw`, rev `65ed122c2460d0af03d47`.
- Drive ID `1IyO2X5mAfHA4y7aC9oi-iIR5ECccRJxc`.

### 전달 후속 묶음

[BASS_HE_HE_EXP_PHOTON05_DELIVERY_20261027_4db5ce72.zip](https://drive.google.com/file/d/1xkamMw3xT31FqDhbDfvoWS4pMJmDZTks/view?usp=drivesdk)

- 크기2,203,799 bytes,35 members,32 changed paths/0deletions.
- SHA256: `25ac28965be174457a1b5e57f73f387185fc0674c9c152172a845906c206883a`
- 중앙 후보·독립 검토·소스 backup 영수증과 실제 S05→D05 Git bundle을 포함한다.
- Bundle `BASS_HE_251c6baa_to_4db5ce72.bundle`:295,676 bytes, SHA256 `7449f1fc116382a8d036ed7aef5dfd8ed344d32ecebc782f09b10044094d18b0`; prerequisite는 S05다.
- Dropbox ID `id:BSpOijBcT10AAAAAAEDHew`, rev `65ed13be39e150af03d47`.
- Drive ID `1xkamMw3xT31FqDhbDfvoWS4pMJmDZTks`.

두 파일 모두 Dropbox의 `/BASS_DERIVATION_DOSSIERS_20260912/` 및 기존 Drive 연구 backup folder에 실제 업로드했다. 각각 upload ACK와 별도 metadata ID/name/size를 확인했다. Local committed blob·actual Git bundle·ZIP CRC/member hash 검증도 PASS다. **Remote 전체 파일을 다시 내려받아 SHA256를 확인한 것은 아니다.** 두 archive builder는 각각1회이며 과학 코드나 기존 suite를 실행하지 않았다.

복구는 source ZIP 후 D05의 changed-file overlay 순서로 한다. Git 복구에는 해당 prerequisite가 있는 저장소에서 두 actual bundle을 순서대로 사용한다. Source와 tail은 서로 다른 단계의 묶음이며, D05 뒤의 실제 tail backup ACK는 함께 제공하는 최종 CLOSEOUT JSON에 있다. 원과학·plot 실패 증거를 재계산하지 않는다.

## 중앙 DAG: 검토한 후보와 이후 관측의 구분

16개 upsert 후보는 base `1a38f94fa50c763bb9df6ccc8ba569f287fe97d5`에 대해 독립적으로 `APPROVED_LOCAL_METADATA_DELTA_ONLY` 판정을 받았다. Review SHA256는 `628dca1183886e548851c01b1b0cd2a29dfdf63abf5acd6f90fc4b726038f6a1`다.

바뀌는 것은5개 node의 observation과 같은5개 CURRENT_STATUS row의 observation이다. HE-EXCHANGE/HE-EXP-PAIR는 STATE04 관찰을 그대로 옮긴다. 두 closure와 WU-led HE-EXP-NUCLEAR에 PHOTON05 관찰을 추가하되 WU lead·원계약·status·budget을 바꾸지 않는다. 검토 기준의 나머지83개와 B3h·CR proper-injection·HE101·JOINT·PHOTON-PAIR를 보존했다. 52 internal pointers와24 retained external references의 기존 기계 검증 근거를 재사용했다.

**최종 remote 확인에서는 중앙 HEAD가 `152b82cac23fedcb75a9effe0c159bae3d800c01`이었다.** 이는 B3h의 native endpoint stock inverse와 finite photon return을 반영한1commit/5paths 변경이다. Commit 시각은11:56:40 UTC이며, 이 보고의 관측이 전달 후였다는 뜻이지 commit이 D05 후에 생성됐다는 뜻은 아니다. 실제 patch는 B3h current_status·pass_next_action·observation을 바꾼다. Physical non-Lyα energy owner와 full atomic transaction은 여전히 열려 있고, 이를 HE 과학이나 카운터에 채택하지 않았다.

따라서 후보의 승인은1a38f94 기준으로 보존한다. **나중에 게시할 때는 당시 실제 central HEAD를 새로 읽고 HE 관찰 변경만 재적용·검토해야 한다.** 오래된 전체 DAG/status를152b82 또는 후속 HEAD 위에 그대로 쓰거나 expected SHA만 바꾸면 안 된다. D05·기존 후보·archive는 이 관측 때문에 다시 쓰지 않았다. 상세 post-delivery 관측은 CLOSEOUT JSON에 포함돼 있다.

## GitHub 게시의 미완료 사유

마지막 HE 원격 HEAD는 `ac6042a6b0610b09d0576538767ee0299389a5eb`다. 동일 원 DRIFT02 75-file tree payload에 대한 다섯 번째 도구 요청이 실제 `user rejected MCP tool call`로 끝났다. 추가 사유는 제공되지 않았다. 이번 turn에서 그 뒤의 GitHub 쓰기·대체 게시 경로는0이며 새 remote ref update도0이다. 자동 심사나 특정 계정 권한 문제라는 원인을 추측하지 않는다.

이에 따라 **GitHub source 게시와 원격 central 반영은 완료되지 않았다.** 실제 local S/D·source/tail ZIP·이중 backup·검토 기록은 보존됐다. 향후 게시 재개 시 실제 HEAD/AGENTS/병렬 변경을 먼저 읽고, 바뀐 base에 대한 변경을 검토한 후 expected SHA와 force=false를 사용한다. API-created commit SHA는 실제 반환값을 써야 하며 local SHA를 remote publication 증거로 취급하지 않는다.

## 다음 재개 지점

`BASS_HE_PHOTON05_CLOSEOUT_20261027.json`과 source+tail ZIP의 `continuation_photon_20261027/HANDOFF_KO.md`, RESULT, DAG, root acceptance를 먼저 읽는다. HE101 reserve0와 새 plot FAIL을 보존하며 완료한 검증·plot을 다시 시작하지 않는다. 실제 물리 후속은 실험 사영·전체 미분/encounter measure·named deposition 입력에서 진행한다. 전달 후속은 GitHub 승인이 허용된 경우 최신 central base 재적용과 expected-SHA non-force 반영이다.
