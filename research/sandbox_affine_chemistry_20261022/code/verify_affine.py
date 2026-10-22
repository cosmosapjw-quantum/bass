#!/usr/bin/env python3
"""One bounded finite-state verification against the pinned actual H--Li owner."""
import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
import numpy as np

p=argparse.ArgumentParser()
p.add_argument('--baseline',type=Path,default=Path(__file__).resolve().parents[2]/'rei_hheli_compact_pilot_20261022')
p.add_argument('--output',type=Path,required=True)
args=p.parse_args()
sys.path.insert(0,str(args.baseline/'code'))
from compact_system import CompactSystem, lift as lift62
from affine_system import AffineSystem, BLOCKS, KEEP, LIFT, SELECT

t0=time.monotonic()
compact=CompactSystem(dict(Sigma_F=.6,matter_A=1.5561956189864556,
                          radiation_A=-.4275708327913344,backend='prepared',opacity=True))
model=AffineSystem(compact)
rng=np.random.default_rng(20261022)
cases=[('actual_initial',0.,compact.y0.copy())]
for label,x,chem in [('partly_ionized',.8,([.6,.4],[.4,.35,.25],[.1,.3,.4,.2])),
                     ('high_ionization',1.4,([.08,.92],[.06,.22,.72],[.02,.08,.25,.65]))]:
    v=compact.y0.copy();v[1]=.035;v[2]=.12
    for block,f in zip(BLOCKS,chem):v[list(block)]=f
    cases.append((label,x,v))
rows=[]
for label,x,v in cases:
    u=model.restrict(v); full=model.lift(u)
    f=compact.rhs(x,full); fr=model.rhs(x,u)
    jr=model.jac(x,u); j=compact.jac(x,full)
    fd_errors=[]
    for _ in range(4):
        direction=rng.normal(size=30);direction/=np.linalg.norm(direction);h=1e-6
        fd=(model.rhs(x,u+h*direction)-model.rhs(x,u-h*direction))/(2*h)
        actual=jr@direction
        fd_errors.append(float(np.max(abs(fd-actual)/np.maximum(1,np.maximum(abs(fd),abs(actual))))))
    rows.append(dict(label=label,x=x,
        state_reconstruction_max_abs=float(np.max(abs(full-v))),
        rhs_lift_scaled=float(np.max(abs(LIFT@fr-f)/np.maximum(1,abs(f)))),
        jac_projection_scaled=float(np.max(abs(jr-SELECT@j@LIFT)/np.maximum(1,abs(jr)))),
        tangent_invariance_scaled=float(np.max(abs(j@LIFT-LIFT@jr)/np.maximum(1,abs(j@LIFT)))),
        fd_direction_errors=fd_errors,
        element_sums=[float(np.sum(full[list(b)])) for b in BLOCKS],
        all21_population_reconstruction_max_abs=float(np.max(abs(model.full62(u)[40:61]-lift62(v)[40:61])))))
guards={}
for name,fn in [('bad_lift_shape',lambda:model.lift(np.zeros(29))),
                ('bad_restrict_shape',lambda:model.restrict(np.zeros(32)))]:
    try:fn();guards[name]=False
    except ValueError:guards[name]=True
rp=float(np.max(abs(SELECT@LIFT-np.eye(30))))
passed=rp==0 and all(guards.values()) and all(
    r['rhs_lift_scaled']<=2e-12 and r['jac_projection_scaled']<=2e-12 and
    r['tangent_invariance_scaled']<=2e-12 and max(r['fd_direction_errors'])<=2e-6 and
    r['all21_population_reconstruction_max_abs']<=2e-14 for r in rows)
receipt=dict(status='PASS_SCOPED' if passed else 'FAIL',scope='actual finite H-Li RHS/Jacobian, no IVP',
    baseline_commit='574c3af93810122af0a7977e00e34195e5251a09',RP_error=rp,
    totals=model.totals.tolist(),rows=rows,guards=guards,ivp_count=0,
    elapsed_seconds=time.monotonic()-t0,python=platform.python_version(),numpy=np.__version__,
    source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')},
    norm_contract='Full33 lifted error and full33 scales required for original adaptive WRMS; not wired into solver')
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
print(json.dumps(receipt,indent=2));sys.exit(0 if passed else 1)
