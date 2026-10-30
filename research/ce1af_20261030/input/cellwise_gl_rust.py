#!/usr/bin/env python3
"""CE1-T: positive physical-cell tensor Gauss-Legendre angular quadrature.

Uses BASS native Rust _rustcore/src/kinetic/comoving.rs through CE1-R's verified
Rust Liouville CLI. Exactly frozen six positive original cells; no smoothing,
no redefinition of the continuum measure. Report convergence against numerical
GL40, not an interval certificate for C4' or the full Boltzmann model.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import time
import numpy as np

MU = np.array([0., .5, 1.], dtype='<f8')
PHI = np.array([0., .25, .75, 1.], dtype='<f8')
CELL_E = np.array([[.1, .25, .05], [.2, .15, .15]], dtype='<f8')
SHEAR = np.array([.2, -.13, -.07], dtype='<f8')
FROZEN_INPUT_SHA = '022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
EXPECT_COMOVING_GIT_BLOB = 'a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84'
EXPECTED_GL40_FINAL_C4PRIME = -0.00014789130274602826
EXPECTED_GL40_FINAL_E = 0.7584190590089329
DEFAULT_ORDERS = (1, 2, 3, 4, 6, 8, 12, 16, 24, 40)


def sha(data): return hashlib.sha256(data).hexdigest()

def frozen_source_identity():
    digest = sha(MU.tobytes()+PHI.tobytes()+CELL_E.tobytes()+SHEAR.tobytes())
    assert digest == FROZEN_INPUT_SHA, (digest, FROZEN_INPUT_SHA)
    return digest


def make_cell_rays(order):
    """Return 6*n^2 positive ray masses, preserving each 8-reflection cell mass.

    GL nodes are in mu=|q_z| and phi_frac=(2/pi)*atan2(|q_y|,|q_x|).
    Each cell energy is already the eight-octant sum.  Unit-interval GL weights
    integrate a constant exactly; all masses strictly positive.
    """
    if isinstance(order, bool) or not isinstance(order,int) or not 1<=order<=64:
        raise ValueError('quadrature order must be a positive integer <=64')
    nodes, qweights = np.polynomial.legendre.leggauss(order)
    nn, ww, index = [], [], []
    for i in range(2):
        for j in range(3):
            mu_center=(MU[i]+MU[i+1])/2
            mu_rad=(MU[i+1]-MU[i])/2
            ph_center=(PHI[j]+PHI[j+1])/2
            ph_rad=(PHI[j+1]-PHI[j])/2
            for a in range(order):
                u=mu_center+mu_rad*nodes[a]
                for b in range(order):
                    frac=ph_center+ph_rad*nodes[b]
                    phi=frac*math.pi/2
                    t=math.sqrt(max(0.,1-u*u))
                    n=[t*math.cos(phi),t*math.sin(phi),u]
                    w=float(CELL_E[i,j])*float(qweights[a])*float(qweights[b])/4
                    if not (w>0 and math.isfinite(w)) or abs(sum(z*z for z in n)-1)>2e-14:
                        raise ValueError('bad positive unit ray')
                    nn.append(n);ww.append(w);index.append((i,j))
    rays=np.asarray(nn,dtype='<f8');weights=np.asarray(ww,dtype='<f8')
    assert len(weights)==6*order*order
    for i in range(2):
        for j in range(3):
            subtotal=sum(float(weights[k]) for k,cell in enumerate(index) if cell==(i,j))
            assert abs(subtotal-float(CELL_E[i,j]))<5e-13,(i,j,subtotal)
    assert abs(float(np.sum(weights))-.9)<5e-13
    return rays,weights


def read_history(path):
    with open(path,newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows) in (1,3,41),len(rows)
    fields=('u','ell1','ell2','ell3','h1','h2','h3')
    out=[]
    for row in rows:
        point={k:float(row[k]) for k in fields}
        assert all(math.isfinite(z) for z in point.values())
        assert 0<=point['u']<=.08 and all(point['ell'+str(j)]>=0 for j in (1,2,3))
        assert all(point['h'+str(j)]>0 for j in (1,2,3))
        out.append(point)
    assert abs(out[0]['u'])<1e-16 and abs(out[-1]['u']-.08)<1e-16 if len(out)>1 else True
    return out


def bits(x):return str(struct.unpack('<Q',struct.pack('<d',float(x)))[0])


def rust_payload(rays,weights,history,lmax=4):
    assert len(weights)==len(rays)
    lines=[f'{len(rays)} {len(history)} {lmax}']
    for w,n in zip(weights,rays):lines.append(' '.join([bits(w),*(bits(v) for v in n)]))
    for row in history:lines.append(' '.join(bits(row[k]) for k in ('u','ell1','ell2','ell3','h1','h2','h3')))
    return '\n'.join(lines)+'\n'


def harmonics(row,l,m,derivative=False):
    name='da' if derivative else 'a'
    return complex(float(row[f'{name}_{l}_{m}_re']),float(row[f'{name}_{l}_{m}_im']))


def c_and_cprime(row,l):
    a=[harmonics(row,l,m) for m in range(-l,l+1)]
    d=[harmonics(row,l,m,True) for m in range(-l,l+1)]
    return (sum(abs(z)**2 for z in a)/(2*l+1),
            2*sum((z.conjugate()*dz).real for z,dz in zip(a,d))/(2*l+1))


def run_rust(binary,rays,weights,history):
    started=time.perf_counter()
    cp=subprocess.run([str(binary)],input=rust_payload(rays,weights,history),text=True,
                      capture_output=True,timeout=250)
    if cp.returncode:raise RuntimeError(f'Native BASS Rust rejected input: {cp.stderr[:250]}')
    rows=list(csv.DictReader(io.StringIO(cp.stdout)))
    assert len(rows)==len(history)
    stats=[]
    for r,point in zip(rows,history):
        c2,d2=c_and_cprime(r,2);c4,d4=c_and_cprime(r,4)
        e=float(r['E']);p=sum(float(r['P'+str(k)]) for k in (1,2,3))
        trace=abs(e-p)
        continuity=abs(float(r['Eprime'])+sum(point['h'+str(k)] for k in (1,2,3))*e+
                       sum(point['h'+str(k)]*float(r['P'+str(k)]) for k in (1,2,3)))
        assert trace<8e-11 and continuity<8e-11,(trace,continuity)
        stats.append({'u':point['u'],'E':e,'C2':c2,'C2prime':d2,'C4':c4,'C4prime':d4,
                      'a40':float(r['a_4_0_re']),'da40':float(r['da_4_0_re']),
                      'trace_gap':trace,'continuity_gap':continuity})
    return stats,time.perf_counter()-started


def select_empirical_order(out,atol=1e-9):
    ref=out['40']['stats']
    for n in sorted(map(int,out.keys())):
        if n==40:continue
        stats=out[str(n)]['stats']
        if max(max(abs(a['C4prime']-b['C4prime']),abs(a['C4']-b['C4'])) for a,b in zip(stats,ref))<atol:
            return n
    return None


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--binary',required=True)
    ap.add_argument('--history',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--orders',default=','.join(map(str,DEFAULT_ORDERS)))
    ap.add_argument('--empirical-target',type=float,default=1e-9)
    opt=ap.parse_args()
    frozen=frozen_source_identity()
    hist=read_history(opt.history)
    binary=Path(opt.binary).resolve()
    assert binary.is_file()
    orders=[int(z) for z in opt.orders.split(',')]
    assert len(orders)==len(set(orders)) and 40 in orders
    out={}
    for n in orders:
        rays,weights=make_cell_rays(n)
        stats,duration=run_rust(binary,rays,weights,hist)
        out[str(n)]={'rays':len(weights),'source_kind':'original six-cell GL quadrature; positive point masses',
                     'ray_sha256':sha(rays.tobytes()),'mass_sha256':sha(weights.tobytes()),
                     'seconds_process_wall':duration,'stats':stats}
        print(f'order={n:2d} rays={len(weights):5d} C4prime(u=.08)={stats[-1]["C4prime"]:.17g}',flush=True)
    ref=out['40']['stats']
    for n in orders:
        v=out[str(n)]
        v['max_abs_delta_C4prime_vs_GL40']=max(abs(a['C4prime']-b['C4prime']) for a,b in zip(v['stats'],ref))
        v['max_abs_delta_C4_vs_GL40']=max(abs(a['C4']-b['C4']) for a,b in zip(v['stats'],ref))
        v['max_abs_delta_C2prime_vs_GL40']=max(abs(a['C2prime']-b['C2prime']) for a,b in zip(v['stats'],ref))
        v['endpoint_abs_delta_C4prime_vs_GL40']=abs(v['stats'][-1]['C4prime']-ref[-1]['C4prime'])
        print(f'order={n:2d} max |C4prime-GL40|={v["max_abs_delta_C4prime_vs_GL40"]:.3e}',flush=True)
    assert len(hist)==3 or len(hist)==41
    assert abs(ref[-1]['C4prime']-EXPECTED_GL40_FINAL_C4PRIME)<2e-11,(ref[-1],EXPECTED_GL40_FINAL_C4PRIME)
    assert abs(ref[-1]['E']-EXPECTED_GL40_FINAL_E)<2e-10
    outinfo={'schema':'bass.ce1t.angular_cell_gauss_legendre.v1','parent':'PR261','upper_dag':'9/15',
             'frozen_original_source_sha256':frozen,'geometry':'exact inherited GL40 parent history; not a new coupled solution',
             'nodes_are_exact_positive_cell_weights':True,'ray_counts_per_cell':'n^2',
             'empirical_target_abs':opt.empirical_target,'empirical_minimum_uniform_order':select_empirical_order(out,opt.empirical_target),
             'record_count':len(hist),'results':out,'reference':'GL40 numerical not rigorous MPFR',
             'native_ffi':'BASS _rustcore/src/kinetic/comoving.rs Frame::apply/det/phys_dirs via CE1-R',
             'production_ready':False,'merge_ready':False,'formal_sky_error_certificate':False}
    Path(opt.output).parent.mkdir(parents=True,exist_ok=True)
    Path(opt.output).write_text(json.dumps(outinfo,indent=2,allow_nan=False)+'\n')
    print('CE1T_BASS_RUST_POSITIVE_CELL_GL_CONVERGENCE_PASS')
    return outinfo
if __name__=='__main__':main()
