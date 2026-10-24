# BASS B3b 유한 LINE01 교환 — 연구·구현 결과

## 판정

**BASS_B3B_FINITE_LINE_EXCHANGE_20261024는 고정 계수 thick LINE01의 gross
사건수 밀도와 canonical-rest f_plus=0 유한 원자–광자 교환에 대해
PASS_SCOPED다.** 실제 REC population owner와 기존 BASS State/Source/kinetic
코드를 연결했다. 독립 코드 검토의 두 결함은 실패 probe, 수정, 같은 probe의
exit0으로 닫았다. 초기 검토와 실패는 보존했다.

일반 f_plus의 gross down/up 계산은 prescribed-boundary ledger로 완료했다.
f_plus>0 유한 photon-stock absorption, native history 결합, background IVP,
production restart는 미완이다. 전체 BASS 완료율은 null이다.

완전한 산출물은 이 lane 전체다. CONTRACT.md/CONTRACT_ADDENDUM.md에 계약,
THEORY.md와 reviews/THEORY_REVIEW.md에 유도, code/에 구현, vendor/에 unchanged
원본, results/에 명령·실패·수정·18/18 검증·49행 그림 데이터가 있다.
reviews/CODE_REVIEW_FINAL.json 및 PHYSICS_REPAIR_ADDENDUM.json이 최종 독립 수용
근거다. WORKFLOW.json, DAG.json, delivery/는 과학과 저장·게시 판정을 구별한다.

## 최신 자료의 조사와 합성

초기 조사에서는 owner 저장소51개, 관련6개 저장소의1,111 branches/874 PR
metadata를 확인했다. 모든 파일·대화 전문을 확보했다는 뜻은 아니다.
Pagination과 실제 반환 범위는 provenance/CENSUS_SYNTHESIS_KO.md 및 원본 JSON에
보존했다.

| 저장소 | 초기 branch | 초기 PR | 이번 연결에서의 역할 |
|---|---:|---:|---|
| bass | 270 | 185 | B3a 완료와 기존 core/kinetic 재사용 |
| rec_bianchi | 149 | 131 | 실제 LINE01 finite population owner |
| BASS_HE | 99 | 94 | angular/source 입수 경계 확인 |
| rei_bianchi | 264 | 222 | 중앙 authority·AGENTS·전체 DAG |
| bass_cr | 178 | 100 | 다른 source owner의 최신 상태 |
| WU088_HH | 151 | 142 | nuclear/thermal 실행·입력 상태 |

Dropbox BASS_BACKUPS는247 entries와 has_more=false, Drive BASS folder는76개
항목의 provider 응답을 확인했다. Drive 전체 inventory로 확대하지 않았다.
다른 대화는 검색된 요약/예약 상태로 확인했고 실제 source/provider ACK로
대조했다. 이미 복구된 archive는 다시 다운로드하지 않았다.

게시 전04:29:38 UTC에 변경된 병렬 owner를 다시 확인했다.
provenance/FINAL_REFRESH.json과 FINAL_PARALLEL_DELTA.md/json이 cutoff 기록이다.

- REC132는 retarded Bianchi-I characteristic/native-Wien adapter를 범위 내
  완료했지만 parent HISTORY는 PARTIAL, H5는 INPUT_DEPENDENT_UNCALIBRATED다.
  실제 history uncertainty, angular supplier/measure/full Jacobian은 미해결이다.
  새 HEAD ae189694c15e09c6f96c44ef6b74b48afc2632ac에서도 LINE01 blob
  5ac2a3107b80710504e63705ff16562131b5d1cf가 동일함을 직접 확인했다.
- HE95는 조건부 equal-sharing CCC adapter의 교정 후 검토를 보고한다.
  physical_provider_admitted=false, HE-ANG SOURCE_INPUT_PENDING은 유지된다.
  HE94의 후속 변화는 기존 과학 결과를 유지한 delivery 완료다.
- REI224는 REC132의 제한된 관측이며 중앙 전역 수용을 바꾸지 않는다.
- CR101은 조건부 finite-band CE first-event 진단이고 전체 N4/N5는 미완이다.
- HH143은 Jüttner moment 이론 checkpoint이며 reference0이다. HH142의
  두 불완전 reference 호출은 NOT_VERIFIED다. 양쪽 backup 복원 완료와
  application 완료를 구별했다.

새 병렬 결과가 이번 LINE01 직접 의존성을 바꾸지는 않았다. 초기 개수는 당시
snapshot으로 남기고, 갱신 뒤의 전체 개수는 추정하지 않았다.
중앙 AGENTS blob429a5a13ee75b1222bc50627f8d5973d01dd21c4도 동일했다.

별도 과거 Thomson Drive capsule은0/8→5/8→20/21→최종21/21의 후속 텍스트 보고를
제공했다. 기존20/21 관측을 지우지 않고 추가 지식으로 남겼다. 이 자료는
별도 Thomson prototype이며 B3a event A/B 준비, original .wl byte export,
새 independent model review와 동일하지 않다.

## 유도와 수치 구조

N은 원자 수 밀도, x=n_u/N, f=f_plus이고, 실제 source card의 g를 사용한다.
H>0와 S=sigma/H는 local source step 동안 고정한다.

\[
b=g+1,\quad F=1+bf,\quad x_e=\frac{gf}{F},\quad d_e=\frac gF,\quad
k_\ell=\frac{8\pi H}{N\lambda^3},\quad \eta=\frac{k_\ell F}{d_e}.
\]

실제 owner의 thick ODE는

\[
\dot x=-\frac{k_\ell F(x-x_e)}{g-bx}.
\]

0<=x<g/(g+1), q(n)=1+n.S.n>0와 source-owned whole-path thick gate를 요구한다.
y0=x0-x_e, z0=-b*y0/d_e, omega=eta*Delta t로 두면

\[
\omega=v+z_0(1-e^{-v}),\quad x_1=x_e+(x_0-x_e)e^{-v},\quad
\Delta x=-(x_0-x_e)a,\qquad a=1-e^{-v}.
\]

z0>-1이므로 v의 방정식은 단조이고 해가 유일하다.
원래 양수 gross rates를 dt/dv와 함께 적분하면 opacity 분모가 소거된다.
r=v-a로 두어 다음을 얻는다.

\[
\boxed{D_\downarrow=\frac{N(1+f)}F[x_0a+x_e r]},\qquad
\boxed{D_\uparrow=\frac{Ngf}F[(1-x_0)a+(1-x_e)r]}.
\]

D는 단위 proper volume당 적분 사건수다. 작은 v에서는
r=v²/2-v³/6+v⁴/24-...의 bounded alternating series를 사용한다.
대수적으로 같은 N(1+f)(k_l*f*Delta t-dx)는 absorption 시작점 x0=0에서
선도항을 빼므로 기본 floating 알고리즘으로 사용하지 않았다.

정확 LTE의 owner u=0은 net-only shortcut이다. Gross adapter는 v=omega로
해석해 D_down=D_up=N*k_l*f*(1+f)*Delta t>0와 net0을 동시에 보존한다.
Net은 큰 두 rounded gross 값을 빼서 만들지 않고 -N*owner_dx를 사용한다.
f=0에서는 D_up=0, D_down<=N*x0이므로 실제 upper population이 유한 donor다.
고정 계수 map과 두 gross 적분은 one-full/two-half semigroup을 만족한다.

6축 방향 각각1/15와8 cube corners 각각3/40는 degree5까지 구면 moment를
정확히 적분한다. A_j*q(n_j)를 사용하면 number1, flux0 및 spatial
I/3+2*S/15가 된다. 14방향의 정확성은 이 quadratic thick model의 rest N/T
moment에 관한 것이며 observer-changed event K(u)의 rational 분모까지
결정하지 않는다.

\[
\alpha_L=\kappa_{\rm grav}L^2,\quad
\mathbf k_j=\frac{E}{cP_\star}\mathbf n_j,\quad
\Delta w_j=\alpha_LcP_\star D_{\rm net}A_jq_j.
\]

실제 kinetic.moments에서

\[
\Delta\rho_\gamma=\alpha_LE D_{\rm net},\quad
\Delta\rho_a=-\Delta\rho_\gamma,\quad
\Delta p_\gamma=\Delta\rho_\gamma/3,\quad
\Delta\pi_\gamma=\Delta\rho_\gamma\,2S/15
\]

를 재현한다. 유한 state 변화의 L²와 average rate의 L³/c를 구별했다.
Source.pi는 state stress이며 이미 적용한 interval의 U/J는0이다.
입력 U/J가 비영이면 다른 rate를 지우지 않도록 transaction을 거부한다.

실제 State/Source와 photon packet moments를 대조하고 h=HL/c, sigma=hS를
확인한다. 원자 sector는 기존 E*n_u excitation을 소유해야 한다. 빈 photon
stock은 진공 branch로 처리한다. 상태와 두 stock을 함께 복사해 갱신하며,
거부 시 입력은 변하지 않는다. owner/card/scope/epoch/frame/clock/scale 및
물리 transfer ID를 연결하고 중복 charge를 막는다.

고정 geometry와 total rho/flux 보존으로 Hamiltonian/Codazzi 잔차를 보존한다.
초기 fixture의 잔차는 일반적으로 비영이다. 새 constraint solution을 만들었다는
주장이 아니며, 새 p/pi가 이후 RHS에 반영되는 것은 의도된 결과다.

## 실제 검증과 실패·교정

Wolfram의 실제19 residual groups가0이었다. 원래 rate에 대한 역미분,
net/LTE, angular 2차·4차 moment, state/rate unit 변환을 포함한다.

| 판별량 | 실제 관찰 |
|---|---:|
| 최종 unittest | 18/18 PASS |
| 원래 양수 rate의 독립 quadrature 최대 상대차 | 5.900257765644724e-16 |
| omega1e-12 absorption 시작의 작은 down count | 4.2950853810910675e-17 m^-3 |
| Decimal r oracle 최대 상대차 | 8.442749547406038e-17 |
| 정확 유리수 degree5 이하 monomial checks | 56 |
| vacuum/occupied 교환 최대 에너지 residual/gross | 1.2571e-16 이하 |
| 두 fixture의 constraint 변화 | 0 |
| L을2배로 바꾼 유한 increment 비 | 4 |
| rate를 Delta tau에 적분한 unit 대응 residual | 0 |

실패도 결과의 일부다.

1. 최초16검사 중15 PASS/1 FAIL: 14항 floating 합산 잔차3.33e-16에
   atol3e-16을 적용했다. Floating identity만32eps로 교정했고 exact rational
   oracle과 physical256eps 검사는 유지했다.
2. 독립 probe의 F1: omega50의 양수 owner endpoint를 nu_old-D 계산이0으로
   만들었다. F2: 복소수 geometry가 수용됐다. 실제 probe exit1을 보존했다.
3. F1은 n_u1=N*x1 및 아래의 동등한 안정적 구성으로 교정했다.

\[
\rho_{a,1}=(\rho_{a,0}-\alpha_LE n_{u,0})+\alpha_LE n_{u,1}.
\]

기존 constant atomic component를 보존하며 새 reservoir/floor/clipping이 없다.
표현 불가능한 작은 변화나 양수 잔여 excitation은 명시적으로 거부한다.
F2는 모든 State/Source 물리 수치의 finite-real 선검사로 교정했다.
4. 다음 실행은 신규 경계 검사를 통과했으나 기존 거부 메시지 assertion이
   앞선 동등 guard에서 바뀌어17/18이었다. 계약인 unrepresentable 거부를
   검사하도록 assertion만 교정했다.
5. 최종18/18, 같은 독립 probe exit0. omega50에서
   n_u1=3.878639060635223e-14 m^-3,
   rho_excitation=1.3161275159163052e-24가 실제 owner와 일치한다.

독립 이론·코드·그림/repair-impact 검토를 수행했다. 별도 cross-model review로
표시하지 않는다. 원래 event 준비의 NumberQ 오류/NumericQ 교정과 과거 B3a
실패 기록은 parent에서 보존되며 새 실행으로 바꾸지 않았다.

## 실행·비용·재현

실제 cwd는
/workspace/scratch/fe69646d3c76/bass_source/research/bass_b3b_finite_line_exchange_20261024
이다. 실제 scientific child argv는 ["python","code/reference_runner.py"]다.
Guard를 포함한 재현 명령은 python code/run_bounded.py python code/reference_runner.py
이다. 실행별 argv/cwd/exit/stdout/stderr/wall/CPU는 results/EXECUTION_LEDGER.json에 있다.

| 분류 | Wall s | CPU s |
|---|---:|---:|
| 구현 성공·실패5회 전체 | 7.141907655022806 | 7.074283 |
| 독립 결함 발견·수정확인 probe2회 | 0.8012240359967109 | 0.800168 |
| 이번 실제 Wolfram kernel | 0.128027 | 0.1274340000000005 |
| 이번 측정 scientific subtotal | 8.071158691019516 | 8.001885000000001 |

Fresh Python3.12.14와 g++ compile/run은 실제 성공했다. Runtime probe wall
0.154530278s는 별도이며 CPU 미측정이다. Network/orchestration/backup은
scientific subtotal에 포함하지 않았고0으로 간주하지 않았다.

신규 IVP0, 과거 campaign replay0, 기존 archive download0이다.
34.1262904040002초는 과거 부분 합계이며 잔여 예산이 아니다.
remaining_campaign_wall_seconds=null, remaining_campaign_cpu_seconds=null,
budget_reset=false다. 이번120s ceiling은 새 경량 작업의 prospective guard다.

## 전체 목표와 다음 의무

B1 exact historical pytest argv/cwd는 미확인이다. S1/S2 전체 byte recovery,
110 payload 검증, 실제 curved command/exit0는 재사용했다. B2는 선택된 V/VIII,
tau=[0,0.8], gate2e-8 범위의 수용이며 결합 trajectory의 interval certificate가 아니다.

B3a event-source와 B3b의 실제 f=0 emission receiver는 완료했다.
B3 전체는 유한 f>0 photon bath/absorption, history/각분포 결합, bounded coupled
evolution이 남아 PARTIAL이다. 현재 monochromatic packet과 prescribed f_plus로
새 finite bath occupation normalization을 만들지 않는다. 실제 spectral stock/
line-boundary owner를 특정하는 다음 계약이 필요하다.

REC132의 특성선 결과는 관련 근거지만 누락된 physical uncertainty·angular measure를
채운 것으로 읽지 않는다. B4 restart와 B5 전체 domain validation은 미실행이다.
Merge와 production activation은 수행하지 않았다.

## 백업·게시

S0는 R1–R9/C1–C4 준비를 묶은 누적 checkpoint로 Drive/Dropbox ACK 및
Git46b114144d93783f9ff4426c915b7a505afdb284, Draft PR186을 확보했다.
S1은 검증 완료 science payload, S2는 실제 delivery ACK와 handoff closeout이다.
각 stage가 어느 checkpoint에 포함되는지는 WORKFLOW.json에 명시한다.
20개의 별도 업로드를 주장하지 않는다. 최종 S1/S2 identity는 delivery의 실제
ACK를 따르며 scientific PASS_SCOPED와 별개로 기록한다.

