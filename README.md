# bianchi-solver

모든 Bianchi 유형(I–IX, class A/B, 예외형 VI\*₋₁/₉)과 tilted 모델의
배경 우주론 solver. 지원 완료된 생산 경로는 `bianchi_rustcore`를 사용하고,
Python/JAX + diffrax 구현은 명시적 오라클 또는 아직 이식되지 않은 경로로 유지한다.

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

## 설치

정상 설치 단위는 루트 `bianchi-solver`와 정확히 같은 버전의
`bianchi-rustcore` 휠이다. 먼저 현재 Python/플랫폼에 맞는 검증된 로컬 휠의
경로를 정한다. RF-00 native r3 CPython 3.12 Linux x86-64 휠의 SHA-256은
`e050974a78e5e02dc5ce8b77aa1dff5bf2bd62d2f52cb2cdcccf8b49d57f3917`이다.

```bash
export BASS_NATIVE_WHEEL=/absolute/path/to/verified-native-wheel/bianchi_rustcore-0.1.0-cp312-cp312-manylinux_2_34_x86_64.whl
printf '%s  %s\n' e050974a78e5e02dc5ce8b77aa1dff5bf2bd62d2f52cb2cdcccf8b49d57f3917 "$BASS_NATIVE_WHEEL" | sha256sum --check --strict
python -m pip install --constraint requirements.lock "$BASS_NATIVE_WHEEL" .
```

이 기본 resolver 진입점은 생산용 Rust-first 최소 프론트엔드만 설치한다:
정확히 일치하는 native 휠과 NumPy가 필수이고 JAX/diffrax/SciPy/SymPy는 로드하지
않는다. 로컬 휠이 없거나 현재
Python/ABI/플랫폼과 맞지 않으면 pip가 설치를 실패시킨다. 다른 버전의 native
배포본이나 Python-only 설치로 조용히 진행하지 않는다. 소스에서 native 휠을
복구해야 할 때만 아래 `_rustcore/README.md`의 고정 도구·`--locked` 절차 또는
`bootstrap.sh` 복구 helper를 사용한다.

독립 Python 오라클이나 기호/과학 프론트엔드가 필요한 환경만 같은 resolver에
`python-oracle` extra를 명시한다. 이 extra는 JAX/diffrax/equinox/optimistix/lineax,
SciPy, SymPy, mpmath를 설치하며 생산 native fallback을 허용하지 않는다.

```bash
python -m pip install --constraint requirements.lock "$BASS_NATIVE_WHEEL" '.[python-oracle]'
```

직접 JAX 오라클 코드를 작성할 때는 배열이나 JAX companion package를 만들기 전에
x64 로더를 명시적으로 호출한다. 실패하면 설치/구성 정보를 포함한
`OptionalDependencyError` 계열 예외가 발생하며 float32로 계속하지 않는다.

```python
from bianchi.optional_dependencies import require_jax_x64

jax, jnp = require_jax_x64(feature="interactive_python_oracle")
```

## 실행

```bash
PYTHONPATH=. python scripts/demo.py
```

`bianchi.backend.capability_report()`는 선택 policy, extension/distribution 버전,
Python ABI, Cargo.lock digest, build profile, CPU dispatch, thread-pool 크기와 optional
features를 보고한다. native 지원 경로의 missing/ABI mismatch는 typed error이며
Python 오라클로 자동 폴백하지 않는다.

전체 과거 회귀군은 설치 smoke test가 아니다. 변경 경로에 해당하는 검증 명령은
각 작업의 evidence/CI receipt를 따른다.

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
