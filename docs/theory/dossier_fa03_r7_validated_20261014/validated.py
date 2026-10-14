"""Interval Taylor enclosure of FA03's finite GL3x12 detector.

Exact decimal model. Six Hermitian matrices use (F11,F22,Re F12,Im F12).
All endpoint interval coefficients include inherited incoming error. A separate
analytic Cauchy tail is added each step; no refinement difference is a bound.
Only a finite angular quadrature is certified, not its continuous cap integral.
"""
from __future__ import annotations
from fractions import Fraction as Q
from pathlib import Path
import argparse,json,time
from mpmath import iv,mp


def tail_bound(majorant,ratio,degree):
    if majorant<0 or not 0<=ratio<1 or not isinstance(degree,int) or degree<0:
        raise ValueError('nonnegative majorant, 0<=ratio<1, integer degree required')
    return majorant*ratio**(degree+1)/(1-ratio)

def iq(a,b=1): return iv.mpf(a)/b

def frac(t):
    sign,man,exp,bc=t
    return Q((-1 if sign else 1)*man)*(Q(2)**exp)

def ends(x): return tuple(frac(t) for t in x._mpi_)
def upper_abs(x):
    a,b=ends(x);return max(abs(a),abs(b))
def encode(x):
    a,b=ends(x)
    return {'lo':[a.numerator,a.denominator],'hi':[b.numerator,b.denominator],
            'mid':float((a+b)/2),'radius':float((b-a)/2)}
def ivq(x): return iq(x.numerator,x.denominator)

def add(a,b): return [x+y for x,y in zip(a,b)]
def neg(a): return [-x for x in a]
def scale(a,b):return [x*b for x in a]
def mul(a,b):
    n=len(a);return [sum((a[j]*b[k-j] for j in range(k+1)),iv.mpf(0)) for k in range(n)]
def power(a,r):
    """Series of a**r from a*y'=r*y*a'; r is an exact rational."""
    n=len(a);out=[iv.exp(ivq(r)*iv.ln(a[0]))]
    rr=ivq(r)
    for k in range(1,n):
        out.append(sum((((rr+1)*j-k)*a[j]*out[k-j] for j in range(1,k+1)),iv.mpf(0))/(k*a[0]))
    return out

def dot(a,b):return sum((x*y for x,y in zip(a,b)),iv.mpf(0))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def cross_series(a,b):
    return [add(mul(a[1],b[2]),neg(mul(a[2],b[1]))),
            add(mul(a[2],b[0]),neg(mul(a[0],b[2]))),
            add(mul(a[0],b[1]),neg(mul(a[1],b[0])))]

def geometry(chi='0.008',psi='0.01'):
    ch=iv.mpf(chi);ps=iv.mpf(psi);delta=iq(1,50)
    sh=(iv.exp(ch)-iv.exp(-ch))/2;coh=(iv.exp(ch)+iv.exp(-ch))/2
    cp,sp=iv.cos(ps),iv.sin(ps)
    t=[-iv.sqrt(iq(3,5)),iv.mpf(0),iv.sqrt(iq(3,5))]
    wr=[Q(5,18),Q(4,9),Q(5,18)];rays=[]
    # Exact cap-area substitution: ell1 = 1-(t+1)*sin(delta/2)^2.
    for ir,tt in enumerate(t):
        ell1=1-(tt+1)*iv.sin(delta/2)**2;sr=iv.sqrt(1-ell1**2)
        for j in range(12):
            phi=iv.pi*j/6;ell=[ell1,sr*iv.cos(phi),sr*iv.sin(phi)]
            m=[cp*ell[0]-sp*ell[1],sp*ell[0]+cp*ell[1],ell[2]]
            L=coh+sh*m[0];n=[(sh+coh*m[0])/L,m[1]/L,m[2]/L]
            dm=iv.sqrt(1-m[1]**2)
            aw=[-m[0]*m[1]/dm,dm,-m[1]*m[2]/dm]
            bw=[-m[2]/dm,iv.mpf(0),m[0]/dm]
            at=[[coh*a[0]-sh*n[0]*a[0],a[1]-sh*n[1]*a[0],a[2]-sh*n[2]*a[0]] for a in [aw,bw]]
            hh=iv.sqrt(n[0]**2+n[1]**2);kk=[-n[1]/hh,n[0]/hh,iv.mpf(0)]
            b0=[kk,cross(n,kk)]
            C=[[dot(b0[i],at[jj]) for jj in range(2)] for i in range(2)]
            rays.append({'n':n,'kk':kk,'C':C,'L':L,'weight':wr[ir]/12,'index':(ir,j)})
    return rays

def fields_series(x0,p,data):
    z=iv.mpf(0);const=lambda a:[a]+[z]*p
    X=const(ivq(x0));X[1]=iv.mpf(1);n=data['n'];kk=data['kk'];C=data['C']
    vv=add(const(1-n[2]**2),scale(mul(X,X),n[2]**2));v=power(vv,Q(1,2));vi=power(vv,Q(-1,2))
    ray=[scale(vi,n[0]),scale(vi,n[1]),scale(mul(X,vi),n[2])]
    cb=cross_series(ray,[const(a) for a in kk]);B=[[const(kk[i]),cb[i]] for i in range(3)]
    S=[[add(scale(B[i][0],C[0][j]),scale(B[i][1],C[1][j])) for j in range(2)] for i in range(3)]
    # Source real/imaginary entries from exactly the parent's P3.
    Pr=[];Hi=[]
    for i,j in [(0,0),(1,1),(0,1)]:
        a=scale(mul(S[1][i],S[1][j]),iq(7,10));a=add(a,scale(mul(S[2][i],S[2][j]),iq(3,10)))
        a=add(a,scale(add(mul(S[1][i],S[2][j]),mul(S[2][i],S[1][j])),iq(1,10)))
        Pr.append(a)
        Hi.append(sum_series([scale(mul(S[k][i],S[k][j]),iq(1,5) if k<2 else iq(2,5)) for k in range(3)]))
    Pi=scale(add(mul(S[1][0],S[2][1]),neg(mul(S[2][0],S[1][1]))),iq(1,20))
    rot=scale(ray[0],iq(3,10));g=[Hi[0],Hi[1],add(Hi[2],neg(rot)),add(Hi[2],rot)]
    k=scale(mul(power(X,Q(-2,3)),v),data['L'])
    return Pr+[Pi],Hi,g,k

def sum_series(rows):return [sum(a,iv.mpf(0)) for a in zip(*rows)]
def loss_entries(g):
    g11,g22,g12,g21=g
    # Non-zero (row,col,coefficient-series) of -G F-F G^T.
    return [(0,0,scale(g11,-2)),(0,2,scale(g12,-2)),(1,1,scale(g22,-2)),(1,2,scale(g21,-2)),
            (2,0,neg(g21)),(2,1,neg(g12)),(2,2,neg(add(g11,g22))),(3,3,neg(add(g11,g22)))]

def moment(j):return (Q(51,50)**(j+1)-Q(49,50)**(j+1))/(Q(j+1)*Q(1,25))

def coefficients(x0,p,data):
    P,H,G,k=fields_series(x0,p,data);zero=[iv.mpf(0)]*(p+1)
    src=[zero[:] for _ in range(24)];entries=[]
    for b in range(6):
        for i,j,a in loss_entries(G):entries.append((4*b+i,4*b+j,a))
    for b in range(3):
        fac=scale(k,ivq(moment(b+4))/10);fac[0]+=ivq(moment(b+3))
        for i in range(4):src[4*b+i]=mul(fac,P[i])
    h_loss=loss_entries([H[0],H[1],H[2],H[2]])
    # Vj'=... -{H,k S(j+1)-Sj}; W'=... -2{H,k V1-V0}.
    for target,low,high,factor in [(3,0,1,1),(4,1,2,1),(5,3,4,2)]:
        for i,j,a in h_loss:
            entries.append((4*target+i,4*high+j,scale(mul(a,k),factor)))
            entries.append((4*target+i,4*low+j,scale(a,-factor)))
    return src,entries

def step(y,x0,h,p,data):
    src,ent=coefficients(x0,p,data);co=[list(y)]
    for n in range(p):
        rhs=[row[n] for row in src]
        for i,j,aa in ent:
            rhs[i]+=sum((aa[k]*co[n-k][j] for k in range(n+1)),iv.mpf(0))
        co.append([a/(n+1) for a in rhs])
    hh=ivq(h);result=co[-1]
    for a in co[-2::-1]:result=[a[i]+hh*result[i] for i in range(24)]
    # Complex-time proof: max block trace norm generator <=7, forcing <=2,
    # analytic disk R=1/8. Initial block trace <=5*max real component.
    ymax=max(upper_abs(a) for a in y);M=3*(5*ymax+Q(1,4)) # exp(7/8)<3
    tail=tail_bound(M,h*8,p);T=ivq(tail);rad=iv.mpf([-T.b,T.b])
    return [a+rad for a in result],tail

def solve(*,p=20,steps=32,ray_limit=36,ray_start=0):
    if steps<8 or p<4 or not 1<=ray_limit<=36 or not 0<=ray_start<36 or ray_start+ray_limit>36:raise ValueError('resolution outside bounded contract')
    iv.dps=65;mp.dps=80;rays=geometry();h=Q(1,2*steps)
    values=[];start=time.perf_counter()
    for i,data in enumerate(rays[ray_start:ray_start+ray_limit]):
        y=[iv.mpf(0)]*24;tails=[]
        for j in range(steps):y,r=step(y,Q(1,2)+j*h,h,p,data);tails.append(r)
        values.append(y)
        print(json.dumps({'ray_completed':ray_start+i+1,'total':ray_limit,'elapsed_s':time.perf_counter()-start,
                          'largest_radius':max(encode(a)['radius'] for a in y)}),flush=True)
    total=[sum((ivq(rays[ray_start+i]['weight'])*values[i][k] for i in range(ray_limit)),iv.mpf(0)) for k in range(24)]
    return {'schema':'fa03.r7.validated_taylor.v1','degree':p,'steps':steps,'rays':ray_limit,'interval_digits':iv.dps,
            'complete_detector':ray_limit==36,'ray_start':ray_start,'endpoint_components':[encode(a) for a in total],
            'rays_components':[[encode(a) for a in row] for row in values],
            'largest_detector_component_radius':max(encode(a)['radius'] for a in total),
            'elapsed_seconds':time.perf_counter()-start,
            'scope':'exact-decimal six matrix GL3x12 detector with time truncation and iv arithmetic; angular continuum/model errors excluded'}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output',required=True);a.add_argument('--degree',type=int,default=20);a.add_argument('--steps',type=int,default=32);a.add_argument('--rays',type=int,default=36);a.add_argument('--ray-start',type=int,default=0);args=a.parse_args()
    out=solve(p=args.degree,steps=args.steps,ray_limit=args.rays,ray_start=args.ray_start)
    Path(args.output).write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ('rays_components','endpoint_components')},indent=2))
