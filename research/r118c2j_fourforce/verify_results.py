import pathlib,json,hashlib,math,gzip,re,shutil
import numpy as np
D=pathlib.Path(__file__).resolve().parent
H=pathlib.Path.home()/'Downloads'
R=H/'bass_r118c2j_final'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
J=json.loads((R/'RESULTS.json').read_text())
cases=J['cases'];assert len(cases)==12 and all(c['status']=='PASS_SCOPED' for c in cases)
for c in cases:
 for f,v in c['hashes'].items():assert sha(R/c['case']/f)==v,(c['case'],f)
 assert c['uv_ledger']['energy']<1e-9 and c['uv_ledger']['axial_momentum']<1e-9 and c['uv_ledger']['binding_heat']<1e-9
 assert c['uv_ledger']['max_event_gap']<1e-10 and c['uv_ledger']['max_absorption_energy_gap']<1e-8
 assert c['number_defect']<1e-8 and c['energy_defect']<1e-8
 assert c['characteristic_error']<5e-10
# Compare actual common redshifts, not different stop redshifts.
# Different discretizations/temporal rules prevent interpreting the comparison as a pure resolution test.
b=next(c for c in cases if c['steps']==32768)
q=np.genfromtxt(R/b['case']/'history.tsv',names=True,delimiter='\t')
paths={n:H/'rei_r118c2j_reduced'/n/'history.csv' for n in ('long16','long32')}
rs={k:np.genfromtxt(v,names=True,delimiter=',',dtype=None,encoding=None) for k,v in paths.items()}
keys=['x_HII','x_HeII','x_HeIII','Tm_K']
common=[]
for z in [19.98,15,12,10,9,8,7,6,float(rs['long32']['zbar'][-1])]:
 zz=21*np.exp(-q['eta'])-1
 base={k:float(np.interp(z,zz[::-1],q[k][::-1])) for k in keys}
 row=dict(z=z,BASS=base)
 for n,v in rs.items():
  zz=v['zbar']
  if min(zz)<=z<=max(zz):
   row[n]={k:float(np.interp(z,zz[::-1],v[('temperature_K' if k=='Tm_K' else k)][::-1])) for k in keys}
 common.append(row)
(D/'COMMON_REDSHIFT.json').write_text(json.dumps(dict(scope='linear interpolation in redshift; shared source and IC but different temporal and spectral discretizations; no convergence claim',histories={'BASS':sha(R/b['case']/'history.tsv'),**{k:sha(v) for k,v in paths.items()}},rows=common),indent=2)+'\n')
shutil.copyfile(R/'RESULTS.json',D/'RESULTS.json')
for n in ('bass_red','bass_green','bass_cross_trial','bass_build','bass_pin','bass_final_build','bass_campaign','bass_full','bass_examples'):
 p=pathlib.Path('/tmp/r118c2j_'+n+'.log')
 if p.exists():(D/(n+'.log.gz')).write_bytes(gzip.compress(p.read_bytes(),mtime=0))
def tests(n):
 s=pathlib.Path('/tmp/r118c2j_bass_'+n+'.log').read_text()
 assert 'test result: FAILED' not in s
 a=re.findall(r'test result: ok\. (\d+) passed',s)
 assert a
 return sum(map(int,a))
A=dict(status='PASS_SCOPED',parent='312d5d06b17dc4963a2641eb32a5d0bc11275693',rec_pin='7a1c593973ea74ccb13b987a30ebc1623f8b4cd4',rei_pin='156a812155a06eca03b1cc9ee4ce7c1473902e87',cases=len(cases),steps=sum(c['steps'] for c in cases),rust_tests=tests('full'),example_tests=tests('examples'),max_uv_energy=max(c['uv_ledger']['energy'] for c in cases),max_uv_pz=max(c['uv_ledger']['axial_momentum'] for c in cases),max_uv_binding_heat=max(c['uv_ledger']['binding_heat'] for c in cases),max_event_gap=max(c['uv_ledger']['max_event_gap'] for c in cases),max_packet_loss=max(c['uv_ledger']['max_packet_loss'] for c in cases),max_crossing_error=max(c['uv_ledger']['max_crossing_error'] for c in cases),max_number=max(c['number_defect'] for c in cases),max_total_energy=max(c['energy_defect'] for c in cases),tau_long=b['tau'],terminal_long=b['terminal'],uv_terminal_long=b['uv_ledger']['terminal'],raw_path=str(R),binary_sha256=J['binary_sha256'],limitations=['UV ledger is diagnostic and axial only, non-tilted LRS I; no material momentum evolution or active Einstein feedback','BASS packet chemistry still uses BE, not REI opt-in continuous birth','current endpoint compression does not control nonlinear rates; planned stage-level rate-checked compression deferred','symmetry crossing test is manufactured; long live FLRW has zero vector moment'],files={p.name:sha(p) for p in sorted(D.iterdir()) if p.is_file() and p.name!='ACCEPTANCE.json'})
(D/'ACCEPTANCE.json').write_text(json.dumps(A,indent=2)+'\n')
print(json.dumps({k:v for k,v in A.items() if k!='files'},indent=2))
