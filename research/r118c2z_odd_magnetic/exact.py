import sympy as s,json
from pathlib import Path
x,y,z,a,b=s.symbols('x y z a b',real=True);v=[x,y,z];t=[a,b,-a-b];r2=x*x+y*y+z*z;Q=sum(q*w*w for q,w in zip(t,v));R=sum(q*q*w*w for q,w in zip(t,v));I2=sum(q*q for q in t)
p=x*y*z*(Q**2-s.Rational(4,13)*r2*R+s.Rational(6,143)*r2**2*I2)
assert s.expand(sum(s.diff(p,w,2) for w in v))==0
def df(n):return s.factorial2(n) if n>=0 else s.Integer(1)
def avg(poly):
 return s.expand(sum(c*s.prod(df(i-1) for i in k)/df(sum(k)+1) for k,c in s.Poly(poly,x,y,z).terms() if all(i%2==0 for i in k)))
norm=s.factor(avg(p*p));coef=s.factor(norm/I2**2);assert not coef.free_symbols
tensorcoef=s.factor(coef*s.factorial2(15)/s.factorial(7))
out=dict(status='EXACT_SYMBOLIC',sphere_mean_coefficient=str(coef),tensor_norm_coefficient=str(tensorcoef),polynomial=str(s.expand(p)),scope='divide full B7 polynomial by Vandermonde; norm squared times Delta^2 I2^2')
Path(__file__).with_name('EXACT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
