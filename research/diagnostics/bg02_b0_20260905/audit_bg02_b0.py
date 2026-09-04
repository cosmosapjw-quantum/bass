#!/usr/bin/env python3
"""Read-only BG-02 coordinate oracle; never a native xTensor admission.

All coordinates have length units and tau=c*t. K=+1/2*d_tau(h).
R[a,b,c,d]=g(e_d,([nabla_a,nabla_b]-nabla_[a,b])e_c).
Run with SymPy 1.14.0. This file modifies no repository source.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import re
import sys
import sympy as s

PINS = {
    'wolfram/BASS/Kernel/Geometry/Abstract1Plus3.wl': '4bfacaacd52af90a835665bbfe1c264983fda79f',
    'wolfram/BASS/Kernel/Geometry/ONFConnectionCurvature.wl': '820d09dd2bb0c5364b0fe3c0d0bdb3bc7841bb7c',
    'wolfram/BASS/Kernel/Geometry/XCobaCurvatureWitnesses.wl': 'e556bd4fbde147e7bcf5ad276ad92b571da04c14',
    'wolfram/BASS/Kernel/Background/EinsteinProjection.wl': 'c7d40bd046b69fb9d1715538cfc7d570efc5e791',
}
HEAD = 'ac3186939ffe1e37ea1af15faa910df1e320277d'
TREE = 'bb5f382e58d48d6ac889a12576c4555dee8cc763'

class Geometry:
    def __init__(self, metric: s.Matrix, coordinates: tuple):
        if metric.shape != (len(coordinates), len(coordinates)):
            raise ValueError('Metric shape mismatch')
        self.g, self.q, self.n = metric, coordinates, len(coordinates)
        self.inv = metric.inv()

    @lru_cache(None)
    def gamma(self, d, a, b):
        return s.simplify(sum(self.inv[d,j] * (
            s.diff(self.g[j,b],self.q[a]) + s.diff(self.g[j,a],self.q[b])
            - s.diff(self.g[a,b],self.q[j]))/2 for j in range(self.n)))

    @lru_cache(None)
    def rup(self, a, b, c, d):
        return s.simplify(s.diff(self.gamma(d,b,c),self.q[a])
            - s.diff(self.gamma(d,a,c),self.q[b]) + sum(
            self.gamma(d,a,k)*self.gamma(k,b,c)
            - self.gamma(d,b,k)*self.gamma(k,a,c) for k in range(self.n)))

    @lru_cache(None)
    def r(self, a, b, c, d):
        return s.simplify(sum(self.g[d,j]*self.rup(a,b,c,j) for j in range(self.n)))

    def ricci(self):
        return s.Matrix(self.n,self.n,lambda c,b:
            s.simplify(sum(self.rup(a,b,c,a) for a in range(self.n))))

    def scalar(self):
        ric = self.ricci()
        return s.simplify(sum(self.inv[a,b]*ric[a,b]
            for a in range(self.n) for b in range(self.n)))


def source_check(root):
    records, texts = {}, {}
    for name, expected in PINS.items():
        data = (root/name).read_bytes()
        actual = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if actual != expected:
            raise ValueError(f'SOURCE_BLOB_MISMATCH: {name}: {actual} != {expected}')
        records[name] = {'git_blob':actual,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
        texts[name] = data.decode('utf-8')
    w2 = texts[next(iter(PINS))]
    def terms(formula):
        block = w2.split('makeEquation["'+formula+'"',1)[1].split('makeEquation[',1)[0]
        return {name:s.Rational(value) for name,value in re.findall(
            r'equationTerm\["([^"\n]+)",\s*(-?\d+(?:/\d+)?)\]',block)}
    gauss, codazzi = terms('W2-CURV-001'), terms('W2-CURV-002')
    oracle = texts['wolfram/BASS/Kernel/Background/EinsteinProjection.wl']
    if '"MomentumProjection"->divKv-gradKv-kgv qv' not in oracle:
        raise ValueError('Unexpected momentum expression')
    adapter = texts['wolfram/BASS/Kernel/Geometry/XCobaCurvatureWitnesses.wl']
    if '"xact_to_bass_sign_adapter" -> -1' not in adapter:
        raise ValueError('Unexpected xAct-to-BASS adapter')
    return records, gauss, codazzi


def audit(root):
    source, gauss, codazzi = source_check(root)
    tau,x,y,z = s.symbols('tau x y z', real=True)
    H,h1,h2,h3,a = s.symbols('H H1 H2 H3 a_B0', real=True)
    ell = s.symbols('ell', positive=True)
    kg,qx = s.symbols('kappa_G q_x', real=True)
    coords = (tau,x,y,z)
    f = 1+tau*x/ell**2
    cases = {
        'flat_flrw':s.diag(-1,*([s.exp(2*H*tau)]*3)),
        'bianchi_v':s.diag(-1,s.exp(2*h1*tau),s.exp(2*h2*tau-2*a*x),s.exp(2*h3*tau-2*a*x)),
        'inhomogeneous_synchronous':s.diag(-1,1,f**2,f**2),
    }
    checks, measurements, mismatch = {}, {}, {}
    def zero(name, value):
        vals = list(value) if isinstance(value,(list,tuple,s.MatrixBase)) else [value]
        residuals = [s.simplify(v) for v in vals]
        checks[name] = {'pass':all(v==0 for v in residuals),
            'component_count':len(residuals),
            'nonzero_residuals':[str(v) for v in residuals if v!=0]}
    for label,g in cases.items():
        geo = Geometry(g,coords)
        spatial = Geometry(g[1:4,1:4],coords[1:])
        K = s.diff(spatial.g,tau)/2
        kt = s.simplify(s.trace(spatial.inv*K))
        @lru_cache(None)
        def dk(i,j,k):
            return s.simplify(s.diff(K[j,k],coords[i+1])-sum(
                spatial.gamma(m,i,j)*K[m,k]+spatial.gamma(m,i,k)*K[j,m] for m in range(3)))
        div = s.Matrix([s.simplify(sum(spatial.inv[j,k]*dk(k,i,j)
            for j in range(3) for k in range(3))) for i in range(3)])
        grad = s.Matrix([s.diff(kt,c) for c in coords[1:]])
        ric = geo.ricci(); r4 = geo.scalar(); r3 = spatial.scalar()
        einstein = ric-g*r4/2
        zero(label+'/first_fourth_Ricci_contraction',[ric[c,b]-sum(geo.inv[i,j]*geo.r(i,b,c,j) for i in range(4) for j in range(4)) for c,b in itertools.product(range(4),repeat=2)])
        zero(label+'/xAct_Ricci_same_physical_tensor',[ric[c,b]+sum(geo.inv[i,j]*geo.r(c,i,b,j) for i in range(4) for j in range(4)) for c,b in itertools.product(range(4),repeat=2)])
        quad = s.simplify(s.trace((spatial.inv*K)**2))
        zero(label+'/K_from_covariant_normal',
            [K[i,j]-geo.gamma(0,i+1,j+1) for i,j in itertools.product(range(3),repeat=2)])
        gauss_res, codazzi_res, raw_gauss, raw_codazzi = [], [], [], []
        for i,j,k,l in itertools.product(range(3),repeat=4):
            direct=geo.r(i+1,j+1,k+1,l+1)
            target=spatial.r(i,j,k,l)+K[j,k]*K[i,l]-K[i,k]*K[j,l]
            gauss_res.append(direct-target)
            # W2 is consistent as a RAW_XACT view, not as BASS derivative-first.
            raw_rhs=-gauss['R3_abcd']*spatial.r(i,j,k,l)+gauss['K_ac K_bd']*K[i,k]*K[j,l]+gauss['K_ad K_bc']*K[i,l]*K[j,k]
            raw_gauss.append(-direct-raw_rhs)
        for i,j,k in itertools.product(range(3),repeat=3):
            direct=geo.r(i+1,j+1,k+1,0)
            rhs=codazzi['D_a K_bc']*dk(i,j,k)+codazzi['D_b K_ac']*dk(j,i,k)
            codazzi_res.append(direct+dk(i,j,k)-dk(j,i,k))
            raw_codazzi.append(-direct-rhs)
        zero(label+'/BASS_Gauss',gauss_res)
        zero(label+'/BASS_Codazzi',codazzi_res)
        zero(label+'/RAW_XACT_W2_Gauss_with_R3_adapter',raw_gauss)
        zero(label+'/RAW_XACT_W2_Codazzi',raw_codazzi)
        zero(label+'/mixed_Ricci',ric[1:4,0]-(div-grad))
        zero(label+'/Hamiltonian',einstein[0,0]-(r3+kt**2-quad)/2)
        trace=s.simplify(sum(spatial.inv[i,j]*einstein[i+1,j+1] for i in range(3) for j in range(3))/3)
        zero(label+'/spatial_trace',trace-(-r3/6-2*s.diff(kt,tau)/3-quad/2-kt**2/6))
        # Matter part of -h E n for T_x0=-q_x is -kappa_G q_x.
        coordinate_m=-ric[1,0]-kg*qx
        published_m=div[0]-grad[0]-kg*qx
        corrected_m=-div[0]+grad[0]-kg*qx
        zero(label+'/corrected_momentum_with_matter',coordinate_m-corrected_m)
        measurements[label] = {'R_xyyx':str(geo.r(1,2,2,1)),
            'R_xyy_n':str(geo.r(1,2,2,0)),
            'divK_minus_gradK_x':str(s.simplify(div[0]-grad[0])),
            'Ricci_xn':str(ric[1,0]),'R3':str(r3),
            'coordinate_momentum_x':str(s.simplify(coordinate_m)),
            'published_momentum_x':str(s.simplify(published_m))}
        if label=='flat_flrw':
            published_gauss=gauss['R3_abcd']*spatial.r(0,1,1,0)+gauss['K_ac K_bd']*K[0,1]*K[1,0]+gauss['K_ad K_bc']*K[0,0]*K[1,1]
            mismatch[label+'/W2_Gauss_as_BASS']=s.simplify(geo.r(1,2,2,1)-published_gauss)
        else:
            rhs=codazzi['D_a K_bc']*dk(0,1,1)+codazzi['D_b K_ac']*dk(1,0,1)
            mismatch[label+'/W2_Codazzi_as_BASS']=s.simplify(geo.r(1,2,2,0)-rhs)
            mismatch[label+'/BG02_momentum']=s.simplify(coordinate_m-published_m)
    sentinel={tau:0,x:0,H:1/ell,h1:1/ell,h2:0,h3:0,a:1/ell}
    mismatch_result={k:{'residual':str(v),'sentinel':str(s.simplify(v.subs(sentinel))),
        'detected':s.simplify(v.subs(sentinel))!=0} for k,v in mismatch.items()}
    passed=all(v['pass'] for v in checks.values()) and all(v['detected'] for v in mismatch_result.values())
    return {'schema_version':'1.0.0','stage_id':'BG02_B0_COORDINATE_CONVENTION_AUDIT',
        'source_head':HEAD,'source_tree':TREE,'source_subset':source,
        'execution_scope':'EXACT_BLOB_SUBSET_PLUS_INDEPENDENT_SYMPY_ORACLE_NOT_FULL_CHECKOUT',
        'python':platform.python_version(),'sympy':s.__version__,
        'checks':checks,'checks_passed':sum(v['pass'] for v in checks.values()),
        'checks_total':len(checks),'measurements':measurements,'authority_mismatches':mismatch_result,
        'diagnostic_status':'PASS_REPRODUCED_CONVENTION_CONFLICT' if passed else 'FAIL_DIAGNOSTIC',
        'authority_gate':'FAIL_W2_W3_BG02_CONVENTION_COMPOSITION',
        'native_xtensor_executed':False,'production_source_modified':False,
        'constraint_propagation_verified':False,'provider_admission':False,
        'notes':['Scalar/component algebra is not native tensor evidence.',
            'Raw xAct and BASS all-lower Riemann views differ; their physical Ricci tensors agree.',
            'Generic class-B divergence carrier remains valid; Einstein momentum uses its negative.',
            'No new native 13-test suite replay is claimed.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists():
        parser.error('Refusing to overwrite an existing receipt')
    try:
        result=audit(args.source_root.resolve())
    except Exception as error:
        result={'diagnostic_status':'BLOCKED_DIAGNOSTIC',
            'error_type':type(error).__name__,'error':str(error),'native_xtensor_executed':False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    data=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
    tmp=args.output.with_name(args.output.name+'.tmp.'+str(os.getpid()))
    with tmp.open('x',encoding='utf-8') as stream:
        stream.write(data);stream.flush();os.fsync(stream.fileno())
    if json.loads(tmp.read_text())!=result:
        raise RuntimeError('Receipt round-trip mismatch')
    # Hard-link publication is atomic and refuses an existing destination.
    os.link(tmp,args.output);tmp.unlink()
    print(data,end='')
    return 0 if result['diagnostic_status']=='PASS_REPRODUCED_CONVENTION_CONFLICT' else 2

if __name__=='__main__':
    sys.exit(main())
