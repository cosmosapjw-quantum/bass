#!/usr/bin/env python3
"""Real MPFR-192 directed outward E/P at five saved Einstein-Vlasov knots.

Proof scope: includes real-number evaluation of *stored exact binary64* rays,
weights and binary64 (ell,h) states. Does not enclose numerical state/IVP error.
"""
from __future__ import annotations
import ctypes as C, csv, sys, json, math, argparse
from pathlib import Path
import numpy as np

class MP(C.Structure):
    _fields_=[('_prec',C.c_long),('_sign',C.c_int),('_exp',C.c_long),('_data',C.POINTER(C.c_ulong))]
LP=C.CDLL('libmpfr.so.6')
ptr=C.POINTER(MP)
for name,types in {
 'mpfr_init2':[ptr,C.c_long], 'mpfr_clear':[ptr],
 'mpfr_set_d':[ptr,C.c_double,C.c_int], 'mpfr_get_d':[ptr,C.c_int],
 'mpfr_add':[ptr,ptr,ptr,C.c_int], 'mpfr_sub':[ptr,ptr,ptr,C.c_int],
 'mpfr_mul':[ptr,ptr,ptr,C.c_int], 'mpfr_div':[ptr,ptr,ptr,C.c_int],
 'mpfr_sqrt':[ptr,ptr,C.c_int], 'mpfr_exp':[ptr,ptr,C.c_int],
}.items():
 f=getattr(LP,name);f.argtypes=types;f.restype=C.c_double if name=='mpfr_get_d' else C.c_int if name not in ('mpfr_init2','mpfr_clear') else None
LO,HI=3,2
PREC=192
class M:
    def __init__(self):
        self.z=MP();LP.mpfr_init2(C.byref(self.z),PREC)
    def __del__(self):
        try:LP.mpfr_clear(C.byref(self.z))
        except Exception:pass
    def set_d(self,x,rnd):LP.mpfr_set_d(C.byref(self.z),float(x),rnd);return self
    def get_d(self,rnd):return LP.mpfr_get_d(C.byref(self.z),rnd)

def mpcalc(name,x,y=None,rnd=0):
    z=M()
    if y is None:getattr(LP,'mpfr_'+name)(C.byref(z.z),C.byref(x.z),rnd)
    else:getattr(LP,'mpfr_'+name)(C.byref(z.z),C.byref(x.z),C.byref(y.z),rnd)
    return z

class IV:
    def __init__(self,l:M,u:M):self.l=l;self.u=u
    @staticmethod
    def exact(v):return IV(M().set_d(v,0),M().set_d(v,0))
    def __add__(self,r):
        if not isinstance(r,IV):r=IV.exact(r)
        return IV(mpcalc('add',self.l,r.l,LO),mpcalc('add',self.u,r.u,HI))
    __radd__=__add__
    def __sub__(self,r):
        if not isinstance(r,IV):r=IV.exact(r)
        return IV(mpcalc('sub',self.l,r.u,LO),mpcalc('sub',self.u,r.l,HI))
    def __mul__(self,r):
        if not isinstance(r,IV):r=IV.exact(r)
        # all operands in this source calculation are positive except raw negative
        # exponent arguments. Multiplication only used after exp, positive.
        if min(self.l.get_d(LO),r.l.get_d(LO))<0:raise ArithmeticError('nonnegative multiply only')
        return IV(mpcalc('mul',self.l,r.l,LO),mpcalc('mul',self.u,r.u,HI))
    __rmul__=__mul__
    def __truediv__(self,r):
        if not isinstance(r,IV):r=IV.exact(r)
        if r.l.get_d(LO)<=0:raise ArithmeticError('strictly positive denominator needed')
        return IV(mpcalc('div',self.l,r.u,LO),mpcalc('div',self.u,r.l,HI))
    def exp(self):return IV(mpcalc('exp',self.l,None,LO),mpcalc('exp',self.u,None,HI))
    def sqrt(self):
        if self.l.get_d(LO)<0:raise ArithmeticError('nonnegative sqrt input needed')
        return IV(mpcalc('sqrt',self.l,None,LO),mpcalc('sqrt',self.u,None,HI))
    def pair(self):return [self.l.get_d(LO),self.u.get_d(HI)]


def mpfr_source(rays,masses,ell):
    ell=[IV.exact(z) for z in ell]
    # exact binary64 input transported through outward MPFR192 operations
    b=[(IV.exact(0)-2*e).exp() for e in ell]
    vol=(IV.exact(0)-ell[0]-ell[1]-ell[2]).exp()
    en=IV.exact(0);pp=[IV.exact(0) for _ in range(3)]
    for nn,w0 in zip(rays,masses):
        n2=[IV.exact(float(z))*IV.exact(float(z)) for z in nn]
        r2=b[0]*n2[0]+b[1]*n2[1]+b[2]*n2[2]
        r=r2.sqrt();ww=IV.exact(float(w0))
        en=en+ww*r
        for i in range(3):pp[i]=pp[i]+ww*b[i]*n2[i]/r
    e=(vol*en).pair();p=[(vol*x).pair() for x in pp]
    return {'E_interval':e,'P_intervals':p,'precision_bits':PREC,
            'input':'exact_stored_binary64_GL_ray_mass_and_binary64_ell',
            'scope':'directed MPFR source value; not actual continuum, geometry IVP, or float BLAS error'}

def main(out):
    root=None
    for r in Path(__file__).resolve().parents:
        if (r/'research/ce1t_20261030/cellwise_gl_rust.py').exists():root=r;break
    assert root is not None
    sys.path.insert(0,str(root/'research'/'ce1t_20261030'))
    from cellwise_gl_rust import make_cell_rays,frozen_source_identity
    frozen_source_identity()
    data={}
    for n in [6,8]:
        rays,masses=make_cell_rays(n)
        with (root/f'research/ce1u_20261030/data/GL{n}_coupled_41epochs.csv').open() as f:
            rows=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(f)]
        result=[]
        for k in (0,10,20,30,40):
            row=rows[k];ell=[row[f'ell{i}'] for i in (1,2,3)]
            z=mpfr_source(rays,masses,ell)
            z['u']=row['u'];z['index']=k
            z['E_binary64']=row['E'];z['P_binary64']=[row[f'P{i}'] for i in (1,2,3)]
            z['max_binary64_gap_from_mpfr_interval']=max([max(z['E_interval'][0]-row['E'],row['E']-z['E_interval'][1],0)]+[max(v[0]-row[f'P{i}'],row[f'P{i}']-v[1],0) for i,v in enumerate(z['P_intervals'],1)])
            result.append(z)
        data[f'GL{n}']=result
        print('MPFR192 GL',n,'source knots',len(result),'max float offset',max(t['max_binary64_gap_from_mpfr_interval'] for t in result),flush=True)
    Path(out).write_text(json.dumps({'schema':'bass.ce1u.mpfr192_source_knots.v1','source_identity':frozen_source_identity(),'results':data},indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();main(args.output)
