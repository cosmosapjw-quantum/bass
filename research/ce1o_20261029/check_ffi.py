"""Independent x86_64 LP64 C/MPFR versus Python ctypes and rational/mpmath cross-check.

Compile standalone C helper without MPFR dev headers against libmpfr.so.6.
Tests 192-bit RNDD/RNDU, MPFR struct ABI, monotone and arithmetic operations.
Trust model: two callers of the *same* MPFR shared library, not formal verification.
"""
from __future__ import annotations
import argparse
import ctypes as C
from fractions import Fraction
from pathlib import Path
import json
import math
import os
import random
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

from bianchi.nonperturbative.einstein_interval import Interval, _S, BITS

BINARY = ('add', 'sub', 'mul', 'div')
UNARY = ('sqrt', 'exp', 'sinh', 'cosh', 'tanh')


def _run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=10).stdout.strip()


def _binary(a, b, op):
    x, y = Interval.decimal(a), Interval.decimal(b)
    return {'add': lambda: x + y,
            'sub': lambda: x - y,
            'mul': lambda: x * y,
            'div': lambda: x / y}[op]()


def _unary(a, op):
    x=Interval.decimal(a)
    return {'sqrt':x.sqrt, 'exp':x.exp, 'sinh':x.sinh,
            'cosh':x.cosh, 'tanh':x.tanh}[op]()


def _compare(exe, op, a, b=None):
    value=_binary(a,b,op) if op in BINARY else _unary(a,op)
    cmd=[str(exe),op,a] + ([b] if b is not None else [])
    out=_run(cmd)
    match=re.fullmatch(r'lo=(\S+) hi=(\S+)',out)
    assert match, out
    c_lo,c_hi=(float.fromhex(z) for z in match.groups())
    assert (value.lower,value.upper)==(c_lo,c_hi), (op,a,b,value,out)
    return value


def main():
    root=Path(__file__).resolve().parents[2]
    src=root/'research/ce1o_20261029/mpfr_abi_oracle.c'
    assert src.is_file()
    rng=random.Random(0xCE10A8)
    cases={'abi':0,'binary':0,'unary':0,'rational_inclusions':0,
           'mpmath_inclusions':0,'nonfinite_rejections':0}
    with TemporaryDirectory(prefix='bass_ce1o_') as temp:
        exe=Path(temp)/'mpfr_c_oracle'
        compiler=os.environ.get('CC','cc')
        _run([compiler,'-std=c11','-Wall','-Wextra','-Werror','-O2',str(src),
              '-Wl,-l:libmpfr.so.6','-o',str(exe)])
        layout=_run([str(exe),'layout'])
        expected=(32,0,8,16,24)
        got=(C.sizeof(_S),*(getattr(_S,n).offset for n,_ in _S._fields_))
        assert got==expected, (got,expected)
        assert layout.startswith('layout size=32 prec=0 sign=8 exp=16 d=24 mpfr='),layout
        assert BITS==192
        cases['abi']=1
        # Decimal literals are exact-real, not pre-rounded binary64 inputs.
        for i in range(65):
            a=(rng.randrange(-8000,8001))/1024
            b=(rng.randrange(-8000,8001))/2048
            if abs(b)<0.25:b=b+2.5
            sa=f'{a:.16f}';sb=f'{b:.16f}'
            for op in BINARY:
                gotiv=_compare(exe,op,sa,sb)
                A=Fraction(sa);B=Fraction(sb)
                exact={'add':lambda:A+B,'sub':lambda:A-B,'mul':lambda:A*B,
                       'div':lambda:A/B}[op]()
                assert Fraction.from_float(gotiv.lower)<=exact<=Fraction.from_float(gotiv.upper), (op,sa,sb)
                cases['rational_inclusions']+=1
                cases['binary']+=1
        import mpmath as mp
        mp.mp.dps=120
        for i in range(50):
            a= (rng.randrange(1,7001))/4096
            sa=f'{a:.16f}'
            for op in UNARY:
                iv=_compare(exe,op,sa)
                exact=getattr(mp,op)(mp.mpf(sa))
                assert mp.mpf(iv.lower)<=exact<=mp.mpf(iv.upper),(op,sa,iv,exact)
                cases['unary']+=1;cases['mpmath_inclusions']+=1
        for lit in ['nan','NaN','+nan','inf','-inf','Infinity','-Infinity']:
            p=subprocess.run([str(exe),'exp',lit],capture_output=True,text=True,timeout=10)
            assert p.returncode!=0 and 'nonfinite' in p.stderr
            try:Interval.decimal(lit)
            except ValueError: pass
            else: raise AssertionError('nonfinite input accepted '+lit)
            cases['nonfinite_rejections']+=1
    print(json.dumps({'status':'PASS_CROSS_LANGUAGE_CONDITIONAL','mpfr_layout':layout,
                      'python_ctypes':got,'precision_bits':BITS,'checks':cases,
                      'trust_limit':'C and ctypes use same libmpfr.so.6; not formal program verification'},indent=2))
    return cases

if __name__=='__main__':
    main()
