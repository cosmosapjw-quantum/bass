"""Exact Fraction Hermite-defect certificate for manufactured passive matrix RK4.

Not a bound for time-dependent FA03 geodesic coefficients. This demonstrates the
correct cone-contractivity residual technology, with a physically typed toy
P3 block and diagonal positive extinction. Absolutely no sampled suprema.
"""
from __future__ import annotations
from fractions import Fraction as Q
from math import comb
import argparse,json

def cubic_bernstein(coeff):
    if len(coeff)!=4:raise ValueError("cubic coefficients exactly four")
    return tuple(sum(coeff[k]*Q(comb(i,k),comb(3,k)) for k in range(i+1))
                 for i in range(4))

def one_step(g:Q,b:Q,y:Q,h:Q):
    if g<0 or h<=0:raise ValueError("passive positive domain required")
    # Explicit RK4 for linear constant coefficient dy/dt=b-g*y.
    f=b-g*y
    z=g*h
    y1=y+h*f*(1-z/2+z*z/6-z*z*z/24)
    f1=b-g*y1
    # Endpoint-fitted cubic Hermite exactly interpolates y0,y1,f0,f1.
    a0=y
    a1=h*f
    a2=3*(y1-y)-h*(2*f+f1)
    a3=2*(y-y1)+h*(f+f1)
    # r = d[p]/dt - b +g p; residual of Hermite reconstructed trajectory.
    power=(a1/h-b+g*a0,2*a2/h+g*a1,3*a3/h+g*a2,g*a3)
    assert power[0]==0
    coeff=cubic_bernstein(power)
    # B_i^3(u)>=0, sum B_i=1 and integral B_i du=1/4.
    one_bound=h*sum((abs(z) for z in coeff),Q(0))/4
    return y1,one_bound,coeff

def componentwise_exact(numsteps=64):
    if isinstance(numsteps,bool) or not isinstance(numsteps,int) or numsteps<1:
        raise ValueError("positive steps")
    h=Q(1,2*numsteps)
    # Frozen 2x2 P3 Hermitian principal block with original exact rationals.
    real_B=((Q(7,10),Q(1,10)),(Q(1,10),Q(3,10)))
    imag_B=((Q(0),Q(1,20)),(Q(-1,20),Q(0)))
    H=(Q(1,5),Q(2,5))
    R=[[Q(0),Q(0)],[Q(0),Q(0)]]
    I=[[Q(0),Q(0)],[Q(0),Q(0)]]
    bound=Q(0)
    for _ in range(numsteps):
        for i in range(2):
            for j in range(2):
                g=H[i]+H[j]
                R[i][j],rad_r,_=one_step(g,real_B[i][j],R[i][j],h)
                I[i][j],rad_i,_=one_step(g,imag_B[i][j],I[i][j],h)
                bound+=rad_r+rad_i
    assert R[0][1]==R[1][0] and I[0][1]==-I[1][0]
    assert I[0][0]==I[1][1]==0
    # Actual error operator from p(t) has zero initial error, contractive
    # U(t,s)=diag(exp[-H_i(t-s)]), Schatten1 <= entrywise L1 residual.
    return {"schema":"bass.fa03.c8.manufactured_exact_rational.v1",
       "steps":numsteps,"dt_fraction":str(h),
       "positivity_source_minor":str(Q(7,10)*Q(3,10)-Q(1,10)**2-Q(1,20)**2),
       "source_model":"constant 2x2 original P3 physical Hermitian subblock",
       "H_diagonal":list(map(str,H)),
       "zero_screen_rotation":True,
       "interval_method":"exact Fraction RK4; cubic Hermite endpoint reconstruction; exact Bernstein L1 residual envelope integrated over every time step",
       "end_real_parts":[[str(c) for c in row] for row in R],
       "end_imag_parts":[[str(c) for c in row] for row in I],
       "global_trace_norm_residual_bound":str(bound),
       "bound_float_display":float(bound),
       "time_dependent_FA03_error_bound":None,
       "source_input_roundoff":"none, exact rationals",
       "physical_cone":"analytic exact solution PSD by Jones congruence"}

def report(steps=(8,16,32,64,128)):
    return {"reference":"contractive Jones semigroup for fixed H>=0",
      "runs":[componentwise_exact(n) for n in steps]}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=str)
    args=parser.parse_args()
    r=report()
    if args.output:
        from pathlib import Path
        p=Path(args.output)
        if p.exists():raise FileExistsError(p)
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps([{"steps":x["steps"],"global_bound":x["bound_float_display"]} for x in r["runs"]],indent=2))
