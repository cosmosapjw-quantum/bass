#!/usr/bin/env python3
"""CE1AG: source-locked rational proof W(u)>0 on u in [0,2/25].

This is a proof for the exact original continuum six-cell Einstein--Vlasov
initial value problem, not for a GL surrogate. All numerical inequalities
in the certificate are checked as integer/fraction comparisons. Standard
analytic facts invoked separately: 7/5<sqrt(2)<3/2, 3<pi<22/7,
exp(x)<=1/(1-x) for 0<=x<1, and exp(-x)>=1-x for x>=0.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import csv
import hashlib
import json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL_SOURCE_SHA='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
MU=np.array([0.,.5,1.],dtype='<f8')
PHI=np.array([0.,.25,.75,1.],dtype='<f8')
CELLS=np.array([[.1,.25,.05],[.2,.15,.15]],dtype='<f8')
SHEAR=np.array([.2,-.13,-.07],dtype='<f8')
U=F(2,25)
EUP=F(901,1000)
ELOW=F(899,1000)
HLO=F(5,9)
HUP=F(14,25)
L=F(7,100)
HMAX=F(77,100)
WTHRESH=F(1,5000)
ETHRESH=F(7,10)


def frac(v):
    return F.from_float(float(v))


def certify():
    got_sha=hashlib.sha256(MU.tobytes()+PHI.tobytes()+CELLS.tobytes()+SHEAR.tobytes()).hexdigest()
    assert got_sha==ORIGINAL_SOURCE_SHA,('source_array_sha_mismatch',got_sha)
    ss=list(map(frac,SHEAR));assert sum(ss)==0
    cc=[[frac(v) for v in row] for row in CELLS]
    assert all(v>0 for row in cc for v in row)
    assert list(map(frac,MU))==[F(0),F(1,2),F(1)]
    assert list(map(frac,PHI))==[F(0),F(1,4),F(3,4),F(1)]
    E=sum(map(sum,cc)); Pz=F(0); D=F(0)
    for i in range(2):
        a,b=map(frac,MU[i:i+2]);musq=(a*a+a*b+b*b)/3
        Pz+=sum(cc[i])*musq
        D+=(1-musq)*(cc[i][0]-cc[i][2])
    assert D>0
    sx,sy,sz=ss
    A=(sx+sy)*(E-Pz)/2+sz*Pz
    B=(sx-sy)/2
    assert B>0
    # Exact actual W(0)=A+B*(2sqrt(2)/pi)*D
    # Lower bound using 7/5<sqrt(2) and pi<22/7.
    Wlo=A+B*D*(2*F(7,5)/F(22,7))
    # Upper bound on |Px-Py|: 2sqrt(2)/pi<1 from sqrt(2)<3/2, pi>3.
    Pxupper=(E-Pz+D)/2
    assert F(899,1000)<E<EUP
    assert Pz/E<F(37,100) and Pxupper/E<F(37,100)
    assert Wlo>F(7,1000)
    S0=sum(v*v for v in ss)/2
    H0sq=(E+S0)/3
    assert HLO*HLO<H0sq<HUP*HUP
    assert max(abs(x) for x in ss)<F(21,100)
    assert HLO>F(21,100)  # all h_i(0)=H0+sigma_i(0)>0
    # h_i'= -theta h_i + P_i, 0<P_i<=E<=E0, hence h_i>0 and h_i<=h_i(0)+EUP*u.
    assert HUP+F(21,100)<=HMAX
    # For all 0<=u<=U, 0<=ell_i<=U*(HMAX+EUP*U)<L.
    assert U*(HMAX+EUP*U)<L
    # w_i(u)<= exp(3L) w_i(0) <= w_i(0)/(1-3L)< 37/79 <2/3.
    assert 3*L<F(1)
    wcap=F(37,100)/(1-3*L)
    assert wcap==F(37,79) and wcap<F(2,3)
    # H'= -2H^2-S/3, 0<=S<=3H^2, so H>=H0/(1+3H0 u).
    theta_floor=3*HLO/(1+3*HLO*U)
    assert theta_floor==F(25,17)
    # sigma'_i=-theta sigma_i+Pi_i, |Pi_i|<=EUP/3.
    M=EUP/(3*theta_floor)
    assert all(abs(v)<M for v in ss)
    k=3*HUP; b=2*M*M
    q0lo=Wlo/EUP
    # q'= -3H q + E||w-1/3||^2 -2 sum sigma_i^2 w_i
    #       + sigma^T (R/E) sigma + q^2 >= -3H q -2M^2.
    # Until first zero q>=0, H<=HUP; comparison gives q(u)>
    # q0lo*(1-k u)-b u >= q0lo*(1-k U)-b U.
    q_uniform=q0lo*(1-k*U)-b*U
    assert k*U<1 and q_uniform>WTHRESH
    # E'/E=-theta-sum_i h_i w_i >= -(3HUP+HMAX+EUP U) = -K.
    K=k+HMAX+EUP*U
    E_uniform=ELOW*(1-K*U)
    assert K*U<1 and E_uniform>ETHRESH
    W_uniform=ETHRESH*WTHRESH
    assert W_uniform==F(7,50000)
    data=[]
    for j in range(401):
        t=U*F(j,400)
        qlb=q0lo*(1-k*t)-b*t
        elb=ELOW*(1-K*t)
        wlb=qlb*elb
        assert qlb>=q_uniform>WTHRESH
        assert elb>=E_uniform>ETHRESH
        assert wlb>W_uniform
        data.append((str(t),format(float(t),'.17g'),format(float(qlb),'.17g'),format(float(elb),'.17g'),format(float(wlb),'.17g')))
    cert={
      'schema':'bass.ce1ag.original_continuum_finite_horizon_work_sign.v1',
      'base_ce1af_pr':284,'base_ce1af_head':'a3e1139e043e3f42f682a0dd84857db819972e73',
      'source_array_sha256':got_sha,'model':'exact original six-cell massless collisionless diagonal Bianchi I, Lambda=0, signature (-,+,+,+)',
      'time_u':['0',str(U)],'input_provenance':'exact fractions from original binary64 values; not GL rays',
      'initial_exact':{'E0':str(E),'Pz0':str(Pz),'D0':str(D),'sigma0':list(map(str,ss)),
                       'S0':str(S0),'H0_squared':str(H0sq),'W0_strict_lower':str(Wlo)},
      'bounds_rational':{'E0_upper':str(EUP),'E0_lower':str(ELOW),'H0_lower':str(HLO),
                        'H0_upper':str(HUP),'ell_upper':str(L),'h_initial_upper':str(HMAX),
                        'initial_w_i_upper':'37/100','horizon_w_i_upper':str(wcap),
                        'theta_lower':str(theta_floor),'shear_abs_upper':str(M),
                        'H_upper':str(HUP),'q0_lower':str(q0lo),
                        'q_uniform_strict_lower':str(q_uniform),'q_uniform_decimal_display':format(float(q_uniform),'.17g'),
                        'q_claim':'q(u)=W/E>1/5000 for every u in [0,2/25]',
                        'E_uniform_strict_lower':str(E_uniform),
                        'W_claim':'W(u)>7/50000 for every u in [0,2/25]',
                        'K_energy_upper':str(K)},
      'proof_type':'conditional analytic comparison plus exact rational original source certificate',
      'proof_status':'derived_and_exact_rational_inequalities_checked; analytic inequalities require mathematical review',
      'numerical_gl_not_used':True,'data_rows':len(data),'upper_DAG':'9/15','CE1':'PARTIAL',
      'new_upper_nodes':0,'distinct_author_R6':'NOT_RUN','distinct_author_C9':'NOT_RUN',
      'production_ready':False,'merge_ready':False,'auto_next':False}
    return cert,data


def main():
    cert,rows=certify()
    dest=ROOT/'data';dest.mkdir(parents=True,exist_ok=True)
    (dest/'CE1AG_CONTINUUM_SIGN_CERTIFICATE.json').write_text(json.dumps(cert,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    with (dest/'CE1AG_RIGOROUS_LOWER_CURVE_401.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['u_rational','u','q_lower','E_lower','W_lower']);w.writerows(rows)
    print('CE1AG_CONTINUUM_SIGN_RATIONAL_PASS',
          'q_min>',cert['bounds_rational']['q_uniform_decimal_display'],
          'W>',str(F(7,50000)), 'rows=',len(rows))
    return cert

if __name__=='__main__':main()
