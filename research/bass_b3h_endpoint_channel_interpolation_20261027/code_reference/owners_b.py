"""Finite MP event inventories and explicit radiation/thermal energy owners."""
from mp_b import *

def exp_moment3(a,b,k):
    def primitive(E):return -mp.exp(-k*E)*(E**3/k+3*E**2/k**2+6*E/k**3+6/k**4)
    return primitive(b)-primitive(a)
def poly_moment(a,b,x,y,left,right):
    slope=(y-x)/(b-a);intercept=x-slope*a
    return intercept*(right**4-left**4)/4+slope*(right**5-left**5)/5

def spectral_owner(knot,op,c,h):
    E=c['energies'];dep=knot['average_virtual'];TR=op['TR'];E21=c['E21'];EV=c['eV_J'];Kgamma=c['G']/E21**3
    bb=mp.pi**4*TR**4/15;PL=ZERO;mins=[]
    for j,(a,b) in enumerate(zip(E[:-1],E[1:])):
        x,y=dep[j:j+2];slope=(y-x)/(b-a);candidates=[a,b]
        if slope>0:
            candidate=-TR*mp.log(TR*slope)
            if a<candidate<b:candidates.append(candidate)
        vals=[x+slope*(t-a)+mp.exp(-t/TR) for t in candidates];minimum=min(vals);mins.append(minimum)
        check(f'spectral bin{j} analytic positivity',minimum>=0,minimum)
        PL+=poly_moment(a,b,x,y,a,b)
    # Planck-Wien is a positive exponentially convergent series, integrated
    # analytically with an explicit positive geometric tail bound.
    correction=ZERO;tail=None
    for n in range(2,100):
        correction+=exp_moment3(E[0],E[-1],n/TR)
        tail=exp_moment3(E[0],E[-1],(n+1)/TR)/(1-mp.exp(-E[0]/TR))
        if tail<=ARITH*bb:break
    else:raise ValueError('spectral Planck series tail unresolved')
    shell_left=E21;shell_right=E21*mp.exp(h);shell=ZERO;shellpieces=[]
    for j,(a,b) in enumerate(zip(E[:-1],E[1:])):
        lo=max(a,shell_left);hi=min(b,shell_right)
        if lo<hi:
            val=poly_moment(a,b,dep[j],dep[j+1],lo,hi)+exp_moment3(lo,hi,1/TR);shell+=val;shellpieces.append(dict(bin=j,left=lo,right=hi,energy_moment=val))
    check('selected Lyalpha shell inside represented spectrum',E[0]<shell_left<shell_right<E[-1])
    initial=Kgamma*EV*(bb+PL-correction-shell);error=Kgamma*EV*tail+ARITH*Kgamma*EV*(bb+abs(PL)+correction+shell)
    check('positive finite ambient radiation stock excluding selected shell',initial>error,[initial,error])
    return dict(Uambient0=initial,error=error,Kgamma=Kgamma,Planck_total_moment=bb,PL_departure_moment=PL,
      Wien_minus_Planck_moment=-correction,positive_series_tail_bound=tail,series_last_n=n,
      removed_selected_shell_moment=shell,shell_pieces=shellpieces,bin_occupation_lower_bounds=mins,
      model='Planck outside actual energy nodes; PL saved mean departure plus source Wien inside; selected Lyalpha shell removed once',
      physical_spectral_radius=None)

def owners(model,fin,clock,op,knot,c):
    NH=clock.NH;EV=c['eV_J'];EI=c['EI'];E21=c['E21'];p0=fin['p0'];p1=fin['p1'];Ip=fin['Ip'];S=fin['weighted'][0]['S']
    initial=mp.matrix([NH*(1-op['xHII']-p0[0]-p0[1]),NH*p0[0],NH*p0[1],NH*op['xHII']]);delta=mp.matrix([0,0,0,0]);q=mp.matrix([0,0,0,0]);q1=mp.matrix([0,0,0,0]);q2=mp.matrix([0,0,0,0])
    gross_count=[ZERO]*4;debits=[ZERO]*4;energydebit=[ZERO]*4;energyerror=[ZERO]*4;count_error=[ZERO]*4
    rows=[];groups={};weighted_energy_errors={1:[ZERO]*4,2:[ZERO]*4}
    for ch in model['maps']:
        ell=mp.matrix([ch['ell']]);count=NH*(ch['a']*S+(ell*Ip)[0]);propensity(count)
        error=NH*(abs(ch['a'])*fin['weighted'][0]['S_error']+norm(ch['ell'])*fin['Ip_error'])+ARITH*abs(count)
        counts={0:count};weighted_errors={}
        for k in [1,2]:
            wi=fin['weighted'][k];counts[k]=NH*(ch['a']*wi['S']+(ell*wi['Ip'])[0])
            weighted_errors[k]=NH*(abs(ch['a'])*wi['S_error']+norm(ch['ell'])*wi['Ip_error'])+ARITH*abs(counts[k])
        ee=mp.matrix(ch['energy_eV']);nu=mp.matrix(ch['stoich']);delta+=nu*count;q+=ee*count*EV;q1+=ee*counts[1]*EV;q2+=ee*counts[2]*EV
        for i in range(4):
            gross_count[i]+=abs(nu[i])*count;debits[i]+=max(-nu[i],0)*count;count_error[i]+=abs(nu[i])*error
            energydebit[i]+=max(-ee[i],0)*count*EV;energyerror[i]+=abs(ee[i])*error*EV
            for k in [1,2]:weighted_energy_errors[k][i]+=abs(ee[i])*weighted_errors[k]*EV
        check_energy=abs(sum(ee));
        if check_energy>ARITH*max(norm(ee),m('1e-100')):raise ValueError('event energy ownership mismatch '+ch['name'])
        row=dict(**ch,count=count,count_error=error,weighted_count_k1=counts[1],weighted_count_k2=counts[2],weighted_count_errors=weighted_errors,event_energy_J=ee*count*EV)
        rows.append(row);group=groups.setdefault(ch['kind'],dict(count=ZERO,atomic_change=mp.matrix([0,0,0,0]),energy_J=mp.matrix([0,0,0,0])))
        group['count']+=count;group['atomic_change']+=nu*count;group['energy_J']+=ee*count*EV
    # Direct Lyalpha is time-dependent only in its known positive incoming map.
    Nout=NH*Ip[1];Nin=clock.Nin;net=Nout-Nin;nu=mp.matrix([1,0,-1,0]);ee=mp.matrix([-E21,0,0,E21]);delta+=nu*net;q+=ee*net*EV
    outErr=NH*fin['Ip_error'];inErr=clock.inherited_errors['Nin']
    for i in range(4):
        gross_count[i]+=abs(nu[i])*(Nout+Nin);debits[i]+=max(-nu[i],0)*Nout+max(nu[i],0)*Nin;count_error[i]+=abs(nu[i])*(outErr+inErr)
        energydebit[i]+=max(-ee[i],0)*Nout*EV+max(ee[i],0)*Nin*EV;energyerror[i]+=abs(ee[i])*(outErr+inErr)*EV
    Uout0=NH*c['E21_J']*fin['weighted'][1]['Ip'][1]
    # q1,q2 Lyalpha are not used for ambient/gas propagation; those slots remain
    # separately identified to avoid introducing duplicated photon credits.
    groups['Lyalpha']=dict(down_count=Nout,up_count=Nin,net_count=net,atomic_change=nu*net,energy_J=ee*net*EV)
    final=initial+delta;storage=NH*(p1-p0);storage_error=NH*fin['p1_error'];storage_res=mp.matrix([delta[1]-storage[0],delta[2]-storage[1]])
    for i in range(2):
        allowed=count_error[i+1]+storage_error+ARITH*gross_count[i+1]
        check(f'interface{i} storage count resolved identity',abs(storage_res[i])<=allowed and abs(storage_res[i])<=m('1e-8')*abs(storage[i]),dict(residual=storage_res[i],storage=storage[i],derived_bound=allowed),m('1e-8'))
    check('finite continuum and electron gross debit margin',initial[3]>debits[3]+count_error[3],dict(initial=initial[3],gross_debit=debits[3],error=count_error[3]))
    check('finite ground gross debit margin',initial[0]>debits[0]+count_error[0],dict(initial=initial[0],gross_debit=debits[0],error=count_error[0]))
    check('all final finite stocks positive',min(final)>0,final)
    check('total hydrogen inventory exact conservation',abs(sum(final)-NH)<=ARITH*NH,sum(final)-NH,ARITH*NH)
    atom0=(EI*initial[3]+E21*(initial[1]+initial[2]))*EV;atom1com=(EI*final[3]+E21*(final[1]+final[2]))*EV
    check('atom energy from actual finite stocks',abs((atom1com-atom0)-q[0])<=ARITH*(abs(atom0)+abs(atom1com)+sum(abs(x['event_energy_J'][0]) for x in rows)),(atom1com-atom0)-q[0])
    fHe=m(c['fHe']);gas0=m('1.5')*NH*(1+fHe+op['xe'])*op['Tm']*EV;rest0=NH*c['mH']*(1+m(3.97153)*fHe)*EV
    spectrum=spectral_owner(knot,op,c,clock.h);ambient0=spectrum['Uambient0'];Uin0=clock.Uin
    gas_weighted_debit=mp.exp(2*clock.h)*(energydebit[1]+energyerror[1]);ambient_weighted_debit=mp.exp(clock.h)*(energydebit[2]+energyerror[2])
    check('gas throughout-step weighted gross energy debit margin',gas0>gas_weighted_debit,dict(initial=gas0,unweighted_gross_debit=energydebit[1],error=energyerror[1],conservative_weighted_debit=gas_weighted_debit))
    check('ambient throughout-step weighted gross energy debit margin',ambient0>spectrum['error']+ambient_weighted_debit,dict(initial=ambient0,unweighted_gross_debit=energydebit[2],error=energyerror[2],conservative_weighted_debit=ambient_weighted_debit))
    h=clock.h;initial_energy=[rest0,atom0,gas0,ambient0,Uin0]
    final_energy=[mp.exp(-3*h)*rest0,mp.exp(-3*h)*atom1com,mp.exp(-5*h)*(gas0+q2[1]),mp.exp(-4*h)*(ambient0+q1[2]),mp.exp(-4*h)*Uout0]
    propagated_errors=[ARITH*rest0,mp.exp(-3*h)*energyerror[0],mp.exp(-5*h)*weighted_energy_errors[2][1],mp.exp(-4*h)*(spectrum['error']+weighted_energy_errors[1][2]),mp.exp(-4*h)*NH*c['E21_J']*fin['weighted'][1]['Ip_error']]
    event_energy=[ZERO,q[0],q[1],q[2],q[3]];Vratio=mp.exp(3*h);final_common=[Vratio*x for x in final_energy]
    # Independently derived adiabatic work in the common V0, rather than a
    # subtraction of densities at unequal volumes. Dust/internal have no work.
    work=[ZERO,ZERO,mp.expm1(-2*h)*gas0+mp.exp(-2*h)*q2[1]-q[1],
      mp.expm1(-h)*ambient0+mp.exp(-h)*q1[2]-q[2],
      mp.expm1(-h)*Uin0+mp.exp(-h)*(Uout0-Uin0)-q[3]]
    work_errors=[ZERO,ZERO,abs(mp.expm1(-2*h))*ARITH*gas0+mp.exp(-2*h)*weighted_energy_errors[2][1]+energyerror[1],
      abs(mp.expm1(-h))*spectrum['error']+mp.exp(-h)*weighted_energy_errors[1][2]+energyerror[2],
      mp.exp(-h)*(NH*c['E21_J']*fin['weighted'][1]['Ip_error']+clock.inherited_errors['Uin'])+clock.inherited_errors['Uin']+energyerror[3]]
    grossenergy=sum(abs(x) for x in event_energy);eventres=sum(event_energy)
    check('five-sector finite event energies sum zero before conversion',abs(eventres)<=ARITH*grossenergy,dict(residual=eventres,gross=grossenergy),ARITH)
    check('all propagated sector energies positive with conditional numerical margins',all(x>e for x,e in zip(final_energy,propagated_errors)),dict(values=final_energy,conditional_errors=propagated_errors))
    totalres=sum(final_common)-sum(initial_energy)-sum(work)-sum(event_energy)
    work_identity_bound=sum(work_errors)+Vratio*sum(propagated_errors)+ARITH*(sum(initial_energy)+sum(final_common))
    check('common V0 total event plus independently adiabatic geometry-work identity',abs(totalres)<=work_identity_bound,dict(residual=totalres,conditional_bound=work_identity_bound))
    clock_identity(Nout,NH*fin['Ip'][1]);clock_identity(Uout0,NH*c['E21_J']*fin['weighted'][1]['Ip'][1]);check('outgoing native clock count and weighted energy identities',True)
    return dict(inventory_order=['ground','2s','2p','continuum'],initial_stocks=initial,final_stocks=final,electrons_initial=initial[3],electrons_final=final[3],
      stock_change_from_events=delta,interface_storage=storage,interface_storage_residual=storage_res,interface_endpoint_error=storage_error,
      gross_debits=debits,gross_stoichiometric_scales=gross_count,derived_count_errors=count_error,channel_counts=rows,channel_groups=groups,
      sector_order=['rest_dust','atomic_internal','gas_thermal','ambient_radiation','outgoing_Lyalpha'],initial_sector_energy_J_m3=initial_energy,
      final_sector_energy_J_m3=final_energy,event_sector_energy_J_m3=event_energy,geometry_work_J_m3=work,
      final_sector_energy_common_V0_J_m3=final_common,right_volume_ratio=Vratio,geometry_work_conditional_errors=work_errors,geometry_work_identity_bound=work_identity_bound,
      throughout_step_weighted_energy_debit_bounds=dict(gas=gas_weighted_debit,ambient=ambient_weighted_debit),
      event_energy_sum_residual=eventres,total_energy_work_identity_residual=totalres,
      weighted_nonLya_sector_events_k1=q1,weighted_nonLya_sector_events_k2=q2,unweighted_sector_energy_error=energyerror,
      weighted_sector_energy_errors=weighted_energy_errors,conditional_propagated_energy_errors=propagated_errors,
      Nout_new=Nout,Uout0_new=Uout0,Nout1_new=mp.exp(-3*h)*Nout,Uout1_new=final_energy[-1],Nin_reused=Nin,Uin0_reused=Uin0,
      spectral_owner=spectrum,gas_thermal_owner='relative-motion gas+ions+electrons with inert source He; no extra 3Tm/2 subtraction',
      direct_Lya_recoil=ZERO,virtual_boundary_energy_credited_twice=False,physical_radii=dict(eS=None,en=None,eE=None,geometry=None,temporal=None,total=None))
