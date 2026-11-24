"""Compare every native weighted/Haar row to a two-pass independent NumPy calculation."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

import numpy as np


def read_modes(path):
    with path.open() as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    keys = [(int(r["ell"]),int(r["m"])) for r in rows]
    values = [[complex(float(r[f"{x}_re"]),float(r[f"{x}_im"])) for x in "TEB"] for r in rows]
    return keys,np.asarray(values)


def matrix(rows, keys, field):
    idx = {k:i for i,k in enumerate(keys)}
    out = np.full((3*len(keys),3*len(keys)),np.nan+1j*np.nan)
    for r in rows:
        i = idx[int(r["ell"]),int(r["m"])]*3+"TEB".index(r["X"])
        j = idx[int(r["ell_prime"]),int(r["m_prime"])]*3+"TEB".index(r["Y"])
        if np.isfinite(out[i,j]):
            raise ValueError("duplicate covariance row")
        out[i,j] = complex(float(r[f"{field}_re"]),float(r[f"{field}_im"]))
    if not np.isfinite(out).all():
        raise ValueError("missing covariance entry")
    return out


def read_law(binary, args):
    raw = subprocess.check_output([binary,*args,"--all"])
    return list(csv.DictReader(io.StringIO(raw.decode()),delimiter="\t")), hashlib.sha256(raw).hexdigest()


def rotated_haar_oracle(keys, initial):
    """Direct SO(3) quadrature over independent healpy active rotations."""
    import healpy as hp

    L=max(l for l,m in keys)
    size=len(keys)*3
    alm=np.zeros((3,hp.Alm.getsize(L)),complex)
    for i,(l,m) in enumerate(keys):
        if m>=0:
            alm[:,hp.Alm.getidx(L,l,m)]=initial[i]
    take=[hp.Alm.getidx(L,l,abs(m)) for l,m in keys]
    negative=np.array([m<0 for l,m in keys])
    phase=np.array([(-1)**abs(m) for l,m in keys])
    azimuth=2*np.pi*np.arange(2*L+1)/(2*L+1)
    z,weight=np.polynomial.legendre.leggauss(L+1)
    moment=np.zeros((size,size),complex)
    mean=np.zeros(size,complex)
    for ct,w in zip(z,weight):
        mass=w/(2*len(azimuth)**2)
        for a in azimuth:
            for g in azimuth:
                rotated=alm.copy()
                hp.rotate_alm(rotated,psi=a,theta=np.arccos(ct),phi=g)
                field=rotated[:,take].T.copy()
                field[negative]=phase[negative,None]*field[negative].conj()
                field=field.ravel()
                mean+=mass*field
                moment+=mass*np.outer(field,field.conj())
    return moment,moment-np.outer(mean,mean.conj()),len(z)*len(azimuth)**2,hp.__version__


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary",type=Path,required=True)
    parser.add_argument("--member",nargs=3,action="append",required=True,metavar=("NAME","WEIGHT","MODES"))
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--rotate-haar",action="store_true",help="cross-check small L via actual rotated skies")
    args=parser.parse_args()
    keys=None
    paths=[]
    arrays=[]
    law=[]
    native=[]
    for label,weight,name in args.member:
        path=Path(name)
        k,v=read_modes(path)
        if keys is not None and k!=keys:
            raise ValueError("mode ranges differ")
        keys=k
        arrays.append(v)
        paths.append(path)
        native.extend(["--member",weight,str(path)])
        law.append({"label":label, "weight":float(weight), "mode_table_bytes":path.stat().st_size,
                    "mode_table_sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    rows,digest=read_law(args.binary,native)
    weights=np.asarray([i["weight"] for i in law])
    weights/=weights.sum()
    a=np.asarray(arrays).reshape(len(arrays),-1)
    mean=weights@a
    dev=a-mean
    raw=a.T@(weights[:,None]*a.conj())
    centered=dev.T@(weights[:,None]*dev.conj())
    cov=matrix(rows,keys,"cov")
    observed_raw=matrix(rows,keys,"raw")
    meanouter=matrix(rows,keys,"mean_outer")
    closure=matrix(rows,keys,"closure")
    norm=lambda x: float(np.max(np.abs(x)))
    target_scale=max(norm(raw),np.finfo(float).tiny)
    tol=5e-13*target_scale
    if max(norm(observed_raw-raw),norm(cov-centered),norm(closure))>tol:
        raise ValueError("native raw, centered or closure disagrees with two-pass calculation")
    lam=np.linalg.eigvalsh(cov)
    ranktol=1e-12*max(abs(lam))
    signed=[]
    for akey,bkey,x,y in [((2,0),(2,2),"T","T"),((2,0),(2,2),"T","E"),
                          ((2,0),(2,0),"E","E"),((2,2),(3,-1),"E","B")]:
        if akey not in keys or bkey not in keys:
            continue
        i=keys.index(akey)*3+"TEB".index(x)
        j=keys.index(bkey)*3+"TEB".index(y)
        pair=lambda z:[float(z.real),float(z.imag)]
        signed.append({"left":[*akey,x],"right":[*bkey,y],"mean_outer":pair(meanouter[i,j]),
                       "covariance":pair(cov[i,j]),"second_moment":pair(observed_raw[i,j])})
    haar_rows,haar_digest=read_law(args.binary,["--haar",str(paths[0])])
    haar=matrix(haar_rows,keys,"raw")
    oracle=np.zeros_like(haar)
    for l in sorted({k[0] for k in keys}):
        idx=[i for i,k in enumerate(keys) if k[0]==l]
        block=arrays[0][idx].T@arrays[0][idx].conj()/(2*l+1)
        for i in idx:
            oracle[i*3:i*3+3,i*3:i*3+3]=block
    if norm(haar-oracle)>tol:
        raise ValueError("Haar second moment disagrees with harmonic mean spectrum")
    output={"schema":"bass.r109.weighted_sky_law.v1",
            "measure":"finite declared population on deterministic solver outputs; weights normalize to unity",
            "members":law,"probabilities":weights.tolist(),"num_complex_field_modes":len(mean),
            "num_ordered_complex_matrix_entries":len(rows),"weighted_all_output_sha256":digest,
            "max_abs_raw_vs_numpy":norm(observed_raw-raw),"max_abs_cov_vs_numpy":norm(cov-centered),
            "max_abs_raw_minus_cov_minus_meanouter":norm(closure),"max_abs_hermiticity":norm(cov-cov.conj().T),
            "minimum_cov_eigenvalue":float(lam[0]),"maximum_cov_eigenvalue":float(lam[-1]),
            "centered_numerical_rank":int(np.sum(lam>ranktol)), "rank_threshold":float(ranktol),
            "maximum_possible_centered_rank":len(arrays)-1, "selected_entries":signed,
            "haar_first_member_all_output_sha256":haar_digest,
            "haar_max_abs_vs_numpy_schur_average":norm(haar-oracle)}
    if args.rotate_haar:
        rraw,rcov,count,version=rotated_haar_oracle(keys,arrays[0])
        errs=[norm(haar-rraw),norm(matrix(haar_rows,keys,"cov")-rcov)]
        if max(errs)>tol:
            raise ValueError("Haar law disagrees with independent SO(3) angular quadrature")
        output["haar_direct_rotation_quadrature"]={"n_rotations":count,"healpy":version,
            "max_abs_raw_error":errs[0],"max_abs_centered_error":errs[1]}
    args.output.write_text(json.dumps(output,indent=2,allow_nan=False)+"\n")


if __name__=="__main__":
    main()
