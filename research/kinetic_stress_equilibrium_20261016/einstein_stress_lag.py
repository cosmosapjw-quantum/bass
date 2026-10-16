"""BASS PR164 original Einstein-Vlasov IVP vs stress-neutral source chart.
This only evolves BASS FD96 massive matter and frozen isotropic radiation;
no REI photon hierarchy, chemistry, stellar recoil or momentum Q^a owner.
"""
from __future__ import annotations
import csv,hashlib,json,math,pathlib,sys,argparse
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
pinned=HERE.parents[1]/'rei_einstein_tangent_20261016'
if pinned.joinpath('kinetic_tangent.py').exists():
    sys.path.insert(0,str(pinned))
else:
    sys.path.insert(0,str(HERE.parent/'reference_pr164'))
from kinetic_tangent import EinsteinTangent,AREF,XMAX
from kinetic_equilibrium import FD96Equilibrium

def evaluate(m,A,grid=81):
    model=EinsteinTangent(mass=float(m),fraction=.1,A=float(A),Sigma_ref=0.,orientation=1)
    source=FD96Equilibrium(float(m))
    sol=model.solution(rtol=2e-12,atol=2e-14,n=grid)
    rows=[];max_energy=0.;max_ray=0.
    for idx,x in enumerate(sol.t):
        state=sol.y[:,idx];b,v,t=state[:3]
        M,H,dust,rad=model.field(x,b,v)
        s=model.href*v
        neutral=source.equilibrium(x,A)
        stress=source.stress(x,b,A)
        if abs(stress.rho-M.rho)>8e-14 or abs(stress.delta-M.delta)>8e-14:
            raise ArithmeticError('SOURCE_STRESS_MODEL_DISAGREEMENT')
        if idx not in (0,len(sol.t)-1):
            h=min(1.5e-5,x*.4,(XMAX-x)*.4)
            ym=sol.sol(x-h);yp=sol.sol(x+h)
            Mminus=model.field(x-h,ym[0],ym[1])[0]
            Mplus=model.field(x+h,yp[0],yp[1])[0]
            drho=(Mplus.rho-Mminus.rho)/(2*h)
            energy=drho+3*(M.rho+M.pbar)+2*(s/H)*M.delta
            den=3*(M.rho+M.pbar)+2*abs(s/H*M.delta)
            max_energy=max(max_energy,abs(energy)/max(den,1e-30))
            hm=model.field(x-h,ym[0],ym[1])[1]
            hp=model.field(x+h,yp[0],yp[1])[1]
            fd=(hp-hm)/(2*h)
            ray=model.raychaudhuri(x,state)
            max_ray=max(max_ray,abs(fd-ray)/max(abs(ray),1e-30))
        rows.append(dict(m=float(m),A=float(A),x=float(x),a=AREF*math.exp(x),
            b=float(b),b_neutral=neutral.b_star,lag_b=float(b-neutral.b_star),
            signed_s_per_H=float(s/H),Sigma=float(3**.5*abs(s/H)),
            delta=float(M.delta),chi_b=stress.chi_b,H=float(H),
            rho_kinetic=float(M.rho),pbar_kinetic=float(M.pbar),
            d_b_neutral_dx=neutral.db_dx,
            ratio_abs_b_over_b_neutral=float(abs(b/neutral.b_star)) if abs(neutral.b_star)>1e-13 else None))
    return rows,dict(max_norm_energy_work=max_energy,max_norm_raychaudhuri=max_ray,
                     solver_nfev=int(sol.nfev),solver_success=bool(sol.success))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,required=True);o=ap.parse_args().out
    if o.exists():raise FileExistsError('CREATE_ONLY_EVIDENCE')
    o.mkdir(parents=True)
    rows=[];cases=[]
    for m in (3,30,300):
        for A in (-.5,0.,.5,2.):
            rr,diag=evaluate(m,A)
            rows.extend(rr);v=rr[-1]
            if A==0 and (v['b']!=0 or v['Sigma']!=0 or v['delta']!=0):
                raise AssertionError('A0_ZERO_SHEAR_LIMIT')
            if A!=0 and (v['b']*A<=0 or v['signed_s_per_H']*A<=0):
                raise AssertionError('KINETIC_SHEAR_SIGN')
            cases.append(dict(m=m,A=A,endpoint=v,checks=diag))
    with (o/'DYNAMICAL_HISTORY.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    energy=max(c['checks']['max_norm_energy_work'] for c in cases)
    ray=max(c['checks']['max_norm_raychaudhuri'] for c in cases)
    receipt={'schema':'bass.vlasov.stress_neutral_vs_einstein_ivp.v1',
        'parent_pr164_git_blob':'1cab2bf7eab5a306ab207206ca3a0fc793dc9163',
        'scope':'LRS FD96 + isotropic nonkinetic radiation; no native REI',
        'rows':len(rows),'cases':len(cases),'max_norm_kinetic_energy_work_fd':energy,
        'max_norm_raychaudhuri_fd':ray,'state_cases':cases}
    (o/'DYNAMICS.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (o/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name for f in sorted(o.iterdir()))+'\n')
    print(json.dumps({'rows':len(rows),'cases':len(cases),'max_energy_work':energy,'max_raychaudhuri':ray},indent=2))
    if energy>2e-9 or ray>2e-9:raise AssertionError('KINETIC_DYNAMICS_CONSERVATION')

if __name__=='__main__':main()
