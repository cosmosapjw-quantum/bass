# FA03-R7: 유한 검출기 수치계수 인증과 REI 참조 norm

선택 R7 완료. 기존 b453 두 observer 매개변수 family와 R6 parent를 보존한다. 전체 이론/증명은 R7_VALIDATION_KO.md, 다음 작업은 READY.json과 CODEX_HANDOFF_KO.md를 읽는다.

정확한 chi=.008,psi=.01,cap=.02의 GL3×12 detector에서36ray를 interval Taylor20차/32steps로 적분했다. 복소시간R=1/8, blocknormA<7, forcing<2의 analytic Cauchy tail과 incoming error를 모두 포함했다.24real component의 최대 반경3.303729497659651e-17; exact energy-band moments다.

원 저장 RK4 다항식의 계수 오차와 R6 나머지를 합친 전체 error는 |epsilon|<=.1에서4.743255106663706e-7 이하, 새 exact-rational midpoint는4.743180031668196e-7 이하이다. Continuous cap/observer-derivative/empirical provider errors는 포함하지 않는다. 소수 display를 exact midpoint나 outward endpoint로 사용하지 않는다.

REI helper는 같은 ln(a) PL 참조를 합집합knots에서 비교해 exact sup/L1/L2_squared를 반환한다. 현재1001점 sampled norm을 오류라고 하거나 폐기하지 않고 추가한다. Narrow tent의1001samples=0, exact PLsup=1이라는 구별을 검사했다. Source/normalization은 기존 HH68/HE51 owner guard에서 먼저 결속하며 이 helper는 scientific admission을 하지 않는다. 실제 parent24행 예제와 raw evidence는 private full ZIP 안에만 있다.

Actual remote Wolfram15.0.0/xTensor1.3.0의4zeros, cloud9True와2수식이 저장됐다.22unit tests,11bridge checks,8assembly checks가 scoped PASS다. 별도 모델의 독립 심사/native subagents는 미실행이다. Parent chemistry/atomic/HPC 및 불변36ray 밖의 과학 suite는 재실행하지 않았다.

이 Git에는 증명, generic producer/helper,22tests, 인계/상태/백업 identity만 있다. 전체124-memberZIP에는36rayexact endpoints,CASrawlogs,실패,원 parentZIP 및 private24행이 들어 있다. ARCHIVE_IDENTITY.json의 두 기존 backup object에서 복원할 수 있다. Dropbox 실제 download/hash와 로컬 relocated/negative/restore 검사 완료; Drive는 저장ACK이며 별도 restore는 미실행이다.

다음 FA03-R8은 READY_NOT_EXECUTED. REI_AX11_EXACT_PL_REFERENCE_NORMS는 ownerimport-ready지만 canonical AX11 또는 solver permission을 바꾸지 않는다. 최신성은 actual STATE를 다시 읽어 판단하고, 기존 supervisor/준비된T1/4GiB정책을 중복 실행하지 않는다. main/active REI code/STATE 변경과 자동 merge는 없다.

이 directory에서 `python -m unittest test_validated test_pl_metrics`로 작은 기능검사를 실행할 수 있다. 원 기록의 read-only검증과 science regeneration은 full archive의 REPRODUCE.md를 따른다.
