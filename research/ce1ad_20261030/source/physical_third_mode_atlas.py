#!/usr/bin/env python3
"""CE1-AD actual source-locked l4 third temporal mode atlas (numerical diagnostics).

Reuses 82 physical timejet records from immutable original GL6/8 six-cell source,
plus strictly inherited MPFR192 angular intervals. The continuum theorem comes
from certify_sampled_lambda3.py; eigenvectors/phase and time plots here are
numerical diagnostics, not an independent certificate or a CMB likelihood.
"""
from __future__ import annotations
from pathlib import Path
import csv,hashlib,itertools,json
import numpy as np
from certify_sampled_lambda3 import BASE,find_input,scale_columns,hex_mpfr192_rational,SOURCE_SHA

SOURCE_SHA_LOCK=SOURCE_SHA

def main():
    results={};records=[]
    for n in (6,8):
        mpfr_file=find_input(f'GL{n}_SOURCE_MPFR192.json',f'ce1aa_20261030/data/GL{n}_mpfr192_source_41.json')
        a=json.loads(mpfr_file.read_text())
        assert a['source_sha256']==SOURCE_SHA_LOCK
        src=BASE/'input'/f'GL{n}_PHYSICAL_TIMEJETS.csv'
        if not src.exists():
            src=BASE.parent/'ce1ac_20261030'/'data'/f'GL{n}_ORIGINAL_L4_TIMEJET_41.csv'
        with src.open() as fd: rows=list(csv.DictReader(fd))
        assert len(rows)==41
        # MPFR192 intervals from PR275; midpoint used solely for numerical SVD.
        mat=np.array([[(float(v.lo)+float(v.hi))/2 for v in scale_columns(st['alpha_mpfr192'])] for st in a['states']])
        old=np.array([[float(r[f'X{i}']) for i in range(3)] for r in rows])
        max_reuse=np.max(abs(mat-old))
        assert max_reuse<1e-12,'Previously frozen original 41 X values no longer agree'
        U,s,Vh=np.linalg.svd(mat,full_matrices=False)
        v3=Vh[2].copy()
        if v3[2]<0:v3*=-1
        amp=mat@v3
        deriv=np.array([[float(r[f'dX{i}']) for i in range(3)] for r in rows])@v3
        secderiv=np.array([[float(r[f'd2X{i}']) for i in range(3)] for r in rows])@v3
        signs=np.sign(amp);cross=[]
        for k in range(40):
            if signs[k]*signs[k+1]<0: cross.append([float(rows[k]['u']),float(rows[k+1]['u'])])
        maxdet=0;best=None
        for i,j,k in itertools.combinations(range(41),3):
            value=float(np.linalg.det(mat[[i,j,k]]))
            if abs(value)>maxdet:maxdet=abs(value);best=(i,j,k,value)
        out={
          'GL':n,'original_source_sha256':SOURCE_SHA_LOCK,
          'original_mpfr192_source_json_sha256':hashlib.sha256(mpfr_file.read_bytes()).hexdigest(),
          'numerical_41sample_singular_values':s.tolist(),
          'numerical_lambda3':float(s[-1]**2),
          'physical_41sample_mode3_direction_X40_X42_X44':v3.tolist(),
          'sum_mode3_amplitude_sq':float(np.dot(amp,amp)),
          'mode3_amplitude_first':float(amp[0]),'mode3_amplitude_last':float(amp[-1]),
          'mode3_amplitude_min':float(amp.min()),'mode3_amplitude_max':float(amp.max()),
          'third_mode_sign_crossing_u_brackets':cross,
          'max_absolute_three_epoch_det_X':maxdet,
          'max_three_epoch_det_indices_and_signed_value':best,
          'max_abs_agreement_with_old_saved_GL_41_X':float(max_reuse),
          'scope':'numerically checked, exact original GL sources at frozen geometry; not extra continuum eigenvalue certification'}
        results[str(n)]=out
        for k,r in enumerate(rows):
            records.append({'GL':n,'epoch':k,'u':r['u'],
                       'X40':mat[k,0],'X42':mat[k,1],'X44':mat[k,2],
                       'mode3_amplitude':amp[k],
                       'mode3_time_derivative_at_fixed_v':deriv[k],
                       'mode3_second_time_derivative_at_fixed_v':secderiv[k],
                       'E':r['E'],'C4_fractional':r['C4'],'C4_fractional_prime':r['C4prime']})
    with (BASE/'data'/'CE1AD_82_PHYSICAL_THIRD_MODE_TIMELINE.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(records[0]));wr.writeheader();wr.writerows(records)
    (BASE/'data'/'THIRD_MODE_ATLAS.json').write_text(json.dumps(results,indent=2)+'\n')
    for n,x in results.items():print('ATLAS',n,'lambda3 numeric',x['numerical_lambda3'],'minmax',x['mode3_amplitude_min'],x['mode3_amplitude_max'],'maxtriple',x['max_three_epoch_det_indices_and_signed_value'])
    return results

if __name__=='__main__':main()
