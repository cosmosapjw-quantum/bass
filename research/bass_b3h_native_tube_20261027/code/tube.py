"""Finite native incoming Lyalpha characteristic inventory; no atomic transfer."""
from pathlib import Path
import bisect
import json
import math
import sys
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'vendor'))
from transport import diagonal_bound, determinant_bound
C_SI = 299792458.0


def finite(value, name):
    x = float(value)
    if not math.isfinite(x):
        raise ValueError('nonfinite '+name)
    return x


def exp_linear_integral(a, b, fa, fb, power):
    """Positive endpoint basis via convergent exponential moment series."""
    if not b > a:
        raise ValueError('positive segment width required')
    z = power*(b-a)
    term = 1.0
    left = right = 0.0
    for n in range(24):
        left += term/((n+1)*(n+2))
        right += term/(n+2)
        term *= z/(n+1)
        if abs(term) < 1e-30:
            break
    return (b-a)*math.exp(power*a)*(fa*left+fb*right)


def physical_bound(a, b, fa, fb, wien):
    bound = min(finite(fa,'departure endpoint'),finite(fb,'departure endpoint')) + min(finite(wien(a),'Wien endpoint'),finite(wien(b),'Wien endpoint'))
    if bound < 0:
        raise ValueError('UNRESOLVED_POSITIVITY: segment lower bound is negative; no clipping')
    return bound


class NativeTube:
    def __init__(self, packet):
        self.packet = packet
        sel, inc = packet['selection'], packet['incoming']
        self.k = sel['cell_indices'][0]
        if sel['cell_indices'] != [self.k,self.k+1] or inc['source_row'] != 140:
            raise ValueError('frozen adjacent cell / virtual140 required')
        self.h = float.fromhex(sel['dlna_hex'])
        self.eta_start = float.fromhex(sel['eta0_hex'])
        self.eta_ref = math.fsum([self.eta_start,self.k*self.h])
        self.E = float.fromhex(inc['target_energy_eV_hex'])
        self.Es = float.fromhex(inc['source_energy_eV_hex'])
        if not (self.h>0 and self.Es>self.E>0):
            raise ValueError('positive clock / strict-past energy ordering required')
        self.lag = math.log1p((self.Es-self.E)/self.E)
        self.causal_margin_lower_bound = self.lag-self.h
        if not self.causal_margin_lower_bound>0:
            raise ValueError('strict-past interpolation not certified: lag must exceed native cell width')
        self.knots = [(i-self.k)*self.h+self.lag for i in inc['source_indices']]
        self.values = [float.fromhex(x) for x in inc['departure_hex']]
        if not self.knots[0] <= 0 < self.h <= self.knots[-1]:
            raise ValueError('missing strict-past interpolation coverage')
        self.edges = [0.0]+[x for x in self.knots if 0<x<self.h]+[self.h]
        self.cos = packet['native_cosmology']
        if any(self.cos[k] != v for k,v in [('okh2',0.0),('w0',-1.0),('wa',0.0)]):
            raise ValueError('frozen native H specialization changed')
        self.G = 3e6*self.cos['LYA_FACT_cm3_inv']
        self.E_J = self.E*self.cos['EV_J']
        self.wien_A = self.E*math.exp(self.eta_ref)*self.cos['fsR']**2*self.cos['meR']/(self.cos['kBoltz_eV_K']*self.cos['T0_K'])

    def departure(self,u):
        j = min(max(bisect.bisect_right(self.knots,u)-1,0),len(self.knots)-2)
        t = (u-self.knots[j])/self.h
        if t < -1e-12 or t>1+1e-12:
            raise ValueError('outside supplied native interpolation segment')
        return (1-t)*self.values[j]+t*self.values[j+1]

    def wien(self,u):
        return math.exp(-self.wien_A*math.exp(u))

    def H(self,eta):
        p=self.cos
        rad=p['photon_omega_prefactor']*p['T0_K']**4*(1+p['neutrino_factor']*p['Nnueff'])
        return p['H_prefactor_s_inv']*math.sqrt(p['omh2']*math.exp(-3*eta)+p['odeh2']+rad*math.exp(-4*eta))

    def nH(self,eta):
        p=self.cos
        return p['nH0_prefactor_m3']*p['obh2']*(1-p['Y'])*math.exp(-3*eta)

    def integrate(self):
        nodes, weights = np.polynomial.legendre.leggauss(24)
        totals={3:[],4:[]}; bounds=[]; dt=[]; crossing_work=[]
        for a,b in zip(self.edges[:-1],self.edges[1:]):
            fa,fb=self.departure(a),self.departure(b)
            lower=physical_bound(a,b,fa,fb,self.wien)
            j=bisect.bisect_right(self.knots,(a+b)/2)-1
            source_right_u=(self.packet['incoming']['source_indices'][j+1]-self.k)*self.h
            source_margin=a-source_right_u
            if not source_margin>0:
                raise ValueError('strict-past segment interpolation endpoint not certified')
            bounds.append(dict(u_start=a,u_end=b,departure_start=fa,departure_end=fb,physical_trace_lower_bound=lower,
                source_right_endpoint_u=source_right_u,arrival_min_minus_source_right_eta=source_margin))
            u=(a+b)/2+(b-a)/2*nodes
            for power in [3,4]:
                wien=(b-a)/2*math.fsum(float(w)*math.exp(power*float(t))*self.wien(float(t)) for t,w in zip(u,weights))
                totals[power].append(exp_linear_integral(a,b,fa,fb,power)+wien)
            crossing_work.append((b-a)/2*math.fsum(float(w)*math.exp(3*float(t))*math.expm1(float(t))*(self.departure(float(t))+self.wien(float(t))) for t,w in zip(u,weights)))
            dt.append((b-a)/2*math.fsum(float(w)/self.H(self.eta_ref+float(t)) for t,w in zip(u,weights)))
        I3,I4=math.fsum(totals[3]),math.fsum(totals[4])
        N=self.G*I3; U=self.G*self.E_J*I4
        if N<0 or U<0 or not math.isfinite(N+U):
            raise ValueError('nonphysical finite photon inventory')
        return dict(N_in_m3=N,U0_J_m3=U,capacity_mu_m3=self.G*math.expm1(3*self.h)/3,
                    proper_duration_s=math.fsum(dt),crossing_redshift_work_J_m3=self.G*self.E_J*math.fsum(crossing_work),segments=bounds,integrals={3:I3,4:I4})

    def transport(self,N,U):
        R=diagonal_bound([self.h]*3,None)
        D=determinant_bound(self.h,None,beta_exactly_stf=True)
        r=float(R['Rhat_diagonal'][0]); det=D['Dhat']
        N1=det*N; U1=det*r*U
        return dict(R_diagonal=R['Rhat_diagonal'].tolist(),detR=det,N1_m3=N1,U1_J_m3=U1,
            number_relative_residual=(N1-math.exp(-3*self.h)*N)/N,
            energy_relative_residual=(U1-math.exp(-4*self.h)*U)/U,
            signed_propagation_energy_change_per_V0_J_m3=math.expm1(-self.h)*U,
            physical_map_radius=None)


def require_atomic_interval(packet):
    required=['x1s_interval','xr_p_interval','opacity_interval','atomic_stock_refill_ledger','internal_energy_recoil_owner']
    if packet is None or any(packet.get(k) is None for k in required):
        raise ValueError('ATOMIC_INPUT_OPEN: actual same-tube atomic interval and stock/refill owner required')
    return packet


def load():
    return NativeTube(json.loads((ROOT/'inputs/FINITE_TUBE_INPUT_SLICE.json').read_text()))
