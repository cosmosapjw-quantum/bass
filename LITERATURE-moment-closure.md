# 문헌 기반 · 모멘트 계층 절단·닫힘과 tilted 정확도

작성 2026-07-31.  H5-e3 에서 **i-닫힘이 지배 오차**로 드러난 뒤, 문헌을 뒤져 기전과
개선안을 정리한 문서.  결론부터: 지배 오차의 정체는 "i-닫힘이 부정확" 이 아니라
**정확한 축퇴를 수치가 깨뜨리는 것**이었고, 원논문이 그 해답을 명시하고 있었다.

---

## 1. 가장 중요한 발견 — 원논문이 이미 답을 적어놓았다

Lewis & Challinor, *Evolution of cosmological dark matter perturbations*
(astro-ph/0203507; PRD 66, 023531) §"The covariant equations…":

> "For massless particles $E=\lambda$ and the velocity-weighted moments are identical,
> $J^{(i)}_{A_l}=J^{(i')}_{A_l}$. The momentum-integrated equations then reduce to
> the usual one-dimensional Boltzmann hierarchy."

우리 코드는 무질량에서도 2차원 (l,i) 격자를 **독립적으로** 적분했다.  초기조건은
축퇴를 3.1e−15 로 만족하지만, i_max 절단이 i 마다 다르게 되먹임되어 t=T 에서 축퇴가
**2.2e−1 (21%)** 까지 깨진다 — 궤적오차(1e−4)보다 크다.  즉 오차의 **원천**이었다.

### 조치와 결과 (측정)
```
2차원 격자 (l_max=2, i_max=1):  rho 5.3e−4   q 3.0e−4   pi 8.9e−4
1차원 환원 (l_max=2):            rho 1.6e−6   q 1.5e−5   pi 1.5e−4
1차원 환원 (l_max=3):            rho 7.8e−8   q 2.3e−6   pi 1.5e−5     ← ρ 약 6800배 개선
```
환원 후에는 오차가 다시 **l_max 지배**가 된다 (l_max 2→3 에서 ρ 21배, π 10배 개선).
2차원 판에서는 l_max 를 올려도 거의 변화가 없었다 — 진단이 정확했다는 증거.

---

## 2. 유질량을 위한 절단 — 원논문의 n_* 체계 (아직 미구현)

같은 논문:

> "If we neglect terms with $l+2i > n_\ast$ … As expected the truncated equations will
> be accurate to within terms that decay as an $n_\ast$th-order velocity density."

핵심 두 가지:

### 2.1 절단은 **총 속도가중 n_* = l + 2i 의 삼각형**이다 (직사각형이 아니다)
우리 구현은 `l ≤ l_max`, `i ≤ i_max` 의 **직사각형** 절단이다.  논문 체계는
`l + 2i ≤ n_*` 의 삼각형이다.  직사각형은 (l_max, i_max) 모서리에서 총 가중이
`l_max + 2 i_max` 까지 올라가므로 일관성이 없다.

### 2.2 ★ **n_* 가 홀수일 때만 프레임 불변**이다 — tilted 에 직결
> "Under linear changes in the fiducial velocity, $u^a \to u^a + v^a$ … the form of
> Eq. (trans) implies that the truncation condition $J^{(i)}_{A_l}=0$ for
> $l+2i > n_\ast$ is only frame-invariant at linear order for $n_\ast$ **odd**."

변환식은
```
J^(i)_{A_l} → J^(i)_{A_l} − ⅓ δ_{l1} v_{a_1}[(3+2i)J^(i) + (1−2i)J^(i+1)]
```
로 **l=1 에서 속도가중에 대해 비동차**다.  tilt 는 문자 그대로 fiducial velocity 를
바꾸는 것이므로, 이 성질이 우리 오차가 **∝ v²** 로 커진 것과 맞물릴 가능성이 크다
(측정 지수 1.79).

**검증 가능한 예측**: 유질량에서 삼각 절단을 쓰되 n_* 를 홀·짝으로 바꾸면
**홀수 쪽이 뚜렷이 정확해야** 한다.  아직 시험하지 않았다 — 다음 증분의 1순위.

### 2.3 비율 닫힘 (기하외삽의 물리적 대체)
> "Truncating the full momentum-integrated hierarchy at $n_\ast=3$, one can show that
> $J_a^{(1)} \approx r J^{(0)}_a$ … are solutions on large scales if $r \approx 5w$.
> Note that these conditions are frame-invariant to the order of our velocity-weight
> truncation."

우리 `close_i` 는 마지막 두 i 에서 비를 **추정**한다 (데이터 구동).  논문은 물리적
값 `r ≈ 5w` (후기) 와 `r ≈ (3w)^{1/2}` (초기) 를 준다.  ★ "frame-invariant" 라는
단서가 tilted 에 특히 중요하다.

---

## 3. 현대 관행 — 참고했으나 우리에겐 부적합한 것들

| 접근 | 출처 | 우리에 대한 적용성 |
|---|---|---|
| **q-샘플링** (운동량 격자 × l-계층) | CLASS/CAMB 표준, [CAMB 2](https://arxiv.org/html/2607.14854) | i-계층 자체를 회피하는 정공법.  우리는 **정확 구적**이 있어 초기조건은 이미 정확하고, 시간적분에서만 문제가 생긴다 → 전면 도입은 과함 |
| **적분방정식(IE) 정식화** — 절단 자체를 없앰 | [CLASSIER, 2506.01956](https://arxiv.org/html/2506.01956);  <0.01% 정확, 4–40배 빠름 | 특성곡선 따라 적분해 절단 인공물을 제거.  **우리 배경은 이미 특성곡선 정확해를 갖고 있다** — 사실상 우리 `tilted_moments` 가 그 역할.  적분기를 IE 로 바꾸는 것은 검토할 가치 있음 |
| **일반화 Boltzmann 계층 (GBH)** — 속도가중 모멘트 확장 | [PRD 104, 083535 / 2104.00703](https://arxiv.org/abs/2104.00703);  CLASS 대비 ≲0.5% | 우리와 **같은 구조**(l × n 두 지표).  절단 부록이 있으나 0.5% 수준 — 우리의 1e−7 목표에는 부족 |
| **모멘트 닫힘 이론** (Grad / 최대엔트로피 / Levermore) | [Levermore 1996, J. Stat. Phys. 83, 1021](https://link.springer.com/article/10.1007/BF02179552) | 쌍곡성·실현가능성을 보장하는 일반론.  우리는 **정확해가 있어** 닫힘을 추측할 필요가 없다 → 우선순위 낮음 |
| 절단 인공물이 τ ~ 2l_max/k 에서 반사 | CLASSIER | k-모드가 있는 섭동 계산의 병리.  **우리 배경에는 k 가 없어** 해당 없음 |

★ 이 표의 요점: 우리 문제는 "닫힘을 잘 추측하는 것" 이 아니라 **알고 있는 정확한
구조(축퇴)를 수치가 깨뜨리지 않게 하는 것** 이었다.  그래서 정교한 닫힘 이론보다
원논문의 1차원 환원이 6800배를 벌었다.

---

## 4. 다음 순서 (문헌 근거 순)

1. **유질량 삼각 절단 + n_* 홀짝 시험** — §2.2 의 예측을 측정으로 검증/반증.
   홀수가 낫다면 그 자체가 문헌 주장의 비선형 확장 확인이 된다.
2. **비율 닫힘 r ≈ 5w / (3w)^{1/2}** 을 `close_i` 대안으로 넣고 비교 (§2.3).
3. 그 다음에 Rust 이식 — **정확도 개선이 끝난 뒤**가 맞다 (이식은 빠르게만 할 뿐).

---

## 참고문헌

- A. Lewis, A. Challinor, *Evolution of cosmological dark matter perturbations*,
  PRD **66**, 023531 (2002), [astro-ph/0203507](https://arxiv.org/abs/astro-ph/0203507)
  — 본 프로젝트의 식 (12) 원전.  §속도가중 절단, 프레임 불변성, 비율 닫힘.
- C. D. Levermore, *Moment closure hierarchies for kinetic theories*,
  J. Stat. Phys. **83**, 1021 (1996),
  [Springer](https://link.springer.com/article/10.1007/BF02179552)
- *Generalized Boltzmann hierarchy for massive neutrinos in cosmology*,
  PRD **104**, 083535, [arXiv:2104.00703](https://arxiv.org/abs/2104.00703)
- *Rapid and accurate numerical evolution of linear cosmological perturbations with
  non-cold relics* (CLASSIER), [arXiv:2506.01956](https://arxiv.org/html/2506.01956)
- *CAMB 2: cosmological power spectra for high-precision surveys*,
  [arXiv:2607.14854](https://arxiv.org/html/2607.14854)
- *Efficient analytic approximation for small-scale non-cold relic perturbations*,
  [arXiv:2510.20821](https://arxiv.org/html/2510.20821)
- A. Pontzen, A. Challinor, *Bianchi model CMB polarization…*,
  MNRAS **380**, 1387 (2007), [arXiv:0706.2075](https://arxiv.org/abs/0706.2075)
- *CMB line-of-sight integrators for nearly-isotropic cosmological models*,
  [arXiv:2506.07786](https://arxiv.org/html/2506.07786)
