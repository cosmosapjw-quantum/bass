"""New smooth integrals with declared analytic disks and MP allowance.

No empirical rule difference is treated as the analytic remainder. The exact
Gauss theorem is conditional on the separately declared MP arithmetic model.
"""
from mp_b import *

CERTIFICATES=[]
def magnitude(x):return matnorm(x) if isinstance(x,mp.matrix) else abs(x)
def nodes(a,b,n=24):
    if n not in RULES:RULES[n]=mp.gauss_quadrature(n,'legendre')
    x,w=RULES[n];mid=(a+b)/2;half=(b-a)/2
    return [(mid+half*x[i],half*w[i]) for i in range(n)]
def integrate(name,fn,a,b,radius,sup,n=24,diagnostic16=False):
    if a==b:return m(0),m(0)
    half=(b-a)/2;ratio=half/radius
    if not 0<ratio<1:raise ValueError('quadrature panel is outside declared analytic disk')
    terms=[];evaluation_error=m(0)
    for u,weight in nodes(a,b,n):
        evaluated=fn(u)
        if isinstance(evaluated,tuple):value,error=evaluated
        else:value,error=evaluated,m(0)
        terms.append(weight*value);evaluation_error+=weight*error
    start=mp.zeros(terms[0].rows,terms[0].cols) if isinstance(terms[0],mp.matrix) else m(0)
    value=sum(terms,start);gross=sum(magnitude(x) for x in terms);truncation=2*(b-a)*sup*ratio**(2*n)/(1-ratio);arithmetic=ARITH*gross
    diag=None
    if diagnostic16:
        terms16=[]
        for u,weight in nodes(a,b,16):
            evaluated=fn(u);terms16.append(weight*(evaluated[0] if isinstance(evaluated,tuple) else evaluated))
        diag=magnitude(value-sum(terms16,start))
    CERTIFICATES.append(dict(name=name,a=a,b=b,points=n,analytic_radius=radius,halfwidth_over_radius=ratio,analytic_sup=sup,
      analytic_quadrature_remainder=truncation,declared_MP_arithmetic_allowance=arithmetic,gross_scale=gross,
      propagated_node_evaluation_error=evaluation_error,diagnostic_GL16_GL24_difference=diag,
      qualification='analytic truncation bound plus declared MP arithmetic allowance; conditional numerical enclosure'))
    return value,truncation+arithmetic+evaluation_error
