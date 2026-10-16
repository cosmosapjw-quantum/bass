"""Bounded source-only diagonal Einstein--Vlasov IVP, in 8 pi G = 1 units.

This is an independently labelled research control.  It has no radiation,
dust, chemistry, REI callback or production checkpoint semantics.
"""
import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

from nonlrs_fd96 import B, FD96Diagonal


def field(source, x, y):
    u = np.asarray(y[:2])
    s = B @ np.asarray(y[2:4])
    m = source.moments(x, u)
    sigma2 = float(s @ s / 2.)
    H = math.sqrt((m.rho + sigma2) / 3.)
    return m, s, sigma2, H


def rhs(source, x, y):
    m, s, _, H = field(source, x, y)
    pi = np.diag(m.pi)
    return np.array([s[0]/H, s[1]/H, -3*s[0]+pi[0]/H,
                     -3*s[1]+pi[1]/H, 1./H])


def run(source=None, n=17):
    source = source or FD96Diagonal(3., .3, triaxial_C=.2)
    y0 = np.array([.02, -.01, .004, -.002, 0.])
    sol = solve_ivp(lambda x, y: rhs(source, x, y), (0., .05), y0,
                    method="DOP853", rtol=2e-11, atol=2e-13,
                    t_eval=np.linspace(0., .05, n), dense_output=True)
    if not sol.success:
        raise ArithmeticError(sol.message)
    rows = []
    for x, y in zip(sol.t[1:-1], sol.y.T[1:-1]):
        m, s, sigma2, H = field(source, x, y)
        Hx = (-.5*(m.rho+m.pbar)-sigma2)/H
        h=5e-6
        Hplus=field(source,x+h,sol.sol(x+h))[3]
        Hminus=field(source,x-h,sol.sol(x-h))[3]
        Hx_fd=(Hplus-Hminus)/(2*h)
        drho=(field(source,x+h,sol.sol(x+h))[0].rho-
              field(source,x-h,sol.sol(x-h))[0].rho)/(2*h)
        work=-3*(m.rho+m.pbar)-float(s@np.diag(m.pi))/H
        rows.append(dict(x=float(x),rho=m.rho,H=H,
                         beta=(B@y[:2]).tolist(),signed_shear_over_H=(s/H).tolist(),
                         Sigma=math.sqrt(sigma2)/H,
                         hamiltonian_raw=3*H*H-m.rho-sigma2,
                         hamiltonian_denominator=3*H*H,
                         raychaudhuri_raw=Hx_fd-Hx,
                         raychaudhuri_denominator=abs(Hx),
                         energy_work_raw=drho-work,
                         energy_work_denominator=abs(work),
                         min_hessian_eigen=float(np.linalg.eigvalsh(m.hessian2)[0]),
                         offdiagonal_over_rho=m.offdiagonal_max/m.rho))
    return dict(schema="bass.fd96.nonlrs.source_only_ivp.v1",source="FD96 radial original; explicit reflection-even triaxial C=.2 extension",solver="DOP853",nfev=sol.nfev,success=sol.success,rows=rows,
                max_hamiltonian_normalized=max(abs(z['hamiltonian_raw'])/z['hamiltonian_denominator'] for z in rows),
                max_raychaudhuri_normalized=max(abs(z['raychaudhuri_raw'])/z['raychaudhuri_denominator'] for z in rows),
                max_energy_work_normalized=max(abs(z['energy_work_raw'])/z['energy_work_denominator'] for z in rows))


if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);o=p.parse_args().out
    if o.exists():raise FileExistsError("CREATE_ONLY_NONLRS_IVP")
    r=run();o.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps({k:v for k,v in r.items() if k.startswith("max_") or k in ("nfev","success")},indent=2))
