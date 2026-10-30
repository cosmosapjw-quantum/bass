# KM2H | R6/C9 동일 연구자 적대적 검산 (single pass)

범위: S0/S1 외부 FLRW x_e를 원본 Einstein-Bianchi I P8 코드에 결합한 6개 실제 ODE. 2026-10-30.

- **PASS scoped (원본 바이트):** 원래 KM2G, KM2F, KM2A/C/D/E 소스 Git blob byte locks 및 이전 user-native FLRW 1600-행 SHA256 검사. 상위 원본은 변경하지 않았다.
- **PASS scoped (보존식):** 18개 pytest; 실제 GL n_theta12/16에서 Hamiltonian/운동량 제약, 원래 편광 스크린 수송·광원, p/lab number, source P8 raw-covariance discrepancy를 독립 시간 GL24 적분으로 기록. 원래 응력 힘을 임의로 0으로 projection 하지 않았다.
- **PASS scoped (저장된 데이터 독립 재집계):** 새 RHS를 import하지 않는 `hostile_saved_physics_audit.py`가 실물 6개 케이스의 30 full-stress epochs 및 144 원래 P8 force-gap GL24 행을 읽었다. rho total closure max 1.42109e-14, source charge/current perfect 0, proton/electron free number equality exact 0, species mass-fraction sum error 1.11022e-16, SI Thomson opacity error 4.44089e-16, raw P8 force source-record equality 0. 독립 선형 보간으로 확인한 native HYREC/CLASS x_e 차이 최대 9.16542e-07이며 기초 커브의 PCHIP 변환 차이만 포함한다.
- **CONCERN / observational blocker:** BASS synthetic n_H(0)/CLASS n_H(z_ref) = 5.73964456; H만 초기 동기화했으며 전체 Friedmann 배경을 동기화하지 않았다. 관측 적합, 마지막 산란면 sky, realistic density 주장 금지. 이 과제 범위에 대해서는 blocker 아님.
- **CONCERN / microscopic blocker:** FLRW 원전 x_e는 isotropic blackbody, thermal expansion history와 표준 원자물리의 입력으로 만들어졌음. Bianchi P8 비등방 광자 자체를 원자 excitation, two-photon rates, matter temperature ODE에 다시 보내지 않아 recombination is prescribed. 실제 비등방 recombination 해결 주장 금지.
- **CONCERN / reaction-energy blocker:** 외부 x_e 변화에 따라 charged/neutral species mass fraction이 바뀌지만 중성 H의 binding 13.6eV 원자당 에너지, radiative escaping recombination photon spectrum, entropy/chemical source는 빠져 있다. 상대 질량 에너지 ~1.45e-8 수준의 local approximation; 임의의 thermal history/energy accuracy claim 금지.
- **CONCERN / finite collision lock:** charged e/p, neutral H, neutral He가 common bulk U를 지닌다는 이상적 lock을 물리 가정으로 두었고 Coulomb cross-species finite slip이나 neutral collisions, Maxwell fields는 직접 진화하지 않았다.
- **CONCERN / quadrature:** finite positive angular GL n_theta 12/16에서 이산화 잔차를 측정했지만 full angular continuum error interval certificate는 NOT_RUN. 자체 검증자가 독립 저자 R6/C9가 아니며 native subagent NOT_RUN.
- **NONBLOCKING traceable:** HYREC-2 standalone와 CLASS HyRec2020 간 원자물리 C source overlap. 수치 차이 작음을 두 독립 모델 검산으로 분류하지 않고 source execution/path parity로만 사용했다.

**판정:** `COMPLETE_SCOPED_CONDITIONAL_PHYSICAL_SCIENCE` / `PRODUCTION_HOLD`; upper BASS 9/15, KM2 PARTIAL, new upper nodes 0. R6 hostile self-pass 종료, 중복 reviewer tree 금지. 다음 한정 과제는 full anisotropic recombination rates & microscopic radiation frequency/thermal coupling의 원전 확보/구현. 사용자 원전 FLRW x_e와 T_m은 확보되어 있으나 해당 anisotropic kinetic rates의 원자료는 아직 없음.
