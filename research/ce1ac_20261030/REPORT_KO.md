# CE1-AC 과학 결과 (2026-10-30)

원본 BASS six-cell model (massless, collisionless, diagonal Bianchi I, Λ=0, u∈[0,.08])의 정확한 연속각도 원천에 대해 초기 l4의 3개 real-even 시간 jet [f,f',f''] determinant 양수 `>1.3102168598e-5`를 정수 유리 간격으로 인증. 기존 CE1-AB의 rank≥2를 다시 계산하지 않고, 일체 DOP853 연속경로 오차와 독립적인 초기 jet 분석으로 연속시간 kernel의 질적 rank=3을 도출. 41-sample λ3 양적 lower 및 연속시간 고유값 하계는 **미인증**.

별도 관측량 소스 데이터: 원본 GL6/GL8 41개 geometry states에서 82개의 X,X',X'' record, 3,362개의 K4와 두 시간미분/혼합미분 record. 41시점 근사 sample Gram λ3 = GL6 5.71332598e-11, GL8 5.71331075e-11 (NUMERICAL ONLY). 정규화 fractional C4는 u=0→.08에서 ~0.010541886→0.011060265 증가, raw energy C4는 ~5.4073e-5→4.0287e-5 감소. 도함수 정규화 닫힘 ∆<5e-15 in scoped tests.

검증: Wolfram 직접 symbolic `r''/r=2C-B²-D`, `x_i''=4x_i(B−h_i)^2+2x_i(B'−h_i')` 체크 모두 0. Source lock, exact moment sum, harmonic basis SciPy independent, GL6/8/16/32/64 jet convergence, time FD, full 41×41 kernel mirror/energy C4 closure, sign-negative control scoped pytest 17/17 PASS. Original R6/C9 distinct-author gate NOT_RUN; current-context blind-referee checks documented separately.

원전 Heinzle & Uggla CQG 23:3463 (2006) and Barzegar–Fajman–Heißel PRD 101:044046 (2020) concern general Bianchi-I EV and isotropization, not this original source rank-3 certificate. No novel literature priority claim.

DAG 9/15, CE1 PARTIAL, new upper nodes 0, production_ready=false, merge_ready=false, auto_next=false. Standalone Draft branch only; no merge or modification of PR273/275/277.
