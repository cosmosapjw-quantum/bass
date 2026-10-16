"""54-digit crosscheck of SAME FD96 binary64 quadrature nodes, not continuum."""
import sys,math,json,pathlib
import mpmath as mp
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from kinetic_equilibrium import FD96Equilibrium
mp.mp.dps=54
F=mp.mpf

def root(m,x,A):
    obj=FD96Equilibrium(m)
    q=[F(repr(float(v))) for v in obj.q]
    w=[F(repr(float(v))) for v in obj.rw]
    z=[F(repr(float(v)))**2 for v in obj.mu]
    a=[F(repr(float(v))) for v in obj.wa]
    mass=F(str(m));r=mp.exp(-F(str(x)));amp=F(str(A))
    k=[(r*qi)**2 for qi in q]
    norm=mp.fsum(wi*mp.sqrt(mass*mass+qi*qi) for wi,qi in zip(w,q))
    def delta(b):
        p=mp.exp(2*b);v=mp.exp(-4*b)
        return r**3/norm*mp.fsum(w[i]*a[j]*(1+amp*(3*z[j]-1)/2)*
          (k[i]*(v*z[j]-p*(1-z[j])/2))/
          mp.sqrt(mass*mass+k[i]*(p*(1-z[j])+v*z[j]))
          for i in range(len(q)) for j in range(len(z)))
    binary=obj.equilibrium(x,A).b_star
    higher=mp.findroot(delta,(F(str(binary)),F(str(binary+.003))))
    return dict(m=m,x=x,A=A,binary64=binary,mp54=mp.nstr(higher,54),
      abs_difference=float(abs(higher-F(str(binary)))),
      mp_residual=mp.nstr(delta(higher),20))

if __name__=="__main__":
    out=[root(3.,.7,2.),root(300.,1.,-1.)]
    assert all(c["abs_difference"]<4e-14 for c in out)
    print(json.dumps({"scope":"same fixed double FD96 nodes, not continuum","cases":out},indent=2))
