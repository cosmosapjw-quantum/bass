#!/usr/bin/env python3
"""Controlled native FULL source interventions, not a full tilted radiation closure."""
from pathlib import Path
import importlib.util,sys,os,json,hashlib,subprocess,shutil
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PAR=ROOT/'research/typeii_hyrec_atommode_audit_20261102'
spec=importlib.util.spec_from_file_location('owner_modes',PAR/'native_modes.py');owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
owner.RUN=HERE/'native_run/owner';owner.SRC=HERE/'native_run/original_source'
OUT=HERE/'outputs';OUT.mkdir(exist_ok=True)
def check(c,msg):
 if not bool(c):raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def replace(s,a,b):
 check(s.count(a)==1,'source replacement mismatch: '+a);return s.replace(a,b,1)
def build(refine):
 b=owner.prepare('FULL',refine)
 for f in ('clock_adapter.c','clock_adapter.h'):shutil.copyfile(HERE/f,b/f)
 h=(b/'hydrogen.c').read_text();h=replace(h,'double rec_dxHIIdlna(','double bass_legacy_dxHIIdlna(')
 h='#include "clock_adapter.h"\n'+h
 h+='\ndouble rec_dxHIIdlna(HYREC_DATA *data,int model,double xe,double xHII,double nH,double H,double TM,double TR,unsigned iz,double z){\n return bass_legacy_dxHIIdlna(data,model,xe,xHII,nH,H,TM,TR,iz,z)*bass_reaction_scale(z);\n}\n'
 (b/'hydrogen.c').write_text(h)
 he=(b/'helium.c').read_text();he=replace(he,'double rec_helium_dxHeIIdlna(','double bass_legacy_helium_dxHeIIdlna(')
 he='#include "clock_adapter.h"\n'+he
 he+='\ndouble rec_helium_dxHeIIdlna(HYREC_DATA *data,double z,double xH1,double xHeII,double H){\n return bass_legacy_helium_dxHeIIdlna(data,z,xH1,xHeII,H)*bass_reaction_scale(z);\n}\n'
 (b/'helium.c').write_text(he)
 hist=(b/'history.c').read_text()
 for old,new in [('rec_Tmss','bass_legacy_Tmss'),('rec_dTmdlna','bass_legacy_dTmdlna'),('Tm_implicit','bass_legacy_Tm_implicit')]:
  hist=replace(hist,'double '+old+'(','double '+new+'(')
 hist=replace(hist,'#include "helium.h"','#include "helium.h"\n#include "clock_adapter.h"\ndouble Tm_implicit(double,double,double,REC_COSMOPARAMS*,double,double,double);')
 hist+='\n'+(HERE/'thermal_wrappers.c.txt').read_text();(b/'history.c').write_text(hist)
 cmd=['gcc','-O3','-std=gnu11','-I'+str(b)]+[str(b/n) for n in ('hyrectools.c','helium.c','hydrogen.c','history.c','energy_injection.c','bass_proper_density.c','clock_adapter.c','mode_driver.c')]+['-lm','-o',str(b/'two_clock')]
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=90);(b/'compile.log').write_text(p.stdout+p.stderr);check(p.returncode==0,'native compile: '+p.stderr[-3000:]);return b

def execute(b,refine,lane,H,F):
 wd=b/lane;wd.mkdir(exist_ok=True)
 for x in owner.SRC.glob('*.dat'):
  q=wd/x.name
  if q.exists() or q.is_symlink():check(q.is_symlink() and q.resolve()==x.resolve(),'atomic table identity')
  else:q.symlink_to(x)
 path=OUT/f'FULL_r{refine}_{lane}.dat';meta=OUT/f'FULL_r{refine}_{lane}.meta.json'
 env=dict(os.environ,BASS_CLOCK_LANE=lane,BASS_CLOCK_TABLE=str(HERE/'CLOCK_GRID.dat'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 p=subprocess.run([str(b/'two_clock'),str(H),str(F),str(path),str(meta)],cwd=wd,env=env,input=(owner.P0/'HYREC2_FLRW_INPUT_20261102.dat').read_bytes(),capture_output=True,timeout=120)
 (OUT/f'FULL_r{refine}_{lane}.log').write_bytes(p.stdout+p.stderr)
 if p.returncode!=0:return {'refinement':refine,'lane':lane,'exit':p.returncode,'status':'FAILED','stderr':p.stderr.decode(errors='replace')[-2000:]}
 a=np.loadtxt(path);mi=json.loads(meta.read_text());check(a.shape==(8000,3) and np.isfinite(a).all() and np.min(a[:,1:])>0,'native history invalid')
 check(mi['model']==3 and abs(mi['dlna']-8.49e-5/refine)<1e-16,'wrong FULL configuration')
 print('NATIVE',refine,lane,'xe1100',a[6900,1],'Tm300',a[7700,2],flush=True)
 return {'refinement':refine,'lane':lane,'exit':0,'path':str(path.relative_to(HERE)),'sha256':sha(path),'H_sha256':sha(H),'nH_sha256':sha(F),'meta':mi}

def campaign():
 owner.verify_source();clock=json.loads((HERE/'SOURCE_FIELDS.json').read_text());check(sha(HERE/'CLOCK_GRID.dat')==clock['clock_grid_sha256'],'clock grid drift')
 H=owner.P1/'NATIVE_TYPEII_H_ARRAY_2248.dat';F=owner.P1/'TYPEII_PROPER_NH_FACTOR_2248.dat';table=np.loadtxt(HERE/'CLOCK_GRID.dat');z=np.arange(2248)*8000/2248
 factor=1/np.sqrt(1-table[:,0]**2);factor[z>=1700]=1
 globalH=HERE/'NAIVE_GLOBAL_GAMMA_H.dat';np.savetxt(globalH,np.loadtxt(H)*factor,fmt='%.17e')
 runs=[];builds=[]
 for ref in (1,2):
  b=build(ref);builds.append({'refinement':ref,'files':{n:sha(b/n) for n in ('history.c','hydrogen.c','helium.c','clock_adapter.c','mode_driver.c','history.h','hydrogen.h')}})
  for lane in ('legacy','reaction','thermal','both','zero','global'):
   r=execute(b,ref,lane,globalH if lane=='global' else H,F);runs.append(r)
   (HERE/'NATIVE_RUNS.json').write_text(json.dumps({'runs':runs,'builds':builds,'original_sources':owner.verify_source()},indent=2)+'\n')
   check(r['exit']==0,'native source failure: '+str(r))
  baseline=np.loadtxt(OUT/f'FULL_r{ref}_legacy.dat');prior=np.loadtxt(PAR/f'outputs/FULL_r{ref}_TypeII.dat');zero=OUT/f'FULL_r{ref}_zero.dat'
  check(sha(zero)==sha(OUT/f'FULL_r{ref}_legacy.dat'),'zero clock adapter not byte-identical')
  check(np.max(abs(baseline-prior))<1e-9,'legacy differs from parent')
 print('NATIVE_CLOCK_CAMPAIGN_COMPLETE',len(runs),flush=True)
if __name__=='__main__':campaign()
