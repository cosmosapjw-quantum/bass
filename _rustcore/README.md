# bianchi_rustcore — Rust 연산 코어

Bianchi 배경 우주론 솔버의 native 수치 백엔드. 지원 경로는 Rust가 실행하고,
Python은 명시적 오라클과 아직 이식되지 않은 경로의 오케스트레이션을 유지한다.
노출된 수치 함수는 해당 Python 오라클과 **차등테스트로 대조**된다.

## 현황 — R-DAG 완주 (R0·R1·R2·R3·R4 + 통합; R5 GPU 만 유예)

```
R0 스캐폴드 ─┬─> R1 광선추적 ✓ ─┬─> R4 조석 닫힌형 ✓ ─> 광학 완전가속 ✓
             └─> R2 RHS+diffsol ✓ ┴─> R3 배치(Rayon) ✓ ─> 통합 bianchi.backend ✓
                                                          (R5 GPU: 유예)
```


| 노출 함수 | 대응 Python 오라클 | 상태 |
|---|---|---|
| `rotation_matrix(R)` | `conventions.rotation_matrix` | 패리티 ✓ |
| `tracefree_from_5(...)` | `conventions.tracefree_from_5` | 패리티 ✓ |
| `p_double(N,A,x)` | `rays.frame.P_double` | 패리티 ✓ |
| `trace_ray_diag(...)` | `rays.geodesics.trace_ray_diag_bianchi` | **비트-정확** ✓ |
| `trace_rays_batch(...)` | 위를 방향 루프 (CMB z(n̂)) | 병렬(Rayon), 비트-정확 ✓ |
| `trace_optical_diag(...)` | `rays.optical.trace_optical_diag_bianchi` | z 비트-정확, d_A 2.3e-16 ✓ |
| `trace_optical_batch(...)` | 위를 방향 루프 (d_A 지도) | 병렬(Rayon) ✓ |
| `chart_rhs(...)` | `charts.class_a/class_b.rhs` | **비트-정확 (0.0)** ✓ |
| `chart_aux(...)` | `charts.*.aux` / `codazzi` | Ω·Codazzi 진단 ✓ |
| `integrate_background(...)` | `integrate.solve` (diffrax Kvaerno5) | diffsol BDF, 2.4e-10 ✓ |
| `integrate_batch(...)` | 위를 초기조건 루프 | 병렬(Rayon), 낙오자 격리 ✓ |

**검증:** `tests/test_rustcore_differential.py` **21개 통과** (측지 z 최대 상대오차
**0.00e+00**, 광학 d_A 2.3e-16, 스크린 직교성 1.1e-15, EdS 기준해 <1e-6).
전체 스위트 회귀 **263 통과**.

**성능 (2코어 실측):**

| 작업 | Python | Rust | 배율 |
|---|---|---|---|
| 측지 전천 지도 (64×128×1500) | ~139 분 | **~0.7 초** | ≈12,000× |
| 광학 d_A 지도 (64×128×1500) | ~400 분 | **~5.2 초** | ≈4,650× |
| 배경 배치 스캔 (K=256, 강성 15%) | 8.5 초 (JAX vmap, **warm**) | **33 ms** | ≈260× |

numpy 는 스텝마다 소형 배열 오버헤드가, 광학은 추가로 sympy/JAX 조석 평가가 병목이었다.
배경 배치는 JAX 가 이미 JIT/vmap 된 상태(warm)와 비교한 값이다 — 이득의 원천은
**낙오자 격리**다(아래).

### R4 — 조석행렬의 탈-sympy (닫힌형)

Python 은 144성분 sympy pickle 을 lambdify/vmap 해 조석행렬을 만든다.  대각 Bianchi I
(N=A=R=0, ³R=0) 에서는 Gauss-Codazzi 로 프레임 Riemann 이 **닫힌형**이다 (오라클 대조로 확인):

```
K = Hδ + σ,  K̇ = Ḣδ + σ̇,  M = -(K̇ + K²)
R_{0a0b} = M_ab      R_{abcd} = K_ac K_bd - K_ad K_bc      R_{0abc} = 0     (4.4e-16)
```

조석 축약을 더 줄이면 (E_A=(α_A,u_A), k=(k⁰,κ), w_A = α_A κ - k⁰ u_A):

```
T_AB = -[ w_A·M w_B + (u_A·K u_B)(κ·Kκ) - (u_A·Kκ)(Kκ·u_B) ]                (1.4e-14)
```

→ sympy/JAX 없이 순수 산술.  일반 유형(N,A,R≠0)은 후속 codegen 경로로 확장한다.

### R2/R3 — 배경 ODE (diffsol BDF + Rayon 배치)

차트 RHS (class_a 5상태 Σ₊,Σ₋,N₁,N₂,N₃ / class_b 5상태 Σ₊,Σ̃,Δ,Ã,N₊ + κ) 를 Rust 로
옮기고 **diffsol BDF(가변차수)** 로 적분한다.  야코비안-벡터 곱은 중심차분 — FD 는
Newton 수렴률에만 영향을 주고 해의 정확도는 잔차가 결정하므로 안전하다.

**낙오자 격리 (R3 의 핵심).**  JAX 의 batched `while_loop` 은 종료조건을 배치축에
OR-리듀스해 *끝난 원소도 본문을 실행*하므로 비용이 `batch × max_steps` 다.  Rayon 은
원소마다 독립 적분이라 강성 낙오자가 배치 전체를 오염시키지 않는다.  실측(K=256, 15% 가
Kasner 근방)에서 Rust 는 229/256 을 완료하고 **실패 27개는 전부 Ω<0 인 비물리 초기조건**
이었다 (JAX 도 같은 원소에서 발산: 0/8 성공).  즉 실패는 솔버 약점이 아니라 초기데이터
자체의 발산이며, Rust 는 그것을 원소 단위로 격리해 보고한다.

**보존 성질.**  `N_i' = (…)·N_i` 의 곱셈 구조가 Rust 에서도 유지되어 N_i = 0 과 부호가
부동소수점에서 **정확히** 보존된다 (유형 안전성).  Class B Codazzi 구속 C 도 궤적 위에서
<1e-8 로 유지된다.

## 낮은 수준의 native 복구 빌드

일반 사용자는 repository 루트의 단일 pip resolver 진입점을 사용한다. 아래는
검증된 native 휠이 없을 때의 개발/복구 절차이며 Python 패키지를 따로 설치하는
두 번째 정상 진입점이 아니다. Rust 1.94.1과 maturin 1.14.1을 사용하고 lockfile을
변경하지 않는다.

시스템 Python 환경(venv 없이)에서 휠을 만들어 설치:

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install 'maturin==1.14.1'
cd _rustcore
python -m maturin build --release --locked
cd ..
python -m pip install --constraint requirements.lock _rustcore/target/wheels/bianchi_rustcore-0.1.0-*.whl .
```

native crate만 개발하는 경우에도 lockfile을 고정한다:

```bash
cd _rustcore
python -m maturin develop --release --locked
```

## 테스트

```bash
cargo test --lib --locked --offline                # 검증된 vendor/cache가 있을 때
pytest ../tests/test_rustcore_differential.py -q   # 차등테스트 (인수 게이트)
```

`extension-module` 은 **crate feature** 라 `cargo test` 는 이를 끄고 libpython 에 링크,
`maturin` 은 `pyproject [tool.maturin].features` 로 켜서 확장모듈을 만든다.

## 구조

```
src/
  lib.rs                 PyO3 모듈 등록 + 경계(무복사 numpy, GIL 해제 detach)
  core/conventions.rs    EPS3·rotation·tracefree·P_double  (Python 규약 미러)
  rays/geodesic.rs       photon_rhs (일반) + trace_ray_diag (Euler 정확 포트) + Rayon 배치
  rays/optical.rs        스크린 기저·3-패스 광학·조석 닫힌형(R4)·Jacobi RK4 + Rayon 배치
  ode/charts.rs          class_a/class_b RHS·보조량·Codazzi·J·v (Python 차트 미러)
  ode/solve.rs           diffsol BDF 적분 + Rayon 배치 스캔 (낙오자 격리)
```

## 통합 — `bianchi.backend`

RF-00 이후 공개 경로는 정적 capability matrix를 따른다. native 지원 경로는
`rust_required`로 실패 폐쇄되고, Python 오라클은 명시적으로만 선택한다. 아직
이식되지 않은 경로만 보이는 `legacy_python_transitional` 상태를 사용한다:

```python
from bianchi import backend
from bianchi.backend_policy import BackendPolicy
backend.capability_report()                 # ABI/build/policy 진단
backend.ray_final_z_batch(model, nhats, t0, t_end)      # R1
backend.optical_batch(model, nhats, t0, t_end)          # R1+R4
backend.integrate_background('class_a', y0, ts, gamma)  # R2
backend.integrate_batch('class_a', y0s, ts, gamma)      # R3
# policy=BackendPolicy.PYTHON_ORACLE 는 차등테스트·디버깅에만 명시적으로 사용
```

검증된 Python 모듈은 **수정하지 않았다** — 디스패치만 얹었다.
구 `bianchi.rays._dispatch` 는 하위호환 별칭으로 유지된다.

## 다음

- **R5 GPU** (유예): diffsol 실험적 CUDA 백엔드 재활용 또는 cudarc.  `cuda` feature 뒤.
- 일반 유형 조석: N,A,R≠0 의 Riemann 을 codegen 으로 Rust 상수산술화 (현재는 대각 I).
- 나머지 차트(class_b_tilted, exceptional, type_ix_d)의 RHS 이식.
- 수치 견고성 (계획 §4a): 이벤트 검출(Kasner 바운스), 혼합정밀, 구속 사영.
