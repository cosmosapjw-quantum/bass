import json,hashlib,gzip,re,subprocess
from pathlib import Path
import numpy as np
H=Path('/home/cosmosapjw');B=H/'worktrees/bass-r109-native-20261124';R=H/'Downloads/htt_r109_original_rec';I=H/'worktrees/rei-htt-thomson-20261124'
D=B/'research/r118c3d_four_tracks';RD=R/'research/r118c3d_two_sided';ID=I/'research/r118c3d_live_spectral'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def hb(b):return hashlib.sha256(b).hexdigest()
def j(p):return json.loads(Path(p).read_text())
def write(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def count(p):
 r=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;',Path(p).read_text());assert r and all(x[0]=='ok' and x[2]=='0' for x in r)
 return sum(int(x[1]) for x in r)
def verify_sha(root,p):
 for line in Path(p).read_text().splitlines():
  h,f=line.split(maxsplit=1);assert sha(root/f)==h,f
for p in ('NULL_BINARY.sha256','EARLY_BINARY.sha256','BRIDGE.sha256','FEEDBACK.sha256'):verify_sha(B,D/p)
x=j(D/'REC_INPUT.json');src=Path(x['source']);assert sha(src)==x['compressed_sha'] and hb(gzip.decompress(src.read_bytes()))==x['uncompressed_sha'] and sha(D/'REC_CLOCK.csv')==x['clock_sha']
f=j(D/'FEEDBACK_INPUT.json');assert sha(f['donor'])==f['donor_sha'] and sha(D/'FEEDBACK_CLOCK.csv')==f['clock_sha'] and sha(D/'early_32768.csv')==f['input_bass_clock_sha']
r=j(D/'RESULTS.json');assert r['clock_iteration_max_H_relative']<1e-10
assert r['early']['32768']['max_gauss']<4e-8 and r['early']['32768']['max_gauss']<r['early']['8192']['max_gauss']/15
assert r['null']['null_refined_8192']['norms']['B3_2']<1e-12
assert r['null']['null_refined_8192']['norms']['B3_3']>1e-5 and r['null']['null_refined_8192']['norms']['B5_3']>1e-5
assert r['null']['simple1024']['norms']['B3_2']>1e-6
def raw(n,key):
 m=j(D/(n+'_RAW.json'));q=m['files'][key];z=D/q['compressed']
 assert sha(z)==q['compressed_sha'];b=gzip.decompress(z.read_bytes());assert hb(b)==q['sha']
 p=Path(m['raw'])/key
 if p.exists():assert sha(p)==q['sha']
 return b
def parsebits(t):return np.asarray([int(z,16) for z in t.split()],dtype=np.uint64).view(np.float64)
cases={}
for n in r['cases']:
 m=j(D/(n+'_RAW.json'))
 for k in m['files']:raw(n,k)
 man=raw(n,'checkpoint/MANIFEST').decode().splitlines();assert man[0]=='C3D_TRIPLE_V1'
 exe=B/'_rustcore/target/release'/('feedback' if n in ('feedback','feedback_fine','refined') else 'c3d_live_triple_bridge')
 assert man[1]==sha(exe)
 for l in man[3:]:
  h,k=l.split();assert hb(raw(n,'checkpoint/'+k))==h
 boundary=raw(n,'REC_BASS_BOUNDARY.txt');assert hb(boundary)==man[2].split()[-1].split(':')[0]
 n0='feedback' if n in ('feedback','feedback_fine') else '32768' if n=='refined' else '2048'
 assert boundary==(D/('early_'+n0+'.state')).read_bytes()
 donor=raw(n,'REC_DONOR_ID.txt').decode().strip()
 assert donor==('REC_HMLA_' if n in ('feedback','feedback_fine','refined') else '')+(f['donor_sha'] if n0=='feedback' else x['uncompressed_sha'])
 ck=raw(n,'checkpoint/rei.txt').decode();head,ident=ck.split('\nGENERAL_SOURCE_IDENTITY\n',1);l=head.splitlines()
 assert l[0]=='AXBI_CHECKPOINT_V11_GENERAL' and len(l)==28
 for k in ('axbi_covariant_driver.rs','igm_thermal.rs','spectral_ff.rs'):assert (I/'rust/rei_microphysics/src'/k).read_text() in ident
 import io
 s=np.genfromtxt(io.BytesIO(raw(n,'secondary_spectrum.csv')),names=True,delimiter=',');z=np.genfromtxt(io.BytesIO(raw(n,'history.csv')),names=True,delimiter=',')
 assert len(s)==len(z) and np.array_equal(s['a'],z['a'])
 v=np.fromstring(l[26],sep=' ');assert v[7]==s['FF_birth'][-1] and v[9]==s['FF_abs_birth'][-1]
 mode3=l[27]!='NONE';assert mode3==(n not in ('table','fine_table'))
 if mode3:
  d=parsebits(l[27]);assert len(d)==128
  dl=np.log(60/1e-10)/128;xx=1e-10*np.exp((np.arange(128)+.5)*dl)
  assert np.all(1/np.expm1(xx)+d>=0)
  u=s['BB_U'][-1]*15/np.pi**4*np.sum(xx**4*dl*d)
  err=abs(u-s['spectral_U'][-1])/max(abs(u),1e-300);assert err<1e-12
 else:u=0.;err=0.
 cases[n]=dict(mode3=mode3,terminal_spectral_U=float(u),energy_relative=float(err),ff_redshift_work=float(v[7]-v[9]-u) if mode3 else None,gauss_initial=float(z['gauss'][0]),gauss_end=float(z['gauss'][-1]),files=len(m['files']))
for k in ('history.csv','secondary_spectrum.csv','error_components.csv'):
 a=raw('split',k).splitlines(keepends=True);b=raw('resume',k).splitlines(keepends=True)
 assert b''.join(a+b[1 if k=='error_components.csv' else 2:])==raw('live',k)
for k in j(D/'live_RAW.json')['files']:
 if k.startswith('checkpoint/'):assert raw('live',k)==raw('resume',k)
assert int((D/'reject_wrong_donor.exit').read_text())!=0 and 'REC donor IC identity' in (D/'reject_wrong_donor.log').read_text()
b=dict(status='SCOPED_REC_BASS_REC_REI_AND_NATIVE_NULL_VERIFIED',cases=cases,lib_tests=count(D/'lib_tests.log'),targeted_tests=count(D/'regression.log'),restart_byte_identical=True)
# REC physical photon and real ledgers, independently normalized by net change.
q=j(RD/'TIGHT.json');assert q['modes']==1058
for p,h in q['source_hashes'].items():assert sha(p)==h
for p,h in j(RD/'CLOCK_FEEDBACK.json')['source_hashes'].items():assert sha(R/p)==h if not Path(p).is_absolute() else sha(p)==h
rows=[]
for p in sorted(RD.glob('*tight_state.npz')):
 with np.load(p) as z:
  e=z['e'].astype(np.longdouble);v=z['dynamic'].astype(np.longdouble);n=len(e);dp=v[n];d=v[:n];l=v[n+1:];el=np.longdouble('10.198714553953742')
  N=d.sum()+l[0]-l[3]-l[9];U=d@e+l[1]+l[2]+l[5]+l[8]-l[4]-el*l[9];P=dp+l[9]+l[7]-l[6]
  rn=float(abs(N)/np.sum(abs(d)));ru=float(abs(U)/np.sum(abs(d*e)))
  assert rn<1e-9 and ru<1e-9 and abs(P)<1e-7
  rows.append(dict(case=p.name,photon_N_relative=rn,photon_E_relative=ru,real_residual=float(P),combined_number=float(N+P),combined_energy=float(U+el*P)))
r=dict(status='SCOPED_TWO_SIDED_REAL_LINE_AND_CLOCK_FEEDBACK',ledger=rows,regression_tests=int(re.search(r'(\d+) passed',(RD/'regression.log').read_text())[1]),scope=q['scope'])
# REI separate fixed-temperature number-conserving Kompaneets; no actual y effect resolved.
k=j(ID/'KOMPANEETS.json');assert sha(ID.parent/'r118c3c_spectral_exchange/table512_spectrum.csv')==k['source_sha']
assert sha(H/'Downloads/bass_r118c3b_table/history.csv')==k['history_sha']
assert max(x['number_defect'] for x in k['rows'])<1e-11 and max(x['oracle_relative'] for x in k['rows'])<1e-8
i=dict(status='SCOPED_LIVE_SPECTRAL_AND_INDEPENDENT_KOMPANEETS',full_tests=count(ID/'full_tests.log'),post_c9_tests=count(ID/'audit_tests.log'),actual_spectral_energy=cases,kompaneets=k)
for p,v in ((D/'FINAL_RESULTS.json',b),(RD/'FINAL_RESULTS.json',r),(ID/'FINAL_RESULTS.json',i)):
 write(p,v);print(p,v['status'])
print('REC ledger',rows,'BASS',b['lib_tests'],b['targeted_tests'],'REI',i['full_tests'],i['post_c9_tests'])
