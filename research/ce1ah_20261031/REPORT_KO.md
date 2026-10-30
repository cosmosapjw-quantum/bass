# BASS CE1-AH | 실제 원본 물리 반응 데이터

범위: exact original six positive binary64 angular cells, expanding diagonal Bianchi I Einstein–Vlasov, massless collisionless, (-,+,+,+), Λ=0, proper u=t/Tstar in [0,0.08].

Parent Draft PR #286 HEAD `4d6a5d9c391bbd5aac1a885ff72b4f33f027e28a`, original source SHA-256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.

## 실제 생성한 물리 데이터

- baseline=1203 실제 coupled Einstein–Vlasov IVP epochs (GL6/8/16 × 401)
- tangent=2406 response rows (GL6/8/16 × 2 linearly independent traceless initial-shear modes × 401)
- finite validation=3208 실제 nonlinear Einstein–Vlasov IVP records (GL6/8 × ± × 2 modes × 401)
- 3 CSV 파일 + 1 JSON 결과 + 5 science plots; 데이터는 sample-based, not analytic lower curves.

## GL16 endpoint u=0.08: physically meaningful derivatives

| Quantity | A=(1,-1,0) | B=(1,1,-2) |
|---|---:|---:|
| dW | +0.0266498789932 | -0.0687029378696 |
| dq | +0.0353002319441 | -0.0905327062605 |
| dC2 | -0.0741723868893 | +0.140258493039 |
| dC4 | +0.00234274402197 | +0.000259181242548 |
| dE | -0.0241132240762 | -0.00811216944197 |
| denergy_ratio | -0.00400548323747 | +0.0069933221985 |

Base physical endpoint: E=0.758419059008955, W=0.00385259653385333, C2=0.0543070897764551, C4=0.0110602647059212.

## Verification by actual runs

- Current 19/19 pytest PASS, parent original CE1AF 24/24 pytest PASS, compileall PASS.
- Max baseline Hamiltonian |C| = 9.24e-14; max tangent |δC| = 2.58e-13.
- Max derivative of exact volume-compensated photon-energy exchange balance = 5.2e-15.
- Max central-finite-difference deviation of tangent (GL6,8) = 2.9e-10; finite difference ε=1e-4, with exact constrained non-linear initial data.
- Original frozen GL6/GL8 41-state histories and CE1AF 1604-row baseline agree numerically, original SHA-latched file preserved.
- Independent SciPy spherical harmonics Y20/Y22/Y40/Y42/Y44 vs polynomial harmonics, common spatial-scale invariance, independent pressure-Jacobian finite difference, source-tamper negative test.
- All tests above are SAME-CONTEXT/implementation-check. Distinct-author R6/C9 NOT_RUN. No formally verified proofs or continuum GL certified error bound.

## Scientific interpretation

Axy initial shear response changes C2 negatively, C4 positively, and W positively at final u=.08. Baxial changes C2 positively, C4 weakly positively, and W negatively. Distinct signs show angular response anisotropy and real self-consistent metric feedback, not a claim of observational CMB detection or entropy creation.

## Correct DAG classification

- `UPPER_DAG=9/15`; `UPPER_EDGES=21`; `CE1=PARTIAL`; `SCOPED_R_C=18/20`; `NEW_UPPER_NODES=0`.
- This scoped CE1AH physics unit is implemented and numerically checked. It does not close CE1, R6, C9, production or merge.
- Literature needed to reproduce: NONE beyond pinned immutable original six-cell input and published source code; original primary papers are available at arXiv:gr-qc/0512031, arXiv:1911.04937 and DOI 10.1103/PhysRevD.101.044046.
- STOP_AFTER_ONE_BOUNDED_UNIT=true; AUTO_NEXT=false.
