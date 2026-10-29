#!/usr/bin/env python3
"""Exact-rational source-discrepancy certificate for CE1-T binary64 GL6/GL8.

This certifies exact-real continuum-vs-the-STORED BINARY64 positive quadrature
source over the entire expanding logscale box [0, 0.08]^3. It does NOT
certify roundoff in a live binary64 BLAS implementation, its numerical ODE,
or ideal Gauss nodes/weights. No MPFR execution is asserted.
"""
from __future__ import annotations
import sys, json, hashlib, math, functools
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import numpy as np
def _find_root():
    for root in Path(__file__).resolve().parents:
        if (root/'research'/'ce1t_20261030'/'cellwise_gl_rust.py').is_file():
            return root
    raise FileNotFoundError('Frozen CE1-T source not in parent directories')
ROOT=_find_root()
sys.path.insert(0,str(ROOT/'research'/'ce1t_20261030'))
from cellwise_gl_rust import make_cell_rays, frozen_source_identity, MU,PHI,CELL_E,SHEAR

PREC=92
Q=F(1,11); B=F(23,25); PREF=F(21,20); T=F(2,25); ENERGY=sum((F.from_float(float(x)) for x in CELL_E.flatten()),F(0))
SOURCE_SHA=frozen_source_identity()

def arctan_bounds(x:F,N:int):
    s=F(0)
    for k in range(N):s+= (-1)**k*x**(2*k+1)/F(2*k+1)
    nxt=(-1)**N*x**(2*N+1)/F(2*N+1)
    return min(s,s+nxt),max(s,s+nxt)

def pi_bounds():
    a=arctan_bounds(F(1,5),80);b=arctan_bounds(F(1,239),35)
    return 16*a[0]-4*b[1],16*a[1]-4*b[0]

PI_L,PI_H=pi_bounds()
SQ=int(math.isqrt(2*10**(2*PREC)))
SQ_L,SQ_H=F(SQ,10**PREC),F(SQ+1,10**PREC)
assert PI_L<PI_H and SQ_L*SQ_L<=2<=SQ_H*SQ_H

def sin_exact(ks:int,t:F):
    k=ks*t
    # source fraction edges are {0,1/4,3/4,1}. sin(k*pi/4) in Q(sqrt(2))
    assert (4*k).denominator==1,k
    n=int(4*k) % 8
    base={0:(0,0),1:(0,F(1,2)),2:(1,0),3:(0,F(1,2)),4:(0,0),5:(0,F(-1,2)),6:(-1,0),7:(0,F(-1,2))}
    return base[n]

@functools.lru_cache(None)
def phi_avg_symbol(a:int,b:int,lo:F,hi:F):
    n=a+b
    A={}
    for p in range(2*a+1):
        for q in range(2*b+1):
            k=n-p-q
            A[k]=A.get(k,F(0))+F((-1)**(b+q)*math.comb(2*a,p)*math.comb(2*b,q),4**n)
    assert all(A[k]==A.get(-k,0) for k in A)
    base=A.get(0,F(0)); r=F(0); s=F(0)
    for k in range(1,n+1):
        hi0,hi1=sin_exact(k,hi);lo0,lo1=sin_exact(k,lo)
        fac=F(2)*A.get(k,0)/F(k)/(hi-lo)
        r+=fac*(hi0-lo0);s+=fac*(hi1-lo1)
    return base,r,s

@functools.lru_cache(None)
def mu_avg(a,b,c,lo:F,hi:F):
    m=a+b
    out=F(0)
    for j in range(m+1):
        d=2*(c+j)+1
        out+=F((-1)**j*math.comb(m,j))*(hi**d-lo**d)/F(d)/(hi-lo)
    return out

@functools.lru_cache(None)
def continuum_symbol(a,b,c):
    # E_cell weights are eight-reflection positive-octant masses.
    A=D=G=F(0)
    for i in range(2):
        for j in range(3):
            mu_a=F.from_float(float(MU[i]));mu_b=F.from_float(float(MU[i+1]))
            ph_a=F.from_float(float(PHI[j]));ph_b=F.from_float(float(PHI[j+1]))
            fac=F.from_float(float(CELL_E[i,j]))*mu_avg(a,b,c,mu_a,mu_b)
            z=phi_avg_symbol(a,b,ph_a,ph_b)
            A+=fac*z[0];D+=fac*z[1];G+=fac*z[2]
    return A,D,G

def continuum_interval(t):
    A,D,G=t
    t=[D+G*SQ_L,D+G*SQ_H]
    lo,hi=min(t),max(t)
    vals=(lo/PI_L,lo/PI_H,hi/PI_L,hi/PI_H)
    return A+min(vals),A+max(vals)

def all_monos(K):
    # monomials total order 1..K+1
    return [(a,b,c) for d in range(1,K+2) for a in range(d+1) for b in range(d-a+1) for c in [d-a-b]]

def gl_moments_exact(n:int,K:int):
    rays,mass=make_cell_rays(n)
    # Lock source and ray/mass SHA from source-native CE1T code.
    sha={'ray_sha256':hashlib.sha256(np.asarray(rays,dtype='<f8').tobytes()).hexdigest(),
         'mass_sha256':hashlib.sha256(np.asarray(mass,dtype='<f8').tobytes()).hexdigest()}
    mons=all_monos(K)
    out={m:F(0) for m in mons}
    for nn,w in zip(rays,mass):
        wx=F.from_float(float(w))
        coords=[F.from_float(float(t))**2 for t in nn]
        powers=[[F(1)] for _ in range(3)]
        for axis in range(3):
            for j in range(K+1):powers[axis].append(powers[axis][-1]*coords[axis])
        for a,b,c in mons:
            out[a,b,c]+=wx*powers[0][a]*powers[1][b]*powers[2][c]
    # init energy mismatch in exactly stored binary64 rays: use sqrt(r²)-1 ≤ |r²−1|.
    E0b=sum([F.from_float(float(w)) for w in mass],F(0))
    norm_gap=sum((F.from_float(float(w))*abs(sum((F.from_float(float(q))**2 for q in nn),F(0))-1) for nn,w in zip(rays,mass)),F(0))
    assert all(abs(sum((F.from_float(float(t))**2 for t in nn),F(0))-1)<F(1,10**12) for nn in rays)
    assert E0b < F(91,100) and E0b>F(89,100)
    init_E_bound=abs(E0b-ENERGY)+norm_gap
    return out,sha,init_E_bound,len(mass),norm_gap

def calc(n:int,K=6):
    import time
    start=time.perf_counter()
    print('GL',n,'monomials',len(all_monos(K)),flush=True)
    gl,hashes,init_gap,nr,norm_gap=gl_moments_exact(n,K)
    delta={}
    for j,mono in enumerate(gl):
        a,b=continuum_interval(continuum_symbol(*mono)); v=gl[mono]
        delta[mono]=max(abs(a-v),abs(b-v))
    # For all log-scales in [0,.08]^3, alpha_i plus floating ray norm ≤1/11.
    factors=[]
    for i in range(3):
        pre=F(0)
        by_degree=[]
        for k in range(K+1):
            moment_sum=F(0)
            for a in range(k+1):
                for b in range(k-a+1):
                    c=k-a-b
                    coeff=F(math.factorial(k),math.factorial(a)*math.factorial(b)*math.factorial(c))
                    mono=(a+(i==0),b+(i==1),c+(i==2))
                    moment_sum+=coeff*delta[mono]
            term=F(math.comb(2*k,k),4**k)*Q**k*moment_sum
            pre+=term
            by_degree.append(float(term))
        tail=2*PREF*F(91,100)*Q**(K+1)/(1-Q) # safe total source weight <.91
        # Correct binary64 stored rays are not mathematically unit vectors.
        # Surrogate X=sum(alpha_j n_j²) differs from actual (r²-B)/B by
        # d=|n|²−1. For r² and surrogate >=.83, |d(x^-1/2)/dx|<1.
        # Thus each positive stored-ray source difference is <=2 sum_w w|d|.
        # (B<=1, b_i n_i²<=1+1e-12, safe factor 2.)
        bound=PREF*pre+tail+2*norm_gap
        factors.append((bound,by_degree,float(tail)))
    eps=max(x[0] for x in factors)
    # Z=norm_inf(delta h)+norm_inf(delta ell), bounded by Gronwall L=7.
    # 7 T=14/25, exp(7T) <= 1/(1-7T)=25/11 and forcing <= T/(1-7T)=2/11.
    geometry_bound=F(25,11)*(init_gap/F(3))+F(2,11)*eps
    result={
      'certificate':'EXACT_RATIONAL_REAL_SOURCE_BOUND_NOT_FLOAT_RUNTIME_NOT_MPFR192',
      'source_sha256':SOURCE_SHA,'n':n,'rays':nr,'K':K,
      'box':{'ell_i_min':'0','ell_i_max':'2/25','a_i_initial':'1','u_final':'2/25'},
      'preconditions':{'all_expanding':True,'h_i_initial_less_than_one':True,'massless_trace':True,'max_h_i':'1','max_energy':'91/100'},
      'q_exact':'1/11','b_reference_exact':'23/25','prefactor_bound':'21/20',
      'stored_gl_hashes':hashes,
      'max_abs_initial_energy_defect_upper':format(float(init_gap),'.17g'),
      'stored_ray_nonunit_weighted_defect':float(norm_gap),
      'stored_ray_nonunit_correction_upper':float(2*norm_gap),
      'max_source_pressure_discrepancy_per_i': [float(x[0]) for x in factors],
      'maximum_epsilon_source_exact':str(eps.numerator)+'/'+str(eps.denominator),
      'maximum_epsilon_source':float(eps),
      'maximum_epsilon_ceil_1e20':str((eps*10**20).__ceil__())+'/100000000000000000000',
      'final_h_ell_bound':float(geometry_bound),
      'final_h_ell_bound_exact':str(geometry_bound.numerator)+'/'+str(geometry_bound.denominator),
      'final_h_ell_ceil_1e20':str((geometry_bound*10**20).__ceil__())+'/100000000000000000000',
      'target_h':1e-5,'meets_target':bool(geometry_bound<F(1,100000)),
      'moment_count':len(delta),
      'max_delta_moment':float(max(delta.values())),
      'each_pressure_by_degree': [x[1] for x in factors],
      'tail_each': [x[2] for x in factors],
      'pi_interval_method':'Machin alternating rational arctan with explicit next-term enclosure',
      'sqrt2_interval_method':'integer isqrt with 10^92 outward rational truncation',
      'pi_enclosure_digits':PREC, 'pi_interval_width':float(PI_H-PI_L),
      'sqrt2_interval_width':float(SQ_H-SQ_L),
      'rationale':'Analytic finite binomial polynomial difference + positive angular mass tails; Q=1/11 safely includes exact binary64 off-unit ray error after explicit bound' ,
      'elapsed_seconds':time.perf_counter()-start,
    }
    print('RESULT',n,'eps',result['maximum_epsilon_source'],'geometry',result['final_h_ell_bound'],'time',round(result['elapsed_seconds'],2),flush=True)
    return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--order',type=int,default=6);p.add_argument('--K',type=int,default=6);p.add_argument('--output',required=True);args=p.parse_args()
    r=calc(args.order,args.K)
    Path(args.output).parent.mkdir(exist_ok=True,parents=True)
    Path(args.output).write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
