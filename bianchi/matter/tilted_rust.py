"""
R5b · tilted 계층 적분의 **Rust 경로** — 마샬링과 배치만 담당한다.

R5a 는 텐서층(⊥J̇, D_B X, …)만 Rust 로 옮겼는데 **1.32배**에 그쳤다.  이유는 (l,i)
조합마다 작은 배열이 FFI 를 넘나들었기 때문이다.  여기서는 `equation_lhs` + 질량행렬
+ 선형해 + RK4 루프가 **한 호출** 안에 들어가고 J 가 Python 으로 돌아오지 않는다.

★ Rust 에 다시 구현하지 않고 **넘겨 주는 것**:
  · 시각별 기하 — `tilted._geometry` 는 sympy lambdify 로 만든 닫힌형이다.  RK4 가 쓰는
    시각(t, t+dt/2, t+dt)을 Python 이 **같은 부동소수 인자**로 계산해 넘긴다.
    (`(step+1)*dt` 와 `step*dt + dt` 는 부동소수에서 다르므로 스텝당 3 개를 넘긴다.)
  · PSTF 사영 연산자 Q_l (`hierarchy.pstf_operator`) 과 PSTF 정규직교기저 B_l
    (`tilted_mass.pstf_basis`) — 기저는 SVD 라 구현마다 달라질 수 있다.  Python 것을
    쓰면 질량행렬의 좌표계까지 같아져 M 을 성분별로 대조할 수 있다.

★ **비트-정확은 되지 않는다** (R5a 와 다른 점, 정직하게 적어 둔다):
  선형해가 LAPACK `dgesv` 가 아니라 Rust 쪽 부분추축 LU 이고, `to_coef`/`to_tensor` 도
  BLAS `dgemv` 가 아니라 단순 루프다.  둘 다 합 순서·FMA 사용이 달라 마지막 비트가
  어긋난다.  그래서 `th_force_and_matrix` 로 **F 와 M 을 따로** 노출해 두었다 —
  포트의 정확성(항 조립)과 선형대수의 반올림을 시험이 분리해 판정한다.
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import tilted as TL
from bianchi.matter import tilted_mass as TMass
from bianchi.matter.hierarchy import pstf_operator
from bianchi.backend_policy import load_native, select_backend

_GEO_LEN = 142
_SIGN_ORDER = ("A", "B", "C", "D", "E", "Omega", "divcon", "divfree")

#: 닫힘 모드 → Rust 코드.  `tilted_closure.MODES` 를 **전부** 옮겼다.
#:
#: ★ 처음에는 기본 경로("ratio" + J̇ 닫힘)만 옮겼는데, 계수를 세어 보니 tilted 시험
#:   1260 스텝 중 **310 스텝(25%)** 만 그 경로였다 — 나머지는 전부 대조군(frozen /
#:   jdot 끔 / 삼각절단 / 물리처방)이라 Python 으로 되돌아갔다.  대조군이 느리면
#:   전체 벽시계는 그대로다.  그래서 모드 전부를 포트했다.
MODE_CODE = {"frozen": 0, "ratio": 1, "ratio_scalar": 2, "zero": 3,
             "phys_sqrt": 4, "phys_5w": 5, "phys_interp": 6}


def available(mode="ratio"):
    """진단용 Rust 계층 가용성 (실제 dispatch 권한은 capability matrix)."""
    load = load_native()
    return bool(
        mode in MODE_CODE
        and load.available
        and load.module is not None
        and hasattr(load.module, "th_integrate")
    )


class _LazyRustAvailability:
    """Historical bool-like diagnostic without probing native code at import time."""

    def __bool__(self):
        return available()

    def __repr__(self):
        return repr(available())


# Historical test/diagnostic compatibility only. Numerical dispatch never reads it.
USE_RUST = _LazyRustAvailability()


def _native(route_id, mode="ratio"):
    return select_backend(route_id, mode=mode).native_module


def pack_geo(geo):
    """기하 dict → 평탄 142 벡터 (Rust `th_geo` 의 배치와 짝)."""
    out = np.empty(_GEO_LEN)
    out[0:12] = np.asarray(geo["eup"], float).ravel()
    out[12:24] = np.asarray(geo["edn"], float).ravel()
    out[24:36] = np.asarray(geo["deup"], float).ravel()
    out[36:52] = np.asarray(geo["hmix"], float).ravel()
    out[52:56] = np.asarray(geo["uup"], float).ravel()
    out[56:120] = np.asarray(geo["G"], float).ravel()
    out[120] = float(geo["H"])
    out[121:130] = np.asarray(geo["sigma"], float).ravel()
    out[130:139] = np.asarray(geo["omega"], float).ravel()
    out[139:142] = np.asarray(geo["udot"], float).ravel()
    return out


def pack_signs(signs=None):
    s = TL.SIGNS if signs is None else signs
    return np.asarray([float(s[k]) for k in _SIGN_ORDER])


def ops_and_bases(l_max):
    """(Q_l, B_l) 목록 — l < 2 의 Q_l 은 쓰이지 않으므로 빈 배열."""
    ops = [np.zeros(0) if l < 2
           else np.ascontiguousarray(pstf_operator(l), float).ravel()
           for l in range(l_max + 1)]
    bases = [np.ascontiguousarray(TMass.pstf_basis(l), float).ravel()
             for l in range(l_max + 1)]
    return ops, bases


def pack_state(J, l_max, i_max):
    """dict[(l,i)] → 평탄 벡터.  삼각절단으로 빠진 블록은 0 으로 채운다.

    ★ Rust 격자는 항상 직사각형이다.  `n_star` 절단에서는 그 블록들이 매 스텝
      닫힘에서 0 으로 덮이고 `unpack_state` 가 다시 떨어뜨리므로 물리에 영향이 없다.
    """
    out = []
    for l in range(l_max + 1):
        z = np.zeros(3 ** l)
        for i in range(i_max + 1):
            v = J.get((l, i))
            out.append(z if v is None
                       else np.atleast_1d(np.asarray(v, float)).ravel())
    return np.concatenate(out)


def unpack_state(flat, l_max, i_max, keys=None):
    out, p = {}, 0
    for l in range(l_max + 1):
        d = 3 ** l
        for i in range(i_max + 1):
            if keys is None or (l, i) in keys:
                v = np.asarray(flat[p:p + d], float)
                out[(l, i)] = float(v[0]) if l == 0 else v.reshape((3,) * l)
            p += d
    return out


def geometry_rows(bg, nsteps, dt):
    """RK4 가 쓰는 시각의 기하 — 스텝당 3 개 (t, t+dt/2, t+dt).

    ★ Python 루프와 **같은 산술**로 시각을 만든다: `t = step*dt` 뒤 `t + 0.5*dt`,
      `t + dt`.  `(step+1)*dt` 로 바꾸면 마지막 비트가 달라져 대조가 흐려진다.
    """
    rows = np.empty((3 * nsteps, _GEO_LEN))
    for step in range(nsteps):
        t = step * dt
        for k, tt in enumerate((t, t + 0.5 * dt, t + dt)):
            rows[3 * step + k] = pack_geo(bg.geometry(tt))
    return rows


def _cfg(mode, jdot_closure, n_star):
    return (int(MODE_CODE[mode]), bool(jdot_closure),
            int(-1 if n_star is None else n_star))


def integrate(bg, J0, t_end, nsteps, l_max, i_max, signs=None, mode="ratio",
              jdot_closure=True, n_star=None, keys=None, *, _native_module=None):
    """RK4 적분 (Rust) → (t 목록, J dict 목록).  `J0` 는 이미 걸러진 상태 dict."""
    dt = t_end / nsteps
    ops, bases = ops_and_bases(l_max)
    native = _native_module or _native("tilted.integrate", mode)
    hist = native.th_integrate(
        np.ascontiguousarray(pack_state(J0, l_max, i_max)),
        np.ascontiguousarray(geometry_rows(bg, nsteps, dt)),
        int(nsteps), float(dt), pack_signs(signs), ops, bases,
        int(l_max), int(i_max), *_cfg(mode, jdot_closure, n_star))
    ts = [0.0] + [step * dt + dt for step in range(nsteps)]
    return ts, [unpack_state(hist[k], l_max, i_max, keys)
                for k in range(nsteps + 1)]


def rhs(J, geo, l_max, i_max, signs=None, mode="ratio", jdot_closure=True,
        n_star=None, keys=None):
    """한 스텝 J̇ (Rust) — 차등시험용."""
    ops, bases = ops_and_bases(l_max)
    native = _native("tilted.rhs", mode)
    flat = native.th_rhs(np.ascontiguousarray(pack_state(J, l_max, i_max)),
                         np.ascontiguousarray(pack_geo(geo)), pack_signs(signs),
                         ops, bases, int(l_max), int(i_max),
                         *_cfg(mode, jdot_closure, n_star))
    return unpack_state(flat, l_max, i_max, keys)


def force_and_matrix(J, geo, l_max, i_max, signs=None, mode="ratio",
                     jdot_closure=True, n_star=None):
    """한 스텝의 (F 평탄벡터, M) — 포트의 어느 층까지 정확히 같은지 가르는 진단."""
    from bianchi.matter import tilted_mass as _TMass
    ops, bases = ops_and_bases(l_max)
    native = _native("tilted.force_and_matrix", mode)
    f, m = native.th_force_and_matrix(
        np.ascontiguousarray(pack_state(J, l_max, i_max)),
        np.ascontiguousarray(pack_geo(geo)), pack_signs(signs), ops, bases,
        int(l_max), int(i_max), *_cfg(mode, jdot_closure, n_star))
    n = _TMass.layout(l_max, i_max, n_star)[2]
    return np.asarray(f), np.asarray(m).reshape(n, n)
