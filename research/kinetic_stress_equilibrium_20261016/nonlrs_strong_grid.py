"""Create-only angular convergence counterexample near the allowed beta chart edge."""
import json
from pathlib import Path

import numpy as np

from nonlrs_fd96 import FD96Diagonal


def run():
    x=0.;beta2=(1.,-.3);mass=3.;A=.5;radial=96
    models={n:FD96Diagonal(mass,A,radial=radial,polar=n,azimuth=n).moments(x,beta2)
            for n in (16,24,32,48,64,96)}
    ref=models[96]
    rows=[]
    for n,m in models.items():
        rows.append(dict(polar=n,azimuth=n,
            rho_relative=abs(m.rho-ref.rho)/ref.rho,
            pressure_max_relative=float(np.max(abs(m.pressure-ref.pressure))/ref.rho),
            pi_max_relative=float(np.max(abs(m.pi-ref.pi))/ref.rho),
            hessian2_max_relative=float(np.max(abs(m.hessian2-ref.hessian2))/ref.rho),
            offdiagonal_over_rho=m.offdiagonal_max/m.rho,
            hessian2_min_eigen=float(np.linalg.eigvalsh(m.hessian2)[0])))
    return dict(schema="bass.fd96.nonlrs.strong_chart_grid.v1",
        source="original FD96 radial and PR164 axisymmetric W, no triaxial extension",
        source_commit="fe48e9a90a14bc6bad09941763a15aad34505e2c",
        original_freestream_blob="8467932c3281f9d426712b3a582f2aae3a484692",
        state=dict(mass=mass,A=A,x=x,beta=[1.,-.3,-.7],radial=radial),
        angular_reference=(96,96),rows=rows,
        claim="GL96 discrete reference only; full-chart continuum quadrature error not certified")


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);out=p.parse_args().out
    if out.exists():raise FileExistsError("CREATE_ONLY_STRONG_GRID")
    result=run();out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['rows'],indent=2))
