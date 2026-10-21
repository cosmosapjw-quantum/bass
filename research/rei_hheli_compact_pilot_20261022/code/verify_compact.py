#!/usr/bin/env python3
"""Prescribed finite-coordinate and guard verification; never integrates an IVP."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import numpy as np
from compact_system import (CompactSystem,P,R,lift,restrict,require_eligible,ROOT)


def main():
    rng=np.random.default_rng(20261022)
    config=dict(Sigma_F=.6,matter_A=1.5561956189864556,
                radiation_A=-.4275708327913344,backend='prepared',opacity=True)
    system=CompactSystem(config); owner=system.owner
    states=[]
    states.append(('initial',0.,system.y0.copy()))
    for label,x,b,shear,chem in (
        ('moderate_synthetic_positive',.8,.035,.12,([.6,.4],[.4,.35,.25],[.1,.3,.4,.2])),
        ('high_anisotropy_synthetic_positive',1.4,.13,.32,([.08,.92],[.06,.22,.72],[.02,.08,.25,.65]))):
        y=system.original_initial62.copy();y[0]=x;y[1]=b;y[2]=shear
        for indices,values in (([1,2],chem[0]),([3,4],chem[0]),([7,8,9],chem[1]),
                               ([10,11,12],chem[1]),([13,14,15,16],chem[2]),([17,18,19,20],chem[2])):
            y[40+np.array(indices)]=values
        # Even moments are retained as physical initial positive towers.
        states.append((label,x,restrict(y)))
    rp=float(np.max(abs(R@P-np.eye(33)))); rows=[]
    for label,x,v in states:
        y=lift(v);fo=owner.rhs(x,y);fc=system.rhs(x,v)
        rhs_error=float(np.max(abs(lift(fc)-fo)/np.maximum(1,abs(fo))))
        jac=system.jac(x,v); projected=R@owner.jac(x,y)@P
        matrix_error=float(np.max(abs(jac-projected)/np.maximum(1,abs(projected))))
        dirs=[]
        for _ in range(4):
            d=rng.normal(size=33);d/=np.linalg.norm(d);step=1e-6
            fd=(system.rhs(x,v+step*d)-system.rhs(x,v-step*d))/(2*step)
            analytic=jac@d
            dirs.append(float(np.max(abs(fd-analytic)/np.maximum(1,np.maximum(abs(fd),abs(analytic))))))
        scaled=y[40:61];Y=scaled*owner.scale
        # Independently aggregate inventory-weighted element charge fractions.
        baryon=0.;electron=0.
        for groups,rep in ((('H1','D'),[1,2]),(('He3','He4'),[10,11,12]),(('Li6','Li7'),[17,18,19,20])):
            f=scaled[rep]
            for name in groups:
                ids=owner.atomic.isotope_groups[name]; inventory=owner.atomic.isotope_inventory[name]
                baryon+=inventory*owner.atomic.A[ids[0]]*float(np.sum(f))
                electron+=inventory*float(np.arange(len(rep))@f)
        baryon_error=abs(float(owner.atomic.A@Y)-baryon)
        electron_error=abs(float(owner.atomic.q@Y)-electron)
        isotope_derivative=max(abs(float(np.sum(fo[40+np.array(ids)]))) for name,ids in owner.atomic.isotope_groups.items())
        angular=owner.diagnostics(x,y)
        rows.append(dict(state=label,x=x,lifted_rhs_scaled_error=rhs_error,
                         analytic_projection_scaled_error=matrix_error,
                         jacobian_fd_directional_scaled_errors=dirs,
                         baryon_reconstruction_error=baryon_error,
                         electron_reconstruction_error=electron_error,
                         scaled_isotope_derivative_sum=isotope_derivative,
                         min_scaled_population=float(np.min(scaled)),
                         min_angular_weight=min(angular[k] for k in ('min_photon_angular_weight','min_neutrino_angular_weight','min_photon_number_angular_weight','min_neutrino_number_angular_weight'))))
    guards={}
    for name,index,increment in (('nonzero_tritium',45,1e-6),('unequal_isotope_fraction',43,1e-6),('nonzero_odd_geometry',5,1e-6)):
        y=owner.y0.copy();y[index]+=increment
        try:require_eligible(owner,y)
        except ValueError as error:guards[name]=str(error)
        else:guards[name]='DID_NOT_REJECT'
    passed=(rp==0 and all(r['lifted_rhs_scaled_error']<=2e-12 and
        max(r['jacobian_fd_directional_scaled_errors'])<=2e-6 and
        max(r['baryon_reconstruction_error'],r['electron_reconstruction_error'])<=2e-14
        for r in rows) and all(v.startswith('NEED_FULL62:') for v in guards.values()))
    files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
           for folder in ('code','data','provenance') for p in sorted((ROOT/folder).rglob('*'))
           if p.is_file() and '__pycache__' not in p.parts}
    result=dict(status='PASS' if passed else 'FAIL',stage='FINITE_ONLY_NO_IVP',RP_max_abs=rp,
                eligibility=system.eligibility,states=rows,guards=guards,
                directional_scale='max(1, abs(centered_difference), abs(analytic_direction)); step=1e-6; unit-L2 deterministic directions',
                rhs_scale='each entry max(1, abs(full62_rhs))',
                environment=dict(python=sys.version.split()[0],numpy=np.__version__,platform=platform.platform(),
                    requested_executor='gpt-6.1-sol',observed_runtime_model='not exposed',
                    threads={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')}),files_sha256=files)
    print(json.dumps(result,indent=2,allow_nan=False))
    (ROOT/'evidence/COMPACT_FINITE_VERIFICATION.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
