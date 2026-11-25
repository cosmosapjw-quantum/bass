"""R118-C dual-conservative actual history and bounded Wien redistribution experiments."""
import argparse,concurrent.futures,csv,hashlib,json,math,os,pathlib,subprocess,time
P=pathlib.Path
p=argparse.ArgumentParser()
p.add_argument('--binary',type=P,required=True);p.add_argument('--r118b',type=P,required=True)
p.add_argument('--r118b-dense',type=P,required=True);p.add_argument('--out',type=P,required=True)
p.add_argument('--only-prefix',default='')
a=p.parse_args();root=a.out.resolve();root.mkdir(parents=True,exist_ok=False);exe=a.binary.resolve()
env=dict(os.environ,RAYON_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((a.r118b/'RESULTS.json').read_text());rd=json.loads((a.r118b_dense/'RESULTS.json').read_text())
by={c['case']:c for c in r['cases']+rd['cases'] if c['status']=='PASS_SCOPED'}
cases=[]
def put(cmd,k,v):
 if k in cmd:cmd[cmd.index(k)+1]=str(v)
 else:cmd.extend([k,str(v)])
def rm(cmd,k):
 if k in cmd:i=cmd.index(k);del cmd[i:i+2]
def add(name,base,bins=None,steps=None,sub=None,nt=None,np=None,red=None,overrides=None,moments=None):
 c=by[base];cmd=list(c['command']);cmd[0]=str(exe);out=root/name;put(cmd,'--out',out);put(cmd,'--frequency-collision','dual')
 for k,v in [('--frequency-bins',bins),('--steps',steps),('--frequency-line-substeps',sub),('--frequency-nmu',nt),('--frequency-nphi',np)]:
  if v is not None:put(cmd,k,v)
 if red is not None:put(cmd,'--frequency-redistribution',','.join(map(str,red)))
 for k,v in (overrides or {}).items():put(cmd,k,v)
 if moments is True:
  put(cmd,'--spectral-moments','rays');put(cmd,'--spectral-ntheta',nt or c['nt']);put(cmd,'--spectral-nphi',np or c['np'])
 if moments is False:
  for k in ['--spectral-moments','--spectral-ntheta','--spectral-nphi']:rm(cmd,k)
 cases.append(dict(case=name,base=base,command=cmd,bins=int(cmd[cmd.index('--frequency-bins')+1]),nt=int(cmd[cmd.index('--frequency-nmu')+1]),np=int(cmd[cmd.index('--frequency-nphi')+1]),red=red,baseline=str(P(c['command'][c['command'].index('--out')+1])) if steps is None and not overrides else None))
for n in (64,128,256,512,1024):
 add(f'cold_f{n}','cold_f128',bins=n)
for n in (2,4,8,16):add(f'cold_t{n}','cold_t4',bins=64,steps=n)
for name in ('flrw_free','flrw_rest','cold_boundary','cold_be','cold_beta_0.6','cold_beta_0.85'):
 add(name,name,bins=64 if 'beta' not in name else 128)
add('cold_beta_0.85_wide','cold_beta_0.85',bins=256,overrides={'--frequency-log-min':-16,'--frequency-log-max':8})
add('cold_thick','cold_f128',bins=64,steps=2,overrides={'--tau':6.0})
for fam in ['I','II','III','IV','V','VI0','VIh_-0.25','VIstar','VII0','VIIh_0.25','VIII','IX']:
 add('r117_he_'+fam,'r117_he_'+fam,bins=64,moments=True)
for name in ('r117_overlap_flrw','r117_he_i_rays','r117_he_i_continuum'):add(name,name,bins=64,moments=True)
for name in ('dense_projected_backward-euler','dense_projected_sdirk2'):add(name,name)
for n in (64,128,256,512,1024):
 for prefix in ('monotone','turn'):
  add(f'{prefix}_f{n}',prefix+'_f128',bins=n)
for n in (8,16,32,64,128):
 add(f'turn_t{n}','turn_t64',bins=512,steps=n)
# The narrow line is deliberately a difficult off-node quadrature test.
for n in (128,512,1024):
 add(f'narrow_f{n}','narrow_line',bins=n,sub=8)
# Same R118-B accepted table-owned cold trajectory.
for n in (128,256,512,1024,2048):
 add(f'early_cold_f{n}','early_host_cold',bins=n,moments=True)
 add(f'early_line_f{n}','early_host_line',bins=n,moments=False)
# Angular refinement with a modest frequency mesh.
add('early_line_ang72','early_host_line',bins=256,nt=6,np=12,moments=False)
for sub in (4,8):
 add(f'early_line_time_sub{sub}','early_host_line',bins=512,sub=sub,moments=False)

# Prescribed dilute coherent-in-angle frequency diffusion: independent
# time refinement and two finite tilt, nonmonotone runs.
for n in (16,32,64,128):
 add(f'redist_t{n}','monotone_f128',bins=64,steps=n,sub=1,red=(.002,.15),overrides={'--frequency-line':'0,0.25,0,0'})
for name in ('turn_t64','early_host_line'):
 add('redist_'+name,name,bins=256,sub=2,red=(.0002,.15),overrides={'--frequency-line': '0,0.1,0,0' if name.startswith('turn') else '2.741153842023497,0.02,0,0'})
# Stiff saturation: actual pair rate vastly exceeds clock step; only
# positivity and conservation are asserted, not splitting accuracy.
add('redist_stiff','monotone_f128',bins=64,steps=8,sub=1,red=(1e4,.15),overrides={'--frequency-line':'0,0.25,0,0'})
def read(p):
 with p.open() as f:return [{k:float(v) for k,v in q.items()} for q in csv.DictReader(f,delimiter='\t')]
def run(c):
 out=root/c['case'];t=time.monotonic();r=dict(c)
 try:
  p=subprocess.run(c['command'],env=env,capture_output=True,text=True,timeout=300)
  r.update(returncode=p.returncode,stderr=p.stderr[-2000:],wall_s=time.monotonic()-t)
  if p.returncode:r['status']='FAIL_EXECUTION';return r
  h=read(out/'frequency_history.tsv');rays=read(out/'frequency_rays.tsv');f=read(out/'frequency_nodes.tsv')
  info=dict(l.split('=',1) for l in (out/'run.txt').read_text().splitlines() if '=' in l)
  assert info['frequency_method']=='dual' and len(f)==len(rays)*(c['bins']+1) and len(rays)==c['nt']*c['np']
  assert not (out/'frequency_cells.tsv').exists()
  assert all(math.isfinite(v) for row in h+rays+f for v in row.values())
  keys=['number_collision_defect','material_energy_preprojection_defect','material_energy_projection_defect','line_number_defect','normal_energy_balance_defect','number_continuity_trapezoid_defect','max_fv_stage_residual','max_fv_stage_iterations','collision_events','collision_subcells','line_cells','turning_rays','redistribution_cells','redistribution_number_defect','redistribution_energy_defect','pair_balance_defect','numerical_second_energy_moment','wall_s']
  m={k:float(info['frequency_'+k]) for k in keys}
  for k in ['min_drift','max_drift','b4_relative_gap']:
   if not info['frequency_'+k].startswith('not_applicable'):m[k]=float(info['frequency_'+k])
  m['min_screen_relative']=min(q['min_screen_relative'] for q in h)
  m['initial_number_error']=abs(h[0]['number_centered']-1);m['initial_energy_error']=abs(h[0]['energy_centered']-1)
  m['observer_trace_error']=max(abs(sum(q['n_'+k] for k in ('xx','yy','zz'))-sum(q['observer_n_'+k] for k in ('xx','yy','zz')))/max(abs(sum(q['n_'+k] for k in ('xx','yy','zz'))),1e-300) for q in f)
  if (out/'spectral_history.tsv').is_file():
   s=read(out/'spectral_history.tsv')
   m['moment_B3_gap']=abs(s[-1]['number_comoving']-h[-1]['number_centered']);m['moment_B4_gap']=abs(s[-1]['energy_comoving']-h[-1]['energy_centered'])
  r.update(first=h[0],last=h[-1],metrics=m,hashes={n:sha(out/n) for n in ['frequency_history.tsv','frequency_rays.tsv','frequency_nodes.tsv']})
  if (out/'frequency_line_velocity.tsv').exists():r['hashes']['frequency_line_velocity.tsv']=sha(out/'frequency_line_velocity.tsv')
  if c['baseline']:
   files=['modes.tsv','cl.tsv','los_modes.tsv','los_cl.tsv','diagnostics.tsv','lie_constants.tsv','thermochemistry.tsv','coupled_stages.tsv']
   old=P(c['baseline']);r['legacy_byte_equal']={n:(out/n).read_bytes()==(old/n).read_bytes() for n in files if (old/n).is_file()}
   assert all(r['legacy_byte_equal'].values())
  assert all(abs(m[k])<2e-11 for k in ('number_collision_defect','material_energy_preprojection_defect','material_energy_projection_defect','line_number_defect','normal_energy_balance_defect','redistribution_number_defect','redistribution_energy_defect','pair_balance_defect','max_fv_stage_residual'))
  assert m['numerical_second_energy_moment']>=-1e-14
  assert m['min_screen_relative']>=-1e-10 and m['observer_trace_error']<2e-10 and abs(m['number_continuity_trapezoid_defect'])<2e-8
  if c['case'].startswith(('turn_','early_line','redist_turn','redist_early')):
   assert m['min_drift']<0<m['max_drift'] and m['turning_rays']>0
  if 'boundary' in c['case']:assert h[-1]['escaped_number_centered']>1e-4
  if c['case']=='cold_thick':assert m['collision_subcells']>m['collision_events']
  if c['red'] is not None:assert m['redistribution_cells']>0
  r['status']='PASS_SCOPED'
 except Exception as e:r.update(status='FAIL_CHECK',error=repr(e))
 return r
def wrap(c):
 r=run(c);print(r['case'],r['status'],round(r.get('wall_s',0),3),r.get('error',''),r.get('stderr','')[-200:],flush=True);return r
sel=[c for c in cases if c['case'].startswith(a.only_prefix)];assert sel
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(wrap,sel))
(root/'RESULTS.json').write_text(json.dumps(dict(schema='bass.r118c.dual/1',binary_sha256=sha(exe),cases=results),indent=2)+'\n')
print('done',len(results),flush=True)
