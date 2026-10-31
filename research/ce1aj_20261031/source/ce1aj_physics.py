#!/usr/bin/env python3
"""CE1AJ real original six-cell Einstein-Vlasov dark-source tangent plus nonlinear IVPs."""
from __future__ import annotations
from pathlib import Path
import sys,csv,json,math
import numpy as np
from scipy.integrate import solve_ivp
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
RESEARCH=HERE.parents[1]
sys.path.insert(0,str(RESEARCH/'ce1ai_20261031'/'source'))
import ce1ai_source_response as p
from certify_finite_transfer import certify
BC=['GL','window','u','E','H','W','q','C2','C4','F','constraint']
TC=['GL','window','u','dell1','dell2','dell3','dh1','dh2','dh3','dE','dW','dq','dC2','dC4',
    'dalpha20','dalpha22','dalpha40','dalpha42','dalpha44','dconstraint','rigorous_upper_bound','rigor_applies']
FC=['GL','window','u','eps','sign','E','W','q','C2','C4','alpha42','constraint']

def compute(gl,window,times,eps):
    p.validate_immutable()
    rays,mass=p.make_cell_rays(gl)
    ray2=rays*rays
    dm=p.ray_source_basis(gl,mass)[-1:]
    y0=p.initial_condition(ray2,mass)
    state=np.r_[y0,p.tangent_initial(ray2,mass,dm).ravel()]
    sol=solve_ivp(lambda u,z:p.rhs_joint(ray2,mass,dm,z),(0,float(times[-1])),state,
       method='DOP853',rtol=3e-12,atol=3e-14,t_eval=times)
    if not sol.success:raise RuntimeError(sol.message)
    finite={}
    for sign in (-1,1):
        shifted=p.positive_reweighted_mass(gl,mass,'DARK_L2L4',sign*eps)
        yy=p.initial_condition(ray2,shifted)
        sf=solve_ivp(lambda u,y:p.rhs_base(ray2,shifted,y),(0,float(times[-1])),yy,
           method='DOP853',rtol=3e-12,atol=3e-14,t_eval=times)
        if not sf.success:raise RuntimeError(sf.message)
        finite[sign]=(shifted,sf.y.T)
    baseline=[];tangents=[];nonlinear=[]
    for i,(u,z) in enumerate(zip(times,sol.y.T)):
        y=z[:6];de=z[6:9];dh=z[9:12]
        o=p.ancestor.basic_observables(ray2,mass,y)
        E=o['E'];P=o['P'];R=o['R'];alpha=o['alpha']
        dEs,dPs,dOmega=p.source_integrals(ray2,dm,y[:3],x=o['x'])
        dE=float((-E-P)@de+dEs[0])
        dP=p.ancestor.pressure_jacobian(P,R)@de+dPs[0]
        dH=float(dh.mean());dSigma=dh-dH
        dW=float(dSigma@o['Pi']+o['sig']@(dP-dE/3))
        dq=(dW-o['q']*dE)/E
        f=p.real_even_harmonics(o['x'])
        dAlpha=o['jac']@de+(4*math.pi/E)*(f@dOmega[0])-alpha*(dEs[0]/E)
        dC2=float((2*alpha[0]*dAlpha[0]+4*alpha[1]*dAlpha[1])/5)
        dC4=float((2*alpha[2]*dAlpha[2]+4*alpha[3]*dAlpha[3]+4*alpha[4]*dAlpha[4])/9)
        dcon=float((sum(y[3:])-y[3:])@dh-dE)
        F=E*math.exp(4*sum(y[:3])/3)/.9
        bound=-(float(u)/2) if window=='micro_certified' and u>0 else float('nan')
        applies=int(window=='micro_certified' and u>0)
        baseline.append([gl,window,u,E,o['H'],o['W'],o['q'],o['C2'],o['C4'],F,o['C']])
        tangents.append([gl,window,u,*de,*dh,dE,dW,dq,dC2,dC4,*dAlpha,dcon,bound,applies])
        for sign,(m,states) in finite.items():
            v=p.ancestor.basic_observables(ray2,m,states[i])
            nonlinear.append([gl,window,u,eps,sign,v['E'],v['W'],v['q'],v['C2'],v['C4'],v['alpha'][3],v['C']])
    ends={int(q[4]):q for q in nonlinear if q[2]==times[-1]}
    fd=(float(ends[1][10])-float(ends[-1][10]))/(2*eps)
    stats={'GL':gl,'window':window,'rays':len(mass),'epochs':len(times),
        'base_constraint_max':float(max(abs(x[-1]) for x in baseline)),
        'tan_constraint_max':float(max(abs(x[TC.index('dconstraint')]) for x in tangents)),
        'fd_alpha42_endpoint_gap':abs(fd-tangents[-1][TC.index('dalpha42')]),
        'endpoint_dalpha42':float(tangents[-1][TC.index('dalpha42')]),
        'endpoint_dC4':float(tangents[-1][TC.index('dC4')]),
        'endpoint_dW':float(tangents[-1][TC.index('dW')])}
    return baseline,tangents,nonlinear,stats

def main():
    cert=certify()
    data=ROOT/'data';data.mkdir(parents=True,exist_ok=True)
    allb=[];allt=[];allf=[];stats={}
    for gl in (6,8,16):
        for window,t in (('micro_certified',np.linspace(0,1e-6,401)),
                         ('full_numeric',np.linspace(0,.08,401))):
            b,z,f,meta=compute(gl,window,t,1e-3)
            allb.extend(b);allt.extend(z);allf.extend(f)
            stats[f'{gl}_{window}']=meta
            print('CE1AJ',gl,window,len(b),len(z),len(f),meta['endpoint_dalpha42'],flush=True)
    for filename,cols,rows in (
        ('CE1AJ_BASELINE_PHYSICAL.csv',BC,allb),
        ('CE1AJ_DARK_TANGENT_PHYSICAL.csv',TC,allt),
        ('CE1AJ_DARK_FINITE_IVP.csv',FC,allf)):
        with (data/filename).open('w',newline='') as out:
            w=csv.writer(out);w.writerow(cols);w.writerows(rows)
    (data/'CE1AJ_CONTINUUM_FINITE_TRANSFER_CERTIFICATE.json').write_text(json.dumps(cert,indent=2)+'\n')
    result={'schema':'bass.ce1aj.real_original_dark_transfer.v1',
            'source_sha256':p.ORIGINAL_SOURCE_SHA,
            'parent_head':'06a89b70200c09e44711235ef6d01a0b797b2a03',
            'rows':{'baseline':len(allb),'tangent':len(allt),'nonlinear':len(allf)},
            'stats':stats,'certified_u':[0,1e-6],'numerical_full_u':[0,.08],
            'finite_amplitude':1e-3,'upper_DAG':'9/15','CE1':'PARTIAL',
            'new_upper_nodes':0,'distinct_author_R6_C9':'NOT_RUN',
            'production_ready':False,'merge_ready':False,'auto_next':False}
    (data/'CE1AJ_REAL_PHYSICAL_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    print('CE1AJ_COUNTS',result['rows'])

if __name__=='__main__':main()
