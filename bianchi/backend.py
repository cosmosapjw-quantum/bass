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


# ════════════════════════════════ 운동론 계층 (H2/H3/H4)
# ★ 두 경로(freestream 구적 / PSTF 계층) 를 **디스패치 층에서도 분리해 유지**한다 —
#   한쪽이 실수하면 다른 쪽이 잡는 구조를 Rust 전환 후에도 잃지 않기 위해.
def j_moment(a_vec, mass, l, i, dipole_eps=0.0, dipole_axis=2, force_python=False):
    """구적 모멘트 J^(i)_{A_l} → rank-l ndarray (l=0 은 스칼라).

    Rust: 색인표 캐시 + Rayon (반경노드 병렬).  폴백: `matter.hierarchy.J_moment`.
    """
    a_vec = np.asarray(a_vec, float)
    if HAVE_RUST and not force_python:
        flat = np.asarray(_rc.kin_j_moment(a_vec, float(mass), int(l), int(i),
                                           float(dipole_eps), int(dipole_axis)))
        return float(flat[0]) if l == 0 else flat.reshape((3,) * l)
    from bianchi.matter import freestream as _fs
    from bianchi.matter import hierarchy as _H
    f0 = _fs.f_fermi_dirac if dipole_eps == 0.0 else _H.f_dipole(dipole_eps, dipole_axis)
    return _H.J_moment(a_vec, mass, l, i, f0)


def kinetic_moments(a_vec, mass, force_python=False):
    """freestream 대응 (ρ, p, π_ab) — 경로 A(정확 구적)."""
    a_vec = np.asarray(a_vec, float)
    if HAVE_RUST and not force_python:
        rho, p, pi = _rc.kin_moments(a_vec, float(mass))
        return float(rho), float(p), np.asarray(pi)
    from bianchi.matter import freestream as _fs
    rho, p, pi = _fs.moments(a_vec, mass)
    return float(rho), float(p), np.asarray(pi, float)


def hierarchy_integrate(a0, mass, H, sigma_diag, t_end, nsteps=40, l_max=4, i_max=2,
                        dipole_eps=0.0, n_e_sigma_T=0.0, route="analytic",
                        force_python=False):
    """계층 RK4 적분 → dict(t, rho, p, pi[N,3,3]).

    `n_e_sigma_T > 0` 이면 H3 Thomson 충돌항이 켜진다 (0 이면 무충돌과 **비트-정확** 동일).

    ★ 강성 경고: n_eσ_T·dt·(1−λ₂) ≳ 2.785 면 RK4 가 불안정하다 —
      `thomson_stiffness()` 로 사전 진단할 수 있다.
    """
    a0 = np.asarray(a0, float); sigma_diag = np.asarray(sigma_diag, float)
    if HAVE_RUST and not force_python:
        if n_e_sigma_T == 0.0:
            t, rho, p, pi = _rc.kin_integrate(a0, float(mass), float(H), sigma_diag,
                                              float(t_end), int(nsteps), int(l_max),
                                              int(i_max), float(dipole_eps))
        else:
            t, rho, p, pi = _rc.kin_integrate_collisional(
                a0, float(mass), float(H), sigma_diag, float(n_e_sigma_T),
                float(t_end), int(nsteps), int(l_max), int(i_max),
                float(dipole_eps), route)
        return dict(t=np.asarray(t), rho=np.asarray(rho), p=np.asarray(p),
                    pi=np.asarray(pi).reshape(-1, 3, 3))
    if n_e_sigma_T != 0.0:
        raise NotImplementedError(
            "충돌 계층의 Python 폴백 적분기는 없다 — 계수는 collision.py 에서 검증되어 "
            "있으나 궤적 적분은 Rust 경로만 제공한다 (force_python=False 로 호출)")
    from bianchi.matter import hierarchy as _H
    res = _H.integrate_hierarchy(a0, mass, H, sigma_diag, t_end, nsteps=nsteps,
                                 l_max=l_max, i_max=i_max)
    return dict(t=np.asarray(res["t"]),
                rho=np.array([float(J[(0, 0)]) for J in res["J"]]),
                p=np.array([float(J[(0, 1)]) / 3.0 for J in res["J"]]),
                pi=np.array([np.asarray(J[(2, 0)], float) for J in res["J"]]))


# ── H3 · Thomson 충돌 (경로 A = 수치 위상함수, 경로 B = 해석 다극)
def thomson_eigenvalue(l, route="analytic", force_python=False):
    """λ_l.  route='analytic' → 해석 다극(경로 B), 'numeric' → 위상함수 적분(경로 A)."""
    if HAVE_RUST and not force_python:
        return (_rc.kin_thomson_eigenvalue(int(l)) if route == "analytic"
                else _rc.kin_thomson_eigenvalue_numeric(int(l), 200))
    from bianchi.matter import collision as _C
    return (_C.thomson_eigenvalue(l) if route == "analytic"
            else _C.thomson_eigenvalue_numeric(l))


def thomson_viscosity(rho, n_e_sigma_T, H=0.0, include_thomson_9_10=True,
                      force_python=False):
    """유도된 광자 전단점성 → dict(eta, tau_pi, damping_rate, eta_times_nesigT_over_rho).

    ★ 9/10 (Thomson 사중극) 포함 시 8/27, 미포함 시 4/15 — **차이의 전부가 이 인자**다.
      문헌 관례가 갈리므로 플래그로 노출하고 어느 쪽이 맞다고 단정하지 않는다.
    """
    if HAVE_RUST and not force_python:
        eta, tau, damp, ratio = _rc.kin_thomson_viscosity(
            float(rho), float(n_e_sigma_T), float(H), bool(include_thomson_9_10))
        return dict(eta=eta, tau_pi=tau, damping_rate=damp,
                    eta_times_nesigT_over_rho=ratio,
                    include_thomson_9_10=bool(include_thomson_9_10))
    from bianchi.matter import collision as _C
    return _C.thomson_viscosity(rho, n_e_sigma_T, H, include_thomson_9_10)


def thomson_stiffness(n_e_sigma_T, dt, force_python=False):
    """RK4 강성 진단 → (n_eσ_T·dt·(1−λ₂), 안정 여부).  2.785 는 RK4 실축 안정한계."""
    if HAVE_RUST and not force_python:
        r, ok = _rc.kin_stiffness_ratio(float(n_e_sigma_T), float(dt))
        return float(r), bool(ok)
    from bianchi.matter import collision as _C
    r = n_e_sigma_T * dt * _C.thomson_damping(2)
    return float(r), bool(r < 2.785)


# ── H4 · imperfect fluid 유도 (경로 A = 구적 차분, 경로 B = 계층 방정식)
def transport_coefficients(mass=0.0, a_vec=(1.0, 0.85, 1.18), H=1.0,
                           route="hierarchy", force_python=False):
    """유도된 (η, τ_π) — 자유 파라미터 없음.  무질량: τ_π = 1/(4H), η = ρ/(15H).

    route='hierarchy' → 경로 B(계층 방정식), 'quadrature' → 경로 A(구적 차분).
    ★ 경로 A 는 유한차분 조건수 때문에 유효자리 ~7 자리다 (경로 B 는 방정식 평가라 정확).
    """
    a_vec = np.asarray(a_vec, float)
    if HAVE_RUST and not force_python:
        eta, tau, rho, damp, src, eta_rh = _rc.kin_transport_coefficients(
            float(mass), a_vec, float(H), route)
        return dict(eta=eta, tau_pi=tau, rho=rho, damping_rate=damp,
                    source_coeff=src, eta_over_rho_H=eta_rh, route=route)
    from bianchi.matter import viscous_derived as _vd
    return _vd.transport_coefficients(mass, tuple(a_vec), H_hubble=H, route=route)


def viscous_cross_validate(mass=0.0, a_vec=(1.0, 0.85, 1.18), H=1.0,
                           force_python=False):
    """★ 두 경로 교차검증 → dict(damping_rel_diff, source_rel_diff, agree).

    이 교차검증이 실제로 버그를 잡은 이력이 있다 (등방 a_vec rescale → m=1 에서 23%).
    Rust 전환 후에도 **양쪽 경로를 모두 유지**하는 이유다.
    """
    a_vec = np.asarray(a_vec, float)
    if HAVE_RUST and not force_python:
        d, s, ok = _rc.kin_cross_validate(float(mass), a_vec, float(H), 2e-3, 5e-3)
        return dict(damping_rel_diff=d, source_rel_diff=s, agree=bool(ok))
    from bianchi.matter import viscous_derived as _vd
    return _vd.cross_validate(mass, H_hubble=H)


# ════════════════════════════════ tilted (boosted) 구적 (H5-e)
def j_moment_tilted(a_vec, v, mass, l, i, dipole_eps=0.0, dipole_axis=2,
                    force_python=False):
    """tilted 관측자의 J′^(i)_{A_l} → rank-l ndarray (l=0 은 스칼라).

    ★ 오라클 순수성 주의: `audit/h5d_tilted_residual.py` 는 **Python 경로를 기본**으로
      쓴다 (계층을 시험하는 오라클이므로).  이 디스패치는 생산 경로용이며, 두 경로가
      1e−12 이내 일치함은 차등테스트로 고정돼 있다.
    """
    a_vec = np.asarray(a_vec, float); v = np.asarray(v, float)
    if HAVE_RUST and not force_python:
        flat = np.asarray(_rc.kin_j_moment_tilted(a_vec, v, float(mass), int(l), int(i),
                                                  float(dipole_eps), int(dipole_axis)))
        return float(flat[0]) if l == 0 else flat.reshape((3,) * l)
    from bianchi.matter import freestream as _fs
    from bianchi.matter import hierarchy as _H
    from bianchi.matter import tilted_moments as _TM
    f0 = _fs.f_fermi_dirac if dipole_eps == 0.0 else _H.f_dipole(dipole_eps, dipole_axis)
    return _TM.J_moment_tilted(a_vec, v, mass, l, i, f0, backend="python")


def moments_tilted(a_vec, v, mass, force_python=False):
    """tilted 관측자가 보는 (ρ′, p′, q′_A, π′_AB)."""
    a_vec = np.asarray(a_vec, float); v = np.asarray(v, float)
    if HAVE_RUST and not force_python:
        rho, p, q, pi = _rc.kin_moments_tilted(a_vec, v, float(mass))
        return float(rho), float(p), np.asarray(q), np.asarray(pi)
    from bianchi.matter import tilted_moments as _TM
    return _TM.moments_tilted(a_vec, v, mass, backend="python")


def boost_shell_residual(a_vec, v, mass, force_python=False):
    """★ boost 대수 자기검증 λ′² = E′² − m² 의 격자 전점 최대 상대잔차."""
    a_vec = np.asarray(a_vec, float); v = np.asarray(v, float)
    if HAVE_RUST and not force_python:
        return float(_rc.kin_boost_shell_residual(a_vec, v, float(mass)))
    from bianchi.matter import tilted_moments as _TM
    return _TM.boost_algebra_residual(tuple(a_vec), tuple(v), mass)["mass_shell"]
