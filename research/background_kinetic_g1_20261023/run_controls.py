"""New finite collisionless controls. Refuse to overwrite completed outputs."""
from pathlib import Path
import json,sys,time,hashlib,platform
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.linalg import expm
import kinetic as kn
from vendor import core as bg

HERE=Path(__file__).resolve().parent
FAMILIES={'I':([0,0,0],0),'II':([.4,0,0],0),'III':([0,.4,-.4],.4),
 'IV':([0,0,.4],.1),'V':([0,0,0],.2),'VI0':([0,.4,-.4],0),
 'VIh':([0,.4,-.4],.1),'VII0':([0,.4,.4],0),'VIIh':([0,.4,.4],.1),
 'VIII':([-.4,.4,.4],0),'IX':([.4,.4,.4],0),'VI_exc':([0,.6,-.6],.2)}
S=np.array([[.06,.02,-.01],[.02,-.025,.015],[-.01,.015,-.035]])
GRID=np.linspace(0,1.5,101)

def init_case(name,rotation=(0.,0.,0.)):
    diag,a0=FAMILIES[name];n=np.diag(diag);a=np.array([a0,0.,0.]);s=S.copy()
    directions=np.vstack([np.eye(3)[i]*sgn for i in range(3) for sgn in [1.,-1.]])
    k=np.tile(directions,(2,1));mass=np.r_[np.full(6,3.),np.zeros(6)];sector=np.repeat([0,1],6)
    target=3*s@a+bg.epsilon_product(n,s);counter=np.array([.02,-.01,.005])
    f=[.6*target+counter,.4*target-counter];rhos=[1.8,.9];weights=[]
    for j in range(2):
        E=np.sqrt(mass[6*j]**2+1)
        pair=rhos[j]*np.array([1.2,.9,.9])/(6*E)
        weights.extend(np.ravel(np.column_stack([pair+f[j]/2,pair-f[j]/2])))
    w=np.array(weights);model=kn.CoupledPackets(mass,sector,cosmological_constant=.2,rotation=rotation)
    rho,_,_=model.moment_blocks(k,w);R3,_=bg.curvature(n,a)
    h=np.sqrt((sum(rho)+.2+np.sum(s*s)/2-R3/2)/3)
    z=model.initial(h,s,n,a,k,w)
    assert min(w)>0 and np.max(np.abs(bg.constraints(z[:24],.2)))<1e-14
    return model,z

def summarize(model,Y):
    cc=[];cm=[];ledger=[];rhom=[];flux=[];pi=[];num=[];weights=[]
    for z in Y.T:
        y,k,w=model.decode(z);rho,f,src=model.moment_blocks(k,w)
        zz=z[:model.nb].copy();zz[16:16+model.ns]=rho;zz[16+model.ns:]=f.ravel()
        cc.append(bg.relative_constraint(z[:model.nb],model.lam));cm.append(bg.relative_constraint(zz,model.lam))
        ledger.append(max(np.max(np.abs(rho-y.rho)/(1+np.abs(rho))),np.max(np.abs(f-y.flux)/(1+np.abs(f)))))
        rhom.append(rho);flux.append(f);pi.append(src.pi)
        num.append([np.sum(w[model.sectors==j])*np.exp(3*y.alpha) for j in range(model.ns)])
        weights.append(np.min(w))
    arrays=dict(core_constraint=np.array(cc),kinetic_constraint=np.array(cm),ledger=np.array(ledger),
                rho_packet=np.array(rhom),flux_packet=np.array(flux),pi=np.array(pi),comoving_number=np.array(num))
    return dict(max_core_constraint=max(cc),max_kinetic_constraint=max(cm),max_moment_mismatch=max(ledger),
        min_weight=min(weights),max_flux=float(np.max(np.linalg.norm(arrays['flux_packet'],axis=2))),
        max_offdiagonal_pi=float(np.max(np.abs(arrays['pi'][:,:,[0,0,1],[1,2,2]]))),
        comoving_number_fractional_change=(arrays['comoving_number'][-1]/arrays['comoving_number'][0]-1).tolist()),arrays

def solve(name,model,z,out,*,tight=False,wrong_weight=False):
    target=out/(name+'.npz')
    if target.exists():raise FileExistsError(target)
    fun=model.rhs
    if wrong_weight:
        def fun(t,z):
            dz=model.rhs(t,z);y,k,w=model.decode(z);dz[-len(w):]=-3*y.h
            return dz
    t=time.perf_counter()
    sol=solve_ivp(fun,(0,GRID[-1]),z,t_eval=GRID,method='DOP853',rtol=2e-12 if tight else 2e-10,
                  atol=2e-14 if tight else 2e-12,max_step=.05)
    if not sol.success:raise RuntimeError(sol.message)
    info,arrays=summarize(model,sol.y)
    info.update(name=name,nfev=sol.nfev,elapsed_s=time.perf_counter()-t,tight=tight,wrong_weight=wrong_weight)
    np.savez_compressed(target,tau=GRID,state=sol.y,**arrays)
    info['raw_sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
    return info,sol.y

def main(out):
    out.mkdir(parents=True,exist_ok=False)
    rows=[];states={};started=time.perf_counter()
    for name in FAMILIES:
        m,z=init_case(name);info,Y=solve(name,m,z,out);rows.append(info);states[name]=Y
    convergence=[]
    for name in ['V','VIII','VI_exc']:
        m,z=init_case(name);info,Y=solve(name+'_tight',m,z,out,tight=True);rows.append(info)
        convergence.append({'name':name,'max_scaled_state_difference':float(np.max(np.abs(Y-states[name])/(1+np.maximum(np.abs(Y),np.abs(states[name])))))})
    omega=np.array([.11,-.07,.13]);m,z=init_case('V',omega);info,Y=solve('V_rotating',m,z,out,tight=True);rows.append(info)
    # Compare all frame indices to the separate nonrotating tight trajectory.
    ref=np.load(out/'V_tight.npz')['state'];maxrot=0.
    for j,t in enumerate(GRID):
        O=expm(bg.cross(omega)*t);want=ref[:,j].copy();want[:24]=bg.rotate_state(want[:24],O)
        want[24:60]=(ref[24:60,j].reshape(-1,3)@O.T).ravel()
        maxrot=max(maxrot,float(np.max(np.abs(Y[:,j]-want)/(1+np.abs(want)))))
    m,z=init_case('V');wrong,_=solve('V_wrong_weight',m,z,out,wrong_weight=True)
    # A genuinely new closed collisionless mixture, not the prior perfect-fluid solution.
    k=np.tile(np.vstack([np.eye(3)[i]*sgn for i in range(3) for sgn in [1.,-1.]]),(2,1))
    mass=np.r_[np.full(6,3.),np.zeros(6)];w=np.r_[np.full(6,2.2/(6*np.sqrt(10))),np.full(6,.92/6)]
    m=kn.CoupledPackets(mass,np.repeat([0,1],6));z=m.initial(.2,np.zeros((3,3)),2*np.eye(3),np.zeros(3),k,w)
    info,Y=solve('IX_turnaround',m,z,out);rows.append(info)
    turnaround={'initial_h':float(Y[0,0]),'final_h':float(Y[0,-1]),'negative_h_samples':int(np.sum(Y[0]<0))}
    maxes={key:max(row[key] for row in rows) for key in ['max_core_constraint','max_kinetic_constraint','max_moment_mismatch']}
    passed=all(v<2e-8 for v in maxes.values()) and maxrot<2e-8 and all(x['max_scaled_state_difference']<2e-8 for x in convergence)
    passed=passed and turnaround['final_h']<0 and wrong['max_moment_mismatch']>1e-4
    result={'status':'PASS_SCOPED' if passed else 'FAIL','cases':rows,'maxima':maxes,'convergence':convergence,
      'rotating_full_state_error':maxrot,'wrong_weight_control':wrong,'turnaround':turnaround,
      'new_ivps':len(rows)+1,'new_nominal_family_ivps':len(FAMILIES),'old_ivps_replayed':0,
      'total_elapsed_s':time.perf_counter()-started,'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
      'platform':platform.platform(),'scope':'finite positive collisionless measures; no smooth-source or global convergence certification'}
    (out/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    return 0 if passed else 1
if __name__=='__main__':sys.exit(main(Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'evidence/controls_001'))
