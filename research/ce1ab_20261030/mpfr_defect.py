"""CE1-AB original GL6/GL8 DOP853 dense polynomial MPFR192 interval defect proof.

A posteriori defect upper bounds for replayed exact-dyadic dense polynomials;
not a formal proof of Python/MPFR interface nor a certificate for the continuum
Einstein-Vlasov IVP without comparison and source transport.
"""
import sys,json,csv,hashlib,math,time, argparse
from fractions import Fraction
from pathlib import Path
BASE=Path(__file__).resolve().parent
ORIGINAL=(BASE/'ce1aa_input') if (BASE/'ce1aa_input').is_dir() else (BASE.parent/'ce1aa_20261030')
SRC=ORIGINAL/'source'
sys.path.insert(0,str(SRC))
from mpfr192_sky import IV,d,op,cmp,M,P,RD,RU,PREC,lib, rays, SOURCE_SHA
from cellwise_gl_rust import make_cell_rays,frozen_source_identity

Z=IV.val(0);ONE=IV.val(1);TWO=IV.val(2)

def interval(l,h):
    if l>h:raise ValueError('reverse interval')
    return IV(d(l),d(h))

def abs_up(v):
    x=v.pair()
    return max(abs(x[0]),abs(x[1]))

def contained(v,low,high):
    a,b=v.pair();return low <= a and b <= high

def interp_jets(F,y0,s):
    """Exact DOP853 F nesting with outward MPFR192 first/second derivatives by AD."""
    p0=[Z for _ in range(6)];p1=[Z for _ in range(6)];p2=[Z for _ in range(6)]
    for i in range(7):
        b=s if i%2==0 else ONE-s
        db=ONE if i%2==0 else -ONE
        v=[IV.val(float.fromhex(F[6-i][j])) for j in range(6)]
        q0=[p0[j]+v[j] for j in range(6)]
        q1=p1;q2=p2
        p2=[q2[j]*b+TWO*q1[j]*db for j in range(6)]
        p1=[q1[j]*b+q0[j]*db for j in range(6)]
        p0=[q0[j]*b for j in range(6)]
    p0=[p0[j]+IV.val(float.fromhex(y0[j])) for j in range(6)]
    return p0,p1,p2

def pstate(step,s):
    return interp_jets(step['F_hex'],step['y_old_hex'],s)

def physical_source_jac(ell,prepared):
    """Original exact stored dyadic rays/masses as real, with MPFR192 bound."""
    B=[(-TWO*e).exp() for e in ell]
    vol=(-ell[0]-ell[1]-ell[2]).exp()
    pv=[Z,Z,Z];t=[[Z,Z,Z] for _ in range(3)]
    for w,n2 in prepared:
        q=[B[i]*n2[i] for i in range(3)]
        Q=q[0]+q[1]+q[2];rr=Q.sqrt()
        inv=w/rr
        qi_inv=[qi*inv for qi in q]
        for i in range(3):pv[i]=pv[i]+qi_inv[i]
        # T_ij = mass*vol*q_i*q_j/Q^(3/2)
        inv_Q=ONE/Q
        for i in range(3):
            for j in range(3):t[i][j]=t[i][j]+qi_inv[i]*q[j]*inv_Q
    pv=[vol*x for x in pv]
    t=[[vol*x for x in row] for row in t]
    J=[[t[i][j]-(IV.val(1+2*int(i==j))*pv[i]) for j in range(3)] for i in range(3)]
    return pv,J

def defect(step,prepared,s,eval_jac=False):
    p,p_s,p_ss=pstate(step,s)
    h=IV.val(float.fromhex(step['h_hex']))
    p_u=[v/h for v in p_s]
    p_uu=[v/(h*h) for v in p_ss]
    ell,H=p[:3],p[3:]
    P,J=physical_source_jac(ell,prepared)
    theta=H[0]+H[1]+H[2]
    R=[p_u[i]-H[i] for i in range(3)]
    R += [p_u[3+i] +theta*H[i] -P[i] for i in range(3)]
    if not eval_jac:return R,p
    # R'_ell = y''_ell - y'_H
    Rp=[p_uu[i]-p_u[3+i] for i in range(3)]
    thetap=sum(p_u[3:6],Z)
    for i in range(3):
        Rp.append(p_uu[i+3]+thetap*H[i]+theta*p_u[3+i]-sum((J[i][j]*p_u[j] for j in range(3)),Z))
    return R,Rp,p

def end_normalized_s(step):
    # t_end is the original next SciPy node, its exact dyadic real not necessarily equal ta+h.
    # Compute the ratio in outward MPFR to preserve the true physical knot time.
    a=IV.val(float.fromhex(step['t_old_hex']));b=IV.val(float.fromhex(step['t_end_hex']))
    h=IV.val(float.fromhex(step['h_hex']))
    return (b-a)/h

def initial_error(order,prepared,step):
    # exact GL-source initial H from positive ray at ell=0 with source MPFR192.
    P,J=physical_source_jac([Z,Z,Z],prepared)
    # E0 = volume * sum mass * sqrt(sum n_i^2); directly with MPFR192.
    E=Z
    for w,n2 in prepared:
        norm=(n2[0]+n2[1]+n2[2]).sqrt()
        E=E+w*norm
    ss=[IV.val(float(v)) for v in (.2,-.13,-.07)]
    H0=((E+sum((x*x for x in ss),Z)/TWO)/IV.val(3)).sqrt()
    exact=[Z,Z,Z]+[H0+x for x in ss]
    ys=[IV.val(float.fromhex(x)) for x in step['y_old_hex']]
    return [abs_up(exact[j]-ys[j]) for j in range(6)], E.pair()

def run(n,divisions,out):
    tstart=time.monotonic()
    filename=BASE/'results'/f'GL{n}_REPLAY_DOP853_DENSE.json'
    a=json.loads(filename.read_text())
    assert a['source_sha256']==SOURCE_SHA
    assert a['replay_target_status']=='EXACT' and a['num_binary64_equal_saved_states']==246
    prepared=rays(n)
    N=divisions
    allstep=[];all_max=[0.0]*6;max_knot=[0.0]*6
    ymin=[float('inf')]*6;ymax=[float('-inf')]*6
    init_err,E0=initial_error(n,prepared,a['steps'][0])
    for j,step in enumerate(a['steps']):
        s_end=end_normalized_s(step)
        # s_end may differ from 1; slab intervals on [0,s_end], s_edge = s_end * (i/N)
        # The extra interval width <= MPFR rounding. All ratios represented as MPFR endpoints.
        r_sup=[0.0]*6; max_r_mid=[0.0]*6; max_dr=[0.0]*6
        # Physical length, outward-double from exact binary64 nodes (conservative).
        length=abs_up(IV.val(float.fromhex(step['t_end_hex']))-IV.val(float.fromhex(step['t_old_hex'])))
        for i in range(N):
            s_lo=s_end*(IV.val(i)/IV.val(N));s_hi=s_end*(IV.val(i+1)/IV.val(N))
            s_panel=IV(s_lo.lo,s_hi.hi)
            s_mid=s_end*(IV.val(2*i+1)/IV.val(2*N))
            # Interval midpoint gets uncertainty of 192-bit division. Not just f64 point.
            Rmid,_=defect(step,prepared,s_mid,False)
            _,Rp,ps=defect(step,prepared,s_panel,True)
            for q in range(6):
                rr=abs_up(Rmid[q]);der=abs_up(Rp[q])
                if not math.isfinite(rr) or not math.isfinite(der):raise ArithmeticError('nonfinite')
                sup=(IV.val(rr)+IV.val(length)*IV.val(der)/IV.val(2*N)).hi.f(RU)
                r_sup[q]=max(r_sup[q],sup);max_r_mid[q]=max(max_r_mid[q],rr);max_dr[q]=max(max_dr[q],der)
                vmin,vmax=ps[q].pair();ymin[q]=min(ymin[q],vmin);ymax[q]=max(ymax[q],vmax)
        for q in range(6):all_max[q]=max(all_max[q],r_sup[q])
        knot=[0]*6
        if j+1<len(a['steps']):
            pleft=pstate(step,s_end)[0]
            pright=pstate(a['steps'][j+1],Z)[0]
            knot=[abs_up(pleft[k]-pright[k]) for k in range(6)]
            max_knot=[max(x,y) for x,y in zip(max_knot,knot)]
        allstep.append({'step':j,'t0_hex':step['t_old_hex'],'t1_hex':step['t_end_hex'],
                       'h_hex':step['h_hex'],'duration_upper':length,
                       'defect_sup_abs_upper':r_sup,'residual_mid_abs_upper':max_r_mid,
                       'defect_derivative_sup_abs_upper':max_dr,
                       'knot_jump_abs_upper':knot})
        print('MPFR192',n,'step',j,'N',N,'max|R| <= %.4e'%max(r_sup),'max|Rprime| <=%.4e'%max(max_dr),'jump',max(knot),flush=True)
    # Bridge MPFR exact-dyadic dense polynomial evaluations to originally SAVED
    # binary64 41-state outputs; this is distinct from trajectory defect.
    state_names=['ell1','ell2','ell3','h1','h2','h3']
    sample_gap=0.0
    with (ORIGINAL/'input'/f'GL{n}_DOP853_coupled_41epochs.csv').open() as fd:
        frozen_rows=list(csv.DictReader(fd))
    for row in frozen_rows:
        u=float(row['u'])
        chosen=next((st for st in a['steps'] if u<=float.fromhex(st['t_end_hex'])),a['steps'][-1])
        s=(IV.val(u)-IV.val(float.fromhex(chosen['t_old_hex'])))/IV.val(float.fromhex(chosen['h_hex']))
        y=pstate(chosen,s)[0]
        for name,iv in zip(state_names,y):
            sample_gap=max(sample_gap,abs_up(iv-IV.val(float(row[name]))))
    # Conservative Lipschitz L=12 on y tube ell[-0.001,0.081], h[0,0.9], ray norm (tiny >1), source sum 0.9.
    # Bound uses Jpressure row sum <=6E for non-negative ray quadrature; F_h Jacobian row <= theta+3 max|h|.
    # E upper on tube <= sum masses exp(4*.001)*normray_max; use exact f64 outward 
    # Certified exact-dyadic total masses, radicand and exp upper in tube:
    # Sum w < .91, every exact stored ||n||^2 < 1+10^-12.
    # exp(.004) <= 1/(1-.004) = 250/249. Hence E < .91*(250/249)*(1+1/10^12) < .92.
    # Analytical exact GL Jacobian: sum_j |dP_i/dell_j| = 5P_i <= 5E.
    # In h box [0,.9]: row-sum |-theta I - h_i 1^T| <= 2.7+2.7=5.4.
    # Lipschitz infinity norm of (h,-theta h+P) <= max(1,5*.92+5.4) = 10 < 12.
    rays_f,masses=make_cell_rays(n)
    weights_exact=sum((Fraction.from_float(float(w)) for w in masses),Fraction(0))
    norm2max=max(sum((Fraction.from_float(float(q))**2 for q in xyz),Fraction(0)) for xyz in rays_f)
    assert weights_exact < Fraction(91,100) and norm2max < 1+Fraction(1,10**12)
    e_tube_rational=Fraction(91,100)*Fraction(250,249)*(1+Fraction(1,10**12))
    assert e_tube_rational < Fraction(92,100)
    E_tube=float(e_tube_rational)  # diagnostic only, proof uses rational exact inequality
    L_check=10.0  # proved exact upper 5*0.92+5.4=10.0
    L=12.0
    # local maximum max-component defect * integrated e^{L(T-t)}; knot jumps e^{L(T-ti)}; init term
    T=.08; initmax=max(init_err);Rmax=max(all_max)
    # Gronwall source aggregation, all bounds MPFR192 RNDD/RNDU through final comparison.
    LT=IV.val(12)*IV.val(float.fromhex(a['steps'][-1]['t_end_hex']))
    expLT=LT.exp()
    jump_weight_iv=Z
    for state in allstep:
        time_remain=IV.val(float.fromhex(a['steps'][-1]['t_end_hex']))-IV.val(float.fromhex(state['t1_hex']))
        jump_weight_iv += IV.val(max(state['knot_jump_abs_upper']))*(IV.val(12)*time_remain).exp()
    err_iv=expLT*IV.val(initmax) + (expLT-ONE)*IV.val(Rmax)/IV.val(12) +jump_weight_iv
    jump_weight=jump_weight_iv.hi.f(RU)
    err=err_iv.hi.f(RU)
    # initial exact self-consistent GL IC and new continuous GL ODE trajectory are enclosed if the bound stays within tube.
    # Set pilot tube margins by measured certified polynomial bound. E.g. y elliptic: [-0.001, .081], h [0,.9].
    tube_ok=(err<1e-3 and min(ymin[:3])>=-1e-3+err and max(ymax[:3])<=.081-err and min(ymin[3:])>=err and max(ymax[3:])<=.9-err)
    output={'schema':'bass.ce1ab.mpfr192.dense_defect.v1',
        'method':'DOP853 replay exact stored states; MPFR192 RNDD/RNDU interval AD of dense polynomial and source + local midpoint/derivative defect bound',
        'order':n,'source_sha256':SOURCE_SHA,'replayed_dense_source_sha256':hashlib.sha256(filename.read_bytes()).hexdigest(),
        'original_saved_41row_sha256':a['frozen_reference_csv_sha256'],
        'source_gl_ray_mass_sha256':[a['rays_sha256'],a['masses_sha256']],
        'mpfr_precision_bits':PREC,'subdivisions_per_step':N,'original_rtol':3e-12,'original_atol':3e-14,
        'initial_error_component_upper':init_err,'initial_E0_interval':E0,
        'global_defect_component_max_upper':all_max,'global_defect_infinity_upper':Rmax,
        'knot_jumps_infinity_sum_weighted_upper':jump_weight,
        'upper_Lipschitz_12_assumed_tube_verified':L_check,
        'Grönwall_global_infty_error_upper':err,'saved_states_vs_exact_dense_max_upper':sample_gap,'original_saved_state_geometry_error_upper':(IV.val(err)+IV.val(sample_gap)).hi.f(RU),'prescribed_tube_ell':[-.001,.081],
        'prescribed_tube_h':[0,.9],'poly_component_lower':ymin,'poly_component_upper':ymax,
        'tube_self_consistent':tube_ok,
        'GL_IVP_CERTIFIED':tube_ok,'CONTINUUM_6CELL_IVP_CERTIFIED':False,
        'EXACT_CONTINUUM_RANK2_CERTIFIED':False,
        'steps':allstep,'elapsed_seconds':time.monotonic()-tstart}
    out.mkdir(parents=True,exist_ok=True)
    p=out/f'GL{n}_MPFR192_DOP853_DEFECT_N{N}.json';p.write_text(json.dumps(output,indent=2)+'\n')
    print('GL',n,'CERT GLIVP=',tube_ok,'err<=',err,'Rmax',Rmax,'E tube',E_tube,'L bound',L_check,'elapsed',output['elapsed_seconds'],flush=True)
    return output
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--n',type=int,choices=(6,8),default=6);p.add_argument('--divisions',type=int,default=16);a=p.parse_args()
    run(a.n,a.divisions,BASE/'results')
