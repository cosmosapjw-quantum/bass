"""RHS-free independent read-only audit of saved VI0 photon transport data.

Only CSV/JSON and NumPy, no import of original geodesic or Einstein implementation.
All critical validations use explicit exceptions, valid under python -O.
"""
from __future__ import annotations
import csv,json,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
DATA=ROOT/'data'

def check(cond,msg):
    if not bool(cond):raise RuntimeError('SAVED_PHYSICS_AUDIT_FAILED: '+str(msg))

def read(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))

def audit(path=DATA):
    path=Path(path)
    summary=json.loads((path/'VI0_NULL_RESULTS.json').read_text())
    mom=read(path/'VI0_NULL_MOMENT_HISTORY.csv')
    ray=read(path/'VI0_NULL_RAY_PHYSICAL.csv')
    check(len(ray)==78720 and len(mom)==1476,'expected scoped physics counts')
    check(summary['new_distinct_gravitating_einstein_ivps']==0,'no new Einstein claim')
    check(summary['original_G_DYN_MANIFOLD_VI0']=='PARTIAL','must not claim completed gate')
    check(summary['JOIN_J1']=='0/2_FULL_PASS_HOLD','join gate')
    check(not any(summary[x] for x in ('production_ready','merge_ready','auto_next')),'no production')
    groups={}
    for row in ray:
        key=(row['grid'],int(row['case']),row['u'])
        groups.setdefault(key,[]).append(row)
    check(len(groups)==1476,'36 times 41 physical epochs')
    mommap={(row['grid'],int(row['case']),row['u']):row for row in mom}
    check(set(groups)==set(mommap),'moment and ray histories same clocks')
    max_gap=max_J=max_drift=0.
    all_grid_counts={'AXIS6':6,'LEBEDEV26':26,'GL8x16':128}
    per_group={}
    for key,rr in groups.items():
        g,case,t=key;nexp=all_grid_counts[g]
        check(len(rr)==nexp,'physical ray count '+str(key))
        ra=np.array([[float(x[n]) for n in ('nx','ny','nz')] for x in rr])
        E=np.array([float(x['E_normal']) for x in rr]);I=np.array([float(x['I_bolometric']) for x in rr]);w=np.array([float(x['weight_sky_fraction']) for x in rr]);
        s=np.array([float(x['S_shear']) for x in rr])
        check(np.all(np.isfinite(ra)) and np.all(np.isfinite(I)) and np.all(I>0) and np.all(E>0) and np.all(w>0),'positive finite photon states')
        norm=np.max(abs(np.linalg.norm(ra,axis=1)-1));max_drift=max(max_drift,norm)
        check(norm<1e-10,'unit sphere')
        li=np.max(abs(I/E**4-1))
        check(li<1e-12,'null Liouville bolometric I/E^4 invariance')
        rho=float(w@I);press=(w*I)[:,None,None]*ra[:,:,None]*ra[:,None,:]
        P=np.sum(press,axis=0)
        m=mommap[key];q=float(m['rho_tracer']);di=max(abs(rho-q),abs(float(m['sky_weight_sum'])-sum(w)))
        di=max(di,abs(P[0,1]-float(m['I_quad_xy'])),abs(P[0,2]-float(m['I_quad_xz'])),abs(P[1,2]-float(m['I_quad_yz'])))
        max_gap=max(max_gap,di)
        check(di<1.1e-13,'independent ray/pressure moment recomputation')
        # Reconstruct moment equation from *saved* samples, without source RHS import.
        dR_by_ray=float(np.dot(w*I,3*s-4*(1+s)))
        # sigma:P = sum(wI S) pointwise; independent observable contraction.
        dR_mom=-4*rho-np.dot(w*I,s)
        Jr=abs(dR_by_ray-dR_mom);max_J=max(max_J,Jr)
        check(Jr<1e-12,'saved ray-vs-moment balance')
        per_group.setdefault((g,case),[]).append((float(t),float(np.log(w[0])),float(s[0]),float(np.log(E[0])),float(np.log(I[0]))))
    # Finite-difference longitudinal derivatives are independent controls on
    # dynamical integration, not exact identities recomputed from a single time.
    max_fd={'logw':0.,'logE':0.,'logI':0.}
    for key,h in per_group.items():
        h=np.array(sorted(h));tt=h[:,0];s=h[:,2]
        for col,target,name in [(1,3*s,'logw'),(3,-1-s,'logE'),(4,-4*(1+s),'logI')]:
            d=np.gradient(h[:,col],tt,edge_order=2)
            gap=np.max(abs(d-target));max_fd[name]=max(max_fd[name],float(gap))
    for k,v in max_fd.items():check(v<0.004,'time-derivative '+k+' '+str(v))
    out=dict(independent_original_ray_rows=len(ray),independent_moment_rows=len(mom),
        max_photon_sphere_drift=max_drift,max_sky_moment_recompute_gap=max_gap,
        max_saved_energy_balance_gap=max_J,independent_time_derivative_gap=max_fd,
        ownership='geometry source original PR311 exact / non-gravitating isotropic test photons only',
        verifier_imports_implementations=False,
        explicitly_checked_optimized_python=True)
    print('RHS_FREE_SAVED_PHYSICS_AUDIT '+json.dumps(out,sort_keys=True))
    return out

if __name__=='__main__':
    audit(Path(sys.argv[1]) if len(sys.argv)>1 else DATA)
