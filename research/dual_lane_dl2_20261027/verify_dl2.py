"""Bounded DL2 validation with raw evidence; no previous campaign is rerun."""
import sys,json,hashlib,importlib.util,platform
from pathlib import Path
import numpy as np
import scipy
from scipy.special import sph_harm_y
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'code'))
import polarized_dictionary as D
spec=importlib.util.spec_from_file_location('p8',ROOT/'vendor/polarization.py')
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
blob=(ROOT/'vendor/polarization.py').read_bytes()
assert hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()=='7448ea6701f236fd41d22f3c5cadfd80f482d82f'
ATOL=2e-11
labels=[(f,l,m) for f in ('I','E','B','V') for l in range(5) if f not in ('E','B') or l>=2 for m in range(-l,l+1)]
rows=[]; mixed=[]; gram=[]; gauge=[]
for n in (8,12,20):
    g=D.Grid(n,2*n)
    scalar_error=max(float(np.max(np.abs(g.y(0,l,m)-sph_harm_y(l,m,g.theta,g.phi)))) for l in range(5) for m in range(-l,l+1))
    zs=np.stack([g.z(2,l,m) for l in range(2,5) for m in range(-l,l+1)])
    gram.append({'ntheta':n,'scalar_scipy_error':scalar_error,'spin2_gram_error':float(np.max(np.abs((zs.conj()*g.w)@zs.T-np.eye(len(zs)))))})
    for label in labels:
        c={label:1.}; J=D.synthesize(g,c); out=D.analyze(g,J,4)
        M=np.einsum('n,nij->ij',g.w,J)
        direct=P.collide(g.n,g.w,J,.7); predicted=D.synthesize(g,D.collision_coefficients(c,.7))
        rows.append({'ntheta':n,'field':label[0],'ell':label[1],'m':label[2],
                     'roundtrip_error':max(abs(v-c.get(k,0.)) for k,v in out.items()),
                     'source_error':float(np.max(np.abs(M-D.source_matrix(c)))),
                     'collision_error_at_chi_0_7':float(np.max(np.abs(direct-predicted)))})
    rng=np.random.default_rng(20261027)
    c={label:float(.02*rng.normal()) for label in labels}; c['I',0,0]=2*np.sqrt(4*np.pi)
    J=D.synthesize(g,c); screen=np.stack([g.bt,g.bp],axis=2)
    for chi in (1e-8,.1,1.,8.):
        direct=P.collide(g.n,g.w,J,chi); expected=D.synthesize(g,D.collision_coefficients(c,chi))
        h2=np.einsum('nia,nij,njb->nab',screen,D.hermitian(direct),screen)
        mixed.append({'ntheta':n,'chi':chi,'error':float(np.max(np.abs(direct-expected))),
          'screen_min_eigenvalue':float(np.linalg.eigvalsh(h2).min()),
          'screen_leak':float(np.max(np.abs(np.einsum('nij,nj->ni',direct,g.n)))),
          'monopole_conservation_error':float(abs(np.dot(g.w,np.trace(direct,axis1=1,axis2=2)-np.trace(J,axis1=1,axis2=2))))})
    I,Q,U,V=P.stokes_diagnostic(g.n,J); k=np.argmin(np.abs(g.n),axis=1)
    b=np.eye(3)[k];b-=np.einsum('ni,ni->n',b,g.n)[:,None]*g.n;b/=np.linalg.norm(b,axis=1)[:,None]
    z=np.einsum('ni,ni->n',b,g.bt)+1j*np.einsum('ni,ni->n',b,g.bp)
    own=D.stokes(g,J); truepol=own[1]+1j*own[2]
    gauge.append({'ntheta':n,'converted_error':float(np.max(np.abs(z**2*(Q+1j*U)-truepol))),
                  'unconverted_error':float(np.max(np.abs(Q+1j*U-truepol)))})
# Exact gain-relevant map: 1 I00 + 5 I2 + 5 E2 + 3 V1 coefficients.
active=[('I',0,0)]+[(f,2,m) for f in ('I','E') for m in range(-2,3)]+[('V',1,m) for m in range(-1,2)]
mat=np.stack([D.source_matrix({k:1.}).ravel() for k in active],axis=1)
sv=np.linalg.svd(mat,compute_uv=False)
g=D.Grid(12,24); c={('I',2,1):np.sqrt(6),('E',2,1):1.};J=D.synthesize(g,c)
dark={'source_norm':float(np.linalg.norm(np.einsum('n,nij->ij',g.w,J))),
      'state_norm':float(np.sqrt(np.einsum('n,nij,nij->',g.w,J,J))),
      'decay_error':float(np.max(np.abs(P.collide(g.n,g.w,J,.7)-np.exp(-.7)*J)))}
# All initial l4 moments are invisible to M, but finite shear returns an I2 source.
J=D.synthesize(g,{('I',4,0):1.});S=np.diag([-.2,-.2,.4]); H=.3;Z=np.zeros((3,3));z=np.zeros(3)
s=np.einsum('ni,ij,nj->n',g.n,S,g.n)
md=np.einsum('n,nij->ij',g.w,-(4*H+s)[:,None,None]*J+P.tensor_rate(J,g.n,H,S,z,Z,z))
pred=-.5*np.einsum('n,n,ni,nj,nk,nl,kl->ij',g.w,D.stokes(g,J)[0],g.n,g.n,g.n,g.n,S)
tail={'initial_source_norm':float(np.linalg.norm(np.einsum('n,nij->ij',g.w,J))),
 'Mdot':md.tolist(),'Mdot_norm':float(np.linalg.norm(md)),'independent_J4_contraction_error':float(np.max(np.abs(md-pred)))}
# Deliberate convention/source mutations; do not modify the source kernel.
eonly={('E',2,0):1.}; correct=D.source_matrix(eonly); wrong=-correct
mut={'E_sign_flip_source_discrepancy':float(np.max(np.abs(wrong-correct))),
     'delete_E_source_discrepancy':float(np.max(np.abs(correct))),
     'discard_initial_dark_state_error':dark['state_norm']*np.exp(-.7),
     'ignore_high_tail_streaming_error':tail['Mdot_norm'],
     'ignore_screen_phase_error':max(r['unconverted_error'] for r in gauge)}
# Tail reconstruction vs scattering-source sufficiency are separate quantities.
c={('I',0,0):2*np.sqrt(4*np.pi),('E',4,-2):.1,('B',4,1):.07,('I',4,0):.12}
J=D.synthesize(g,c); low=D.synthesize(g,{k:v for k,v in c.items() if k[1]<=2})
trunc={'lmax_kept':2,'full_field_lmax':4,
       'carrier_L2_error':float(np.sqrt(np.einsum('n,nij,nij->',g.w,J-low,J-low))),
       'gain_source_error':float(np.linalg.norm(np.einsum('n,nij->ij',g.w,J-low)))}
maxima={k:max(r[k] for r in rows) for k in ['roundtrip_error','source_error','collision_error_at_chi_0_7']}
maxima['mixed_field_error']=max(r['error'] for r in mixed)
assert all(v<ATOL for v in maxima.values())
assert all(r['scalar_scipy_error']<ATOL and r['spin2_gram_error']<ATOL for r in gram)
assert all(r['screen_min_eigenvalue']>0 and r['screen_leak']<ATOL and r['monopole_conservation_error']<ATOL for r in mixed)
assert np.linalg.matrix_rank(mat,tol=ATOL)==9 and dark['source_norm']<ATOL and dark['decay_error']<ATOL
assert tail['initial_source_norm']<ATOL and tail['independent_J4_contraction_error']<ATOL
assert all(v>1e-3 for v in mut.values())
res={'scope':'DL2 frozen rest-electron angular source dictionary; no production/Rust/tilted/Einstein history',
 'status':'PASS_SCOPED','source_commit':'cc602e209e7deeb511ab2a1f3b2268d55206c43c',
 'p8_blob':'7448ea6701f236fd41d22f3c5cadfd80f482d82f','atol':ATOL,
 'basis_rows':len(rows),'mixed_rows':len(mixed),'maxima':maxima,'harmonic_checks':gram,
 'gain_map':{'shape':list(mat.shape),'rank':9,'nullity':5,'singular_values':sv.tolist()},
 'dark_quadrupole':dark,'initial_l4_tail_streaming':tail,'finite_tail_reconstruction':trunc,
 'gauge_rows':gauge,'mutations':mut,'rows':rows,'mixed':mixed,
 'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
 'native_subagent':'NOT_RUN_TOOL_NOT_EXPOSED','independent_model_review':'NOT_RUN','old_campaign_reruns':0}
(ROOT/'evidence'/'DL2_RESULTS.json').write_text(json.dumps(res,indent=2))
print(json.dumps({k:v for k,v in res.items() if k not in ('rows','mixed')},indent=2))
