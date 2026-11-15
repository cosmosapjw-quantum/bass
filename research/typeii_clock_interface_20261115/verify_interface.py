#!/usr/bin/env python3
"""One bounded same-author native-interface verification pass."""
from pathlib import Path
import json,os,subprocess,sys,ast
import numpy as np
from clocks import kinematics,thermal_rhs,tracking_temperature,implicit_temperature
from native_experiment import HERE,ROOT,owner,build,check,sha

def main():
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 receipts=[]
 for optimized in (False,True):
  p=subprocess.run([sys.executable]+(['-O'] if optimized else [])+[str(HERE/'test_clocks.py')],env=env,cwd=ROOT,capture_output=True,text=True,timeout=45)
  (HERE/('UNIT_OPTIMIZED.log' if optimized else 'UNIT_NORMAL.log')).write_text(p.stdout+p.stderr);check(p.returncode==0,'analytic unit contracts failed');receipts.append({'kind':'unit','optimized':optimized,'cases':10,'exit':p.returncode})
 b=build(2);wd=b/'both';inp=(owner.P0/'HYREC2_FLRW_INPUT_20261102.dat').read_bytes();H=owner.P1/'NATIVE_TYPEII_H_ARRAY_2248.dat';F=owner.P1/'TYPEII_PROPER_NH_FACTOR_2248.dat'
 scratch=HERE/'native_run/verification';scratch.mkdir(exist_ok=True)
 goodenv=dict(env,BASS_CLOCK_LANE='both',BASS_CLOCK_TABLE=str(HERE/'CLOCK_GRID.dat'),BASS_TYPEII_NH_FACTOR_FILE=str(F))
 # Fresh rebuilt native replay, kept separate from primary evidence outputs.
 out=scratch/'replay.dat';meta=scratch/'replay.meta.json';p=subprocess.run([str(b/'two_clock'),str(H),str(F),str(out),str(meta)],cwd=wd,input=inp,env=goodenv,capture_output=True,timeout=120)
 check(p.returncode==0,'fresh native replay failed');check(sha(out)==sha(HERE/'outputs/FULL_r2_both.dat'),'fresh native output not byte-identical');receipts.append({'kind':'native_rebuild_replay','exit':0,'byte_exact':True})
 # C-level probes independently compare all three thermal paths to Python formulas.
 cc=['gcc','-O3','-std=gnu11','-I'+str(b)]+[str(b/n) for n in ('hyrectools.c','helium.c','hydrogen.c','history.c','energy_injection.c','bass_proper_density.c','clock_adapter.c')]+[str(HERE/'probe_components.c'),'-lm','-o',str(scratch/'probe')]
 p=subprocess.run(cc,capture_output=True,text=True,timeout=90);check(p.returncode==0,'native component probe build '+p.stderr[-1500:])
 probegap=0.;rategap=0.
 for lane in ('both','zero'):
  ee=dict(goodenv,BASS_CLOCK_LANE=lane);p=subprocess.run([str(scratch/'probe')],cwd=wd,input=inp,env=ee,capture_output=True,timeout=45);check(p.returncode==0,'native component probe failure '+p.stderr.decode(errors='replace'))
  (HERE/f'PROBE_{lane}.log').write_bytes(p.stdout);a=np.loadtxt(p.stdout.splitlines());check(a.shape==(4,10),'component probe shape')
  for z,g,L,Tr,K,T,ss,dT,impl,rat in a:
   k={'H':1e-13,'Gamma':g,'L':L,'proper_per_tau':1/(g*1e-13),'theta':g*1e-13*(3+L),'A':2+2*L/3}
   expected=[tracking_temperature(Tr,K,0.,k),thermal_rhs(T,Tr,K,0.,k),implicit_temperature(T,Tr,K,0.,k,.001)]
   probegap=max(probegap,float(max(abs((np.array([ss,dT,impl])-expected)/np.maximum(1,abs(np.asarray(expected)))))))
   rategap=max(rategap,abs(rat-1/g))
  receipts.append({'kind':'native_component_probes','lane':lane,'states':4,'paths':'tracking,differential,implicit,atomic_clock','exit':0})
 check(probegap<5e-13 and rategap<5e-14,'native coefficient/formula mismatch')
 # Changed interface rejects malformed actual C inputs; tests call native binary.
 clock=np.loadtxt(HERE/'CLOCK_GRID.dat');invalid={}
 for name,arr in [('superluminal',clock.copy()),('nan',clock.copy()),('short',clock[:-1]),('extra',np.vstack((clock,clock[-1])) )]:
  if name=='superluminal':arr[0,0]=1.01
  if name=='nan':arr[0,0]=np.nan
  file=scratch/(name+'.dat');np.savetxt(file,arr,fmt='%.17e',header='beta beta_prime')
  invalid[name]=dict(goodenv,BASS_CLOCK_TABLE=str(file))
 invalid['unknown_lane']=dict(goodenv,BASS_CLOCK_LANE='bad_lane')
 for name,ee in invalid.items():
  badout=scratch/(name+'.out');p=subprocess.run([str(b/'two_clock'),str(H),str(F),str(badout),str(scratch/(name+'.meta'))],cwd=wd,env=ee,input=inp,capture_output=True,timeout=60)
  check(p.returncode==7 and 'CLOCK_ADAPTER_ERROR' in p.stderr.decode(errors='replace'),'bad clock accepted '+name);check(not badout.exists(),'bad clock output created')
  receipts.append({'kind':'negative_clock_input','name':name,'expected_exit':7,'exit':p.returncode,'stderr':p.stderr.decode(errors='replace')[-250:]})
 outputs=('NATIVE_RESULTS.json','THOMSON_ENDPOINTS.csv','ATOMIC_PROBES.csv');before={n:sha(HERE/n) for n in outputs}
 p=subprocess.run([sys.executable,'-O',str(HERE/'analyze_native.py')],cwd=ROOT,env=env,capture_output=True,text=True,timeout=90);(HERE/'ANALYSIS_OPTIMIZED.log').write_text(p.stdout+p.stderr);check(p.returncode==0,'optimized analysis');check(all(sha(HERE/n)==h for n,h in before.items()),'optimized science output drift')
 for n in ('clocks.py','native_experiment.py','analyze_native.py','verify_interface.py'):
  check(not any(isinstance(a,ast.Assert) for a in ast.walk(ast.parse((HERE/n).read_text()))),'bypassable assertion in science code')
 result={'unit_cases_normal_optimized':20,'native_histories_current_campaign':12,'fresh_rebuild_replay_byte_exact':True,'component_probe_states':8,'native_component_relative_gap':probegap,'native_reaction_scale_abs_gap':rategap,'native_negative_clock_cases':5,'optimized_analysis_byte_exact':True,'original_source_files_byte_exact':owner.verify_source(),'receipts':receipts,'review_type':'SAME_AUTHOR_HOSTILE_NOT_BLIND','native_subagent':'NOT_RUN','distinct_author_referee':'NOT_RUN'}
 (HERE/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='receipts'},indent=2))
if __name__=='__main__':main()
