"""Independent ray analytic attenuation, no Rust transport or spectral moments.
FLRW, stationary or prescribed linearly interpolated beta, constant source.
Compute exact continuum frequency-bin number averages and a semidiscrete
finite-volume generator reference (average opacity, no repeated remapping).
"""
import csv,sys,pathlib,json,math
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import ndtr,gamma
from scipy.integrate import quad
root=pathlib.Path(sys.argv[1]);summary=json.loads((root/'RESULTS.json').read_text())
xg,wg=leggauss(24);tg,tw=leggauss(24)
result=[]
def load(path):return np.genfromtxt(path,names=True,delimiter='\t')
for q in summary['cases']:
 name=q['case']
 if not name.startswith(('monotone_f','turn_f','turn_t','narrow_line')):continue
 assert q['status']=='PASS_SCOPED'
 center,sigma,strength,S=q['line'];out=root/name
 v=load(out/'frequency_line_velocity.tsv');r=load(out/'frequency_rays.tsv')
 f=load(out/'frequency_cells.tsv');nr=len(r);nf=q['bins'];f=f.reshape(nr,nf)
 a=f['u_lo'][0];b=f['u_hi'][0];w3=np.exp(3*a)*np.expm1(3*(b-a))/3
 u=(a[:,None]+b[:,None])/2+(b-a)[:,None]*xg/2
 w=(b-a)[:,None]*wg/2*np.exp(3*u)
 init=1/np.expm1(np.exp(u));init_avg=np.sum(w*init,axis=1)/w3
 end=float(v['eta'][-1]);ws=r['weight']/(4*np.pi)
 t=[];dt=[];bs=[]
 for l,h,bl,bh in zip(v['eta'][:-1],v['eta'][1:],v['beta_z'][:-1],v['beta_z'][1:]):
  t.append((l+h)/2+(h-l)*tg/2);dt.append((h-l)*tw/2);bs.append((bl+bh)/2+(bh-bl)*tg/2)
 t=np.concatenate(t);dt=np.concatenate(dt);bs=np.concatenate(bs)
 err=0.;err_fv=0.;signal=0.;max_bin=0.;num=0.;fv_num=0.
 for i,mu in enumerate(r['e_z']):
  if np.max(np.abs(bs))==0.:
   tau=strength*(ndtr((u-center)/sigma)-ndtr((u-end-center)/sigma))
  else:
   D=(1-mu*bs)/np.sqrt(1-bs**2)
   shift=-t+np.log(D);tau=np.empty(u.size)
   flat=u.ravel()
   for start in range(0,len(flat),2048):
    z=(flat[start:start+2048,None]+shift[None,:]-center)/sigma
    tau[start:start+2048]=strength/(sigma*np.sqrt(2*np.pi))*(np.exp(-z*z/2)@(dt*D))
   tau=tau.reshape(u.shape)
  exact=S+(init-S)*np.exp(-tau)
  cell=np.sum(w*exact,axis=1)/w3
  avg_tau=np.sum(w*tau,axis=1)/w3
  fv=S+(init_avg-S)*np.exp(-avg_tau)
  actual=f['f_xx'][i]+f['f_yy'][i]+f['f_zz'][i]
  err+=ws[i]*np.sum(w3*np.abs(actual-cell));err_fv+=ws[i]*np.sum(w3*np.abs(actual-fv))
  signal+=ws[i]*np.sum(w3*np.abs(init_avg-cell))
  max_bin=max(max_bin,float(np.max(np.abs(actual-cell))))
  num+=ws[i]*np.sum(w3*cell)/2.4041138063191885
  fv_num+=ws[i]*np.sum(w3*fv)/2.4041138063191885
 row=dict(case=name,bins=nf,n_steps=len(load(out/'frequency_history.tsv'))-1,relative_line_signal_l1=err/signal,relative_fv_line_signal_l1=err_fv/signal,max_cell_occupation_abs_error=max_bin,exact_number=num,exact_fv_number=fv_num,actual_number=q['last']['number_centered'],absolute_number_error=abs(q['last']['number_centered']-num),absolute_fv_number_error=abs(q['last']['number_centered']-fv_num))
 result.append(row)
 print(name,'L1/signal',row['relative_line_signal_l1'],'FV',row['relative_fv_line_signal_l1'],'Nerr',row['absolute_number_error'],flush=True)
# Tangency integral has sigma^-1/2, not 1/|zeta'|. Rescale quadrature
# variable to avoid missing the shrinking support.
turn=[]
for sigma in (1e-1,1e-2,1e-3,1e-4,1e-6):
 a=2.;scale=math.sqrt(sigma/a)
 actual=quad(lambda t:math.exp(-0.5*t**4),-20,20,epsabs=1e-12,epsrel=1e-12)[0]*scale/(sigma*math.sqrt(2*math.pi))
 exact=gamma(.25)/(2**1.25*math.sqrt(math.pi*a*sigma))
 assert abs(actual/exact-1)<1e-12
 turn.append(dict(sigma=sigma,optical_depth_per_Dkappa=actual,scaled=actual*math.sqrt(sigma),relative_error=abs(actual/exact-1)))
print('turn scaling',turn)
(root/'LINE_ORACLE.json').write_text(json.dumps(dict(cases=result,tangency=turn),indent=2)+'\n')
