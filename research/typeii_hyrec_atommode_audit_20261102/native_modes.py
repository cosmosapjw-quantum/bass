#!/usr/bin/env python3
"""Source-locked, compile-time-isolated HYREC mode experiment.
No production source changes. Each build has a consistent MODEL, allocation,
atomic timestep and integrator. The supplied H/nH functions use a fixed grid.
"""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,time,zipfile
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
P0=ROOT/'research/typeii_hyrec2_history_20261102'
P1=ROOT/'research/typeii_native_hyrec_expansion_20261102'
RUN=HERE/'native_run'
SRC=RUN/'original_source'
OUT=HERE/'outputs'
MODES={'SWIFT':4,'EMLA2s2p':2,'FULL':3}
LOCK=json.loads((P0/'HYREC2_NATIVE_SOURCE_REPORT.json').read_text())
def check(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def verify_source():
    names=[n for n in LOCK['original_source_atomic_table_sha256'] if n not in ('input.dat','output_xe.dat')]
    if not SRC.exists():
        SRC.mkdir(parents=True)
        with zipfile.ZipFile(HERE/'HYREC_EXECUTION_SOURCE_16.zip') as z:
            check(set(z.namelist())==set(names),'source archive members differ')
            for name in names:(SRC/name).write_bytes(z.read(name))
    for n in names:check(sha(SRC/n)==LOCK['original_source_atomic_table_sha256'][n],'original source changed: '+n)
    return len(names)
def replacement(s,old,new,count=1):
    check(s.count(old)==count,'source replacement count: '+old)
    return s.replace(old,new)
def tag(mode,refine):return mode+('_matched' if refine=='matched' else '_r'+str(refine))
def step(mode,refine):
    if mode not in MODES:raise ValueError('unknown mode')
    if refine=='matched':
        if mode!='SWIFT':raise ValueError('matched is only a SWIFT diagnostic')
        return 8.49e-5
    if refine not in (1,2,4):raise ValueError('refinement must be 1,2,4')
    return (.004 if mode=='SWIFT' else 8.49e-5)/refine
def prepare(mode,refine=1):
    dt=step(mode,refine);verify_source()
    b=RUN/tag(mode,refine);b.mkdir(parents=True,exist_ok=True)
    for n in SRC.iterdir():
        if n.suffix in ('.c','.h'):shutil.copyfile(n,b/n.name)
    h=(b/'history.h').read_text()
    h=replacement(h,'#define MODEL SWIFT','#define MODEL '+mode)
    (b/'history.h').write_text(h)
    h=(b/'hydrogen.h').read_text();macro='DLNA_SWIFT' if mode=='SWIFT' else 'DLNA_HYREC'
    h,n=re.subn(r'(^#define '+macro+r'\s+)\S+',lambda m:m[1]+format(dt,'.17g'),h,flags=re.M)
    check(n==1,'timestep macro is not unique');(b/'hydrogen.h').write_text(h)
    hist=(b/'history.c').read_text()
    hist=replacement(hist,'  double Nz = data->Nz, dz = data->zmax/Nz;','  double Nz = 2248, dz = data->zmax/Nz;')
    hist=replacement(hist,'  int Nz = data->Nz;','  int Nz = 2248;')
    def nh(m):return 'bass_hydrogen_density(cosmo,'+('z_in' if 'z_in' in m[0] else 'z')+')'
    hist,n=re.subn(r'cosmo->nH0\s*\*\s*cube\(1\.\+z(?:_in)?\)',nh,hist)
    check(n==12,'hydrogen density owner count changed')
    hist=replacement(hist,'#include "helium.h"','#include "helium.h"\n#include "bass_proper_density.h"')
    (b/'history.c').write_text(hist)
    he=(b/'helium.c').read_text();old='nH0*ainv*ainv*ainv';check(he.count(old)==4,'helium density owner count changed')
    for i in range(4):he=he.replace(old,'bass_hydrogen_density('+('cosmo' if i<3 else 'data->cosmo')+',z)',1)
    he=replacement(he,'#include "helium.h"','#include "helium.h"\n#include "bass_proper_density.h"');(b/'helium.c').write_text(he)
    for n in ('bass_proper_density.c','bass_proper_density.h'):shutil.copyfile(P1/n,b/n)
    shutil.copyfile(HERE/'mode_driver.c',b/'mode_driver.c')
    return b
def compile_mode(mode,refine=1):
    b=prepare(mode,refine)
    cmd=['gcc','-O3','-std=gnu11','-I'+str(b)]+[str(b/n) for n in ('hyrectools.c','helium.c','hydrogen.c','history.c','energy_injection.c','bass_proper_density.c','mode_driver.c')]+['-lm','-o',str(b/'hyrec_mode')]
    cp=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
    (b/'compile.log').write_text(cp.stdout+cp.stderr);check(cp.returncode==0,'compile failed: '+cp.stderr[-2000:])
    return b,cmd

def inputs():
    x=RUN/'inputs';x.mkdir(parents=True,exist_ok=True)
    H=np.loadtxt(P1/'NATIVE_HYREC_FLRW_H_GRID.dat')[:,1]
    np.savetxt(x/'H_FLRW.dat',H,fmt='%.17e')
    np.savetxt(x/'unity.dat',np.ones(2248),fmt='%.17e')
    check(sha(P0/'HYREC2_FLRW_INPUT_20261102.dat')==LOCK['calibrated_input_sha256'],'cosmological input identity')
    return {'FLRW':(x/'H_FLRW.dat',x/'unity.dat'),'TypeII':(P1/'NATIVE_TYPEII_H_ARRAY_2248.dat',P1/'TYPEII_PROPER_NH_FACTOR_2248.dat')}

def execute(b,mode,refine,bg,H,F):
    name=tag(mode,refine)+'_'+bg
    wd=b/bg;wd.mkdir(exist_ok=True)
    for n in SRC.iterdir():
        if n.suffix=='.dat':
            dest=wd/n.name
            if dest.exists() or dest.is_symlink():check(dest.is_symlink() and dest.resolve()==n.resolve(),'rate-table link drift')
            else:dest.symlink_to(n)
    OUT.mkdir(exist_ok=True)
    file=OUT/(name+'.dat');meta=OUT/(name+'.meta.json')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    cmd=[str(b/'hyrec_mode'),str(H),str(F),str(file),str(meta)]
    started=time.monotonic()
    cp=subprocess.run(cmd,input=(P0/'HYREC2_FLRW_INPUT_20261102.dat').read_bytes(),cwd=wd,env=env,capture_output=True,timeout=120)
    (OUT/(name+'.log')).write_bytes(cp.stdout+cp.stderr)
    if cp.returncode!=0:
        print('NATIVE_RUN',name,'exit='+str(cp.returncode),'FAILED_NATIVE_SOLVER',flush=True)
        return {'mode':mode,'refinement':refine,'background':bg,'exit':cp.returncode,'status':'FAILED_NATIVE_SOLVER','data':None,'stderr':cp.stderr.decode(errors='replace'),'H_sha256':sha(H),'nH_factor_sha256':sha(F)}
    arr=np.loadtxt(file);info=json.loads(meta.read_text())
    check(arr.shape==(8000,3) and np.isfinite(arr).all() and np.min(arr[:,1:])>0,'bad native output '+name)
    check(info['model']==MODES[mode] and abs(info['dlna']-step(mode,refine))<1e-17,'configuration disagreement')
    check(info['Nz']==int(np.log(8001)/step(mode,refine))+2,'allocation timestep disagreement')
    r={'mode':mode,'refinement':refine,'background':bg,'exit':cp.returncode,'seconds':time.monotonic()-started,'data':str(file.relative_to(HERE)),'sha256':sha(file),'meta':info,'H_sha256':sha(H),'nH_factor_sha256':sha(F)}
    print('NATIVE_RUN',name,'exit=0','xe1100=',arr[6900,1],flush=True)
    return r

def campaign():
    inp=inputs();res=[];builds=[]
    previous=json.loads((HERE/'NATIVE_RUNS.json').read_text()) if (HERE/'NATIVE_RUNS.json').exists() else {'runs':[]}
    known={(x['mode'],str(x['refinement']),x['background']):x for x in previous['runs']}
    failed_log=OUT/'SWIFT_r4_FLRW.log'
    if failed_log.exists() and 'xHeI = -3.020442E-05' in failed_log.read_text():
        known[('SWIFT','4','FLRW')]={'mode':'SWIFT','refinement':4,'background':'FLRW','exit':2,'status':'FAILED_NATIVE_SOLVER','data':None,'stderr':failed_log.read_text(),'evidence':'NATIVE_CAMPAIGN.log and outputs/SWIFT_r4_FLRW.log'}
    for mode,refine in [('SWIFT',1),('SWIFT',2),('SWIFT',4),('SWIFT','matched'),('EMLA2s2p',1),('EMLA2s2p',2),('FULL',1),('FULL',2),('FULL',4)]:
        b,cmd=compile_mode(mode,refine)
        builds.append({'mode':mode,'refinement':refine,'command':cmd,'patched_files_sha256':{n:sha(b/n) for n in ('history.c','history.h','hydrogen.c','hydrogen.h','helium.c','mode_driver.c')}})
        for bg,(H,F) in inp.items():
            key=(mode,str(refine),bg)
            if key in known:
                rec=known[key]
                if rec.get('data'):
                    check(sha(HERE/rec['data'])==rec['sha256'],'cached output drift')
                    check(sha(H)==rec['H_sha256'] and sha(F)==rec['nH_factor_sha256'],'cached input drift')
                print('PRESERVED_CURRENT_RUN',tag(mode,refine),bg,rec['exit'],flush=True)
            elif mode=='SWIFT' and refine==4 and bg=='TypeII' and any(x.get('status')=='FAILED_NATIVE_SOLVER' and x['mode']=='SWIFT' and x['refinement']==4 for x in res):
                rec={'mode':mode,'refinement':refine,'background':bg,'exit':None,'status':'NOT_RUN_SHARED_EARLY_HELIUM_FAILURE','data':None,'reason':'FLRW control fails at z=2852.557707, above the z=1700 intervention; no identical retry.'}
            else:rec=execute(b,mode,refine,bg,H,F)
            res.append(rec)
            (HERE/'NATIVE_RUNS.json').write_text(json.dumps({'builds':builds,'runs':res,'original_sources_byte_exact':verify_source()},indent=2)+'\n')
    a=np.loadtxt(OUT/'SWIFT_r1_TypeII.dat');p=np.loadtxt(P1/'NATIVE_TYPEII_H_AND_PROPER_NH_XE_TM_8000.dat');mask=(a[:,0]>=300)&(a[:,0]<=1700)
    gap=float(np.max(abs(a[mask,1]-p[mask,1])));check(gap<2e-9,'parent SWIFT parity failed')
    (HERE/'PARENT_PARITY.json').write_text(json.dumps({'max_abs_xe_300_1700':gap,'limit':2e-9,'status':'NUMERICALLY_MATCHED','original_sources_byte_exact':verify_source()},indent=2)+'\n')
    print('NATIVE_CAMPAIGN_COMPLETE',len(res),'PARENT_XE_GAP',gap,flush=True)
if __name__=='__main__':campaign()
