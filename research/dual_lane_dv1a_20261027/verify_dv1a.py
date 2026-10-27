"""New DV1-A bounded instantaneous campaign, no previous IVPs/campaigns rerun."""
from pathlib import Path
import sys,json,time,hashlib,ast,copy,platform
import numpy as np
import scipy,sympy
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'code'),str(ROOT/'vendor')]
import harmonic_streaming as HS
import direct_oracle as DO
import legacy_scalar as LS
from polarized_dictionary import Grid,synthesize,stokes,hermitian

ATOL=2e-11
FIELDS=[('isotropic',.7,np.zeros((3,3))),('lrs',.4,np.diag([-.2,-.2,.4])),
        ('strong_offdiag',.3,np.array([[.31,.17,-.09],[.17,-.12,.11],[-.09,.11,-.19]]))]
GRIDS=[8,12,20]
MODES=[(f,l,m) for f in ('I','E','B','V') for l in range(5) if f not in ('E','B') or l>=2 for m in range(-l,l+1)]

def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def strip(node):
    node=copy.deepcopy(node)
    for n in ast.walk(node):
        if isinstance(n,(ast.FunctionDef,ast.ClassDef,ast.Module)) and n.body and isinstance(n.body[0],ast.Expr) and isinstance(n.body[0].value,ast.Constant) and isinstance(n.body[0].value.value,str):n.body.pop(0)
    return ast.dump(node,include_attributes=False)

def identity():
    out={}
    for f,h in [('polarization.py','7448ea6701f236fd41d22f3c5cadfd80f482d82f'),('polarized_dictionary.py','639c9a3b2626783da82d759a7a792bf339ec4be9'),('archive_hierarchy_coeff.py','9ed97cab33d1ab7a458c44a56e53ab114a9142f9')]:
        b=(ROOT/'vendor'/f).read_bytes();got=blob(b);assert got==h,(f,got)
        out[f]={'identity':'BYTE_IDENTITY_GIT_BLOB','blob':got,'sha256':hashlib.sha256(b).hexdigest()}
    def functions(f):return {n.name:n for n in ast.parse((ROOT/'vendor'/f).read_text()).body if isinstance(n,ast.FunctionDef)}
    old,new=functions('archive_hierarchy.py'),functions('current_kernel_excerpt.py')
    for name in ['_contract_one','_contract_two','_outer_sigma','hierarchy_rhs']:
        assert strip(old[name])==strip(new[name])
        out['H::'+name]={'identity':'EXECUTABLE_AST_TO_PRESERVED_LIVE_READ_EXCERPT','sha256':hashlib.sha256(strip(old[name]).encode()).hexdigest()}
    out['helper_context']={'identity':'PRESERVED_ARCHIVAL_HELPERS','not_claimed':'whole-current-H/PSTF-package execution','current_hierarchy_blob':'d1dc99a9f662afa423dc7d3545645ad5b0469ab1','current_pstf_blob':'1b33670ea53e827261f0a13f97d9cd353da9369d'}
    return out

def main():
    started=time.perf_counter();ids=identity();rows=[];physical=[];legacy=[];mutations={}
    sample={};rng=np.random.default_rng(20261027)
    c={k:float(.02*rng.normal()) for k in MODES};c['I',0,0]=3*np.sqrt(4*np.pi)
    for n in GRIDS:
        g=Grid(n,2*n)
        for name,H,S in FIELDS:
            for mode in MODES:
                seed={mode:1.}
                direct=DO.projected_rhs(g,seed,H,S,0.,6)
                predicted=HS.coefficient_rhs(seed,H,S,0.,6)
                err=max(abs(v-predicted.get(k,0.)) for k,v in direct.items())
                rows.append({'ntheta':n,'nphi':2*n,'field':name,'input_channel':mode[0],'ell':mode[1],'m':mode[2],'max_rhs_coefficient_error':float(err)})
                assert err<ATOL,rows[-1]
            # Physical mixed fixture, no amplitude truncation. Positivity only at input.
            J=synthesize(g,c);screen=np.stack([g.bt,g.bp],axis=2)
            H2=np.einsum('nia,nij,njb->nab',screen,hermitian(J),screen)
            min_eig=float(np.linalg.eigvalsh(H2).min());assert min_eig>0
            nu=1.3;dr=DO.direct_rhs(g,c,H,S,nu)
            pred=HS.coefficient_rhs(c,H,S,nu,6);pr=DO.projected_rhs(g,c,H,S,nu,6)
            err=max(abs(v-pred.get(k,0.)) for k,v in pr.items());assert err<ATOL
            I,Q,U,V=stokes(g,J);Id,Qd,Ud,Vd=stokes(g,dr)
            rho=float(np.dot(g.w,I));pi=np.einsum('n,n,nij->ij',g.w,I,np.einsum('ni,nj->nij',g.n,g.n)-np.eye(3)/3)
            balance=abs(np.dot(g.w,Id)+4*H*rho+np.sum(S*pi));assert balance<ATOL
            coord=DO.spin_coordinate_rhs(g,c,H,S)
            stream=DO.direct_rhs(g,c,H,S,0.);st=stokes(g,stream)
            spinerr=float(np.max(np.abs(st[1]+1j*st[2]-coord['P'])));assert spinerr<ATOL
            physical.append({'ntheta':n,'field':name,'total_rhs_coefficient_error':float(err),'input_screen_min_eigenvalue':min_eig,'energy_balance_absolute':float(balance),'spin_coordinate_vs_P8_pointwise_error':spinerr,'sigma_over_H_norm2':float(np.linalg.norm(S,2)/abs(H))})
            # Reuse scalar H dense and J coefficient kernels, no polarization misidentification.
            ic={k:v for k,v in c.items() if k[0]=='I'}
            i_rhs=HS.coefficient_rhs(ic,H,S,0.,6);j_rhs=LS.coefficient_reference(ic,H,S,4)
            jerr=max(abs(v-i_rhs[k]) for k,v in j_rhs.items());assert jerr<ATOL
            iraw=stokes(g,DO.direct_rhs(g,ic,H,S,0.))[0]
            dense=LS.dense_reference(g,I,H,S);exact=LS.dense_moments(g,iraw,2)
            herr=max(float(np.max(np.abs(np.asarray(dense[l])-exact[l]))) for l in range(3));assert herr<ATOL
            legacy.append({'ntheta':n,'field':name,'J_coefficient_l0_to_l4_error':float(jerr),'H_dense_l0_to_l2_error':herr})
        print('grid',n,'complete, rows',len(rows),flush=True)
    # All selection-rule blocks and a CAS-checkable E->B fixture.
    S=FIELDS[2][2];a=HS.streaming_matrix(2,4,6,0.,S);lo,li=HS.labels(2,6),HS.labels(2,4)
    forbidden=[];even_im=[];odd_re=[]
    for i,(l,m) in enumerate(lo):
        for j,(lp,mp) in enumerate(li):
            if abs(l-lp)>2:forbidden.append(abs(a[i,j]))
            if (l-lp)%2==0:even_im.append(abs(a[i,j].imag))
            else:odd_re.append(abs(a[i,j].real))
    sel={'abs_delta_l_gt2':float(max(forbidden)),'same_parity_EB_leak':float(max(even_im)),'opposite_parity_EE_BB_leak':float(max(odd_re)),'nonzero_EB_block_max':float(np.max(np.abs(a.imag)))}
    assert max(sel[k] for k in ['abs_delta_l_gt2','same_parity_EB_leak','opposite_parity_EE_BB_leak'])<ATOL
    ebc={('E',2,2):1.};S_lrs=np.diag([-.2,-.2,.4]);p=HS.coefficient_rhs(ebc,0.,S_lrs,0.,4)
    eb={'sigma':S_lrs.tolist(),'input':'E_2,2=1','output':'dot B_3,-2','rate':p['B',3,-2],'exact_expression':'4 sqrt(5/7) s, sigma=diag(-s,-s,2s)','s':.2,'exact_value':4*np.sqrt(5/7)*.2}
    assert abs(eb['rate']-eb['exact_value'])<ATOL
    axis=HS.coefficient_rhs({('E',2,0):1.},0.,S_lrs,0.,4)
    eb['axisymmetric_E20_B_max']=max(abs(v) for k,v in axis.items() if k[0]=='B')
    assert eb['axisymmetric_E20_B_max']<ATOL
    gp=Grid(12,24);jp=synthesize(gp,{('I',0,0):3*np.sqrt(4*np.pi),('E',2,2):.2})
    scr=np.stack([gp.bt,gp.bp],axis=2)
    eb['positive_mixed_input_screen_min_eigenvalue']=float(np.linalg.eigvalsh(np.einsum('nia,nij,njb->nab',scr,hermitian(jp),scr)).min())
    eb['positive_mixed_B_rate']=.2*eb['rate']
    assert eb['positive_mixed_input_screen_min_eigenvalue']>0
    # Direct derivative mutation controls: do not change production or accepted gates.
    g=Grid(12,24);H=.3;S=FIELDS[2][2]
    good=DO.spin_coordinate_rhs(g,c,H,S);wrong=DO.spin_coordinate_rhs(g,c,H,S,connection=False)
    mutations['drop_spin_connection_pointwise_error']=float(np.max(np.abs(good['P']-wrong['P'])))
    mutations['delete_EB_block_rate_error']=abs(eb['rate'])
    top={('E',4,2):1.,('I',4,0):.2};out=HS.coefficient_rhs(top,H,S,0.,6)
    tail=float(np.sqrt(sum(v*v for (f,l,m),v in out.items() if l>4)))
    mutations['discard_generated_l5_l6_rhs_norm']=tail
    bright={('I',0,0):np.sqrt(4*np.pi)};b=HS.coefficient_rhs(bright,H,S,0.,2)
    mutations['wrong_harmonic_to_PSTF_scale_example']=float(abs(1-np.sqrt(LS.Dnorm(2)))*np.linalg.norm([b['I',2,m] for m in range(-2,3)]))
    assert min(mutations.values())>1e-3
    # Tiny-step reconstruction check uses source derivatives only, not a new time history.
    scaling=[]
    for amp in [.1,.6,1.3]:
        S=amp*FIELDS[2][2];g=Grid(12,24)
        a=HS.coefficient_rhs(c,.3,S,1.3,6);b=DO.projected_rhs(g,c,.3,S,1.3,6)
        er=max(abs(a[k]-b[k]) for k in b);assert er<ATOL
        scaling.append({'shear_multiplier':amp,'max_error':float(er)})
    result={'schema':'bass.dv1a.results.v1','status':'PASS_SCOPED_INSTANTANEOUS_FULL_POLARIZED_GENERATOR',
      'parent_commit':'5dd5daef9f95e3b1e6dff536e701415f4d0e9894','tolerance':ATOL,
      'scope':'BianchiI prescribed nonrotating normal frame; full-polarized bolometric; untilted cold Thomson; input ell<=4, retain RHS through ell6; no trajectory triangle',
      'runtime':'PYTHON_PASS','source_identity':ids,'basis_rows':rows,'physical_rows':physical,'legacy_scalar_rows':legacy,'selection':sel,'EB_example':eb,'mutations':mutations,'amplitude_rows':scaling,
      'counts':{'basis_rows':len(rows),'physical_rows':len(physical),'legacy_comparisons':len(legacy),'amplitude_rows':len(scaling),'new_IVPs':0,'old_campaign_reruns':0},
      'maxima':{'basis_rhs':max(r['max_rhs_coefficient_error'] for r in rows),'mixed_rhs':max(r['total_rhs_coefficient_error'] for r in physical),'scalar_J':max(r['J_coefficient_l0_to_l4_error'] for r in legacy),'scalar_H':max(r['H_dense_l0_to_l2_error'] for r in legacy),'energy_balance':max(r['energy_balance_absolute'] for r in physical),'screen_coordinate':max(r['spin_coordinate_vs_P8_pointwise_error'] for r in physical)},
      'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'sympy':sympy.__version__},
      'wall_seconds':time.perf_counter()-started,'native_subagent':'NOT_RUN_TOOL_NOT_EXPOSED','independent_model_review':'NOT_RUN','production_ready':False}
    (ROOT/'evidence/DV1A_RESULTS.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in ('basis_rows','physical_rows','legacy_scalar_rows')},indent=2))
if __name__=='__main__':main()
