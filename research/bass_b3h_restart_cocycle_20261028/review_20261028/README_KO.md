# 현재 B3h restart 노드의 검토·수정

별도 새 노드가 아니라 PR212의 R6/C9 보조 검토와 실제 clock 결속 결함 수정이다. 원 단계18/20, 원 중앙 DAG28/88, 이번 증가분0을 유지한다. 독립 작성자 R6/C9는 NOT_RUN이며 CAS·직렬 검토로 대체하지 않는다.

## 실행 경계
기존 loader는 checkpoint32의 t를1.25s로 바꾸어도 받아들이지만 실제 rk4는 step*dt=0.25s에서 시작한다. 새 load_for_execution은 expected_dt, 정확히 step*dt인 시각, state/reward 차원과 유한성을 검사한다. 기존 generic codec은 유지한다. canonical code/run_study.py에는 import 및 loader 호출의 두 줄만 변경했다. numerical RHS/solver/정상 입력값은 변하지 않았다.

## 새 테스트
이 review_20261028 디렉터리에서:

    python -I -S tests/test_checked_restart.py

Python 표준 라이브러리만 필요하다. 먼저 같은16개 시험에서13 assertion failures를 관측하고, 구현 후16/16 PASS했다. 세 기존 checkpoint는 float-hex 값과 계수를 그대로 보존한다. 이 실행은 옛 연구 suite나 native ODE 재실행이 아니다.

전체 source ZIP은 원 실패·성공 로그, RED_BASELINE.py, 상세 한국어 보고서, 정확 유리수 native scalar qualification 및 source metadata를 함께 보존한다. Git은 실행 가능한 helper/tests/기존 checkpoint와 선택된 요약을 게시하며 ZIP 전체와 동일한 파일집합이라고 주장하지 않는다. 후속 실제 FINAL_RECEIPT.json에 source ZIP identity와 provider ACK를 기록한다.

canonical code/run_study.py는 기존 캠페인의 caller 수정이다. 그것을 전달 확인 목적으로 실행하지 말라. 기존9/9·10/10·13/13 및 그림은 원 근거로 재사용한다. 새 native ODE/B3i/옛 quadrature/옛 전체 suite 실행은0이다.

## 이론과 조건부 경계
THEORY_REVIEW.md의 perturbed-law 유도는 기존 same-law 정리를 보존하면서 delta_a+delta_L*p_hat+r_z가 만드는 direct reward 오차를 별도로 포함한다. reward_upper는 supplied nonnegative rational bounds에 대한 보수적 Fraction 계산이며 물리 입력을 공급하지 않는다. gamma0·duration0 극한과 양의 상계를 분리했다.

저장 native cut의 상속 오차가 추가하는 count 항은2.4414482644972628e-42/V0다. QSS 평가오차와 물리 입력오차는 미확정이다. 이 추가 항을 새 완결 certificate나 관측된 correction으로 부르지 않는다.

fresh recorded child CPU0.270263s/wall0.275144503s에는 red/green 및 새 saved-operand qualification만 포함한다. 준비·원격·모델 비용은 unknown,0이 아니다. 새40CPU/120wall 검증 allocation과 과거 allocation은 각각 닫혔으며 이월하지 않는다.

다음은 같은 노드의 distinct-author R6/C9 검토다. 실제 결함 발견 전 완료 계산을 재실행하거나 다음 노드를 시작하지 않는다. Central/foreign writes0, merge0, physical radii=null, L4=false, AUTO_NEXT_NODE=false.
