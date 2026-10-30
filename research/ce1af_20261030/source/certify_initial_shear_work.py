#!/usr/bin/env python3
"""Exact rational proof: original positive six-cell continuum initial shear work W(0)>0.007.

No GL numerical rays, no ODE integration, no floating astronomical outputs in the proof.
Uses sqrt(2)>7/5 and pi<22/7 and the original immutable exact dyadic
physical cell weights and shear. Valid only for initial u=0, NOT full horizon.
"""
from fractions import Fraction as F
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'input'))
from cellwise_gl_rust import MU,PHI,CELL_E,SHEAR,frozen_source_identity
SRC='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'

def compute():
    assert frozen_source_identity()==SRC
    mu=[F.from_float(float(x)) for x in MU]
    t=[F.from_float(float(x)) for x in PHI]
    cells=[[F.from_float(float(x)) for x in row] for row in CELL_E]
    shear=[F.from_float(float(x)) for x in SHEAR]
    assert len(cells)==2 and all(len(row)==3 for row in cells) and all(x>0 for row in cells for x in row)
    assert sum(shear)==0
    assert t==[0,F(1,4),F(3,4),1] and mu==[0,F(1,2),1]
    E=sum(sum(row) for row in cells)
    Pz=F(0);D=F(0)
    for i in range(2):
        a,b=mu[i],mu[i+1]
        musq=(a*a+a*b+b*b)/3
        for j in range(3):Pz+=cells[i][j]*musq
        # <cos(2 phi)>_cell exactly = +/- 2 sqrt(2) / pi for j=0/2,
        # with middle cell zero. Thus Px-Py=(2sqrt(2)/pi)D.
        D+=(1-musq)*(cells[i][0]-cells[i][2])
    assert D>0
    sx,sy,sz=shear
    # W = sum shear_i P_i = A + B*(2sqrt(2)/pi)*D.
    A=(sx+sy)/2*(E-Pz)+sz*Pz
    B=(sx-sy)/2
    assert B>0
    lower_sqrt2=F(7,5);upper_pi=F(22,7)
    assert lower_sqrt2**2<2 and upper_pi>3
    # pi<22/7 is Archimedes; use exact established rational bound.
    work_lower=A+B*D*(2*lower_sqrt2/upper_pi)
    assert work_lower>F(7,1000),(work_lower,F(7,1000))
    result={'schema':'bass.ce1af.exact_continuum_initial_shear_work.v1',
      'source_sha256':SRC,'proof_kind':'exact rational original six-cell continuum angular integration, only at u=0',
      'E0_exact':str(E),'Pz0_exact':str(Pz),'D_exact':str(D),
      'SHEAR_dyadic_exact':list(map(str,shear)),
      'W0_exact_form':'A + B*(2*sqrt(2)/pi)*D',
      'A_exact':str(A),'B_exact':str(B),
      'rational_relations':['sqrt(2)>7/5','pi<22/7','D>0','B>0'],
      'strict_lower_exact':str(work_lower),'strict_lower_decimal_display':format(float(work_lower),'.17g'),
      'strict_initial_shear_work_gt_0p007':work_lower>F(7,1000),
      'full_horizon_positive_work_NOT_certified':True,'upper_DAG':'9/15','CE1':'PARTIAL'}
    (ROOT/'data'/'CE1AF_EXACT_INITIAL_SHEAR_WORK.json').write_text(json.dumps(result,indent=2)+'\n')
    print('EXACT_ORIGINAL_SIXCELL_INITIAL_W', '>',float(work_lower),'E0',float(E),'Pz0',float(Pz),'D',float(D))
    return result
if __name__=='__main__':compute()
