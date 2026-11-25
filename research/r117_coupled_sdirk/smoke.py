"""R117 production-path stage audit, fixed-band time refinement and regressions."""
import argparse,concurrent.futures,csv,gzip,hashlib,json,math,os,pathlib,subprocess,time
P=pathlib.Path
p=argparse.ArgumentParser()
p.add_argument('--binary',required=True,type=P)
p.add_argument('--rec',required=True,type=P)
p.add_argument('--out',required=True,type=P)
p.add_argument('--legacy-b',type=P)
p.add_argument('--legacy-a',type=P)
a=p.parse_args()
a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=False);exe=a.binary.resolve()
env=dict(os.environ,RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
meta=json.loads((a.rec/'SLICE_RECEIPT.json').read_text())
refs={}
for name,z in [('helium_overlap',1700),('helium',2800),('h_window',1400),('thermal_window',250)]:
 f=a.out/(name+'.tsv');f.write_bytes(gzip.decompress((a.rec/(name+'.tsv.gz')).read_bytes()))
 assert sha(f)==next(r['sha256'] for r in meta['slices'] if r['name']==name)
 refs[name]=(f,z,float(f.read_text().splitlines()[-1].split()[0]))
families=['I','II','III','IV','V','VI0','VIh:-0.25','VIstar','VII0','VIIh:0.25','VIII','IX']
cases=[('he_'+f.replace(':','_'),'helium_overlap',f,0.001,1e-5,32,'harmonic',False) for f in families]
cases += [('he_flrw','helium','FLRW',0.,0.,128,'harmonic',False),
 ('overlap_flrw','helium_overlap','FLRW',0.,0.,64,'harmonic',False),
 ('h_flrw','h_window','FLRW',0.,0.,128,'harmonic',False),
 ('thermal_flrw','thermal_window','FLRW',0.,0.,128,'harmonic',False),
 ('he_i_rays','helium_overlap','I',0.001,1e-5,32,'rays',False),
 ('he_i_continuum','helium_overlap','I',0.001,1e-5,32,'harmonic-continuum',False)]
cases += [(f'h_i_{n}','h_window','I',0.01,1e-4,n,'harmonic',False) for n in [64,128,256,512]]
cases += [(f'thermal_i_{n}','thermal_window','I',0.04,0.02,n,'harmonic',False) for n in [32,64,128,256]]
cases += [(f'thermal_viih_{n}','thermal_window','VIIh:0.25',0.04,0.02,n,'harmonic',False) for n in [32,64,128]]
cases += [(f'thermal_nonuniform_{n}','thermal_window','I',0.04,0.02,n,'harmonic',False) for n in (32,64,128)]
cases += [('thermal_stronger','thermal_window','I',0.06,0.1,128,'harmonic',False)]
cases += [(f'he_strong_probe_{n}','helium','I',0.03,0.1,n,'harmonic',True) for n in (128,512,2048)]
def read(p):
 with p.open() as f:return [{k:float(v) for k,v in r.items() if v!=''} for r in csv.DictReader(f,delimiter='\t')]
def run(case):
 name,ref,fam,shear,beta,n,route,probe=case;f,z,dur=refs[ref]
 matter=.14309694000000003*(1+z)**3
 rg=4.48162687719e-7*2.7255**4*(1+z)**4;rn=.227107317660239*3.03821934419124*rg;lam=.31113726660800006
 out=a.out/name
 cmd=[str(exe),'--out',str(out),'--family',fam,'--shear',str(shear),'--dust-beta',f'{beta},{.3*beta},0','--duration',str(dur),'--steps',str(n),'--route',route,'--feedback','recoil','--dust-fraction',str(matter/(matter+rg+rn)),'--baryon-fraction',str(.0224/.14309694000000003),'--omega-lambda',str(lam/(matter+rg+rn+lam)),'--neutrino-fraction',str(rn/(rg+rn)),'--expansion-equation','gauss-reduced','--collision','sdirk2','--lie-update','congruence','--lmax','3','--los-lmax','4','--los-ntheta','8','--los-nphi','16','--recombination','species-sdirk','--species-reference',str(f)]
 cmd+=['--harmonic-lmax','4','--harmonic-ntheta','10','--harmonic-nphi','24'] if route.startswith('harmonic') else ['--nmu','10','--nphi','24']
 if route=='harmonic-continuum':cmd+=['--harmonic-work-lmax','12']
 edges=[dur*j/n for j in range(n+1)];edges[-1]=dur
 if 'nonuniform' in name:
  edges=[dur*(j/n)**1.3 for j in range(n+1)];edges[-1]=dur
  path=a.out/(name+'_grid.tsv');path.write_text('eta\n'+'\n'.join(f'{v:.17g}' for v in edges)+'\n')
  cmd+=['--species-step-grid',str(path)]
 t=time.monotonic()
 result=dict(case=name,family=fam,reference=ref,reference_sha256=sha(f),steps=n,route=route,probe=probe,command=cmd)
 try:
  x=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=180)
  result.update(returncode=x.returncode,stderr=x.stderr[-3000:],wall_s=time.monotonic()-t)
  if x.returncode:
   result['status']='PROBE_REJECTED' if probe and 'minimum Sobolev expansion -' in x.stderr else 'FAIL_EXECUTION'
   return result
  r=read(out/'thermochemistry.tsv');s=read(out/'coupled_stages.tsv');g=read(out/'diagnostics.tsv');m=read(out/'los_modes.tsv')
  fhe=float(f.read_text().splitlines()[1].split()[1]);gamma=1-1/math.sqrt(2);c_sigma=29_979_245_800.0*6.652_458_705_1e-25*1e-6
  # Match the exact pinned REC source constants, independent recomputation.
  assert len(r)==len(g)==n+1 and len(s)==2*n and len(m)==25
  assert all(math.isfinite(v) for q in r+s+g+m for v in q.values())
  depth_err=0.;clock_err=0.;rate_err=0.;continuity=0.;prev_eta=0.
  for i,q in enumerate(s):
   clock_err=max(clock_err,abs(q['eta']-(edges[i//2]+(gamma if i%2==0 else 1.)*(edges[i//2+1]-edges[i//2]))))
   assert q['stage']==i%2+1 and q['macro_step']==i//2+1
   depth_err=max(depth_err,abs(q['depth']-(q['eta']-prev_eta)*(q['rate_left']+q['rate_used'])*.5))
   rate_err=max(rate_err,abs(q['rate_rebuilt']-c_sigma*q['n_h_m3']*q['xe']/q['h_s'])/max(q['rate_rebuilt'],1e-30))
   if i:continuity=max(continuity,abs(q['rate_left']-s[i-1]['rate_rebuilt'])/max(q['rate_left'],1e-30))
   prev_eta=q['eta']
  mx=lambda rows,k:max(abs(q[k]) for q in rows)
  charge=max(abs(q['xe']-q['xp']-q['x_heii']-2*q['x_heiii']) for q in r)
  he=max(abs(q['x_hei']+q['x_heii']+q['x_heiii']-fhe) for q in r)
  h=max(abs(q['xp']+q['x_hi']-1) for q in r)
  energy=mx(r,'thermal_defect_j_per_h')
  coupling=mx(s,'relative_residual')
  final_depth_err=abs(sum(q['depth'] for q in s)-g[-1]['proper_depth'])
  psd=min(q['min_screen_eigenvalue'] for q in g)
  assert max(charge,he,h)<1e-14
  assert all(min(q['xp'],q['x_hi'],q['x_hei'],q['x_heii'],q['x_heiii'])>=0 and q['tm_k']>0 for q in r)
  assert all(q['xe']>=0 and q['tm_k']>0 and q['rate_used']>=0 for q in s)
  assert coupling<1e-12 and rate_err<1e-14 and continuity<1e-12 and clock_err<1e-14
  assert depth_err<1e-12 and final_depth_err<1e-9 and energy<1e-27 and psd>=0
  result.update(status='PASS_SCOPED',last=r[-1],metrics=dict(
    max_charge=charge,max_h_nuclei=h,max_he_nuclei=he,max_thermal_defect=energy,
    max_stage_residual=coupling,max_independent_rate_relative=rate_err,max_stage_rate_continuity=continuity,
    max_stage_depth_defect=depth_err,depth_sum_defect=final_depth_err,max_stage_clock_defect=clock_err,
    max_iterations=mx(s,'iterations'),mean_iterations=sum(q['iterations'] for q in s)/len(s),
    max_chemistry_residual=mx(s,'chemistry_residual'),max_beta_prime=max(math.sqrt(sum(q[k]**2 for k in ['beta_prime_x','beta_prime_y','beta_prime_z'])) for q in s),
    peak_delta_xe=mx(r,'delta_xe'),peak_delta_tm_k=mx(r,'delta_tm_k'),max_gauss=mx(g,'gauss'),
    max_codazzi=max(math.sqrt(sum(q[k]**2 for k in ['codazzi_x','codazzi_y','codazzi_z'])) for q in g),
    max_jacobi=mx(g,'jacobi_norm'),max_recoil_defect=mx(g,'collision_energy_defect'),min_screen=psd,
    proper_depth=g[-1]['proper_depth']),stage_sha256=sha(out/'coupled_stages.tsv'),history_sha256=sha(out/'thermochemistry.tsv'),mode_sha256=sha(out/'los_modes.tsv'),
    vec=[q[k] for q in m if q['ell']>=1 for k in ['T_re','T_im','E_re','E_im','B_re','B_im']])
 except Exception as e:result.update(status='FAIL_CHECK',error=repr(e),wall_s=time.monotonic()-t)
 return result
def wrapped(c):
 r=run(c);print(r['case'],r['status'],r.get('wall_s'),r.get('stderr','')[-500:],r.get('error',''),flush=True);return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(wrapped,cases))
by={r['case']:r for r in results}
def dist(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
def compare(a,b):
 if by[a]['status']!='PASS_SCOPED' or by[b]['status']!='PASS_SCOPED':return {'status':'BLOCKED'}
 x,y=by[a],by[b];return dict(abs_xe=abs(x['last']['xe']-y['last']['xe']),abs_tm_k=abs(x['last']['tm_k']-y['last']['tm_k']),mode_l2=dist(x['vec'],y['vec']),abs_depth=abs(x['metrics']['proper_depth']-y['metrics']['proper_depth']))
comparisons={a+'__'+b:compare(a,b) for a,b in [('he_I','he_i_rays'),('he_I','he_i_continuum')]}
time_ratios={}
for group,ns in [('h_i',[64,128,256,512]),('thermal_i',[32,64,128,256]),('thermal_viih',[32,64,128]),('thermal_nonuniform',[32,64,128])]:
 pairs=[compare(f'{group}_{x}',f'{group}_{y}') for x,y in zip(ns,ns[1:])]
 time_ratios[group]={'n':ns,'successive_diffs':pairs,'ratios':[]}
 if all('status' not in p for p in pairs):
  time_ratios[group]['ratios']=[{k:a[k]/b[k] if b[k] else None for k in a} for a,b in zip(pairs,pairs[1:])]
legacy={}
for root,cases_ in [(a.legacy_b,['he_overlap_i','h_i']),(a.legacy_a,['grid_I','continuum_I'])]:
 if root is None:continue
 data=json.loads((root/('RESULTS.json' if root==a.legacy_b else 'summary.json')).read_text())
 for case in cases_:
  c=next(x for x in data['cases'] if x['case']==case);cmd=list(c['command']);out=a.out/('legacy_'+case);cmd[0]=str(exe);cmd[cmd.index('--out')+1]=str(out)
  # Substitute freshly extracted hash-identical reference for old B run.
  if '--species-reference' in cmd:
   i=cmd.index('--species-reference')+1;cmd[i]=str(refs[c['reference']][0])
  x=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=90)
  files=['modes.tsv','cl.tsv','los_modes.tsv','los_cl.tsv','diagnostics.tsv','lie_constants.tsv']
  if root==a.legacy_b:files+=['thermochemistry.tsv']
  legacy[case]=dict(command=cmd,returncode=x.returncode,stderr=x.stderr,byte_equal={f:(out/f).read_bytes()==(root/case/f).read_bytes() for f in files} if x.returncode==0 else {})
# Compare the physical trajectories at common macro-grid nodes, not just
# endpoint corrections (which may be cancellation-dominated).
def history_gap(a,b):
    if by[a]['status']!='PASS_SCOPED' or by[b]['status']!='PASS_SCOPED':return {}
    x=read(aout/a/'thermochemistry.tsv'); y=read(aout/b/'thermochemistry.tsv')
    stride=(len(y)-1)//(len(x)-1);y=y[::stride]
    assert len(x)==len(y) and max(abs(p['eta']-q['eta']) for p,q in zip(x,y))<1e-13
    return {k:math.sqrt(sum((p[k]-q[k])**2 for p,q in zip(x,y))/len(x)) for k in ('xe','tm_k')}
aout=a.out
for group,v in time_ratios.items():
    ns=v['n']; pairs=[history_gap(f'{group}_{x}',f'{group}_{y}') for x,y in zip(ns,ns[1:])]
    v['history_rms_diffs']=pairs
    v['history_rms_ratios']=[{k:p[k]/q[k] if q[k] else None for k in p} for p,q in zip(pairs,pairs[1:]) if p and q]
for r in results:r.pop('vec',None)
summary=dict(schema='bass.r117.stage.smoke/1',scope='fixed macro-grid partitioned SDIRK chemistry, stage-linear bare opacity; mild early tilt and finite low-z tilt, tracer thermal',binary_sha256=sha(exe),cases=results,time_ratios=time_ratios,comparisons=comparisons,legacy=legacy)
(a.out/'RESULTS.json').write_text(json.dumps(summary,indent=2)+'\n')
print('TIME',time_ratios,'COMPARISONS',comparisons,'LEGACY', {k:v['byte_equal'] for k,v in legacy.items()},flush=True)
assert all(r['status']==('PROBE_REJECTED' if r['probe'] else 'PASS_SCOPED') for r in results)
assert all(v['returncode']==0 and all(v['byte_equal'].values()) for v in legacy.values())
