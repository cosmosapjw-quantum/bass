"""CE1-AB: certified GL6/8 sampled-state -> true continuum geometry Gram transport.

Uses verified original six-cell source identities and predecessor exact K4 source-only bounds.
The new ingredient is directed MPFR192 all-41-state local angular Jacobian bounds.
"""
import csv,hashlib,json,math,sys, argparse
from pathlib import Path
from fractions import Fraction
from decimal import Decimal, localcontext, ROUND_FLOOR
BASE=Path(__file__).resolve().parent
ORIGINAL=(BASE/'ce1aa_input') if (BASE/'ce1aa_input').is_dir() else (BASE.parent/'ce1aa_20261030')
sys.path.insert(0,str(ORIGINAL/'source'))
from mpfr192_sky import IV,pi_iv,constants,rays,SOURCE_SHA,RAY_SHA,INPUT_SHA,PREC,RU

Z=IV.val(0); O=IV.val(1); TWO=IV.val(2); FOUR=IV.val(4)

def absupper(iv):
    p=iv.pair()
    return max(abs(p[0]),abs(p[1]))

def box(center,r):
    lo=IV.val(center)-IV.val(r)
    hi=IV.val(center)+IV.val(r)
    return IV(lo.lo,hi.hi)

def jac_alpha(ell,prep,cs):
    """Exact analytic derivatives of alpha=4πa/E, incl energy normalization.

    Original alpha40,42,44 defined by normalized massless bolometric energy sky.
    All data interpreted as exact stored dyadics, interval exp/sqrt/π RNDD/RNDU.
    """
    P,cc40,cc42,cc44=cs
    factors=[FOUR*P*cc40,FOUR*P*cc42,FOUR*P*cc44]
    b=[(-TWO*z).exp() for z in ell]
    M0=Z;M=[Z,Z,Z];M0p=[Z,Z,Z];Mp=[[Z,Z,Z] for _ in range(3)]
    for w,n2 in prep:
        q=[b[i]*n2[i] for i in range(3)]
        Q=q[0]+q[1]+q[2]
        rr=Q.sqrt()
        wr=w*rr
        x=[qi/Q for qi in q]
        a,bb,z=x
        T=[35*z*z-30*z+3,(a-bb)*(7*z-1),a*a-6*a*bb+bb*bb]
        M0=M0+wr
        M=[M[m]+wr*T[m] for m in range(3)]
        for j in range(3):
            dx=[TWO*x[i]*(x[j]-(O if i==j else Z)) for i in range(3)]
            da,db,dz=dx
            dT=[(70*z-30)*dz,(da-db)*(7*z-1)+7*(a-bb)*dz,(TWO*a-6*bb)*da+(TWO*bb-6*a)*db]
            M0p[j]=M0p[j]-wr*x[j]
            for m in range(3):Mp[m][j]=Mp[m][j]+wr*(dT[m]-x[j]*T[m])
    alpha=[factors[m]*M[m]/M0 for m in range(3)]
    deriv=[[factors[m]*(Mp[m][j]/M0 - M[m]*M0p[j]/(M0*M0)) for j in range(3)] for m in range(3)]
    return alpha,deriv

def run(n,N,root):
    st=json.loads((ORIGINAL/'data'/f'GL{n}_mpfr192_source_41.json').read_text())
    d=json.loads((root/f'GL{n}_MPFR192_DOP853_DEFECT_N{N}.json').read_text())
    src=json.loads((ORIGINAL/'data'/'SCIENCE_RESULTS.json').read_text())['channels'][str(n)]
    assert st['source_sha256']==SOURCE_SHA and d['source_sha256']==SOURCE_SHA
    assert src['continuous_original_six_cell_source_fixed_geometry_lambda2_lower_decimal']
    assert st['history_sha256']==INPUT_SHA[n]==d['original_saved_41row_sha256']
    source_geom_bound = {6:'5.474586575721355e-13',8:'1.1315891404909281e-14'}[n]
    # Upward f64 for prior exact-rational theorem's bound: decimal rational exact then nextafter if required.
    # Stored binary64 final endpoint exceeds exact rational 2/25 by
    # 3/1801439850948198400 < 2e-18. Lipschitz 7, source eps<3.1e-12,
    # previous |delta geometry|<6e-13 imply an extra < 2e-29; allow 1e-20.
    # This simultaneously absorbs decimal display rounding of the old bound.
    f=Fraction(source_geom_bound)+Fraction(1,10**20)
    geom=(IV.val(d['original_saved_state_geometry_error_upper'])+IV.val(float(f))).hi.f(RU)
    if Fraction.from_float(geom)<f+Fraction.from_float(d['original_saved_state_geometry_error_upper']):geom=math.nextafter(geom,math.inf)
    prep=rays(n); const=constants();rt2=TWO.sqrt()
    x0sq=Z;dsq=Z
    max_jac=[0.]*3; max_local=[0.]*3
    outrows=[]
    for row in st['states']:
        ellbox=[box(float(e),geom) for e in row['ell']]
        alpha,deriv=jac_alpha(ellbox,prep,const)
        rscale=[O/3,rt2/3,rt2/3]
        lin=[];local_jac=[]
        for m in range(3):
            jbound=sum((IV.val(absupper(deriv[m][j])) for j in range(3)),Z).hi.f(RU)
            max_jac[m]=max(max_jac[m],jbound);local_jac.append(jbound)
            delta=(IV.val(jbound)*IV.val(geom)*rscale[m]).hi.f(RU)
            lin.append(delta)
            max_local[m]=max(max_local[m],delta)
            x0=IV(float_to_mpfr(row['alpha'][m][0]),float_to_mpfr(row['alpha'][m][1])) *rscale[m]
            x0sup=absupper(x0)
            x0sq=x0sq+IV.val(x0sup)*IV.val(x0sup)
            dsq=dsq+IV.val(delta)*IV.val(delta)
        outrows.append({'u':row['u'],'geom_error_upper':geom,'derivative_l1_upper':local_jac, 'delta_X_per_mode_upper':lin})
    A=x0sq.sqrt().hi.f(RU);B=dsq.sqrt().hi.f(RU)
    delta_S=(TWO*IV.val(A)*IV.val(B)+IV.val(B)*IV.val(B)).hi.f(RU)
    source_lambda=Fraction(src['continuous_original_six_cell_source_fixed_geometry_lambda2_lower_rational'])
    remain=source_lambda-Fraction.from_float(delta_S)
    with localcontext() as ctx:
        ctx.prec=65;ctx.rounding=ROUND_FLOOR
        margin=format(Decimal(remain.numerator)/Decimal(remain.denominator),'.30g')
    data={'schema':'bass.ce1ab.einstein_vlasov_41epoch_rank2_transport.v1',
          'GL':n,'original_source_sha256':SOURCE_SHA,'original_history_sha256':INPUT_SHA[n],
          'MPFR_precision_bits':PREC,'MPFR_dense_divisions_per_step':N,
          'exact_stored_source_Gram_lambda2_lower':src['continuous_original_six_cell_source_fixed_geometry_lambda2_lower_decimal'],
          'original_exact_continuum_vs_GL_ODE_geometry_error_decimal':source_geom_bound,
          'source_ODE_endpoint_display_and_dyadic_extension_budget':'1e-20',
          'new_MPFR_dop853_GL_trajectory_error':d['Grönwall_global_infty_error_upper'],
          'replayed_dense_vs_exact_original_saved_41states':d['saved_states_vs_exact_dense_max_upper'],
          'total_original_continuum_vs_saved_geometry_error_upper':geom,
          'max_angular_alpha_component_jacobian_l1_upper':max_jac,
          'max_angular_X_component_difference_upper':max_local,
          'frob_Xref_upper':A,'frob_deltaX_upper':B,
          'Gram_weyl_delta_upper':delta_S,
          'strict_original_continuum_rank2_lambda2_lower_margin_floor_decimal':margin,
          'rank_at_least_two':remain>0,
          'integrator_GL_enclosed':d['tube_self_consistent'],
          'conditional_on_parent_PR270_PR264_exact_source_proofs':True,
          'conditional_on_correct_MPFR192_interval_arithmetic_implementation':True,
          'third_mode': 'UNRESOLVED',
          'upper_DAG':'9/15','CE1':'PARTIAL','production_ready':False,'merge_ready':False,'auto_next':False}
    if not d['tube_self_consistent']:data['rank_at_least_two']=False
    root.mkdir(exist_ok=True,parents=True)
    (root/f'GL{n}_CE1AB_RANK2_N{N}.json').write_text(json.dumps(data,indent=2)+'\n')
    with (root/f'GL{n}_ANGULAR_JACOBIAN_41.csv').open('w',newline='') as fd:
        wr=csv.writer(fd);wr.writerow(['u','geometry_bound','Jac_l1_alpha40','Jac_l1_alpha42','Jac_l1_alpha44','delta_X40','delta_X42','delta_X44']);
        for row in outrows:wr.writerow([row['u'],geom,*row['derivative_l1_upper'],*row['delta_X_per_mode_upper']])
    print('CERT',n,'GEO',geom,'Xnorm',A,'DXnorm',B,'deltaGram',delta_S,'rank2_margin_floor',margin,'CERTIFIED?',data['rank_at_least_two'],flush=True)
    return data

def float_to_mpfr(x):
    # MPFR192 point exactly equal to stored outward-binary64 bound.
    from mpfr192_sky import d
    return d(x)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--n',type=int,choices=[6,8],default=6);p.add_argument('--divisions',type=int,default=32);a=p.parse_args()
    run(a.n,a.divisions,BASE/'results')
