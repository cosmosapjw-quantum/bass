"""R118-B actual fixed-history frequency replay, source-locked cold controls,
prescribed finite lines and accepted early-tilt table-opacity history.
No atomic population feedback."""
import argparse,concurrent.futures,csv,hashlib,json,math,os,pathlib,subprocess,time
P=pathlib.Path
p=argparse.ArgumentParser()
p.add_argument('--binary',required=True,type=P)
p.add_argument('--r117',required=True,type=P)
p.add_argument('--out',required=True,type=P)
p.add_argument('--only-prefix',default='')
a=p.parse_args()
root=a.out.resolve();root.mkdir(parents=True,exist_ok=False)
exe=a.binary.resolve()
env=dict(os.environ,RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r117=json.loads((a.r117/'RESULTS.json').read_text())
by={q['case']:q for q in r117['cases']}
cases=[]
def base(name,dur,steps,beta=(0,0,0),tau=0,nt=4,np=8,scheme='sdirk2'):
 return [str(exe),'--out',str(root/name),'--family','FLRW','--shear','0','--duration',str(dur),'--steps',str(steps),'--nmu',str(nt),'--nphi',str(np),'--route','rays','--lmax','3','--tau',str(tau),'--electron-beta',','.join(map(str,beta)),'--feedback','tracer','--collision',scheme,'--observer-beta','0.12,0.02,-0.04']
def add(name,cmd,bins,lo=-12,hi=5,nt=4,np=8,line=None,vel=None,sub=1,baseline=None,ref='manufactured',moments=True,method='union'):
 cmd=list(cmd);cmd[0]=str(exe);cmd[cmd.index('--out')+1]=str(root/name)
 cmd+=['--frequency-collision',method,'--frequency-bins',str(bins),'--frequency-log-min',str(lo),'--frequency-log-max',str(hi),'--frequency-nmu',str(nt),'--frequency-nphi',str(np)]
 if line is not None:cmd+=['--frequency-line',','.join(map(str,line)),'--frequency-line-velocity',str(vel),'--frequency-line-substeps',str(sub)]
 if moments:cmd+=['--spectral-moments','rays','--spectral-ntheta',str(nt),'--spectral-nphi',str(np)]
 cases.append(dict(case=name,command=cmd,method=method,bins=bins,lo=lo,hi=hi,nt=nt,np=np,line=line,velocity=str(vel) if vel is not None else None,substeps=sub,baseline=str(baseline) if baseline else None,reference=ref))
add('flrw_free',base('flrw_free',.4,8),256)
add('flrw_rest',base('flrw_rest',.4,8,tau=1.),256)
for n in (128,256,512,1024):
 add(f'cold_f{n}',base('x',.1,4,(.2,-.1,.05),.3),n)
add('cold_boundary',base('x',.1,4,(.2,-.1,.05),.3),128,-1,1)
for n in (2,4,8,16):
 add(f'cold_t{n}',base('x',.1,n,(.2,-.1,.05),.3),512)
for b in (.6,.85):
 add(f'cold_beta_{b}',base('x',.1,8,(0,0,b),.15,8,16),256,nt=8,np=16)
add('cold_be',base('x',.1,4,(.2,-.1,.05),.3,scheme='backward-euler'),512)
# Time-independent line benchmark: FLRW redshift with stationary material.
vel0=root/'rest_velocity.tsv';vel0.write_text('eta beta_x beta_y beta_z\n0 0 0 0\n0.4 0 0 0\n')
# Fixed, piecewise-linear velocity schedule. At least some angular rays have
# positive drift then negative drift. This is not a self-consistent host.
vel=root/'turn_velocity.tsv'
vel.write_text('eta beta_x beta_y beta_z\n'+'\n'.join(f'{t:.17g} 0 0 {math.tanh(-t+3*(t-0.2)**2):.17g}' for t in [0.4*i/8 for i in range(9)])+'\n')
for n in (128,256,512,1024):
 for case,v in [('monotone',vel0),('turn',vel)]:
  add(f'{case}_f{n}',base('x',.4,64),n,-2,2,line=(0,.04,.08,0),vel=v,sub=2,moments=False)
for n in (8,16,32,64):
 add(f'turn_t{n}',base('x',.4,n),512,-2,2,line=(0,.04,.08,.15),vel=vel,sub=1,moments=False)
# A narrow prescribed line tests profile-aware quadrature (width << cell).
add('narrow_line',base('x',.4,128),512,-2,2,line=(0,.0005,.0002,0),vel=vel0,sub=2,moments=False)
# Original accepted R117 histories, spectral rays independently replay their
# event depths and velocities. Re-run the actual owner commands, not samples.
for name in ['he_'+x for x in ['I','II','III','IV','V','VI0','VIh_-0.25','VIstar','VII0','VIIh_0.25','VIII','IX']]+['overlap_flrw','he_i_rays','he_i_continuum']:
 q=by[name];assert q['status']=='PASS_SCOPED'
 add('r117_'+name,q['command'],128,baseline=a.r117/name,ref='R117 accepted source history')
# Strong early-tilt route with same initial parameters as rejected R117
# probe, but explicitly table-owned xe and NO REC response. A finite-width
# illustrative true line samples the ACTUAL accepted host endpoints.
ref=a.r117/'helium.tsv'
lines=ref.read_text().splitlines()
rows=[list(map(float,l.split())) for l in lines[4:]]
ion=root/'early_table_xe.tsv'
ion.write_text('eta xe_per_H\n'+'\n'.join(f'{v[0]:.17g} {1-v[1]+v[2]+2*v[3]:.17g}' for v in rows)+'\n')
orig=by['he_strong_probe_128']['command']
def put(cmd,key,value):cmd[cmd.index(key)+1]=str(value)
cmd=list(orig)
for key in ('--recombination','--species-reference'):
 i=cmd.index(key);del cmd[i:i+2]
put(cmd,'--duration',.025);put(cmd,'--steps',64)
cmd+=['--ionization',str(ion),'--n-h-emit-m3',str(rows[0][5]),'--h-emit-s',str(rows[0][6])]
center=math.log(10.2/(8.617333262e-5*rows[0][7]))
add('early_host_cold',cmd,256,ref='R117 initial strong probe, table xe and accepted cold recoil only')
add('early_host_line',cmd,256,line=(center,.02,.03,0.),vel='host',sub=2,ref='same early accepted cold host; illustrative broadened line',moments=False)
# Refine the same early accepted trajectory in frequency and angle.
for nf in (512,1024,2048):
 add(f'early_host_cold_f{nf}',cmd,nf,ref='same accepted early host, frequency refinement',moments=False)
 add(f'early_host_line_f{nf}',cmd,nf,line=(center,.02,.03,0.),vel='host',sub=2,ref='same accepted early host, frequency refinement',moments=False)
add('early_host_line_ang72',cmd,512,nt=6,np=12,line=(center,.02,.03,0.),vel='host',sub=2,ref='same accepted early host, angular refinement',moments=False)
# Stage-consistent projected generator: fixed grid time test and actual
# accepted histories. The union reference is deliberately retained.
for n in (2,4,8,16):
 add(f'projected_t{n}',base('x',.1,n,(.2,-.1,.05),.3),64,-4,3,method='projected')
add('projected_boundary_be',base('x',.1,4,(.2,-.1,.05),.3,scheme='backward-euler'),128,-1,1,method='projected')
for name in ('he_I','he_VIIh_0.25'):
 q=by[name]
 add('projected_r117_'+name,q['command'],128,baseline=a.r117/name,ref='R117 accepted source history',method='projected')
add('projected_early_host_line',cmd,128,line=(center,.02,.03,0.),vel='host',sub=2,ref='same accepted early cold host; projected FV',moments=False,method='projected')
for nf in (512,1024):
 add(f'projected_early_refine_{nf}',cmd,nf,line=(center,.02,.03,0.),vel='host',sub=2,ref='same accepted early host; projected FV frequency refinement',moments=False,method='projected')
# Small independent dense angular-frequency operator oracles.
for method in ('union','projected'):
 for scheme in ('backward-euler','sdirk2'):
  name=f'dense_{method}_{scheme}'
  cc=base('x',.1,1,(.2,-.1,.05),.3,4,6,scheme)
  put(cc,'--lmax',2)
  add(name,cc,16,-2,2,nt=3,np=6,moments=False,method=method)
def read(p):
 with p.open() as f:return [{k:float(v) for k,v in r.items()} for r in csv.DictReader(f,delimiter='\t')]
def run(c):
 name=c['case'];out=root/name;cmd=c['command'];t=time.monotonic();r=dict(c)
 try:
  p=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=240)
  r.update(returncode=p.returncode,stderr=p.stderr[-2000:],wall_s=time.monotonic()-t)
  if p.returncode:r['status']='FAIL_EXECUTION';return r
  h=read(out/'frequency_history.tsv');info=dict(l.split('=',1) for l in (out/'run.txt').read_text().splitlines() if '=' in l)
  x=read(out/'frequency_rays.tsv');q=read(out/'frequency_cells.tsv')
  assert len(q)==c['bins']*c['nt']*c['np'] and len(x)==c['nt']*c['np']
  assert all(math.isfinite(v) for z in h+x+q for v in z.values())
  m={k.removeprefix('frequency_'):float(v) for k,v in info.items() if k in ['frequency_number_collision_defect','frequency_material_energy_preprojection_defect','frequency_material_energy_projection_defect','frequency_line_number_defect','frequency_number_continuity_trapezoid_defect','frequency_normal_energy_balance_defect','frequency_turning_rays','frequency_collision_events','frequency_collision_subcells','frequency_line_cells','frequency_wall_s','frequency_max_fv_stage_residual','frequency_max_fv_stage_iterations']}
  for k in ['frequency_min_drift','frequency_max_drift','frequency_b4_relative_gap']:
    if info[k] not in ('not_applicable','not_applicable_prescribed_line'):m[k.removeprefix('frequency_')]=float(info[k])
  m['min_screen_relative']=min(z['min_screen_relative'] for z in h)
  m['observer_trace_error']=max(abs((z['f_xx']+z['f_yy']+z['f_zz'])-(z['observer_f_xx']+z['observer_f_yy']+z['observer_f_zz']))/max(abs(z['f_xx']+z['f_yy']+z['f_zz']),1e-300) for z in q)
  m['initial_number_error']=abs(h[0]['number_centered']-1)
  m['initial_energy_error']=abs(h[0]['energy_centered']-1)
  if (out/'spectral_history.tsv').is_file():
    s=read(out/'spectral_history.tsv');m['moment_B3_gap']=abs(h[-1]['number_centered']-s[-1]['number_comoving']);m['moment_B4_gap']=abs(h[-1]['energy_centered']-s[-1]['energy_comoving'])
  r.update(metrics=m,first=h[0],last=h[-1],nrows=len(h),sha256={k:sha(out/k) for k in ('frequency_history.tsv','frequency_rays.tsv','frequency_cells.tsv')})
  if (out/'frequency_line_velocity.tsv').is_file():r['sha256']['frequency_line_velocity.tsv']=sha(out/'frequency_line_velocity.tsv')
  if c['baseline']:
    old=P(c['baseline']);files=['modes.tsv','cl.tsv','los_modes.tsv','los_cl.tsv','diagnostics.tsv','lie_constants.tsv','thermochemistry.tsv','coupled_stages.tsv']
    r['legacy_byte_equal']={f:(out/f).read_bytes()==(old/f).read_bytes() for f in files if (old/f).is_file()}
    assert all(r['legacy_byte_equal'].values())
  assert max(m['number_collision_defect'],m['material_energy_preprojection_defect'],m['line_number_defect'])<2e-11
  assert abs(m['normal_energy_balance_defect'])<2e-10 and m['min_screen_relative']>=-1e-10
  assert m['observer_trace_error']<2e-10
  if c['method']=='projected':assert m['max_fv_stage_residual']<2e-13
  if name.startswith('turn_'):assert m['min_drift']<0 and m['max_drift']>0 and m['turning_rays']>0
  if name.startswith('early_host_line') or name=='projected_early_host_line':assert m['min_drift']<0 and m['max_drift']>0 and m['turning_rays']>0
  if name=='cold_boundary':assert h[-1]['escaped_number_centered']>1e-4
  r['status']='PASS_SCOPED'
 except Exception as e:r.update(status='FAIL_CHECK',error=repr(e))
 return r
def wrapped(c):
 r=run(c);print(r['case'],r['status'],round(r.get('wall_s',0),3),r.get('error',''),r.get('stderr','')[-300:],flush=True);return r
selected=[c for c in cases if c['case'].startswith(a.only_prefix)]
assert selected
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(wrapped,selected))
summary=dict(schema='bass.r118b.frequency/1',binary_sha256=sha(exe),reference_sha256=sha(ref),ionization_sha256=sha(ion),velocity_sha256={p.name:sha(p) for p in (vel0,vel)},cases=results)
(root/'RESULTS.json').write_text(json.dumps(summary,indent=2)+'\n')
print('done',len(results),flush=True)
