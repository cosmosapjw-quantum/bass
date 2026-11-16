#!/usr/bin/env python3
"""One bounded same-author hostile physics and replay check.
No simulated reviewers; no source-PASS inferred from process exit alone.
"""
import ast,hashlib,json,os,subprocess,sys
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
from collisions import *
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def check(v,msg):
 if not bool(v):raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 receipts=[]
 for opt in (False,True):
  cmd=[sys.executable]+(['-O'] if opt else [])+[str(HERE/'test_collisions.py')]
  p=subprocess.run(cmd,env=env,cwd=ROOT,capture_output=True,text=True,timeout=45)
  (HERE/('UNIT_OPTIMIZED.log' if opt else 'UNIT_NORMAL.log')).write_text(p.stdout+p.stderr)
  check(p.returncode==0,'analytic tests fail');receipts.append({'kind':'analytic_tests','optimized':opt,'cases':12,'exit':p.returncode})
 before={n:sha(HERE/n) for n in ('SPECTRAL_SOURCE_RESULTS.json','SPECTRAL_COMPTON_FIELDS.csv','GROUND_PHOTOIONIZATION.csv','PASSIVE_FIXED_XE_TEMPERATURE.csv','KERNEL_VERIFICATION.json')}
 for name in ('verify_sources_and_kernels.py','source_campaign.py'):
  p=subprocess.run([sys.executable,'-O',str(HERE/name)],env=env,cwd=ROOT,capture_output=True,text=True,timeout=120)
  (HERE/(name.replace('.py','')+'_OPTIMIZED.log')).write_text(p.stdout+p.stderr)
  check(p.returncode==0,'optimized science replay failed '+name)
  for n,h in before.items():check(sha(HERE/n)==h,'science replay changed '+n)
  receipts.append({'kind':'fresh_optimized_source_replay','program':name,'exit':0,'data_byte_exact':True})
 # Finite-boundary numerical number/energy moment checks, not just algebra labels.
 flux_cases=[]
 for b,eta,tau in [(0.,0.,1.),(.05,0.,.7),(.05,.7,1.2)]:
  x0,w0=frequency_grid(40);scale=np.sqrt((1+abs(b))/(1-abs(b)));x=x0*scale;wx=w0*scale
  mu,mw=gauss(40);mw=mw/2;g=1/np.sqrt(1-b*b);aa=g*(1+b*mu)
  y=x[:,None]*aa+eta;f=np.exp(-y)/(-np.expm1(-y));fp=-aa*f*(1+f);fpp=aa*aa*f*(1+f)*(1+2*f)
  pl=legvander(mu,3);mats=mw[:,None]*pl;nl=f@mats;npl=fp@mats
  B=np.sum(nl*nl*np.array([1.,-1.2,.5,-.3]),axis=1);Bp=2*np.sum(nl*npl*np.array([1.,-1.2,.5,-.3]),axis=1)
  n0=f@mw;n0p=fp@mw;n0pp=fpp@mw
  inner=tau*n0p+n0+B;innerp=tau*n0pp+n0p+Bp
  flux=x**4*inner;der=4*x**3*inner+x**4*innerp
  Ndot=float(np.sum(wx*der));Edot=float(np.sum(wx*x*der))
  U=float(np.sum(wx*x**3*n0));J=float(np.sum(wx*x**4*(n0+B)))
  check(abs(Ndot)<2e-9 and abs(Edot-(4*tau*U-J))<3e-9,'number/energy flux moment mismatch')
  flux_cases.append({'beta':b,'eta':eta,'Tm_over_Tn':tau,'number_flux_integral':Ndot,'energy_moment_residual':Edot-(4*tau*U-J)})
 # A different polarization-free recoil computation: azimuth quadrature of
 # the literal W(cosTheta), not the azimuth-averaged polynomial.
 mu,w=gauss(16);w=w/2;phi=2*np.pi*(np.arange(64)+.5)/64
 cost=mu[:,None,None]*mu[None,:,None]+np.sqrt(1-mu[:,None,None]**2)*np.sqrt(1-mu[None,:,None]**2)*np.cos(phi)
 Wbar=np.mean(.75*(1-cost)*(1+cost*cost),axis=2)
 f=np.exp(.4*mu)+.1*mu**2;literal=float((f*w)@Wbar@(f*w));mult=float(induced_multipoles(f,mu,w))
 check(abs(literal/mult-1)<3e-11,'literal 3-angle recoil mismatch')
 # Deliberately wrong absorption frame measure, applied on the same spectrum.
 T,b=3000.,.05;mu,w=gauss(48);g=1/np.sqrt(1-b*b);D=g*(1-b*mu)
 logR=np.array([photo_rate(T*d,0.,'HI',order=96)['log_rate_s'] for d in D])
 proper=float(logsumexp(logR+np.log(w/2)-2*np.log(D)))
 wrong=float(logsumexp(logR+np.log(w/2)))
 frame_error=float(np.expm1(wrong-proper));check(abs(frame_error)>.01,'missing aberration control not discriminating')
 c=compton_moments(.05);zero=compton_moments(0.)
 check(abs(zero['Tc_spontaneous_over_Tn']-1)>.03,'no-induced false equilibrium not detected')
 check(c['Tc_wrong_monopole_over_Tn']-c['Tc_over_Tn']>5e-5,'angular-induced collapse not detected')
 # Heating sign: positive for cold electrons and negative above T_C.
 cold=compton_heating(3000,.05,0.);hot=compton_heating(3000,.05,4000.)
 check(cold['electron_heat_W']>0 and hot['electron_heat_W']<0,'Compton heat sign wrong')
 # Half-order/angle tolerance and stable small-beta second-order behavior.
 asym=[]
 exact=2*np.pi**2/9-7/6
 for b in (.0005,.001,.002):
  coef=(compton_moments(b,order=40)['Tc_over_Tn']-1)/(b*b)
  check(abs(coef-exact)<3e-5,'small-beta asymptotic coefficient')
  asym.append({'beta':b,'coefficient':coef})
 # Deliberately invalid scalar/thermal/energy/fit-domain inputs.
 bad=[('superluminal',lambda:photo_rate(3000,1,'HI')),('nonfinite',lambda:photo_rate(3000,float('nan'),'HI')),('negative_temperature',lambda:photo_rate(-1,.05,'HI')),('beyond_fit',lambda:sigma_ev(1e5,'HI')),('negative_energy',lambda:sigma_ev(-1,'HI')),('negative_eta',lambda:compton_moments(0.,eta=-1)),('negative_Tm',lambda:compton_heating(3000,.05,-1))]
 negative=[]
 for name,call in bad:
  try:call()
  except ValueError:negative.append(name)
  else:raise RuntimeError('invalid input accepted '+name)
 for name in ('collisions.py','source_campaign.py','verify_sources_and_kernels.py','verify_final.py'):
  check(not any(isinstance(n,ast.Assert) for n in ast.walk(ast.parse((HERE/name).read_text()))),'bypassable science assert '+name)
 # No production mutation: lock current original BASS 9 inputs only.
 lock=json.loads((ROOT/'research/typeii_host_preflight_20261101/SOURCE_LOCK.json').read_text())['original_git_blobs_sha1']
 for rel,expect in lock.items():
  got=subprocess.check_output(['git','hash-object',rel],cwd=ROOT,text=True).strip();check(got==expect,'original BASS source changed '+rel)
 result={'analytic_test_executions':24,'source_Fortran_cases':24,'independent_flux_moment_cases':flux_cases,'literal_angle_vs_multipole_relative_gap':abs(literal/mult-1),'wrong_photo_frame_relative_error':frame_error,'omit_induced_Planck_Tc_relative_error':zero['Tc_spontaneous_over_Tn']-1,'collapse_induced_to_monopole_Tc_ratio_error':c['Tc_wrong_monopole_over_Tn']-c['Tc_over_Tn'],'small_beta_checks':asym,'invalid_cases_rejected':negative,'replay_receipts':receipts,'science_output_sha256':before,'original_BASS_blobs':len(lock),'same_author_hostile_review':'PERFORMED_NOT_INDEPENDENT_BLIND','native_subagent':'NOT_RUN','distinct_author_referee':'NOT_RUN','limits':['prescribed normal Planck field','leading nonrelativistic unpolarized Compton energy moment only','ground-state single-target photoionization only','no bound-free reverse/population detailed-balance network','fixed parent xe thermal experiment only','no new xe or optical depth history','momentum and Einstein backreaction not evolved']}
 (HERE/'VERIFICATION_AND_HOSTILE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ('science_output_sha256','replay_receipts')},indent=2))
if __name__=='__main__':main()
