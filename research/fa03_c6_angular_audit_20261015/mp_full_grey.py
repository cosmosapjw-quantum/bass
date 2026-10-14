"""Independent arbitrary-precision full grey S0 transfer for angular alias diagnosis.

This is a completely separate scalar/matrix Python implementation from frozen FA03
NumPy RK4. It checks the full S0 ODE, but is not an interval integrator and neither
this output nor its difference is a rigorous angular quadrature certificate.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import mpmath as mp
from mp_cap_snapshot import source_at, source_lock,stokes

def m2_add(A,B,s=1):
    return [[A[i][j]+s*B[i][j] for j in range(2)] for i in range(2)]

def rhs(x,F,t,phi):
    B,_,G=source_at(t,phi,x,True)
    return [[B[i][j]-sum(G[i][k]*F[k][j]+F[i][k]*G[j][k] for k in range(2)) for j in range(2)] for i in range(2)]

def one_ray(t,phi,steps):
    h=mp.mpf(".5")/steps
    F=[[mp.mpc(0),mp.mpc(0)],[mp.mpc(0),mp.mpc(0)]]
    for j in range(steps):
        x=mp.mpf(".5")+j*h
        k1=rhs(x,F,t,phi)
        k2=rhs(x+h/2,m2_add(F,k1,h/2),t,phi)
        k3=rhs(x+h/2,m2_add(F,k2,h/2),t,phi)
        k4=rhs(x+h,m2_add(F,k3,h),t,phi)
        F=[[F[i][k]+(h/6)*(k1[i][k]+2*k2[i][k]+2*k3[i][k]+k4[i][k]) for k in range(2)] for i in range(2)]
    return F

def average(nr,nphi,steps,phase="0"):
    nodes,weights=mp.gauss_quadrature(nr,"legendre")
    p=mp.mpf(phase)
    out=[[mp.mpc(0),mp.mpc(0)],[mp.mpc(0),mp.mpc(0)]]
    for t,w in zip(nodes,weights):
        for j in range(nphi):
            phi=2*mp.pi*(j+p)/nphi
            F=one_ray(t,phi,steps)
            for a in range(2):
                for b in range(2):out[a][b]+=w*F[a][b]/(2*nphi)
    return out

def delta(A,B):
    return max(abs(A[i][j]-B[i][j]) for i in range(2) for j in range(2))

def run(dps=55,steps=32,grids=((3,12),(3,16),(4,16))):
    source_lock()
    if steps<8 or dps<35:raise ValueError("steps>=8 dps>=35")
    mp.mp.dps=dps
    t0=time.monotonic();outputs={}
    for nr,nphi in grids:
        outputs[(nr,nphi)]=average(nr,nphi,steps)
    ref=outputs[grids[-1]]
    return {"type":"independent_mp_rk4_full_S0_no_interval_certificate",
      "dps":dps,"steps":steps,
      "rows":[{"nr":nr,"nphi":nphi,
         "stokes":[mp.nstr(v,50) for v in stokes(outputs[(nr,nphi)])],
         "max_entry_delta_to_last_grid":mp.nstr(delta(outputs[(nr,nphi)],ref),50)}
         for nr,nphi in grids],
      "elapsed_seconds":time.monotonic()-t0,
      "true_continuum_angular_error_bound":None,"true_ode_error_bound":None}

def main():
    p=argparse.ArgumentParser();p.add_argument("--dps",type=int,default=55)
    p.add_argument("--steps",type=int,default=32)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args();out=run(a.dps,a.steps)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.output.exists():raise FileExistsError(a.output)
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
if __name__=="__main__":main()
