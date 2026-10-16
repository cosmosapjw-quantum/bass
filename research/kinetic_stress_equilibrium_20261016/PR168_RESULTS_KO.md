# BASS 비-LRS FD96 응력·Hessian: 실제 source 검산

기준은 PR167 `fe48e9a90a14bc6bad09941763a15aad34505e2c`이며, 원본 `bianchi/matter/freestream.py` Git blob은 `8467932c3281f9d426712b3a582f2aae3a484692`이다. 원본의 고정 canonical momentum, FD96 `q²/(exp(q)+1)` radial 분포, GL96 radial 및 GL24×24 full-sphere angular 구적을 그대로 사용한다. PR164/167의 기준 에너지 적분 `N`과 같은 정규화로 LRS 축대칭 `W=1+A P₂(n_z)`를 적용한다. `C=0`만 원래 PR164/167 분포이며, `C≠0`의 `W=1+A P₂(n_z)+C(n_x²−n_y²)`는 별도로 표시한 양의 reflection-even 확장이다.

두 독립 좌표 `u,v`에 대해 `β=(u,v,−u−v)`, `a_i=a exp(β_i)`, `E=sqrt(m²+Σq_i²/a_i²)`이다. 실제 full tensor는 `P_ij=∫ f p_i p_j/E`, `π_ij=P_ij−δ_ij tr(P)/3`이고, 고정 source의 `∂β_iρ=−P_ii`, `H_ij=2δ_ij w_i/E−w_iw_j/E³`을 적분한다. 코드에서는 `BᵀHB`의 두 고유값을 검사한다. 원래 angular weight는 각 좌표축 반사에 대해 even이며, 반사에 odd인 양의 `1+0.4n_x n_y` 제어를 주입하면 대각 Einstein source admission을 거부한다. 검사용 full tensor에서는 그 경우 `P_xy≠0`을 실제 계산한다.

LRS `β=(−b,−b,2b)`의 원래 PR167 에너지·평균압력·`ΔP`·각 방향 압력·`−2χ_b` 대조 24개에서 최대 절댓값 차이는 각각 `3.3306690738754696e-16`, `5.551115123125783e-17`, `1.2212453270876722e-15`, `8.326672684688674e-16`, `6.661338147750939e-16` (기준 에너지밀도 단위)이다. 최대 offdiagonal 성분은 `3.611534852061245e-18`이다. 원래 source 자체의 7 pytest와 신규·기존 연구 23 unittest가 exit 0이다.

고정 `(m,x,A,β)=(3,.7,.5,(.05,−.02,−.03))`에서 radial `64/96/128/160` 및 angular `16/24/32/48`을 각각 독립 세분화했다. `160×48×48` 이산 기준에 대한 radial64의 에너지 상대차는 `2.94e-16`, angular16의 Hessian 최대 상대차는 `3.87e-13`, angular24는 `1.36e-15`다. 원시 pressure·π·Hessian 차이는 [FD96_TENSOR_CAMPAIGN.json](pr168_evidence/FD96_TENSOR_CAMPAIGN.json)에 있다. 이 수치는 구적 수렴의 이산 측정이며 연속 적분의 엄밀한 오차 상계는 아니다. MP50의 별도 고정 binary64 32×16×16 노드 평가에서 에너지 차이는 `3.388e-17`, 압력 대각 최대 `1.492e-18`, Hessian 최대 `6.939e-18` (모두 기준 밀도 단위); 이것도 연속 구적 인증은 아니다.

원본 축대칭 `C=0`에서 2D neutral root는 `u=v=−b_*`로 돌아간다. 별도 `C=.2`의 양의 triaxial FD96 radial 확장에서 `u=0.01379528555210261`, `v=−0.0779461778412526`; 압력 차이의 2D gradient 잔차/ρ는 `1.8420629022954742e-17`, 최소 제약 Hessian 고유값은 `0.0137566105711673` (기준 밀도 단위)이다. 따라서 이 비-LRS root 수치를 원래 축대칭 source 결과로 승격하지 않는다.

별도 source-only `8πG=1` 비-LRS Einstein IVP는 triaxial 확장의 15개 내부 상태에서 Hamiltonian 정규화 최대 `2.697e-16`, Raychaudhuri finite-difference 정규화 최대 `2.807e-11`, kinetic energy-work finite-difference 정규화 최대 `6.676e-11`이었다. 기준 분모와 원시 값은 [NONLRS_IVP.json](pr168_evidence/NONLRS_IVP.json)에 행별로 기록했다. `Σ=sqrt(Σ_iσ_i²/2)/H`는 양수이며 signed `σ_i/H`를 별도로 보존한다. 이는 CMB, massive FD96 allocation, photon/neutrino 계층, REI 화학이 없는 source-only IVP다.

Kinetic neutral point는 고정 source의 에너지 정류점일 뿐 Einstein 진화에 강제하는 closure가 아니다. 등방 압력도 실제 전단 0을 뜻하지 않는다. Full non-LRS BASS production solver, momentum counterpart, REI callback과 EoR admission은 별도 `HOLD`다.

첫 직접 실행은 script import 경로 때문에 exit 1이었고 경로를 명시해 수정한 뒤 exit 0으로 재실행했다. 독립 검토의 최초 대조에서는 angular grid점만 양수인 `A=2,C=.001`이 연속구면에서 음수가 될 수 있고, `C≠0`의 축 permutation에서 부호가 뒤집히는 결함을 확인했다. 구면 quadratic의 세 축 계수를 직접 검사하고 원래 x/y 라벨을 permutation에 실어 보냈다. 수정 후 7개 표적 테스트, 전체 23개 unittest가 모두 통과했고 기존 campaign/IVP JSON은 재실행 SHA-256까지 동일했다. [FIRST_FAILURES.json](pr168_evidence/FIRST_FAILURES.json)에 실패와 수정 범위를 보존한다.

추가 독립 검토는 공개 진단 modifier에서 all-zero·미세 음수·overflow를 허용할 수 있음을 발견했다. 반사된 weight까지 비음수·유한인지, 전체 angular weight가 유한 양수인지, 결과 tensor가 유한 양수인지 검사하도록 수정하고 음성 대조를 추가했다. 이 입력 검사 수선은 원래 `C=0` 계산과 유효 `C=.2` 계산의 연산자를 변경하지 않는다.
