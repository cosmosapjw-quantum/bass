# 다음 스레드: BASS G1A 이후 G1B

```text
$physmath-research-loop로 BASS background kinetic 연구를 이어가라.
repo: cosmosapjw-quantum/bass
PR183: Draft/open/unmerged
branch: research/background-kinetic-g1-20261023
source implementation pin: b456e218213fda302cf6e5168f8beb608eeb3e1b
parent PR182: df2f5c78d49ea27b3d48fd2aaebb4add9f2d7f6e
unit: research/background_kinetic_g1_20261023/

최신 branch/PR 및 DELIVERY_FINAL.json부터 읽고 REPORT_KO.md, THEORY.md,
DAG.json, evidence/SOURCE_LOCK.json, evidence/CURRENT_EXECUTABLE_LOCK.json,
evidence/controls_001/RESULTS.json을 확인하라.
Git selected source와 full raw archive를 구분하라. 전체 archive는
BASS_G1A_S2_20261023.zip이며 exact provider ID/SHA는 최신 DELIVERY_FINAL.json에 있다.
현재 파일이 없으면 연결된 provider에서 직접 복구하라.

G1A는 일반 Bianchi normal-frame의 양의 finite collisionless measure closure다.
새 18IVP=12family+3tight+1rotating+1newIXturnaround+1negativecontrol.
17정상+1의도적 잘못된 Class-B 가중치이며, 과거 캠페인 재실행0이다.
고유9pytest그룹, actual FD96 55296node 순간 검사6개, Wolfram exact
{0,0,{0,0,0}}을 보존한다. 새 독립 subagent 심사는 NOT_RUN이었다.
같은 입력/코드의 완료 적분과 도표는 다시 만들지 마라.

Fixed units tau=ct/L, k=p_phys/Pstar, m=m_phys*c/Pstar,
w=kappa*L^2*c*Pstar*proper_number_density를 유지하라.
k'=-h*k-sigma*k+R cross k+[(a.k)k-a*k^2-k cross(n*k)]/E.
(logw)'=-3h+2a.k/E. a는 spatial structure vector다.
Local boost의 w'=w*E'/E를 유지하고 이를 global tilted solution으로 오인하지 마라.

핵심 negative control: wrong-weight V는 core constraint4.8901e-12인데
kinetic constraint7.9509e-3, rho/flux mismatch1.3636e-2다.
따라서 Einstein constraint와 microscopic-to-ledger mismatch를 모두 감시한다.

다음 G1B는 smooth-source의 positive quadrature와 tail/normalization 계약부터다.
원 freestream의 clipped exponential finite-node source와 실제 연속 FD 함수를
구별하고 기존 finite-node bytes를 임의로 바꾸지 마라. Planck photon은 별도 source다.
먼저 frozen-state radial/angular refinements를 분리하여 기준을 세우고,
그 다음에만 새 curved kinetic IVP의 time/grid error를 분리해 계산하라.
작은12packet benchmark를 smooth FD96 convergence로 승격하지 마라.

새 HE37/REC LINE01의 최신 변경은 조사하되 electron-STF rate, angular emission
injection과 current total-gas/photon stress를 혼합하지 마라.
G2 완전한 four-force 소유권, G3 production/restart, G4 global convergence는 남는다.
현재 runtime은 실제 probe하고 과거 실패를 상속하지 마라.
각 단계 실제 게시/백업/검증범위/DAG를 기록하고 merge·production 활성화는 하지 마라.
```
