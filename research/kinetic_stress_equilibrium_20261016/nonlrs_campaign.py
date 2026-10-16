"""Create-only actual FD96 tensor, LRS parity and independent grid controls."""
import hashlib
import json
from pathlib import Path

import numpy as np

from kinetic_equilibrium import FD96Equilibrium
from nonlrs_fd96 import FD96Diagonal


def git_blob(path):
    raw=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()


def tensor_error(a,b):
    return dict(rho_relative=abs(a.rho-b.rho)/b.rho,
                pressure_max_relative=float(np.max(abs(a.pressure-b.pressure))/b.rho),
                hessian_max_relative=float(np.max(abs(a.hessian2-b.hessian2))/b.rho),
                pi_max_relative=float(np.max(abs(a.pi-b.pi))/b.rho))


def main(out):
    if out.exists():raise FileExistsError("CREATE_ONLY_NONLRS_CAMPAIGN")
    source=Path(__file__).resolve().parents[2]/"bianchi/matter/freestream.py"
    blob=git_blob(source)
    if blob!="8467932c3281f9d426712b3a582f2aae3a484692":
        raise ArithmeticError("ORIGINAL_FREESTREAM_BLOB_MISMATCH")
    records=[]
    for mass in (3.,30.):
        for A in (-1.,0.,.5,2.):
            model=FD96Diagonal(mass,A,polar=32,azimuth=32)
            lrs=FD96Equilibrium(mass,angular=32)
            for x,b in ((0.,0.),(.7,-.08),(1.2,.13)):
                m=model.moments(x,(-b,-b));p=lrs.stress(x,b,A)
                delta=m.pressure[2,2]-.5*(m.pressure[0,0]+m.pressure[1,1])
                records.append(dict(mass=mass,A=A,x=x,b=b,
                    rho_diff=m.rho-p.rho,pbar_diff=m.pbar-p.pbar,
                    delta_diff=delta-p.delta,
                    p_perp_diff=m.pressure[0,0]-p.p_perp,
                    p_parallel_diff=m.pressure[2,2]-p.p_parallel,
                    hessian_b_diff=np.array([-1.,-1.,2.])@m.hessian3@np.array([-1.,-1.,2.])+2*p.chi_b,
                    offdiagonal_max=m.offdiagonal_max))
    x=.7;u=(.05,-.02)
    fine=FD96Diagonal(3.,.5,radial=160,polar=48,azimuth=48).moments(x,u)
    radial=[]; angular=[]
    for nr in (64,96,128,160):
        m=FD96Diagonal(3.,.5,radial=nr,polar=48,azimuth=48).moments(x,u)
        radial.append(dict(radial=nr,**tensor_error(m,fine)))
    for n in (16,24,32,48):
        m=FD96Diagonal(3.,.5,radial=160,polar=n,azimuth=n).moments(x,u)
        angular.append(dict(polar=n,azimuth=n,**tensor_error(m,fine)))
    roots=[]
    for C in (0.,.2):
        for n in (16,24,32,48):
            f=FD96Diagonal(3.,.3,radial=96,polar=n,azimuth=n,triaxial_C=C)
            u0,m,res=f.neutral_root(.7)
            roots.append(dict(C=C,angular=n,beta2=u0.tolist(),
                              pressure_tracefree_gradient=m.energy_gradient2.tolist(),
                              residual_per_rho=res/m.rho,
                              hessian_min_eigen=float(np.linalg.eigvalsh(m.hessian2)[0]),
                              weight_min=m.quadrature_weight_min,
                              offdiagonal_over_rho=m.offdiagonal_max/m.rho))
    result=dict(schema="bass.fd96.nonlrs.source_grid.v1",producer_blob=blob,
                source="original freestream FD96 radial and full sphere; C=0 PR164 P2 source, C=.2 explicit positive reflection-even triaxial extension",
                units="rho, P, pi, Hessian in reference rho units; x,b,beta dimensionless",
                lrs_records=records,lrs_max_abs={k:max(abs(t[k]) for t in records) for k in
                    ("rho_diff","pbar_diff","delta_diff","p_perp_diff","p_parallel_diff","hessian_b_diff","offdiagonal_max")},
                radial_convergence=radial,angular_convergence=angular,
                neutral_roots=roots,fine_reference_resolution=(160,48,48),
                resolution_claim="discrete 160x48x48 reference only; not a continuum quadrature certificate")
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"lrs_max_abs":result["lrs_max_abs"],"radial":radial,"angular":angular,
                      "triaxial_root":roots[-1]},indent=2))


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    main(p.parse_args().out)
