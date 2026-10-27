"""Independent 70-digit quadrature on the exact represented native inputs."""
import mpmath as mp


def evaluate(packet):
    with mp.workdps(70):
        def hx(s):
            n,d=float.fromhex(s).as_integer_ratio()
            return mp.mpf(n)/d
        def q(x):
            if isinstance(x,int): return mp.mpf(x)
            n,d=float(x).as_integer_ratio()
            return mp.mpf(n)/d
        s,i,p=packet['selection'],packet['incoming'],packet['native_cosmology']
        k=s['cell_indices'][0]; h=hx(s['dlna_hex']); eta0=hx(s['eta0_hex'])+k*h
        E,Es=hx(i['target_energy_eV_hex']),hx(i['source_energy_eV_hex'])
        lag=mp.log(Es/E)
        knots=[(j-k)*h+lag for j in i['source_indices']]
        values=[hx(x) for x in i['departure_hex']]
        edges=[mp.mpf(0)]+[x for x in knots if 0<x<h]+[h]
        A=E*mp.exp(eta0)*q(p['fsR'])**2*q(p['meR'])/(q(p['kBoltz_eV_K'])*q(p['T0_K']))
        def f(u):
            j=next(j for j in range(len(knots)-1) if knots[j]<=u<=knots[j+1])
            t=(u-knots[j])/(knots[j+1]-knots[j])
            return values[j]*(1-t)+values[j+1]*t+mp.exp(-A*mp.exp(u))
        G=3*10**6*q(p['LYA_FACT_cm3_inv']); EJ=E*q(p['EV_J'])
        N=G*mp.fsum(mp.quad(lambda u:mp.exp(3*u)*f(u),[a,b]) for a,b in zip(edges[:-1],edges[1:]))
        U=G*EJ*mp.fsum(mp.quad(lambda u:mp.exp(4*u)*f(u),[a,b]) for a,b in zip(edges[:-1],edges[1:]))
        rad=q(p['photon_omega_prefactor'])*q(p['T0_K'])**4*(1+q(p['neutrino_factor'])*q(p['Nnueff']))
        def H(u):
            eta=eta0+u
            return q(p['H_prefactor_s_inv'])*mp.sqrt(q(p['omh2'])*mp.exp(-3*eta)+q(p['odeh2'])+rad*mp.exp(-4*eta))
        dt=mp.quad(lambda u:1/H(u),[0,h])
        stored=[hx(x) for x in s['eta_endpoint_hex']]
        return dict(N_in_m3=mp.nstr(N,65),U0_J_m3=mp.nstr(U,65),proper_duration_s=mp.nstr(dt,65),
            precision_decimal_digits=70,eta_ref_exact=mp.nstr(eta0,65),delta_eta_exact=mp.nstr(h,65),
            lag_exact=mp.nstr(lag,65),stored_minus_affine_eta=[mp.nstr(stored[j]-(eta0+j*h),65) for j in range(2)],
            split_u_exact=[mp.nstr(x,65) for x in edges],method='independent mpmath piecewise quadrature; exact binary64 inputs as integer ratios')
