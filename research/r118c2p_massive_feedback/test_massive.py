import numpy as np
from massive import Species,Background,OG0,ON0,exact_stress
def test_limits_and_direct_tensor():
    for m in (0,.001,.05,.3):
        s=Species(m,128)
        for a in (1/21,.1,.2):
            rho,p,c,dc=s.moments(a)
            assert 0<c<=8*rho/15*(1+1e-13)
            assert dc<=1e-16
            x=exact_stress(s,a,1e-5);y=exact_stress(s,a,-1e-5)
            assert abs((x-y)/(2e-5)/(-c)-1)<2e-8
    s=Species(0,128);r,p,c,d=s.moments(.2)
    assert abs(c/r-8/15)<1e-14 and abs(p/r-1/3)<1e-14 and d==0
    r,p,c,d=Species(100.,128).moments(.2);assert abs(c/(2*p)-1)<1e-8
def test_background_continuity():
    for m in (0,.05,.3):
        bg=Background(m,128)
        assert abs(bg.coeff(1.)[0]/bg.h0-1)<2e-14
        for a in (.05,.2,.9):
            ep=1e-5
            H,og,oc,der,dchi=bg.coeff(a)
            fd=(np.log(bg.coeff(a*np.exp(ep))[0])-np.log(bg.coeff(a*np.exp(-ep))[0]))/(2*ep)
            assert abs(fd-der)<1e-8
