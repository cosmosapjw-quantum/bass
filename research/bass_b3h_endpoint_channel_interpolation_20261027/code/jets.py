"""Finite algebraic u-Taylor jets; matrix multiplication order is preserved.

Coefficients are derivatives divided by factorial. Proper differentiation is
the explicit analytic operator D=H(u)*partial_u, never a finite difference.
"""
from mp_b import mp,m,matnorm,ARITH

def zero_like(x):return mp.zeros(x.rows,x.cols) if isinstance(x,mp.matrix) else m(0)
def mag(x):return matnorm(x) if isinstance(x,mp.matrix) else abs(x)
def product_error(a,ea,b,eb):return mag(a)*eb+ea*mag(b)+ea*eb+ARITH*mag(a)*mag(b)
class Jet:
    def __init__(self,coeff,errors=None):self.c=list(coeff);self.e=list(errors) if errors is not None else [m(0)]*len(self.c)
    @property
    def degree(self):return len(self.c)-1
    @classmethod
    def constant(cls,x,n,error=m(0)):return cls([x]+[zero_like(x) for _ in range(n)],[error]+[m(0)]*n)
    @classmethod
    def variable(cls,x,n=3):return cls([m(x),m(1)]+[m(0)]*(n-1))
    def truncate(self,n):return Jet(self.c[:n+1],self.e[:n+1])
    def _other(self,x):return x if isinstance(x,Jet) else Jet.constant(x,self.degree)
    def __add__(self,x):
        x=self._other(x);n=min(self.degree,x.degree);return Jet([self.c[k]+x.c[k] for k in range(n+1)],[self.e[k]+x.e[k]+ARITH*(mag(self.c[k])+mag(x.c[k])) for k in range(n+1)])
    __radd__=__add__
    def __neg__(self):return Jet([-x for x in self.c],self.e)
    def __sub__(self,x):return self+-self._other(x)
    def __rsub__(self,x):return self._other(x)+-self
    def __mul__(self,x):
        x=self._other(x);n=min(self.degree,x.degree)
        return Jet([sum((self.c[k]*x.c[j-k] for k in range(j+1)),zero_like(self.c[0]*x.c[0])) for j in range(n+1)],
          [sum(product_error(self.c[k],self.e[k],x.c[j-k],x.e[j-k]) for k in range(j+1)) for j in range(n+1)])
    def __rmul__(self,x):return self._other(x)*self
    def inverse(self):
        q=[self.c[0]**-1];beta=mag(q[0])*self.e[0]
        if beta>=1:raise ValueError('point inverse jet error Neumann margin failed')
        eq=[mag(q[0])**2*self.e[0]/(1-beta)+ARITH*mag(q[0])*(1+mag(q[0])*mag(self.c[0]))]
        for n in range(1,self.degree+1):
            inner=sum((self.c[k]*q[n-k] for k in range(1,n+1)),zero_like(self.c[0]*q[0]));ei=sum(product_error(self.c[k],self.e[k],q[n-k],eq[n-k]) for k in range(1,n+1))
            q.append(-q[0]*inner);eq.append(product_error(q[0],eq[0],inner,ei))
        return Jet(q,eq)
    def __truediv__(self,x):return self*self._other(x).inverse()
    def __rtruediv__(self,x):return self._other(x)*self.inverse()
    def derivative_u(self):return Jet([(k+1)*self.c[k+1] for k in range(self.degree)],[(k+1)*self.e[k+1]+ARITH*(k+1)*mag(self.c[k+1]) for k in range(self.degree)])
    def derivative_t(self,H):return H*self.derivative_u()
    def exp(self):
        out=[mp.exp(self.c[0])];errors=[abs(out[0])*mp.expm1(self.e[0])+ARITH*abs(out[0])]
        for n in range(1,self.degree+1):
            out.append(sum(k*self.c[k]*out[n-k] for k in range(1,n+1))/n)
            errors.append(sum(k*product_error(self.c[k],self.e[k],out[n-k],errors[n-k]) for k in range(1,n+1))/n+ARITH*abs(out[-1]))
        return Jet(out,errors)
    def sqrt(self):
        if self.c[0]<=self.e[0]:raise ValueError('sqrt jet positive branch error margin failed')
        out=[mp.sqrt(self.c[0])];errors=[self.e[0]/(mp.sqrt(self.c[0]-self.e[0])+out[0])+ARITH*out[0]]
        for n in range(1,self.degree+1):
            numerator=self.c[n]-sum(out[k]*out[n-k] for k in range(1,n));en=self.e[n]+sum(product_error(out[k],errors[k],out[n-k],errors[n-k]) for k in range(1,n));denom=2*out[0];ed=2*errors[0]
            out.append(numerator/denom);errors.append((en+abs(out[-1])*ed)/(denom-ed)+ARITH*abs(out[-1]))
        return Jet(out,errors)

def slow_state(M,b,H,order=2):
    K=M.inverse();terms=[K*b]
    for _ in range(order):terms.append(-(K*terms[-1].derivative_t(H)))
    value=sum((x.c[0] for x in terms),mp.zeros(b.c[0].rows,b.c[0].cols));residual=terms[-1].derivative_t(H).c[0]
    return dict(value=value,value_error=sum(x.e[0] for x in terms)+ARITH*sum(mag(x.c[0]) for x in terms),terms=terms,residual=residual,residual_evaluation_error=terms[-1].derivative_t(H).e[0])

def adjoint_terms(q,M,H,order=3):
    K=M.inverse();terms=[q*K]
    for _ in range(order-1):terms.append(terms[-1].derivative_t(H)*K)
    return terms,terms[-1].derivative_t(H).c[0]
