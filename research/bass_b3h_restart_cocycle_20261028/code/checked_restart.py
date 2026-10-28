"""Explicit fixed-grid admission and exact-rational conditional reward bounds.

This is a companion execution boundary, not an adaptive solver or a physical
uncertainty certificate. It does not alter the historical generic JSON codec.
"""
from __future__ import annotations
import json
import math
from fractions import Fraction
from typing import Any


def load_for_execution(text: str, identity: dict[str, Any], expected_dt: float,
                       state_size: int) -> dict[str, Any]:
    """Decode the existing packet and bind it to the caller's global RK4 grid.

    Time is exactly the represented scheduler expression step * dt. No tolerance
    is introduced. The caller must retain the same state/reward layout and RHS.
    This does not validate a physical source or authenticate a packet.
    """
    if (isinstance(expected_dt, bool) or not math.isfinite(expected_dt)
            or expected_dt <= 0 or type(state_size) is not int or state_size < 1):
        raise ValueError('finite positive step and positive state size required')
    value = json.loads(text)
    keys = {'identity','step','t','dt','y','attempted_work','pending'}
    if (not isinstance(value, dict) or set(value) != keys
            or value['identity'] != identity or value['pending'] is not False):
        raise ValueError('complete same-identity closed-cut packet required')
    if any(type(value[k]) is not int or value[k] < 0
           for k in ('step','attempted_work')):
        raise ValueError('nonnegative integer step and work required')
    try:
        y = [float.fromhex(x) for x in value['y']]
        t = float.fromhex(value['t'])
        dt = float.fromhex(value['dt'])
        scheduled_t = value['step'] * dt
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError('invalid hexadecimal state or global schedule') from exc
    if (len(y) != state_size or not all(math.isfinite(x) for x in y)
            or not all(math.isfinite(x) for x in (t,dt,scheduled_t))
            or dt != float(expected_dt) or t != scheduled_t):
        raise ValueError('time, step, dt or state/reward layout mismatch')
    return dict(value, t=t, dt=dt, y=y)


def reward_upper(duration, gamma, initial_state_error, initial_reward_error,
                 state_forcing_bound, reward_row_bound, direct_reward_bound):
    """Exact conservative upper bound for the *supplied* nonnegative rationals.

    Strings, integers and Fraction values are accepted; floats are rejected so
    callers explicitly choose decimal versus binary-rational source semantics.
    The exact exponential kernel is bounded by positive rational envelopes.
    """
    args = (duration,gamma,initial_state_error,initial_reward_error,
            state_forcing_bound,reward_row_bound,direct_reward_bound)
    if any(isinstance(x,(float,bool)) for x in args):
        raise ValueError('use explicit rational/decimal inputs, not floats/bools')
    try:
        d,g,ep,ez,rho,ell,zeta = map(Fraction,args)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError('finite rational inputs required') from exc
    if min(d,g,ep,ez,rho,ell,zeta) < 0:
        raise ValueError('nonnegative conditional bounds required')
    phi = d if g == 0 else min(d,1/g)
    psi = d*d/2 if g == 0 else min(d*d/2,d/g)
    return ez + ell*ep*phi + ell*rho*psi + zeta*d
