# Exact BG-02 off-shell identity audit for SageMath.
R3,H,sigma2,divA,A2,Lambda,kappaG,rho,p,tau = var(
    'R3 H sigma2 divA A2 Lambda kappaG rho p tau'
)
Hres=(R3+6*H^2-sigma2-2*Lambda-2*kappaG*rho)/2
Ftrace=-R3/12-3*H^2/2-sigma2/4+(divA+A2)/3+Lambda/2-kappaG*p/2
FADM=-R3/3-3*H^2+(divA+A2)/3+kappaG*(rho-p)/2+Lambda
FRay=-H^2-sigma2/3+(divA+A2)/3-kappaG*(rho+3*p)/6+Lambda/3
residuals=[expand(FADM-Ftrace+Hres/2),expand(Ftrace-FRay+Hres/6),expand(FADM-FRay+2*Hres/3)]
assert residuals == [0,0,0]
print('BG02_SAGEMATH_OFFSHELL=PASS')
