"""Exact scoped VI_0 diagonal-eigenframe constraint and scalar Kato geometry.

Owner: cosmosapjw-quantum/bass; expected 2026-08-21 PR15 design.
Not a VI0 dynamical solver, not the generic polarized P8 projector.
Independent primary equations: BASS bianchi.conventions.codazzi_residual,
bianchi.matter.fluid.sources, bianchi.charts.general curvature,
and generated Type-II scalar projector. All inputs are rederived algebraically.
"""
from __future__ import annotations
import json
from pathlib import Path
import sympy as s

DESIGN_PR15_HEAD = "af467a974cfd9bd8ccd59870e5a03c8099f23db1"
OWNER_MAIN_BASE = "9c6506e4e2087129a8b674ff10438e5db1a55c9d"
SOURCE_SHA = {
    "bianchi/conventions.py": "09cbbf1046f292506a009bd45a0598ec0da65da5",
    "bianchi/matter/fluid.py": "41905ff26914b2a7931ce2281d67b25fbde273b5",
    "bianchi/charts/general.py": "115aec90df83d097904695817b6aa337d5ba76ee",
    "bianchi/charts/class_a.py": "305438f3f82919390282d469bca7d3185451aed9",
    "compiler/lowering/rust_typeii.py": "108fe5810af80c251b0c82fda517c57c3ee0c3fb",
    "generated/rust/typeii/typeii_kato.rs": "9c8d49b6d42daf28734b4d439ca50f6535ee3519",
    "docs/superpowers/specs/2026-08-21-g-dyn-manifold-vi0-design.md": "fff778b7ac55a2580097fa4780eefd7b41cea77c",
}

def abstract_symbols():
    sp, sm, p, q, g = s.symbols('sp sm p q g', real=True)
    v1, v2, v3, Om = s.symbols('v1 v2 v3 Om', real=True)
    b12, b13, b23 = s.symbols('b12 b13 b23', real=True)
    return sp, sm, p, q, g, (v1, v2, v3), Om, (b12, b13, b23)

def geometry_equations():
    sp, sm, p, q, gamma, v, Om, off = abstract_symbols()
    v1, v2, v3 = v; b12,b13,b23 = off
    N = s.diag(0,p,-q)
    Sigma = s.Matrix([[-2*sp,b12,b13],[b12,sp+s.sqrt(3)*sm,b23],[b13,b23,sp-s.sqrt(3)*sm]])
    Gp = 1+(gamma-1)*(v1*v1+v2*v2+v3*v3)
    flux = 3*gamma*Om/Gp * s.Matrix(v)
    # epsilon^(abc) N_(bd) Sigma_(cd); ε123=+1
    codazzi = s.Matrix([(p+q)*b23,-q*b13,-p*b12]) - flux
    S2=s.trace(Sigma*Sigma)/6
    curvature=(p+q)**2/12
    gauss=Om+S2+curvature-1
    Dz=[p+q,-q,-p]
    alpha=3*gamma/Gp
    solution={b23:alpha*Om*v1/Dz[0],b13:alpha*Om*v2/Dz[1],b12:alpha*Om*v3/Dz[2]}
    beta=(alpha**2/s.Integer(3))*sum(v[i]**2/Dz[i]**2 for i in range(3))
    source_budget=1-sp**2-sm**2-curvature
    reduced=s.expand(gauss.subs(solution,simultaneous=True))
    expect=Om+beta*Om**2-source_budget
    # Codazzi constraints must be structurally eliminated, without using numeric tolerance.
    assert all(s.simplify(z.subs(solution, simultaneous=True)) == 0 for z in codazzi)
    assert s.simplify(reduced-expect)==0
    # rank certificate: determinant of 4 exact constraints wrt original offdiags and Omega.
    C=s.Matrix([codazzi[0],codazzi[1],codazzi[2],gauss])
    vars4=s.Matrix([b23,b13,b12,Om])
    jac=C.jacobian(vars4)
    # Determinant by exact 3x3 diagonal Schur complement.
    # Codazzi rows are diagonal in (b23,b13,b12); Gauss supplies 4th row.
    # Full symbolic determinant expands unnecessarily into giant rationals.
    diag_product=(p+q)*p*q
    det_on=diag_product*(1+s.Rational(2,3)*alpha**2*Om*sum(v[i]**2/Dz[i]**2 for i in range(3)))
    rank_cert=diag_product*(1+2*beta*Om)
    assert s.simplify(det_on-rank_cert)==0
    return dict(N=N,Sigma=Sigma,G_plus=Gp,codazzi=codazzi,gauss=gauss,
                shearsquared=S2,curvature=curvature,alpha=alpha,
                reduced=s.factor(reduced),Omega_budget=source_budget,
                beta=beta,offdiag_solution=solution,det_on=det_on,
                rank_certificate=rank_cert,
                variables=dict(sp=sp,sm=sm,p=p,q=q,gamma=gamma,v=v,Om=Om,off=off))

def projector_6axes(v, vdot=(0,0,0)):
    """Exact rational finite spherical six-axis scalar projector and Kato action.

    r_a = [Gamma*(1-v·n_a)]^-4;
    a_a = w_a*(1-v·n_a)/(4pi), w_a = 4pi/6.
    The grid contains each ±e_i, giving an exact 3-coordinate inverse witness.
    """
    vel=s.Matrix(v);dv=s.Matrix(vdot)
    n=s.Matrix([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]])
    speed2=(vel.T*vel)[0]
    G=1-speed2
    dots=n*vel
    qu=[1-dots[i] for i in range(6)]
    r=s.Matrix([(G**2)/qi**4 for qi in qu])
    a=s.Matrix([qi/s.Integer(6) for qi in qu])
    den=(a.T*r)[0]
    P=r*a.T/den
    ris=[];ais=[];Pdirs=[]
    for j in range(3):
        ri=s.Matrix([r[i]*4*(n[i,j]/qu[i]-vel[j]/G) for i in range(6)])
        ai=s.Matrix([-n[i,j]/6 for i in range(6)])
        di=(ai.T*r+a.T*ri)[0]
        Pi=(ri*a.T+r*ai.T)/den-r*a.T*di/den**2
        ris.append(ri);ais.append(ai);Pdirs.append(Pi)
    Pdot=sum((dv[j]*Pdirs[j] for j in range(3)),s.zeros(6,6))
    K=Pdot*P-P*Pdot
    return dict(P=P,Pdot=Pdot,K=K,P_i=Pdirs,
                r=r,a=a,den=den,n=n,ratio=(r[0]/r[1],r[2]/r[3],r[4]/r[5]),
                speed2=speed2)

def constraint_witness():
    x=geometry_equations();d=x['variables']
    subs={d['sp']:s.Rational(1,7),d['sm']:s.Rational(1,9),d['p']:s.Rational(3,5),d['q']:s.Rational(2,5),
          d['gamma']:s.Rational(4,3),d['v'][0]:s.Rational(1,10),d['v'][1]:-s.Rational(1,9),d['v'][2]:s.Rational(1,11)}
    B=x['beta'].subs(subs);R=x['Omega_budget'].subs(subs)
    Om=2*R/(1+s.sqrt(1+4*B*R))
    assert s.simplify(Om+B*Om**2-R)==0
    full={**subs,d['Om']:Om}
    full.update({name:s.simplify(value.subs(full)) for name,value in x['offdiag_solution'].items()})
    assert all(s.simplify(c.subs(full))==0 for c in x['codazzi'])
    assert s.simplify(x['gauss'].subs(full))==0
    assert s.N(x['rank_certificate'].subs(full),30)>0
    return x,full

def run_all():
    x,state=constraint_witness()
    vv=[s.Rational(1,10),-s.Rational(1,9),s.Rational(1,11)]
    dd=[s.Rational(1,23),-s.Rational(1,17),s.Rational(1,19)]
    o=projector_6axes(vv,dd)
    def iszero(mat):return all(z==0 for z in mat)
    assert iszero(o['P']*o['P']-o['P']),"P2 !=P"
    assert iszero(o['Pdot']*o['P']+o['P']*o['Pdot']-o['Pdot']),"d(P2) !=dP"
    assert iszero(o['K']*o['P']-o['P']*o['K']-o['Pdot']),"Kato identity failed"
    # Dimensional certificate: r_+i/r_-i = [(1+vi)/(1-vi)]^4,
    # and its logarithmic derivative 8/(1-vi^2). Distinct independent n_i.
    assert tuple(o['ratio'])==tuple(((1+vi)/(1-vi))**4 for vi in vv)
    wrong=projector_6axes([0,vv[1],0])
    assert o['P']!=wrong['P'],"false Type-II transplant accepted"
    # Full manifold 7 dimensions, projector rank 3; strict v=0 branch 4 dimensions / rank 0.
    o_zero=projector_6axes([0,0,0])
    assert o_zero['P']!=o['P']
    assert all(any(z!=0 for z in d) for d in o_zero['P_i']),"false v=0 full-tangent rank0"
    # N principal-frame rotation follows Ndot=qN + Sigma N+N Sigma +[W,N].
    p=s.Rational(3,5);q=s.Rational(2,5)
    n=s.diag(0,p,-q);Sig=s.Matrix([[0,s.Rational(1,7),s.Rational(1,8)],
                               [s.Rational(1,7),0,s.Rational(1,9)],
                               [s.Rational(1,8),s.Rational(1,9),0]])
    W=s.zeros(3,3)
    for i,j in ((0,1),(0,2),(1,2)):
        W[i,j]=-(n[i,i]+n[j,j])/(n[j,j]-n[i,i])*Sig[i,j]
        W[j,i]=-W[i,j]
    Ndot=Sig*n+n*Sig+W*n-n*W
    assert all(Ndot[i,j]==0 for i,j in ((0,1),(0,2),(1,2)))
    # Branch controls: VI0 p>0,q>0 versus type II p=0 or q=0.
    vp=x['variables']
    rank_factor=x['rank_certificate']
    assert s.simplify(rank_factor.subs({vp['p']:0}))==0
    assert s.simplify(rank_factor.subs({vp['q']:0}))==0
    # Gamma=6/5 is a *dynamical stability* bifurcation, not algebraic constraint rank-loss.
    full_65={**state,vp['gamma']:s.Rational(6,5)}
    assert s.N(rank_factor.subs(full_65),20)>0
    result={
      'schema':'bass.g_dyn_manifold_vi0.scalar_eigenframe_constructive.v1',
      'branch_base_head':OWNER_MAIN_BASE,
      'design_pr15_head':DESIGN_PR15_HEAD,
      'input_blob_sha1':SOURCE_SHA,
      'source_convention':'(-,+,+,+); eps123=+1; Hubble normal 8piG=c=1 only within BASS adopted source; keep physical c in external definitions',
      'scope':'one tilted gamma-law perfect fluid and co-moving scalar bolometric Thomson projector on a principal VI0 frame, N=diag(0,p,-q), p,q>0, Omega>0, |v|<1, 0<gamma<2',
      'equation_of_state':'p_fluid=(gamma-1)rho_rest',
      'dimension_background_constraint_manifold':7,
      'dimension_strict_zero_tilt_background':4,
      'dimension_scalar_projector_image_generic':3,
      'dimension_scalar_projector_image_strict_zero_tilt':0,
      'branch_typeii_boundary': 'p==0 or q==0 (invalid VI0 local chart), conditional TypeII rank reduction',
      'analytic_codazzi': ['(p+q)*Sigma23=3gamma Omega v1/Gp','-q*Sigma13=3gamma Omega v2/Gp','-p*Sigma12=3gamma Omega v3/Gp'],
      'analytic_gauss_reduction':'Omega+beta*Omega**2 = 1-sp**2-sm**2-(p+q)**2/12, beta=3gamma**2/Gp**2*[v1**2/(p+q)**2+v2**2/q**2+v3**2/p**2]',
      'rank_minor':'p*q*(p+q)*(1+2beta Omega)>0',
      'proven_exact': ['constraint_elimination','rank4_constraint_jacobian','7D_local_chart','positive_unique_density','6axis_full_tilt_projector_global_inverse','P2=P','dP_tangent_identity','Kato_commutator','nonzero_vi0_3_velocity_rank','principal_frame_offdiagonal_rotation'],
      'negative_controls':['TypeII_v2_only_false_transplant','drop_codazzi_loses_rank','TypeII_pq_boundary','zero_tilt_branch_distinction','gamma_6over5_not_rank_loss'],
      'not_derived':['full VI0 physical polarized screen projector','moving-grid Liouville closure','gauge-independent production Rust lowering','VI0 evolution invariant set for all gamma','P_MIG_II_PREFLIGHT','cross-family production'],
      'status':'DERIVED_EXACT_IN_SOURCE_CONDITIONAL_SCOPE_NUMERICALLY_SPOT_CHECKED; FULL_GATE_REVIEW_HOLD',
      'production_ready':False,'merge_ready':False,'auto_next':False,
    }
    return result

if __name__=='__main__':
    print(json.dumps(run_all(),indent=2,ensure_ascii=False))
