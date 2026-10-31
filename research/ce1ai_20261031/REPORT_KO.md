# CE1AI | 진짜 original-source 물리 응답과 exact dark-mode 결과

- 기준 parent: Draft PR #287 HEAD `c7660436f233bfe94d954146017059fd79385dd5`. 원본 six-cell SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. 고정 parent/main/siblings 불변.
- CE1AI는 **5차원** 원본 cell-energy-conserving perturbation family의 방향 다섯 개와, 그 선형결합인 **dark control** 한 개를 계산한다. 여섯 개 독립 파라미터라고 주장하지 않는다. 원본 초기자료는 대체되지 않는다.
- E, pressure, Weyl/metric 없음: 정확히 collisionless massless normal-frame angular energy and Einstein diagonal Bianchi-I stress만 생성. 시각화는 모형의 fractional bolometric, 실제 CMB 온도/편광 스펙트럼이나 likelihood 아님.

## 새 실제 물리 데이터

| 실행 종류 | GL orders | 시점 | 새 기록 수 |
|---|---|---:|---:|
| 원본 self-consistent 6D baseline | 6,8,16 | 401/order | **1203** |
| 5 independent+1 dependent source tangent (42D coupled IVP) | 6,8,16 | 401/mode/order | **7218** |
| ± source-cell mass, 진짜 완전 비선형 Einstein–Vlasov | 6,8 | 401/±/mode/order | **9624** |
| 5×5 source-to-l2/l4 Jacobian singular spectrum | 6,8,16 | 401/order | **1203** (diagnostic) |

총 물리 상태·응답 저장 18,045행, 진단 1,203행. 과학 이미지 7개.

## GL16, u=2/25의 endpoint 미분값

각 수치는 **하나의 해당 source-cell energy transfer parameter ε 단위당 미분**, dark 방향은 integer matrix/406로 정규화. 무차원 `W`, `E`, `C_l`, `F`에 해당한다.

| mode | dC2/dε | dC4/dε | dW/dε | dF/dε |
|---|---:|---:|---:|---:|
| EQ_X | +0.93818239662 | -0.56732025077 | +0.10351955421 | -0.011499739869 |
| EQ_Y | -0.92311102105 | -0.41512698395 | -0.10185802176 | +0.011406904442 |
| POL_X | +1.4195339856 | -0.029214291773 | +0.011311285705 | -0.0010233563431 |
| POL_MID | +0.9922155604 | -0.10912923685 | -0.035305209628 | +0.0041791025461 |
| POL_Y | +0.56884475727 | -0.43767807818 | -0.081492995231 | +0.0093575153854 |
| DARK_L2L4 | -6.3654411401e-06 | -0.0039335529629 | +2.5446912614e-06 | -9.5885342126e-08 |

정확한 초기 source null을 보존한 `DARK_L2L4`의 수치 endpoint: `dalpha42=-0.05877289633234494`, `dalpha44=0.013535384243958384`, `dC4=-0.003933552962851191`, `dW=2.5446912613895055e-06`.

## 핵심 물리적 판단

1. **Exact continuum:** source-locked 초기 cell mass perturbation `[[53,-106,53],[-203,406,-203]]/406`의 `δE`, 모든 `l=2,4` angular coefficients 및 initial P,R tensor = 0. 정해진 에너지 보존 5차원 family에서 초기 five-harmonic map의 rank는 정확히 **4**. 양의 기하와 source mass를 보존하면서 비영인 차수6 angular witness는 `(-4752/1421)/pi`.
2. **Exact continuum first-time response:** `∂ε∂u alpha42(0) = (3/8)*sqrt(5/(2*pi)) * (-1296/203) * (sigma_x0-sigma_y0)/E0` ≈ **-0.783081077582325** <0. Liouville moment coupling에 의해 초기 보이지 않던 source shape 정보가 즉시 l=4로 유입된다. Wolfram 별도 exact rational cross-check 및 source-GL SciPy finite differential check 완료.
3. **Numerical GL finite-time:** 5×5 harmonic-source Jacobian의 초기 최소 특잇값 `s5(GL16)=9.92718e-16` (machine residual), 끝시점 `s5=0.000110319799409`, 조건수 `134286.331381`. **유한시간 exact continuum spectral-gap 증명으로 승격하지 않는다.**
4. **Source and physics validation:** GL16 Hamiltonian baseline max `6.195e-14`, linearized constraint max `1.9373e-14`, response-work log balance max `4.8685e-15`. GL6/GL8 ±finite perturbation vs analytic tangent maximum absolute error `2.8349e-09`. 원본 41-time GL6/8 데이터 비교 차이 ≤1.964e-13. GL8/16 endpoint agreement empirical.

## Claim gate

- **exact derived:** source-mass/geometry Jacobians, trace, constraint tangent, initial rank 4, explicit dark vector, nonzero first-time l4 response.
- **numerically checked:** coupled 6/42D GL6/8/16 histories, ±true nonlinear 6D 24 IVPs, u=.08 response and spectral singular value.
- **implementation verified locally:** scoped new 31/31 tests; ancestor CE1AH 19/19; CE1AF 24/24. Remote CI must be read before claiming remote PASS.
- **not established:** full-horizon exact-continuum finite-time rank5, angular quadrature rigorous enclosure, independent distinct-author R6/C9, observational likelihood, CMB temperature or polarization, production readiness.
- Upper BASS **9/15**, 21 edges; `CE1=PARTIAL`; original scoped R/C **18/20**; new **upper** nodes 0; `production=false`, `merge=false`, `auto_next=false`. Bounded CE1AI subunit scientific deliverable produced, not upper DAG promotion.
