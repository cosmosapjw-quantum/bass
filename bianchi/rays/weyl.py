"""
PR-45 · 프레임 Riemann/Weyl (JAX).  generate_weyl.py 의 pickle 을 로드해 lambdify.

    riemann_up(state)           R^a_{bcd}  (4,4,4,4)
    riemann_low(state)          R_{abcd}
    tidal_matrix(k, screen, state)   T_AB = -R_{a m b n} k^m k^n E_A^a E_B^b  (2,2)

state = dict(H, N(3,3), A(3), sigma(3,3), R(3), Hd, sigmad(3,3)).
좌표계 검산(D16): tr T = -R_ab k^a k^b (Ricci 집속), T 대칭, 잔차 2.8e-14.
"""
from __future__ import annotations

import os
import pickle

import numpy as np

from bianchi.optional_dependencies import require_jax_x64, require_optional

jax, jnp = require_jax_x64(feature=__name__)
sp = require_optional("sympy", feature=__name__)

_ETA = np.diag([-1.0, 1.0, 1.0, 1.0])
_ETA_J = jnp.asarray(_ETA)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PKL = os.path.join(os.path.dirname(_HERE), "generated", "riemann_frame.pkl")

_NAMES = None
_FN = None            # jitted: args -> (4,4,4,4) R^a_bcd
_KEYS = None


def _load():
    global _NAMES, _FN, _KEYS
    if _FN is not None:
        return
    if not os.path.exists(_PKL):
        raise FileNotFoundError(
            f"{_PKL} 없음 — 먼저 `python -m bianchi.rays.generate_weyl` 실행")
    payload = pickle.load(open(_PKL, "rb"))
    _NAMES = payload["names"]
    syms = [sp.Symbol(nm) for nm in _NAMES]
    comps = {k: sp.sympify(v) for k, v in payload["components"].items()}
    _KEYS = list(comps.keys())
    exprs = [comps[k] for k in _KEYS]
    flat = sp.lambdify(syms, exprs, "jax")     # JAX 백엔드 -> jit 가능
    idx = jnp.asarray(np.array(_KEYS))         # (ncomp, 4)

    @jax.jit
    def riem(args):
        vals = jnp.stack(flat(*args))          # (ncomp,)
        R = jnp.zeros((4, 4, 4, 4))
        return R.at[idx[:, 0], idx[:, 1], idx[:, 2], idx[:, 3]].set(vals)
    _FN = riem


def _pack_args(state):
    H = float(state["H"]); N = np.asarray(state["N"], float); A = np.asarray(state["A"], float)
    s = np.asarray(state["sigma"], float); R = np.asarray(state["R"], float)
    Hd = float(state.get("Hd", -H ** 2 - np.trace(s @ s) / 3.0))
    sd = state.get("sigmad", None)
    if sd is None:
        sd = -3.0 * H * s
    sd = np.asarray(sd, float)
    return [H, N[0, 0], N[0, 1], N[0, 2], N[1, 1], N[1, 2], N[2, 2],
            A[0], A[1], A[2], s[0, 0], s[0, 1], s[0, 2], s[1, 1], s[1, 2],
            R[0], R[1], R[2], Hd, sd[0, 0], sd[0, 1], sd[0, 2], sd[1, 1], sd[1, 2]]


def riemann_up(state):
    """R^a_{bcd} (4,4,4,4)."""
    _load()
    return np.asarray(_FN(jnp.asarray(_pack_args(state))))


def riemann_low(state):
    """R_{abcd} = eta_ae R^e_{bcd}."""
    return np.einsum("ae,ebcd->abcd", _ETA, riemann_up(state))


def tidal_matrix(k, screen, state):
    """T_AB = -R_{a m b n} k^m k^n E_A^a E_B^b  (스크린 사영 조석행렬).

    k: (4,) 널 벡터,  screen: (2,4) 스크린 기저 (k·E_A = u·E_A = 0).
    """
    Rl = riemann_low(state)
    k = np.asarray(k, float); screen = np.asarray(screen, float)
    T = -np.einsum("ambn,Aa,m,Bb,n->AB", Rl, screen, k, screen, k)
    return T


def _riem_up_jax(args):
    """jit 된 R^a_bcd (내부 고속 경로용; args = _pack_args 리스트)."""
    _load()
    return _FN(jnp.asarray(args))


def pack_state(state):
    """공개 래퍼: state -> (24,) arg 배열 (optical 2-패스에서 사용)."""
    return np.asarray(_pack_args(state), float)


def tidal_batch(ks, scs, args_batch):
    """배치 조석행렬:  (M,4),(M,2,4),(M,24) -> (M,2,2).  vmap+jit 로 1회 평가."""
    _load()

    @jax.jit
    def _one(k, sc, args):
        Ru = _FN(args)                                   # R^a_bcd
        Rl = jnp.einsum("ae,ebcd->abcd", _ETA_J, Ru)
        return -jnp.einsum("ambn,Aa,m,Bb,n->AB", Rl, sc, k, sc, k)

    return jax.vmap(_one)(jnp.asarray(ks), jnp.asarray(scs), jnp.asarray(args_batch))
