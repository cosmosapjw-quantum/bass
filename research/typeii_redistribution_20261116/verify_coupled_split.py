#!/usr/bin/env python3
"""Independent exact-generator test of the declared factorized collision model.
This is a constructed static medium test, not an extra cosmological result.
"""
import json
import numpy as np
from scipy.linalg import expm
from redistribution import *
def main():
 n,w=sphere_rule(3,4);na,D=atom_directions(n,.05);A,pi=angular_generator(na,w/D**2,D)
 e=NU0*(1+np.linspace(-.002,.002,17));nu=(e[:-1]+e[1:])/2
 rate=.4+.2*np.exp(-((nu-NU0)/(NU0*.001))**2);face=.4+.2*np.exp(-((e-NU0)/(NU0*.001))**2)
 pd=.03;model=frequency_model(e,3000.,rate,face,pd,absorbing=True)
 B=np.diag(-model['loss'])+np.diag(model['up'],-1)+np.diag(model['down'],1)
 M=len(n);N=len(nu);size=M*N;Q=np.zeros((size,size));count_rates=np.zeros((3,size))
 for a in range(M):
  ids=np.arange(a*N,(a+1)*N);Q[np.ix_(ids,ids)]+=D[a]*B
  count_rates[0,ids[0]]=D[a]*model['red'];count_rates[1,ids[-1]]=D[a]*model['blue'];count_rates[2,ids]=D[a]*model['kill']
 for k in range(N):
  ids=np.arange(M)*N+k;Q[np.ix_(ids,ids)]+=(1-pd)*rate[k]*A
 ext=np.zeros((size+3,size+3));ext[:size,:size]=Q;ext[size:,:size]=count_rates
 check(np.max(abs(ext.sum(axis=0)))<1e-14,'whole coupled generator conservation')
 p=np.exp(3*n[:,0,None]-.5*((np.arange(N)[None,:]-7.5)/2)**2);p/=p.sum();state0=np.r_[p.ravel(),[0.,0.,0.]]
 duration=3.;expected=expm(duration*ext)@state0;checks=[]
 for steps in (20,40,80,160):
  y=p.copy();loss=np.zeros(3);dt=duration/steps
  for _ in range(steps):
   y=angular_evolve(A,pi,y,.5*dt*(1-pd)*rate)
   for a in range(M):
    r=frequency_step(model,y[a],dt*D[a]);y[a]=r['N'];loss+=np.array([r['red'],r['blue'],r['death']])
   y=angular_evolve(A,pi,y,.5*dt*(1-pd)*rate)
  got=np.r_[y.ravel(),loss]
  checks.append({'steps':steps,'maximum_full_state_gap':float(max(abs(got-expected))),'L1_full_state_gap':float(sum(abs(got-expected))),'count_gap':float(abs(got.sum()-1)),'minimum_alive':float(y.min())})
 check(all(checks[i+1]['maximum_full_state_gap']<checks[i]['maximum_full_state_gap'] for i in range(3)),'coupled split convergence')
 check(max(x['count_gap'] for x in checks)<1e-12,'coupled split number')
 # Correct Doppler-weighted normal-slice stationary count versus wrong atom-slice count.
 right=pi;wrong=(w/D**2)/sum(w/D**2)
 wrongres=float(np.linalg.norm(A@wrong,1));rightres=float(np.linalg.norm(A@right,1))
 # Recoil omitted: the physical Wien state is no longer stationary.
 mr=frequency_model(e,3000.,rate,face,0.,absorbing=False,recoil=True);mw=frequency_model(e,3000.,rate,face,0.,absorbing=False,recoil=False)
 q=mr['pi']/sum(mr['pi']);Bw=np.diag(-mw['loss'])+np.diag(mw['up'],-1)+np.diag(mw['down'],1)
 recoil_defect=float(np.linalg.norm(Bw@q,1));check(recoil_defect>1e-10 and wrongres>1e-4,'hostile physical counterexamples')
 result={'closure':'factorized frequency diffusion + elastic dipole angle, fixed medium','coupled_system_size':size,'independent_dense_exponential_checks':checks,'correct_angular_equilibrium_L1_residual':rightres,'wrong_rest_slice_equilibrium_L1_residual':wrongres,'missing_recoil_Wien_L1_residual_s_inverse':recoil_defect,'no_full_correlated_PRD_claim':True}
 (HERE/'COUPLED_SPLIT_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
