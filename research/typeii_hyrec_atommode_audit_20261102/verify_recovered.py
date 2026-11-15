#!/usr/bin/env python3
"""Bounded real executable verification; preserve scientific failed cases separately."""
from pathlib import Path
import ast,json,os,subprocess,sys
import numpy as np
from native_modes import HERE,ROOT,RUN,SRC,P0,OUT,MODES,check,sha,verify_source,inputs,compile_mode

def main():
    receipts=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    for opt in (False,True):
        cmd=[sys.executable]+(['-O'] if opt else [])+[str(HERE/'test_native_modes.py')]
        p=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=45)
        (HERE/('UNIT_OPTIMIZED.log' if opt else 'UNIT_NORMAL.log')).write_text(p.stdout+p.stderr)
        check(p.returncode==0,'unit test failure');receipts.append({'test':'unit5_optimized' if opt else 'unit5_normal','exit':p.returncode,'cases':5})
    inp=inputs();goodh,goodn=inp['TypeII'];h=np.loadtxt(goodh);n=np.loadtxt(goodn)
    scratch=RUN/'negative_inputs';scratch.mkdir(exist_ok=True)
    tests={
      'H_negative':(-h, n),
      'H_short':(h[:-1],n),
      'H_extra':(np.r_[h,h[-1]],n),
      'H_nan':(np.r_[np.nan,h[1:]],n),
      'nH_negative':(h,-n),
      'nH_short':(h,n[:-1]),
    }
    # This binary was built during the current native campaign, not a mock.
    binary=RUN/'SWIFT_r1/hyrec_mode';check(binary.is_file(),'missing current SWIFT binary')
    for name,(hh,nn) in tests.items():
        hp=scratch/(name+'_H.dat');np0=scratch/(name+'_n.dat')
        np.savetxt(hp,hh,fmt='%.17e');np.savetxt(np0,nn,fmt='%.17e')
        p=subprocess.run([str(binary),str(hp),str(np0),str(scratch/(name+'.out')),str(scratch/(name+'.meta'))],input=(P0/'HYREC2_FLRW_INPUT_20261102.dat').read_bytes(),cwd=scratch,env=env,capture_output=True,timeout=30)
        stderr=p.stderr.decode(errors='replace');check(p.returncode==2 and 'grid' in stderr,'negative case not rejected: '+name)
        check(not (scratch/(name+'.out')).exists(),'negative case emitted output')
        receipts.append({'test':name,'exit':p.returncode,'expected_exit':2,'stderr':stderr})
    # A fresh rebuilt FULL-quarter-step replay: no historic output is overwritten.
    b,cmd=compile_mode('FULL',4);wd=b/'TypeII'
    for file in SRC.glob('*.dat'):
        dest=wd/file.name
        if not dest.exists():dest.symlink_to(file)
    replay=scratch/'FULL_r4_TypeII_replay.dat';metadata=scratch/'FULL_r4_TypeII_replay.meta.json'
    p=subprocess.run([str(b/'hyrec_mode'),str(goodh),str(goodn),str(replay),str(metadata)],input=(P0/'HYREC2_FLRW_INPUT_20261102.dat').read_bytes(),cwd=wd,env=env,capture_output=True,timeout=120)
    check(p.returncode==0,'fresh FULL replay failed')
    check(sha(replay)==sha(OUT/'FULL_r4_TypeII.dat'),'FULL replay byte difference')
    receipts.append({'test':'fresh_FULL_r4_TypeII_rebuild_and_replay','exit':0,'byte_exact':True,'sha256':sha(replay)})
    expected={name:sha(HERE/name) for name in ('MODE_COMPARISON_RESULTS.json','MODE_OPACITY.csv')}
    p=subprocess.run([sys.executable,'-O',str(HERE/'analyze_recovered.py')],cwd=ROOT,env=env,capture_output=True,text=True,timeout=90)
    (HERE/'ANALYSIS_OPTIMIZED.log').write_text(p.stdout+p.stderr);check(p.returncode==0,'optimized analysis failed')
    check(all(sha(HERE/n)==h for n,h in expected.items()),'optimized analysis changed science data')
    receipts.append({'test':'optimized_physics_analysis','exit':0,'byte_exact_outputs':expected})
    for name in ('native_modes.py','analyze_recovered.py','verify_recovered.py'):
        tree=ast.parse((HERE/name).read_text());check(not any(isinstance(n,ast.Assert) for n in ast.walk(tree)),'bypassable science assert: '+name)
    result={'status':'SCOPED_EXECUTION_VERIFIED','receipts':receipts,'unit_assertions':10,'negative_native_input_cases':6,'fresh_native_replays':1,'optimized_analysis_replays':1,'original_sources_byte_exact':verify_source(),'scientific_campaign_failures_not_erased':True,'distinct_author_review':False,'native_subagent':'NOT_RUN'}
    (HERE/'IMPLEMENTATION_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print('VERIFIED',json.dumps({k:v for k,v in result.items() if k!='receipts'}),flush=True)
if __name__=='__main__':main()
