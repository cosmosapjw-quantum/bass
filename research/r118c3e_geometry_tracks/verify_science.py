import json,hashlib,gzip,io,re
from pathlib import Path
import numpy as np
H=Path('/home/cosmosapjw');B=H/'worktrees/bass-r109-native-20261124';R=H/'Downloads/htt_r109_original_rec';I=H/'worktrees/rei-htt-thomson-20261124'
D=B/'research/r118c3e_geometry_tracks';RD=R/'research/r118c3e_directional_line';ID=I/'research/r118c3e_nonlinear_compton'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def hb(b):return hashlib.sha256(b).hexdigest()
def j(p):return json.loads(Path(p).read_text())
def write(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def tests(p):
 a=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;',Path(p).read_text());assert a and all(x[0]=='ok' and x[2]=='0' for x in a);return sum(int(x[1]) for x in a)
def checklinks(rows,root):
 for p,h in rows.items():assert sha(root/p)==h,p
for p in ('INPUT.sha256','MULTI.sha256','TRIPLE.sha256'):
 for line in (D/p).read_text().splitlines():
  h,f=line.split(maxsplit=1);assert sha(B/f)==h,f
a=j(D/'TRIPLE_RESULTS.json');cases={}
for n in ('zero','plus','zerotight','plustight'):
 m=j(D/(n+'_RAW.json'));raw=Path(m['raw']);data={}
 for k,v in m['files'].items():
    p=D/v['compressed'];assert sha(p)==v['compressed_sha'];b=gzip.decompress(p.read_bytes());assert hb(b)==v['sha'];data[k]=b
    if (raw/k).exists():assert sha(raw/k)==v['sha']
 man=data['checkpoint/MANIFEST'].decode().splitlines();assert man[0]=='C3D_TRIPLE_V1' and man[1]==sha(B/'_rustcore/target/release/feedback')
 for line in man[3:]:
    h,k=line.split();assert hb(data['checkpoint/'+k])==h
 case='plusfine' if n.startswith('plus') else 'zerofine';donor=j(D/(case+'_DONOR.json'));assert sha(donor['source'])==donor['source_sha']
 assert data['REC_DONOR_ID.txt'].decode().strip()=='REC_HMLA_'+donor['source_sha']
 assert data['REC_BASS_BOUNDARY.txt']==(D/(case+'_replay.state')).read_bytes()
 assert hb(data['REC_BASS_BOUNDARY.txt'])==man[2].split()[-1].split(':')[0]
 ck=data['checkpoint/rei.txt'].decode();head,ident=ck.split('\nGENERAL_SOURCE_IDENTITY\n',1);l=head.splitlines();assert l[0]=='AXBI_CHECKPOINT_V11_GENERAL' and len(l)==28
 for k in ('axbi_covariant_driver.rs','igm_thermal.rs','spectral_ff.rs'):assert (I/'rust/rei_microphysics/src'/k).read_text() in ident
 s=np.genfromtxt(io.BytesIO(data['secondary_spectrum.csv']),names=True,delimiter=',');r=np.genfromtxt(io.BytesIO(data['history.csv']),names=True,delimiter=',')
 x=np.asarray([int(v,16) for v in l[27].split()],dtype=np.uint64).view(np.float64);assert len(x)==128
 dl=np.log(60/1e-10)/128;xx=1e-10*np.exp((np.arange(128)+.5)*dl);assert min(1/np.expm1(xx)+x)>=0
 U=s['BB_U'][-1]*15/np.pi**4*np.sum(xx**4*dl*x);err=abs(U/s['spectral_U'][-1]-1);assert err<1e-12
 assert max(abs(r['ledger']))<1e-8 and r['z'][-1]==19.95
 cases[n]=dict(spectrum_relative=float(err),energy_ledger=float(max(abs(r['ledger']))),source_sha=donor['source_sha'],files=len(data))
w=j(D/'PHYSICAL_WEDGE.json');assert all(x['projected_span_fraction']>=1/np.sqrt(5)-1e-8 for x in w['rows'])
assert min(x['projected_fraction'] for x in w['rows'])>.6
assert abs(w['rows'][0]['native_B3']/w['rows'][-1]['native_B3']-1)<1e-4
for k in ('DIRECTION.json','DIRECTION_FINE.json','SCHUR.json','AUTONOMOUS.json','MATCHED_CLOCK.json'):
 q=j(RD/k);checklinks(q['source_hashes'],R)
d=j(RD/'DIRECTION_FINE.json');assert all(x['rate_min']>0 and x['matrix_residual']<1e-12 for x in d['rows'])
assert max(abs(x['relative_rhs']) for x in d['rows'] if x['case']=='zerofine')<1e-10
r=j(RD/'AUTONOMOUS.json');led=[]
for p in sorted(RD.glob('*autonomous_state.npz')):
 z=np.load(p);e=z['e'].astype(np.longdouble);v=z['dynamic'].astype(np.longdouble);n=len(e);x=v[:n];dp=v[n];l=v[n+1:];el=np.longdouble('10.198714553953742')
 N=x.sum()+l[0]-l[3]-l[9];E=x@e+l[1]+l[2]+l[5]+l[8]-l[4]-el*l[9];P=dp+l[9]+l[7]-l[6]
 rn=abs(N)/np.sum(abs(x));re0=abs(E)/np.sum(abs(x*e));assert max(rn,re0)<1e-9 and abs(P)<1e-7
 led.append(dict(case=p.name,relative_N=float(rn),relative_E=float(re0),real_residual=float(P)))
co=j(RD/'CLOCK_ORACLE.json');old=j(RD/'MATCHED_CLOCK.json')
def delta(rows,tol):return next(x['T'] for x in rows if x['case']=='plusfine' and x['tol']==tol)-next(x['T'] for x in rows if x['case']=='zerofine' and x['tol']==tol)
dold=delta(old['rows'],1e-12);dn=delta(co['rows'],3e-13);dn0=delta(co['rows'],1e-11)
assert abs(dn/dn0-1)<.01
k=j(ID/'RESULTS.json');assert sha(ID.parent/'r118c3c_spectral_exchange/table512_spectrum.csv')==k['source_sha']
assert max(x['number_defect'] for x in k['rows'])<1e-12 and max(x['entropy_change'] for x in k['rows'])<0
rr=j(ID/'REFINE.json');assert max(x['increment_relative'] for x in rr if 'increment_relative' in x)<1e-5
assert max(abs(x['residual']) for x in k['closed'])<1e-10
b=dict(status='SCOPED_MATCHED_TRIPLE_AND_PHYSICAL_WEDGE',cases=cases,tests_lib=tests(D/'lib_tests.log'),tests_targeted=tests(D/'regression.log'),scope=a['scope'],physical_wedge=w['rows'],temperature_precision='HOLD_TIGHT_DONOR_NOT_REPLAYED')
r=dict(status='SCOPED_DIRECTIONAL_FULL_AND_EXTERIOR_SCHUR',ledger=led,old_donor_deltaT=dold,tight_oracle_deltaT=dn,oracle_coarse_deltaT=dn0,tests=int(re.search(r'(\d+) passed',(RD/'regression.log').read_text())[1]),scope='local common atomic angular closure and state-dependent external Schur source; no full causal writeback')
i=dict(status='SCOPED_NONLINEAR_KOMPANEETS',full_rust_tests=tests(ID/'full_tests.log'),python_tests=int(re.search(r'(\d+) passed',(ID/'regression.log').read_text())[1]),max_pair_refinement_error=max(x['increment_relative'] for x in rr if 'increment_relative' in x),max_number_defect=max(x['number_defect'] for x in k['rows']),scope=k['scope'])
for p,v in ((D,b),(RD,r),(ID,i)):write(p/'FINAL_RESULTS.json',v);print(p.name,v['status'])
print('donor deltas',dold,dn,dn0,'REC ledger',led,'BASS tests',b['tests_lib'],b['tests_targeted'],'REI tests',i['full_rust_tests'],i['python_tests'])
