"""Independent high-precision angular snapshot, pinned to FA03 original formulas.

This independently evaluates B(x,theta,phi), not the full six-state ODE.
It does not create a validated continuum cap certificate.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import mpmath as mp

ROOT=Path(__file__).resolve().parent
R7=ROOT.parent/"fa03_c5_angular_cap_20261015"/"reference"
LOCKS={"fa02.py":"1e89e75f7a08d2eec1851a58e602c2683b1888a37b3e1fe10b1be4234756eee5",
       "fa03.py":"ad865127da7c2f9ea613541571f9b842f9da7630af9bb951a3df5968ad44ecf7"}
def source_lock():
    for name,expect in LOCKS.items():
        if hashlib.sha256((R7/name).read_bytes()).hexdigest()!=expect:
            raise ValueError("SOURCE_BYTE_IDENTITY_MISMATCH:"+name)

def cross(u,v):
    return (u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])

def source_at(t,phi,x,return_operator=False):
    """Independent mpmath transcription of fa02.setup and fa03.fields."""
    m=mp.mpf
    chi=m("0.008");psi=m("0.01")
    r=2*mp.asin(mp.sqrt((1+t)/2)*mp.sin(m("0.02")/2))
    ell=(mp.cos(r),mp.sin(r)*mp.cos(phi),mp.sin(r)*mp.sin(phi))
    cs=mp.cos(psi);sn=mp.sin(psi); ch=mp.cosh(chi); sh=mp.sinh(chi)
    vec=(cs*ell[0]-sn*ell[1],sn*ell[0]+cs*ell[1],ell[2])
    L=ch+sh*vec[0]; n=((sh+ch*vec[0])/L,vec[1]/L,vec[2]/L)
    dm=mp.sqrt(1-vec[1]**2)
    aw=(-vec[0]*vec[1]/dm,dm,-vec[1]*vec[2]/dm)
    bw=(-vec[2]/dm,m(0),vec[0]/dm)
    A=[(aw[i],bw[i]) for i in range(3)]
    Avec=[[ch*A[0][j] if i==0 else A[i][j] for j in range(2)] for i in range(3)]
    At=[[Avec[i][j]-sh*n[i]*A[0][j] for j in range(2)] for i in range(3)]
    hh=mp.sqrt(n[0]**2+n[1]**2)
    kk=(-n[1]/hh,n[0]/hh,m(0))
    B0=[(kk[i],cross(n,kk)[i]) for i in range(3)]
    C=[[sum(B0[k][i]*At[k][j] for k in range(3)) for j in range(2)] for i in range(2)]
    v=mp.sqrt(1-(1-x*x)*n[2]*n[2])
    q=x**(-m(2)/3)*v
    e=(n[0]/v,n[1]/v,x*n[2]/v)
    B=[(kk[i],cross(e,kk)[i]) for i in range(3)]
    S=[[sum(B[i][k]*C[k][j] for k in range(2)) for j in range(2)] for i in range(3)]
    P3=((m(0),m(0),m(0)),
        (m(0),m(".7"),m(".1")+1j*m(".05")),
        (m(0),m(".1")-1j*m(".05"),m(".3")))
    P=[[sum(S[i][a]*P3[i][j]*S[j][b] for i in range(3) for j in range(3)) for b in range(2)] for a in range(2)]
    scale=m("1.0004")+m(".1")*m("1.000800032")*L*q
    source=[[scale*P[a][b] for b in range(2)] for a in range(2)]
    if not return_operator:
        return source
    K=(m(".4"),m(".4"),m(".8"))
    H=[[m(".5")*sum(K[i]*S[i][a]*S[i][b] for i in range(3)) for b in range(2)] for a in range(2)]
    G=[[H[a][b]+m(".3")*e[0]*(-1 if (a,b)==(0,1) else 1 if (a,b)==(1,0) else 0) for b in range(2)] for a in range(2)]
    return source,H,G

def cap(nr,nphi,x,phase=None):
    phase=mp.mpf(0) if phase is None else phase
    nodes,weights=mp.gauss_quadrature(nr,"legendre")
    out=[[mp.mpc(0),mp.mpc(0)],[mp.mpc(0),mp.mpc(0)]]
    for t,w in zip(nodes,weights):
        for j in range(nphi):
            phi=2*mp.pi*(mp.mpf(j)+phase)/nphi
            B=source_at(t,phi,x)
            for a in range(2):
                for b in range(2):out[a][b]+=w*B[a][b]/(2*nphi)
    return out

def difference(a,b):
    return max(abs(a[i][j]-b[i][j]) for i in range(2) for j in range(2))

def stokes(f):
    return [mp.re(f[0][0]+f[1][1]),mp.re(f[0][0]-f[1][1]),2*mp.re(f[0][1]),-2*mp.im(f[0][1])]

def study(dps=70,xstring="0.7"):
    source_lock()
    if dps<35:raise ValueError("min dps 35")
    mp.mp.dps=dps
    x=mp.mpf(xstring)
    grids=[(2,8),(3,12),(3,16),(3,24),(4,16),(6,24)]
    data={k:cap(k[0],k[1],x) for k in grids}
    ref=data[(6,24)]
    out=[]
    for k in grids:
        out.append({"nr":k[0],"nphi":k[1],
          "stokes":[mp.nstr(y,55) for y in stokes(data[k])],
          "max_matrix_component_delta_6x24":mp.nstr(difference(data[k],ref),40)})
    phase=cap(3,12,x,mp.mpf(".37"))
    return {"type":"independent_full_real_angle_source_snapshot_not_time_integrated",
            "dps":dps,"x":xstring,"rows":out,
            "phase_point37_3x12_delta":mp.nstr(difference(data[(3,12)],phase),40),
            "time_integrated_continuum_cap_error":None}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--dps",type=int,default=70)
    p.add_argument("--x",default="0.7")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    v=study(a.dps,a.x)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.output.exists():raise FileExistsError(a.output)
    a.output.write_text(json.dumps(v,indent=2)+"\n")
    print(json.dumps(v,indent=2)[:13000])
if __name__=="__main__":main()
