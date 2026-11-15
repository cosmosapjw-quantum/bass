#!/usr/bin/env python3
"""Source FULL thermal-only Compton-spectrum intervention at fixed atom bath.
Zero lane reproduces PR334 both-clock outputs; spectral photoionization is not
silently substituted for effective n=2 atomic rates. All builds are isolated.
"""
from pathlib import Path
import importlib.util,json,os,subprocess,shutil,hashlib
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PAR=ROOT/'research/typeii_clock_interface_20261115'
spec=importlib.util.spec_from_file_location('parent_clocks',PAR/'native_experiment.py')
parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
owner=parent.owner;owner.RUN=HERE/'native_run/owner';owner.SRC=HERE/'native_run/original_source'
OUT=HERE/'outputs';OUT.mkdir(exist_ok=True)
def check(c,msg):
 if not bool(c):raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def replace(s,a,b):
 check(s.count(a)==1,'source anchor mismatch: '+a);return s.replace(a,b,1)
def build(refine):
 b=parent.build(refine)
 for n in ('radiation_adapter.c','radiation_adapter.h'):shutil.copyfile(HERE/n,b/n)
 h=(b/'history.c').read_text()
 for old,new in [('rec_Tmss','bass_scalar_Tmss'),('rec_dTmdlna','bass_scalar_dTmdlna'),('Tm_implicit','bass_scalar_Tm_implicit')]:
  h=replace(h,'double '+old+'(double z,','double '+new+'(double z,')
 h=replace(h,'#include "clock_adapter.h"','#include "clock_adapter.h"\n#include "radiation_adapter.h"')
 h=replace(h,'fabs(1.-Tm_output[iz-1]/cosmo->T0/(1.+z))','bass_spectral_tracking_lag(Tm_output[iz-1],z,cosmo->T0)')
 h+='\n'+(HERE/'spectral_thermal.c.txt').read_text();(b/'history.c').write_text(h)
 # Fail closed on a nonphysical source state before it can enter native FULL
 # radiation-history indexing. This adds no changed physical rates.
 atom=(b/'hydrogen.c').read_text()
 old_return=' return bass_legacy_dxHIIdlna(data,model,xe,xHII,nH,H,TM,TR,iz,z)*bass_reaction_scale(z);'
 guarded=' if(!isfinite(xe)||!isfinite(TM)||!isfinite(TR)||xe<0.||TM<=0.||TR<=0.){fprintf(stderr,"SPECTRAL_ADAPTER_ERROR: invalid atomic state z=%.17g xe=%.17g TM=%.17g\\n",z,xe,TM);exit(8);}'+'\n'+old_return
 atom=replace(atom,old_return,guarded);(b/'hydrogen.c').write_text(atom)
 sources=('hyrectools.c','helium.c','hydrogen.c','history.c','energy_injection.c','bass_proper_density.c','clock_adapter.c','radiation_adapter.c','mode_driver.c')
 cmd=['gcc','-O3','-std=gnu11','-I'+str(b)]+[str(b/n) for n in sources]+['-lm','-o',str(b/'spectral_compton')]
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=90);(b/'spectral_build.log').write_text(p.stdout+p.stderr)
 check(p.returncode==0,'spectral native compile: '+p.stderr[-2500:]);return b

def execute(b,refine,lane):
 wd=b/('spectral_'+lane);wd.mkdir(exist_ok=True)
 for f in owner.SRC.glob('*.dat'):
  link=wd/f.name
  if link.exists() or link.is_symlink():check(link.is_symlink() and link.resolve()==f.resolve(),'atomic input link drift')
  else:link.symlink_to(f)
 out=OUT/f'FULL_r{refine}_{lane}.dat';meta=OUT/f'FULL_r{refine}_{lane}.meta.json'
 env=dict(os.environ,BASS_CLOCK_LANE='both',BASS_CLOCK_TABLE=str(PAR/'CLOCK_GRID.dat'),
          BASS_SPECTRAL_LANE=lane,BASS_SPECTRAL_TABLE=str(HERE/'COMPTON_GRID.dat'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 H=owner.P1/'NATIVE_TYPEII_H_ARRAY_2248.dat';F=owner.P1/'TYPEII_PROPER_NH_FACTOR_2248.dat'
 p=subprocess.run([str(b/'spectral_compton'),str(H),str(F),str(out),str(meta)],cwd=wd,env=env,
    input=(owner.P0/'HYREC2_FLRW_INPUT_20261102.dat').read_bytes(),capture_output=True,timeout=120)
 (OUT/f'FULL_r{refine}_{lane}.log').write_bytes(p.stdout+p.stderr)
 check(p.returncode==0,'native spectral run failed '+lane+' exit='+str(p.returncode)+': '+p.stderr.decode(errors='replace')[-2500:])
 data=np.loadtxt(out);mi=json.loads(meta.read_text())
 check(data.shape==(8000,3) and np.isfinite(data).all() and np.min(data[:,1:])>0,'invalid native output')
 check(mi['model']==3 and abs(mi['dlna']-8.49e-5/refine)<1e-17,'wrong native mode/timestep')
 if lane=='zero':check(sha(out)==sha(PAR/f'outputs/FULL_r{refine}_both.dat'),'zero radiation adapter not parent byte-exact')
 print('NATIVE',refine,lane,'xe1100',data[6900,1],'Tm1100',data[6900,2],'Tm300',data[7700,2],flush=True)
 return {'refinement':refine,'lane':lane,'exit':0,'path':str(out.relative_to(HERE)),'sha256':sha(out),'H_sha256':sha(H),'nH_sha256':sha(F),'meta':mi}

def main():
 r=json.loads((HERE/'SPECTRAL_RESULTS.json').read_text());check(sha(HERE/'COMPTON_GRID.dat')==r['compton_grid_sha256'],'spectral grid source identity')
 owner.verify_source();runs=[];builds=[]
 for refine in (1,2):
  b=build(refine);builds.append({'refinement':refine,'files':{n:sha(b/n) for n in ('history.c','hydrogen.c','helium.c','clock_adapter.c','radiation_adapter.c','hydrogen.h','history.h')}})
  for lane in ('zero','moments','energy_scalar','monopole'):
   runs.append(execute(b,refine,lane))
   (HERE/'NATIVE_RUNS.json').write_text(json.dumps({'runs':runs,'builds':builds,'original_sources':owner.verify_source(),'radiation_photoionization_native':'NOT_COUPLED'},indent=2)+'\n')
 print('COMPTON_NATIVE_CAMPAIGN_COMPLETE',len(runs),flush=True)
if __name__=='__main__':main()
