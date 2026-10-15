"""Byte-locked BASS FD96 -> Rust source grid, and deterministic kinetic cases.

Outputs contain immutable original kinetic quadrature data, no private AX08 HHe donor.
No automatic REI chemistry activation; consumer validates grid contents and unit contract.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

HERE=Path(__file__).resolve().parent
BASS=HERE.parents[1]
STABLE=BASS/"research/rei_sigma_kinetic_gamma_nu_20261015"
sys.path.insert(0,str(STABLE))
from stable_moments import StableMassiveMoments
from joint_kinetic import verify_original_sources

MASS_CHOICES=(3.,30.,300.)
def sha(path:Path)->str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def source_grid(mass:float,angular:int=32)->tuple[str,StableMassiveMoments]:
    verify_original_sources()
    if mass not in MASS_CHOICES:
        raise ValueError("Only declared representative physical masses are admitted")
    m=StableMassiveMoments(mass,angular_n=angular)
    rows=[f"BASS_FD96_STRESS_V1 {len(m.q)} {len(m.mu)} {mass:.17g} {m.norm:.17g}"]
    rows.extend(f"{q:.17g} {w:.17g}" for q,w in zip(m.q,m.rw))
    rows.extend(f"{mu:.17g} {w:.17g}" for mu,w in zip(m.mu,m.w))
    return "\n".join(rows)+"\n",m

def cases(n_random:int,seed:int=20261015):
    if n_random<0 or n_random>50000:raise ValueError("bounded source case count")
    rng=np.random.default_rng(seed)
    # This prefix is a diagnostic, not a random-only sampling of scientific limits.
    q=[(0.,0.,0.),(.5,0.,0.),(.5,1e-16,0.),(.5,-1e-16,0.),
       (.5,1e-14,0.),(.5,-1e-14,0.),(.5,1e-12,0.),(.5,0.,.5),
       (.5,0.,-.7),(.5,.06,.5),(.8,-.02,-.7),
       (1.4,-.07,1.9),(0.,.07,-.9)]
    for i in range(n_random):
        x=float(rng.uniform(0.,np.log(21./5.)))
        b=float(rng.uniform(-.07,.07))
        A=float(rng.uniform(-.9,1.9))
        q.append((x,b,A))
    return q

def prepare(output:Path,n_random:int=1000):
    if output.exists():raise FileExistsError(output)
    output.mkdir(parents=True)
    result={"schema":"bass.rei.fd96.native_grid.v1","parent":"31c41541eb053545f8638177b8e848d5495b57fd",
            "mass":"m_over_Tref dimensionless","coords":"x=ln(a/aref), b dimensionless, W=1+A P2",
            "source_kind":"original BASS FD96 source-read-only","source_pins":verify_original_sources(),
            "grids":{}}
    c=cases(n_random)
    for mass in MASS_CHOICES:
        text,m=source_grid(mass)
        postfix=int(mass)
        gp=output/f"grid_m{postfix}.txt"
        qp=output/f"cases_m{postfix}.tsv"
        gp.write_text(text)
        qp.write_text("\n".join(f"{x:.17g} {b:.17g} {a:.17g}" for x,b,a in c)+"\n")
        result["grids"][str(postfix)]={"source_sha256":sha(gp),"cases_sha256":sha(qp),
               "cases":len(c),"radial":len(m.q),"angular":len(m.mu),
               "source_norm":m.norm,"initial_mean_v2":m.initial_mean_v2}
    (output/"SOURCE_RECEIPT.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--random",type=int,default=1000)
    args=parser.parse_args()
    print(json.dumps(prepare(args.out,args.random),indent=2))
