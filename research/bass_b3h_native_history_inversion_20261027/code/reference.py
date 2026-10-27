"""Independent 70-digit reference: coth inversion and direct piecewise quadrature."""
import mpmath as mp

def exact(x):
    f=float.fromhex(x['binary64_hex']) if isinstance(x,dict) else float(x)
    a,b=f.as_integer_ratio()
    return mp.mpf(a)/b

def reconstruct(packet,lyman,tr):
    with mp.workdps(70):
        i=exact(tr['incoming_derived_from_saved_prefix']);v=exact(tr['average_stored']);o=exact(tr['outgoing_stored'])
        r=(v-i)/(o-i)
        def fn(t):return mp.mpf('.5')+mp.coth(t/2)/2-1/t
        lo=mp.mpf(0);hi=mp.mpf(1)
        while fn(hi)<r:hi*=2
        for _ in range(250):
            t=(lo+hi)/2
            if fn(t)<r:lo=t
            else:hi=t
        t=(lo+hi)/2
        c={k:exact(v) for k,v in packet['constants'].items()}
        # Native z is independently reproduced by binary64 source arithmetic;
        # reference coefficients evaluate the exact represented z and constants.
        a=1+exact(tr['native_z'])
        TR=c['kBoltz_eV_per_K']*c['T0_K']*a/(c['fsR']**2*c['meR'])
        nH=mp.mpf('1e-6')*c['nH0_coefficient']*c['obh2']*(1-c['Y'])*a**3
        rad=c['photon_density_coefficient']*c['T0_K']**4*a**4
        H=c['Hubble_coefficient_s_inv']*mp.sqrt(c['omh2']*a**3+c['okh2']*a**2+
          c['odeh2']*a**(3*(1+c['w0']))*mp.exp(3*c['wa']*(mp.log(a)-1+1/a))+
          rad+c['neutrino_coefficient']*rad*c['Nnueff'])
        row=next(x for x in packet['table_rows'] if x['bin']==tr['bin'])
        p={k:exact(v) for k,v in row['fields'].items()};E=p['Eb_eV'];rr=c['fsR']**8*c['meR']
        Cs=rr*p['A2s']/abs(mp.expm1((E-c['E21_eV'])/TR))
        Cp=rr/3*(mp.exp(-c['E32_eV']/TR)*p['A3s3d']/abs(mp.expm1((E-c['E31_eV'])/TR))+
           mp.exp(-c['E42_eV']/TR)*p['A4s4d']/abs(mp.expm1((E-c['E41_eV'])/TR)))
        G=mp.exp((E-c['E21_eV'])/TR)*(Cs+3*Cp)
        lam=c['hPc_eV_cm']/E/c['fsR']**2/c['meR']
        x=t*8*mp.pi*H/(G*lam**3*nH)
        ly=next(x for x in lyman['records'] if x['index']==tr['index'])
        da,db,dg=[exact(x) for x in ly['outgoing_lyman_departures']]
        yp=3*da;ysb=db*mp.exp(c['E32_eV']/TR);ysg=dg*mp.exp(c['E42_eV']/TR)
        feq=i+(o-i)/(-mp.expm1(-t));ysv=(G*feq-Cp*yp)/Cs
        vals=dict(tau=t,x1s=x,Gamma=G,TR_eV=TR,nH_cm3=nH,H_s_inv=H,
          ys_beta=ysb,ys_gamma=ysg,ys_virtual=ysv,
          x2s=x*(ysb+mp.exp(-c['E21_eV']/TR)),x2p=x*(yp+3*mp.exp(-c['E21_eV']/TR)))
        return {**{k:mp.nstr(v,65) for k,v in vals.items()},'precision_decimal_digits':70,
          'method':'independent coth bisection; exact binary64 input ratios; independent coefficient expressions'}

def net(packet,lyman,saved):
    with mp.workdps(70):
        s=packet['selection'];p=packet['incoming'];c=packet['native_cosmology'];k=s['cell_indices'][0]
        h=exact(float.fromhex(s['dlna_hex']))
        E=exact(float.fromhex(p['target_energy_eV_hex']));Es=exact(float.fromhex(p['source_energy_eV_hex']))
        lag=mp.log(Es/E);knots=[(n-k)*h+lag for n in p['source_indices']]
        vals=[exact(float.fromhex(x)) for x in p['departure_hex']]
        out=[exact(x['outgoing_lyman_departures'][0]) for x in lyman['records']]
        edges=[mp.mpf(0)]+[x for x in knots if 0<x<h]+[h]
        def j(u):
            n=next(n for n in range(len(knots)-1) if knots[n]<=u<=knots[n+1])
            f=vals[n]+(vals[n+1]-vals[n])*(u-knots[n])/(knots[n+1]-knots[n])
            return out[0]+(out[1]-out[0])*u/h-f
        I={n:mp.fsum(mp.quad(lambda u:mp.exp(n*u)*j(u),[a,b]) for a,b in zip(edges[:-1],edges[1:])) for n in [3,4]}
        G=3*10**6*exact(c['LYA_FACT_cm3_inv']);EJ=E*exact(c['EV_J'])
        dn=G*I[3];du=G*EJ*I[4]
        nin=mp.mpf(saved['independent_reference']['N_in_m3']);uin=mp.mpf(saved['independent_reference']['U0_J_m3'])
        vals=dict(DeltaN0=dn,DeltaU0=du,I3=I[3],I4=I[4],
          Nout0=nin+dn,Uout0=uin+du,Nout1=mp.exp(-3*h)*(nin+dn),Uout1=mp.exp(-4*h)*(uin+du))
        return {**{k:mp.nstr(v,65) for k,v in vals.items()},'precision_decimal_digits':70,
                'split_u':[mp.nstr(x,65) for x in edges], 'method':'independent direct 70-digit piecewise quadrature of signed net trace'}
