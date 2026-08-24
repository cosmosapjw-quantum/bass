# Q-CONTRACT v1.0 — 과학적 계약 (Q0, 76차)

기계가독 사본: `bianchi/q/contract.py`.  **시험은 임계를 스스로 정하지 않고
`contract.budget(pr, key)` 로 읽는다** — 그래야 "합격을 위한 임계 조정"이 불가능하다.

## 1. 단위·시간

| 양 | 정의 |
|---|---|
| 부호규약 | (−,+,+,+) |
| 자연단위 | c = G = ℏ = 1 |
| 시간변수 | τ, dτ = H dt (붕괴는 τ → −∞) |
| 정규화 | Wainwright–Ellis (팽창 정규화): Σ = σ/H, N = n/H, A = a/H |
| 물질 | Ω = ρ/(3H²) |
| 충돌률 | ν_τ = σ_T n_e c / H — **B2b 통합양식 §6 과 동일** |
| 운동량 | tetrad 성분 p_α; p = \|p\|, ê = p/p |

## 2. 규약 (기존 코어와 패리티 강제)

- 회전: **COMMUTATOR** (`bianchi.conventions.ROTATION_CONVENTION`)
- W_ab = −ε_abc R_c, 벡터 +W@Y, 텐서 +[W,X]
- ε_123 = +1
- trace-free 5성분 → (s00, s11, s01, s02, s12), s22 = −s00−s11
- n_ab 대칭 6성분 순서: (n11, n22, n33, n12, n13, n23)
- 구조상수: C^c_ab = ε_abd n^dc + 2 δ^c_[a a_b], Jacobi n^ab a_b = 0
- 구면: Cartesian (x,y,z), θ from +z, φ from +x; 실수 구면조화 (Condon–Shortley)
- 각 격자: Gauss–Legendre in cosθ × 균일 φ / 반경 격자: 균일 ln p
- Thomson 고유값 (k₀,k₁,k₂,k_{l≥3}) = (1, 0, 1/10, 0) — **하드코딩 금지, 상시 재계산**
- Liouville: dp_a/dλ = C^c_{ba} p_c p^b (I1a 정리 T1)

`validate_contract()` 가 위 넷 (회전·ε·W·k_l) 을 실행해 패리티를 확인한다.

## 3. "approximation-free" 의 범위 — 벗는 것 5종

각 항목은 **대응 시험 ID** 를 가진다 (주장은 시험 가능해야 한다).

| 벗는 것 | 시험 |
|---|---|
| 모멘트 절단·닫힘 부재 | `test_q5_transport.py::test_no_closure_state_is_f` |
| 충돌핵 선형화 부재 (정확 광행차) | `test_q7b_boosted_collision.py::test_exact_vs_ov_expansion_scales_as_v2` |
| 섭동전개 부재 (O(1) 이방성) | `test_q8_einstein_grid.py::test_strong_anisotropy_no_expansion` |
| **근사 절환 부재** | `test_q7_collision.py::test_no_switching_stiff_limit_exact` |
| 유체 닫힘 부재 (소스는 구적 출력) | `test_q8_einstein_grid.py::test_sources_are_quadrature_outputs` |

### ★ 외부 참조 — SymBoltz (arXiv:2509.24740, H. Sletmoen)

"SymBoltz.jl: a symbolic-numeric, approximation-free and differentiable linear
Einstein-Boltzmann solver". 그 코드의 "approximation-free" 는 **근사 절환의
부재**를 뜻한다: tight-coupling ↔ 완전결합 같은 영역별 방정식 교체를 하지 않고,
암시적 강성 적분 + **해석·희소 야코비안**으로 전 구간을 통째로 푼다.

이쪽이 승계하는 것:

1. **근사 절환 금지**를 계약 조항으로 (위 표 4번째 행).
2. **해석·희소 야코비안** — 기하 블록의 야코비안을 기호 유도에서 생성 (Q10).
   야코비안 재사용·LU 재사용으로 장기 run 비용을 낮춘다.
3. **미분가능성 보존** — jax 차트 경로를 AD 오라클로 유지, Rust 는 전방-dual.

이쪽이 다른 것 (더 강한 수단, 같은 주장 범위):

- SymBoltz 는 **선형 섭동** Einstein–Boltzmann 이다. 이쪽은 **배경만, 그러나
  비섭동** — 섭동전개 자체가 없다 (정반대 축의 문제).
- 계층 강성을 암시적으로 받는 대신, 충돌항이 **정확 지수**(§ 아래)라 강성이
  소멸한다. ν → ∞ 가 안정할 뿐 아니라 **정확**하다.

정확 충돌 지수 (PLAN-Q §3):
```
exp(Δτ·C) f = P₀f + e^{−x}(f − P₀f − P₂f) + e^{−0.9x} P₂f ,  x = νΔτ
```
사전검증: dense `expm` 대비 ≤ 2e−14 (`audit/q_check_collision_exact.py`).

## 4. 남는 것 — 이산화 5축과 기대 차수

| 축 | 기대 차수 | 비고 |
|---|---|---|
| 각 (n_θ×n_φ) | 스펙트럴 | 지수 감쇠 확인 |
| 반경 (n_p) | ≥ 6 | 8점 Lagrange 실효차수 |
| 보간 | ≥ 6 | 반-라그랑주 스텐실 |
| 시간 Δτ | 4 | RK4 / DOP853 |
| 분할 | 2 | Strang |

Q17 이 이 표를 **실측으로** 채운다. 채우지 못하는 축이 나오면 §3 의 주장 범위를
그만큼 좁힌다 (숨기지 않는다).

## 5. 오차예산

`contract.ERROR_BUDGET` 참조 (PLAN-Q §6 게이트 행렬의 기계가독 사본).
완화하려면 **완화 사유를 PR-STATUS 에 박제**한다.

## 6. 계획을 강제한 실측 (박제)

| 이름 | 값 |
|---|---|
| I2b 격자 지수 (절단 없음) | +0.234 |
| I2b PSTF l_max=8 | −0.258 ← **부호 반전** |
| I2b 완전유체 | +1.906 |
| I2c Gauss 잔차 | 2e−10 |
| I2c LNA_WALL (Q6 가 제거) | 300.0 |
| G1b 전-루프 Rust 가속 | ×1042 |
| 3항 충돌지수 vs expm | ≤ 2e−14 |

## 7. 알려진 간극 (77차 실행 결과 — 계약이 스스로 주장 범위를 좁히는 자리)

기계가독: `contract.KNOWN_GAPS`.

**잔여 곡률 이류 (Q5b 대기)** — 공변 프레임의 해석적 자유흐름은 곡률항 (n, a) 의
방향공간 잔여 이류를 담지 않는다.

- class A: 정리 T4 (N-항의 l ≤ 1 기여가 정확히 0) 가 보호 ⇒ Gauss·Codazzi 가
  기계정밀로 유지된다.  **단 l ≥ 2 해에는 O(N) 오차가 있다.**
- class B: a-항은 l = 1 에 **직접** 작용한다 (Q-T5) ⇒ Codazzi 잔차 **3.55e−3**.
  ★ Δτ 를 8배 정밀화해도 값이 바뀌지 않는다 — 이산화 오차가 아니라 **누락된 항**
  이라는 증명.  시험이 이 숫자를 고정한다.

따라서 §3 의 "approximation-free" 주장은 현재 **class A 에서 완전**하고,
class B 에서는 l = 1 섹터에 대해 Q5b 가 들어올 때까지 **유보**한다.

## 8. 실행 요약 (77차)

| 항목 | 값 |
|---|---|
| 공변 프레임 I2b 지수 | +0.233923 (불변격자 +0.233933) |
| 도달 축비 | 2.2e28 (LNA_WALL 없음) |
| 3항 충돌 vs dense expm | ≤ 1e−13 |
| νΔτ = 10⁶ | 정확히 P₀f (강성 소멸) |
| 비섭동 y-왜곡 (ΔT/T=0.4) | 해석 2차식 대비 1.128 |
| 수렴차수 (time/split/radial) | 4.00 / 2.00 / ≥6.5 |

## 9. 편광 (P0, 84차)

기계가독: `contract.POLARIZATION`, 검사 `contract.validate_polarization()`.

캐리어는 **기저-없는 에르미트 3-텐서** `J_ab(ê)`, 제약 `J_ab ê^b = 0`.
저장은 실수 대칭 6 (I + 선형편광) + 반대칭 3 (V) = **9 성분**.
세기는 `I = tr J`, 무편광은 `J = (I/2)(δ − êê)`.

★ **Stokes 부호 규약이 필요 없다.** IAU vs CMB 의 U 부호, V 부호, 스크린 방향 —
기저-없는 텐서를 쓰면 전부 무의미하다. 이 사실을 계약에 적는 이유는, 나중에 누가
편의를 위해 Stokes 기저를 도입하려 할 때 **여기서 걸리게** 하기 위함이다.

핵과 그 축약 (`docs/P-DERIVATION.md` D5):
```
(K J)_ab(ê′) = (3/8π) ∫ dΩ Π_ac(ê′) J_cd(ê) Π_db(ê′)      Π = δ − êê
M_cd = ∫ J_cd dΩ  (9 성분)  ⇒  K 는 rank 9  ⇒  l-분해 불필요
𝒦[M] = (7/10)M + (1/10)tr(M)δ  (대칭),   𝒦[A] = (1/2)A  (반대칭)
고유값 (1, 7/10, 1/2)   ← **하드코딩 금지, 상시 재계산** (k_l 조항의 편광판)
```
수송 (D3): `편광 = 스칼라 수송 ⊗ SO(2)(ψ)`, 스크린 홀로노미 **배율 정확히 1**.

### 9.1 · 87차 정정 (외부 리뷰) — 주장의 범위

**부스트 하 ψ = 0 (D7).** 이 진술은 **정준 수송 스크린 사상**에 대한 것이다 —
스크린 대표원 `W` (`W⁰ = 0`, `W·p = 0`) 를 Lorentz 수송한 뒤 게이지를 복원해
얻은 사상을, 산란면 적응기저 (`m₁ ∝ P⊥[v]`) 에서 읽은 값이다. 임의의 외부
tetrad 나 전역 편광 기저를 고정하면 **Wigner phase 가 다시 나타날 수 있다** —
그것은 기저 선택의 성질이지 이 사상의 성질이 아니다. 이 코드가 기저-없는 텐서
캐리어를 쓰기 때문에 실제 계산에서 그 phase 가 등장하지 않는 것이고,
"부스트가 편광면을 절대 돌리지 않는다" 는 더 넓은 명제를 주장하지 않는다.
논문 표기: *"ψ = 0 for the canonical transported screen map"*.

**E/B 를 격리하는 이유.** "E/B 는 선형이론의 언어" 는 **틀린 서술**이었다 —
spin-2 장의 전역 E/B 분해는 비섭동적으로도 정의된다. 격리하는 진짜 이유는
**구현 쪽**이다: `argmin|ê|` 국소 스크린 게이지가 구면 위에서 불연속이라 그
위에서 정의한 `Q/U` 가 각 해상도로 **수렴하지 않고** (실측 −4.8e−4 … −2.3e−4;
`I₂` 는 9자리 안정), 따라서 전역 spin-2 분해가 정량적으로 안정적이지 않다.
연속 스크린 게이지 (또는 spin-weighted 구면조화) 를 도입하면 정량화할 수 있다.
그때까지 정량 결론에는 기저-없는 `polarization_fraction` 만 쓴다.

**"강성 소멸" 의 범위.** 정확 충돌 지수가 제거한 것은 **충돌 부분스텝의 안정성
강성**이다. 수송과 충돌은 비가환이고 `ν_τ` 는 재결합에서 급변하므로 **분할
정확도 제약은 남는다** — 오차예산의 Strang 2차가 그 증거다. 즉 "Δτ 를 안정성
때문에 줄일 필요가 없다" 는 참, "정확도 때문에도 줄일 필요가 없다" 는 거짓.

**이온화 이력의 경계.** `x_e(z)` 는 **외부 공급**이다. 재결합·재이온화는 아직
자기일관하게 풀리지 않는다 — `KNOWN_GAPS['atomic_ionization_history_is_external']`.

**H 앵커 lane (Q20).** `lane` 은 **필수**다.
`internal` = Gauss 구속이 정하는 H, `phenomenology` = 관측 calibrate 된 앵커.
두 lane 을 섞으면 재결합 이동이 anisotropic physics 인지 H normalization 차이인지
구분할 수 없다.
