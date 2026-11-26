import json,hashlib,gzip,io,re
from pathlib import Path
import numpy as np
H=Path('/home/cosmosapjw');B=H/'worktrees/bass-r109-native-20261124';R=H/'Downloads/htt_r109_original_rec';I=H/'worktrees/rei-htt-thomson-20261124'
D=B/'research/r118c3f_four_memory';RD=R/'research/r118c3f_directional_history';ID=I/'research/r118c3f_signed_thermal'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def hb(b):return hashlib.sha256(b).hexdigest()
def j(p):return json.loads(Path(p).read_text())
def write(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def tests(p):
 a=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;',Path(p).read_text());assert a and all(x[0]=='ok' and x[2]=='0' for x in a);return sum(int(x[1]) for x in a)
def checklinks(rows,root):
 for p,h in rows.items():assert sha(root/p)==h,p
for p in (B/'research/r118c3e_geometry_tracks/INPUT.sha256',D/'MULTI.sha256',D/'TRIPLE.sha256'):
 for line in p.read_text().splitlines():
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
w=j(D/'PHYSICAL_WEDGE.json')
assert len(w['rows'])==5 and all(x['rank_span']==4 for x in w['rows'])
assert all(.6<x['projected_fraction']<=1.00000001 for x in w['rows'])
wb=next(x for x in w['rows'] if x['name']=='base');wf=next(x for x in w['rows'] if x['name']=='fine')
assert abs(wb['native_B3']/wf['native_B3']-1)<1e-4
for x in w['rows']:
 assert sha(D/(x['name']+'.geom'))==x['geometry_sha']
 for key in ('native_B3','quadratic_norm','projected_fraction','gauss'):assert np.isfinite(x[key])
for name in ('zerofine','plusfine'):
 donor=j(D/(name+'_DONOR.json'))
 assert sha(donor['source'])==donor['source_sha'] and sha(D/(name+'_CLOCK.csv'))==donor['clock_sha']
 source=j(donor['source']);assert len(source['history']['states'])==701 and source['initial']==donor['initial']
 assert sha(D/(name+'_replay.csv'))==a['early'][name]['history_sha']
 assert sha(D/(name+'_replay.state'))==a['early'][name]['state_sha']
delta_old=j(B/'research/r118c3e_geometry_tracks/TRIPLE_RESULTS.json')['deltas']['plustight']['T']
late=a['deltas']['plustight']['T'];late0=a['deltas']['plus']['T'];assert abs(late/late0-1)<.002
dr=j(RD/'DONORS.json')['rows']
for x in dr:
 name=x['case'];f=RD/(name+('_tight.json' if x['tol']==3e-13 else '_normal.json'))
 assert sha(f)==x['donor_sha']; assert sha(B/'research/r118c3e_geometry_tracks'/(name+'.csv'))==x['clock_sha']
 z=j(f);assert len(z['history']['states'])==701
 assert z['initial']['T_m_K']==x['T'] and z['initial']['x_HII']==x['x']
def dt(tol):return next(x['T'] for x in dr if x['case']=='plusfine' and x['tol']==tol)-next(x['T'] for x in dr if x['case']=='zerofine' and x['tol']==tol)
assert abs(dt(3e-13)/dt(1e-11)-1)<.002
directions={}
for n in ('z64','p64','p128','z128','p128_t','p128_saved','p128_a','z256','p256'):
 r=j(RD/(n+'.json'));assert r['max_mean_defect']<1e-8 and r['max_matrix_residual']<1e-10 and r['max_area_defect']<1e-8
 assert sha(B/'research/r118c3e_geometry_tracks'/(r['case']+'.csv'))==r['coframe_sha']
 assert sha(R/'research/r118c2w_causal/FULL_128.npz')==r['prefix_sha']
 assert sha(R/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')==r['rates_sha']
 with np.load(RD/(n+'.npz')) as z:
  assert z['final'].shape==(r['nray'],314) and np.isfinite(z['final']).all()
  assert z['rows'].shape[0]==r['steps'] and z['rows'][-1,1]==r['terminal_rhs']
  assert r['min_lookback']>max(np.diff(z['eta']))
 directions[n]=r
# Actual accepted full angular history read-back, not just endpoint.
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table
from full_bianchi_hyrec.trajectory.hmla_flrw import KB_NATIVE_EV_K
tab=_canonical_twophoton_table(R/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')
with np.load(RD/'ACCEPTED_DIRECTIONAL.npz') as z:
 assert z['outgoing'].shape==(128,128,314)
 assert str(z['prefix_sha'])==directions['p128_saved']['prefix_sha'] and str(z['coframe_sha'])==directions['p128_saved']['coframe_sha']
 assert np.isfinite(z['outgoing']).all() and np.all(np.diff(z['eta'])>0)
 with np.load(RD/'p128_saved.npz') as q:assert np.array_equal(z['outgoing'][-1],q['final'])
 bb=1/np.expm1(tab.energy_eV[None,None,:]/(KB_NATIVE_EV_K*2.7255*np.exp(-z['eta'])[:,None,None]))
 min_occ=float(np.min(bb+z['outgoing'][:,:,:311]));assert min_occ>=0
 history_sha=sha(RD/'ACCEPTED_DIRECTIONAL.npz')
def rhs(n):return directions[n]['terminal_rhs']
diffs={k:rhs(p)-rhs(z) for k,p,z in [('64x32','p64','z64'),('128x32','p128_t','z128'),('128x128','p128_saved','z128'),('128x512','p128_a','z128'),('256x128','p256','z256')]}
assert min(diffs.values())>0
k=j(ID/'RESULTS.json');checklinks(k['source_hashes'],I)
assert all(abs(x['ledger'])<1e-15 and abs(x['compton_number_error'])<1e-12*abs(x['ff_number']) for x in k['rows'])
assert abs(k['rows'][-1]['relative_compton'])<.01 and max(abs(x['residual']) for x in k['closed'])<1e-14
with np.load(ID/'SPECTRUM.npz') as z:
 assert len(z['x'])==1024 and np.all(1/np.expm1(z['x'])+z['delta']/z['c']>=0)
 assert abs(float(z['delta'].sum())-k['rows'][-1]['total_delta_number'])<1e-25
b=dict(status='SCOPED_TIGHT_MATCHED_TRIPLE_AND_FOUR_MEMORY',cases=cases,tests_lib=tests(D/'lib_tests.log'),tests_targeted=tests(D/'regression.log'),scope=a['scope'],physical_wedge=w['rows'],old_late_deltaT=delta_old,tight_late_deltaT=late,late_refinement_relative=abs(late/late0-1))
r=dict(status='SCOPED_SELF_GENERATED_DIRECTIONAL_HISTORY',directions=directions,matched_rhs_differences=diffs,accepted_history_sha=history_sha,min_virtual_occupation=min_occ,donor_deltaT=dt(3e-13),donor_refinement_relative=abs(dt(3e-13)/dt(1e-11)-1),tests=int(re.search(r'(\d+) passed',(RD/'regression.log').read_text())[1]),scope='prescribed actual gas and accepted isotropic prefix; generated common-atom directional outgoing; no autonomous FULL HHe chemistry, no exterior reaction closure')
i=dict(status='SCOPED_SIGNED_COMPTON_FF_ACTUAL_CLOCK',full_rust_tests=tests(ID/'full_tests.log'),python_tests=int(re.search(r'(\d+) passed',(ID/'regression.log').read_text())[1]),max_ledger=max(abs(x['ledger']) for x in k['rows']),finest=k['rows'][-1],closed=k['closed'],scope=k['scope'])
for p,v in ((D,b),(RD,r),(ID,i)):write(p/'FINAL_RESULTS.json',v);print(p.name,v['status'])
print('donor',r['donor_deltaT'],'late',late,'old',delta_old,'late refine',b['late_refinement_relative'],'direction diffs',diffs,'min occupation',min_occ,'BASS tests',b['tests_lib'],b['tests_targeted'],'REC',r['tests'],'REI',i['full_rust_tests'],i['python_tests'])
