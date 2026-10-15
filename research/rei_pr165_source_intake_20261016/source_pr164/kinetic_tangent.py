"""BASS PR163 source-normalized FD96 massive Einstein--Vlasov tangent demonstrator.

Standalone *Python* reference, for scoped LRS Bianchi I on a frozen isotropic
radiation background. It does NOT evolve REI gamma/nu multipoles or H/He chemistry.

Reconstructs BASS bianchi/matter/freestream.py _Q/_DQ (Gaussian NR=96,
L=3 compactification) with the exact same FD rule, and PR163 GL32 angular rule.
The original source SHA/commit is recorded separately; this is an independent
source-formula reconstruction, not a byte-read of the original Python module.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp

H0 = 2.1842852410855026e-18
OMEGA_M = .315
OMEGA_B = .049309230511847414
OMEGA_R = 9.2e-5
OMEGA_L = .6849080000000001
AREF = 1.0 / 21.0
AEND = .2
XMAX = math.log(AEND / AREF)

@dataclass(frozen=True)
class Stress:
    rho: float
    pbar: float
    delta: float
    chi: float
    rho_A: float
    delta_A: float

class MassiveFD96:
    def __init__(self, mass: float, nangle: int = 32):
        if not (math.isfinite(mass) and 3 <= mass <= 1e5):
            raise ValueError('mass/Tref outside original BASS domain')
        if not (isinstance(nangle, int) and 8 <= nangle <= 256):
            raise ValueError('GL node count outside original source domain')
        self.mass = mass
        u, wu = leggauss(96)
        self.q = 3.0 * (1 + u) / (1 - u)
        dq = wu * 6.0 / (1 - u)**2
        fd = 1.0 / (np.exp(np.minimum(self.q, 700.0)) + 1.0)
        self.rw = dq * self.q**2 * fd
        self.mu, wa = leggauss(nangle)
        self.wa = wa * .5
        self.p2 = (3*self.mu*self.mu - 1)*.5
        self.norm = float(self.rw @ np.hypot(mass, self.q))
        self.initial_v2 = float(self.rw @ (self.q**2/np.hypot(mass,self.q)) / self.norm)
        if not self.norm > 0: raise ArithmeticError('bad FD kinetic source norm')

    def moments(self, x: float, b: float, A: float) -> Stress:
        if not all(map(math.isfinite, (x,b,A))) or not (0 <= x <= XMAX+1e-9 and abs(b) <= 1 and -1 <= A <= 2):
            raise ValueError('source chart or positive W domain failure')
        r = math.exp(-x)
        k = (r*self.q[:,None])**2
        z = (self.mu[None,:])**2
        p2 = self.p2[None,:]
        tp = math.expm1(2*b)
        tz = math.expm1(-4*b)
        d = tp*(1-z)+tz*z
        E0 = np.hypot(self.mass,r*self.q)[:,None]
        E = np.sqrt(E0*E0+k*d)
        wa = self.wa[None,:]
        w = wa*(1+A*p2)
        wr = self.rw[:,None]*w
        weight = (r**3)/self.norm
        rho = weight * np.sum(wr*E)
        pbar = weight * np.sum(wr*k*(1+d)/(3*E))
        # PR162 stable representation, analytic angular polynomial.
        poly = A/5 + tz*(1/3+2*A/15)-tp*(1/3-A/15)
        g = p2+tz*z-tp*(1-z)*.5
        inv_diff = -k*d/(E*E0*(E+E0))
        tail = np.sum(w*g*inv_diff,axis=1)
        delta = weight * np.sum(self.rw*(r*self.q)**2*(poly/E0[:,0]+tail))
        # PR163 exact analytic partial_b DeltaP.
        dl = -4*(1+tz)*z-(1+tp)*(1-z)
        L = k*g
        chi = weight * np.sum(wr*(k*dl/E+2*L*L/E**3))
        # Parameter derivative at fixed x,b and canonical kinetic mass norm.
        rho_A = weight*np.sum(self.rw[:,None]*wa*p2*E)
        poly_A = 1/5 + tz*2/15+tp/15
        tail_A = np.sum(wa*p2*g*inv_diff,axis=1)
        delta_A = weight*np.sum(self.rw*(r*self.q)**2*(poly_A/E0[:,0]+tail_A))
        return Stress(*(float(q) for q in (rho,pbar,delta,chi,rho_A,delta_A)))

class EinsteinTangent:
    def __init__(self,mass:float=30.,fraction:float=.1,A:float=.5,
                 Sigma_ref:float=0.,orientation:int=1,nangle:int=32):
        if not (math.isfinite(fraction) and 0<=fraction<= (OMEGA_M-OMEGA_B)/OMEGA_M):
            raise ValueError('massive Ωm must exclude baryons and not double-count matter')
        if not (math.isfinite(A) and -1<=A<=2):raise ValueError('positive W=1+A P2 domain')
        if not (0<=Sigma_ref<=.07 and orientation in (-1,1)) or (Sigma_ref==0 and orientation==-1):
            raise ValueError('bounded source Sigma with canonical zero and separate orientation')
        self.fd=MassiveFD96(mass,nangle)
        self.fraction=fraction
        self.A=A
        self.Sigma_ref=Sigma_ref
        self.orientation=orientation
        self.cm=OMEGA_M*fraction/AREF**3
        self.g=H0**2*self.cm
        self.href=H0*math.sqrt(OMEGA_M/AREF**3+OMEGA_R/AREF**4+OMEGA_L)
        self.y0=np.array([0.,orientation*Sigma_ref/math.sqrt(3-Sigma_ref**2),0.,0.,0.,0.],dtype=float)

    def field(self,x,b,v,A=None):
        if A is None:A=self.A
        M=self.fd.moments(x,b,A)
        a=AREF*math.exp(x)
        dust=OMEGA_M*(1-self.fraction)/a**3
        rad=OMEGA_R/a**4
        H2=H0**2*(dust+rad+OMEGA_L+self.cm*M.rho)+(self.href*v)**2
        if H2<=0:raise ArithmeticError('Einstein Hamiltonian nonpositive')
        return M,math.sqrt(H2),dust,rad

    def derivative(self,x,y,A=None):
        if A is None:A=self.A
        b,v,t=y[:3]
        M,H,_,_=self.field(x,b,v,A)
        Hb=-self.g*M.delta/H
        Hv=self.href*self.href*v/H
        HA=self.g*M.rho_A/(2*H)
        bdot=self.href*v/H
        vdot=-3*v+self.g*M.delta/(self.href*H)
        tdot=self.href/H
        dbdot_db=-(self.href*v)*Hb/H**2
        dbdot_dv=self.href/H-(self.href*v)*Hv/H**2
        dbdot_dA=-(self.href*v)*HA/H**2
        dvdot_db=self.g/self.href*(M.chi/H-M.delta*Hb/H**2)
        dvdot_dv=-3-self.g/self.href*(M.delta*Hv/H**2)
        dvdot_dA=self.g/self.href*(M.delta_A/H-M.delta*HA/H**2)
        dtdot_db=-self.href*Hb/H**2
        dtdot_dv=-self.href*Hv/H**2
        dtdot_dA=-self.href*HA/H**2
        u,w,z=y[3:]
        return np.array([bdot,vdot,tdot,
                dbdot_db*u+dbdot_dv*w+dbdot_dA,
                dvdot_db*u+dvdot_dv*w+dvdot_dA,
                dtdot_db*u+dtdot_dv*w+dtdot_dA])

    def jacobian(self,x,y):
        b,v,_=y[:3]
        M,H,_,_=self.field(x,b,v)
        Hb=-self.g*M.delta/H
        Hv=self.href*self.href*v/H
        h=self.href
        return np.array([
            [-h*v*Hb/H**2, h/H-h*v*Hv/H**2,0.],
            [self.g/h*(M.chi/H-M.delta*Hb/H**2), -3-self.g/h*M.delta*Hv/H**2,0.],
            [-h*Hb/H**2, -h*Hv/H**2,0.]
        ])

    def raychaudhuri(self,x,y):
        b,v=y[:2]
        M,H,dust,rad=self.field(x,b,v)
        s=self.href*v
        Hp=(H0**2*(-3*dust-4*rad-3*self.cm*(M.rho+M.pbar))-6*s*s)/(2*H)
        return Hp

    def solution(self,rtol=2e-11,atol=5e-13,n=101):
        t_eval=np.linspace(0,XMAX,n)
        y=solve_ivp(self.derivative,(0.,XMAX),self.y0,t_eval=t_eval,
                    rtol=rtol,atol=atol,method='DOP853',dense_output=True)
        if not y.success:raise RuntimeError('Einstein kinetic IVP did not converge: '+y.message)
        return y

    def endpoint(self,**kwargs):
        sol=self.solution(**kwargs)
        b,v,t,u,w,z=sol.y[:,-1]
        _,H,_,_=self.field(XMAX,b,v)
        return {'b':float(b),'signed_s_over_H':float(self.href*v/H),
                'Sigma':float(math.sqrt(3)*abs(self.href*v)/H),
                'tau_href':float(t),'sensitivity_b_A':float(u),
                'sensitivity_v_A':float(w),'sensitivity_tau_A':float(z),
                'nfev':int(sol.nfev)}
