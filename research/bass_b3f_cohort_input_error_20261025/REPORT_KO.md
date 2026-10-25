# BASS B3f: 유한 cohort 입력 오차와 각도 오차의 합성

## 과학 판정과 범위

**BASS_B3F_COHORT_INPUT_ERROR_20261025 = PASS_SCOPED.** 명시적으로 이어 온 physmath-research-loop **1.0.0**을 유지했다. 부모는 BASS PR189의 final HEAD 6c933f324fe54d1f590bc8ab121032702659e00a, 과학 snapshot 338f982721336dabbe6cced765edf97a896428d5다. 현재 소유 lane은 research/bass_b3f_cohort_input_error_20261025/이며 게시 대상은 Draft PR190이다.

이번 결과는 **공급된 유한 endpoint 입력 R/S/n의 변화가 질량 없는 cohort의 에너지·전체 텐서에 주는 오차와, 그 오차를 기존 B3e 각도 적분 오차에 더하는 충분조건**이다. 실제 B3c/REC history의 오차를 추정한 결과가 아니다. 실제 birth cohort history와 물리적으로 정당화된 입력 오차 반경은 OPEN_INPUT, native finite absorption은 OPEN_INPUT_OWNERSHIP이다. 전체 BASS physical completion은 null이다.

과학 실행과 검토는 R1–R9/C1–C9 중 종료·인계 단계를 제외한 18/20 작업까지 S1에 담는다. R10/C10과 최종 외부 ACK는 S2에서 닫는다. 단계별 현재 상태는 STAGE_LEDGER.json, 실제 전달은 DELIVERY_RECEIPTS.json과 PR190 최종 본문을 구분해 읽어야 한다. 20/20은 한정된 이번 workflow의 작업 완료이지 BASS 전체 물리 완성률이 아니다.

## 1. 현재 입력 조사에서 선택한 연구 경로

실제 runtime과 중앙 AGENTS, 부모 HEAD, 병렬 owner를 먼저 읽었다. 로컬 Git checkout은 없었고 git status/rev-parse가 실제 실패했으므로 checkout/dirty 상태를 꾸며 내지 않았다. 선택 파일만 immutable Git identity에서 받아 사용했으며 clone/worktree를 만들지 않았다. Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8과 실제 executable/environment는 EXECUTION_LEDGER에 있다.

중앙 fixed authority는 rei_bianchi의 0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17에 있는 research/orchestration_longterm_20261023/assembly/HANDOFF_bass_KO.md다. 이번 초기 중앙 관측은 8e946b46aa44581f09141184f193223277f2ec88, 나중 targeted 관측은 **3ae182311e69fe2d7cb641e7bfe30c18e24dd3d0**다. AGENTS blob 429a5a13ee75b1222bc50627f8d5973d01dd21c4와 fixed/current BASS handoff blob 55c86aabe97702d6b64631c5f24a9d1a9563820e는 그대로였다. 중앙 DAG의 7 authorities/40 planning nodes/17 integration edges를 변경하지 않았다.

접근 가능한 owner repo 최초 목록은 51개였다. 관련 9 repo의 최초 metadata pagination은 1,351 branches/992 PR였다. 실제 중앙·CR 변경 뒤 한 번 새로 관측한 **2026-10-25 07:17:00–07:17:17 UTC / 16:17:00–16:17:17 KST** census는 다음과 같다. PR190 게시 전 관측이다.

| Repo | Branch metadata | All-state PR metadata |
|---|---:|---:|
| bass | 274 | 189 |
| rec_bianchi | 155 | 136 |
| rei_bianchi | 269 | 227 |
| bass_cr | 183 | 105 |
| BASS_HE | 106 | 101 |
| WU088_HH | 157 | 148 |
| vigilode | 207 | 88 |
| CLASSIER | 1 | 0 |
| bianchi_phase_r | 1 | 0 |
| 합계 | **1,353** | **994** |

35 pages=19 branch+16 PR, terminal pages 확인, 중복0이다. 현재 전체 owner repo 목록을 재열거한 것은 아니므로 51은 최초 관측이고, 현재 전체 repo count는 null이다. Metadata 전수 pagination을 모든 파일·대화·archive의 완독으로 바꾸지 않는다. 최초 8개 PR 본문과 8개 discussion collection을 읽었으며 중앙 PR222 댓글10개와 Vigil88 댓글1개가 포함된다.

백업 조사에서 Dropbox BASS recursive265, Drive BASS214 entries/6folders, Dropbox REC recursive **7,987 entries/14pages**를 실제 확인했다. ROOT/direct458, bianchi37, research_backups171, htt7, REC backup direct126 등은 각각 명시한 목록 범위다. 소실 뒤 targeted refresh는 BASS direct147/REC direct126이고, 03:12:12 UTC 이후 수정 entry는0이었다. 검색0은 부재 증명이 아니다. Drive 검색이 알려진 ZIP을 누락한 사례와 전체 private conversation 접근 한계를 보존했다. PersonalContext는 이번 실제 probe에서 unavailable 응답을 반환했다. 과거 SERVICE_ERROR를 상속하지 않았다. 사용자 제공 TXT5개를 읽고 첨부20개를 stat했지만 archive 추출은0이다.

### 다른 owner 결과의 통합과 경계

| Owner 관측 | 이번에 유용한 결과 | 아직 닫히지 않은 연결 |
|---|---|---|
| REC136 final f9edbfe7b56ad002f1b7fb35d4c5aec4970682a4 | 실제 same-h scalar history 재구성, stable Ks 314×313 norm enclosure | 물리 epsilon/reference/endpoint/curvature/absolute history error null; finite trace·frame·clock 미결 |
| REC PB01 9637191388afe79b16d22ed76edd6a9493f9a14c | endpoint/query pullback과 Ks 합성의 새 S0 계약 | H5 물리 calibration/H6 retiming 외부 입력; 이번 BASS가 해당 작업을 중복하지 않음 |
| REC HISTORY02 C5 checkpoint | retarded crossing/direction/Wien occupation/fixed-cell tangent 구현 존재 | verification pending; 작은 최종 cohort export 확보 못함 |
| CR105 final b1aed87852d4f8994494c2ae41a913afd390eccd | ground spontaneous Milne RR consumer 20/20 scoped | 실제 photon occupation/stimulated/all-level RR/postcapture feedback 미결 |
| HE101 final 28a26f4db951ab9085180e2ecc5d600d981a1f71 | finite-mass CBA science와 전달 관측 | **19/20**, C8 OPEN/PARTIAL_EXPORT, PASS/FAIL/FAIL, CPU overshoot2, repair reserve0, physical_provider=false |
| HH148 PHYS91 4afb530bc02bc4d611bf421eccac6d6b1ba3606e | global PSD S0 이론·계약·R6 10/20 | primary/reference/Wolfram NOT_RUN, 물리 covariance 공급 미결 |
| Vigil88 final a01f1c5c78e6b06e23565cd4e482716f99efbe97 | D5 scoped20/20 | 실제 BASS owner chain OPEN, production HOLD |
| REI HI science 42f5984a78f123ce26950cec0e0b8505da3e7ce4 | massive stress 4,368 atoms와 JVP scoped20/20 | 실제 nHI/history/IC/geometry/frame/collision/photon feed 미결, L4_ready=false |

모두 owner-reported 결과이며 이번 BASS 재실행이 아니다. REC136/central REC formatting CI 실패와 test skip, Vigil authority CI 실패, HE 실행·export 실패는 삭제하지 않았다. REC PR132 scientific pin ae189694c15e09c6f96c44ef6b74b48afc2632ac의 선택 3NPZ+6modules는 현재 REC136 tree metadata와 **9/9 byte identity 불변**이었다. NPZ/old archive를 재다운로드하지 않았다.

이 조사로 실제 history 입력 계약이 아직 닫히지 않았음을 확인했다. 기존 B3c의 f_plus=0 emission+collisionless background는 owner-reported 한정 결과로 재사용한다. 이를 새로 replay하거나 cell 평균을 f_plus로 선언하는 대신, 그 다음에 반드시 필요한 **유한 입력 오차의 observable map**을 이번 실행 단위로 골랐다.

## 2. 동결한 수학·물리 계약

같은 birth sphere label n, 같은 final frame에서 정규화 평균을 사용한다.

\[
q_S(n)=1+n^\mathsf{T}Sn,\quad S=S^\mathsf{T},\quad\operatorname{tr}S=0,\quad
\lambda_{\min}(S)\ge-1,\qquad H_S=I/3+2S/15.
\]

Source의 실제 영점은 허용하며 clipping이나 투영으로 양성을 만들지 않는다. R은 det R>0인 실수 가역행렬이다. 수학적 유한 bound는 일반 R에 성립하지만 이번 수치 interface는 \(\sigma_{\max}(R)\le1,\ \sigma_{\max}/\sigma_{\min}\le2\)로 한정한다.

\[
G(v)=\operatorname{blockdiag}(|v|,vv^\mathsf{T}/|v|),\quad G(0)=0,\quad
T=\langle q_SG(Rn)\rangle,\quad F=T_{00}.
\]
\[
D=\det R,\quad W=E_bn_bD,\quad Q=WT,\quad
M=RH_SR^\mathsf{T},\quad
F_{\rm lo}={\operatorname{tr}M+ab\over a+b},\quad
F_{\rm up}=\sqrt{\operatorname{tr}M}.
\]

G는 even source의 odd flux를 상쇄한 block-diagonal integrand다. 한 ray의 flux를 포함한 전체 stress matrix라고 부르지 않는다. Euclidean Frobenius norm의 공간 회전 불변성은 Lorentz scalar라는 뜻이 아니다.

공통 birth energy \(E_b=1.6340142155180418\times10^{-18}\) J, \(P_*=E_b/c\), \(L=1\) m를 고정했다. 패킷은 \(k=Rn,\ w=\alpha_LE_bn_bDAq,\ m=0\)이며 에너지 owner는 계속 \(E=c|p|\) 한 번이다. 이번 코드가 Source/U/J/PiRate, event rate, bath/donor/bandwidth, finite absorption을 생성하지 않는다. 두 endpoint의 frame·clock·source support가 다르면 먼저 owner 계약이 필요하다.

## 3. 새 유도: 유한 map/source/prefactor 오차

### Pointwise identity와 전역 map bound

\(r=|v|,\ s=|w|,\ z=\widehat v\cdot\widehat w\)라 두면

\[
\|G(v)-G(w)\|_F^2
=2(r-s)^2+2rs(1-z^2)
=2\|v-w\|^2-2rs(1-z)^2
\le2\|v-w\|^2.
\]

영벡터에서도 연속적으로 성립한다. 따라서 inverse singular-value 인자 없이 G는 전역 \(\sqrt2\)-Lipschitz다. 이 pointwise 상수는 평행한 양의 벡터에서 달성되지만, 최적 cohort 상수나 일반적 새 정리라는 주장은 하지 않는다.

\[
r_i=\sqrt{\operatorname{tr}(\Delta R H_i\Delta R^\mathsf{T})},\qquad
s_j=\sqrt{\frac{2\operatorname{tr}(U^2)\operatorname{tr}C_j+
8\operatorname{tr}(U^2C_j)}{105}},
\]
여기서 \(U=S_1-S_0,\ C_j=R_j^\mathsf{T}R_j\)다. Source 항은 exact sixth sphere moment의 15개 pairing을 축약한 식이다. 비가환 행렬을 그대로 허용한다.

\[
h=\min(r_0+s_1,\ r_1+s_0),\qquad
|F_1-F_0|\le h,\quad \|T_1-T_0\|_F\le\sqrt2h.
\]

두 순서의 삼각부등식을 각각 증명하고 작은 bound를 택한다. Source와 map을 평균해 새로운 물리 상태를 만들지 않는다.

\[
U_{\rm pair}=\min\!\left(
W_0h+|\Delta W|F_{{\rm up},1},
W_1h+|\Delta W|F_{{\rm up},0}\right).
\]
\[
|Q_{1,00}-Q_{0,00}|\le U_{\rm pair},\qquad
\|Q_1-Q_0\|_F\le\sqrt2U_{\rm pair}.
\]

작은 determinant 차이는 일곱 개의 nonempty column-replacement 항을 합산해 평가했다. \(n_0\Delta D+\Delta nD_0+\Delta n\Delta D\)를 모두 보존했으며 1차 선형화나 작은 차이 floor를 쓰지 않았다.

### 공급된 물리 ball의 충분조건

\(e_R,e_S,e_n\)은 각각 spectral/Frobenius/density 반경이다. None/null은 INPUT_ERROR_UNSPECIFIED이며0으로 바꾸지 않는다. nominal n0>0, actual n1=0인 vacuum endpoint는 절대 bound에서 허용한다.

\[
e_R<a,\quad b+e_R\le1,\quad{b+e_R\over a-e_R}\le2,\quad
e_S\le1+\lambda_{\min}(S_0),\quad e_n\le n_0
\]
를 모두 만족하고 actual pair가 이 반경 안에 들어야 전체 ball을 보증한다. Source-zero boundary에서는 이 대칭 ball의 source 반경이0이므로, 유효한 one-sided pair라도 whole-ball 충분조건은 거절할 수 있다.

\[
\delta D=e_2(\sigma)e_R+e_1(\sigma)e_R^2+e_R^3,\quad
\delta W=E_b[n_0\delta D+e_n(D_0+\delta D)],\quad W_{\max}=W_0+\delta W,
\]
\[
h_{\rm ball}=e_R+
e_S\sqrt{\frac{2\sum_i(\sigma_i+e_R)^2+8(b+e_R)^2}{105}},
\]
\[
U_{\rm ball}=\min\!\left(
W_0h_{\rm ball}+\delta W(b+e_R),
W_{\max}h_{\rm ball}+\delta WF_{{\rm up},0}\right).
\]

Cofactor expansion과 Schatten norm 부등식으로 determinant 다항식을 증명했다. 각 분해 branch의 지배 관계로 포함된 pair에 대해 \(U_{\rm pair}\le U_{\rm ball}\)을 얻는다. 물리 ball을 사용하지 못해도 유효 endpoint pair의 절대 bound 자체가 사라지는 것은 아니다.

### B3e 각도 오차와 양의 분모 합성

부모에서 저장한 nominal angular bound와 selected K를 그대로 재사용한다.

\[
A_0=W_0B_{T,0},\quad L_0=W_0F_{{\rm lo},0},\quad B_0=W_0F_{{\rm up},0}.
\]

유효한 U에 대해 \(L_0-U>0\)일 때,

\[
C_{\rm ideal}={A_0+\sqrt2U\over L_0-U},\qquad
C_{\rm num}={A_0+\sqrt2U+2\times10^{-12}B_0\over L_0-U}.
\]
\[
U_{\max}={\tau L_0-A_0-2\times10^{-12}B_0\over\sqrt2+\tau},
\qquad \tau=2\times10^{-8}.
\]

분모 floor와 음의 Umax clipping은 금지했다. \(2\times10^{-12}\)는 empirical binary64 reserve이고 interval certification이 아니다. Truth-reference comparison의 별도 \(2\times10^{-12}\) allowance와도 역할이 다르다. Positive mixture는 물리 텐서와 각 cohort의 절대 A/L/B/U를 합산하며 R 평균이나 오차 상쇄를 사용하지 않는다.

## 4. 실제 실행 결과

고정된 24행은 21 manufactured finite pairs, 2 independent birth/final-frame comparisons, 1 positive mixture다. Nominal G3/G5는 부모 raw를 재사용했다. 변화 크기는 \(10^{-10},10^{-8},10^{-4},10^{-2}\), family는 density/map scaling/source/mixed/source-zero다. 새 truth-reference는 P3/P4의 8쌍만 GL64×128과 GL96×192로 계산했고, P4/P5 두 kinetic mapping 검사는 같은 GL32×64 rule에서 normalization과 tensor map을 비교했다. 두 mapping 검사를 continuum accuracy 증거로 승격하지 않는다.

| 실제 판정 | 결과 |
|---|---:|
| Focused test methods | **9/9 PASS** |
| 저장 row gate + deliberate control gate | **180+2=182 PASS** |
| 출력 | **24행**, failed_gates=[] |
| Pair 충분조건 | **7 CERTIFIED**, **14 BUDGET_NOT_CERTIFIED** |
| Whole-ball domain | **17 covered**, **4 NOT_COVERED_BY_PHYSICAL_BALL** |
| Whole-ball 오차 예산 | **6 certified**, **11 not certified**, 위 4개 domain refusal |
| Certified 7개 중 최대 실제 total relative error | **1.2936870629485947e-9** |
| 전체 21 pair의 최대 실제 total relative error | **0.0515176377926866** |
| 64/96 reference 최대 차이 | **2.007497406667157e-15** |
| 회전 검사 모든 지표 최대 | **4.949916335652119e-16** |
| 실제 kinetic mapping 지표 최대 | **3.161251056175737e-15** |
| Positive mixture 실제 total error | **6.877496257209542e-11** |
| Positive mixture Cnum | **5.522484728952715e-9** |

큰 변화에서 실제 오차가 크도록 만든 행도 그대로 있다. 모든 24행의 실제 오차가 2e-8 이하라고 주장하지 않는다. 충분조건으로 certified된 경우에만 해당 admission gate가 실제 total error까지 확인한다.

Pair 실제 오차가 2e-8 이하인 행은9개다. 그중 P1 epsilon1e-8은 실제1.182499689317879e-8인데 bound2.0008460909358628e-8, P5 epsilon1e-8은 실제1.2005924525176424e-8인데 bound2.0510715102716002e-8이었다. 두 행은 **실제 통과하지만 충분조건으로 보증되지 않는 보수성**을 보여 준다.

Signed energy/tensor bound violation의 최대는0이다. U_pair−U_ball의 실제 endpoint energy Q1_00 정규화 최대는 **2.764451713219432e-26**인 작은 양수로, 비교 allowance 안에 있었고 삭제하거나0으로 덮지 않았다. Raw/CSV 24 labels와 선택 수치의 독립 대조 불일치는0이고, 저장 tensor의 직접 산술 재조합 차이는 최대6.938893903907228e-18이다. 새 solver/quadrature 실행 없이 저장 값만 읽은 대조다.

### 실제로 구분한 두 잘못된 계산

- P2 epsilon1e-4에서 determinant dilution 변화를 생략하면 tensor 상대 잔차가 **0.0003548207610662296**으로 2e-8보다 크다. Isotropic scaling의 네 거듭제곱 중 세 거듭제곱을 잃는 오류를 검출한다.
- P2 epsilon1e-2에서 올바른 lower-energy 분모를 사용한 bound는 **0.06032862936913553**, nominal 분모를 고정한 값은 **0.05786037636103816**으로 **0.0024682530080973666** 차이가 난다. Input 오차를 더하면서 분모 변화만 생략할 수 없다.

### Wolfram과 독립 검토

Wolfram 15.0.1의 실제 evaluate 1회에서 **16 exact residual groups 전부0**이었다. Sphere moments, kernel identity/Lipschitz residual, isotropic STF, determinant/prefactor, two-frame invariance, budget boundary, mixture reserve를 포함한다. 이번 evaluate의 symbol repair는 없었다. Context retrieval의 NoResults/무관 ADM snippet은 근거에서 제외했다.

R6 contract, preexecution code, 실제 raw/CSV, 수정 후 실제 두 PNG의 독립 검토는 PASS_SCOPED다. Requested lower-tier executor는 gpt-6.1-sol이며 observed model identity는 null이다. 이를 실제 관측 모델명으로 바꾸지 않는다. Different-model scientific review는 NOT_RUN이다.

최초 PNG에는 overview footer와 x-axis label의 겹침, terms figure 상단 legend clipping이 있었다. 원본 source/PNG/metadata를 보존하고 root가 승인한 한 번의 margin-only repair로 닫았다. Summary만 추가 실행했고 tests/sweep/reference를 재실행하지 않았다. 수치 raw/CSV/summary/tests 4파일의 전후 SHA는 동일하다. 최종 PNG를 구현자·독립 reviewer·root가 실제로 열어 확인했다.

## 5. 실행 영수증과 자원

CWD는 /workspace/scratch/67bff5d01305/bass_source/research/bass_b3f_cohort_input_error_20261025 이다. 아래는 wrapper가 기록한 실제 child 실행이다.

| 순서 | wrapper 뒤 child | Wall s | CPU s | Exit |
|---|---|---:|---:|---:|
| 1 | tests/test_cohort_input_error.py | 0.8139556599999196 | 0.811379 | 0 |
| 2 | code/run_sweep.py | 0.823037440999542 | 0.8200689999999999 | 0 |
| 3 | code/summarize.py | 1.4678552109999146 | 1.4669949999999998 | 0 |
| 4 | code/summarize.py — 승인된 배치 수정 | 0.7576116150003145 | 0.756854 | 0 |
| Python subtotal | | **3.8624599269996907** | **3.8552969999999998** | |
| Wolfram evaluate 1회 | | 0.056437 | 0.0568249999999999 | 성공 |
| 이번 scientific subtotal | | **3.9188969269996905** | **3.9121219999999997** | |

실제 argv는 Python executable + 각 child이고 실행 명령은 python code/metered_run.py <child>였다. 최초 실행은07:38:32 UTC, repair는07:43:10 UTC에 시작했다. Start/stdout/stderr, 코드·입력 SHA, 스레드 환경, wall/CPU limit을 모두 보존했다.

Historical remaining wall/CPU=null, budget_reset=false다. 34.1262904040002초는 부분 과거 합계이며 잔여 예산이 아니다. 이번 guard120wall/60CPU, implementation60wall/40CPU, child30wall/20CPU를 지켰다. 재고 조사·문서 생성·포장·provider 대기는 scientific CPU로 측정하지 않았다. 새 IVP0, old campaign replay0, old archive download0, old NPZ download0, source transaction0이다.

## 6. 실제 소실과 복구를 구분한 전달

이번 원 S0와 private intake는 업로드 전 workspace 소실로 **LOST_BEFORE_GIT_AND_UPLOAD / ACK0**였다. Root는07:13:42 UTC에 실제 파일 부재를 확인했고 다른 두 agent도 독립적으로 확인했다. 원인은 UNKNOWN이다. Clock gap이나 서비스 동작을 원인으로 추정하지 않았다. 소실 전 scientific Python은0이었다.

원 S0는66files/759947bytes, SHA256 efb4602733f539d13cb7407f75cb0b373480bae2c286585717d995bb2326da38이었다. 원 private intake는688469bytes, SHA256 863a8822f67d5f8c7d5ca4c3aa6cc22ff9be234a0ed262c977ceee480d4b6dca였다. 최초 private Drive 시도는 NoSuchFile로 실패했다. Library의 title-only BASS_B3F 검색0은 전체 부재 증명이 아니다.

17개 검토된 과학 입력을 byte-exact 복구했고 Wolfram raw를 재사용했다. 원 private51repo metadata, 최초1,351branch/992PR raw census, 원 REC14page metadata 전체는 **미복구**다. 새 owner census와 targeted backup metadata는 새 관측으로 분리했다. 재구성된 review 문서는 원래 digest가 없는 경우 byte-exact를 주장하지 않는다.

복구 S0R는 과학 Python 실행 전에 Git commit **d17d633c20a7913fd9b7dd22ba6523e26e8ced66**, **75/75 blob+size readback**, Drive success **198_vLr12gluw4ZVsshdC0oipulOWzHkD**, Dropbox completed **id:BSpOijBcT10AAAAAAD_-CA**를 실제 받았다. Archive는666940bytes, SHA256 c67b78983d6dce76cdcd63f6c06a73fb8c6579472b2495dd0d4e38bf6dd13996다.

S1/S2의 실제 Git·ZIP·provider identity는 생성 후 DELIVERY_RECEIPTS와 외부 PR 본문에 기록한다. 과학 판정, Git full-lane identity, upload ACK, remote full-archive restore는 네 별도 축이다. Remote full-archive restore는 **NOT_RUN**이다. 각 단계는 해당 누적 snapshot으로 보호하며20개의 개별 업로드를 했다고 주장하지 않는다. Merge/production activation은0이다.

백업 복구 문서에 남았던 잘못된53repo/991PR 설명은 이번 root가 실제 census51/1351/992 및 새1353/994로 교정했다. 이는 출처 설명 교정이고 수치 결과·계약·허용오차 변경이 아니다. S0R에 들어간 이전 설명은 역사적 snapshot으로 남는다.

## 7. 다음 실행 가능한 의존성

최우선은 작은 owner export로 실제 cohort의 birth S/R/n/E_b, common frame, clock, source support와 물리 오류 반경을 연결하는 일이다. 각 반경이 정의된 norm·단위·reference·source identity를 갖춰야 한다. REC Ks norm만으로 BASS eR/eS/en을 만들어서는 안 된다.

그와 병렬로 실제 REC LINE01 incident trace를 finite receiver cell/face에 연결해야 한다. Angular/spectral/time support, finite donor, normalization, frame, observer clock, internal-energy 귀속과 atomic term의 독점 owner가 닫혀야 유한 absorption을 채택할 수 있다. Cell average는 f_plus가 아니다. Gross emission/absorption을 구별하며 없는 bath/donor/bandwidth/clipping을 만들지 않는다.

REC HISTORY02와 PB01은 각각 geodesic/retiming과 endpoint/query pullback을 소유한다. 이번 단위에서 JVP/history integration/retarded crossing을 새로 구현하거나 old IVP를 재실행하지 않았다. B4 restart/B5 general domain은 NOT_RUN이다.

## 8. 근거와 보존할 과거 제한

이번 exact sixth moment는 표준 sphere-moment contraction을 사용한다. [Wiens (1992), author PDF](https://sites.ualberta.ca/~dwiens/home%20page/pubs/moments.pdf)의 quadratic-form moment 식과 독립 전개를 대조했다. [Sarbach–Zannias (2013)](https://arxiv.org/abs/1303.2899)는 relativistic kinetic moment의 문헌 맥락이다. SciSpace10개 결과와 Exa5개 결과를 실제 조회했지만, 문헌 검색만으로 신규성·최적성·불가능성을 주장하지 않았다. Strong no-go NG1–NG7은 NOT_APPLICABLE이다.

부모 및 이전 제한은 provenance/reused_data/의 exact handoff에 보존한다. 특히 B1 pytest argv/cwd UNKNOWN, B2 selected V/VIII/tau[0,.8]/2e-8, [PR184 실제 receipt](https://github.com/cosmosapjw-quantum/bass/pull/184#issuecomment-6373136365)의110payload/curved exit0, B3b2의 초기10tests 후3inverse+1actual targeted repair와 전체11method 재실행 미주장, B3a NumberQ7/16 실패→NumericQ16/16 및 source4/4를 유지한다.

B3b2 910packet은 hydrogen-frame scalar/unpolarized isotropic bootstrap INITIAL_DATA, coupled_macro_endpoint=false다. State boost의 w'=Dw를 invariant dR event rate에 적용하지 않는다. Source.pi와 PiRate_hat을 혼동하지 않는다. B3c는 제한된 f_plus=0 cold finite14/12IVP/tau[0,.1] owner-reported 결과이고 원 Git NO_ACK를 재시도하지 않았다. B3d의22/28 coarse-rule 실패와 B3e의 약1e-14 signed Loewner residual, 과거 raw loss·repair 이력은 새 PASS_SCOPED로 지우지 않는다.

### S1 게시 직전의 실제 병렬 변경

07:49:32 UTC / 16:49:32 KST targeted 확인에서 중앙 orchestration branch가 **b24a9daee54fc0860c4cf299c4ea5f2a977c0fd4**로 이동했다. 두 commit/69개 변경은 모두 HI strain-response lane 안이었다. AGENTS와 BASS handoff 원문을 새로 읽어 완전히 같음을 확인했고, 중앙 planning DAG도 변경 경로에 없었다. BASS PR189 및 현재 B3f branch는 각각6c933f324fe54d1f590bc8ab121032702659e00a와d17d633c20a7913fd9b7dd22ba6523e26e8ced66 그대로였다.

새 REI HI science **190e283357f49f287ab02442a3751959cc53b4bd**는 처음 등방인4,368 native atoms의 same-birth/frame 순간 strain response와 amplitude/mass/strain JVP를 채택한 owner-reported 결과다. 저장 W/S/A/K/L을 재사용하고 R/R_M만 새로 적분했다. 실제 history/density/geometry/clock/collision/photon feedback는 OPEN, L4_ready=false다. Science18/20와 실제 delivery commit 관측을 구분한다. 그 owner의 최종 외부 readback receipt까지 별도로 읽었다고 주장하지 않는다.

이 변경은 B3f의 massless finite endpoint 계약이나 실제 cohort/receiver 입력 결손을 바꾸지 않았다. 전체 census와 과학 계산을 반복하지 않고 현재 출처·영향 판정만 provenance/S1_SOURCE_PUBLICATION_REFRESH.json과 선택 owner 원문 두 개에 보존했다. 이후 게시의 branch 이동은 별도 실제 expectedSHA로 제어한다.

## 9. S1 실제 전달과 S2 종료 조건

S1 최종 scientific snapshot은 **3fd81005baf5b978fe3566a8d189c3dc792f3065**이며 full-lane110/110 blob·size readback이 통과했다. ZIP1,224,484bytes, SHA256354d8c300a4d67422793479de222cfd2c49e3c60d6404f1bd5477809b532550f, Drive success1LYPK0Ryn4jdmBgYTIA-ojB6TS3mL2b6k, Dropbox completed id:BSpOijBcT10AAAAAAD_-DA를 실제 받았다.

첫 Git transport commit81aa098c8eeb34a3e54725f1268d612266acd1b7는109/110match였으며 CSV의25CRLF가LF로 정규화되어6015→5990bytes였다. 원래6015byte CSV를 base64 blob으로 게시한 한 파일 교정 뒤110/110이 되었다. Local CSV·ZIP·수치 값은 바뀌지 않았고 과학 재실행은0이다. 이는 전송 byte-identity mismatch이고 scientific failure가 아니다. 실패와 수정 commit을 둘 다 provenance/S1_TRANSPORT_BYTE_REPAIR.json에 보존한다.

S2에는 실제 S1 receipt, 최종 handoff와 단계별 index를 담는다. 이 파일을 포장할 때 실제 완료는18/20, 준비된 종료 활동은20/20이다. **Enclosing S2 Git 게시·full-lane readback·Drive success·Dropbox completed가 PR190 외부 최종 receipt에 기록된 뒤 R10/C10을 포함한 이번 workflow20/20을 실제 완료로 읽는다.** Self SHA나 self upload ACK를 archive 안에서 만들어 내지 않는다. 전체 BASS physical completion=null, native actual input obligations와 B4/B5 상태는 그대로다.
