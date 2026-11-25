"""R116 short solver comparisons; no long-history or inference claim."""
import concurrent.futures
import csv
import hashlib
import json
import math
import os
import pathlib
import subprocess
import sys
import time

new,old,root=map(lambda p:pathlib.Path(p).resolve(),sys.argv[1:4])
root.mkdir(parents=True,exist_ok=False)
families=['I','II','III','IV','V','VI0','VIh:-0.25','VIstar','VII0','VIIh:0.25','VIII','IX']
env=dict(os.environ,RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
def run(name,fam,route='harmonic-continuum',n=4,l=8,w=20,beta='0.06,0.02,-0.01',shear='0.02',binary=new):
    out=root/name
    cmd=[str(binary),'--out',str(out),'--family',fam,'--shear',shear,'--duration','0.04','--steps',str(n),'--route',route,'--harmonic-lmax',str(l),'--harmonic-ntheta',str(max(24,l+3)),'--harmonic-nphi',str(max(48,2*l+6)),'--feedback','recoil','--dust-fraction','0.8','--baryon-fraction','0.157','--dust-beta',beta,'--observer-beta','0.01,-0.02,0.03','--tau','0.1','--collision','sdirk2','--lie-update','congruence','--lmax','4','--los-lmax','6','--los-ntheta','12','--los-nphi','24']
    if route=='harmonic-continuum': cmd+=['--harmonic-work-lmax',str(w)]
    start=time.perf_counter()
    p=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=180)
    wall=time.perf_counter()-start
    if p.returncode:
        return dict(case=name,family=fam,status='FAIL',command=cmd,wall_s=wall,error=p.stderr[-3000:])
    m=read(out/'los_modes.tsv'); diag=read(out/'diagnostics.tsv')
    assert len(m)==49 and all(math.isfinite(float(v)) for r in m for v in r.values())
    def mode(r,x):return complex(float(r[x+'_re']),float(r[x+'_im']))
    reality=max(abs(mode(r,x)-(-1)**int(r['m'])*mode(next(q for q in m if q['ell']==r['ell'] and int(q['m'])==-int(r['m'])),x).conjugate()) for r in m for x in 'TEB')
    vec=[float(r[x+'_'+c]) for r in m if int(r['ell'])>=1 for x in 'TEB' for c in ['re','im']]
    return dict(case=name,family=fam,status='PASS',command=cmd,wall_s=wall,mode_sha256=sha(out/'los_modes.tsv'),n_modes=len(m),reality_max=reality,
                max_gauss=max(abs(float(r['gauss'])) for r in diag),max_codazzi=max(abs(float(r['codazzi_'+x])) for r in diag for x in 'xyz'),
                max_jacobi=max(abs(float(r['jacobi_norm'])) for r in diag),min_screen=min(float(r['min_screen_eigenvalue']) for r in diag),max_energy_defect=max(abs(float(r['collision_energy_defect'])) for r in diag),vec=vec)
def diff(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a['vec'],b['vec'])))
def norm(a):return math.sqrt(sum(x*x for x in a['vec']))
def compare(a,b):
    if a['status']!=b['status'] or a['status']!='PASS':return {'status':'BLOCKED_BY_CASE'}
    return dict(abs_l2=diff(a,b),relative_l2=diff(a,b)/max(norm(b),1e-30))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    pairs=list(pool.map(lambda fam:(run('continuum_'+fam.replace(':','_'),fam),run('grid_'+fam.replace(':','_'),fam,route='harmonic')),families))
results=[x for pair in pairs for x in pair]
gaps=[dict(family=fam,**compare(a,b)) for fam,(a,b) in zip(families,pairs)]
# Three time grids and an independent working-band change, fixed physical band.
ref=[run('VIstar_time_'+str(n),'VIstar',n=n) for n in (8,16,32)]
work=run('VIstar_work28','VIstar',n=8,w=28)
strong=run('I_strong','I',n=4,l=16,w=44,beta='0.3,-0.1,0.2')
strong_grid=run('I_strong_grid','I',route='harmonic',n=4,l=16,beta='0.3,-0.1,0.2')
flrw=run('FLRW','FLRW',n=4,beta='0,0,0',shear='0')
legacy=run('legacy_R114','I',route='harmonic',binary=old)
files=['modes.tsv','cl.tsv','los_modes.tsv','los_cl.tsv','diagnostics.tsv','lie_constants.tsv']
parity={f:sha(root/'legacy_R114'/f)==sha(root/'grid_I'/f) for f in files} if legacy['status']=='PASS' and pairs[0][1]['status']=='PASS' else {}
time_ref={}
if all(a['status']=='PASS' for a in ref):
    d1,d2=diff(ref[0],ref[1]),diff(ref[1],ref[2])
    time_ref=dict(d8_16=d1,d16_32=d2,ratio=d1/d2 if d2 else None)
summary=dict(schema='bass.r116.continuum.smoke/1',scope='short fixed-band deterministic template',new_binary_sha256=sha(new),old_binary_sha256=sha(old),env={'RAYON_NUM_THREADS':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'},family_gaps=gaps,time_refinement=time_ref,work_gap=compare(ref[0],work),strong_gap=compare(strong,strong_grid),legacy_byte_equal=parity,cases=results+ref+[work,strong,strong_grid,flrw,legacy])
for r in summary['cases']:
    r.pop('vec',None)
(root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for r in summary['cases']:
    print(r['case'],r['status'],r.get('wall_s'),r.get('max_gauss'),r.get('max_energy_defect'),r.get('error',''),flush=True)
print('gaps',gaps,'time',time_ref,'work',summary['work_gap'],'strong',summary['strong_gap'],'parity',parity,flush=True)
if any(r['status']!='PASS' for r in summary['cases']):sys.exit(1)
