"""Separate proper reaction time, fluid expansion and photon-frame quantities.
Inputs H [s^-1], beta=v/c, beta_prime=d beta/d tau_H. Temperature functions
assume a fixed-composition monatomic gas and a prescribed scalar reservoir;
exact boosted radiation moments are exposed separately, never silently used
as a scalar blackbody temperature in an atomic collision kernel.
"""
import numpy as np

def finite(x,name):
    a=np.asarray(x,dtype=float)
    if not np.isfinite(a).all():raise ValueError('nonfinite '+name)
    return a

def kinematics(H,beta,beta_prime):
    h,b,bp=np.broadcast_arrays(finite(H,'H'),finite(beta,'beta'),finite(beta_prime,'beta_prime'))
    if np.any(h<=0) or np.any(abs(b)>=1):raise ValueError('H must be positive and |beta|<1')
    g=1/np.sqrt(1-b*b);L=b*bp/(1-b*b)
    return {'H':h,'Gamma':g,'L':L,'proper_per_tau':1/(g*h),'theta':g*h*(3+L),'A':2+2*L/3}

def reaction_rhs(R_proper,k):
    return finite(R_proper,'R_proper')*k['proper_per_tau']

def thermal_rhs(T,Tr,K_proper,Q_proper,k):
    T,Tr,K,Q=np.broadcast_arrays(finite(T,'T'),finite(Tr,'Tr'),finite(K_proper,'K'),finite(Q_proper,'Q'))
    if np.any(T<0) or np.any(Tr<0) or np.any(K<0):raise ValueError('negative temperature or coupling')
    return -k['A']*T+reaction_rhs(K*(Tr-T)+Q,k)

def tracking_temperature(Tr,K_proper,Q_proper,k):
    C=reaction_rhs(K_proper,k);J=reaction_rhs(Q_proper,k);den=C+k['A']-1
    if np.any(den<=0):raise ValueError('tracking approximation denominator not positive')
    return (C*finite(Tr,'Tr')+J)/den

def implicit_temperature(T,Tr,K_proper,Q_proper,k,dt):
    dt=finite(dt,'dt')
    if np.any(dt<=0):raise ValueError('nonpositive step')
    C=reaction_rhs(K_proper,k);J=reaction_rhs(Q_proper,k);den=1+dt*(k['A']+C)
    if np.any(den<=0):raise ValueError('implicit denominator not positive')
    return (finite(T,'T')+dt*(C*finite(Tr,'Tr')+J))/den

def directional_temperature(Tn,beta,mu_e):
    T,b,mu=np.broadcast_arrays(finite(Tn,'Tn'),finite(beta,'beta'),finite(mu_e,'mu_e'))
    if np.any(T<=0) or np.any(abs(b)>=1) or np.any(abs(mu)>1):raise ValueError('invalid radiation input')
    return T*np.sqrt(1-b*b)/(1+b*mu)

def radiation_moments(beta):
    b=finite(beta,'beta')
    if np.any(abs(b)>=1):raise ValueError('superluminal radiation frame')
    g=1/np.sqrt(1-b*b)
    return {'number_ratio':g,'energy_ratio':g*g*(1+b*b/3),'flux_ratio':-4*g*g*b/3,
            'parallel_pressure_ratio':g*g*(1/3+b*b),'transverse_pressure_ratio':np.ones_like(b)/3}
