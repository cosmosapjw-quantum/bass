"""Proposed read-only rei_microphysics::BackgroundPoint-like LRS field table.

Not native Rust compiled and not a REI chemistry driver replacement. Distinguishes
signed_s_over_H (native geometry) from public nonnegative Sigma.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from kinetic_tangent import EinsteinTangent,AREF,AEND,H0,OMEGA_M,OMEGA_R,OMEGA_L,XMAX

HEADER=('case','x','a','zbar','proper_elapsed_s','b','H_mean_per_s',
        's_per_s','Sigma','signed_s_over_H','H_cold_FLRW_reference_per_s',
        'massive_rho_norm','massive_pbar_norm','massive_deltaP_norm',
        'massive_partial_b_deltaP_norm','massive_deltaP_A_norm',
        'dH_db_per_s','db_dA','d(s_per_s)_dA',
        'dH_dln_a_per_s','H_perp_per_s','H_parallel_per_s')

def scenarios():
    q=.01
    Sigma_ref=math.sqrt(3)*q/math.hypot(1,q)
    return [('COLD_FLRW',dict(fraction=0.,mass=30.,A=0.,Sigma_ref=0.,orientation=1)),
       ('WARM_ISOTROPIC',dict(fraction=.1,mass=30.,A=0.,Sigma_ref=0.,orientation=1)),
       ('MASSIVE_A_PLUS',dict(fraction=.1,mass=30.,A=.5,Sigma_ref=0.,orientation=1)),
       ('MASSIVE_A_MINUS',dict(fraction=.1,mass=30.,A=-.5,Sigma_ref=0.,orientation=1)),
       ('MASS3_A_PLUS',dict(fraction=.1,mass=3.,A=.5,Sigma_ref=0.,orientation=1)),
       ('MASS300_A_PLUS',dict(fraction=.1,mass=300.,A=.5,Sigma_ref=0.,orientation=1)),
       ('SIGNED_PLUS',dict(fraction=.1,mass=30.,A=.5,Sigma_ref=Sigma_ref,orientation=1)),
       ('SIGNED_MINUS',dict(fraction=.1,mass=30.,A=.5,Sigma_ref=Sigma_ref,orientation=-1))]

def generate(out:Path,n:int=121):
    if not isinstance(n,int) or n<11 or n>2001:raise ValueError('bounded snapshot count')
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    results=[]
    table=out/'PROPOSED_REI_BACKGROUND.csv'
    with table.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=HEADER,lineterminator='\n')
        writer.writeheader()
        for name,params in scenarios():
            m=EinsteinTangent(**params)
            sol=m.solution(n=n,rtol=2e-11,atol=5e-13)
            maximal_Raychaudhuri=0.
            for j,x in enumerate(sol.t):
                x=float(x);b,v,t,u,w,z=(float(z) for z in sol.y[:,j])
                a=AREF*math.exp(x)
                M,H,dust,rad=m.field(x,b,v)
                s=m.href*v
                hflrw=H0*math.sqrt(OMEGA_M/a**3+OMEGA_R/a**4+OMEGA_L)
                dHdb=-m.g*M.delta/H
                Hp=m.raychaudhuri(x,sol.y[:,j])
                writer.writerow(dict(case=name,x=x,a=a,zbar=1/a-1,
                   proper_elapsed_s=t/m.href,b=b,H_mean_per_s=H,
                   s_per_s=s,Sigma=math.sqrt(3)*abs(s)/H,
                   signed_s_over_H=s/H,H_cold_FLRW_reference_per_s=hflrw,
                   massive_rho_norm=m.cm*M.rho,massive_pbar_norm=m.cm*M.pbar,
                   massive_deltaP_norm=m.cm*M.delta,
                   massive_partial_b_deltaP_norm=m.cm*M.chi,
                   massive_deltaP_A_norm=m.cm*M.delta_A,
                   dH_db_per_s=dHdb,db_dA=u,dH_dln_a_per_s=Hp,
                   **{'d(s_per_s)_dA':m.href*w},
                   H_perp_per_s=H-s,H_parallel_per_s=H+2*s))
                # An independent finite-difference check against Raychaudhuri,
                # not a self-subtracted Hamiltonian residual.
                if 0<j<n-1 and j%10==0:
                    h=1e-5;yp=sol.y[:,j]+h*m.derivative(x,sol.y[:,j]);ym=sol.y[:,j]-h*m.derivative(x,sol.y[:,j])
                    fp=m.field(x+h,float(yp[0]),float(yp[1]))[1]
                    fm=m.field(x-h,float(ym[0]),float(ym[1]))[1]
                    maximal_Raychaudhuri=max(maximal_Raychaudhuri,
                              abs((fp-fm)/(2*h)/Hp-1))
            results.append({'case':name,'params':params,'Sigma_end':float(m.endpoint(n=n)['Sigma']),
                            'max_independent_Raychaudhuri_rel_error':maximal_Raychaudhuri})
    sha=hashlib.sha256(table.read_bytes()).hexdigest()
    receipt={'schema':'bass.rei.proposed_background_point_tangent.v1',
       'source':'BASS PR163 FD96 mass; isotropic Omega_r only; no gamma/nu anisotropic hierarchy',
       'date':'2026-10-16 KST','cases':len(results),'points_per_case':n,'rows':len(results)*n,
       'csv_sha256':sha,'state_columns':list(HEADER),'cases_receipt':results,
       'consumer_contract':{'native_geometry_requires':'a,b,time_s,H_per_s,s_per_s,sigma_signed=s/H',
                'user_Sigma':'sqrt3 abs(s)/H',
                'adoption':'NOT_ADOPTED_OWNER_REI_REQUIRES_NEW_SOURCE_CHECKPOINT',
                'gamma_nu_HHe':'NOT_INCLUDED_IN_THIS_SUPPLIER'},
       'claim':'read-only typed table, numerically validated Python, NOT Rust type-checked'}
    (out/'PRODUCER_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--points',type=int,default=121)
    a=p.parse_args()
    r=generate(a.out,a.points)
    print('PROPOSED_REI_INPUT',r['rows'],'rows',r['csv_sha256'])
    print('RAYCHAUDHURI_MAX',max(x['max_independent_Raychaudhuri_rel_error'] for x in r['cases_receipt']))
