# bianchi-solver

모든 Bianchi 유형(I–IX, class A/B, 예외형 VI\*₋₁/₉)과 tilted 모델의
배경 우주론 solver. JAX + diffrax.

## 원칙

1. **유도 우선.** 방정식을 문헌에서 옮겨 적지 않는다. 모든 RHS 는
   구조상수에서 `symbolic/frame.py` 가 유도한다.
2. **PR 하나 = 검증 가능한 관문 하나.**
3. **오라클이 못 잡는 것을 명시한다.** 회귀 테스트가 무엇에 눈감는지를
   코드리뷰가 알아야 한다 (`symbolic/oracles.ORACLE_BLIND_SPOTS`).
4. **차트마다 "무엇을 못 하는가" 를 `LIMITATIONS` 에.**

## 함정 4가지 (전부 `conventions.py` 에 박혀 있음)

| # | 함정 | 왜 위험한가 |
|---|---|---|
| 1 | **프레임 각속도 부호 규약** | shear/N 섹터는 검출하지 못한다. tilt 섹터만 잡는다 |
| 2 | **게이지가 회전 3개를 다 쓴다** | R₁만 켜면 shear 식이 전부 틀리는데 N′·λ′·A′ 는 맞아 보인다 |
| 3 | **trace-free 를 행렬연산으로 만들기** | 원소가 복합식이 되어 치환이 통째로 무시돼도 "돌아간다" |
| 4 | **심볼 충돌 + 순차 치환** | `{v0:v1, v1:v2}` 를 `.subs(dict)` 하면 오염 |

추가: WE/Ringström **9배 함정**, Σ_WE vs Σ_θ **√3 함정** (타입으로 분리).

## 구조

```
bianchi/
  conventions.py     규약 + 함정 가드          (PR-03)
  algebra.py         유형 분류기, κ=1/h        (PR-04)
  symbolic/
    frame.py         유도 엔진 (L0~L4)         (PR-02)
    oracles.py       오라클 A~F + 커널 실증    (PR-05)
  charts/
    class_a.py       Wainwright–Hsu            (PR-06)
    class_b.py       HW93, κ 파라미터화        (PR-07)
    exceptional.py   VI*₋₁/₉                   (PR-08)
    general.py       Layer 0 (Fermi)           (PR-11)
    class_b_tilted.py Hervik 11변수            (PR-16)
    type_ix_d.py     D-정규화 (재붕괴)         (PR-21)
  matter/
    fluid.py         tilted γ-law              (PR-14/15)
    components.py    다중유체·스칼라·자기장    (PR-18/19/20)
  constraints.py     잔차 + GN 투영            (PR-12)
  integrate.py       diffrax 래퍼              (PR-09)
  batch.py           정렬·버케팅·청킹          (PR-22/23)
  physical.py        물리량 재구성             (PR-25)
  thresholds.py      γ 임계값 카탈로그         (PR-17)
  analysis/dynamics.py 고정점·안정성·Lyapunov  (PR-26/27)
```

## 확정된 핵심 결과

* **κ = 1/h** 로 class B 전체를 단일 실수 파라미터로 덮는다. κ 는 **운동 상수**.
* 예외형은 κ=−9 를 상수로 박지 않고 `det L = 3(9A²+n₂n₃) = 0` 에서 판정.
* **`A_exc = A_WE`** — 2배 환산 없음. `Ω = 1−Σ²−N₋²−4A²` 의 4 는 게이지 `n₂₃=3A` 산물.
* **`Ω′` 의 분모는 `G₊`** (G₋ 아님). 8개 후보 중 정확히 하나.
  구조적으로 **G₋ 가 tilt 를, G₊ 가 에너지밀도를 지배**한다.
* `Ω′|_{V=1} = Ω(2q−2+2A·c−Σ_ab c^a c^b)` — **Ω 은 V=1 면에서 0 이 되지 않는다.**
* 재붕괴는 H-차트로 **잡을 수 없다** (H=e^{lnH}>0 이라 근이 없음). D-차트 필수.
* Collins–Stewart(II): **Σ₊ = (3γ−2)/8**, Ω = 9/8 − 3γ/16 (유도 확정).

## γ 임계값 (원문 PDF 대조 확정)

| 유형 | 임계값 |
|---|---|
| tilted II | 2/3 → 10/7 → **14/9** → extreme |
| tilted VI₀ | 2/3, 10/9, **6/5**, 4/3 |
| tilted IV·VII_h | **Σ₊ 의존**: `6/(5+2Σ₊)`, `(4+Σ₊)/3`, `3/(2−Σ₊)` |
| tilted VI_h | 2/3, 6/5, **h 의존** `2(3+√−h)/(5+3√−h)` |

❌ γ=6/7 은 tilt 임계값이 아니다 (단조함수 존재조건). `thresholds.FORBIDDEN` 참조.
⚠️ ar5iv HTML 은 관련 논문 두 편을 본문 중간에서 자른다 — **PDF 로 볼 것**.

## 실행

```bash
pip install -e .
PYTHONPATH=. pytest tests/ -q      # 129 tests (v1.1)
PYTHONPATH=. python scripts/demo.py
```

## v1.1 감사 재현 (외부검토 대응)

```bash
pip install -r requirements.lock
cd audit && python run_all.py     # 25/25 checks, manifest.json 생성
```

`audit/` 는 `bianchi/` 와 코드를 공유하지 않는 독립 재유도 엔진이다.
구조상수 -> 4d 프레임 접속 -> Riemann/Ricci/Einstein 을 처음부터 다시 만들고,
텐서 기저 최소제곱 동정으로 닫힌 형태의 계수를 확정한다.
기대 잔차와 시드는 `audit/manifest.json` 및 보고서 부록 B 에 고정되어 있다.

핵심 규약 (하나만 기억할 것):

> COMMUTATOR 규약에서 **모든** 공간 프레임 지표는 같은 회전항을 받는다.
> 벡터 `Y_a' ⊃ +(R × Y)_a`, 텐서 `X_ab' ⊃ +2 eps_{cd<a} R^c X_b>^d`.
> 예외 없음 — sigma, n, a, v, B, 구속벡터 C 전부.
