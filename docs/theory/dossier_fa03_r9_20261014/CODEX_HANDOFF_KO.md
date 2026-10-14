# BASS-R9 / REI owner에게: 중복 런 없이 실행 가능한 인계

**최신 실제 STATE·프로세스·HEAD를 먼저 다시 읽는다.** 이 파일의 snapshot은 최초 2026-10-14T13:09:31Z, REI HEAD `45f166adee36d57cabe712ff66209926d1aa1556`이다. 그 당시 active `SHEAR_HALF_MINUS`와 epoch-recovery observer가 살아 있었고 AX07 ZERO는 conditional complete, AX08 running, AX11/AX12 pending. Owner `compare_histories.py`, README는 미커밋 수정 중이었다. 본 R9은 그 작업트리에 쓰거나 solver를 시작하지 않았다. 이후 owner의 변경을 절대 덮어쓰지 않는다.

## BASS 후속 연구자

1. `README_KO.md` → `manuscripts/FA03_R9_FORMAL_KO.md` → `contracts/EQUATION_CLAIM_REGISTRY.json` → `contracts/EVALUATOR_CONTRACT.json`을 본다.
2. 원 FA02 b453 two-observer archive와 다른 FA02 72569 three-observer archive를 합치지 않는다. 원 I–VII, D9.1, SOURCE_CLOCKS, ABUNDANCE_MODEL 변경 금지.
3. `python code/verify_package.py`는 read-only hash/structural verification; `python code/test_r9.py`는 13개 changed behavior 확인. `fa03_contract.py --epsilon '1/10'`은 저장 dyadic coefficient와 peer interval bounds를 정확한 Fraction으로 소비하여 Stokes, Schatten-1 error, polarization degree/rank positivity interval을 반환한다. 원 36ray source transport 재실행은 필요 없다.
4. 원 analytic C3·peer numeric E0/E1/E2를 각각 구분한다. `|epsilon|<=.1`, χ=1/125,ψ=1/100,δ=1/50, exactly36ray GL3x12, continuous detector **energy band only**. 임의 χ/ψ 또는 continuum cap에 `<4.75e-7` 전용 금지. `c*t_o*E_*²*j_*(eplus-eminus)` 복원 한 번.
5. 다음 **선택 단계 R10**은 종료·복구성/게시 기록만 수행한다. 별도 새로운 연구 사이클 자동 시작 금지.

## 현재 Codex REI 담당자

1. 이미 owner가 고친 electron xe floor를 새로 패치하지 않는다. 이미 owner가 준비한 T1 binary/config/binding, signed continuation·epoch recovery와 NCP readiness/slot 계약을 재작성하지 않는다.
2. WU088_HH PR70의 source-pair relation guard와 BASS_HE PR53의 combined reducer patch(정확한 union-knot PL norm)를 먼저 기존 current HEAD와 source SHA에 맞춰 scoped import 검토한다. 둘 다 이 문서에서 실제 owner에 import했다고 주장하지 않는다.
3. 신규 `rei_clock.py:geometry_clock(a,q)`는 chemistry와 독립적인 exact signed-even geometry clock plus q^4 bound를 낸다. `milestone_decomposition(a_zero,a_signed,q,source_pair_bound=True,actual_case_reviewed=True,actual_zero_reviewed=True)`는 실제 case의 **owner-verified** 단계에서만 사용한다. 플래그는 외부 source/SCENARIO/refinement review receipt와 함께 Codex가 연결해야 한다. 이 helper만으로 scientific admission 발급 금지.
4. `a`/`zbar` 비교와 proper-time 비교는 별도 coordinate. `x_HII`는 QV가 아니라 local ion fraction; milestone first-upward crossing의 continuous interpolation error/unknown refinement를 floor=0으로 치환하지 않는다. Tgas plot은 time-ordered parametric curve로 유지.
5. CR/RCT/HH OFF, optional full τ/visibility nonblocking, physical relative error와 native numerical residual 분리. Source-locked signed case가 완성되면 owner AX11에서 geometry-only vs crossing-location shift를 표로 함께 제공하면 된다.

본 공급 노드 `REI_R9_CLOCK_QUARTIC`은 **SUPPLIER_COMPLETE_READY_FOR_IMPORT**. Canonical AX08/AX11은 각각 실제 완료·검토·소스·수렴 결과로만 전이한다. 원 run의 교체/중복 start와 active owner process signal을 하지 않는다.
