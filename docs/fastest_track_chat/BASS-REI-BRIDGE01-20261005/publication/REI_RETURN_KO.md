# rei_bianchi에 반환: BASS-REI-BRIDGE01

BASS의 최신 native branch `forward/rust-microphysics-host-20260930`를 읽고, REI `41e4592aa494b48929dcd23fc8504c169a98a908`의 실제 HHe/FT03 state에서 proper electron density를 받아 Thomson normal-clock visibility에 연결하는 adapter를 준비했다. 최종 구현·검증·게시 상태는 함께 제공되는 receipt와 BASS packet README가 소유한다.

실행 증거는 scoped native20개, Decimal70 snapshot 검산786개/native140회, actual static FT03 두 history의 독립 검산22029개 PASS다. native source를 호출해1000/2000개의 interval을 각각 진화시켰으며, BASS full-crate build는 실행하지 않았다. RCT 기본 OFF와 관측량·source physical admission 상한은 그대로다.

소비 경계는 `n_e = n_H x_HII+n_He(y_HeII+2y_HeIII)`, proper cm^-3→m^-3, `q_t=c sigma_T n_e D`다. Thomson ionization-independent cross section은 BASS 상수를 쓰고, D는 기존 MaterialFrame에서 한 번만 적용한다. FT03 snapshot의 density 유효성을 검사하는 경로와 FT03 rate/T guard를 통과한 evolving history는 구분한다. source chemistry RHS와 atomic provider는 REI가 계속 소유한다.

현재 이온분율과 proper nuclear density를 cell마다 제공하면 BASS는 rate schedule 및 `tau`, survival, interval probability를 반환할 수 있다. 입력 clock은 증가하는 normal seconds다. observer tail을 명시하며 interval probability를 억지로1에 정규화하지 않는다. RCT photon escape를 Thomson photon gain에 추가하거나 RCT event rate를 전자 source에 직접 더하지 않는다.

REI의 다음 최소 producer 작업은 `BASS-REI-EXP01`에 전달할 **실제 expanding accepted-state export**다. 각 cell에 normal time, proper nH/nHe, HII/HeII/HeIII fractions, exact source/model identity, accepted stage와 sampling rule, geometry a/H owner를 기록한다. Q filling factor와 local ionization fraction, comoving와 proper density를 명시적으로 구분한다. BASS는 이 payload를 받은 뒤 small FLRW baseline→finite refinement 순서로 소비한다.

현재 controlled FT03 H=0 fixture의 downstream visibility 결과는 expanding EoR history가 아니다. 기존 F04 uniform enclosure의 partial 상태, CR frozen-source certificate 범위, HE mixed-native owner acceptance, HH cutoff/domain 대기는 보존한다. `RCT-STEP01`은 REI 소유의 별도 다음 단위로 남으며 이번 BASS 연결이 자동으로 RCT를 실제 stepper에 넣지 않는다.

본문은 additive return이다. 기존 REI code, PR83의 다른 작업, 원자 장기 lane을 자동 merge·종결하지 않는다. BASS 실제 commit/백업 링크는 같이 게시되는 machine-readable publication receipt에서 읽는다.
