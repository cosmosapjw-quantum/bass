"""CE1-U differential validation with ORIGINAL BASS Rust comoving Frame.
This binary64 check is not part of MPFR error proof.
"""
from __future__ import annotations
import argparse,csv,io,json,subprocess,sys,math
import numpy as np
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from research.ce1u_20261030.certified_gl_source import sample_gl_source
from research.ce1t_20261030.cellwise_gl_rust import rust_payload

def knots(path,n=41):
    out=[]
    for t in np.linspace(0,.08,n):
        j=min(np.searchsorted(path.times,t,side='right')-1,len(path.times)-2)
        d=path.times[j+1]-path.times[j];v=(t-path.times[j])/d
        c=path.coefficients[j]
        y=np.polynomial.polynomial.polyval(v,c)
        out.append({**{'u':float(t)},**{f'ell{i+1}':float(y[i]) for i in range(3)},
                    **{f'h{i+1}':float(y[i+3]) for i in range(3)}})
    return out

def run(binary):
    proof={}
    for n in (4,6,8):
        src=sample_gl_source(n)
        path=rk4_path(src,src.initial_state((.2,-.13,-.07)),.08,4,backend='python_oracle')
        history=knots(path)
        payload=rust_payload(src.n,src.mass,history)
        cp=subprocess.run([binary],input=payload,text=True,capture_output=True,timeout=100)
        if cp.returncode:raise RuntimeError('Rust BASS rejected: '+cp.stderr[:700])
        rows=list(csv.DictReader(io.StringIO(cp.stdout)))
        assert len(rows)==41
        largest={'E':0.,'P':0.,'Eprime':0.,'trace':0.,'continuity':0.}
        for row,h in zip(rows,history):
            ell=np.array([h[f'ell{i+1}'] for i in range(3)]);hh=np.array([h[f'h{i+1}'] for i in range(3)])
            e,p=src.moments(ell)
            rust_e=float(row['E']);rp=np.array([float(row[f'P{i+1}']) for i in range(3)])
            re_dot=float(row['Eprime'])
            want_e_dot=-(sum(hh)*e + np.dot(hh,p))
            largest['E']=max(largest['E'],abs(rust_e-e))
            largest['P']=max(largest['P'],max(abs(rp-p)))
            largest['Eprime']=max(largest['Eprime'],abs(re_dot-want_e_dot))
            largest['trace']=max(largest['trace'],abs(sum(rp)-rust_e))
            largest['continuity']=max(largest['continuity'],abs(re_dot+sum(hh)*rust_e+np.dot(hh,rp)))
        assert max(largest.values()) < 8e-12,largest
        proof[str(n)]={'rays':len(src.mass),'samples':len(history),'max_abs_gap':largest}
    print(json.dumps({'status':'BASS_NATIVE_RUST_COMOVING_DIFFERENTIAL_PASS',
        'scope':'independent binary64 stored GL E,P,Eprime, not MPFR certificate',
        'cases':proof},indent=2))
    return proof

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--binary',required=True);opt=a.parse_args()
    run(opt.binary)
