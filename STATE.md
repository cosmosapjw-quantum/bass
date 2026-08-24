# STATE (v5.1 §11.5 규격 — 컨테이너 소멸 대비 스냅샷 상태카드)
증분: **외부 리뷰 대응 — 정정 4 + lane 강제 + 11유형 커버리지 (87차)**.  (86차: P9b/P9c + 보고서).  (85차: Q19 이력 배선 + P9a D7).  ★ 84차 산출물(polstate.py 등)은 컨테이너 회귀로 소실되어 86차에 **재구성**했다 (게이트 실측 일치 확인).  (82차: Q17 Mode B 축 등재).  (81차: Q7b × Mode B).  (80차: Mode B 정식 결합).  (79차: Q11 전-루프).  (78차: Q5b) — 잔여 곡률 이류.  (77차: Q0–Q18 실행) — Rust 백엔드 / Python 프론트엔드 전환
      ★★ 설계 정정: 고정 tetrad 프레임 기각 → **공변 프레임** (부록 A)
기대값: cargo test 109 passed / pytest 1390 + Q층 162 신규
  (주의: dispatch·i3 속도 시험 타이밍 플레이크 — 단독 재실행 판정.
   스냅샷 .git 무포함 — 복원 후 git init + 기준선 커밋 관례;
   ★복원 후 wheel 재빌드 필요: cd _rustcore && maturin build --release && pip install)
계보: bianchii2b → bianchib2bready (이 타르볼)
미적용 diff: 없음
다음: **B2b 접합** (외부 모듈 도착 시 SPEC §7 체크리스트 6단계 — 계약 무변경).
★ 82차: Mode B 두 축이 **지수** 수렴 (대수 차수 없음).  감쇠율 0.60/n_θ,
  1.74/반경폭.  전체에서 유일한 대수 축은 Q5b 공변 꺾임 (2.45).
★ 81차 반증: 80차 Mode B 충돌이 **공변 q 슬라이스**에서 섞고 있었다 (물리 p 가
  아니라).  비등방 프레임+Planck 에서 lnĜ 최대차 1.97.  Q7b 가 발각.
  정정: δ=ln(μ𝒟) 로 공통 정지계 격자로 옮겨 3항 적용 후 복귀.
★ 80차: ln_ghat 축약 (4lnμ + lnJr) 으로 Mode A/B 가 기계를 공유.
  Mode B 자유흐름은 **정확 항등** (Mode A 의 4dlnμ 는 반경적분 부산물).
  Mode B 만 주는 것: 분광 관측량 (y-왜곡, ΔT/T=0.2 에서 해석식 10% 이내).
★ 79차: 전-루프 Rust ≡ Python 참조 2.665e−15, Python 스텝 루프 0회,
  앙상블 스레드 무관 비트 동일, Mode B 잔여 = 방향 스텐실 + 반경 시프트 결합.
★ Q5b 결과: class B Codazzi 가 **Δτ 불변 3.64e−3 → 각 해상도 수렴 (차수 2.45,
  n_θ=48 에서 3.0e−5)**.  간극이 '누락된 항' 에서 '수렴하는 이산화' 로 전환 —
  approximation-free 주장이 11유형 전부에서 성립.
핵심 자산: grid_coupled (절단·보간 없음; 무충돌 +0.2339 ≡ 시험장, Gauss
      2e−10, Ĝ>0; 약이방 충돌 안정·유체지수 4% 이내; LNA_WALL 명시 거부),
      history_api (프로토콜·Tabulated·Saha/Peebles·validate 7종·thomson_rate
      ·optical_depth — **주입 = 내장 비트-재현 0.0** 달성),
      docs/B2B-INTEGRATION-SPEC.md v1.0 (통합양식 + 수입 체크리스트)
신규 자산 (76–77차): bianchi/q/* (contract·group·characteristics·sphere·
      transport·comoving·collide·boost·coupled·species·integrate·runtime·
      model·stats), _rustcore/src/{geom/group, kinetic/{characteristics,sphere,
      radial,transport,comoving,collide_exact}}.rs,
      docs/Q-CONTRACT.md · docs/Q-ERROR-BUDGET.md(자동) · 계획 부록 A,
      scripts/q17_convergence.py · q18_ci.sh
      ★ 공변 프레임: 보간 0회, I2b 지수 +0.233923, LNA_WALL 제거
      ★ 3항 정확 충돌: dense expm ≤1e−13, νΔτ=10⁶ 정확 (강성 소멸)
      ★ 비섭동 y-왜곡: ΔT/T=0.4 에서 해석 2차식 대비 1.128
빈칸: Taub 제1적분; J2d; rot_block(0); 로그-공간 격자 (→ Q6 로 이관);
      K'2 GPU (HW 부재)
리뷰 이탈: 60–75차 경량/생략 — COST CRITICAL 박제
★환경: 컨테이너 매 턴 리셋 — **매 증분 명령에 직전 타르볼 첨부 필수**

★ 86차: P9b (편광×부스트) — D7 덕에 추가 회전 없이 세 단계로 끝난다.
  P9c (Mode B 편광 Rust) — 슬라이스 = Mode A 게이트, Rust≡Python 3.6e−16, 3.4배.
  결과 보고서 report/report.pdf (8쪽) — 그림 8장 전부 최종 코드에서 자동 생성.

★ 87차 (외부 리뷰 대응):
  · C1 ψ=0 주장을 **정준 수송 스크린 사상**으로 좁힘 (외부 tetrad 고정 시 Wigner phase).
  · C2 "E/B 는 선형이론의 언어" 는 **틀린 서술** — 진짜 이유는 스크린 기저 불연속.
  · C3 "강성 소멸" → **충돌 부분스텝의 안정성 강성** (분할 정확도 제약은 남는다).
  · C4 원자 미시물리 경계를 초록 직후 박스 + KNOWN_GAPS 맨 앞으로.
  · C5 **lane 필수화** (Q20): internal(Gauss 앵커) vs phenomenology(관측 앵커).
    internal 은 외부 앵커 거절, phenomenology 는 Ω 불일치에 **예외**.
  · C7 11유형 커버리지 12/12 PASS.  ★ 표가 "class A 는 Codazzi 기계정밀" 을 반증 —
    기계정밀은 Bianchi I 뿐, 차이는 크기가 아니라 **수렴 차수** (A 3.5–3.7 / B 2.3–2.7).
  · C6 transport core **동결 선언** — Kompaneets/Faraday 등은 로드맵 3–4단계 전 금지.
★ 컨테이너 회귀 3회 — 매 증분 타르볼 첨부가 **필수**다 (85·86차 산출물이 한 번 소실).
