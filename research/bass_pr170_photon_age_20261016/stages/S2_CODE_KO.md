# S2 | 반사·보존·광자 탄생시간 구적 코드 검증

`born_photon_stress.py`는 birth-local 방향 `mu`의 양의 GL 적분과 `expm1`/rationalized inverse energy를 써서 `F(d)`, `D(d)`를 계산한다. `d=0`에서 정확히 `F=1,D=0`을 반환하며, 두 개의 양의 pressure 적분을 직접 빼는 작은 차이 상쇄를 피한다.

`BornIsotropicRadiation.point(x)`는 이전에 존재하던 `rho_old`와 시간에 따라 생성된 외부 등방 bolometric source `S(u)>=0`를 **서로 다른 cohort**로 취급하고, continuum age integrals와 독립적인 two-variable memory `(U,M)`를 보존한다. `memory_ode`는 DOP853 독립 검사이다. `ledger`는 photon energy, physical-volume expansion work, shear work, external emission source integral을 검사한다. 이 계산은 native REI chemical/Thomson/absorption과 동등한 operator가 아니다.

실제 로컬 첫 실행에서 20개 테스트 중 4 FAIL, 1 ERROR가 발생했다. 원인은 이 코드가 `leggauss` 가중치를 angular normalization 때문에 `w/2`로 캐시하는데, birth-time 적분에서 다시 `x/2`를 곱하여 **age integral을 1/2로 잘못 계수**한 것이다. 이 논리 결함은 외부 Gaussian `dt` ledger에도 영향을 주었다. 첫 경계시각 `rho_old=0,x=0`의 양의 emissivity가 광자를 순간 보유했다고 가정한 positivity gate도 오류였다. Birth integration의 weight를 `x*w_norm`으로 고치고 `x=0`에서 zero stored stock을 허용했다. 물리 입력과 tolerance는 변경하지 않았다.

`python -m unittest -v test_born_photon_stress` 최종 실행: **20/20 PASS**, exit 0. 테스트는 massless old/source photon F,D sign, finite/near-zero positive angular, age integration source and b signatures, exact FLRW, local kinetic energy work finite difference, full physical-volume ledger, memory ODE vs independent integral, time/angular refinement, quadrupole second-order remainder and rejection controls를 포함한다. 이 결과는 source-only sandbox Python에서 확인하였으며 NCP 및 native REI 컴파일은 수행하지 않았다.
