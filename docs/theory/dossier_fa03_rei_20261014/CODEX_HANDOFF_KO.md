# Codex handoff: BASS FA03와 REI theory consumer

이 capsule의 README, INPUT_IDENTITY, CLAIMS, FA03_KO, REI_THEORY_KO, THEORY_DAG_OVERLAY를 먼저 읽어라. Parent는 b453 two-parameter FA02다. 같은 날짜의 72569 three-parameter archive나 top-level 오래된 NEXT를 동등하게 덮어쓰지 마라.

## REI 실행 소유자에게

현재 자신의 실제 HEAD/STATE를 읽고 이 문서의 2026-10-14 07:38:35 UTC snapshot보다 최신 작업을 보존하라. 당시 AX06 scoped pilot이 끝났고 AX07/08은 READY였다. 완료 pilot을 재실행하지 말고 owner가 승인한 finite resource/config 계약으로 full histories를 계속하라. 이 인계는 full-history 실행의 새 gate가 아니다.

독립적으로 다음 두 준비를 소비하라. REIT-R1의 초기에 등방인 전체 effective Omega_r radiation에 대한 prescribed-path diagnostic bound `2.61e-5` 및 extra-energy bound `8.68e-7`을 background lock이 동일할 때 사용하라. 이것을 self-consistent geometry/abundance error bound로 승격하지 마라. Ionizing U2 및 thermal/extra-energy 항은 실제 output에서 계속 계산한다.

AX11 분석에는 q=0,±q/2,±q를 동일 ZBAR 또는 PROPER_TIME 좌표에 놓고 E/O, A1 leakage, A2,A3를 산출하라. `code/rei_theory_checks.py:signed_coefficients`는 대수 helper일 뿐 matcher나 scientific admission gate가 아니다. 수치/보간오차와 원래 response floor를 먼저 전파하라. Scalar O(q) 소거는 isotropic differentiable continuum 가정의 진단이며 강제 q-symmetrization 금지다. Odd q^3는 물리적으로 가능하다.

Source law는 동일 comoving law vs a로 유지하고 서로 다른 배경의 a와 proper time을 동시에 같다고 하지 마라. Milestone은 실제 local xHII이며 QV로 부르지 마라. 미도달/평탄 crossing은 censored 또는 ill-conditioned로 남겨라. Temperature-axis curve는 시간순으로 그려라.

CR/RCT/HH/metastable/secondary-electron OFF와 Case-A escape를 보존한다. HE warm pilot 또는 HH exterior certificate를 cold AXBI rate로 가져오지 않는다. Optional observer/tau-tail이 abundance goal을 막지 않게 한다. Runtime readiness와 theory-import readiness, partial/component admission을 분리한다.

## BASS 다음 연구자에게

FA03-R5에서 식 FA3.8–10과 FA3.12–14가 구성되었다. 여섯 행렬 closure는 epsilon=0 미분 전용이다. 실제 xAct 10 zeros, cloud CAS, 11 FA03 checks와 10 REI checks가 저장되어 있다. 다음은 변경영역 한정 R6 검토와 additive equation/claim registry integration이다. 새 full R1–R10를 자동 재시작하지 마라. 독립 agent를 실제 쓸 수 없다면 같은 작성자 검토를 independent라 하지 마라.

읽기 전용 검증: `python code/verify_capsule.py`. 과학 검산을 의도적으로 재실행할 때만 새 출력 디렉터리 또는 이 capsule의 복사본에서 `python code/check_fa03.py`, `python code/rei_theory_checks.py`를 실행하라. Production/HPC/atomic suite는 이 인계에 필요하지 않다. 원본 I–VII, SOURCE_CLOCKS, ABUNDANCE_MODEL, original DAG를 바꾸지 말고 새 경로에서 발전시켜라.
