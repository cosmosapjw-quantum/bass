"""Actual FT03 histories, existing BASS visibility, independent Decimal quadrature."""
from decimal import Decimal as D,getcontext
from pathlib import Path
import argparse,hashlib,json,subprocess,time,csv
getcontext().prec=70
C=D('299792458');S=D('6.6524587e-29');TOL=D('2e-12');ABS=D('2e-14')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--native',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();out=Path(a.out);out.mkdir(exist_ok=True,parents=True)
 checks=0;failures=[];maxima={};hist={};summaries=[]
 def truth(ok,name,case):
  nonlocal checks
  checks+=1
  if not ok:failures.append(dict(check=name,case=case))
 def close(got,want,scale,name,case,tol=TOL):
  got=D(str(got));want=D(str(want));scale=abs(D(str(scale)));err=abs(got-want)/scale if scale else (D(0) if got==want else D('Infinity'))
  maxima[name]=max(maxima.get(name,D(0)),err);truth(err<=tol,name,case)
 for n in [1000,2000]:
  command=f'history {n} .2';start=time.monotonic();run=subprocess.run([a.native],input=command+'\n',capture_output=True,text=True,timeout=60);(out/f'history_{n}.json').write_text(run.stdout);(out/f'history_{n}.stderr').write_text(run.stderr);wall=time.monotonic()-start
  truth(run.returncode==0,'native exit0',n);z=json.loads(run.stdout,parse_float=D);truth(z.get('ok') is True,'history completed',n)
  if not z.get('ok'):continue
  hist[n]=z;edges=list(map(D,z['time_edges_seconds']));states=z['states'];rates=z['interval_rates_s_inverse'];tail=D(z['observer_optical_depth']);taus=[tail]*(n+1)
  truth(len(states)==n+1 and len(edges)==n+1 and len(rates)==n,'dimensions',n)
  truth(z['c_constants_match'] is True,'source and BASS c identities',n);truth(z['rct_enabled'] is False,'RCT OFF',n);truth(z['physical_admission'] is False,'physical claim ceiling',n)
  truth(D(z['max_step_local_error'])<D('2e-4'),'existing local-error gate',n)
  truth(D(z['max_step_residual'])<D('1e-12'),'finite observed residual',n)
  for i,state in enumerate(states):
   x,y,w=map(D,state['fractions']);ne=D('1e-4')*x+D('8.3e-6')*(y+2*w)
   close(state['ne_cm3'],ne,ne,'edge charge density',f'{n}:{i}');close(state['ne_m3'],ne*D('1e6'),ne*D('1e6'),'edge SI density',f'{n}:{i}')
   truth(D('30000')<=D(state['temperature_k'])<=D('110000'),'actual source T guard',f'{n}:{i}')
   if i<n:close(rates[i],ne*D('1e6')*C*S,ne*D('1e6')*C*S,'left-sampled source rate',f'{n}:{i}')
  for i in range(n-1,-1,-1):taus[i]=taus[i+1]+D(rates[i])*(edges[i+1]-edges[i])
  surv=[(-t).exp() for t in taus];mass=[]
  for i in range(n):mass.append(surv[i+1]*(1-(-D(rates[i])*(edges[i+1]-edges[i])).exp()))
  for i in range(n+1):close(z['optical_depth'][i],taus[i],max(taus[i],D('1e-300')),'backward depth',f'{n}:{i}');close(z['survival'][i],surv[i],1,'survival absolute',f'{n}:{i}',ABS)
  for i in range(n):close(z['interval_probability'][i],mass[i],mass[i],'cell probability',f'{n}:{i}')
  close(sum(map(D,z['interval_probability']))+D(z['survival'][0]),(-tail).exp(),1,'boundary mass',n,ABS)
  summaries.append(dict(intervals=n,wall_seconds=wall,thomson_depth=float(D(z['optical_depth'][0])-tail),initial_ne_m3=float(states[0]['ne_m3']),final_ne_m3=float(states[-1]['ne_m3']),initial_T_K=float(states[0]['temperature_k']),final_T_K=float(states[-1]['temperature_k']),interval_probability_mass=float(sum(map(D,z['interval_probability']))),max_step_local_error=float(z['max_step_local_error']),max_step_residual=float(z['max_step_residual'])))
  with (out/f'history_{n}.csv').open('w',newline='') as f:
   w=csv.writer(f,lineterminator='\n');w.writerow(['t_seconds','x_HII','x_HeII','x_HeIII','T_K','ne_m3','q_left_s_inverse','tau','survival','cell_probability'])
   for i in range(n+1):w.writerow([str(edges[i]),*map(str,states[i]['fractions']),str(states[i]['temperature_k']),str(states[i]['ne_m3']),str(rates[i]) if i<n else '',str(z['optical_depth'][i]),str(z['survival'][i]),str(z['interval_probability'][i]) if i<n else ''])
 refinement={}
 if len(hist)==2:
  coarse,fine=hist[1000],hist[2000];ef=[D(0)]*2001;fe=list(map(D,fine['time_edges_seconds']))
  for j in range(1999,-1,-1):ef[j]=ef[j+1]+abs(D(fine['interval_rates_s_inverse'][j])-D(coarse['interval_rates_s_inverse'][j//2]))*(fe[j+1]-fe[j])
  differences=[]
  for i in range(1001):
   diff=abs(D(fine['survival'][2*i])-D(coarse['survival'][i]));bound=1-(-ef[2*i]).exp();truth(diff<=bound+ABS,'common-grid opacity L1 map bound',i);differences.append(diff)
  refinement={'paired_histories':[1000,2000],'opacity_L1_difference':str(ef[0]),'max_survival_difference':str(max(differences)),'mapping_bound_at_start':str(1-(-ef[0]).exp()),'depth_difference':str(abs(D(fine['optical_depth'][0])-D(coarse['optical_depth'][0]))),'interpretation':'finite difference between two actual discrete chemistry/sampling histories; not a continuum error certificate or measured convergence order'}
 result=dict(schema_version='1.0',experiment_id='BASS-REI-E3',status='PASS' if not failures else 'FAIL',checks=checks,native_history_calls=2,precision_digits=70,tolerance=str(TOL),probability_absolute_tolerance=str(ABS),max_scaled_errors={k:str(v) for k,v in maxima.items()},histories=summaries,refinement=refinement,failures=failures,native_binary_sha256=hashlib.sha256(Path(a.native).read_bytes()).hexdigest(),oracle_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='static controlled FT03 histories mapped through actual BASS cold-Thomson model; no expansion, no self-consistent Bianchi or thermal/KN certificate',timestamp_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
 (out/'CONTROLLED_HISTORY_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(0 if not failures else 1)
if __name__=='__main__':main()
