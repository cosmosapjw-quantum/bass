#!/usr/bin/env python3
from pathlib import Path
import argparse,datetime,hashlib,json,os,time,traceback
import numpy as np
from bass_r3.qctrl_r4 import run_axial_mresolved,run_offaxis

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser()
 for k,t in [('energy',float),('b',float),('nr',int),('rmax',float),('lmax',int),('dt',float),('zmax',float),('nangle',int)]:
  ap.add_argument('--'+k,type=t,required=True)
 ap.add_argument('--out',type=Path,required=True)
 ap.add_argument('--save-arrays',action='store_true')
 a=ap.parse_args()
 a.out.mkdir(parents=True,exist_ok=True)
 if (a.out/'COMPLETE').exists():
  print('already complete'); return
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 t=time.perf_counter(); status='failed'; err=None
 try:
  kw=dict(nr=a.nr,rmax=a.rmax,lmax=a.lmax,dt=a.dt,zmax=a.zmax,energy_keV=a.energy,nangle=a.nangle)
  if a.b==0: res,arr=run_axial_mresolved(**kw)
  else: res,arr=run_offaxis(**kw,b=a.b)
  res['runtime_s']=time.perf_counter()-t
  (a.out/'result.json').write_text(json.dumps(res,indent=2)+'\n')
  if a.save_arrays: np.savez_compressed(a.out/'arrays.npz',**arr)
  status='completed'
 except Exception:
  err=traceback.format_exc(); (a.out/'stderr.txt').write_text(err); raise
 finally:
  end=datetime.datetime.now(datetime.timezone.utc).isoformat()
  files={}
  for p in a.out.iterdir():
   if p.is_file() and p.name not in ('receipt.json','COMPLETE'):
    files[p.name]={'size':p.stat().st_size,'sha256':sha(p)}
  receipt={'start_utc':start,'end_utc':end,'wall_s':time.perf_counter()-t,'pid':os.getpid(),'status':status,
           'config':vars(a)|{'out':str(a.out)},'error':err,'files':files}
  (a.out/'receipt.json').write_text(json.dumps(receipt,indent=2,default=str)+'\n')
  if status=='completed':
   with open(a.out/'COMPLETE','w') as f:
    f.write('complete\n'); f.flush(); os.fsync(f.fileno())

if __name__=='__main__': main()
