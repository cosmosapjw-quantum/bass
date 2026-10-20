# S9 figure 08→07 검수

## 그림 의도와 의미

Figure1은 실제 기록된 h,b,y 상태와 고정 S8 수치 참조의 같은 출력 시각에서의 절대 잔차를 보여준다. Figure2는 사례별 기록 오차를 바꾸지 않은 사전 gate로 나눈 값이다. Figure3은 기록된 solver work와 이 실행환경에서의 process 경과시간을 보여준다. 모든 상태변수와 x는 무차원이다. 잔차를 물리적 상태값으로 나누지 않고 정확히0인 값도 symlog축의 선형 구간에 유지한다.

## 08차 최초 감사와 수정

최초 영수증은 ../AUDIT08_INITIAL.json이다. 첫 렌더에서 Figure1의 완료 수 제목이 공통 범례와 겹쳤고 Figure3 범례가 낮은 Jacobian count 곡선을 가렸다(P1). Figure1 완료 수를(a)패널 제목으로 옮기고 Figure3 범례를 패널 위로 옮겼다.

두 arm 모두 rtol1e-8과1e-10의 전체 observation 배열이 정확히 같아 곡선이 겹친다. 해당 사실을 캡션에 명시했고 수렴차수를 추정하지 않았다. 또한 두 arm의 RHS 호출 수가 모든 tolerance에서 같으므로 MF 원과 Small+clock 속이 빈 사각형을 같은 좌표에 그려 겹침을 드러냈다(P2). 데이터 좌표를 벌리거나 수치값을 바꾸지 않았다.

## 07차 잔여 오류 검수

세 최종 PNG를 직접 확인했다. 제목·범례·축·tick·heatmap숫자에 남은 겹침이나 잘림은 발견하지 못했다. Figure2는 행별 모든 PASS의 전체 검증 범위를 숫자6열과 구분하며 나머지 exact stock/moment/workspace 계약은 캡션과 원 assessment로 추적된다. 경과시간은 단일 실행·process/I/O 포함 값이며 이 환경의 진단으로 표시한다.

180mm폭에서8–9pt본문과 라벨을 사용한다. 90mm축소 시4–4.5pt가 되므로 해당 축소 사용은 승인하지 않는다. 원본과 최종 SVG/PNG가 모두 보존돼 있다.

## 판정

**PASS — 180mm 보고용 그림 범위.** 의미·표현·출력시각·gate를 유지하면서 발견한P1/P2문제를 해결했다. 논문의 수렴차수·continuum angular 정확도·portable speedup 등으로 해석 범위를 확대하지 않는다. 이 agent는 ODE를 실행하거나 frozen13source·3input을 변경하지 않았다.
