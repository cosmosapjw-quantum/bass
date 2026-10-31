#!/usr/bin/env python3
"""Original BASS CE1AK: exact sixth angular source jet and actual nonlinear Bianchi I."""
import csv, json, math, sys
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
RESEARCH=ROOT.parent
sys.path.insert(0,str(RESEARCH/'ce1ai_20261031'/'source'))
import ce1ai_source_response as p
ORIGINAL_SHA='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
PARENT_SHA='50dc76e3ba460d0565b65a60b816af2ded0da6a3'
TKEY={'xxx':-3,'xxy':1,'xxz':2,'xyy':1,'xyz':-2,'xzz':0,
      'yyy':-3,'yyz':2,'yzz':0,'zzz':0}
ORDERS=(6,8,16)
WINDOWS={'jet_resolved':.01,'original_horizon':.08}
FIELDS=['GL','window','u','E','W','constraint','T_xxx','T_xxy','T_xxz','T_xyz',
        'dP1','dP2','dP3','dE','dW','dF','dh1','dh2','dh3',
        'dell1','dell2','dell3','dconstraint']
FINITE=['GL','window','u','sign','eps','E','W','P1','P2','P3',
        'h1','h2','h3','ell1','ell2','ell3','constraint']

def frac_avg(a,b,k):
    return (b**(k+1)-a**(k+1))/((k+1)*(b-a))

def certificate():
    if p.validate_immutable()!=ORIGINAL_SHA:
        raise RuntimeError('Original six-cell SHA mismatch')
    mu=[(F(0),F(1,2)),(F(1,2),F(1))]
    avg=[1-3*frac_avg(a,b,2)+3*frac_avg(a,b,4)-frac_avg(a,b,6) for a,b in mu]
    if avg != [F(1759,2240),F(289,2240)]:
        raise RuntimeError('Exact angular moments')
    q=-F(1,16)*(F(212,203)*avg[0]-4*avg[1])
    if q!=F(-27,1421):raise RuntimeError('Exact sixth source')
    sig=[F.from_float(float(x)) for x in p.SHEAR]
    if sum(sig)!=0:raise RuntimeError('Original shear')
    tensor=[[[q*TKEY[''.join(sorted('xyz'[i]+'xyz'[j]+'xyz'[k]))]
               for k in range(3)] for j in range(3)] for i in range(3)]
    if any(sum(tensor[i][j][k] for i in range(3))!=0
           for j in range(3) for k in range(3)):
        raise RuntimeError('Sixth source trace mismatch')
    A=[sum((sig[j]*sig[k]*tensor[i][j][k]
          for j in range(3) for k in range(3)),F(0)) for i in range(3)]
    work=sum((sig[i]*A[i] for i in range(3)),F(0))
    if work != -3*q*(sig[0]-sig[1])**2*(sig[0]+sig[1]-2*sig[2]):
        raise RuntimeError('Exact shear contraction factorization')
    if sum(A)!=0 or work<=0:raise RuntimeError('Original dark work sign')
    E0=sum((F.from_float(float(v)) for row in p.CELL_E for v in row),F(0))
    return {'source_sha256':ORIGINAL_SHA,'parent_head':PARENT_SHA,
      'T_xxy_over_pi':str(q),'A_i_over_pi':[str(x) for x in A],
      'sigma_A_over_pi':str(work),'sigma_A':float(work)/math.pi,
      'delta_P_second_over_pi':[str(3*x) for x in A],
      'delta_W_second_over_pi':str(3*work),
      'delta_E_third_over_pi':str(-3*work),
      'delta_h_third_over_pi':[str(3*x) for x in A],
      'delta_ell_fourth_over_pi':[str(3*x) for x in A],
      'P_u2':[float(F(3,2)*x)/math.pi for x in A],
      'h_u3':[float(F(1,2)*x)/math.pi for x in A],
      'ell_u4':[float(x/8)/math.pi for x in A],
      'W_u2':float(F(3,2)*work)/math.pi,
      'E_u3':-float(work/2)/math.pi,
      'F_u3':-float(work/(2*E0))/math.pi,
      'scope':'Exact continuum initial jets; full-horizon output only GL numerical',
      'upper_DAG':'9/15','CE1':'PARTIAL','new_upper_nodes':0,
      'distinct_R6_C9':'NOT_RUN','merge_ready':False,'production_ready':False}

def t6(ray2,delta_m,ell,x):
    rad=np.sqrt((ray2*np.exp(-2*np.asarray(ell))).sum(axis=1))
    mass=delta_m*rad*math.exp(-sum(ell))
    return np.einsum('r,ri,rj,rk->ijk',mass,x,x,x,optimize=True)

def generate(output=None,orders=ORDERS):
    root=Path(output) if output else ROOT/'data'
    root.mkdir(parents=True,exist_ok=True)
    cert=certificate()
    (root/'CE1AK_EXACT_JETS.json').write_text(json.dumps(cert,indent=2)+'\n')
    rows=[];finite=[];stats={}
    for gl in orders:
        rays,mass=p.make_cell_rays(gl);ray2=rays*rays
        dm=p.ray_source_basis(gl,mass)[-1]
        y0=p.initial_condition(ray2,mass)
        z0=np.r_[y0,p.tangent_initial(ray2,mass,dm[None,:])[0]]
        E0=p.ancestor.moment(ray2,mass,[0.,0.,0.])[0]
        stats[str(gl)]={}
        for window,endpoint in WINDOWS.items():
            times=np.linspace(0,endpoint,401)
            sol=solve_ivp(lambda t,z:p.rhs_joint(ray2,mass,dm[None,:],z),
                          (0,endpoint),z0,method='DOP853',
                          rtol=3e-12,atol=3e-14,t_eval=times)
            if not sol.success:raise RuntimeError(sol.message)
            paths={}
            for sign in (-1,1):
                shifted=p.positive_reweighted_mass(gl,mass,'DARK_L2L4',sign*.001)
                src=solve_ivp(lambda t,y:p.rhs_base(ray2,shifted,y),
                              (0,endpoint),p.initial_condition(ray2,shifted),
                              method='DOP853',rtol=3e-12,atol=3e-14,t_eval=times)
                if not src.success:raise RuntimeError(src.message)
                paths[sign]=(shifted,src.y.T)
            start=len(rows);fstart=len(finite)
            for j,(t,z) in enumerate(zip(times,sol.y.T)):
                y=z[:6];ell=y[:3];h=y[3:];dl=z[6:9];dh=z[9:12]
                ob=p.ancestor.basic_observables(ray2,mass,y)
                E,P,R,x=ob['E'],ob['P'],ob['R'],ob['x']
                srcE,srcP,_=p.source_integrals(ray2,dm[None,:],ell,x=x)
                de=float((-E-P)@dl+srcE[0])
                dp=p.ancestor.pressure_jacobian(P,R)@dl+srcP[0]
                ds=dh-dh.mean()
                dw=float(ds@ob['Pi']+ob['sig']@(dp-de/3))
                FF=E*math.exp(4*sum(ell)/3)/E0
                dF=FF*(de/E+4*sum(dl)/3)
                dc=float((sum(h)-h)@dh-de)
                tt=t6(ray2,dm,ell,x)
                rows.append([gl,window,float(t),E,ob['W'],ob['C'],
                             tt[0,0,0],tt[0,0,1],tt[0,0,2],tt[0,1,2],
                             *dp,de,dw,dF,*dh,*dl,dc])
                for sign,(mm,history) in paths.items():
                    yy=history[j];vals=p.ancestor.basic_observables(ray2,mm,yy)
                    finite.append([gl,window,float(t),sign,.001,
                                   vals['E'],vals['W'],*vals['P'],
                                   *yy[3:],*yy[:3],vals['C']])
            sub=rows[start:];end=sub[-1];at={k:FIELDS.index(k) for k in FIELDS}
            fn=finite[fstart:]
            stats[str(gl)][window]={
               'rows_tangent':len(sub),'rows_finite':len(fn),
               'endpoint_dW':float(end[at['dW']]),
               'endpoint_dE':float(end[at['dE']]),
               'endpoint_dP1':float(end[at['dP1']]),
               'endpoint_dh1':float(end[at['dh1']]),
               'endpoint_dell1':float(end[at['dell1']]),
               'max_constraint':max(abs(r[at['constraint']]) for r in sub),
               'max_tangent_constraint':max(abs(r[at['dconstraint']]) for r in sub),
               'max_nonlinear_constraint':max(abs(r[-1]) for r in fn)}
            if abs(float(sub[0][at['T_xxy']])-float(F(-27,1421))/math.pi)>2e-10:
                raise RuntimeError('Exact sixth tensor vs GL source')
            if stats[str(gl)][window]['max_tangent_constraint']>1e-10:
                raise RuntimeError('Einstein linearized constraint failure')
            print('CE1AK',gl,window,len(sub),len(fn),
                  'dW',stats[str(gl)][window]['endpoint_dW'],flush=True)
    if len(rows)!=2406 or len(finite)!=4812:raise RuntimeError('Unexpected IVP row count')
    for name,cols,data in [('CE1AK_STRESS_EINSTEIN.csv',FIELDS,rows),
                           ('CE1AK_NONLINEAR_IVP.csv',FINITE,finite)]:
        with (root/name).open('w',newline='') as h:
            wr=csv.writer(h);wr.writerow(cols);wr.writerows(data)
    summary={'source_sha256':ORIGINAL_SHA,'parent_head':PARENT_SHA,
             'windows':WINDOWS,'orders':list(orders),'tangent_rows':len(rows),
             'nonlinear_ivp_rows':len(finite),'total_physical_rows':len(rows)+len(finite),
             'reports':stats,'upper_DAG':'9/15','CE1':'PARTIAL',
             'new_upper_nodes':0,'continuum_horizon_sign':'NOT_CERTIFIED',
             'production_ready':False,'merge_ready':False}
    (root/'CE1AK_SUMMARY.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    return summary

if __name__=='__main__':
    report=generate()
    print('CE1AK_NEW_PHYSICAL_ROWS',report['total_physical_rows'])
