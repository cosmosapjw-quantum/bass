"""Atomic opt-in normal-time collision bridge for the real BASS PolQState.

The original Q Hubble-clock/Strang route is deliberately unchanged. This method
holds geometry and beta fixed during a caller-controlled collision substep.
No recoil, spectral support certification, matter feedback or native claim.
"""
from __future__ import annotations
import numpy as np
from . import _oracle
from ._core.tilted_collision import TiltedThomson
from ._core.tilted_history import VolterraHistory


def _real(value, label):
    if np.iscomplexobj(value):
        raise ValueError(f'{label} must use real P8 storage, not a complex array')
    return np.asarray(value, dtype=float)


def _parameters(dt_s, rest_rate_s, panels):
    dt_s, rest_rate_s = float(dt_s), float(rest_rate_s)
    if not np.isfinite(dt_s) or dt_s < 0:
        raise ValueError('dt_s must be finite and nonnegative normal proper seconds')
    if not np.isfinite(rest_rate_s) or rest_rate_s < 0:
        raise ValueError('rest_rate_s must be finite, nonnegative electron-rest opacity')
    if (not isinstance(panels, (int, np.integer)) or isinstance(panels, bool)
            or panels < 1):
        raise ValueError('panels must be a positive integer')
    return dt_s, rest_rate_s, int(panels)


def _physical(op, J):
    J = op._carrier(J)
    scale = max(1.0, float(np.max(np.abs(J))))
    if np.max(np.abs(np.einsum('ni,nij->nj',op.n,J))) > 2e-10*scale:
        raise ValueError('carrier has a non-transverse left index')
    H = (J + J.swapaxes(1,2))/2 + 0.5j*(J-J.swapaxes(1,2))
    if np.min(np.linalg.eigvalsh(H)) < -2e-10*scale:
        raise ValueError('physical coherency is not positive semidefinite')
    if np.any(np.trace(J,axis1=1,axis2=2) < 0):
        raise ValueError('negative intensity is not silently clipped')
    return J


def collision_step(n, weights, carrier, *, dt_s, rest_rate_s, beta, panels):
    dt_s,rest_rate_s,panels = _parameters(dt_s,rest_rate_s,panels)
    op = TiltedThomson(_real(n,'directions'), _real(weights,'weights'), _real(beta,'beta'))
    J = _physical(op,_real(carrier,'carrier')).copy()
    if dt_s == 0 or rest_rate_s == 0:
        return J
    out = VolterraHistory(op,J,rest_rate_s,dt_s,panels).carrier(dt_s)
    # Do not assign/normalize before output validation. Positivity is checked,
    # not guaranteed for an arbitrary collocation step or raw quadrature.
    return _physical(op,out).copy()


def oracle_q_geometry(state):
    """Explicit Python-oracle evaluation of the documented Q frame map.

    This is not an automatic fallback for QState.geometry(), whose native
    backend requirement remains unchanged. It is used only after _oracle().
    """
    M=_real(state.st.M,'momentum map')
    q=_real(state.st.qhat,'comoving directions')
    w=_real(state.st.w_com,'comoving weights')
    if M.shape!=(3,3) or q.ndim!=2 or q.shape[1]!=3 or w.shape!=(len(q),):
        raise ValueError('incompatible Q state geometry arrays')
    if not np.isfinite(M).all() or not np.isfinite(q).all() or not np.isfinite(w).all() or np.any(w<=0):
        raise ValueError('finite geometry and positive raw comoving weights required')
    if np.max(np.abs(np.linalg.norm(q,axis=1)-1))>2e-10:
        raise ValueError('comoving directions must be unit vectors')
    sign,logdet=np.linalg.slogdet(M)
    if sign==0 or not np.isfinite(logdet):
        raise ValueError('nonsingular momentum map required')
    p=q@M.T; mu=np.linalg.norm(p,axis=1)
    if np.any(mu<=0) or not np.isfinite(mu).all():
        raise ValueError('invalid physical photon momenta')
    return p/mu[:,None],np.log(w)+logdet-3*np.log(mu)


def advance_polqstate_normal_time(state, dt_s, rest_rate_s, *, beta,
                                  panels=32, backend=None):
    _oracle(backend, 'q.polstate.collide_normal_time')
    dt_s,rest_rate_s,panels = _parameters(dt_s,rest_rate_s,panels)
    n,log_weights = oracle_q_geometry(state)
    log_weights = np.asarray(log_weights,float)
    if (not np.isfinite(log_weights).all() or
            np.any(log_weights < np.log(np.finfo(float).tiny)) or
            np.any(log_weights > np.log(np.finfo(float).max))):
        raise ValueError('physical angular weights exceed supported float64 range')
    weights = np.exp(log_weights)  # Raw measure. No 4pi renormalization.
    op = TiltedThomson(n,weights,_real(beta,'beta'))
    logs=_real(state.st.lG,'log intensity')
    shape=_real(state.Jhat,'shape')
    if logs.shape!=(len(n),) or np.isnan(logs).any() or np.isposinf(logs).any():
        raise ValueError('log intensity must be finite or exact vacuum -inf')
    _physical(op,shape)
    if np.max(np.abs(np.trace(shape,axis1=1,axis2=2)-1)) > 2e-10:
        raise ValueError('shape trace must be one; no input normalization is performed')
    finite=np.isfinite(logs)
    if not finite.any() or dt_s==0 or rest_rate_s==0:
        return state
    offset=float(np.max(logs[finite]))
    if np.any(logs[finite]-offset < -700):
        raise ValueError('within-step intensity dynamic range exceeds scaled float64 adapter')
    amplitude=np.zeros_like(logs)
    amplitude[finite]=np.exp(logs[finite]-offset)
    J=amplitude[:,None,None]*shape
    out=collision_step(n,weights,J,dt_s=dt_s,rest_rate_s=rest_rate_s,
                       beta=beta,panels=panels)
    intensity=np.trace(out,axis1=1,axis2=2)
    positive=intensity>0
    next_logs=np.full_like(logs,-np.inf)
    next_shape=shape.copy()
    next_logs[positive]=offset+np.log(intensity[positive])
    next_shape[positive]=out[positive]/intensity[positive,None,None]
    if not np.isfinite(next_logs[positive]).all():
        raise ArithmeticError('output log intensity is not representable')
    _physical(op,next_shape)
    # Atomic at the Python API level: all validation is complete before writes.
    state.st.lG=next_logs
    state.Jhat=next_shape
    return state
