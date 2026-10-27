"""Closed-cut affine rewards and fixed-grid checkpoints, not a full B4 restart."""
from __future__ import annotations
import json
import math
from typing import Any
import numpy as np


def compose(first: tuple, second: tuple) -> tuple:
    """Chronological first-then-second affine population/reward map."""
    p, q, r, s = (np.asarray(x, dtype=float) for x in first)
    pp, qq, rr, ss = (np.asarray(x, dtype=float) for x in second)
    if p.ndim != 2 or p.shape[0] != p.shape[1]:
        raise ValueError('square state map required')
    n = p.shape[0]
    if (pp.shape != p.shape or q.shape != (n,) or qq.shape != (n,)
            or r.ndim != 2 or r.shape[1] != n or rr.shape != r.shape
            or s.shape != (r.shape[0],) or ss.shape != s.shape):
        raise ValueError('incompatible state/reward dimensions')
    if not all(np.isfinite(x).all() for x in (p,q,r,s,pp,qq,rr,ss)):
        raise ValueError('finite affine maps required')
    return pp@p, pp@q+qq, r+rr@p, s+rr@q+ss


def rebase(local: np.ndarray, theta_c: float, beta: float,
           k: float, u_c: float) -> np.ndarray:
    """Binomial clock-origin transform; values must already share V0."""
    local = np.asarray(local, dtype=float)
    if local.ndim < 1 or len(local) == 0 or not np.isfinite(local).all():
        raise ValueError('finite moment axis required')
    if not all(math.isfinite(x) for x in (theta_c,beta,k,u_c)):
        raise ValueError('finite rebase parameters required')
    return math.exp(k*u_c)*np.array([
        sum(math.comb(j,r)*theta_c**(j-r)*beta**r*local[r]
            for r in range(j+1)) for j in range(len(local))])


def _validate(s: dict[str, Any]) -> None:
    required={'identity','step','t','dt','y','attempted_work','pending'}
    if set(s) != required or s['pending'] is not False:
        raise ValueError('complete closed-cut packet required')
    if (not isinstance(s['step'],int) or isinstance(s['step'],bool) or s['step']<0
            or not isinstance(s['attempted_work'],int) or s['attempted_work']<0):
        raise ValueError('nonnegative integer step/work required')
    if (not isinstance(s['identity'],dict) or not s['identity'] or not s['y']
            or not math.isfinite(s['t']) or not math.isfinite(s['dt'])
            or s['dt']<=0 or not all(math.isfinite(x) for x in s['y'])):
        raise ValueError('invalid identity/time/state')


def dump_checkpoint(state: dict[str, Any]) -> str:
    """Lossless binary64 serialization of hidden state AND accumulated rewards."""
    _validate(state)
    out=dict(state)
    out['y']=[float(x).hex() for x in state['y']]
    out['t']=float(state['t']).hex();out['dt']=float(state['dt']).hex()
    return json.dumps(out,sort_keys=True,separators=(',',':'),allow_nan=False)


def load_checkpoint(text: str, identity: dict) -> dict[str, Any]:
    s=json.loads(text)
    if not isinstance(s,dict) or s.get('identity') != identity:
        raise ValueError('source/model/frame/clock/volume identity mismatch')
    try:
        s['y']=[float.fromhex(x) for x in s['y']]
        s['t']=float.fromhex(s['t']);s['dt']=float.fromhex(s['dt'])
    except (KeyError,TypeError,ValueError) as exc:
        raise ValueError('invalid hexadecimal checkpoint') from exc
    _validate(s)
    return s


def rk4(rhs, state: np.ndarray, start: int, stop: int, dt: float) -> np.ndarray:
    """Fixed global schedule only. The caller owns the cumulative work count."""
    if not (0<=start<=stop and dt>0 and math.isfinite(dt)):
        raise ValueError('invalid forward global grid')
    y=np.array(state,dtype=float,copy=True)
    for i in range(start,stop):
        t=i*dt
        k1=rhs(t,y);k2=rhs(t+dt/2,y+dt*k1/2)
        k3=rhs(t+dt/2,y+dt*k2/2);k4=rhs(t+dt,y+dt*k3)
        y=y+dt*(k1+2*k2+2*k3+k4)/6
    return y
