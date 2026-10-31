# CE1AI | 동일 맥락 자체 적대적 검토 (single pass)

이 검토는 진짜 분리된 저자 R6/C9가 아니며, 그 결과를 대체하지 않는다. 이미 관측된 오류와 잠재적인 과학적 반례를 분리한다. 새 strong no-go claim은 입장시키지 않는다.

| 제기한 공격 | 실제 반증/검산 | 판정 및 남은 범위 |
|---|---|---|
| 원본 six-cell source가 조용히 다른 분포로 교체됨 | 각 producer 첫 실행에서 원본 `frozen_source_identity` = `022e...3035`; 5 transfer + dark direction은 `CELL_E`의 별도 family이고 `e0` 변경 없음; tamper-negative test PASS | Original/source provenance PASS scoped |
| source mass 변화로 초기 Hamiltonian constraint 위반 | `sum D=0` exact, `dE0≈0` (GL last-bit), `δh_i(0)=δE0/(6H0)`, finite nonlinear every perturbed model constrained `H0` 재구성; residual 모니터 | PASS bounded, original geometry h target unchanged |
| `δP_i`에서 `R_ik` or `−P_i` 항 빠짐 | `∂P_i/∂ell_k=−P_i−2δikP_i+R_ik` original moment derivation; Wolfram trace exact; independent source trace tests, full finite nonlinear IVP derivatives check | PASS |
| harmonics의 `m=2,4` real coefficient 정규화/위상 오류 | 직접 `sph_harm_y` vs polynomial under Condon-Shortley convention independent test; `C_l` degeneracy factors verified; no temperature C_l assertion | PASS normal-frame only |
| 여섯 transfer mode를 여섯 독립 자유도로 오인 | 다섯 `D`는 rank5, dark는 정확한 정수 선형결합. 42D joint IVP는 5+1 directions를 **중복 검증**하는 구성 | CLOSED / representation issue |
| GL 초기 SVD rank~4를 exact continuum rank4로 잘못 승격 | 초기 rank는 **유리수 두 행 모멘트** 행렬식 `1/2`, azimuth 결합 determinant `21/20`, `M_i=203/240,53/240`를 통한 직접 증명으로 확보. SVD는 보조 대조만 | PASS derived for initial ONLY |
| dark response가 초기에는 실제로 이미 비영인데 샘플 인쇄가 0으로 잘림 | `δE,δP,δR,δalpha_l≤4` exact zero를 양의 연속 셀의 초기 적분으로 증명. GL6/8/16 initial alpha ≤1e-12. 6차 다항식 source witness `-4752/(1421π)` nonzero exact | PASS |
| 유한 `u=.08`의 rank5를 원전 연속계 spectral-gap theorem이라고 주장 | `s5(end)~1.1032e-4`는 GL6/8/16 **수치 관찰**; 별도 angular continuum enclosure 없음. 초기 `alpha42` first-time jet는 independent exact negative coefficient | HOLD finite-time theorem, preserve actual physical data |
| Liouville first-time dark jet에 Einstein backreaction 누락 | dark source 초기 `δE,δP,δR=0`, `δell=δh=δh'=0`이므로 first time derivative는 exact null geometry에서의 angular flow; independent finite-difference `sph_harm_y`로 확인 | PASS exact first derivative, not long-time dynamics |
| 소스 perturbation이 부호를 바꿔 음의 kinetic distribution이 됨 | ±1e−4 각 모드의 원래 셀 에너지 직접 검사, 최대 절대 source-mass shift <0.04, finite IC and trajectories positivity sampled | PASS requested family amplitude |
| 에너지 교환식/선형화 잔차가 숨겨짐 | `δ log F+∫δ(W/E)=0`, `δC=0`, pressure trace; baseline/response residual과 finite difference 최대오차 보고 | PASS numerical scoped |
| 원본 CE1AH 및 CE1AF의 source history와 충돌 | 정확히 같은 frozen source SHA; GL6/8 original 41-time physical arrays, CE1AH 401-time baseline 비교; local ancestor suites 전체 다시 실행 | PASS scoped source/baseline |
| 독립 검토/production까지 PASS로 오인 | native subagent not exposed, genuine R6/C9 NOT_RUN, new exact finite-horizon rank theorem NOT_RUN | HOLD production & merge |

**최소 수정 이력:** 첫 5개 source basis 확장 중 `ray_source_basis.reshape(5,6)`이 6번째 dependent dark mode 추가로 불일치하는 구현 오류가 실제 발생했다. `reshape(len(NAMES),6)`으로 교정 후 실행했고 새 회귀 테스트로 exact rank5/base direction, dark combination 및 출력을 검증했다. 이 실패는 수학적 no-go나 source divergence가 아니라 명확한 구현 shape defect였다. **현재 실행에 미해결된 fatal bug 증거는 없다.**

**유효성 경계:** exact initial theorem (`derived + Fraction/CAS checks`)와 finite-time GL physical response (`numerically checked`)를 구별한다. R6/C9 distinct-author review는 계속 NOT_RUN. 새로운 upper DAG 닫힘 0, 9/15, CE1 PARTIAL, production HOLD, no merge.
