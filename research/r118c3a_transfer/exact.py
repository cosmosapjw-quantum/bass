import sympy as s,json
from pathlib import Path
x,y,z,a,b=s.symbols('x y z a b',real=True);v=(x,y,z);r=x*x+y*y+z*z;Q=a*x*x+b*y*y-(a+b)*z*z
def lap(p):return s.expand(sum(s.diff(p,w,2) for w in v))
def harm(l):
 q=x*y*z*Q**((l-3)//2);p=0
 for j in range((l-3)//2+1):
    p+=(-1)**j*r**j*q/(2**j*s.factorial(j)*s.prod(2*l-2*m+1 for m in range(1,j+1)))
    q=lap(q)
 return s.expand(p)
def avg(p):
 return s.expand(sum(c*s.prod(s.factorial2(i-1) if i else 1 for i in k)/s.factorial2(sum(k)+1) for k,c in s.Poly(p,x,y,z).terms() if all(i%2==0 for i in k)))
rows=[]
for l in (9,11):
 p=harm(l);assert lap(p)==0
 w=s.factor(avg(p*p));I2=a*a+b*b+(a+b)**2;I3=a**3+b**3-(a+b)**3
 k=(l-3)//2
 C=w.subs({a:1,b:-1})/2**k;B=(w.subs({a:1,b:1})-C*6**k)/(36*6**(k-3))
 assert s.expand(w-C*I2**k-B*I2**(k-3)*I3**2)==0
 fac=s.factorial2(2*l+1)/s.factorial(l)
 row=dict(ell=l,mean_I2_power=str(C),mean_I3_term=str(B),STF_I2_power=str(C*fac),STF_I3_term=str(B*fac),polynomial=str(p))
 rows.append(row);print(row,flush=True)
# y-distortion energy/number moment by integrations by parts:
# integral x^(m-2) d(x^4 f') = (m-2)(m+1) integral x^m f.
assert [(m-2)*(m+1) for m in (2,3)]==[0,4]
Path(__file__).with_name('EXACT.json').write_text(json.dumps(rows,indent=2)+'\n')
