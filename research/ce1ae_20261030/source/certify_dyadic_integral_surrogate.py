#!/usr/bin/env python3
"""Exact-rational sign witness for the *Simpson sampled dyadic surrogate* only.

Not an enclosure of true time-integral Gram, not a substitute for the separate
physical continuum lower in spectral_gap_certificate.py.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext,ROUND_FLOOR
import csv,json,hashlib,sys
BASE=Path(__file__).resolve().parents[1]

def floor_dec(q:F, digits=40):
    scale=10**digits
    low=q.numerator*scale//q.denominator
    return f'{low//scale}.{low%scale:0{digits}d}'

def certify(n=8,trial=F(1,10**13)):
    file=BASE/'data'/'COUPLED_SIXCELL_DENSE_TIME_SKY.csv'
    with file.open() as f: rows=[r for r in csv.DictReader(f) if r['GL']==str(n)]
    N=len(rows); assert N==401
    X=[[F.from_float(float(r[k])) for k in ('X40','X42','X44')] for r in rows]
    G=[[F(0) for _ in range(3)] for _ in range(3)]
    for i,x in enumerate(X):
        wi=F((1 if i in (0,N-1) else (4 if i%2 else 2)),15000) # h/3 where h=.08/400=1/5000
        for j in range(3):
            for k in range(j,3):G[j][k]+=wi*x[j]*x[k]
    for j in range(3):
        for k in range(j): G[j][k]=G[k][j]
    m=[[G[j][k]-(trial if j==k else 0) for k in range(3)] for j in range(3)]
    d1=m[0][0];d2=m[0][0]*m[1][1]-m[0][1]**2
    d3=m[0][0]*m[1][1]*m[2][2]+2*m[0][1]*m[0][2]*m[1][2]-m[0][0]*m[1][2]**2-m[1][1]*m[0][2]**2-m[2][2]*m[0][1]**2
    result={'schema':'bass.ce1ae_exact_dyadic_401_simpson_surrogate_only.v1','GL':n,'original_numerical_data_csv_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
      'sampled_G_dyadic_Simpson_M11_minus_trial_lower_decimal':floor_dec(d1),
      'sampled_G_dyadic_Simpson_leading_det2_lower_decimal':floor_dec(d2),
      'sampled_G_dyadic_Simpson_det3_lower_decimal':floor_dec(d3,52),
      'strict_lower_for_exact_dyadic_401point_Simpson_surrogate':str(trial),
      'all_three_sylvester_minors_strict_positive':d1>0 and d2>0 and d3>0,
      'physical_continuous_time_operator_certified_by_this_Simpson_witness':False,
      'true_physical_continuous_time_gap_certificate_file':'CONTINUOUS_TIME_STRICT_GAP_WITNESS.json'}
    path=BASE/'data'/f'GL{n}_EXACT_DYADIC_SIMPSON_SURROGATE_WITNESS.json'
    path.write_text(json.dumps(result,indent=2)+'\n')
    if not result['all_three_sylvester_minors_strict_positive']:raise AssertionError('Sylvester failure')
    print('SIMPSON DYADIC GL',n,'eig3 >',trial,'(not true continuous-time bound)',flush=True)
    return result

if __name__=='__main__':
    for x in [6,8,16,64]:certify(x)
