import numpy as np
from feedback import coefficients,mat,lyapunov,loss,integrate
def test_lyapunov_matrix_identity():
    for a in (1/21,.1,.2):
        _,og,on,d=coefficients(a)
        for k in (0.,.02,3.):
            M=mat(a,k,'all')
            P=np.diag([10/og,1.,8/3,on/og])
            dP=np.diag([(4+2*d)*10/og,0,0,0])
            Q=M.T@P+P@M+dP
            want=np.array([[-20/og,0,0,0],[0,-1.8*k,-.8*k,0],[0,-.8*k,-32*k/15,0],[0,0,0,0]])
            assert np.max(abs(Q-want))<1e-10
            for v in ([1.,-2.,.02,-2.],[.1,3.,-4.,2.]):
                v=np.array(v)
                assert abs(v@Q@v+loss(a,k,v,'all'))<1e-10
def test_zero_opacity_and_free_tracer():
    u=np.linspace(0,np.log(21/5),2001);a=np.exp(u)/21;k=np.zeros_like(a)
    tr=integrate(u,k,'tracer');fb=integrate(u,k,'all')
    assert tr['end'][2]==fb['end'][2]==0.
    assert fb['end'][0]<tr['end'][0]
    assert fb['lyapunov_relative_balance']<1e-8
    H0=coefficients(a[0])[0];H1=coefficients(a[-1])[0]
    assert abs(tr['end'][0]-(a[0]/a[-1])**3*H0/H1)<1e-9
