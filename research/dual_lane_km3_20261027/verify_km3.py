"""Bounded independent-Volterra experiment; no parent campaign is rerun.

The production solver input never contains the direct reference. The latter is
constructed separately, then used only to measure discrepancies. This validator
also separates time error, angular error, kernel quadrature error, and geometry.
"""
from pathlib import Path
import hashlib,json,sys,time,platform
import numpy as np
import scipy
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'code'),str(ROOT/'vendor')]
from source_memory import Profile,Geometry,DirectHistory,SourceMemory,ALPHA
from polarized_dictionary import Grid,synthesize,hermitian
import polarization as P8
from volterra_solver import VolterraHistory,solve_global_history
START=time.perf_counter();T=.55
GATE=3e-9;ALG=2e-11;OFFGRID=4e-8
counts={'geometry_histories':0,'direct_ivps':0,'Volterra_solves':0,'uncompressed_reference_solves':0}
for row in json.loads((ROOT/'SOURCE_MAP.json').read_text())['vendor']:
    b=(ROOT/row['path']).read_bytes()
    assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob']

def geom(g,kind,**kw):
    counts['geometry_histories']+=1;return Geometry(g,Profile(kind),T,**kw)
def direct(geo,J,**kw):
    counts['direct_ivps']+=1;return DirectHistory(geo,J,**kw)
def solve(mem,panels,order=4):
    counts['Volterra_solves']+=1;return VolterraHistory(mem,np.linspace(0,T,panels+1),order)
def initial(g):
    return synthesize(g,{('I',0,0):2*np.sqrt(4*np.pi),('I',4,1):.12,
        ('E',2,-1):.035,('B',3,2):.026,('V',1,-1):.018})
def err(a,b):return float(np.max(np.abs(a-b)))

# Three different angular discretizations, one new direct reference per grid.
bases={}
for nt in (6,10,16):
    g=Grid(nt,2*nt);geo=geom(g,'noncommuting');J=initial(g)
    bases[nt]=(g,geo,J,direct(geo,J),SourceMemory(geo,J))
g,geo,J,d,mem=bases[10]
time_rows=[];histories={}
for N in (8,16,32,64,128):
    h=solve(mem,N);histories[N]=h
    row={'angular_ntheta':10,'panels':N,'dt':T/N,
         'moment_endpoint_error':err(h.moment(T),d.moment(T)),
         'carrier_endpoint_error':err(h.state(T),d.state(T)),
         'moment_mesh_error':max(err(h.moments[i],d.moment(t)) for i,t in enumerate(h.times)),
         'midpoint_source_error':max(err(h.panels[i,1],d.moment((a+b)/2)) for i,(a,b) in enumerate(zip(h.times[:-1],h.times[1:]))),
         'max_block_residual':max(h.block_residuals),'max_block_condition':max(h.block_conditions),
         'max_endpoint_consistency':max(h.endpoint_consistency)}
    time_rows.append(row)
fine=histories[128]
orders=[]
for a,b in zip(time_rows[:-1],time_rows[1:]):
    orders.append({'coarse':a['panels'],'fine':b['panels'],**{key:float(np.log2(a[key]/b[key])) for key in ('moment_endpoint_error','carrier_endpoint_error')}})
# Endpoint errors and independent off-grid interpolation/reconstruction errors.
offgrid=[]
for t in T*np.array([.037,.113,.227,.413,.777,.923]):
    offgrid.append({'time':float(t),'moment_error':err(fine.moment(t),d.moment(t)),
        'carrier_error':err(fine.state(t),d.state(t)),
        'source_interpolant_error':err(fine.source_polynomial(t),d.moment(t)),
        'collocation_defect':err(fine.source_polynomial(t),fine.moment(t)),
        'global_history_reconstruction_error':err(fine.global_reconstruction(t,order=8),fine.moment(t))})

# Angular accuracy is a separate question from same-grid representation equality.
angular_rows=[];physical=[];fines={10:fine}
for nt in (6,16):
    gg,ggg,jj,dd,mm=bases[nt];fines[nt]=solve(mm,128)
for nt in (6,10,16):
    gg,ggg,jj,dd,mm=bases[nt];hh=fines[nt]
    for t in (0.,T/3,2*T/3,T):
        z=ggg.at(t);n=z['e'];E=z['screen'];w=z['w'];jt=hh.state(t);M=ggg.moment(t,jt)
        P=np.eye(3)-np.einsum('ni,nj->nij',n,n)
        coll=ggg.profile.rate(t)*(ALPHA*np.einsum('nia,ab,nbj->nij',P,M,P)-jt)
        rho=float(np.trace(M));bal=float(np.einsum('n,nii->',w,coll))
        h2=np.einsum('nia,nij,njb->nab',E,hermitian(jt),E)
        physical.append({'ntheta':nt,'time':t,'source_error_same_grid':err(hh.moment(t),dd.moment(t)),
            'screen_min_eigenvalue':float(np.linalg.eigvalsh(h2).min()),
            'screen_transverse_error':float(np.max(np.abs(np.einsum('nij,nj->ni',jt,n)))),
            'solid_angle_defect':float(abs(w.sum()-4*np.pi)/(4*np.pi)),
            'collision_energy_balance_relative':abs(bal)/(ggg.profile.rate(t)*rho)})
for a,b in ((6,10),(10,16)):
    angular_rows.append({'coarse':a,'fine':b,
      'direct_endpoint_gap':err(bases[a][3].moment(T),bases[b][3].moment(T)),
      'Volterra_endpoint_gap':err(fines[a].moment(T),fines[b].moment(T))})
# Geometry/direct time tolerance sensitivity on a single shared angular grid.
gt=geom(g,'noncommuting',rtol=3e-13,atol=3e-15)
dt=direct(gt,J,rtol=3e-13,atol=3e-15);ht=solve(SourceMemory(gt,J),128)
sensitivity={'direct_tolerance_endpoint_change':err(dt.moment(T),d.moment(T)),
 'Volterra_geometry_tolerance_change':err(ht.moment(T),fine.moment(T)),
 'tight_reference_same_grid_error':err(ht.moment(T),dt.moment(T))}
# Static exact P8 semigroup is valid on the undeformed GL quadrature.
gs=Grid(8,16);geos=geom(gs,'static');Js=initial(gs);ms=SourceMemory(geos,Js)
static=[]
for N in (16,32,64):
    hs=solve(ms,N);exact=P8.collide(gs.n,gs.w,Js,geos.profile.kappa(T))
    static.append({'panels':N,'carrier_error':err(hs.state(T),exact),
                   'moment_error':err(hs.moment(T),geos.moment(T,exact))})
# Transparent finite-shear limit: only full initial carrier transport remains.
geof=geom(gs,'free');mf=SourceMemory(geof,Js);hf=solve(mf,16)
free={'moment_error':err(hf.moment(T),mf.initial_term(T)),
 'carrier_error':err(hf.state(T),mf.reconstruct_with_source(T,lambda t:np.zeros((3,3)),4))}
# Source-null angular tail survives finite-shear transport and collision.
gl=Grid(10,20);glgeo=geom(gl,'lrs');tail=synthesize(gl,{('I',4,0):.13})
base=synthesize(gl,{('I',0,0):2*np.sqrt(4*np.pi)})
dl=direct(glgeo,tail);db=direct(glgeo,base);dp=direct(glgeo,base+tail)
ml=SourceMemory(glgeo,tail);tail_convergence=[]
for N in (32,64,128):
    hl=solve(ml,N)
    tail_convergence.append({'panels':N,'moment_error':err(hl.moment(T),dl.moment(T))})
hb=solve(SourceMemory(glgeo,base),128);hp=solve(SourceMemory(glgeo,base+tail),128)
tail_rows=[]
for t in np.linspace(0,T,12):
    mm=hl.moment(t);bb=ml.initial_term(t)
    tail_rows.append({'time':float(t),'Volterra_Mzz':float(mm[2,2]),'direct_Mzz':float(dl.moment(t)[2,2]),
      'initial_memory_Mzz':float(bb[2,2]),'gain_history_Mzz':float((mm-bb)[2,2]),
      'source_error':err(mm,dl.moment(t))})
pair={'Volterra_pair_linearity_error':err(hp.moment(T)-hb.moment(T),hl.moment(T)),
 'direct_pair_linearity_error':err(dp.moment(T)-db.moment(T),dl.moment(T)),
 'pair_difference_cross_solver_error':err(hp.moment(T)-hb.moment(T),dp.moment(T)-db.moment(T))}
# Product-quadrature sensitivity, not temporal panel refinement.
qrows=[]
for order in (2,8):
    hq=solve(mem,32,order=order)
    qrows.append({'quadrature_order':order,'panels':32,'endpoint_change_from_order4':err(hq.moment(T),histories[32].moment(T))})
# Explicit uncompressed history oracle, independent of accumulator propagation.
g6,geo6,J6,d6,mem6=bases[6];ts=np.linspace(0,T,5)
counts['Volterra_solves']+=1;hc=VolterraHistory(mem6,ts)
counts['uncompressed_reference_solves']+=1;full,stages=solve_global_history(mem6,ts)
assembly={'moment_difference':err(hc.moments,full),'stage_difference':err(hc.panels,stages)}
# Identical prefix is unaffected by whether later panels are solved.
tsf=np.linspace(0,T,9);counts['Volterra_solves']+=2
hprefix=VolterraHistory(mem6,tsf[:5]);hall=VolterraHistory(mem6,tsf)
causality={'prefix_moment_difference':err(hprefix.moments,hall.moments[:5])}
# A deliberate source-only initialization erases an actually nonzero history.
hzero=solve(SourceMemory(glgeo,np.zeros_like(tail)),32)
mutations={'discard_full_initial_tail_endpoint_error':err(hzero.moment(T),hl.moment(T)),
 'initial_tail_source_norm':float(np.linalg.norm(ml.initial_term(0))),
 'surviving_tail_endpoint_norm':float(np.linalg.norm(hl.moment(T)))}

# Fixed acceptance, separated by evidence type.
assert time_rows[-1]['moment_mesh_error']<GATE
assert time_rows[-1]['carrier_endpoint_error']<GATE
assert all(3.5<r['moment_endpoint_error']<4.5 and 3.5<r['carrier_endpoint_error']<4.5 for r in orders[:2])
assert max(r['max_block_residual'] for r in time_rows)<ALG
assert all(max(r[k] for r in offgrid)<OFFGRID for k in ('moment_error','carrier_error','source_interpolant_error'))
assert max(r['global_history_reconstruction_error'] for r in offgrid)<5e-11
assert all(r['screen_min_eigenvalue']>0 and r['screen_transverse_error']<ALG for r in physical)
assert max(assembly.values())<5e-11 and causality['prefix_moment_difference']==0.
assert static[-1]['carrier_error']<GATE and max(free.values())<ALG
assert tail_convergence[-1]['moment_error']<GATE and max(pair.values())<GATE
assert max(sensitivity.values())<GATE and qrows[-1]['endpoint_change_from_order4']<5e-11
assert mutations['discard_full_initial_tail_endpoint_error']>1e-4
assert counts['direct_ivps']<=10 and counts['geometry_histories']<=8 and counts['Volterra_solves']<=30
result={'unit':'KM-3','status':'PASS_SCOPED_INDEPENDENT_VOLTERRA','scope':'prescribed finite-shear Bianchi I, untilted cold Thomson, finite angular grid; not production/QState/Rust/Einstein history',
 'parent_commit':'cc22af0b900dc9d2e6987e70f6ba9581f971831b','interval_u':[0,T],
 'method':'quadratic Lobatto source collocation, GL product integration; 18x18 causal panel solves; algebraically factored angular history',
 'source_is_unknown':True,'direct_source_used_by_solver':False,'hypothesis':'No amplitude expansion; source representation differs from kinetic state dimension',
 'gates':{'fine_time_error':GATE,'algebraic':ALG,'offgrid':OFFGRID,'coarse_order_interval':[3.5,4.5]},
 'time_rows':time_rows,'orders':orders,'offgrid':offgrid,'angular_rows':angular_rows,'physical':physical,
 'time_geometry_sensitivity':sensitivity,'static':static,'free':free,'tail':tail_rows,'tail_convergence':tail_convergence,'positive_pair':pair,
 'quadrature_rows':qrows,'global_assembly':assembly,'causality':causality,'mutations':mutations,
 'counts':counts,'old_campaign_reruns':0,'prior_budget_reset':False,
 'native_subagent':'NOT_RUN_TOOL_NOT_EXPOSED','independent_model_review':'NOT_RUN','Rust_runner':'NOT_RUN',
 'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'elapsed_s':time.perf_counter()-START}
(ROOT/'evidence/KM3_RESULTS.json').write_text(json.dumps(result,indent=2))
brief={k:v for k,v in result.items() if k not in ('offgrid','physical','tail')}
brief['offgrid_max']={k:max(r[k] for r in offgrid) for k in ('moment_error','carrier_error','source_interpolant_error','collocation_defect','global_history_reconstruction_error')}
brief['collision_balance_by_grid']=[{'ntheta':n,'max_defect':max(r['collision_energy_balance_relative'] for r in physical if r['ntheta']==n)} for n in (6,10,16)]
brief['tail_endpoint']=tail_rows[-1]
(ROOT/'evidence/RESULTS_SUMMARY.json').write_text(json.dumps(brief,indent=2))
print(json.dumps(brief,indent=2))
