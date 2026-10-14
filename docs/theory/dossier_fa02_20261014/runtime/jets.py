"""Degree-two multivariate Taylor jets, coefficients in the monomial convention.
The first axis stores 1, chi, eta, zeta, chi^2, chi eta, chi zeta,
eta^2, eta zeta, zeta^2. No finite differencing is used in these jets.
"""
from __future__ import annotations
import numpy as np
TERMS=[(0,0,0),(1,0,0),(0,1,0),(0,0,1),(2,0,0),(1,1,0),(1,0,1),(0,2,0),(0,1,1),(0,0,2)]
INDEX={a:i for i,a in enumerate(TERMS)}
PAIRS=[[(i,j) for i,a in enumerate(TERMS) for j,b in enumerate(TERMS)
        if tuple(x+y for x,y in zip(a,b))==t] for t in TERMS]
class Jet:
    __array_priority__=1000
    def __init__(self,c):self.c=np.asarray(c,dtype=complex)
    @staticmethod
    def const(x):
        x=np.asarray(x,dtype=complex);out=np.zeros((10,)+x.shape,complex);out[0]=x;return Jet(out)
    @staticmethod
    def var(x,k):
        out=Jet.const(x);out.c[k+1]=1;return out
    @staticmethod
    def cast(x):return x if isinstance(x,Jet) else Jet.const(x)
    def __add__(self,b):
        b=Jet.cast(b);return Jet(np.stack([self.c[i]+b.c[i] for i in range(10)]))
    __radd__=__add__
    def __neg__(self):return Jet(-self.c)
    def __sub__(self,b):return self+-Jet.cast(b)
    def __rsub__(self,b):return Jet.cast(b)+-self
    def __mul__(self,b):
        b=Jet.cast(b);return Jet(np.stack([sum((self.c[i]*b.c[j] for i,j in pairs)) for pairs in PAIRS]))
    __rmul__=__mul__
    def __matmul__(self,b):
        b=Jet.cast(b);return Jet(np.stack([sum((self.c[i]@b.c[j] for i,j in pairs)) for pairs in PAIRS]))
    def __rmatmul__(self,b):return Jet.cast(b)@self
    def __truediv__(self,b):return self*Jet.cast(b).inv()
    def __rtruediv__(self,b):return Jet.cast(b)*self.inv()
    def __pow__(self,p):
        if p==0:return Jet.const(np.ones_like(self.c[0]))
        if p==1:return self
        if p==2:return self*self
        return self.unary(lambda x:x**p,lambda x:p*x**(p-1),lambda x:p*(p-1)*x**(p-2))
    def unary(self,f,df,ddf):
        a=self.c[0];u=self-Jet.const(a)
        return Jet.const(f(a))+Jet.const(df(a))*u+Jet.const(.5*ddf(a))*(u*u)
    def inv(self):return self.unary(lambda x:1/x,lambda x:-1/x**2,lambda x:2/x**3)
    def sqrt(self):return self**.5
    def sin(self):return self.unary(np.sin,np.cos,lambda x:-np.sin(x))
    def cos(self):return self.unary(np.cos,lambda x:-np.sin(x),lambda x:-np.cos(x))
    def sinh(self):return self.unary(np.sinh,np.cosh,np.sinh)
    def cosh(self):return self.unary(np.cosh,np.sinh,np.cosh)
    def __getitem__(self,key):
        if not isinstance(key,tuple):key=(key,)
        return Jet(self.c[(slice(None),)+key])
    @property
    def T(self):return Jet(np.swapaxes(self.c,-1,-2))
    def sum(self,axis):return Jet(self.c.sum(axis=axis+1 if axis>=0 else axis))
    def value(self,p):
        return sum(self.c[k]*np.prod([p[j]**t[j] for j in range(3)]) for k,t in enumerate(TERMS))

def stack(xs,axis=-1):
    xs=[Jet.cast(x) for x in xs]
    return Jet(np.stack([np.stack([x.c[k] for x in xs],axis=axis) for k in range(10)]))
def matrix(a,b,c,d):return stack([stack([a,b]),stack([c,d])],axis=-2)
