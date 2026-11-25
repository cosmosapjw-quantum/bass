"""Run frozen, source-owned localized resonance patches. No full sky feedback."""
import argparse,concurrent.futures,csv,hashlib,json,math,os,pathlib,subprocess,time
P=pathlib.Path
p=argparse.ArgumentParser()
p.add_argument('--binary',type=P,required=True);p.add_argument('--r117',type=P,required=True);p.add_argument('--out',type=P,required=True)
a=p.parse_args();root=a.out.resolve();root.mkdir(parents=True,exist_ok=False);exe=a.binary.resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cases=[]
def add(name,source='benchmark',z=None,species='H',profile='dipole',mesh='uniform',extent=12,n=64,clock='s',duration=2,steps=32,init='pulse',p=1,D=1,drifts=(0,0)):
 if source=='benchmark':eta=0.;src=source
 else:
  src=str((a.r117/(source+'.tsv')).resolve());first=list(map(float,P(src).read_text().splitlines()[4].split()))
  eta=math.log(first[-1]/(2.7255*(1+z)))
  if abs(eta)<1e-15:eta=0.
 cmd=[str(exe),str(root/name),src,str(eta),species,profile,mesh,str(extent),str(n),clock,str(duration),str(steps),init,str(p),str(D),str(drifts[0]),str(drifts[1])]
 cases.append(dict(case=name,command=cmd,source=src,z=z,eta=eta,species=species,profile=profile,mesh=mesh,extent=extent,n=n,clock=clock,duration=duration,steps=steps,init=init,p=p,D=D,drifts=drifts))
for model in ('voigt','dipole'):
 for n in (8,16,32,64,128):add(f'bench_{model}_t{n}',profile=model,steps=n)
 for n in (32,64,128,256,512):add(f'bench_{model}_f{n}',profile=model,n=n,steps=256)
 add(f'bench_{model}_stiff',profile=model,n=64,duration=1e10,steps=1)
 add(f'bench_{model}_wien',profile=model,n=64,duration=1e10,steps=1,init='wien')
 add(f'bench_{model}_planck',profile=model,n=64,duration=1e10,steps=1,init='planck')
 for mesh in ('uniform','stretched'):
  for n in (128,256,512):add(f'bench_{model}_{mesh}_wide{n}',profile=model,mesh=mesh,extent=200,n=n,duration=10,steps=256)
for model in ('voigt','dipole'):
 add(f'bench_{model}_stretched_wide2048',profile=model,mesh='stretched',extent=200,n=2048,duration=10,steps=256)
for species,source,zs in [('H','helium',[2800,2000]),('H','h_window',[1400,1100,900]),('He','helium',[2800,2400,2000,1700])]:
 for z in zs:
  for model in ('voigt','dipole'):
   add(f'physical_{species}_{z}_{model}',source,z,species,model,mesh='stretched',extent=40,n=256,clock='eta',duration=1e-8,steps=32,init='physical-pulse')
  add(f'null_{species}_{z}',source,z,species,mesh='stretched',extent=40,n=128,clock='eta',duration=1e-6,steps=1,init='planck')
for model in ('voigt','dipole'):
 for extent in (12,40,100):
  add(f'he_turn_{model}_{extent}','helium',2800,'He',model,'stretched',extent,256,'eta',1e-6,64,'physical-pulse',1,1.1,(100,-100))
for n in (128,256,512):
 add(f'he_turn_refine_{n}','helium',2800,'He','dipole','stretched',40,n,'eta',1e-6,128,'physical-pulse',1,1.1,(100,-100))
add('he_branch_half','helium',2800,'He','dipole','stretched',40,256,'eta',1e-8,32,'physical-pulse',.5)
add('he_branch_zero','helium',2800,'He','dipole','stretched',40,256,'eta',1e-8,32,'physical-pulse',0)
for init in ('bose-pulse','bose-high'):
 for n in (1,8,32,128):add(f'{init}_{n}',n=32,duration=0.3,steps=n,init=init)
add('bose_high_stiff',n=64,duration=1e10,steps=1,init='bose-high')
add('drift_only_outflow','helium',2800,'He','dipole','stretched',12,128,'eta',1e-5,8,'pulse',0,1.1,(100,-100))
def read(p):
 with p.open() as f:return [{k:float(v) for k,v in q.items()} for q in csv.DictReader(f,delimiter='\t')]
def run(c):
 t=time.monotonic();q=dict(c);out=root/c['case']
 try:
  p=subprocess.run(c['command'],capture_output=True,text=True,timeout=60,env=dict(os.environ,RAYON_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'))
  q.update(returncode=p.returncode,stderr=p.stderr[-1500:],wall_s=time.monotonic()-t)
  if p.returncode:q['status']='REJECTED';return q
  meta=dict(l.split('=',1) for l in (out/'run.txt').read_text().splitlines() if '=' in l)
  for k,v in list(meta.items()):
   try:meta[k]=float(v)
   except ValueError:pass
  h=read(out/'history.tsv');g=read(out/'grid.tsv');pr=read(out/'profile.tsv')
  assert len(g)==c['n']+1 and len(h)==c['steps']+1
  assert all(math.isfinite(v) for r in h+g+pr for v in r.values())
  assert min(r['final_mass'] for r in g)>=0.
  assert max(abs(meta[k]) for k in ('number_defect','energy_balance_defect','max_step_number_defect','max_step_continuity_l1','max_step_energy_defect','max_nonlinear_scaled_residual'))<2e-10
  if c['init'] in ('wien','planck'):
   gap=sum(abs(r['initial_mass']-r['final_mass']) for r in g)/meta['initial_mass']
   meta['equilibrium_relative_l1']=gap;assert gap<2e-10
  q.update(status='PASS_SCOPED',metrics=meta,first=h[0],last=h[-1],hashes={n:sha(out/n) for n in ['run.txt','grid.tsv','history.tsv','profile.tsv']})
 except Exception as e:q.update(status='FAIL_CHECK',error=repr(e))
 return q
def wrap(c):
 q=run(c);print(q['case'],q['status'],q.get('stderr','')[-120:],q.get('error',''),flush=True);return q
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:r=list(pool.map(wrap,cases))
data=dict(schema='bass.r118c2.local/1',binary_sha256=sha(exe),input_sha256={c['source']:sha(P(c['source'])) for c in cases if c['source']!='benchmark'},cases=r)
(root/'RESULTS.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
print('done',len(r),flush=True)
