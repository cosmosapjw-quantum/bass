"""
통합 백엔드 디스패치 — Rust 코어(`bianchi_rustcore`) 우선, Python/JAX 오라클 폴백.

계획 §2 하이브리드의 단일 진입점.  검증된 Python 모듈은 **건드리지 않고**, 여기서
가용성에 따라 경로를 고른다.  두 경로는 차등테스트(`tests/test_rustcore_differential.py`)
로 대조되어 있으므로 폴백은 항상 안전하다.

    from bianchi import backend
    backend.available()            # True 면 Rust 가속 경로
    backend.ray_final_z_batch(...) # 측지 z(n̂)      (R1)
    backend.optical_batch(...)     # Sachs d_A(n̂)   (R1+R4)
    backend.integrate_background(...) / integrate_batch(...)   # 배경 ODE (R2/R3)

모든 함수는 `force_python=True` 로 오라클 경로를 강제할 수 있다 (차등테스트·디버깅용).
"""
from __future__ import annotations

import numpy as np

try:
    import bianchi_rustcore as _rc
    HAVE_RUST = True
except ImportError:                       # pragma: no cover
    _rc = None
    HAVE_RUST = False


def available() -> bool:
    """Rust 코어 사용 가능 여부."""
    return HAVE_RUST


def name() -> str:
    """활성 백엔드 이름 ('rust' 또는 'python')."""
    return "rust" if HAVE_RUST else "python"


def info() -> dict:
    """진단용 백엔드 정보."""
    return dict(backend=name(), rust_available=HAVE_RUST,
                functions=sorted(f for f in dir(_rc) if not f.startswith("_")) if HAVE_RUST else [])


# ════════════════════════════════ 광선추적 (R1)
def ray_final_z_batch(model, nhats, t0, t_end, nsteps=4000, force_python=False):
    """방향 배열(K,3) → 방향별 최종 적색이동 z(n̂)  (CMB 패턴용)."""
    nhats = np.atleast_2d(np.asarray(nhats, float))
    if HAVE_RUST and not force_python:
        return np.asarray(_rc.trace_rays_batch(
            float(model["H0"]), np.asarray(model["Sigma0"], float),
            float(model["Omega0"]), float(model["gamma"]),
            nhats, float(t0), float(t_end), int(nsteps)))
    from bianchi.rays import geodesics as geo
    out = np.empty(len(nhats))
    for i, nh in enumerate(nhats):
        m = dict(model); m["nhat"] = nh
        hist = geo.trace_ray_diag_bianchi(m, t0, t_end, nsteps=nsteps)
        out[i] = hist[-1]["z"] if hist else np.nan
    return out


def optical_batch(model, nhats, t0, t_end, nsteps=4000, force_python=False):
    """방향 배열(K,3) → (z[K], d_A[K]).  Sachs 광학 (조석 닫힌형 R4)."""
    nhats = np.atleast_2d(np.asarray(nhats, float))
    if HAVE_RUST and not force_python:
        z, dA = _rc.trace_optical_batch(
            float(model["H0"]), np.asarray(model["Sigma0"], float),
            float(model["Omega0"]), float(model["gamma"]),
            nhats, float(t0), float(t_end), int(nsteps))
        return np.asarray(z), np.asarray(dA)
    from bianchi.rays import optical as opt
    z = np.empty(len(nhats)); dA = np.empty(len(nhats))
    for i, nh in enumerate(nhats):
        m = dict(model); m["nhat"] = nh
        r = opt.trace_optical_diag_bianchi(m, t0, t_end, nsteps=nsteps)
        z[i], dA[i] = r["z_final"], r["dA_final"]
    return z, dA


# ════════════════════════════════ 배경 ODE (R2/R3)
_CHART_MODULES = {"class_a": "bianchi.charts.class_a", "class_b": "bianchi.charts.class_b"}


def integrate_background(chart, y0, t_eval, gamma, kappa=0.0,
                         rtol=1e-10, atol=1e-12, force_python=False):
    """차트 배경 ODE 를 τ 격자에서 적분.  반환 (ys[M,5], ok).

    Rust: diffsol BDF(가변차수, 강성 적합).  폴백: diffrax Kvaerno5.
    """
    y0 = np.asarray(y0, float); t_eval = np.asarray(t_eval, float)
    if HAVE_RUST and not force_python:
        ys, ok = _rc.integrate_background(chart, y0, t_eval, float(gamma),
                                          float(kappa), float(rtol), float(atol))
        return np.asarray(ys), bool(ok)
    # 폴백: JAX/diffrax
    import importlib
    import jax.numpy as jnp
    from bianchi import integrate as itg
    mod = importlib.import_module(_CHART_MODULES[chart])
    args = {"gamma": gamma} if chart == "class_a" else {"gamma": gamma, "kappa": kappa}
    State = mod.StateA if chart == "class_a" else mod.StateB
    cfg = itg.SolverConfig(rtol=rtol, atol=atol, max_steps=100000)
    sol = itg.solve(lambda t, y, a: mod.rhs(t, y, a), State.from_array(jnp.asarray(y0)),
                    float(t_eval[0]), float(t_eval[-1]), args,
                    ts=jnp.asarray(t_eval), cfg=cfg)
    ys = np.asarray(jnp.stack([getattr(sol.ys, n) for n in mod.STATE_NAMES], axis=-1))
    return ys, bool(np.all(np.isfinite(ys)))


def integrate_batch(chart, y0s, t_eval, gamma, kappa=0.0,
                    rtol=1e-10, atol=1e-12, force_python=False):
    """배치 스캔: 초기조건 (K,5) → (마지막 상태 (K,5), 성공 마스크 (K,)).

    ★ Rust 경로는 원소마다 독립 적분(Rayon)이라 **낙오자가 배치 전체를 오염시키지
      않는다** — JAX batched while_loop 의 `batch × max_steps` 병리를 회피 (계획 §1).
    """
    y0s = np.atleast_2d(np.asarray(y0s, float)); t_eval = np.asarray(t_eval, float)
    if HAVE_RUST and not force_python:
        ys, ok = _rc.integrate_batch(chart, y0s, t_eval, float(gamma),
                                     float(kappa), float(rtol), float(atol))
        return np.asarray(ys), np.asarray(ok) == 1.0
    ys = np.empty((len(y0s), 5)); ok = np.zeros(len(y0s), bool)
    for i, y0 in enumerate(y0s):
        y, good = integrate_background(chart, y0, t_eval, gamma, kappa,
                                       rtol, atol, force_python=True)
        ys[i] = y[-1] if good else np.nan
        ok[i] = good
    return ys, ok


def chart_rhs(chart, y, gamma, kappa=0.0, force_python=False):
    """차트 RHS 단일 평가 (진단·차등테스트용)."""
    y = np.asarray(y, float)
    if HAVE_RUST and not force_python:
        return np.asarray(_rc.chart_rhs(chart, y, float(gamma), float(kappa)))
    import importlib
    import jax.numpy as jnp
    mod = importlib.import_module(_CHART_MODULES[chart])
    State = mod.StateA if chart == "class_a" else mod.StateB
    args = {"gamma": gamma} if chart == "class_a" else {"gamma": gamma, "kappa": kappa}
    return np.asarray(mod.rhs(0.0, State.from_array(jnp.asarray(y)), args).as_array())
