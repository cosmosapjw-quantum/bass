"""Exact-rational conditional bounds for a piecewise ODE reconstruction.

These operations consume supplied analytic enclosures. Exact arithmetic does
not certify the physical accuracy or derivation of the input enclosures.
"""
from fractions import Fraction as F
from itertools import product


def exact(x):
    """Keep written decimal/rational semantics; refuse implicit binary64."""
    if isinstance(x,bool) or not isinstance(x,(int,str,F)):
        raise ValueError('explicit finite integer/decimal/rational required')
    try:return F(x)
    except (ValueError,ZeroDivisionError) as e:raise ValueError('invalid rational') from e


def nonnegative(*args):
    values=tuple(exact(x) for x in args)
    if any(x<0 for x in values):raise ValueError('negative magnitude bound')
    return values


def matrix2(m):
    if len(m)!=2 or any(len(row)!=2 for row in m):raise ValueError('two-state matrix required')
    return [[exact(x) for x in row] for row in m]


def norm1(matrix):
    m=matrix2(matrix)
    return max(sum(abs(m[i][j]) for i in range(2)) for j in range(2))


def column_gap(matrix):
    m=matrix2(matrix)
    if m[0][1]>0 or m[1][0]>0:raise ValueError('-M must be Metzler')
    gap=min(sum(m[i][j] for i in range(2)) for j in range(2))
    if gap<=0:raise ValueError('positive column-sum gap required')
    return gap


def duration_interval(d,e):
    d,e=nonnegative(d,e)
    if e>d:raise ValueError('duration lower endpoint is negative')
    return d-e,d+e


def tail(beta,d,n=8):
    beta,d=nonnegative(beta,d)
    if beta==0 or type(n) is not int or n<1:raise ValueError('positive beta and integer n required')
    return (1+beta*d/n)**(-n)


def moments(beta,d):
    """Upper bounds on integral exp(-beta*t), integral t*exp(-beta*t)."""
    beta,d=nonnegative(beta,d)
    if beta==0:raise ValueError('positive beta required')
    return min(d,1/beta),min(d*d/2,1/(beta*beta))


def layer_mass(z,c,alpha,slope,beta,d):
    z,c,alpha,slope=nonnegative(z,c,alpha,slope)
    phi,psi=moments(beta,d)
    return z*min(c*phi,alpha*phi+slope*psi)


def gap_bound(m0,m1,b,theta,rate,allowance=0):
    """Convex norm envelope for an affine matrix and shared nonnegative rate."""
    a0,a1,bb=map(matrix2,(m0,m1,b))
    t0,t1=map(exact,theta);r0,r1=map(exact,rate)
    extra,=nonnegative(allowance)
    if not (0<=t0<=t1<=1 and 0<=r0<=r1):raise ValueError('invalid coefficient box')
    return max(norm1([[(1-t)*a0[i][j]+t*a1[i][j]+(r if i==j==1 else 0)-bb[i][j]
                       for j in range(2)] for i in range(2)])
               for t,r in product((t0,t1),(r0,r1)))+extra


def output_bound(n,r,gamma,initial,residuals,jumps):
    n,r,gamma,initial=nonnegative(n,r,gamma,initial)
    if gamma==0:raise ValueError('positive contraction bound required')
    masses=nonnegative(*residuals,*jumps)
    return n*r/gamma*(initial+sum(masses,F(0)))


def knot_mass(left,right,eps_left,eps_right,z=0,beta=1,dlo=0):
    """L1 jump bound; optional tail belongs only to the preceding panel."""
    if len(left)!=2 or len(right)!=2:raise ValueError('two-state vectors required')
    el,er,z=nonnegative(eps_left,eps_right,z)
    return sum(abs(exact(b)-exact(a)) for a,b in zip(left,right))+el+er+z*tail(beta,dlo)
