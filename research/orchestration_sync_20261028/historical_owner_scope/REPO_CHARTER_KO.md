# BASS 확장 역할과 연구 범위

BASS는 배경 시공간, 물질·복사 stress-energy, 보존적인 반응 four-force를 연결하는 물리 통합 저장소다. 이번 확장은 모든 목표 핵종·이온의 물리와 외부 광자·baryon 주입 및 흡수를 수용할 수 있는 인터페이스를 포함한다. 개별 원자·핵 반응 자료의 생산·검증은 해당 전문 저장소가 담당한다.

## 담당 범위

- 고정 scale을 쓰는 Einstein–Vlasov/배경 진화와 선택된 matter/radiation closure.
- 동일 frame·clock·단위에서 종별 rho, q, p, pi와 전체 T를 구성하는 moment bridge.
- 반응별 gross event measure에서 종별 수밀도 변화와 Q_s를 함께 구성하는 conservative adapter.
- 외부 광자·물질 주입 및 escape의 명시적 reservoir, 유한 donor depletion, source epoch와 재시작.
- 시간·각도·radial·tail·source 오차의 분리와, 유효한 stability 가정 아래 geometry까지의 전파.

REC는 실제 광자 occupation, line/continuum 방출·흡수와 history/retiming/pullback을 소유한다. WU는 재사용 가능한 핵종·ionic charge·상태별 반응률, 단면적, branching과 Q/생성물 kinematics를 소유한다. bass_cr는 외부 분포·주입·비열적 cascade와 stopping을 소유하고 WU의 미시 사건 자료를 소비한다. BASS_HE는 baryon finite-mass 교환과 angular/stress closure를 소유한다. VigilODE는 수치 engine을 제공한다. BASS는 이 결과의 소비 계약을 소유하며 다른 저장소의 활성 작업을 복제하지 않는다.

## 현재 근거와 다음 과제

PR184의 G1B 복구 및 유한 V/VIII 비교는 COMPLETE_SCOPED다. PR190 B3f의 주어진 cohort 입력 오차 합성도 COMPLETE_SCOPED다. 실제 history/error radii의 binding과 native finite incident absorption은 입력 의존성으로 남는다. B3 전체, 일반 domain, production은 아직 완료되지 않았다.

첫 과제 B3g는 실제 cohort의 source pin, birth time/frame, R, S, n, E_b, support와 물리 오차 반경을 기존 B3f에 연결한다. 두 번째 B3h는 유한 incoming occupation·donor와 하나의 exclusive atomic/line owner를 묶는다. 이들이 준비된 선택 채널만 B3i에서 geometry와 결합한다. G1C의 저장 history 기반 오차전파 유도는 독립적으로 진행할 수 있다.

폐쇄 채널은 모든 생성물·binding·recoil·비열적 입자까지 포함해 sum Q_s=0을 만족한다. 외부 주입·escape가 있는 내부계는 sum Q_internal=Q_external로 기록한다. 모든 목표 핵종은 coverage matrix로 추적하며, 미지의 rate·radius를 0으로 채우지 않는다.

## 작업 경계

이 PR은 연구 역할과 과제 배치 문서만 추가한다. 기존 source, 기본 dispatch, 물리 tolerance, active branch 및 dirty work는 보존한다. 새로운 heavy 실행·NCP·과거 campaign 재실행·budget reset은 승인하지 않는다. 향후 구현은 과학 계약, 정확한 입력, 실제 남은 예산과 한정 명령을 고정한 뒤 별도 단위로 진행한다.
