"""CE1-AB: independently replay original CE1-U GL-source DOP853 ODE; no IVP certification."""
import sys,json,hashlib,csv,os,math
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
BASE=Path(__file__).resolve().parent
ORIGINAL=(BASE/'ce1aa_input') if (BASE/'ce1aa_input').is_dir() else (BASE.parent/'ce1aa_20261030')
sys.path.insert(0,str(ORIGINAL/'source'))
from cellwise_gl_rust import make_cell_rays, frozen_source_identity,SHEAR,sha
END=.08
TIMES=np.linspace(0.,END,41)
SOURCE='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
EXPHASH={6:'6eff8cd9f31d027bbee55720332302b6fbad71b3639b5809aab6b9ce6f53e489',8:'1398980ec71662494273e05eb4bd52a78f6e6c7f208702638da6c739698f7502'}
RAYSH={6:'6f6e5d0797404521abd51cb8394a8b2beca3e96b392924b9ad30b2093098d957',8:None}

def angular(rays,mass,ell):
    b=np.exp(-2.*np.asarray(ell,dtype=float))
    q=rays*rays*b
    rr=np.sqrt(np.sum(q,axis=1))
    vv=np.exp(-np.sum(ell));W=mass*vv*rr
    x=q/(rr[:,None]**2)
    E=float(np.sum(W));P=np.sum(W[:,None]*x,axis=0)
    return E,P

def rhs(u,y,rays,mass):
    ell,h=y[:3],y[3:];_,P=angular(rays,mass,ell)
    return np.r_[h,-h.sum()*h+P]

def init(rays,mass):
    E0,_=angular(rays,mass,np.zeros(3));s=SHEAR
    H=math.sqrt((E0+.5*np.dot(s,s))/3)
    return np.r_[np.zeros(3),np.asarray(H+s)]

def run(n,output):
    assert frozen_source_identity()==SOURCE
    rays,mass=make_cell_rays(n)
    frozen=ORIGINAL/'input'/f'GL{n}_DOP853_coupled_41epochs.csv'
    assert hashlib.sha256(frozen.read_bytes()).hexdigest()==EXPHASH[n]
    old=list(csv.DictReader(frozen.open()))
    y0=init(rays,mass)
    # dense output needed for source-derived continuous polynomial, same run settings as original CE1-U.
    sol=solve_ivp(lambda t,y:rhs(t,y,rays,mass),(0.,END),y0,method='DOP853',rtol=3e-12,atol=3e-14,t_eval=TIMES,dense_output=True)
    assert sol.success
    assert len(sol.sol.interpolants)==len(sol.sol.ts)-1
    state_fields=['ell1','ell2','ell3','h1','h2','h3']
    y_saved=np.array([[float(r[k]) for k in state_fields] for r in old])
    maxdiff=np.max(np.abs(sol.y.T-y_saved))
    ulps=np.abs(sol.y.T.view(np.int64)-y_saved.view(np.int64)) # inaccurate near zero but for bit same fine
    dd={'model':'original source-locked GL Einstein-Vlasov six-cell replay; output not original DOP continuous run bytes',
        'source_sha256':SOURCE,'frozen_reference_csv_sha256':EXPHASH[n],
        'scipy_version':__import__('scipy').__version__,'numpy_version':np.__version__,
        'rays_sha256':sha(rays.tobytes()),'masses_sha256':sha(mass.tobytes()),
        'rays':len(rays),'DOP853_rtol':3e-12,'DOP853_atol':3e-14,'nfev':sol.nfev,'n_steps':len(sol.sol.interpolants),
        'max_abs_saved_state_difference':float(maxdiff),'num_binary64_equal_saved_states':int(np.sum(sol.y.T==y_saved)),
        'num_binary64_state_entries':int(y_saved.size),
        'max_abs_initial_difference':float(np.max(abs(y_saved[0]-y0))),
        'interval_coefficients_original_identity':'REGENERATED_WITH_ORIGINAL_ALGORITHM_NOT_ORIGINAL_ADAPTIVE_STEP_CAPTURE',
        'replay_target_status':'EXACT' if maxdiff==0 else 'NOT_EXACT',
        'steps':[]}
    for j,(ta,tb,interp) in enumerate(zip(sol.sol.ts[:-1],sol.sol.ts[1:],sol.sol.interpolants)):
        F=interp.F
        dd['steps'].append({'i':j,'t_old_hex':float(ta).hex(),'t_end_hex':float(tb).hex(),
                     'h_hex':float(interp.h).hex(), 'y_old_hex':[float(x).hex() for x in interp.y_old],
                     'F_hex':[[float(x).hex() for x in v] for v in F],
                     'y_end_hex':[float(x).hex() for x in interp(tb)],
                    })
    output.mkdir(exist_ok=True,parents=True)
    p=output/f'GL{n}_REPLAY_DOP853_DENSE.json'
    p.write_text(json.dumps(dd,indent=2)+'\n')
    print(f'GL{n}: steps {dd["n_steps"]}, nfev {sol.nfev}, max abs frozen mismatch {maxdiff:.4e}, byte equal {dd["num_binary64_equal_saved_states"]}/246, step ts {sol.sol.ts}')
    return dd

if __name__=='__main__':
    a=run(6, BASE/'results');b=run(8, BASE/'results')
