# CE1-AC | 복원된 두 계산 경로의 교차검산 및 claim gate

두 개의 **서로 다른 구현**을 동일 원본 six-cell 입력에 대해 독립 실행했다. 이는 독립 저자 검토를 뜻하지 않는다.

- 경로 A (기존 별도 스레드의 원본 후보): 80자리 *정수 고정소수점 outward* 연산과 `A+(D+G√2)/π`인 35개 정확 모멘트. 부호 판별은 **스케일 전** 초기 f-jet `det > 1.3102168598091e-5`. GL6/GL8 원래 저장 기하학에서 82개 X·X'·X'' 레코드와 3,362개 two-time K4·두 시간미분·혼합미분 레코드 생성. Scoped pytest 17/17 PASS (이 컨테이너에서 독립 복원 재실행).
- 경로 B (본 재개 세션): `fractions.Fraction` 유리수 구간 사칙연산, Machin π 교대급수 N=95/45, 정수 `isqrt` 85자리 상·하계. 스케일 전 `det fjet` 구간은 약 `[1.31021685980918741277055045708348, ...]e-5`, 원본 Y4m 정규화를 복원한 물리 Gram X-jet은 `[3.0160395947362265220450786884093, 3.0160395947362265220450786884094]e-5`, 정확 하계 `>3/100000` 인증. GL6/8/16/64의 별도 방정식 초기 jet, 그리고 새 GL16/64 self-consistent DOP853 41 epochs 계산. Scoped pytest 17/17 PASS, 합친 두 경로 34/34 PASS.
- 동일 원본 binary64 source SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`; 원본 CE1-AB head `1ee44436da37a45b6322c3606f0fb43998bed83c`, 원본 검증 아카이브 불변.
- Mathematica에서 `D[Sqrt[Q] T_m(x(u)), {u,1,2}]`와 직접 미분 전개한 6개 식의 차이가 `{0,0,0,0,0,0}`임을 실행 확인. 두 별도 Python 구현, 이견 없이 strict positive 부호 재현.

## 적대적 검사 결과

1. **입력 바꿔치기**: SHA가 달라지면 증명 가정을 만족하지 않는다. 코드에는 원본 `frozen_source_identity()` guard가 있다.
2. **연속 원천 vs GL64**: GL64는 24,576개의 양의 quadrature rays를 쓰는 수치 교차검산이며 exact source proof 자체는 어떠한 GL rays도 입력으로 쓰지 않았다.
3. **무차원 부호·정규화**: X=f×양의 열 스케일. 증명 본문/코드에서 동일 원본 4πa/E, [1,√2,√2]/3를 사용하며 열 스케일은 rank 변화를 초래하지 않는다. C4^α와 원래 raw C4^U는 다른 물리량이다.
4. **국소 jet → 연속시간 Gram**: C² 함수와 양의 w du 시간측도에 대해서만 rank 3이라는 정성적 결론. 41개 이산 sample의 λ3 strict lower, 연속시간 적분 Gram의 **수치** 고유값 lower, 실제 관측 power/likelihood는 추론하지 않는다.
5. **원래 41시점 λ3의 미해결**: λ3≈5.7133e-11은 numerical (GL16/64)이고 CE1-AB Gram perturbation ≤7.7e-6은 훨씬 크다. 이 perturbation bound를 새 정성적 정리에 몰래 적용하거나 반대로 보정하지 않는다.
6. **초기 Einstein constraint**: 원래 shear의 정확 dyadic 합은 0, 원본 positive six-cell 초기 조건의 제약식은 맞는다. 비물리적으로 바뀐 source나 음의 셀 질량에 정리를 적용하지 않는다.
7. **오염/음수 대조**: integer interval 구현에서는 행렬 row sign inversion 시 negative determinant가 나오고, 34개 과학 테스트가 PASS. 그러나 truly distinct-author R6/C9=NOT_RUN.

가장 작은 후속 검증: original continuum 41point λ3를 정량 인증하려면 양의 3×3 minor의 raw 3-epoch interval 평가 또는 이산 표본에 특화된 고차 시간 Taylor 구간(원래 continuum source 및 coupled geometry)을 추가해야 한다. 무의미한 반복 IVP와 수치 tolerance 완화는 하지 않는다.

DAG upper 9/15 (21 edges), CE1 PARTIAL, 18/20 scoped, production=false, merge=false, auto_next=false.
