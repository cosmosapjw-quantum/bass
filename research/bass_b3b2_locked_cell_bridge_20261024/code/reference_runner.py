"""Bounded direct-sum experiments and labelled rejected mutations."""
from dataclasses import replace
import csv
import json
import platform
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from locked_bridge import (C, EPS, SUM_TOL, ROUNDTRIP_TOL, ROOT, Units, load_actual_inputs,
                           to_packets, fixed_grid_inverse, state_boost, physical_sums,
                           packet_observables, residual)
from vendor import kinetic


def write_csv(path, rows):
    with path.open('w', newline='') as handle:
        writer=csv.DictWriter(handle, fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    out=ROOT/'artifacts'
    grid,f,diag=load_actual_inputs()
    units=Units(8*np.pi*6.67430e-11/C**4,1e20,5.45e-27)
    state=to_packets(grid,f,units)
    N,T,Ns,Ts=physical_sums(grid,f)
    actualN,actualT=packet_observables(state)
    fback=fixed_grid_inverse(state,grid)
    bridge=dict(number_current_residual=residual(actualN,N,Ns),stress_tensor_residual=residual(actualT,T,Ts),
                max_positive_f_roundtrip_relative=float(np.max(np.abs(fback/f-1))),
                exact_zero_f_preserved=bool(np.array_equal(fback[f==0],f[f==0])))
    assert bridge['number_current_residual'] <= SUM_TOL
    assert bridge['stress_tensor_residual'] <= SUM_TOL
    assert bridge['max_positive_f_roundtrip_relative'] <= ROUNDTRIP_TOL
    stock=[]
    for i,label in enumerate(grid.cell_labels):
        number=float(sum(grid.G[i]*grid.A[j]*f[i,j] for j in range(len(grid.A))))
        stock.append(dict(cell_label=label,energy_J=float(C*grid.p[i]),energy_eV=float(C*grid.p[i]/1.602176634e-19),
                          number_density_m3=number,energy_density_J_m3=float(C*grid.p[i]*number),
                          mode_measure_m3=float(grid.G[i]),angularly_isotropic=True))
    write_csv(out/'CELL_STOCK.csv',stock)
    covariance=[]
    scenarios={'actual_REC_isotropic_initial_data':f,
               'synthetic_anisotropic_perturbation_actual_grid':f*(1+.4*grid.directions[:,0]+.3*(3*grid.directions[:,2]**2-1)/2)[None,:]}
    for scenario,occupation in scenarios.items():
        original=to_packets(grid,occupation,units)
        n,t,ns,ts=physical_sums(grid,occupation)
        for chart,direction in (('axial',np.array([1.,0,0])),('nonaxial',np.array([2.,-3.,1.])/np.sqrt(14))):
            for speed in (0.,.1,.2,.3,.4,.5,.6,.7,.8):
                beta=speed*direction;B=kinetic.boost_matrix(beta)
                transformed=state_boost(original,beta)
                n_expected=B@n;t_expected=B@t@B.T
                nscale=np.abs(B)@ns;tscale=np.abs(B)@ts@np.abs(B.T)
                goodn,goodt=packet_observables(transformed)
                badn,badt=packet_observables(replace(transformed,w=original.w))
                restored=state_boost(transformed,-beta)
                recovered=fixed_grid_inverse(restored,grid)
                row=dict(scenario=scenario,boost_chart=chart,beta_magnitude=speed,
                         beta_x=float(beta[0]),beta_y=float(beta[1]),beta_z=float(beta[2]),
                         N_covariance_residual=residual(goodn,n_expected,nscale),
                         T_covariance_residual=residual(goodt,t_expected,tscale),
                         rejected_omitted_weight_N_residual=residual(badn,n_expected,nscale),
                         rejected_omitted_weight_T_residual=residual(badt,t_expected,tscale),
                         inverse_positive_f_relative=float(np.max(np.abs(recovered/occupation-1))))
                assert row['N_covariance_residual']<=SUM_TOL
                assert row['T_covariance_residual']<=SUM_TOL
                assert row['inverse_positive_f_relative']<=ROUNDTRIP_TOL
                if speed: assert row['rejected_omitted_weight_T_residual']>1e-5
                covariance.append(row)
    write_csv(out/'BOOST_COVARIANCE.csv',covariance)
    # Actual competing parent target energy; c*p remains the authority.
    wrong_grid=replace(grid,p=diag['target_energy_J']/C)
    wrongN,wrongT=packet_observables(to_packets(wrong_grid,f,units))
    mutation=[dict(mutation='actual_parent_target_energy_replaces_saved_cp_REJECTED',
                   photon_number_relative_residual=float((wrongN[0]-N[0])/N[0]),
                   energy_density_relative_residual=float((wrongT[0,0]-T[0,0])/T[0,0]),
                   N_L1_residual=residual(wrongN,N,Ns),T_L1_residual=residual(wrongT,T,Ts),
                   min_cell_energy_relative_change=float(np.min(diag['target_energy_J']/(C*grid.p)-1)),
                   max_cell_energy_relative_change=float(np.max(diag['target_energy_J']/(C*grid.p)-1)))]
    assert mutation[0]['T_L1_residual']>1000*SUM_TOL
    write_csv(out/'ENERGY_OWNER_MUTATION.csv',mutation)
    diagnostics={k:v for k,v in diag.items() if k!='target_energy_J'}
    summary=dict(schema='BASS_B3B2_LOCKED_CELL_BRIDGE_NUMERICAL_V1',status='PASS',
                 input_identity=grid.input_identity,grid_identity=grid.identity,shape=list(grid.shape),packets=len(state.w),
                 provenance=diagnostics,units=dict(kappa=units.kappa,L=units.L,Pstar=units.Pstar,alphaL=units.alpha),
                 acceptance=dict(sum_tolerance=SUM_TOL,sum_tolerance_eps=512,positive_f_tolerance=ROUNDTRIP_TOL,positive_f_tolerance_eps=128,
                                 residual_definition='max component absolute error / global L1 sum of absolute contributions',
                                 exact_zeros='Actual zero residuals are retained as numeric zero. No log floor is fabricated.'),
                 physical=dict(number_density_m3=float(N[0]/C),energy_density_J_m3=float(T[0,0]),N=N.tolist(),T=T.tolist(),
                               stock_is_scalar_unpolarized_isotropic=True),bridge=bridge,
                 covariance=dict(rows=len(covariance),
                                 max_N_residual=max(x['N_covariance_residual'] for x in covariance),
                                 max_T_residual=max(x['T_covariance_residual'] for x in covariance),
                                 max_inverse_f_relative=max(x['inverse_positive_f_relative'] for x in covariance),
                                 max_rejected_omitted_weight_T_residual=max(x['rejected_omitted_weight_T_residual'] for x in covariance)),
                 energy_mutation=mutation[0],versions=dict(python=sys.version,numpy=np.__version__,matplotlib=matplotlib.__version__,platform=platform.platform()),
                 new_ivp=0,old_campaign_replay=0,full_trajectory_claim=False)
    (out/'VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
    plt.rcParams.update({'font.size':10,'axes.titlesize':11})
    fig,axes=plt.subplots(2,2,figsize=(16,10),layout='constrained')
    ax=axes[0,0];x=np.arange(len(stock))
    ax.bar(x,[r['number_density_m3'] for r in stock],color='#27647b')
    ax.set_xticks(x,[r['cell_label'] for r in stock],rotation=90,fontsize=7)
    ax.set_ylabel('Photon stock per locked cell [m⁻³]');ax.set_title('(a) Actual REC scalar isotropic bootstrap INITIAL-DATA')
    twin=ax.twinx();twin.plot(x,[r['energy_eV'] for r in stock],'.-',color='#b55322',lw=1,ms=3)
    twin.set_ylabel('Saved physical energy c pᵢ [eV]',color='#b55322')
    twin.ticklabel_format(axis='y',style='plain',useOffset=False)
    ax=axes[0,1]
    for chart,style in (('axial','-'),('nonaxial','--')):
        for name,color in (('N','#27647b'),('T','#b55322')):
            subset=[r for r in covariance if r['scenario'].startswith('synthetic') and r['boost_chart']==chart]
            ax.plot([r['beta_magnitude'] for r in subset],[r[name+'_covariance_residual']/EPS for r in subset],style+'o',color=color,label=f'{name}, {chart}',ms=3)
    ax.set_title('(b) Correct state boost: synthetic anisotropy on actual grid')
    ax.set_xlabel('|β|');ax.set_ylabel('Covariance residual / machine ε');ax.legend(fontsize=8,ncol=2)
    ax.text(.03,.97,'Frozen acceptance ≤ 512 ε\nZero is plotted at zero; no fabricated floor.',transform=ax.transAxes,va='top',fontsize=8)
    ax=axes[1,0]
    for chart,style in (('axial','-'),('nonaxial','--')):
        for name,color in (('N','#27647b'),('T','#b55322')):
            subset=[r for r in covariance if r['scenario'].startswith('synthetic') and r['boost_chart']==chart]
            ax.plot([r['beta_magnitude'] for r in subset],[r['rejected_omitted_weight_'+name+'_residual'] for r in subset],style+'o',color=color,label=f'{name}, {chart}',ms=3)
    ax.set_title('(c) REJECTED mutation: omit state-density w′ = D w')
    ax.set_xlabel('|β|');ax.set_ylabel('L1-scaled covariance residual');ax.legend(fontsize=8,ncol=2)
    ax=axes[1,1];mut=mutation[0]
    vals=[mut['photon_number_relative_residual'],mut['energy_density_relative_residual']]
    bars=ax.bar(['Photon number','Energy density'],np.array(vals)*1e9,color=['#27647b','#b55322'])
    ax.axhline(0,color='black',lw=.5)
    ax.set_ylim(-7.5,.55)
    for bar,value in zip(bars,vals):ax.annotate(f'{value:.6g}',(bar.get_x()+bar.get_width()/2,bar.get_height()),xytext=(0,-16 if value<0 else 5),textcoords='offset points',ha='center',fontsize=9)
    ax.set_title('(d) REJECTED mutation: actual parent target energy for c pᵢ')
    ax.set_ylabel('Signed relative change × 10⁹')
    ax.text(.03,.19,'Photon number is energy-independent.\nLabels show raw signed relative changes.',transform=ax.transAxes,va='top',fontsize=8)
    fig.suptitle('Locked-cell inventory → BASS state packets: direct sums, covariance, and rejected mutations',fontsize=14)
    fig.savefig(out/'LOCKED_CELL_BRIDGE.png',dpi=160)
    fig.savefig(out/'LOCKED_CELL_BRIDGE.pdf')
    plt.close(fig)
    print(json.dumps({key:summary[key] for key in ('status','shape','packets','physical','bridge','covariance','energy_mutation')},indent=2))


if __name__=='__main__':main()
