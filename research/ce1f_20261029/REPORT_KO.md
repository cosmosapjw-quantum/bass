# BASS CE1-F — 양의 각분포 표와 결합 기하 오차 인증

비음수 cell 에너지 표를 물리 입력으로 받아, 충돌 없는 질량 없는 복사의 압력 구적 오차와 비선형 Bianchi-I 기하에 전달되는 오차를 상계했다. 이론 R1–R10과 구현 C1–C10의 범위는 CE1-F다. 상위 정본 DAG는 **9/15**, CE-1은 PARTIAL이며 원래15개 ID와 의존성을 보존한다.

## 확인한 최신 상태

BASS의322개 현재 브랜치와237개 PR, 관련6개 저장소의1249개 브랜치와1347개 PR를 열거했다. 합계1571개 ref/1584개 PR는 조사 시점의 metadata 범위다. 관련 최신 source/handoff와 실제 BASS dependency pin을 대조했다. 모든 과거 commit의 의미 검토나 접근할 수 없는 대화 전체의 열람을 주장하지 않는다. 정확한 목록·조사 범위는 SOURCE_SURVEY.md와 provenance/에 있다.

재개 정본은 PR237, CE1-E a05906527d7dd5e5f6a653a0e4f7d977679d4a0c다. CE1-E 원본 ZIP844606bytes의 SHA2569105b9ef9dd0494bbb520085b9246bd0cb2e40ce1a6c92b9a776dd260f2a34e2를 실제 복원 바이트로 확인했고 실행 module/test가 현재 Git bytes와 일치했다. 다른 저장소의 최신 반응률·HD·핵종 연구는 별도 조건과 DAG에 둔다. BASS의 실제 REC/REI pin은 각각d3cc6e0120061f113d28e7a3a55a2e3dd561e81e,1bda1e8cea7629d31f905e126ba47ec3b3c1d0d8다.

## 결과와 의미

물리 입력은 첫 octant의(mu,phi) cell마다 일정한 에너지 밀도를 놓고 여덟 좌표 반사로 확장한 비음수 함수다. 표의 값은 각 cell의 반사본을 모두 합친 에너지다. cell을 세분할 때 정확한 면적 비율로 에너지를 나눠 같은 물리 함수를 유지한다. 임의의 비음수 표를 받을 수 있으며 여기서 실행한 표는 합성 입력이다.

signature(-,+,+,+), Lambda0, u=t/Tstar, ell=ln a, h=Tstar H, E/P=(8piG Tstar²/c²) times physical energy density/pressure. h_i>=0인 대각·균질·reflection-even massless Einstein–Vlasov를 다룬다. 동역학과 각분포를 소진폭 또는 유한 multipole로 절단하지 않는다. 양의 표는 cell 경계에서 불연속일 수 있는 완전한 각함수로 유지한다.

각 cell의 x_i=q_i² 평균을 구적점으로 선택하면 1차 Taylor 오차가 상쇄된다. x의 분산, 정확한 Hessian과 simplex 조건으로 2차 cell 오차를 상계했다. MPFR192 RNDD/RNDU가 cell 평균·범위·초월함수·저장 ray 노름·질량과 초기 에너지를 감싼다. 그 결과를 기존 비선형 Dini 비교식에 전달했다. 완전한 유도는 THEORY.md, 식–함수 대응은 ALGORITHM.md다.

u∈[0,.08], 원본2x3 표[[.1,.25,.05],[.2,.15,.15]], shear(.2,-.13,-.07), 고정 목표max_i|Tstar Delta H_i|<1e-5에서 다음을 얻었다.

| 세분화 | 구적점 | 압력 상계 | 기하 h 상계 | 독립 수치 h 차이 | 고정 목표 |
|---:|---:|---:|---:|---:|---|
|1|6|8.79551e-3|7.06346e-4|1.72007e-5|미달|
|2|24|2.28080e-3|1.83166e-4|4.29688e-6|미달|
|4|96|5.73120e-4|4.60259e-5|1.07752e-6|미달|
|8|384|1.43044e-4|1.14875e-5|2.69631e-7|미달|
|16|1536|3.56928e-5|**2.86640e-6**|6.74240e-8|충족|

상계의 관측된 세분화 차수는1.99956785다. 최대 제약 잔차는2.6534e-14, 독립32/48차 구적의 기하 차이는2.22e-15, 느슨한/엄격한 시간적분 설정 차이는1.57e-12였다. 같은 물리 입력·구간·초기조건을 사용했다. 기하 인증은 **연속 각분포와 저장된 이산 source가 정의하는 정확 ODE 사이의 source/초기자료 기여**다. 계산된 궤적의 총 인증에는 부동소수점 source 평가 및 시간적분 defect 상계가 추가로 필요하다.

## 실제 검증

로컬 부모39개와 새18개 검사 통과. 별도 agent가 새18개를 독립 실행했고 실제 소스·테스트 SHA를 대조했다. GitHub의 검증된 코드 commit bca52319247618ad8feca1e0bc5ffa45457a0e8f, run40785425117에서57개 검사와 설치된 wheel의 수치 인증 계산이 성공했다. 로컬에서도 설치 경로를 강제한 wheel import/계산을 확인했다. 이후 core/test bytes는 검토된 해시를 유지했다.

현재 과학 캠페인은9개 결합 IVP와255개 압력 probe, 다른 표의80자리 독립 적분, l6/l8/l10 비영 moment를 포함한다. 그 외 별도 R6/C9 검사에는96개 사전 수학 cell,108개 독립 GL 압력 평가,14개 Decimal120 삼각함수,12개 Decimal110 L0 검사가 있다. 도함수 항등식은 Wolfram으로 잔차0을 얻었다. SciSpace/Exa/원전 검색의 적용 범위와 정확한 독립성은 provenance에 기록했다. 소프트웨어 형식 검증이나 서로 다른 모델 계열의 맹검 심사를 주장하지 않는다.

압력 부호 반전은 제약 잔차0.11948을 만들어 검출됐고, cell Taylor 오차항 제거는 모든 해상도에서 검출됐다. 원래1/18 참조 실패는 float GL 누적오차였으며90자리 독립 참조로 교정했다. 허용치8e-16을 유지하고 원 실패를 보존했다. f8 목표 미달은 같은 입력의 f16 세분화로 해결했다. 새 no-go 성과는 제출하지 않았다.

직접 생성·읽은 그림은 evidence/SOURCE_CONVERGENCE.png와 GEOMETRY_CONVERGENCE.png, 인쇄용 PDF다. 균일 상계와51점 표본 차이, exact-ODE 비교와 수치 궤적 차이를 분리했다. 그림·두 감사·CRAG·잔여 오류 판정은 AUDIT.md에 있다. 측정된 과학 캠페인 wall10.522s,CPU10.495s이며 서비스 대기·포장·다른 검토 비용은 이 값에 포함하지 않는다.

## 코드, 보존, 재개

새 module bianchi/nonperturbative/einstein_tabulated_source.py는 TabulatedRadiation, certified_tabulated_energy, certified_tabulated_pressure, certified_tabulated_geometry를 제공한다. backend='python_oracle'을 명시해야 한다. 부모/main merge와 native 기본 경로 변경은 수행하지 않았다. production_ready=false,merge_ready=false를 유지한다.

R1–R10/C1–C10 각 단계에는 stages/ 문서, 독립 Git commit, expected-SHA/force=false 원격 ref ACK, SHA256이 있는 ZIP snapshot이 있다. 로컬 Git commit과 원격 API commit은 생성 metadata가 달라 식별자를 별도로 기록했고 매 게시에서 전체 tree SHA의 일치를 확인했다. 최종 패키지의 STAGE_PRESERVATION.json과 PUBLICATIONS/가20개 단계의 실제 보존 근거다. 초기에 실패한 셸 push의 원인은 인증 부재였고 연결된 GitHub 쓰기 기능으로 완료했다.

재현: 이 branch를 checkout하고 Python3.12,MPFR4.2 계열, NumPy2.3.5,SciPy1.17.0,mpmath1.3.0,pytest9.0.2,matplotlib를 준비한다. 정확한 로컬 실행환경은 evidence/RESULTS.json에 있다.

```bash
python -m pytest -q tests/nonperturbative/test_einstein_tabulated_source.py tests/nonperturbative/test_einstein_exponential_source.py tests/nonperturbative/test_einstein_physical_input.py tests/nonperturbative/test_einstein_interval.py tests/nonperturbative/test_einstein_error_budget.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/ce1f_20261029/science.py
python research/ce1f_20261029/plot_saved.py
```

다음 후보 CE1-G는 선택된 표·해상도에서 whole-panel source 평가/시간적분 defect를 인증하여 현재 source/초기자료 경계와 합치는 작업이다. 기존 CE1-C MPFR residual 도구의 cell source 호환성을 먼저 확인한다. 물리 입력 획득 오차와 cell 내부의 실제 변화는 실제 관측 표를 도입할 때 별도 입력 계약으로 관리한다. 상위 CE-1의 다른 물리 의무는 DAG_UPDATED.json에 유지했다. 이번 요청의 한정된 다음 R/C 루프는 CE1-F에서 종료한다.
