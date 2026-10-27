"""New bounded KM1 experiment. Reads preserved DL2 code, does not rerun its suite."""
from pathlib import Path
import json,sys,hashlib,time,platform
import numpy as np
import scipy
from numpy.polynomial.legendre import leggauss
from scipy.linalg import expm
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'code'),str(ROOT/'vendor')]
from polarized_dictionary import Grid,synthesize,hermitian
from source_memory import Profile,Geometry,DirectHistory,SourceMemory,ALPHA
import polarization as P8
start=time.perf_counter()
expected={'polarization.py':'7448ea6701f236fd41d22f3c5cadfd80f482d82f','polarized_dictionary.py':'639c9a3b2626783da82d759a7a792bf339ec4be9'}
for name,sha in expected.items():
    b=(ROOT/'vendor'/name).read_bytes()
    assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==sha
ATOL=3e-9 # new source-memory sampled identity test, not the DL2 algebraic gate
rows=[];geometry_rows=[];physical_rows=[];endpoints={};tail_rows=[]
for nt in (6,10,16):
    g=Grid(nt,2*nt); prof=Profile('noncommuting');geo=Geometry(g,prof,.6)
    c={('I',0,0):2*np.sqrt(4*np.pi),('I',4,0):.1,('E',2,1):.04,('B',3,-2):.03,('V',1,0):.02}
    J=synthesize(g,c);direct=DirectHistory(geo,J);mem=SourceMemory(geo,J)
    endpoints[nt]=direct.moment(.6)
    for t in (.0,.2,.4,.6):
        d=geo.at(t); E=d['screen'];n=d['e'];H,S=prof.fields(t)
        native=P8.screen_vector_rate(E[:,:,0],n,H,S,np.zeros(3),np.zeros((3,3)),np.zeros(3))
        geometric=geo.screen_rate(t,d)[:,:,0]
        gorth=float(np.max(np.abs(np.einsum('nia,nib->nab',E,E)-np.eye(2))))
        gtrans=float(np.max(np.abs(np.einsum('ni,nia->na',n,E))))
        geometry_rows.append({'ntheta':nt,'time':t,'screen_orth_error':gorth,'screen_transverse_error':gtrans,'P8_screen_rate_error':float(np.max(np.abs(native-geometric))), 'solid_angle_defect':float(abs(d['w'].sum()-4*np.pi)/(4*np.pi))})
        Jt=direct.state(t);M=direct.moment(t);Pt=np.eye(3)-np.einsum('ni,nj->nij',n,n)
        col=prof.rate(t)*(ALPHA*np.einsum('nia,ab,nbj->nij',Pt,M,Pt)-Jt)
        traceC=float(np.einsum('n,nii->',d['w'],col));rho=float(np.trace(M))
        screen_phys=np.einsum('nia,nij,njb->nab',E,hermitian(Jt),E)
        physical_rows.append({'ntheta':nt,'time':t,'screen_min_eigenvalue':float(np.linalg.eigvalsh(screen_phys).min()),'collision_energy_balance_relative':abs(traceC)/(prof.rate(t)*rho),'rho':rho})
        if t>0:
            for order in (4,8,16,32):
                mrec=mem.evaluate_with_source(t,direct.moment,order)
                jrec=mem.reconstruct_with_source(t,direct.moment,order)
                rows.append({'ntheta':nt,'time':t,'time_quadrature_order':order,'moment_max_abs':float(np.max(np.abs(mrec-M))),'carrier_max_abs':float(np.max(np.abs(jrec-Jt)))})
    if nt==10:
        control=(g,prof,geo,J,direct,mem)
# Same equations, tighter time tolerances only; independent from angular refinement.
g,p,geo,J,h,mem=control
geo_f=Geometry(g,p,.6,rtol=3e-13,atol=3e-15)
h_f=DirectHistory(geo_f,J,rtol=3e-13,atol=3e-15)
time_sensitivity=float(np.max(np.abs(h_f.moment(.6)-h.moment(.6))))
# Angular convergence is empirical, not a certified continuum-tail bound.
angular=[{'coarse':a,'fine':b,'endpoint_moment_max_abs':float(np.max(np.abs(endpoints[a]-endpoints[b])))} for a,b in ((6,10),(10,16))]
# Initial gain-null I40: keep complete signed difference, not its zero source.
gt=Grid(10,20);geot=Geometry(gt,Profile('lrs'),.6); Jtail=synthesize(gt,{('I',4,0):.1})
ht=DirectHistory(geot,Jtail);mt=SourceMemory(geot,Jtail)
for t in np.linspace(0,.6,13):
    b=mt.initial_term(t);M=ht.moment(t);rec=mt.evaluate_with_source(t,ht.moment,24)
    tail_rows.append({'time':float(t),'direct_Mzz':float(M[2,2]),'initial_memory_Mzz':float(b[2,2]),'gain_memory_Mzz':float((rec-b)[2,2]),'moment_norm':float(np.linalg.norm(M)),'initial_term_norm':float(np.linalg.norm(b)),'residual':float(np.max(np.abs(rec-M)))})
# Positive pair version: not positivity certification of a signed basis itself.
Jbase=synthesize(gt,{('I',0,0):2*np.sqrt(4*np.pi)})
hbase=DirectHistory(geot,Jbase);hplus=DirectHistory(geot,Jbase+Jtail)
pair_error=float(np.max(np.abs((hplus.moment(.6)-hbase.moment(.6))-ht.moment(.6))))
# Tail source instantaneous derivative matches prior derived formula without old campaign rerun.
z=geot.at(0.); H,S=geot.profile.fields(0.);n=z['e']; s=np.einsum('ni,ij,nj->n',n,S,n)
mdot=np.einsum('n,nij->ij',z['w'],-(4*H+s)[:,None,None]*Jtail+P8.tensor_rate(Jtail,n,H,S,np.zeros(3),np.zeros((3,3)),np.zeros(3)))
dt=1e-5; fd=(mt.initial_term(dt)-mt.initial_term(0.))/dt
# Counterfactual deleting physical angular Jacobian: initial and integrand both changed, target unchanged.
t=.6; a=geo.at(t);Ea=a['screen']; vbad=g.w*a['mu']**4
bad0=np.exp(-p.kappa(t))*np.einsum('n,nia,nab,njb->ij',vbad,Ea,mem.X0,Ea)
bad=bad0.copy(); gx,gw=leggauss(32)
for ss,ww in zip(t*(gx+1)/2,t*gw/2):
    b=geo.at(ss); Z=np.einsum('nia,nja->nij',Ea,b['screen']);pref=ALPHA*p.rate(ss)*np.exp(-(p.kappa(t)-p.kappa(ss)))
    bad+=ww*pref*np.einsum('n,nia,ab,njb->ij',vbad/b['mu']**4,Z,h.moment(ss),Z)
# Lost chronological ordering in A != exponential of integrated B for noncommuting fields.
x,w=leggauss(32);integ=np.zeros((3,3))
for ss,ww in zip(t*(x+1)/2,t*w/2):
    H,S=p.fields(ss);integ+=ww*(H*np.eye(3)+S)
naiveA=expm(-integ)
B0=p.fields(0.)[0]*np.eye(3)+p.fields(0.)[1];B1=p.fields(.6)[0]*np.eye(3)+p.fields(.6)[1]
mutations={'discard_initial_tail_residual':float(np.linalg.norm(mt.initial_term(.6))),
 'omit_angular_jacobian_moment_error':float(np.max(np.abs(bad-h.moment(.6)))),
 'remove_chronological_order_A_error':float(np.max(np.abs(naiveA-a['A']))),
 'B_commutator_norm':float(np.linalg.norm(B0@B1-B1@B0))}
# Kernel norm bound and distinct-time histories: diagnostic samples only, not global certificate.
krows=[]
for tt,ss in ((.2,0.),(.4,.2),(.6,.4),(.6,0.),(.6,.6)):
    norm=float(np.linalg.norm(mem.kernel(tt,ss),2));bound=mem.kernel_bound(tt,ss)
    krows.append({'t':tt,'s':ss,'norm':norm,'bound':bound})
assert all(r['moment_max_abs']<ATOL and r['carrier_max_abs']<ATOL for r in rows if r['time_quadrature_order']>=16)
assert max(r['P8_screen_rate_error'] for r in geometry_rows)<2e-11
assert max(r['screen_transverse_error'] for r in geometry_rows)<2e-11
assert all(r['screen_min_eigenvalue']>0 for r in physical_rows)
assert max(r['residual'] for r in tail_rows)<ATOL
assert pair_error<ATOL and time_sensitivity<ATOL
assert all(r['norm']<=r['bound']*(1+1e-10) for r in krows)
assert mutations['discard_initial_tail_residual']>1e-4 and mutations['omit_angular_jacobian_moment_error']>1e-3 and mutations['remove_chronological_order_A_error']>1e-5
result={'unit':'KM-1','status':'PASS_SCOPED_SOURCE_MEMORY_CONSTRUCTION',
 'scope':'prescribed finite-shear Bianchi I, untilted cold Thomson; continuum derivation and same-quadrature Duhamel residual; no standalone Volterra source solve',
 'parent_commit':'e3e829903294f437373369420b1dff95f6592e85','source_blobs':expected,
 'identity_gate':ATOL,'geometry_gate':2e-11,'rows':rows,'geometry':geometry_rows,'physical':physical_rows,
 'angular_comparisons':angular,'time_tolerance_endpoint_difference':time_sensitivity,
 'tail':tail_rows,'positive_pair_linearity_error':pair_error,'initial_tail_derivative':mdot.tolist(),'initial_term_fd_derivative_error_dt1e_5':float(np.max(np.abs(fd-mdot))),
 'mutations':mutations,'kernel_norm_samples':krows,
 'new_direct_ivps':7,'new_geometry_histories':5,'old_campaign_reruns':0,
 'native_subagent':'NOT_RUN_TOOL_NOT_EXPOSED','independent_model_review':'NOT_RUN','native_Rust':'NOT_RUN',
 'elapsed_s':time.perf_counter()-start,'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__}}
(ROOT/'evidence/KM1_RESULTS.json').write_text(json.dumps(result,indent=2))
brief={k:v for k,v in result.items() if k not in ('rows','geometry','physical','tail')}
brief['max_moment_identity_error_order32']=max(r['moment_max_abs'] for r in rows if r['time_quadrature_order']==32)
brief['max_carrier_identity_error_order32']=max(r['carrier_max_abs'] for r in rows if r['time_quadrature_order']==32)
brief['tail_endpoint']=tail_rows[-1]
brief['collision_balance_by_grid']=[{'ntheta':n,'max_defect':max(r['collision_energy_balance_relative'] for r in physical_rows if r['ntheta']==n)} for n in (6,10,16)]
(ROOT/'evidence/RESULTS_SUMMARY.json').write_text(json.dumps(brief,indent=2))
print(json.dumps(brief,indent=2))
