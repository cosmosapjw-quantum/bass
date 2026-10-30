#!/usr/bin/env python3
"""CE1-AA: exact-real K4 interval + certified positive secondary Gram mode
of the original continuum source on frozen DOP853 binary64 geometry states.
Does not certify DOP853 solution of the Einstein-Vlasov ODE.
"""
from __future__ import annotations
import csv,hashlib,json,math,sys
from fractions import Fraction
from pathlib import Path
import numpy as np
from mpfr192_sky import IV,run_one,ROOT,PREC,SOURCE_SHA,INPUT_SHA,RAY_SHA,op,cmp

EVIDENCE=ROOT/'input/l4_source_and_transfer.json'


def matrix(rows):
    rt2=IV.val(2).sqrt()
    return [[z['alpha'][0]/3,rt2*z['alpha'][1]/3,rt2*z['alpha'][2]/3] for z in rows]

def spectral_matrix(X):
    n=len(X);A=[]
    for i in range(3):
        A.append([sum((X[t][i]*X[t][j] for t in range(n)),IV.val(0)) for j in range(3)])
    return A

def determinant(M):
    a,b,c=M[0];d,e,f=M[1];g,h,i=M[2]
    return a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g)

def minus_L(S,L):
    return [[S[i][j]-(L if i==j else 0) for j in range(3)] for i in range(3)]

def lower_second_mode_proof(S,L):
    det=determinant(minus_L(S,L))
    d0,d1=det.pair()
    tr=sum((S[i][i] for i in range(3)),IV.val(0)).pair()
    if not (d1<0 and tr[0]>3*L):raise AssertionError(('second mode criterion failed',L,det.pair(),tr))
    return {'candidate_L_literal':L,'candidate_L_exact_f64':float(L).hex(),
            'det_S_minus_LI_outward_f64':det.pair(),
            'trace_S_outward_f64':tr,
            'theorem':'Since S=X^T X PSD, trace(S)>3L gives lambda1>L. det(S-LI)<0 then exactly one eigenvalue <L, so lambda2>L.'}

def build_kernel(X):
    n=len(X)
    K=[[None]*n for _ in range(n)]
    for i in range(n):
        for j in range(i,n):
            a=sum((X[i][k]*X[j][k] for k in range(3)),IV.val(0))
            K[i][j]=a;K[j][i]=a
    return K

def main():
    src=json.loads(EVIDENCE.read_text())
    assert src['source']==SOURCE_SHA
    output={'schema':'bass.ce1aa.mpfr192_stored_geometry_interval.v1','source':SOURCE_SHA,'channels':{},
            'scientific_scope':'Exactly stored binary64 DOP853 ell states, exact-real stored GL rays and original continuum angular source at these prescribed geometry states only; NOT DOP853 trajectory certificate',
            'upper_dag':'9/15','upper_edges':21,'CE1':'PARTIAL','production_ready':False,'merge_ready':False,'auto_next':False}
    import time
    for n in (6,8):
        start=time.monotonic()
        z,states,_=run_one(n,ROOT/'data',None)
        X=matrix(z)
        K=build_kernel(X)
        S=spectral_matrix(X)
        cand=3.786e-5
        cert=lower_second_mode_proof(S,cand)
        sNum=np.array([[0.5*(v.pair()[0]+v.pair()[1]) for v in row] for row in S]);approx=np.linalg.eigvalsh(sNum)[::-1]
        target=src['cases'][str(n)]
        assert target['source_ray_sha256']==RAY_SHA[n][0]
        assert target['source_mass_sha256']==RAY_SHA[n][1]
        err_dec=target['source_only_cross_kernel_error_ceil_27']
        eps=Fraction(err_dec) # exact decimal rational UPPER from parent GL proof
        low=Fraction.from_float(cand)-41*eps
        assert low>0
        import decimal
        with decimal.localcontext() as ctx:
            ctx.prec=70
            ctx.rounding=decimal.ROUND_FLOOR
            lower_str=format(decimal.Decimal(low.numerator)/decimal.Decimal(low.denominator),'.38f')
        res={'GL':n,'ray_count':6*n*n,'epoch_count':41,'physical_pair_count':41*41,
            'normal_frame_sky_source_type':'original six-cell frozen source and exact stored GL rays',
            'enclosure':'192-bit MPFR RNDD/RNDU for each step; returned binary64 endpoints outward-rounded again',
            'exact_rays_sha256':RAY_SHA[n][0],'exact_masses_sha256':RAY_SHA[n][1],
            'exact_stored_history_sha256':INPUT_SHA[n],
            'source_only_K4_from_PR270_exact_decimal_upper':err_dec,
            'source_41x41_weyl_matrix_spectral_norm_upper_decimal':str(41*eps),
            'stored_GL_lambda2_strict_lower_candidate':cert,
            'continuous_original_six_cell_source_fixed_geometry_lambda2_lower_rational':str(low),
            'continuous_original_six_cell_source_fixed_geometry_lambda2_lower_decimal':lower_str,
            'stored_GL_lambda_estimates_exploratory':approx.tolist(),
            'max_width_f64_alpha':max(v[1]-v[0] for row in states for v in row['alpha']),
            'max_binary64_DOP_coefficient_gap_from_interval':max(v for row in states for v in row['raw_float_outside_interval'].values()),
            'max_abs_K4_element_interval_width_f64':max(x.pair()[1]-x.pair()[0] for row in K for x in row),
            'K4_endpoint_original_stored_geometry_interval_f64':K[0][-1].pair(),
            'K4_initial_diagonal_interval_f64':K[0][0].pair(),
            'K4_final_diagonal_interval_f64':K[-1][-1].pair(),
            'certified_evaluation_basis':'exact saved binary64 geometry and exact saved binary64 GL rays, MPFR192 signed source/arithmetic',
            'DOP853_geometry_accuracy':'NOT_CERTIFIED',
            'continuous_einstein_vlasov_solution_lambda2':'NOT_CERTIFIED',
            'GL_source_at_fixed_geometry_lambda2':'CERTIFIED_STRICTLY_POSITIVE_IF_PARENT_PR270_PROOF_ACCEPTED',
            'runtime_s':time.monotonic()-start}
        # Store 41^2 nontrivial physical interval-valued angular-energy observable data.
        outcsv=ROOT/'data'/f'GL{n}_MPFR192_K4_1681.csv'
        with outcsv.open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['u','v','K4_delta_lbound_float_outward','K4_delta_ubound_float_outward','claim_scope'])
            for i in range(41):
                for j in range(41):
                    p=K[i][j].pair();w.writerow([states[i]['u'],states[j]['u'],repr(p[0]),repr(p[1]),'fixed-stored-DOP853-geometry-source-only'])
        # Time-resolved nested-Gram scientific observable: first prefix for
        # which the ORIGINAL continuum source's secondary temporal mode can
        # be certified at the *specified stored geometry states*.
        prefix=[]
        first_certified=None
        for count in range(1,42):
            small=spectral_matrix(X[:count])
            num=np.array([[sum((v.pair()))/2 for v in row] for row in small])
            eig=np.linalg.eigvalsh(num)[::-1]
            kerr=eps*count
            entry={'count':count,'last_u':states[count-1]['u'],
                   'lambda1_numeric':float(eig[0]),'lambda2_numeric':float(eig[1]),
                   'lambda3_numeric':float(eig[2]),
                   'source_weyl_upper_decimal':str(kerr),
                   'continuum_secondary_mode_certified':False}
            if count>=2 and eig[1]>float(kerr):
                proposal=(float(eig[1])+float(kerr))/2
                try:
                    tested=lower_second_mode_proof(small,proposal)
                    ge=Fraction.from_float(proposal)-kerr
                    if ge>0:
                        entry['continuous_source_lambda2_lower_decimal']=str(ge.numerator)+'/'+str(ge.denominator)
                        entry['stored_source_lambda2_lower_candidate_binary64_hex']=proposal.hex()
                        entry['det_interval_f64']=tested['det_S_minus_LI_outward_f64']
                        entry['continuum_secondary_mode_certified']=True
                        if first_certified is None:first_certified=count
                except AssertionError:
                    pass
            prefix.append(entry)
        assert prefix[-1]['continuum_secondary_mode_certified']
        res['first_certified_nonzero_continuum_secondary_mode_prefix_count']=first_certified
        res['first_certified_nonzero_continuum_secondary_mode_time']=states[first_certified-1]['u']
        res['prefix_certification_count']=sum(p['continuum_secondary_mode_certified'] for p in prefix)
        with (ROOT/'data'/f'GL{n}_CUMULATIVE_41_PREFIX_SPECTRA.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['count','last_u','lambda1_numeric','lambda2_numeric','lambda3_numeric','source_weyl_upper_decimal','continuum_secondary_mode_certified','stored_source_lambda2_lower_candidate_binary64_hex','continuous_source_lambda2_lower_decimal','det_interval_f64'])
            w.writeheader();w.writerows(prefix)
        import hashlib
        res['K4_csv_sha256']=hashlib.sha256(outcsv.read_bytes()).hexdigest()
        output['channels'][str(n)]=res
        print('CE1AA_MPFR192',n,'FIXED_GEOM_LAMBDA2_LOWER',lower_str,'STORED_LAMBDAS',approx,'MAX_MPFR_ALPHA_FLOAT_INTERVAL_WIDTH',res['max_width_f64_alpha'],'seconds',round(res['runtime_s'],3),flush=True)
    (ROOT/'data/SCIENCE_RESULTS.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    return output

if __name__=='__main__':main()
