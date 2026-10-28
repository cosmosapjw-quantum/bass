"""Outward dyadic intervals for one finite source-literal stationary system.

No floating-point elementary function participates in the enclosure. Each bound
is an integer divided by 2**bits. This is arithmetic validation, not calibration
of physical inputs. The executable domain of exp is |x| <= 128.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from math import isqrt


def _frac(x):
    if isinstance(x,(float,bool)):raise ValueError('choose explicit exact source semantics')
    return F(x)


def ceil_div(a:int,b:int)->int:
    if b<=0:raise ValueError('positive divisor required')
    return -((-a)//b)


@dataclass(frozen=True)
class I:
    lo:int
    hi:int
    bits:int
    def __post_init__(self):
        if type(self.bits) is not int or not 64<=self.bits<=1024:raise ValueError('bits64..1024')
        if type(self.lo) is not int or type(self.hi) is not int or self.lo>self.hi:raise ValueError('ordered integer bounds required')
    @property
    def S(self):return 1<<self.bits
    @classmethod
    def point(cls,x,bits):
        q=_frac(x);s=1<<bits
        return cls(q.numerator*s//q.denominator,ceil_div(q.numerator*s,q.denominator),bits)
    def pair(self):return F(self.lo,self.S),F(self.hi,self.S)
    def pack(self):return {'lo':str(self.lo),'hi':str(self.hi),'bits':self.bits}
    def _coerce(self,x):
        if isinstance(x,I):
            if self.bits!=x.bits:raise ValueError('mixed precisions')
            return x
        return I.point(x,self.bits)
    def __add__(self,x):
        x=self._coerce(x);return I(self.lo+x.lo,self.hi+x.hi,self.bits)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo,self.bits)
    def __sub__(self,x):return self+-self._coerce(x)
    def __rsub__(self,x):return self._coerce(x)+-self
    def __mul__(self,x):
        x=self._coerce(x);p=[a*b for a in (self.lo,self.hi) for b in (x.lo,x.hi)]
        return I(min(p)//self.S,ceil_div(max(p),self.S),self.bits)
    __rmul__=__mul__
    def reciprocal(self):
        if self.lo<=0<=self.hi:raise ValueError('division by zero-containing interval')
        if self.hi<0:return -(-self).reciprocal()
        return I(self.S*self.S//self.hi,ceil_div(self.S*self.S,self.lo),self.bits)
    def __truediv__(self,x):return self*self._coerce(x).reciprocal()
    def __rtruediv__(self,x):return self._coerce(x)*self.reciprocal()
    def __pow__(self,n):
        if type(n) is not int or n<0:raise ValueError('nonnegative integer exponent')
        r=I.point(1,self.bits);a=self
        while n:
            if n&1:r=r*a
            a=a*a;n//=2
        return r
    def abs(self):
        if self.lo>=0:return self
        if self.hi<=0:return -self
        return I(0,max(-self.lo,self.hi),self.bits)
    def sqrt(self):
        if self.lo<0:raise ValueError('negative square-root interval')
        low=isqrt(self.lo*self.S);high=isqrt(self.hi*self.S)
        if high*high<self.hi*self.S:high+=1
        return I(low,high,self.bits)
    def exp(self):
        low=_exp_point(F(self.lo,self.S),self.bits)
        high=low if self.lo==self.hi else _exp_point(F(self.hi,self.S),self.bits)
        return I(low.lo,high.hi,self.bits)


def _exp_point(x:F,bits:int)->I:
    if abs(x)>128:raise ValueError('exp source domain |x|<=128')
    if x==0:return I.point(1,bits)
    if x<0:return _exp_point(-x,bits).reciprocal()
    m=0;y=x
    while y>F(1,8):y/=2;m+=1
    v=I.point(y,bits);term=I.point(1,bits);total=term
    for n in range(512):
        nxt=term*v/(n+1)
        tail=nxt/(1-v/(n+2))
        if tail.hi<=4:
            out=I(total.lo,total.hi+tail.hi,bits)
            for _ in range(m):out=out*out
            return out
        total=total+nxt;term=nxt
    raise ArithmeticError('Taylor term limit exceeded; no unqualified return')


def exp_bounds(x,bits):return I.point(x,bits).exp().pair()
def sqrt_bounds(x,bits):return I.point(x,bits).sqrt().pair()


def solve_intervals(M,b):
    if len(M)!=2 or any(len(row)!=2 for row in M) or len(b)!=2:raise ValueError('2x2 only')
    a,minusbeta=M[0];minuschi,d=M[1]
    if a.lo<=0 or d.lo<=0 or minusbeta.hi>0 or minuschi.hi>0 or min(x.lo for x in b)<0:raise ValueError('positive inverse domain required')
    beta=-minusbeta;chi=-minuschi;det=a*d-beta*chi
    if det.lo<=0:raise ValueError('strict positive determinant not certified')
    return [(d*b[0]+beta*b[1])/det,(chi*b[0]+a*b[1])/det],det


def solve_2x2(M,b,bits):
    q,_=solve_intervals([[I.point(x,bits) for x in row] for row in M],[I.point(x,bits) for x in b])
    return [x.pair() for x in q]
