"""One custom focused test script. Executed only after controller GO."""
from pathlib import Path
import json,math,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
import positive_angular as p
checks=[]
def record(name,residual,limit=p.ROUND,**details):
    assert residual<=limit,(name,residual,limit)
    checks.append(dict(group=name,status='PASS',residual=float(residual),limit=float(limit),**details))
def rejected(name,call,kind=ValueError):
    try:call()
    except kind as e:return dict(name=name,exception=type(e).__name__,message=str(e),**({'history':e.history} if isinstance(e,p.BoundNotMet) else {}))
    raise AssertionError('not rejected: '+name)
def doublefactorial(n):
    return math.prod(range(n,0,-2)) if n>0 else 1
n,A=p.sphere_rule(5);res=0.;count=0
for i in range(9):
 for j in range(9-i):
  for k in range(9-i-j):
   exact=0. if any(e%2 for e in (i,j,k)) else doublefactorial(i-1)*doublefactorial(j-1)*doublefactorial(k-1)/doublefactorial(i+j+k+1)
   actual=float(np.dot(A,n[:,0]**i*n[:,1]**j*n[:,2]**k));res=max(res,abs(actual-exact));count+=1
record('sphere_monomials_degree_le_8',res,monomials=count,Nmu=5)
label,S,R=p.fixtures()[0];d=p.moments(S,R,n,A);g=p.geometry(S,R)
Hq=np.einsum('n,ni,nj->ij',A*np.einsum('ni,ij,nj->n',n,np.eye(3)+S,n),n,n)
record('exact_H_and_noncommuting_M',max(float(np.max(np.abs(Hq-g['H']))),float(np.max(np.abs(d['M_quadrature']-g['M'])))))
_,S5,R5=p.fixtures()[-1];plan=p.select(S5,R5);rays,weights=p.sphere_rule(plan['selected']['Nmu']);isotropic=p.moments(S5,R5,rays,weights)
oracle=np.zeros((4,4));oracle[0,0]=.7;oracle[1:,1:]=.7*(np.eye(3)/3+2*S5/15)
assert plan['selected']['K']==0 and len(rays)==18
record('isotropic_G5_K0_18_ray_oracle',float(np.max(np.abs(isotropic['T']-oracle)))/.7)
zero=np.einsum('ni,ij,nj->n',np.array([[1.,0,0],[-1.,0,0]]),np.eye(3)+S5,np.array([[1.,0,0],[-1.,0,0]]))
record('source_actual_zeros_plus_minus_x',float(np.max(np.abs(zero))),limit=0.)
cap=rejected('G1_maxK0',lambda:p.select(S,R,maxK=0),p.BoundNotMet)
assert len(cap['history'])==1 and cap['history'][0]['bound_relative']>p.ANGULAR
checks.append(dict(group='cap_refusal',status='PASS',evidence=cap))
Z=np.zeros((3,3));I=np.eye(3);bad=[]
for name,s,r in [('nonfinite_S',Z+np.nan,I),('nonfinite_R',Z,I*np.inf),('complex_S',Z.astype(complex),I),('complex_R',Z,I.astype(complex)),('wrong_S_shape',np.zeros(3),I),('wrong_R_shape',Z,np.ones((2,3))),('asymmetric_S',np.array([[0,.1,0],[0,0,0],[0,0,0]]),I),('non_STF_S',.1*I,I),('negative_continuous_q',np.diag([-1.1,.5,.6]),I),('singular_R',Z,np.diag([0.,.6,.9])),('negative_determinant_R',Z,np.diag([-.5,.6,.9])),('condition_over_2',Z,np.diag([.4,.6,.9])),('outgoing_sigma_over_1',Z,1.01*I)]:
 bad.append(rejected(name,lambda s=s,r=r:p.validate(s,r)))
bad.append(rejected('negative_density',lambda:p.packets(S,R,n,A,-1.)))
bad.append(rejected('undefined_all_zero_mixture_relative',lambda:p.mixture_relative([0.,0.],[1.,1.],[1.,1.])))
bad.append(rejected('negative_mixture_coefficient',lambda:p.mixture_relative([1.,-1.],[1.,1.],[1.,1.])))
checks.append(dict(group='invalid_inputs_and_undefined_mixture',status='PASS',cases=bad,case_count=len(bad)))
# Positive mixture identity, including signed tensor entries, and zero-weight allocation.
record('positive_mixture_bound_identity',abs(p.mixture_relative([1.,.25,0.],[1e-9,2e-9,1.],[1.,2.,1.])-1e-9),limit=p.ROUND)
result=dict(status='PASS',script_kind='ONE_CUSTOM_SCRIPT',check_group_count=len(checks),groups=checks)
(ROOT/'results/TEST_RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(dict(status='PASS',check_groups=len(checks),sphere_monomials=count,invalid_cases=len(bad))))
