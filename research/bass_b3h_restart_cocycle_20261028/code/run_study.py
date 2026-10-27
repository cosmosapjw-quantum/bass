"""A new manufactured noncommuting model plus a saved-native cut consumer."""
from pathlib import Path
import json, math, sys
import numpy as np
import mpmath as mp
from scipy.linalg import expm
from restart import rk4,compose,rebase,dump_checkpoint,load_checkpoint
from native_saved import study
U=Path(__file__).resolve().parents[1]
IDENTITY={'source':'manufactured-exact-quadratic-v1','frame':'scalar-FLRW','clock':'t/T_global_T2','V0':'1'}

def matrix(t):return np.array([[2+t,-1.],[-t,3+t]])
def forcing(t):return np.array([1+3*t,6+3*t+2*t*t+t**3])
def exact_p(t):return np.array([1+t,2+t*t])
def rhs(t,y,reset_clock=None):
    theta=t/2 if reset_clock is None else (t-reset_clock)/(2-reset_clock)
    rates=np.array([(1-theta)*(1+y[0]),theta*(2+y[1])])
    return np.concatenate((forcing(t)-matrix(t)@y[:2],*[math.exp(k*.1*t)*rates for k in range(3)]))

def analytic():
    mp.mp.dps=100;T=mp.mpf(2)
    # (1-t/2)(2+t)=2-t^2/2; (t/2)(4+t^2)=2t+t^3/2.
    def moment(degree,a):
        if a==0:return T**(degree+1)/(degree+1)
        def primitive(t):
            return mp.exp(a*t)*sum((-1)**j*mp.factorial(degree)/mp.factorial(degree-j)*t**(degree-j)/a**(j+1) for j in range(degree+1))
        return primitive(T)-primitive(0)
    z=[]
    for k in range(3):
        a=mp.mpf(k)/10;z.extend([2*moment(0,a)-moment(2,a)/2,2*moment(1,a)+moment(3,a)/2])
    return np.array([3.,6.]+[float(v) for v in z])

def main():
    ref=analytic();y0=np.array([1.,2.,0.,0.,0.,0.,0.,0.]);rows=[];checks=[]
    for n in [32,64,128,256]:
        full=rk4(rhs,y0,0,n,2/n);err=np.abs(full-ref)
        rows.append(dict(N=n,dt=2/n,state_error=float(max(err[:2])),reward_error=float(max(err[2:])),max_error=float(max(err)),final_state=full.tolist()))
    checks.append(dict(name='fine_absolute_error_below_5e-7',passed=rows[-1]['max_error']<5e-7))
    ratios=[rows[i]['max_error']/rows[i+1]['max_error'] for i in range(3)]
    checks.append(dict(name='fourth_order_refinement_ratios_above10',passed=min(ratios)>10))
    n=256;dt=2/n;full=np.array(rows[-1]['final_state']);restarts=[];mut=[]
    for tc in [.25,.75,1.5]:
        cut=int(tc/dt);prefix=rk4(rhs,y0,0,cut,dt)
        s=dict(identity=IDENTITY,step=cut,t=cut*dt,dt=dt,y=prefix.tolist(),attempted_work=4*cut,pending=False)
        text=dump_checkpoint(s);loaded=load_checkpoint(text,IDENTITY)
        (U/'results'/f'checkpoint_{cut}.json').write_text(text+'\n')
        end=rk4(rhs,loaded['y'],loaded['step'],n,loaded['dt'])
        bitwise=np.array_equal(end,full);work=loaded['attempted_work']+4*(n-cut)
        restarts.append(dict(cut_s=tc,bitwise_equal=bool(bitwise),cumulative_RHS_evaluations=work,reward_error=float(max(abs(end[2:]-ref[2:])))))
        checks.append(dict(name=f'global_checkpoint_cut_{cut}',passed=bool(bitwise and work==4*n)))
        qss=prefix.copy();qss[:2]=np.linalg.solve(matrix(tc),forcing(tc))
        badq=rk4(rhs,qss,cut,n,dt)
        badclock=rk4(lambda t,y:rhs(t,y,tc),prefix,cut,n,dt)
        badprefix=prefix.copy();badprefix[2:]=0;badprefix=rk4(rhs,badprefix,cut,n,dt)
        eps=float(sum(abs(qss[:2]-prefix[:2])));ell=math.exp(.4)
        bound=ell*eps*(-math.expm1(-2*(2-tc)))/2
        defect=float(max(abs(badq[2:]-full[2:])))
        mut.append(dict(cut_s=tc,QSS_state_error=float(max(abs(badq[:2]-full[:2]))),
            QSS_reward_error=defect,QSS_same_law_reward_bound=bound,
            clock_reset_state_error=float(max(abs(badclock[:2]-full[:2]))),
            clock_reset_reward_error=float(max(abs(badclock[2:]-full[2:]))),
            dropped_prefix_reward_error=float(max(abs(badprefix[2:]-full[2:])))))
        checks.append(dict(name=f'reset_reward_bound_cut_{cut}',passed=defect<=bound+5e-7))
    # A direct noncommuting state transition counterexample, independent of RK4.
    a=-matrix(0);b=-matrix(2);v=np.array([1.,2.])
    ordered=expm(b*.4)@expm(a*.4)@v
    averaged=expm((a+b)*.4)@v
    reversed_=expm(a*.4)@expm(b*.4)@v
    noncomm=dict(commutator_norm=float(np.linalg.norm(a@b-b@a,1)),
        exponential_of_sum_error=float(np.linalg.norm(ordered-averaged,1)),
        reversed_order_error=float(np.linalg.norm(ordered-reversed_,1)))
    checks.append(dict(name='commutation_negative_controls_detected',passed=min(noncomm['exponential_of_sum_error'],noncomm['reversed_order_error'])>1e-4))
    checks.append(dict(name='clock_mutation_changes_rewards_not_population',passed=all(m['clock_reset_state_error']==0 and m['clock_reset_reward_error']>1e-3 for m in mut)))
    # Global reward rebase uses exact analytic synthetic moments, separate from RK4.
    data=dict(status='COMPUTED_MANUFACTURED_REFERENCE',conventions=dict(T_s=2,H_s_inv=.1,gamma_s_inv=2),reference=ref.tolist(),refinement=rows,ratios=ratios,restarts=restarts,mutations=mut,noncommutation=noncomm,checks=checks)
    (U/'results/SYNTHETIC.json').write_text(json.dumps(data,indent=2)+'\n')
    if not all(c['passed'] for c in checks):raise AssertionError('manufactured checks failed; evidence retained')
    source=Path(sys.argv[1]) if len(sys.argv)>1 else U.parent/'bass_b3h_endpoint_channel_interpolation_20261027'
    native=study(source,U/'results')
    print(json.dumps(dict(synthetic_checks=len(checks),synthetic_fine_error=rows[-1]['max_error'],refinement_ratios=ratios,native_checks=len(native['checks']),native_cut=native['cut'],native_negative_controls=native['negative_controls']),indent=2))
if __name__=='__main__':main()
