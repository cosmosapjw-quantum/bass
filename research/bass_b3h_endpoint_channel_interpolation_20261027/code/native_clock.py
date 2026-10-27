"""New native proper clock; old scalar moments are comparison/reuse data only."""
from mp_b import *
from certified_quad import integrate
from jets import Jet

class NativeClock:
    def __init__(self,data,radius=m('.001')):
        packet=data['incoming_packet'];sel=packet['selection'];inc=packet['incoming'];cos=packet['native_cosmology'];self.data=data
        self.h=m(float.fromhex(sel['dlna_hex']));self.eta0=m(float.fromhex(sel['eta0_hex']))+sel['cell_indices'][0]*self.h
        self.matter=m(cos['omh2'])*mp.exp(-3*self.eta0);self.dark=m(cos['odeh2']);self.radiation=m(cos['photon_omega_prefactor'])*m(cos['T0_K'])**4*(1+m(cos['neutrino_factor'])*m(cos['Nnueff']))*mp.exp(-4*self.eta0)
        self.Hpref=m(cos['H_prefactor_s_inv']);self.NH=m(data['tube']['nH_reference_m3']);self.nH0=self.NH/m(10**6);self.LYA=m(cos['LYA_FACT_cm3_inv'])
        self.g0=data['ops'][0]['x1s'];self.g1=data['ops'][1]['x1s'];self.gprime=(self.g1-self.g0)/self.h
        self.E=m(float.fromhex(inc['target_energy_eV_hex']));sourceE=m(float.fromhex(inc['source_energy_eV_hex']));self.lag=mp.log(sourceE/self.E)
        self.knots=[(index-sel['cell_indices'][0])*self.h+self.lag for index in inc['source_indices']];self.departures=[m(float.fromhex(x)) for x in inc['departure_hex']]
        self.edges=[m(0)]+[u for u in self.knots if 0<u<self.h]+[self.h];self.segments=list(zip(self.edges[:-1],self.edges[1:]))
        self.source_segment_indices=[next(j for j in range(len(self.knots)-1) if self.knots[j]<=(a+b)/2<=self.knots[j+1]) for a,b in self.segments]
        self.slopes=[(self.departures[j+1]-self.departures[j])/(self.knots[j+1]-self.knots[j]) for j in self.source_segment_indices]
        self.A=self.E*mp.exp(self.eta0)*m(cos['fsR'])**2*m(cos['meR'])/(m(cos['kBoltz_eV_K'])*m(cos['T0_K']))
        self.radius=radius;self.partial_cache={};mid=self.h/2;disk=self.H_disk(mid,radius)
        self.T,self.T_error=integrate('new native total proper duration once',lambda u:1/self.H(u),m(0),self.h,radius,1/disk['H_min'],diagnostic16=True)
        if self.T<=self.T_error:raise ValueError('new native total duration enclosure not positive')
        self.T_lower=self.T-self.T_error;self.T_upper=self.T+self.T_error
        self.old_saved_duration=m(data['tube']['independent_reference']['proper_duration_s']);self.time_cache={}
    def H(self,u):return self.Hpref*mp.sqrt(self.matter*mp.exp(-3*u)+self.dark+self.radiation*mp.exp(-4*u))
    def Hjet(self,u,n=3):
        U=Jet.variable(u,n);F=self.matter*(-3*U).exp()+self.dark+self.radiation*(-4*U).exp()
        return self.Hpref*F.sqrt()
    def g(self,u):return self.g0+self.gprime*u
    def Ralpha(self,u):return self.LYA/self.nH0*self.H(u)*mp.exp(3*u)/self.g(u)
    def H_disk(self,centre,rho):
        matter=self.matter*mp.exp(-3*centre);rad=self.radiation*mp.exp(-4*centre);F=matter+self.dark+rad
        delta=(matter*mp.expm1(3*rho)+rad*mp.expm1(4*rho))/F
        if delta>=1:raise ValueError('native H square-root disk crosses branch')
        Hc=self.H(centre);lo=Hc*mp.sqrt(1-delta);hi=Hc*mp.sqrt(1+delta)
        return dict(centre=centre,radius=rho,delta_F=delta,H_min=lo,H_max=hi,H_u_over_H_bound=(3*matter*mp.exp(3*rho)+4*rad*mp.exp(4*rho))/(2*F*(1-delta)))
    def theta(self,u):
        if u==0:return m(0),m(0)
        if u==self.h:return m(1),m(0)
        key=u._mpf_
        if key not in self.partial_cache:
            t,error=self.partial_time(u)
            theta=t/self.T;bound=error/self.T_lower+abs(t)*self.T_error/(self.T*self.T_lower)
            self.partial_cache[key]=(theta,bound)
        return self.partial_cache[key]
    def partial_time(self,u):
        if u==0:return m(0),m(0)
        if u==self.h:return self.T,self.T_error
        key=u._mpf_
        if key not in self.time_cache:
            disk=self.H_disk(u/2,self.radius);self.time_cache[key]=integrate('new bounded partial proper clock',lambda x:1/self.H(x),m(0),u,self.radius,1/disk['H_min'])
        return self.time_cache[key]
    def theta_jet(self,u,H,n=3):
        value,error=self.theta(u);invH=H.inverse();coeff=[value]+[invH.c[k-1]/(k*self.T) for k in range(1,n+1)]
        inverse_T_error=self.T_error/(self.T*self.T_lower)
        errs=[error]+[(abs(invH.c[k-1])*inverse_T_error+invH.e[k-1]/self.T_lower)/k+ARITH*abs(coeff[k]) for k in range(1,n+1)]
        return Jet(coeff,errs),error
    def departure(self,u,segment):
        j=self.source_segment_indices[segment];return self.departures[j]+self.slopes[segment]*(u-self.knots[j])
    def incoming_jet(self,u,segment,n=3):
        U=Jet.variable(u,n);j=self.source_segment_indices[segment]
        dep=self.departures[j]+self.slopes[segment]*(U-self.knots[j]);wien=(-self.A*U.exp()).exp()
        return dep+wien
    def report(self):
        return dict(new_duration=self.T,new_duration_error=self.T_error,new_duration_lower=self.T_lower,old_duration_comparison_only=self.old_saved_duration,
          new_minus_old_duration=self.T-self.old_saved_duration,proper_clock_computed_once=True,old_duration_function_calls=0,
          h=self.h,eta0=self.eta0,lag=self.lag,actual_split_edges=self.edges,A=self.A,NH_reference=self.NH,g0=self.g0,g1=self.g1,
          old_incoming_count=self.data['tube']['independent_reference']['N_in_m3'],old_incoming_energy=self.data['tube']['independent_reference']['U0_J_m3'],
          inherited_reference_quadrature_remainder=None,physical_clock_radius=None)
