#!/usr/bin/env python3
"""Independent complete m-block rotation oracle on a constrained nondiagonal type VIII input."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np
from scipy.special import sph_harm_y
from scipy.spatial.transform import Rotation

from run_atlas import CHANNELS, digest, products_and_checks, read_tsv


def packed(a):
    return a[(0,1,2,0,0,1),(0,1,2,1,2,2)]


def save_lie(path,s,n):
    with path.open("x") as stream:
        for label,values in (("shear",packed(s)),("n",packed(n)),("a",[0.,0.,0.])):
            stream.write(label+" "+" ".join(format(x,".17g") for x in values)+"\n")


def required_host_velocity(s,n,dust_fraction):
    # Gauss with A=0, code energy variables normalized by 3H_initial^2.
    curvature=(-np.trace(n@n)+np.trace(n)**2/2)
    omega=1-np.sum(s*s)/6+curvature/6
    ns=n@s
    eps=np.array([ns[1,2]-ns[2,1],ns[2,0]-ns[0,2],ns[0,1]-ns[1,0]])
    return omega,eps/(3*omega*dust_fraction)


def harmonic_rotation(r,lmax):
    # Y_lm(R^{-1} n) acts on scalar E and pseudoscalar B identically under SO(3).
    # This Ylm quadrature does not call the solver's spin transform or Wigner recursion.
    mu,w=np.polynomial.legendre.leggauss(18)
    az=2*np.pi*np.arange(44)/44.
    mu,az=np.broadcast_arrays(mu[:,None],az[None,:])
    xyz=np.stack((np.sqrt(1-mu**2)*np.cos(az),np.sqrt(1-mu**2)*np.sin(az),mu),axis=-1).reshape(-1,3)
    weights=np.broadcast_to(w[:,None]*2*np.pi/44,mu.shape).ravel()
    angles=lambda nd: (np.arccos(np.clip(nd[:,2],-1.,1.)),np.arctan2(nd[:,1],nd[:,0]))
    theta,phi=angles(xyz)
    theta_back,phi_back=angles(xyz@r)
    blocks=[]
    for l in range(lmax+1):
        m=np.arange(-l,l+1)[:,None]
        y=sph_harm_y(l,m,theta[None,:],phi[None,:])
        yrot=sph_harm_y(l,m,theta_back[None,:],phi_back[None,:])
        blocks.append((y.conj()*weights)@yrot.T)
    return blocks


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--binary",type=Path,required=True)
    ap.add_argument("--raw",type=Path,required=True)
    opt=ap.parse_args()
    out=opt.raw.resolve();out.mkdir(parents=True,exist_ok=False)
    exe=out/"homogeneous_sky";shutil.copy2(opt.binary.resolve(strict=True),exe)
    r=Rotation.from_euler("ZYX",[0.63,-0.42,0.28]).as_matrix()
    n0=Rotation.from_euler("XZ",[0.24,-0.33]).as_matrix()
    n=n0@np.diag([-.35,.53,.72])@n0.T
    s=np.array([[.17,.042,-.028],[.042,-.13,.034],[-.028,.034,-.04]])
    obs=np.array([.13,-.07,.04]);f=.28
    d=harmonic_rotation(r,4)
    unitary=max(np.max(abs(mat.conj().T@mat-np.eye(len(mat)))) for mat in d)
    if unitary>2e-13: raise ValueError(f"bad independent rotation block {unitary}")
    cases={}; comparisons={}
    for label,nu,nphi in (("base",10,24),("fine",20,48)):
        skies=[]; cls=[];initial_host_errors=[]
        for name,rot in (("reference",np.eye(3)),("rotated",r)):
            sr,nr=rot@s@rot.T,rot@n@rot.T
            ic=out/f"{label}_{name}.lie";save_lie(ic,sr,nr)
            folder=out/f"{label}_{name}"
            argv=[str(exe),"--expansion-equation","raychaudhuri","--out",str(folder),"--lie-ic",str(ic),"--feedback","recoil","--dust-fraction",str(f),
                  "--tau",".22","--duration",".35","--steps","36","--nmu",str(nu),"--nphi",str(nphi),"--lmax","4",
                  "--observer-beta",",".join(format(z,".17g") for z in rot@obs)]
            subprocess.run(argv,check=True)
            keys,harm,checks,cl=products_and_checks(folder)
            rows=read_tsv(folder/"diagnostics.tsv")
            omega,expected=required_host_velocity(sr,nr,f)
            measured=np.array([rows[0]["host_beta_"+x] for x in "xyz"])
            err=float(np.max(abs(measured-expected)))
            if np.linalg.norm(expected)<.01 or err>2e-13:raise ValueError("initial Codazzi bulk failed")
            skies.append(harm);cls.append(cl);initial_host_errors.append(err)
            cases[folder.name]={"argv":argv,"ic_sha256":digest(ic),"files_sha256":{p.name:digest(p) for p in sorted(folder.iterdir())},
                "omega_total_initial":omega,"host_beta_initial":measured.tolist(),"codazzi_predicted_beta_initial":expected.tolist(),
                "initial_codazzi_norm":np.linalg.norm([rows[0]["codazzi_"+x] for x in "xyz"]),
                "endpoint_codazzi_norm":np.linalg.norm([rows[-1]["codazzi_"+x] for x in "xyz"]),
                "endpoint_gauss":rows[-1]["gauss"],"harmonic_checks":checks}
        reference,rotation=skies
        predicted=np.concatenate([d[l]@reference[l*l:(l+1)**2] for l in range(5)],axis=0)
        cl_abs=np.max(abs(cls[1]-cls[0]),axis=0)
        cl_scaled=cl_abs/np.max(abs(cls[0]),axis=0)
        alm_rel=np.linalg.norm(rotation-predicted,axis=0)/np.linalg.norm(reference,axis=0)
        comparisons[label]={"rotation_max_alm_abs_TEB":np.max(abs(rotation-predicted),axis=0).tolist(),
            "rotation_alm_relative_l2_TEB":alm_rel.tolist(),"rotation_cl_max_abs":dict(zip(CHANNELS,cl_abs.tolist())),
            "rotation_cl_relative_max":dict(zip(CHANNELS,cl_scaled.tolist())),
            "unrotated_comparison_relative_TEB":(np.linalg.norm(rotation-reference,axis=0)/np.linalg.norm(reference,axis=0)).tolist()}
    # The floor covers aliasing from boosted spin maps on the finite sky quadrature.
    if max(comparisons["fine"]["rotation_alm_relative_l2_TEB"])>1e-5 or max(comparisons["fine"]["rotation_cl_relative_max"].values())>1e-5:
        raise ValueError(f"fine-grid rotation failed: {comparisons['fine']}")
    receipt={"schema":"bass.r109.lie_so3_holdout.v1","solver_sha256":digest(exe),"expansion_equation":"raychaudhuri","script_sha256":digest(Path(__file__)),
             "file_format":"Hubble-normalized symmetric packing 11,22,33,12,13,23",
             "geometry":"type VIII; tracefree Sigma not aligned with rotated diag(-.35,.53,.72) spatial N; A=0",
             "transform":"proper rotation applied to both tensors and observer; nonzero host flow fixed by independent Codazzi prediction",
             "independent_oracle":"scalar scipy.special.sph_harm_y on separate 18x44 GL/phi grid projects Y_lm(R^-1 n); all m of T,E,B at all ell=0..4",
             "rotation_matrix":r.tolist(),"det_R":np.linalg.det(r),"rotation_block_unitarity_max_abs":unitary,
             "comparison_limit_fine":1e-5,"cases":cases,"comparisons":comparisons}
    (out/"LIE_ROTATIONS.json").write_text(json.dumps(receipt,indent=2,allow_nan=False)+"\n")
    print(json.dumps(comparisons))


if __name__=="__main__":
    main()
