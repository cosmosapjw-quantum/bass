"""Exact discrete electron-history tangent of original BASS KM2N once-scattered Ly-alpha P8 field.

BASS-source-conditional: frozen Einstein/P8 geometry, electrons' bulk velocity, initial
Ly-alpha emission/source photons and chemical history. We perturb only the positive
Thomson electron opacity ν(u)=n_H x_e σ_T c Tstar, including both angularly-distinct
incoming and outgoing optical histories and gain at the collision edge.

40 per-panel piecewise constant δlnν basis, with left-limit convention ν(t_j)=ν_{j-1}.
The original 8-point Gauss optical increments and Simpson source grid are preserved.
Not actual REI x_e(t), not all-orders CMB, not a dynamical source-history IVP.
"""
from __future__ import annotations
import csv,gzip,hashlib,json,math,io
from pathlib import Path
import numpy as np
from restore_source import ORIGINAL_SHA,HEAD
ROOT=Path(__file__).resolve().parent
INPUTS=ROOT/'source_inputs'
OUT=ROOT/'results'
N_PANELS=40
N_GAUSS=8
SNAPSHOTS=(8,16,24,32,40)
THOMSON_ALPHA=3.0/(8*math.pi)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def assert_true(ok,msg):
 if not ok:raise AssertionError(msg)
def original(gl):
 assert_true(gl in (12,16),'unsupported original angular quadrature')
 names=[f'KM2K_PACKETS_GL{gl}_GLT8.npz',f'KM2L_THOMSON_OPTICAL_GL{gl}_GLT8.npz',f'KM2N_FIRST_SOURCE_LEDGER_GL{gl}.npz',f'KM2N_ONCE_POL_SCREEN_GL{gl}_U40.npz']
 for name in names:assert_true(sha(INPUTS/name)==ORIGINAL_SHA[name],'original byte identity '+name)
 parts=[]
 for name in names:
  with np.load(INPUTS/name,allow_pickle=False) as f:parts.append({k:f[k].copy() for k in f.files})
 p,o,L,screen=parts
 assert_true(len(p['sample_times'])==320 and o['hazard_nodes'].shape==(320,2*gl*gl),'physical source ray shape')
 assert_true(L['F'].shape==(41,2*gl*gl,3,2) and L['Me'].shape==(41,1200,3,3),'original P8 screen shape')
 assert_true(np.max(abs(o['tau_edges']-L['tau']))<1e-12,'original electron opacity owner mismatch')
 assert_true(np.max(abs(o['hazard_edges']-L['nu'][:,None]*L['D']))<3e-11,'live electron hazard mismatch')
 assert_true(np.all(np.diff(o['tau_edges'],axis=0)>0),'non-positive optical clock')
 assert_true(np.all(np.isfinite(p['source_packets'])) and np.all(p['source_packets']>=0),'negative photon source')
 return p,o,L,screen

def photon_moments_at_j(p,o,L,j):
 """Photon moments and 40 panelwise *incoming attenuation losses* at one real scatter edge."""
 NG=N_GAUSS;N=len(L['D'][j]); num=j*NG
 pre=(L['tau'][j][None]-o['tau_nodes'][:num])
 assert_true(np.min(pre)>=-1e-12,'causal optical pre-history')
 red=L['mu'] # same original independent frequency drift in packet's Rend
 R=p['Rend'][j][None]-p['Rnode'][:num]
 assert_true(np.min(R)>=-1e-12,'causal redshift')
 flux=p['source_packets'][:num]*np.exp(-4*R-np.maximum(pre,0))
 emit=p['sample_times'][:num]
 F=L['F'][j];weight=L['w'][j]*L['D'][j]**2
 Proj=np.einsum('nac,nbc->nab',F,F,optimize=True)
 def moment(q):return .5*np.einsum('n,nab->ab',q*weight,Proj,optimize=True)
 flux_sum=flux.sum(axis=0); emit_sum=np.einsum('i,in->n',emit,flux)
 Mat=moment(flux_sum); MatEmit=moment(emit_sum)
 parent=L['Me'][j].sum(axis=0)
 gap=float(np.max(abs(Mat-parent))/max(np.max(abs(parent)),1e-300))
 assert_true(gap<3e-12,'original source electron frame moment mismatch '+str(gap))
 dMat=np.zeros((N_PANELS,3,3));dMatEmit=np.zeros_like(dMat)
 for m in range(j):
  tau_m=o['tau_edges'][m+1]-o['tau_edges'][m]
  prefix=flux[:NG*m]
  low=NG*m;high=low+NG
  sub=flux[low:high]
  remainder=o['tau_edges'][m+1][None]-o['tau_nodes'][low:high]
  assert_true(np.min(remainder)>-1e-12,'invalid panel packet optical ordering')
  loss=tau_m*prefix.sum(axis=0)+np.einsum('in,in->n',sub,remainder)
  loss_emit=tau_m*np.einsum('i,in->n',emit[:low],prefix)+np.einsum('i,in,in->n',emit[low:high],sub,remainder)
  dMat[m]=moment(loss);dMatEmit[m]=moment(loss_emit)
 return Mat,MatEmit,dMat,dMatEmit,gap

def screen_transform(F,M):
 if M.ndim==2:return np.einsum('nac,ab,nbd->ncd',F,M,F,optimize=True)
 return np.einsum('nac,mab,nbd->mncd',F,M,F,optimize=True)

def core(gl,k,p,o,L,moments,derivatives=True):
 """Return baseline I,Q,U and 40 directional electron-history Fréchet derivatives.

 Collision at right edge j uses left limit electron history panel m=j-1.
 This boundary convention is a discrete model choice and is not a REI time map.
 """
 N=2*gl*gl; U=float(L['time'][k]); width=U/k
 sw=np.array([1 if j in (0,k) else (4 if j%2 else 2) for j in range(k+1)])*width/3.
 wobs=L['w'][k]
 B=np.zeros((N,2,2));Bsc=np.zeros_like(B);Bem=np.zeros_like(B)
 dB=np.zeros((N_PANELS,N,2,2));dBsc=np.zeros_like(dB);dBem=np.zeros_like(dB)
 for j in range(1,k+1):
  Mat,MatEmit,dMat,dMatEmit,gap=moments[j]
  F=L['F'][j];D=L['D'][j];rat=L['mu'][k]/L['mu'][j]
  post=o['tau_edges'][k]-o['tau_edges'][j]
  assert_true(np.min(post)>=-1e-12 and np.min(rat)>0,'causal post-scattering source')
  fac=THOMSON_ALPHA*sw[j]*L['nu'][j]*rat**4*np.exp(-np.maximum(post,0))*D**(-3)
  proj=screen_transform(F,Mat);projE=screen_transform(F,MatEmit)
  Bj=fac[:,None,None]*proj;Ej=fac[:,None,None]*projE
  B+=Bj;Bsc+=float(L['time'][j])*Bj;Bem+=Ej
  if derivatives:
   loss=screen_transform(F,dMat);lossEmit=screen_transform(F,dMatEmit)
   outTau=np.zeros((N_PANELS,N))
   for m in range(j,k):outTau[m]=o['tau_edges'][m+1]-o['tau_edges'][m]
   selector=np.zeros(N_PANELS);selector[j-1]=1
   coeff=selector[:,None]-outTau
   dBj=fac[None,:,None,None]*(coeff[:,:,None,None]*proj[None]-loss)
   dEj=fac[None,:,None,None]*(coeff[:,:,None,None]*projE[None]-lossEmit)
   dB+=dBj;dBsc+=float(L['time'][j])*dBj;dBem+=dEj
 return dict(gl=gl,k=k,U=U,wobs=wobs,B=B,Bsc=Bsc,Bem=Bem,dB=dB,dBsc=dBsc,dBem=dBem)

def obs(q):
 w=q['wobs'];B=q['B'];d=q['dB'];I=np.trace(B,axis1=-2,axis2=-1)
 Q=B[:,0,0]-B[:,1,1];U=B[:,0,1]+B[:,1,0]
 Lray=np.hypot(Q,U)
 if np.min(I)<=0:raise ArithmeticError('negative original tagged photon energy')
 skyI=float(w@I);skyL=float(w@Lray);P=skyL/skyI
 dI=np.trace(d,axis1=-2,axis2=-1)
 dQ=d[:,:,0,0]-d[:,:,1,1];dU=d[:,:,0,1]+d[:,:,1,0]
 mask=Lray>1e-12*np.max(Lray)
 assert_true(np.all(mask),'screen polarization degeneration: derivative undefined, requires Q/U field only')
 dL=(Q[None,:]*dQ+U[None,:]*dU)/Lray[None,:]
 dIsky=dI@w;dLsky=dL@w
 dP=(dLsky-P*dIsky)/skyI
 sc=np.trace(q['Bsc'],axis1=-2,axis2=-1);em=np.trace(q['Bem'],axis1=-2,axis2=-1)
 meanSc=float(w@sc/skyI);meanEm=float(w@em/skyI)
 dMeanSc=(np.trace(q['dBsc'],axis1=-2,axis2=-1)@w -meanSc*dIsky)/skyI
 dMeanEm=(np.trace(q['dBem'],axis1=-2,axis2=-1)@w -meanEm*dIsky)/skyI
 return dict(sky_energy=skyI,polarization_fraction=P,mean_scatter=meanSc,mean_emission=meanEm,
             dI=dI,dQ=dQ,dU=dU,dIsky=dIsky,dP=dP,dMeanSc=dMeanSc,dMeanEm=dMeanEm,
             mean_ray_dI=np.mean(dI,axis=1),w=w,nr=len(w),U=q['U'],nobs=q['gl'])

def exact_finite(gl,k,p,o,L,mode,epsilon):
 """Direct finite perturbation of original photon-screen operator, independent of tangent implementation."""
 N=2*gl*gl; width=L['time'][k]/k
 sw=np.array([1 if j in (0,k) else (4 if j%2 else 2) for j in range(k+1)])*width/3.
 B=np.zeros((N,2,2));Bsc=np.zeros_like(B);Bem=np.zeros_like(B)
 for j in range(1,k+1):
  num=j*N_GAUSS
  incoming=o['tau_edges'][j][None]-o['tau_nodes'][:num]
  if mode=='uniform':loss=incoming;local=1.;post=o['tau_edges'][k]-o['tau_edges'][j]
  else:
   m=int(mode); loss=np.zeros_like(incoming)
   if m<j:
    low=m*N_GAUSS;high=low+N_GAUSS
    loss[:low]=o['tau_edges'][m+1]-o['tau_edges'][m]
    loss[low:high]=o['tau_edges'][m+1]-o['tau_nodes'][low:high]
   local=1. if m==j-1 else 0.
   post=o['tau_edges'][m+1]-o['tau_edges'][m] if j<=m<k else np.zeros(N)
  red=p['Rend'][j][None]-p['Rnode'][:num]
  flux=p['source_packets'][:num]*np.exp(-4*red-incoming-epsilon*loss)
  F=L['F'][j];P=np.einsum('nac,nbc->nab',F,F,optimize=True);w=L['w'][j]*L['D'][j]**2
  Mat=.5*np.einsum('n,nab->ab',w*flux.sum(axis=0),P,optimize=True)
  MatEmit=.5*np.einsum('n,nab->ab',w*np.einsum('i,in->n',p['sample_times'][:num],flux),P,optimize=True)
  pref=THOMSON_ALPHA*sw[j]*L['nu'][j]*(1+epsilon*local)*(L['mu'][k]/L['mu'][j])**4*np.exp(-(o['tau_edges'][k]-o['tau_edges'][j])-epsilon*post)*L['D'][j]**(-3)
  Bj=pref[:,None,None]*screen_transform(F,Mat)
  B+=Bj;Bsc+=L['time'][j]*Bj;Bem+=pref[:,None,None]*screen_transform(F,MatEmit)
 return dict(B=B,Bsc=Bsc,Bem=Bem,wobs=L['w'][k],U=L['time'][k])

def obs_finite(q):
 B=q['B'];w=q['wobs'];I=np.trace(B,axis1=-2,axis2=-1)
 P=float(w@np.hypot(B[:,0,0]-B[:,1,1],B[:,0,1]+B[:,1,0])/(w@I))
 total=float(w@I)
 return np.asarray([total,P,float(w@np.trace(q['Bsc'],axis1=-2,axis2=-1)/total),float(w@np.trace(q['Bem'],axis1=-2,axis2=-1)/total)])

def finite_tests(gl,p,o,L,answers,eps=1e-5):
 r=[]
 for mode in ['uniform',0,15,39]:
  plus=obs_finite(exact_finite(gl,40,p,o,L,mode,eps));minus=obs_finite(exact_finite(gl,40,p,o,L,mode,-eps))
  fd=(plus-minus)/(2*eps)
  res=answers[40];out=obs(res)
  if mode=='uniform':pred=np.array([out['dIsky'].sum(),out['dP'].sum(),out['dMeanSc'].sum(),out['dMeanEm'].sum()])
  else:pred=np.array([out['dIsky'][mode],out['dP'][mode],out['dMeanSc'][mode],out['dMeanEm'][mode]])
  abs_error=np.abs(pred-fd);relative=abs_error/np.maximum(np.abs(pred),1e-24)
  assert_true(abs_error[0]/out['sky_energy']<2e-9,f'finite diff rho failed {gl} {mode} {abs_error[0]}')
  assert_true(np.max(abs_error[1:])<2e-9,f'finite diff physical time/pol failed {gl} {mode} {abs_error}')
  r.append(dict(gl=gl,mode=str(mode),predicted=pred.tolist(),finite_difference=fd.tolist(),abs_error=abs_error.tolist(),rel_error=relative.tolist()))
 return r

def write_csv_gz(path,header,rows):
 # Fixed mtime and no original file name: exact gzip reproduction in clean extractions.
 with Path(path).open('wb') as binary:
  with gzip.GzipFile(fileobj=binary,mode='wb',filename='',mtime=0,compresslevel=6) as zipped:
   with io.TextIOWrapper(zipped,encoding='utf8',newline='') as text:
    wr=csv.writer(text);wr.writerow(header);wr.writerows(rows)

def run(output=OUT):
 output=Path(output);output.mkdir(parents=True,exist_ok=True)
 records=[];ray_rows=[];cases=[];finite=[];counts={}
 for gl in (12,16):
  p,o,L,screen=original(gl);moment={j:photon_moments_at_j(p,o,L,j) for j in range(1,41)}
  answers={}
  for k in SNAPSHOTS:
   calc=core(gl,k,p,o,L,moment)
   answers[k]=calc;out=obs(calc)
   ref=json.loads((INPUTS/'KM2N_ONCE_SCATTER_REAL.json').read_text())['cases'][f'GL{gl}']['snapshots'][SNAPSHOTS.index(k)]
   gap=abs(out['sky_energy']/ref['rho_exactly_one']-1)
   assert_true(gap<2e-12,f'original Einstein BASS photon rho mismatch {gl}/{k}: {gap}')
   polgap=abs(out['polarization_fraction']-ref['mean_linear_polarization'])
   assert_true(polgap<2e-12,f'original polarized field mismatch {gl}/{k}: {polgap}')
   if k==40:
    parent=screen['screen_bolometric_first_one']
    screenerr=float(np.max(abs(calc['B']-parent))/max(float(np.max(abs(parent))),1e-300))
    assert_true(screenerr<2e-12,f'original full screen not reproduced {gl}: {screenerr}')
   else:screenerr=None
   for m in range(k):
    fields=(f'GL{gl}',k,float(L['time'][k]),m,float(L['time'][m]),float(L['time'][m+1]),float(out['sky_energy']),
       float(out['dIsky'][m]),float(out['dIsky'][m]/out['sky_energy']),float(out['polarization_fraction']),float(out['dP'][m]),
       float(out['mean_emission']),float(out['dMeanEm'][m]),float(out['mean_scatter']),float(out['dMeanSc'][m]))
    records.append(fields)
    for j in range(len(out['w'])):
     ray_rows.append((f'GL{gl}',k,m,j,float(L['n'][k,j,0]),float(L['n'][k,j,1]),float(L['n'][k,j,2]),float(out['w'][j]),
        float(out['dI'][m,j]),float(out['dQ'][m,j]),float(out['dU'][m,j])))
   cases.append(dict(gl=gl,k=k,observer_u=float(L['time'][k]),original_sky_energy=float(out['sky_energy']),
            original_mean_linear_pol=float(out['polarization_fraction']),original_mean_scatter_u=float(out['mean_scatter']),
            original_mean_emission_u=float(out['mean_emission']),original_rho_relative_gap=float(gap),
            original_polarization_absolute_gap=float(polgap),original_screen_relative_gap=screenerr,
            panel_count=k,sky_uniform_energy_derivative=float(np.sum(out['dIsky'])),
            sky_uniform_energy_elasticity=float(np.sum(out['dIsky'])/out['sky_energy']),
            sky_uniform_polarization_derivative=float(np.sum(out['dP'])),
            sky_uniform_mean_emit_derivative=float(np.sum(out['dMeanEm'])),
            sky_uniform_mean_scatter_derivative=float(np.sum(out['dMeanSc']))))
   print('BASS_ORIGINAL_POL_REI_IGM',gl,k,'rho',out['sky_energy'],'pol',out['polarization_fraction'],'electron_elasticity',sum(out['dIsky'])/out['sky_energy'],flush=True)
  finite.extend(finite_tests(gl,p,o,L,answers))
  counts[f'GL{gl}']=dict(original_ray_count=2*gl*gl,observed_snapshots=len(SNAPSHOTS),active_panels=sum(SNAPSHOTS),
                         ray_panel_records=(2*gl*gl)*sum(SNAPSHOTS))
 hed=['GL','observer_k','u_obs','electron_panel','panel_start_u','panel_end_u','rho_first_one','drho_dlnne_panel','dlogrho_dlnne_panel','pol_fraction','dpol_dlnne_panel','mean_emit_u','dmean_emit_dlnne_panel','mean_scatter_u','dmean_scatter_dlnne_panel']
 write_csv_gz(output/'KM2_REI_POLARIZED_PHOTON_HISTORY_SKY_RESPONSE.csv.gz',hed,records)
 write_csv_gz(output/'KM2_REI_POLARIZED_PHOTON_HISTORY_RAY_RESPONSE.csv.gz',
 ['GL','observer_k','electron_panel','ray','nx','ny','nz','angle_weight','dI_dlnne','dQ_dlnne','dU_dlnne'],ray_rows)
 report={'schema':'bass.rei_igm.original_km2_first_scattered_polarized_electron_history_tangent.v1',
     'asof_kst':'2026-11-01','source_owner_pr':297,'source_owner_head':HEAD,'physical_parent_pr':309,
     'model':'Einstein-Bianchi I-P8-Peebles-KM2N exactly-one Thomson-scattered tagged Ly-alpha',
     'source_only_no_new_ivps':True,'clock':'u=t/Tstar; original 40 panels, original Gaussian emission nodes',
     'perturbation':'40 piecewise-constant electron opacity modes; scattering at original right edge uses its preceding-panel left limit',
     'fixed_owner_fields':['Einstein background','velocity/boost','transported screens','emission source packets','full original chemical history','fixed nH'],
     'varied_owner_field':'Thomson hazard nu=nH xe sigma_T c Tstar and pre/post optical ages',
     'matrix_transport':'Separate incoming ray a and outgoing ray b attenuation; full P8 3x3 gain and 2x2 polarization screens',
     'ray_response_rows':len(ray_rows),'sky_response_rows':len(records),'cases':cases,'counts':counts,'finite_difference_controls':finite,
     'source_lock':dict(head=HEAD,files=ORIGINAL_SHA),
     'BASS_upper':'9/15 scoped/source-mapped','new_BASS_upper_nodes':0,'REI_central':'28/88 reported','new_REI_nodes':0,
     'original_REI_first_interval':'BLOCKED at 160/131072 ticks; no source-matched H/He timeline accepted',
     'REI_history_injected':False,'new_observed_CMB_data':False,'claimed_all_orders_CMB':False,
     'original_Einstein_P8_Peebles_IVPs_new':0,'production_ready':False,'merge_ready':False,'auto_next':False}
 (output/'KM2_REI_POLARIZED_PHOTON_HISTORY_RESULT.json').write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
 return report

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--out',default=OUT,type=Path)
 opts=parser.parse_args();run(opts.out)
