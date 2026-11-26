import json,hashlib,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;B=D.parents[1];H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(Path(p).read_text())
for n in ('physics_build','bridge_build','bridge_final_build','exact','lib_tests','regression','analyze_live'):assert int((D/(n+'.exit')).read_text())==0,n
for f in ('PHYSICS.sha256','BRIDGE_FINAL.sha256'):
 for l in (D/f).read_text().splitlines():
  h,p=l.split(maxsplit=1);assert sha(B/p)==h,p
assert sha(H/'bass_r118c2z_bridge_v1')==(D/'BRIDGE_V1.sha256').read_text().split()[0]
for n in ('angle','joint'):assert int((D/('live_'+n+'_v1.exit')).read_text())!=0
for n in ('base','time','freq'):
 assert sha(H/('bass_r118c2z_'+n)/'history.csv')==sha(H/('bass_r118c2z_final_'+n)/'history.csv')
 assert sha(H/('bass_r118c2z_'+n)/'error_components.csv')==sha(H/('bass_r118c2z_final_'+n)/'error_components.csv')
phy={}
for n in ('a40','a20','a10','a05','p20','p10','lrs','time','ell'):
 assert int((D/(n+'.exit')).read_text())==0,n
 p=D/(n+'.csv');r=np.genfromtxt(p,names=True,delimiter=',')
 assert len(r)==15 and np.all(np.isfinite(r.view(float)))
 b=r['re']+1j*r['im'];t=r['template_re']+1j*r['template_im']
 norm=float(np.linalg.norm(b));tn=float(np.linalg.norm(t));c=np.vdot(t,b)/np.vdot(t,t) if tn>1e-12 else 0j
 phy[n]=dict(sha=sha(p),norm=norm,template_norm=tn,coefficient_re=float(c.real),coefficient_im=float(c.imag),orthogonal_relative=float(np.linalg.norm(b-c*t)/norm))
v=np.array([phy[n]['norm'] for n in ('a40','a20','a10','a05')]);power=np.log2(v[:-1]/v[1:])
assert max(abs(power-5))<.04 and phy['lrs']['norm']<1e-13
assert phy['a05']['orthogonal_relative']<phy['a10']['orthogonal_relative']<phy['a20']['orthogonal_relative']<phy['a40']['orthogonal_relative']
assert abs(phy['p20']['template_norm']/phy['a20']['template_norm']-abs(np.cos(.9)))<1e-12
assert abs(phy['time']['norm']/phy['a20']['norm']-1)<1e-5 and abs(phy['ell']['norm']/phy['a20']['norm']-1)<.002
x=j(D/'EXACT.json');assert x['tensor_norm_coefficient']=='18/1001' and x['sphere_mean_coefficient']=='32/715715'
live=j(D/'LIVE.json');assert live['status']=='SCOPED_LIVE_AXIS_AND_TRANSIENT'
for n,c in live['cases'].items():
 p=Path(c['raw'])
 for f,h in c['hashes'].items():assert sha(p/f)==h
assert live['late_status']=='COMPLETE' and live['cases']['late_tail']['terminal']['z']==17.5
assert live['cases']['late_tail']['return_']['accepted']=='4464'
for n in ('time_freq_time','time_angle_time','freq_time_joint','angle_time_joint'):assert live['comparisons'][n]['same_grid']
assert live['early']['max_shared_J0_relative']<1e-6
nt=sum(map(int,re.findall(r'test result: ok\. (\d+) passed;', (D/'regression.log').read_text())));assert nt==11
assert '189 passed; 0 failed' in (D/'lib_tests.log').read_text()
out=dict(status='PASS_SCOPED_ODD_MAGNETIC_B7_LIVE_AXES_LATE_TRANSIENT',parent='0f59a54f15c06755e6b9bcb23e3a2743bdeff0fd',rei_commit='8275bf964def38b30d0504a4612c8f2292a2612f',physics=phy,quintic_powers=power.tolist(),exact=x,live=live,lib_tests=189,targeted_tests=nt,production_admission='HOLD_FULL_INTERVAL_AND_PHYSICAL_SECONDARY_SPECTRA',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],'powers',power,'late accepted',live['cases']['late_tail']['return_']['accepted'])
