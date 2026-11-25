"""Post-process the smoke receipt and test working/physical bands and diagnostic grid."""
import csv, hashlib, json, math, os, pathlib, subprocess, sys, time
root=pathlib.Path(sys.argv[1]).resolve()
summary=json.loads((root/'summary.json').read_text())
by={r['case']:r for r in summary['cases']}
assert len(summary['family_gaps'])==12
assert all(r['status']=='PASS' for r in by.values())
assert all(r['relative_l2']<1e-9 for r in summary['family_gaps'])
assert all(summary['legacy_byte_equal'].values()) and len(summary['legacy_byte_equal'])==6
assert 3.6<summary['time_refinement']['ratio']<4.4
assert summary['work_gap']['relative_l2']<1e-10
assert summary['strong_gap']['relative_l2']<1e-9
assert all(r['max_energy_defect']<1e-11 and r['min_screen']>0 and r['reality_max']<1e-12 for r in by.values())
def read(p):
    with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
def modes(case,name):
    rows=read(root/case/name)
    return [complex(float(r[x+'_re']),float(r[x+'_im'])) for r in rows if int(r['ell'])>=1 for x in 'TEB']
def gap(a,b,name):
    va,vb=modes(a,name),modes(b,name)
    assert len(va)==len(vb)
    d=math.sqrt(sum(abs(x-y)**2 for x,y in zip(va,vb)))
    return d/max(math.sqrt(sum(abs(x)**2 for x in vb)),1e-30)
def cl_gap(a,b,name):
    va=read(root/a/name);vb=read(root/b/name)
    assert len(va)==len(vb)
    cols=['TT','TE','TB','EE','EB','BB']
    return max(abs(float(x[k])-float(y[k])) for x,y in zip(va,vb) for k in cols)/max(max(abs(float(y[k])) for y in vb for k in cols),1e-30)
def rerun(base,name,changes):
    cmd=list(by[base]['command'])
    cmd[cmd.index('--out')+1]=str(root/name)
    for flag,value in changes.items():cmd[cmd.index(flag)+1]=str(value)
    start=time.perf_counter()
    p=subprocess.run(cmd,env=dict(os.environ, RAYON_NUM_THREADS='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1'),capture_output=True,text=True,timeout=180)
    return dict(case=name,command=cmd,status='PASS' if p.returncode==0 else 'FAIL',wall_s=time.perf_counter()-start,error=p.stderr[-2000:] if p.returncode else None)
grid=rerun('continuum_I','I_diagnostic_grid40x80',{'--harmonic-ntheta':40,'--harmonic-nphi':80})
extra=[grid]
for l in (8,24,32):
    extra.append(rerun('I_strong','I_strong_L'+str(l),{'--harmonic-lmax':l,'--harmonic-ntheta':max(24,l+3),'--harmonic-nphi':max(48,2*l+6)}))
good={r['case'] for r in extra if r['status']=='PASS'}
rows=[]
for x in summary['family_gaps']:
    fam=x['family'].replace(':','_')
    a,b='continuum_'+fam,'grid_'+fam
    rows.append(dict(family=x['family'],direct_rel_l2=gap(a,b,'modes.tsv'),los_cl_max_scaled=cl_gap(a,b,'los_cl.tsv')))
out={'schema':'bass.r116.extra/1','scope':'short fixed-history comparisons; not a high-l long history test','all_primary_gates':True,'direct_and_cl_gaps':rows,'extra_runs':extra,'diagnostic_grid_los_byte_equal':(root/'I_diagnostic_grid40x80'/'los_modes.tsv').read_bytes()==(root/'continuum_I'/'los_modes.tsv').read_bytes() if grid['status']=='PASS' else None,'strong_physical_band':{}}
if 'I_strong_L32' in good:
    for case in ['I_strong_L8','I_strong','I_strong_L24']:
        if case in good or case=='I_strong':
            out['strong_physical_band'][case]=gap(case,'I_strong_L32','los_modes.tsv')
(root/'extra.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='direct_and_cl_gaps'},indent=2))
print('max direct rel L2',max(x['direct_rel_l2'] for x in rows),'max Cl scaled',max(x['los_cl_max_scaled'] for x in rows))
assert all(r['status']=='PASS' for r in extra)
assert out['diagnostic_grid_los_byte_equal']
assert max(x['direct_rel_l2'] for x in rows)<1e-9 and max(x['los_cl_max_scaled'] for x in rows)<1e-9
