"""Accepted-history native harmonic spectral experiments; no spectral feedback."""
import argparse, concurrent.futures, csv, gzip, hashlib, json, math, os, pathlib, subprocess, time
P=pathlib.Path
p=argparse.ArgumentParser()
p.add_argument('--binary',type=P,required=True)
p.add_argument('--r117',type=P,required=True,help='R117 raw output directory including RESULTS.json and inputs')
p.add_argument('--r116',type=P,required=True,help='R116-A raw output directory including summary.json')
p.add_argument('--out',type=P,required=True)
a=p.parse_args()
root=a.out.resolve();root.mkdir(parents=True,exist_ok=False)
binary=a.binary.resolve();env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',RAYON_NUM_THREADS='1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r117=json.loads((a.r117/'RESULTS.json').read_text())
r116=json.loads((a.r116/'summary.json').read_text())
by={q['case']:q for q in r117['cases']}
ba={q['case']:q for q in r116['cases']}
cases=[]
families=['I','II','III','IV','V','VI0','VIh_-0.25','VIstar','VII0','VIIh_0.25','VIII','IX']
for name in ['he_'+x for x in families]+['he_flrw','overlap_flrw','h_flrw','thermal_flrw','h_i_128','thermal_i_32','thermal_i_64','thermal_i_128','thermal_viih_64','thermal_stronger','he_i_rays','he_i_continuum']:
 q=by[name]
 route='rays' if q['route']=='rays' else 'harmonic'
 cases.append((name,q['command'],route,[],a.r117/name,q['family']))
for name in ['grid_I','continuum_I','continuum_IX','I_strong','I_strong_grid']:
 if name in ba:
    q=ba[name];cases.append(('r116_'+name,q['command'],'harmonic',[],a.r116/name,q['family']))
# Fixed same accepted history, spectral-only band refinement.
for l in (6,8,12,16):
 q=by['thermal_stronger']
 cases.append((f'thermal_stronger_L{l}',q['command'],'harmonic',['--spectral-lmax',str(l),'--spectral-ntheta',str(max(20,l+4)),'--spectral-nphi',str(max(40,2*l+6))],a.r117/'thermal_stronger',q['family']))
# Resolve all five observed L=4 warnings by changing ONLY the spectral band.
for name in ('thermal_i_32','thermal_i_64','thermal_i_128','thermal_viih_64'):
    q=by[name]
    for l in ([8,12,16] if name=='thermal_viih_64' else [8]):
        cases.append((f'{name}_L{l}',q['command'],'harmonic',['--spectral-lmax',str(l),'--spectral-ntheta',str(max(20,l+4)),'--spectral-nphi',str(max(40,2*l+6))],a.r117/name,q['family']))
# Independent characteristic path on the same accepted finite-tilt histories.
for name in ('thermal_stronger','thermal_viih_64'):
    q=by[name];cases.append((name+'_ray_oracle',q['command'],'rays',['--spectral-ntheta','24','--spectral-nphi','48'],a.r117/name,q['family']))
# Strong finite tilt: independent prescribed cold scattering, not REC.
for beta in (0.05,0.2,0.6,0.85):
 for n in ([4,8,16] if beta==0.2 else [8]):
    args=[str(binary),'--out','unused','--family','FLRW','--shear','0','--duration','0.1','--steps',str(n),'--nmu','24','--nphi','48','--lmax','4','--tau','0.15','--electron-beta',f'{beta},0,0','--feedback','tracer','--collision','sdirk2','--observer-beta','0.12,0.02,-0.04']
    cases.append((f'cold_beta_{beta}_{n}',args,'rays',['--spectral-ntheta','24','--spectral-nphi','48'],None,'FLRW'))
def read(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
def parse_run(p):
 return dict(l.split('=',1) for l in p.read_text().splitlines() if '=' in l)
def run(case):
 name,old,route,extra,baseline,family=case;out=root/name;cmd=list(old);cmd[0]=str(binary);cmd[cmd.index('--out')+1]=str(out)
 # These R117 commands contain source slices and optionally grid files.
 # Verify that their original paths remain available; no external fetch.
 for flag in ('--species-reference','--species-step-grid'):
    if flag in cmd:assert P(cmd[cmd.index(flag)+1]).is_file()
 cmd+=['--spectral-moments',route]+extra
 t=time.monotonic();r=dict(case=name,command=cmd,family=family,route=route)
 try:
    q=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=180)
    r.update(returncode=q.returncode,stderr=q.stderr[-1500:],wall_s=time.monotonic()-t)
    if q.returncode:r['status']='REJECTED';return r
    info=parse_run(out/'run.txt')
    h=[{k:float(v) for k,v in q.items()} for q in read(out/'spectral_history.tsv')]
    x=[{k:float(v) for k,v in q.items()} for q in read(out/'spectral_normal.tsv')]
    o=[{k:float(v) for k,v in q.items()} for q in read(out/'spectral_observer.tsv')]
    assert len(x)==len(o) and len(h)>=2
    assert all(math.isfinite(v) for q in h+x+o for v in q.values())
    mx=lambda k:max(abs(q[k]) for q in h)
    minv=lambda k:min(q[k] for q in h)
    inv=max(max(abs(u[k]-v[k]) for k in ('variance','y_m')) for u,v in zip(x,o))
    modes=out/'spectral_modes.tsv'
    real=0.;spin0=0.
    if route=='harmonic':
        m=read(modes);z={(q['carrier'],int(q['spin']),int(q['ell']),int(q['m'])):complex(float(q['re']),float(q['im'])) for q in m}
        real=max(abs(v-(-1)**key[3]*z[(key[0],-key[1],key[2],-key[3])].conjugate()) for key,v in z.items())
        spin0=max(abs(v) for key,v in z.items() if key[1] and key[2]<2)
        assert real<1e-12 and spin0<1e-14
    num=float(info['spectral_number_collision_defect']);en=float(info['spectral_rest_energy_collision_defect'])
    gap=float(info['spectral_bolometric_integral_relative_gap'])
    sg=info['spectral_bolometric_screen_relative_gap']
    meshgap=None if sg.startswith('unavailable') else float(sg)
    cls=family in ['FLRW','I','II','VI0','VII0','VIII','IX']
    class_a=max(abs(q['number_comoving']-h[0]['number_comoving']) for q in h) if cls else None
    metrics=dict(number_collision_defect=num,rest_energy_collision_defect=en,number_continuity_defect=float(info['spectral_number_continuity_trapezoid_defect']),class_a_number_drift=class_a,bolometric_integral_gap=gap,bolometric_screen_gap=meshgap,observer_invariance=inv,max_m0_defect=mx('max_m0_defect'),min_variance=minv('min_variance'),min_y_m=minv('min_y_m'),min_primary_eigenvalue=minv('min_primary_eigenvalue'),min_log_gram=minv('min_log_gram_eigenvalue'),signed_reality=real,low_spin_defect=spin0,events=int(info['spectral_collision_events']),spectral_wall_s=float(info['spectral_wall_s']))
    r.update(metrics=metrics,last=h[-1],samples=len(x),history_rows=len(h),spectral_sha256={f:sha(out/f) for f in ['spectral_history.tsv','spectral_normal.tsv','spectral_observer.tsv']+(['spectral_modes.tsv'] if modes.exists() else [])})
    if baseline:
        files=['modes.tsv','cl.tsv','los_modes.tsv','los_cl.tsv','diagnostics.tsv','lie_constants.tsv','thermochemistry.tsv','coupled_stages.tsv']
        r['legacy_byte_equal']={f:(out/f).read_bytes()==(baseline/f).read_bytes() for f in files if (baseline/f).is_file()}
        assert all(r['legacy_byte_equal'].values())
    assert num<2e-11 and en<2e-11 and inv<1e-12 and metrics['max_m0_defect']<1e-9
    if class_a is not None:assert class_a<2e-7
    # Finite angular truncation is not a positivity certificate. Keep all
    # negative values and distinguish materially violated sampled moments.
    r['status']='PASS_SCOPED' if min(metrics['min_variance'],metrics['min_y_m'],metrics['min_primary_eigenvalue'],metrics['min_log_gram'])>=-1e-9 else 'REALIZABILITY_WARNING'
    assert info['spectral_sampled_necessary_checks']==('PASS_SCOPED' if r['status']=='PASS_SCOPED' else 'UNRESOLVED')
 except Exception as e:r.update(status='FAIL_CHECK',error=repr(e))
 return r
def wrapped(c):
 r=run(c);print(r['case'],r['status'],r.get('wall_s'),r.get('metrics',{}).get('min_log_gram'),r.get('error',''),r.get('stderr','')[-250:],flush=True);return r
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(wrapped,cases))
out=dict(schema='bass.r118.cold.spectral/1',scope='independent spectral harmonic/ray pass on accepted fixed history; no thermal/spectral feedback',binary_sha256=sha(binary),cases=results)
(root/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print('done',len(results),flush=True)
