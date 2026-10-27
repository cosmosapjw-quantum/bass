"""Finite tagged-channel inventories; no old solver or spectral preparation.

All new bounds are conditional on the admitted saved inputs and the declared
MP70 arithmetic allowance.  Historical incoming quadrature errors stay null.
"""
from mp_b import *


def _column(values):
    return mp.matrix([m(x[0] if isinstance(x, list) else x) for x in values])


def _row_dot(row, column):
    return mp.fsum(row[i]*column[i] for i in range(2))


def _tag_count(ch, weight, fin, tag):
    """A6/A8, with the row infinity norm dual to a one-norm I error."""
    z=fin['moments'][f'k{weight}_j0'];o=fin['moments'][f'k{weight}_j1']
    if tag==0:
        F=z['F']-o['F'];I=z['I']-o['I']
        Fe=z['F_error']+o['F_error'];Ie=z['I_error']+o['I_error']
        # Cancellation arithmetic is charged to both original moments.
        Fgross=abs(z['F'])+abs(o['F'])
        Igross=[abs(z['I'][i])+abs(o['I'][i]) for i in range(2)]
    else:
        F=o['F'];I=o['I'];Fe=o['F_error'];Ie=o['I_error']
        Fgross=abs(F);Igross=[abs(I[i]) for i in range(2)]
    NH=fin['NH_reference'];ell=ch['ell'];a=ch['a']
    count=NH*(a*F+_row_dot(ell,I))
    gross=NH*(abs(a)*Fgross+mp.fsum(abs(ell[i])*Igross[i] for i in range(2)))
    error=NH*(abs(a)*Fe+max(abs(x) for x in ell)*Ie)+ARITH*gross
    return count,error,gross


def assemble_owners(data, maps, fin):
    """Use one shared set of F/I moments for every endpoint-tagged owner."""
    c=data['constants'];EV=c['eV_J'];EI=c['EI'];E21=c['E21']
    NH=fin['NH_reference'];h=fin['h'];p0=fin['p0'];p1=fin['p1']
    prepared=data['initial_prepared_owner'];spectrum=data['initial_spectral_owner_reused']
    initial=_column(prepared['initial_stocks'])
    initial_energy=[m(x) for x in prepared['initial_sector_energy_J_m3']]
    spectrum_error=m(spectrum['error'])
    check('prepared finite initial stocks match admitted absolute IC',
          all(abs(initial[i+1]-NH*p0[i])<=ARITH*(abs(initial[i+1])+NH*abs(p0[i])) for i in range(2)),
          dict(initial_excited=[initial[1],initial[2]],NH_p0=NH*p0))
    check('prepared initial hydrogen inventory matches common NH',abs(sum(initial)-NH)<=ARITH*NH,sum(initial)-NH,ARITH*NH)
    check('prepared ambient energy is reused spectral stock',
          abs(initial_energy[3]-m(spectrum['Uambient0']))<=ARITH*abs(initial_energy[3]))
    delta=mp.zeros(4,1);q={k:mp.zeros(4,1) for k in range(3)}
    energy_errors={k:[ZERO]*4 for k in range(3)}
    energy_gross={k:[ZERO]*4 for k in range(3)}
    gross_count=[ZERO]*4;debits=[ZERO]*4;debit_errors=[ZERO]*4
    count_error=[ZERO]*4;energydebit=[ZERO]*4;energydebit_error=[ZERO]*4
    rows=[];tagged_rows=[];groups={};positivity=[];tag_energy_checks=[]
    for left,right in zip(maps['left'],maps['right']):
        aggregate_count=ZERO;aggregate_error=ZERO;aggregate_energy=mp.zeros(4,1)
        aggregate_weighted={k:ZERO for k in range(3)}
        aggregate_weighted_error={k:ZERO for k in range(3)}
        tags=[]
        for tag,ch in enumerate((left,right)):
            counts={};errors={};grosses={}
            for k in range(3):
                counts[k],errors[k],grosses[k]=_tag_count(ch,k,fin,tag)
                positivity.append((counts[k],errors[k]))
            count=counts[0];error=errors[0];nu=mp.matrix(ch['stoich']);ee=mp.matrix(ch['energy_eV'])
            tag_energy_checks.append(abs(sum(ee))<=ARITH*max(norm(ee),m('1e-100')))
            delta+=nu*count
            for k in range(3):
                q[k]+=ee*counts[k]*EV
                aggregate_weighted[k]+=counts[k];aggregate_weighted_error[k]+=errors[k]
                for i in range(4):
                    energy_errors[k][i]+=abs(ee[i])*errors[k]*EV
                    energy_gross[k][i]+=abs(ee[i])*grosses[k]*EV
            for i in range(4):
                gross_count[i]+=abs(nu[i])*grosses[0]
                debits[i]+=max(-nu[i],0)*count;debit_errors[i]+=max(-nu[i],0)*error
                count_error[i]+=abs(nu[i])*error
                energydebit[i]+=max(-ee[i],0)*count*EV
                energydebit_error[i]+=max(-ee[i],0)*error*EV
            event=ee*count*EV;aggregate_count+=count;aggregate_error+=error;aggregate_energy+=event
            row=dict(**ch,endpoint_tag=tag,count=count,count_error=error,
                     conditional_count_lower=count-error,weighted_count_k1=counts[1],weighted_count_k2=counts[2],
                     weighted_count_errors={1:errors[1],2:errors[2]},arithmetic_gross_count_scales=grosses,
                     event_energy_J=event)
            tags.append(row);tagged_rows.append(row)
        rows.append(dict(name=left['name'],kind=left['kind'],stoich=left['stoich'],
                         count=aggregate_count,count_error=aggregate_error,event_energy_J=aggregate_energy,
                         weighted_count_k1=aggregate_weighted[1],weighted_count_k2=aggregate_weighted[2],
                         weighted_count_errors={1:aggregate_weighted_error[1],2:aggregate_weighted_error[2]},
                         endpoint_tags=tags))
        group=groups.setdefault(left['kind'],dict(count=ZERO,count_error=ZERO,atomic_change=mp.zeros(4,1),energy_J=mp.zeros(4,1)))
        group['count']+=aggregate_count;group['count_error']+=aggregate_error
        group['atomic_change']+=mp.matrix(left['stoich'])*aggregate_count;group['energy_J']+=aggregate_energy
    check('all 2828 endpoint tags have nonnegative weighted counts with conditional margins',
          all(value>=error for value,error in positivity),
          dict(tags=len(tagged_rows),weighted_tag_counts=len(positivity),minimum_count_lower=min(value-error for value,error in positivity)))
    check('each endpoint energy tag sums to zero',all(tag_energy_checks),dict(tags=len(tag_energy_checks)))

    incoming_meta=data['prior']['finite_solution']['clock']['inherited_saved_reference_uncertainty']
    Nin=fin['Nin_saved'];Uin=fin['Uin_saved']
    in_error=m(incoming_meta['Nin']);uin_error=m(incoming_meta['Uin'])
    alpha0=fin['direct_alpha']['k0'];alpha1=fin['direct_alpha']['k1']
    Nout=NH*alpha0['I'];out_error=NH*alpha0['I_error']+ARITH*abs(Nout)
    Uout=NH*c['E21_J']*alpha1['I'];uout_error=NH*c['E21_J']*alpha1['I_error']+ARITH*abs(Uout)
    check('direct Lyalpha outgoing finite moments positive with conditional margin',Nout>out_error and Uout>uout_error,
          dict(Nout=Nout,Nout_error=out_error,Uout0=Uout,Uout0_error=uout_error))
    net=Nout-Nin;nu=mp.matrix([1,0,-1,0]);ee=mp.matrix([-E21,0,0,E21])
    delta+=nu*net;q[0]+=ee*net*EV
    for i in range(4):
        gross_count[i]+=abs(nu[i])*(Nout+Nin)
        debits[i]+=max(-nu[i],0)*Nout+max(nu[i],0)*Nin
        debit_errors[i]+=max(-nu[i],0)*out_error+max(nu[i],0)*in_error
        count_error[i]+=abs(nu[i])*(out_error+in_error)
        energydebit[i]+=(max(-ee[i],0)*Nout+max(ee[i],0)*Nin)*EV
        energydebit_error[i]+=(max(-ee[i],0)*out_error+max(ee[i],0)*in_error)*EV
        energy_errors[0][i]+=abs(ee[i])*(out_error+in_error)*EV
        energy_gross[0][i]+=abs(ee[i])*(Nout+Nin)*EV
    groups['Lyalpha']=dict(down_count=Nout,up_count=Nin,net_count=net,down_count_error=out_error,
                          up_count_representation_error=in_error,atomic_change=nu*net,energy_J=ee*net*EV,
                          inherited_quadrature_remainder=None)
    final=initial+delta;storage=NH*(p1-p0);storage_error=NH*fin['p1_error']
    storage_res=mp.matrix([delta[i+1]-storage[i] for i in range(2)]);storage_checks=[]
    for i in range(2):
        allowed=count_error[i+1]+storage_error+ARITH*(gross_count[i+1]+abs(initial[i+1])+abs(NH*p1[i]))
        relative=allowed/abs(storage[i]) if storage[i] else None
        record=dict(residual=storage_res[i],storage=storage[i],derived_bound=allowed,
                    bound_relative_to_nonzero_storage=relative,absolute_target=m('1e-16'),relative_target=m('1e-8'))
        check(f'interface{i} storage resolved against actual propagated bound',
              abs(storage_res[i])<=allowed and allowed<=m('1e-16') and (relative is None or relative<=m('1e-8')),record)
        storage_checks.append(record)
    check('endpoint fraction one-norm bound',fin['p1_error']<=m('1e-34'),fin['p1_error'],m('1e-34'))
    for index,label in ((0,'ground'),(3,'continuum and electron')):
        check('finite '+label+' gross debit margin',initial[index]>debits[index]+debit_errors[index],
              dict(initial=initial[index],gross_debit=debits[index],error=debit_errors[index]))
    final_stock_errors=[count_error[i]+ARITH*(abs(initial[i])+gross_count[i]) for i in range(4)]
    check('final finite ground continuum and electron positive with margins',
          all(final[i]>final_stock_errors[i] for i in (0,3)),dict(final=final,conditional_errors=final_stock_errors))
    check('excited final stocks positive by ODE endpoint and event balance',
          all(NH*p1[i]>storage_error and final[i+1]>0 for i in range(2)),
          dict(ODE_excited=NH*p1,ODE_error=storage_error,event_excited=[final[1],final[2]]))
    check('total hydrogen inventory conservation from common event stoichiometry',
          abs(sum(final)-NH)<=ARITH*(NH+sum(gross_count)),sum(final)-NH)
    atom0=initial_energy[1];atom1=(EI*final[3]+E21*(final[1]+final[2]))*EV
    atom_identity_bound=ARITH*(abs(atom0)+abs(atom1)+energy_gross[0][0])
    check('atomic internal energy matches actual finite-stock changes',abs(atom1-atom0-q[0][0])<=atom_identity_bound,
          dict(residual=atom1-atom0-q[0][0],bound=atom_identity_bound))

    rest0,_,gas0,ambient0,prepared_uin=initial_energy
    check('prepared selected incoming line energy matches reused value',abs(prepared_uin-Uin)<=uin_error+ARITH*abs(Uin))
    gas_debit=mp.exp(2*h)*(energydebit[1]+energydebit_error[1])
    ambient_debit=mp.exp(h)*(energydebit[2]+energydebit_error[2])
    check('gas throughout-step weighted gross debit margin',gas0>gas_debit,dict(initial=gas0,weighted_gross_debit=gas_debit))
    check('ambient throughout-step weighted gross debit margin',ambient0>spectrum_error+ambient_debit,
          dict(initial=ambient0,prepared_error=spectrum_error,weighted_gross_debit=ambient_debit))
    final_energy=[mp.exp(-3*h)*rest0,mp.exp(-3*h)*atom1,
                  mp.exp(-5*h)*(gas0+q[2][1]),mp.exp(-4*h)*(ambient0+q[1][2]),
                  mp.exp(-4*h)*(Uout+q[1][3])]
    # The line sector's saved incoming preparation is removed by its explicit
    # incoming debit and replaced by the new outgoing weighted count.
    propagated=[ARITH*abs(final_energy[0]),
                mp.exp(-3*h)*energy_errors[0][0],
                mp.exp(-5*h)*energy_errors[2][1],
                mp.exp(-4*h)*(spectrum_error+energy_errors[1][2]),
                mp.exp(-4*h)*(uout_error+energy_errors[1][3])]
    for i in range(5):propagated[i]+=ARITH*abs(final_energy[i])
    event=[ZERO]+list(q[0]);Vratio=mp.exp(3*h);final_common=[Vratio*x for x in final_energy]
    work=[ZERO,ZERO,
          mp.expm1(-2*h)*gas0+mp.exp(-2*h)*q[2][1]-q[0][1],
          mp.expm1(-h)*ambient0+mp.exp(-h)*q[1][2]-q[0][2],
          mp.expm1(-h)*Uin+mp.exp(-h)*(Uout-Uin+q[1][3])-q[0][3]]
    work_errors=[ZERO,ZERO,
                 abs(mp.expm1(-2*h))*ARITH*gas0+mp.exp(-2*h)*energy_errors[2][1]+energy_errors[0][1],
                 abs(mp.expm1(-h))*spectrum_error+mp.exp(-h)*energy_errors[1][2]+energy_errors[0][2],
                 abs(mp.expm1(-h))*uin_error+mp.exp(-h)*(uout_error+uin_error+energy_errors[1][3])+energy_errors[0][3]]
    for i in range(5):work_errors[i]+=ARITH*(abs(initial_energy[i])+abs(final_common[i])+abs(work[i])+abs(event[i]))
    event_res=sum(event);event_bound=ARITH*sum(energy_gross[0])
    check('five-sector tagged finite event energy sum',abs(event_res)<=event_bound,
          dict(residual=event_res,derived_arithmetic_bound=event_bound))
    check('propagated sector energies positive with conditional margins',all(x>e for x,e in zip(final_energy,propagated)),
          dict(values=final_energy,conditional_errors=propagated))
    work_res=sum(final_common)-sum(initial_energy)-sum(work)-sum(event)
    work_bound=sum(work_errors)+Vratio*sum(propagated)+sum(energy_errors[0])+ARITH*(sum(initial_energy)+sum(final_common))
    check('common V0 independently adiabatic geometry-work identity',abs(work_res)<=work_bound,
          dict(residual=work_res,conditional_bound=work_bound))
    return dict(inventory_order=['ground','2s','2p','continuum'],initial_stocks=initial,final_stocks=final,
                electrons_initial=initial[3],electrons_final=final[3],stock_change_from_events=delta,
                interface_storage=storage,interface_storage_residual=storage_res,interface_endpoint_error=storage_error,
                interface_storage_checks=storage_checks,gross_debits=debits,gross_debit_errors=debit_errors,
                gross_stoichiometric_scales=gross_count,derived_count_errors=count_error,conditional_final_stock_errors=final_stock_errors,
                channel_counts=rows,tagged_channel_counts=tagged_rows,channel_groups=groups,
                sector_order=['rest_dust','atomic_internal','gas_thermal','ambient_radiation','outgoing_Lyalpha'],
                initial_sector_energy_J_m3=initial_energy,final_sector_energy_J_m3=final_energy,
                event_sector_energy_J_m3=event,event_sector_energy_conditional_errors=[ZERO]+energy_errors[0],geometry_work_J_m3=work,
                final_sector_energy_common_V0_J_m3=final_common,right_volume_ratio=Vratio,
                geometry_work_conditional_errors=work_errors,geometry_work_identity_bound=work_bound,
                throughout_step_weighted_energy_debit_bounds=dict(gas=gas_debit,ambient=ambient_debit),
                event_energy_sum_residual=event_res,event_energy_arithmetic_bound=event_bound,
                total_energy_work_identity_residual=work_res,
                weighted_nonLya_sector_events_k1=q[1],weighted_nonLya_sector_events_k2=q[2],
                unweighted_sector_energy_error=energy_errors[0],weighted_sector_energy_errors={1:energy_errors[1],2:energy_errors[2]},
                conditional_propagated_energy_errors=propagated,Nout_new=Nout,Uout0_new=Uout,
                Nout1_new=mp.exp(-3*h)*Nout,Uout1_new=mp.exp(-4*h)*Uout,
                Nout_new_error=out_error,Uout0_new_error=uout_error,Nin_reused=Nin,Uin0_reused=Uin,
                inherited_saved_reference_uncertainty=incoming_meta,inherited_reference_quadrature_remainder=None,
                spectral_owner=spectrum,spectral_owner_reused=True,old_spectral_preparation_calls=0,
                initial_stock_preparation_reused=True,initial_sector_preparation_reused=True,
                gas_thermal_owner=prepared['gas_thermal_owner'],direct_Lya_recoil=ZERO,
                numerical_residual_entered_as_refill=False,virtual_boundary_energy_credited_twice=False,
                numerical_bound_qualification='analytic truncation plus declared MP arithmetic allowance, conditional on admitted saved input values',
                physical_radii=dict(eS=None,en=None,eE=None,geometry=None,temporal=None,total=None),global_radius=None,L4=False)
