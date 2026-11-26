"""Final evidence verification for the three C3C scoped research units."""
import json, re, hashlib, subprocess
from pathlib import Path
import numpy as np
H=Path('/home/cosmosapjw')
B=H/'worktrees/bass-r109-native-20261124'
R=H/'Downloads/htt_r109_original_rec'
I=H/'worktrees/rei-htt-thomson-20261124'
BD=B/'research/r118c3c_memory_kernel'
RD=R/'research/r118c3c_line_face'
ID=I/'research/r118c3c_spectral_exchange'
def sha(p):
    with Path(p).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def read(d,n): return json.loads((d/n).read_text())
def write(d,n,o): (d/n).write_text(json.dumps(o,indent=2)+'\n')
def exits(d):
    vals={p.name:int(p.read_text()) for p in d.glob('*.exit')}
    for k,v in vals.items():
        assert (v!=0 if 'red' in k or 'first_failed' in k else v==0), (d,k,v)
    return vals
def sha_file(repo,p):
    for line in p.read_text().splitlines():
        expected,f=line.split(maxsplit=1)
        assert sha(repo/f)==expected, f
def tests(d,name):
    s=(d/name).read_text()
    rows=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;',s)
    assert rows and all(r[0]=='ok' and int(r[2])==0 for r in rows)
    return sum(int(r[1]) for r in rows)
def links(obj):
    for p,h in obj.items(): assert sha(p)==h,p
w=read(BD,'WEDGE.json'); links(w['inputs'])
sha_file(B,BD/'INPUT.sha256')
conv=read(BD,'CONVERGENCE.json')
assert conv['projector_defect']<1e-12
assert max(row['native_relative'] for row in conv['rows'])<2e-8
assert abs(conv['spin3_fraction']**2+conv['spin1_fraction']**2-1)<1e-12
b=dict(status='SCOPED_WEDGE_KERNEL_VERIFIED',exits=exits(BD),lib_tests=tests(BD,'lib_tests.log'),regression_tests=tests(BD,'regression.log'),post_c9_tests=tests(BD,'audit_tests.log'),convergence=conv)
rr=read(RD,'TIGHT.json'); links(rr['source_hashes'])
assert sha(H/'Downloads/rec_r118c2w_full_local/GRAPH128.npz')==rr['graph_sha']
assert sha(R/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')==rr['rates_sha']
assert all(row['qss_increment_relative']<1e-8 for row in rr['rows'])
ledger=[]
for f in sorted(RD.glob('*tight_state.npz')):
    with np.load(f) as z:
        e=z['e'].astype(np.longdouble); d=z['dynamic'].astype(np.longdouble); n=len(e); p=d[n]; x=d[:n]; l=d[n+1:]; el=np.longdouble('10.198714553953742')
        # Separate physical photon-only and real-population ledgers.
        N=x.sum()+l[0]-l[3]-l[9]
        U=x@e+l[1]+l[2]+l[5]+l[8]-l[4]-el*l[9]
        real=p+l[9]+l[7]-l[6]
        relN=abs(N)/np.sum(abs(x)); relU=abs(U)/np.sum(abs(x*e))
        assert relN<1e-9 and relU<1e-9 and abs(real)<1e-8
        ledger.append(dict(case=f.name,photon_number_residual=float(N),photon_energy_residual=float(U),relative_number=float(relN),relative_energy=float(relU),real_population_residual=float(real),combined_number_residual=float(N+real),combined_energy_residual=float(U+el*real)))
write(RD,'LEDGER_FINAL.json',ledger)
r=dict(status='SCOPED_PHYSICAL_LINE_PAIR_VERIFIED',exits=exits(RD),regression_tests=31,post_c9_tests=2,ledger=ledger,scope=rr['scope'])
assert re.search(r'31 passed', (RD/'regression.log').read_text())
assert re.search(r'2 passed', (RD/'audit_green.log').read_text())
s=read(ID,'STAGES.json')
for name,x in s.items():
    links(x['source']); assert sha(ID/(name+'_stages.csv'))==x['stages_sha']
sha_file(I,ID/'BINARY.sha256')
oracle=read(ID,'ORACLE.json'); absolute=read(ID,'ABSOLUTE.json')
assert sha(ID.parent/'r118c3b_ff_balance/gauntff.dat')==oracle['gaunt_sha']==absolute['sha']
assert max(x['energy_weighted_spectrum_relative'] for x in oracle['rows'])<4e-9
api=read(ID,'AUDIT_API.json'); assert api['grid_exact'] and api['spectrum_energy_relative']<1e-13
spec={}
for p in sorted(ID.glob('*.csv')):
    if p.name.endswith('_spectrum.csv') or p.name.endswith('_stages.csv') or p.name=='audit_spectrum.csv': continue
    a=np.genfromtxt(p,delimiter=',',names=True)
    if 'net' not in a.dtype.names: continue
    row={k:float(a[k][-1]) for k in a.dtype.names}
    assert np.max(abs(a['net']-a['U']-a['work']))<1e-21,p
    spec[p.stem]=row
i=dict(status='SCOPED_EVOLVING_SPECTRUM_VERIFIED',exits=exits(ID),full_tests_before_c9=tests(ID,'full_tests.log'),post_c9_tests=tests(ID,'audit_green.log'),spectra=spec,oracle=oracle,api=api)
# Verify pre-C10 push receipts and ancestor chain.
rows=[s.split('\t') for s in (BD/'PUSH_THROUGH_C9.tsv').read_text().splitlines()]
stages=['R'+str(j) for j in range(1,11)]+['C'+str(j) for j in range(1,10)]
assert len(rows)==57
for repo in [B,R,I]:
    q=[x for x in rows if x[1]==repo.name]
    assert [x[0] for x in q]==stages
    for stage,name,local,remote,code in q:
        assert local==remote and code=='0'
        subprocess.run(['git','-C',str(repo),'merge-base','--is-ancestor',local,'HEAD'],check=True)
for d,v in [(BD,b),(RD,r),(ID,i)]:
    write(d,'FINAL_RESULTS.json',v)
    print(d.name,v['status'],{k:v[k] for k in v if 'tests' in k})
print('REC separate ledger',ledger)
print('57 verified remote stage receipts through C9')
