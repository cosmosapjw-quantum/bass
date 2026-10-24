# BASS B3a 사건률 연구 — 현재 판정과 후속 연결

현재 단위는 `BASS_B3A_REC_EVENT_ADAPTER_20261024`다.
입력으로 받은 준비 연구 `BASS_B3A_EVENT_SOURCE_20261024`를 독립 검토하고,
실제 REC LINE01의 조건부 escaping-line source를 국소 사건률 API에 연결한다.
수용 범위는 명시된 source의 순간적인 gross/net four-force와 pressure-rate,
그리고 BASS의 source-only U/J 인터페이스다. 전체 B3 및 B4/B5 판정은 DAG.json을 따른다.

## 1. 보존한 기준과 실제 읽기

BASS owner는 `28b7705cbb236c26e1b273335f6da7e9da4d1aaf` / PR184
Draft/open/unmerged였다. 중앙 authority는
`rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`의
`assembly/HANDOFF_bass_KO.md`다. BASS root/research/lane의 AGENTS는 존재하지
않으며, 중앙 AGENTS `429a5a13ee75b1222bc50627f8d5973d01dd21c4`를 읽었다.
원 소스·보고서·receipt의 실제 identity는 SOURCE_INDEX.json과 reviews의 intake에 있다.

[추가 recovery receipt](https://github.com/cosmosapjw-quantum/bass/pull/184#issuecomment-6373136365)의
S1/S2 whole-byte 복구와110 payload 확인을 재사용했다.
이번 단위에서 원 archive를 재다운로드하거나 기존18 IVP, 기존 pytest suite,
기존 그림을 재실행하지 않았다. B1의 당시 pytest argv/cwd 공백은 유지된다.
B2의 selected V/VIII finite-window 결과와 고정 gate2e-8는 원래 범위 그대로다.

34.1262904040002초는 부분 과거 wall subtotal이다.
`remaining_campaign_wall_seconds=null`,
`remaining_campaign_cpu_seconds=null`, `budget_reset=false`를 유지했다.
새 adapter의 실제 process 비용은 results/VALIDATION_RECEIPT.json에 별도로 누적한다.

## 2. 사건률의 정의, 관측자와 c

좌표 x0=ct, signature(-+++), u.u=-1로 둔다.
dR은 invariant dV4/c=dt_proper dV_proper당 광자 사건률이며
적분 후 단위는 m^-3 s^-1이다. 기하학적 dV4당 rate가 입력되면 c를 곱하는
변환이 필요하다. p=(E/c)(1,n), E(u)=-c u.p다.

\[
Q^a=\int p^a\,dR,\qquad
K^{ab}(u)=c\int\frac{p^a p^b}{-u\cdot p}\,dR .
\]

Q는 force/volume, cQ0는 power/volume, K는 pressure/time 단위다.
광자 null 조건에서 g_ab K^ab=0이고 K^ab u_b=-cQ^a다.
관측자 rest frame에서 PiRate_ij=K_ij-delta_ij Tr(K_spatial)/3이다.

K(u)는 u를 고정하면 rank-2 tensor다. 정확한 covariance는
K'(Lambda u)=Lambda K(u)Lambda^T다. 다른 물리적 관측자의 시간에 대한 rate를
구하려면 분모를 새 observer로 바꾸어야 한다. 코드의 generic observer 호출은
K(u)를 반환하고, 단순 spatial STF인 PiRate3는 u=(1,0,0,0)에만 반환한다.

기존 kinetic.boost의 w_new=w E_new/E는 순간 상태의 proper number-density
quadrature 규칙이다. 불변 time-volume의 사건률은 boost에서 weight를 유지한다.

## 3. A/B 정확 반례와 범위 교정

A는 6축 각1/6, B는 cube-corner 8방향 각1/8, photon energy와 전체 event rate를
같이 두었다. 둘의 rest cQ/P=(1,0,0,0), pressure-rate/P=I/3이다.

beta=(3/5,0,0)에서

| 대상 | 정확한 값 |
|---|---|
| cQ/P, A와B | (5/4,3/4,0,0) |
| PiRate_A/P | diag(3/10,-3/20,-3/20) |
| PiRate_B/P | diag(5/22,-5/44,-5/44) |
| 차이/P | diag(4/55,-2/55,-2/55) |
| 잘못된 density-weight 재사용의 cQ/P | (7/4,5/4,0,0) |

\[
\frac{\Delta\Pi_{xx}}P=\frac{2\beta^2}{3\gamma(3-\beta^2)}
\]
는 고정된 A/B fixture에 대해 **beta vector=(beta,0,0)**인 식이다.
일반 벡터 방향에 대해 속력 크기만 대입할 수 없다. 예를 들어
beta=(1/5,2/5,2/5), |beta|=3/5에서는
DeltaPi_xx/P=-286408/10384605이다.

각분포가 같은 경우의 G1B massless collisionless radial reduction은 그대로다.
이번 비교는 각분포가 다른 두 event measure를 다룬다.
신규성이나 보편적인 no-go 정리는 주장하지 않는다.

독립 Fraction antipodal-pair 계산23개가 정확하게 통과했다.
새 Wolfram15.0.1 호출에서도 위 fixture, scalar-axis general residual0,
oblique rational value, null trace0를 직접 확인했다.
원본 준비 연구의 NumberQ 최초7/16 실패→교정16/16과 추가4/4는 사용자 receipt로
보존했다. 원래 full Wolfram transcript를 새로 읽었다고 소급하지 않았다.
별도 PR 댓글6375578986의 Thomson wrapper20/21와 남은 Return-inside-Do 문제는
별도 역사로 기록했다.

## 4. 선택한 실제 공급자

REC PR130의 현재 tree
`93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa`에서
`research/rec_line_source_20261023/code/line_source.py`의
LINE01 `standalone_detached` owner를 선택했다.
원본 code/escape_moments.py, vendor/hyrec_spike_transfer.py와 license를
그대로 보존했다. source pin과 byte 비교는 SOURCE_INDEX.json에 있다.

이 source는 matter-comoving local orthonormal frame, proper seconds와
proper density를 사용한다. H>0, Delta=g n_l-n_u>0,
q(n)=1+n.S.n>0, 방향에 무관한 blue-boundary f_plus와
unpolarized recoil-free bound-bound model을 가정한다.

\[
dR_\downarrow
 =A n_u(1+f_+)\beta_{\rm esc}(n)\frac{d\Omega}{4\pi},\qquad
dR_\uparrow
 =A g n_l f_+\beta_{\rm esc}(n)\frac{d\Omega}{4\pi},
\]
\[
\beta_{\rm esc}(n)=\frac{1-e^{-\tau_0/q(n)}}{\tau_0/q(n)},\qquad
R=R_\downarrow-R_\uparrow .
\]

이는 quasi-stationary resonance radiation을 제거한 effective escaping channels다.
실제 원본의 bound-bound Einstein/escape convention은
[Hirata–Forbes2009, eqs.(1)–(3)](https://arxiv.org/html/0903.4925v2)와 비교했다.
방향 확장과 BASS 변환은 이 단위에서 유도·구현한 연결이다.
이 primary paper의 quasi-stationary/redistribution 가정도 모델 범위로 보존했다.

원본 _principal_rule은 한 octant의 squared direction을 반환한다.
새 adapter는 각 node에 대해8개 sign을 모두 복원하고 eigenbasis를 실제 frame으로
회전한다. 이 경로는 scalar B와 STF Q만 boost하는 잘못된 축약을 피한다.

Native scalar extract의 n_l,n_u,H,f_plus를 재구성해 실제 LINE01 함수를 호출했다.
S는 명시적인 rotated triaxial fixture다. 원 native angular history는 저장되지
않았으므로 이 결과는 detached source의 native-scalar-input 평가다.
최신 LINE02/REC-HISTORY signed net boundary API와 혼동하지 않는다.

## 5. 에너지 귀속과 BASS 연결

선택한 원본 owner는 atomic excitation energy를 실제 반대쪽으로 지정한다.

\[
(\dot u_{\rm atomic,int},\dot u_\gamma,\dot u_{\rm thermal})
=(-E_\ell R,+E_\ell R,0).
\]

Gross down/up를 각각 비음수 measure로 보존하고 net의 부호를 유지한다.
bound-bound ionic/free-electron yield는0이다. 프레임을 바꾸어도
Q_atomic=-Q_gamma이며, 이것만으로 matter PiRate를 정하지는 않는다.

\[
U=\frac{\kappa L^3}{c}\dot E,\qquad
J^i=\kappa L^3 f^i,\qquad
\widehat{\Pi}_{\rm rate}
=\frac{\kappa L^3}{c}\Pi_{\rm rate,phys}.
\]

U/J는 Source.energy_transfer/momentum_transfer에 대응한다.
기존 Source.pressure/pi는 caller가 준 상태 응력을 복사하고,
PiRate_hat은 별도 결과로 반환한다. clock/frame/epoch, 중복 charge와
positive-domain callback 거부를 시험한다.

finite photon stock, population transaction, source-age/history receiver가
없는 상태에서는 finite stock advance를 수행하지 않는다.
callback이True인 시험은 합성 인터페이스 시험이며 실제 photon reservoir를
인증하지 않는다. source-only 균형을 coupled physical feedback 수용으로
확대하지 않는다.

## 6. 검증·판정 위치

- results/VALIDATION_RECEIPT.json: 새 실행의 argv/cwd/exit/stdout/stderr와 누적 비용.
- results/CURRENT_REFERENCE.json: 실제 source 호출과 gross-normalized finite-grid 비교.
- results/AB_EXACT_BOOST.csv 및 PNG: 새 event-adapter 진단 그림.
- reviews/THEORY_REVIEW.md: 독립 유도, 정확23검사, 방향 범위 교정.
- reviews/SOURCE_OWNER_REVIEW.md: 실제 source/clock/energy ownership 검토.
- reviews/G1B_SCOPE_REVIEW.md: 기존 evidence의 재사용 범위 검토.
- reviews/CODE_REVIEW.md, PHYSICS_AND_FIGURE_REVIEW.md: 현재 diff의 독립 판정.
- DAG.json, CLAIMS.json, WORKFLOW.json: 단계·주장·후속 의무.
- delivery/: 실제 provider ACK와 과학 판정의 분리.

## 7. 실제 검증과 독립 검토의 최종 판정

| 검사 | 실제 결과 | 해석 |
|---|---|---|
| 독립 Fraction antipodal 계산 | 23/23, exit0 | 정확 유리수 fixture와 관측자 변환의 독립 유도 |
| 새 Wolfram 호출 | 축 일반식·trace 잔차0, 정확 fixture 일치 | 원래 16+4 검사의 재실행으로 세지 않음 |
| 초기 adapter suite | 12/12, exit0 | 뒤의 독립 검토가 두 입력/중복 결손을 발견 |
| 독립 최초 probe | 잘못된 clock/frame 및 중복을 허용 | 진단 process exit0여도 계약 판정은 FAIL |
| 추가 targeted RED | 3 tests, 실패6건, exit1 | F1 하위 검사5건과 F2 1건; 정확 zero-source는 이미 PASS |
| 최소 수정 후 targeted | 3/3, exit0 | canonical origin/clock과 physical duplicate key 교정 |
| 최종 affected suite | 15/15, exit0 | 새 정확 zero-source 검증 포함 |
| 독립 최종 재검토 | physics/math+figure 및 code 모두 PASS_SCOPED | 현재 detached instantaneous adapter 범위 |

F1은 REC factory의 원점 frame=`rest`, clock=`proper_time_dt_dV_invariant`를
강제하고 BASS mapping에서 clock을 다시 검사하여 닫았다. 실제 `.boosted()`로
생성한 대상 frame은 허용한다. F2는 charge key를 `(owner, epoch, transfer_id)`로
정하여 관측 frame 변경으로 같은 transfer를 다시 등록할 수 없게 했다.
별도의 expected identity compatibility 검사도 유지한다.

정확 zero-source는 실제 detached donor에 n_l>0, n_u=f_plus=0, S=0을 넣은
별도 검사다. gross rates, cQ, K, PiRate, U, J가 모두 정확히0이며,
callback 없이 attachment가 가능하고 caller의 상태 pi는 보존된다.
이는 LTE의 작은 gross subtraction residual과 다른 검사다.

수정은 위 검사와 key에 국한되며 moment kernel, donor source와
reference JSON/CSV/PNG가 처음 검토 때와 바이트 동일하다.
따라서 수학·reference·그림 판정을 재사용했고 해당 계산을 반복하지 않았다.

| 동일 finite quadrature의 실제 source 비교 | gross-normalized discrepancy |
|---|---:|
| Native scalar inputs → LINE01 energy | 1.9453006649083304e-16 |
| Native scalar inputs → LINE01 PiRate 최대 성분 | 4.070403924557633e-16 |
| 구성 emission fixture | 1.2070126599814901e-15 |
| 구성 absorption fixture | 2.6822503555144215e-16 |
| LTE net/gross | 2.19456847269362e-16 |
| A/B curve numeric−exact 최대 절대 잔차 | 4.440892098500626e-16 |

현지 gate는5e-12이며 gross scale을 분모로 삼는다.
12×20 principal nodes의 8 sign 복원으로1920 방향을 사용한다.
동일 quadrature parity는 angular continuum convergence를 인증하지 않는다.
원 native angular state도 이 입력에는 저장되어 있지 않다.

## 8. 자원·의존성과 게시

새 Python 실행5개의 wall 합계는5.127101682999637초,
CPU 합계는5.1194999999999995초다. 최초 실패 실행도 포함한다.
독립 reviewer probe 두 번은 wall1.2357569410087308초,
CPU1.2340099999999998초다. Fraction 내부 계측을 포함한
**계측된 새 부분 합계**는 wall6.3684287650103215초,
CPU6.359076642999999초다. Wolfram의 실제 kernel elapsed/CPU와
모델 추론·편집·네트워크 시간은 이 합계에 포함되지 않으며,
Wolfram에 요청한25초 ceiling을 실제 시간으로 바꾸어 쓰지 않는다.
원 campaign의 잔여 wall/CPU는 계속 null이고 budget_reset=false다.

| 단계 | 현재 과학 판정 | 남아 있는 경계 |
|---|---|---|
| B1 | 복구 receipt 재사용, 좁은 수용 유지 | 당시 pytest의 정확 argv/cwd 미확인 |
| B2 | 기존 selected V/VIII finite-window 증거 재사용 | 전체 nonlinear/global tail 또는 전 domain 인증 아님 |
| B3a | 독립 유도·실제 source-only adapter PASS_SCOPED | 중앙 선행의 결손을 소급해서 닫지 않음 |
| B3b | REC owner·사건률·frame·clock·내부에너지 귀속 확인 | 실제 finite-stock/population transaction 및 receiver 연결 필요 |
| B3c | 이번 실행 없음 | bounded coupled test는 아직 admission되지 않음 |
| B4/B5 | 보류 | restart parity와 범위별 물리·수치 검증 필요 |

총 완료율은 null이다. 현재 PASS는 즉시 사용 가능한 국소 rate/reference
경로를 뜻하며, production 활성화 또는 merge 승인으로 해석하지 않는다.
다음 실행 전환은 선택한 REC owner의 실제 receiver/finite-stock 계약 확인이다.
존재하지 않는 reservoir를 추가하거나 positivity clipping으로 결손을 숨기지 않는다.

게시와 백업 ACK는 `delivery/`의 실제 provider 응답으로만 기록한다.
과학 판정은 위 결과와 독립 검토이며, ACK가 그 판정을 대체하지 않는다.
단계별 증거는 작은 공동 capsule에 묶어 보관하므로 각 단계의 ACK가
같은 capsule을 가리킬 수 있다. 개별 단계마다 당시 업로드가 있었다고
소급해서 주장하지 않는다.


