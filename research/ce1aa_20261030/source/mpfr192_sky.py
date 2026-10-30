#!/usr/bin/env python3
"""CE1-AA: 192-bit correctly outward-rounded MPFR l=4 source evaluation.

Exact inputs: stored float64 GL nodes/masses and *stored float64* log-scale state.
No claim of rigor for the numerical DOP853 spacetime path itself, or continuum
source/trajectory, or of a formal proof of the MPFR implementation.
"""
from __future__ import annotations
import ctypes as C
import math, csv, json, sys, hashlib
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cellwise_gl_rust import make_cell_rays, frozen_source_identity
SOURCE_SHA='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
INPUT_SHA={6:'6eff8cd9f31d027bbee55720332302b6fbad71b3639b5809aab6b9ce6f53e489',8:'1398980ec71662494273e05eb4bd52a78f6e6c7f208702638da6c739698f7502'}
RAY_SHA={6:('6f6e5d0797404521abd51cb8394a8b2beca3e96b392924b9ad30b2093098d957','56cb2c5baabdcf10355cc7ddf2f1cf41ad8a131d890e285320e39bab52758199'),8:('90e29d100d35dc7ac31f9d75f7d6d4c2d423d90ad487ec0922246bc8f39891cb','2c0b9ca7d1845458639217fae0a86b3339c32f57f9f71dd6c649c3408d319a79')}
PREC=192; RD=3; RU=2; RN=0

class MP(C.Structure):
    _fields_=[('_prec',C.c_long),('_sign',C.c_int),('_exp',C.c_long),('_data',C.POINTER(C.c_ulong))]
P=C.POINTER(MP); lib=C.CDLL('libmpfr.so.6')
SPECS={
 'init2':([P,C.c_long],None),'clear':([P],None),
 'set_d':([P,C.c_double,C.c_int],C.c_int),'get_d':([P,C.c_int],C.c_double),
 'const_pi':([P,C.c_int],C.c_int),'cmp':([P,P],C.c_int),'number_p':([P],C.c_int),
 'add':([P,P,P,C.c_int],C.c_int),'sub':([P,P,P,C.c_int],C.c_int),
 'mul':([P,P,P,C.c_int],C.c_int),'div':([P,P,P,C.c_int],C.c_int),
 'neg':([P,P,C.c_int],C.c_int),'sqrt':([P,P,C.c_int],C.c_int),
 'exp':([P,P,C.c_int],C.c_int),
}
for name,(args,res) in SPECS.items():
 fn=getattr(lib,'mpfr_'+name);fn.argtypes=args;fn.restype=res

lib.mpfr_get_str.argtypes=[C.c_void_p,C.POINTER(C.c_long),C.c_int,C.c_size_t,P,C.c_int]
lib.mpfr_get_str.restype=C.c_void_p
lib.mpfr_free_str.argtypes=[C.c_void_p]
lib.mpfr_free_str.restype=None

class M:
    __slots__=('v','initialized')
    def __init__(self):
        self.v=MP();self.initialized=True;lib.mpfr_init2(C.byref(self.v),PREC)
    def __del__(self):
        if getattr(self,'initialized',False):lib.mpfr_clear(C.byref(self.v));self.initialized=False
    def ptr(self):return C.byref(self.v)
    def f(self,rnd=RN):return lib.mpfr_get_d(self.ptr(),rnd)
    def hex192(self):
        exponent=C.c_long()
        p=lib.mpfr_get_str(None,C.byref(exponent),16,0,self.ptr(),RN)
        if not p:raise MemoryError('mpfr_get_str')
        try:mantissa=C.string_at(p).decode('ascii')
        finally:lib.mpfr_free_str(p)
        return {'mantissa_base16':mantissa,'base16_exponent':exponent.value}


def d(val):
    if not math.isfinite(float(val)):raise ArithmeticError('nonfinite input')
    a=M();lib.mpfr_set_d(a.ptr(),float(val),RN)
    if not lib.mpfr_number_p(a.ptr()):raise ArithmeticError('nonfinite MPFR input')
    return a

def op(name,a,b=None,rnd=RN):
    c=M();fn=getattr(lib,'mpfr_'+name)
    if b is None:fn(c.ptr(),a.ptr(),rnd)
    else:fn(c.ptr(),a.ptr(),b.ptr(),rnd)
    if not lib.mpfr_number_p(c.ptr()):raise ArithmeticError('nonfinite MPFR result')
    return c

def cmp(a,b):return lib.mpfr_cmp(a.ptr(),b.ptr())

class IV:
    __slots__=('lo','hi')
    def __init__(self,lo,hi):self.lo,self.hi=lo,hi
    @classmethod
    def val(cls,x):return cls(d(x),d(x))
    def pair(self):return [self.lo.f(RD),self.hi.f(RU)]
    def endpoints_mpfr192(self):return [self.lo.hex192(),self.hi.hex192()]
    def __add__(self,r):
        if not isinstance(r,IV):r=IV.val(r)
        return IV(op('add',self.lo,r.lo,RD),op('add',self.hi,r.hi,RU))
    __radd__=__add__
    def __neg__(self):return IV(op('neg',self.hi,rnd=RD),op('neg',self.lo,rnd=RU))
    def __sub__(self,r):return self+-r if isinstance(r,IV) else self+(-float(r))
    def __rsub__(self,r):return IV.val(r)+(-self)
    def __mul__(self,r):
        if not isinstance(r,IV):r=IV.val(r)
        if cmp(self.lo,d(0))>=0 and cmp(r.lo,d(0))>=0:
            return IV(op('mul',self.lo,r.lo,RD),op('mul',self.hi,r.hi,RU))
        lo=[op('mul',a,b,RD) for a in (self.lo,self.hi) for b in (r.lo,r.hi)]
        hi=[op('mul',a,b,RU) for a in (self.lo,self.hi) for b in (r.lo,r.hi)]
        return IV(min(lo,key=lambda x:MPKey(x)),max(hi,key=lambda x:MPKey(x)))
    __rmul__=__mul__
    def __truediv__(self,r):
        if not isinstance(r,IV):r=IV.val(r)
        if cmp(r.lo,d(0))<=0:raise ArithmeticError('division by uncertain or negative interval')
        inv=IV(op('div',d(1),r.hi,RD),op('div',d(1),r.lo,RU))
        return self*inv
    def __rtruediv__(self,r):return IV.val(r)/self
    def exp(self):return IV(op('exp',self.lo,rnd=RD),op('exp',self.hi,rnd=RU))
    def sqrt(self):
        if cmp(self.lo,d(0))<0:raise ArithmeticError('negative square root')
        return IV(op('sqrt',self.lo,rnd=RD),op('sqrt',self.hi,rnd=RU))
    def __repr__(self):return 'IV('+repr(self.pair())+')'

class MPKey:
    __slots__=('val',)
    def __init__(self,x):self.val=x
    def __lt__(self,o):return cmp(self.val,o.val)<0

def pi_iv():
    lo,hi=M(),M();lib.mpfr_const_pi(lo.ptr(),RD);lib.mpfr_const_pi(hi.ptr(),RU)
    return IV(lo,hi)

def hashbytes(b):return hashlib.sha256(b).hexdigest()

def rays(order):
    assert frozen_source_identity()==SOURCE_SHA
    nn,ww=make_cell_rays(order)
    assert (hashbytes(nn.tobytes()),hashbytes(ww.tobytes()))==RAY_SHA[order]
    # Each stored binary64 n component is interpreted EXACTLY as a dyadic real.
    return [(IV.val(float(w)),tuple(IV.val(float(x))*IV.val(float(x)) for x in row)) for row,w in zip(nn,ww)]

def sky_at_state(ell,prepared,consts):
    pi,cc40,cc42,cc44=consts
    e=[IV.val(float(x)) for x in ell]
    b=[(-2*x).exp() for x in e]
    vol=(-e[0]-e[1]-e[2]).exp()
    s0=IV.val(0);sz=IV.val(0);szz=IV.val(0);sa=IV.val(0);sb=IV.val(0);sc=IV.val(0)
    for w,n2 in prepared:
        x=b[0]*n2[0];y=b[1]*n2[1];z=b[2]*n2[2]
        r2=x+y+z;r=r2.sqrt();r3=r*r2
        wr=w*r;wr_inv=w/r;wr_inv3=w/r3
        s0=s0+wr;sz=sz+wr_inv*z;szz=szz+wr_inv3*z*z
        xy=x-y
        sa=sa+wr_inv*xy
        sb=sb+wr_inv3*xy*z
        sc=sc+wr_inv3*(x*x-6*x*y+y*y)
    E=vol*s0
    a40=cc40*vol*(35*szz-30*sz+3*s0)
    a42=cc42*vol*(7*sb-sa)
    a44=cc44*vol*sc
    alpha=[4*pi*a/E for a in (a40,a42,a44)]
    return {'E':E,'a40':a40,'a42':a42,'a44':a44,'alpha':alpha}

def constants():
    pi=pi_iv()
    cc40=3/(16*pi.sqrt())
    cc42=IV.val(3)/8*(IV.val(5)/(2*pi)).sqrt()
    cc44=IV.val(3)/16*(IV.val(35)/(2*pi)).sqrt()
    return pi,cc40,cc42,cc44

def init_row(row,prep,consts):
    ell=[float(row['ell'+str(k)]) for k in (1,2,3)]
    z=sky_at_state(ell,prep,consts)
    bounds={k:z[k].pair() for k in ['E','a40','a42','a44']}
    bounds['alpha']=[x.pair() for x in z['alpha']]
    bounds['raw_mpfr192']={k:z[k].endpoints_mpfr192() for k in ['E','a40','a42','a44']}
    bounds['alpha_mpfr192']=[x.endpoints_mpfr192() for x in z['alpha']]
    bounds['raw_float']={k:float(row[k]) for k in ['E','a40','a42','a44']}
    bounds['raw_float_outside_interval']={k:max(0,bounds[k][0]-float(row[k]),float(row[k])-bounds[k][1]) for k in ['E','a40','a42','a44']}
    bounds['u']=float(row['u']);bounds['ell']=ell
    return z,bounds

def run_one(order=8,outdir=None,limit=None):
    pp=Path(__file__).resolve().parents[1]/'input'/f'GL{order}_DOP853_coupled_41epochs.csv'
    assert hashbytes(pp.read_bytes())==INPUT_SHA[order]
    with pp.open() as f:rows=list(csv.DictReader(f))
    assert len(rows)==41
    assert all(all(0<=float(row[f'ell{k}'])<=.08 for k in (1,2,3)) for row in rows)
    assert all(abs(float(row['u'])-.002*i)<1e-15 for i,row in enumerate(rows))
    prepared=rays(order);cs=constants()
    import time
    t=time.monotonic();rez=[];raw=[]
    for row in rows[:limit]:
        iv,entry=init_row(row,prepared,cs);rez.append(iv);raw.append(entry)
    elapsed=time.monotonic()-t
    if outdir:
        target=Path(outdir);target.mkdir(parents=True,exist_ok=True)
        (target/f'GL{order}_mpfr192_source_{len(raw)}.json').write_text(json.dumps({'schema':'bass.ce1aa.mpfr192.frozen_geometry.v1','source_sha256':SOURCE_SHA,'history_sha256':INPUT_SHA[order],'order':order,'precision_bits':PREC,'states':raw,'elapsed_seconds':elapsed,'identity':RAY_SHA[order],'claim_scope':'Exact real original stored GL source evaluated at exactly stored binary64 DOP853 ell states, not certified DOP IVP'},indent=2)+'\n')
    print('MPFR_SRC',order,len(raw),'elapsed',round(elapsed,3),'E0',raw[0]['E'],'a40_0',raw[0]['a40'],flush=True)
    return rez,raw,elapsed

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--order',type=int,default=8);p.add_argument('--limit',type=int,default=1);p.add_argument('--outdir',default=str(ROOT/'data'));a=p.parse_args()
    run_one(a.order,a.outdir,a.limit)
