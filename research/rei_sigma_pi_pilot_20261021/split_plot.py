#!/usr/bin/env python3
"""Plot actual independent matter/radiation stress responses and cancellation."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from plot_pilot import midpoint_edges, read_numeric
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, TwoSlopeNorm
from matplotlib.lines import Line2D

LANE = Path(__file__).resolve().parent
CONTRACT = LANE/'SPLIT_CONTRACT.json'


def signed_axis(magnitudes):
    return sorted({sign*value for value in magnitudes
                   for sign in ((0,) if value == 0 else (-1,1))})


def change(row, field):
    return row['final_'+field]-row['initial_'+field]


def zero_stress_controls(cases):
    """Actual endpoint controls at each requested initial signed shear."""
    controls = {}
    for row in cases:
        if row['signed_Pi_m_requested'] == 0 and row['signed_Pi_r_requested'] == 0:
            key = row['signed_Sigma_requested']
            if key in controls:
                raise ValueError('DUPLICATE_ZERO_STRESS_CONTROL')
            controls[key] = row
    return controls


def paired_response(row,controls,field='signed_Sigma'):
    control = controls.get(row['signed_Sigma_requested'])
    return np.nan if control is None else row['final_'+field]-control['final_'+field]


def slice_grid(cases,contract,sigma,controls,field='signed_Sigma'):
    pm = signed_axis(contract['grid']['Pi_m_half'])
    pr = signed_axis(contract['grid']['Pi_r_half'])
    values = np.full((len(pr),len(pm)),np.nan)
    for row in cases:
        if row['signed_Sigma_requested'] == sigma:
            values[pr.index(row['signed_Pi_r_requested']),
                   pm.index(row['signed_Pi_m_requested'])] = paired_response(row,controls,field)
    return pm,pr,np.ma.masked_invalid(values)


def zero_norm(values):
    values = np.asarray(values,dtype=float)
    maximum = float(np.max(np.abs(values))) if values.size else 0.
    maximum = maximum if maximum else np.finfo(float).tiny
    return TwoSlopeNorm(vmin=-maximum,vcenter=0.,vmax=maximum)


def style():
    plt.rcParams.update({'font.size':11,'axes.labelsize':11,'axes.titlesize':11,
        'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':9,
        'font.family':'DejaVu Sans','pdf.fonttype':42,'ps.fonttype':42,
        'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':250})


def canvas(title):
    fig,axes=plt.subplots(2,2,figsize=(12.8,10.6))
    fig.subplots_adjust(left=.095,right=.94,bottom=.21,top=.86,hspace=.42,wspace=.38)
    fig.suptitle(title+'\n'+r'Half-contraction; warm $a=0.1999\rightarrow0.2$, $z=4.00250125\rightarrow4$',fontsize=14,y=.96)
    for letter,ax in zip('ABCD',axes.flat):
        ax.text(-.16,1.06,letter,transform=ax.transAxes,fontweight='bold',fontsize=12)
        ax.grid(alpha=.15,lw=.5)
    return fig,axes


def footer(fig,summary,kind):
    delta_text = ('Shear response = endpoint minus same-initial-shear, zero-initial-stress control.'
                  if kind == 'shear_response_slices_and_cancellation_plane' else
                  'Component deltas subtract actual initial values; total norm uses the tensor sum.')
    fig.text(.05,.045,
        f"{summary['case_count']}/{summary['expected_case_count']} completed cases; 64 steps; L=8; native 8×8; independent positive P₂ matter/radiation seeds.\n"
        'Matter stress: massive Vlasov only; isotropic gas/dust contribute zero. Radiation: gamma + massless nu + evolving UV.\n'
        'Gas initially 12,000 K, xHII=0.4, xHeII=0.5; massive fraction=0.1, m/T=30; all stress switches, compression and feedback on.\n'
        'Finite conditional response; full EoR, donor/escape Qᵃ closure and angular/spectral convergence remain open.\n'+
        delta_text+' No fit or interpolation.\n'+
        f"Owner REI {summary['owner_ref']}.",
        fontsize=9,va='bottom',linespacing=1.5)


def save(fig,base,folder,summary,kind):
    footer(fig,summary,kind)
    for ext in ('png','pdf'):
        fig.savefig(base.with_suffix('.'+ext))
    plt.close(fig)
    files=[folder/'cases.csv',folder/'history.csv',folder/'summary.json',CONTRACT]
    provenance={'schema':'rei.sigma_pi_split.figure_provenance.v1','figure_kind':kind,
        'science_binding':summary['science_binding'],'owner_ref':summary['owner_ref'],
        'summary':summary,'inputs':[{'path':str(path.resolve()),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in files],
        'plot_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'plot_helpers_sha256':hashlib.sha256((LANE/'plot_pilot.py').read_bytes()).hexdigest(),
        'delta_definition':('All shear panels: actual signed endpoint minus actual signed endpoint of the control with the same initial signed Sigma and both initial stresses zero; raw initial-to-final changes remain in cases.csv.'
            if kind == 'shear_response_slices_and_cancellation_plane' else
            'Panels A/B: actual signed endpoint minus actual signed initial. Panel C: actual signed component at each stored step minus its own actual initial value. Panel D: actual total stress norm without subtraction.'),
        'interpolation':'none; full contract mesh with midpoint edges and masked missing cells',
        'total_definition':'norm after signed D_m+D_r; component norms are never added as total',
        'figures':[str(base.with_suffix('.'+ext).resolve()) for ext in ('png','pdf')]}
    base.with_suffix('.provenance.json').write_text(json.dumps(provenance,indent=2,sort_keys=True)+'\n')


def plot_slices(cases,contract,folder,summary,out):
    fig,axes=canvas('Independent matter/radiation stress: shear response and cancellation')
    requested_slices=(0.,.004,-.004)
    controls=zero_stress_controls(cases)
    shown=[r for r in cases if r['signed_Sigma_requested'] in requested_slices]
    norm=zero_norm([paired_response(r,controls) for r in shown if r['signed_Sigma_requested'] in controls])
    for ax,sigma in zip(axes.flat[:3],requested_slices):
        pm,pr,values=slice_grid(cases,contract,sigma,controls)
        image=ax.pcolormesh(midpoint_edges(pm)*1e4,midpoint_edges(pr)*1e4,values,
            shading='flat',cmap='coolwarm',norm=norm,rasterized=True)
        # This dashed line identifies the input cancellation subfamily; it is
        # an exact algebraic annotation, not an interpolation of output values.
        ax.plot(np.asarray(pm)*1e4,-np.asarray(pm)*1e4,'k--',lw=.95,label=r'$\Pi_{r,i}=-\Pi_{m,i}$ (signed)')
        ax.set_xticks([-4,-2,0,2,4]);ax.set_yticks([-4,-2,0,2,4])
        ax.set(xlabel=r'Initial signed $\Pi_{m,h}\;(10^{-4})$',
            ylabel=r'Initial signed $\Pi_{r,h}\;(10^{-4})$',
            title=rf'Initial signed $\Sigma_h={sigma:+.4g}$')
        ax.legend(loc='upper right',fontsize=8)
        fig.colorbar(image,ax=ax,pad=.025,label=r'Signed $\Sigma_{h,f}-\Sigma_{h,f}^{\rm control}$')
    ax=axes[1,1]
    sigmas=sorted({r['signed_Sigma_requested'] for r in cases})
    cmap=plt.get_cmap('coolwarm');snorm=Normalize(min(sigmas),max(sigmas))
    for sigma in sigmas:
        rows=sorted((r for r in cases if r['signed_Sigma_requested']==sigma and
            r['signed_Pi_m_requested']+r['signed_Pi_r_requested']==0),key=lambda r:r['signed_Pi_m_requested'])
        if rows:
            ax.plot([r['initial_signed_Pi_m'] for r in rows],
                    [paired_response(r,controls) for r in rows],'.-',lw=.85,ms=5,color=cmap(snorm(sigma)))
    ax.set(xlabel=r'Initial signed $\Pi_{m,h}=-\Pi_{r,h}$',
        ylabel=r'Signed $\Sigma_{h,f}-\Sigma_{h,f}^{\rm control}$',title='Cancellation response relative to zero-stress control')
    ax.ticklabel_format(style='sci',axis='both',scilimits=(-3,3))
    fig.colorbar(plt.cm.ScalarMappable(norm=snorm,cmap=cmap),ax=ax,pad=.025,label=r'Initial signed $\Sigma_h$')
    save(fig,out.with_name(out.name+'_slices'),folder,summary,'shear_response_slices_and_cancellation_plane')


def plot_components(cases,history,contract,folder,summary,out):
    fig,axes=canvas('Separate matter/radiation response and cancellation evolution')
    subset=[r for r in cases if r['signed_Sigma_requested']==0]
    cmap=plt.get_cmap('coolwarm')
    stressmax=max(contract['grid']['Pi_m_half']+contract['grid']['Pi_r_half'])
    norm=Normalize(-stressmax,stressmax)
    for ax,field,other,title in ((axes[0,0],'m','r','Matter stress change at zero initial shear'),
                                 (axes[0,1],'r','m','Radiation stress change at zero initial shear')):
        for other0 in sorted({r[f'signed_Pi_{other}_requested'] for r in subset}):
            rows=sorted((r for r in subset if r[f'signed_Pi_{other}_requested']==other0),
                        key=lambda r:r[f'signed_Pi_{field}_requested'])
            ax.plot([r[f'initial_signed_Pi_{field}'] for r in rows],
                    [change(r,f'signed_Pi_{field}') for r in rows],'.-',ms=5,lw=.85,color=cmap(norm(other0)))
        ax.set(xlabel=rf'Initial signed $\Pi_{{{field},h}}$',
               ylabel=rf'$\Delta$ signed $\Pi_{{{field},h}}$',title=title)
        ax.ticklabel_format(style='sci',axis='both',scilimits=(-3,3))
        fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),ax=ax,pad=.025,
                     label=rf'Initial signed $\Pi_{{{other},h}}$')
    # Actual component evolution for the two nonzero extremal cancellation
    # inputs at zero shear. Total generation has its own finer-scale panel D.
    colors={-1:'#0072B2',1:'#D55E00'}
    ax=axes[1,0]
    selected=[]
    for sign in (-1,1):
        selected += [r for r in cases if r['signed_Sigma_requested']==0 and
            r['signed_Pi_m_requested']==sign*stressmax and r['signed_Pi_r_requested']==-sign*stressmax]
    for case in selected:
        sign=1 if case['signed_Pi_m_requested']>0 else -1
        rows=sorted((r for r in history if r['case_id']==case['case_id']),key=lambda r:r['step'])
        z=[1/r['a']-1 for r in rows]
        ax.plot(z,[r['signed_Pi_m']-rows[0]['signed_Pi_m'] for r in rows],color=colors[sign],lw=1.5,
                label=rf'Matter; $\Pi_{{m,i}}={sign*stressmax:+.4g}$')
        ax.plot(z,[r['signed_Pi_r']-rows[0]['signed_Pi_r'] for r in rows],color=colors[sign],lw=1.3,ls='--',
                label=rf'Radiation; $\Pi_{{r,i}}={-sign*stressmax:+.4g}$')
    ax.set(xlabel=r'Mean redshift $z=1/a-1$',ylabel=r'$\Pi_{A,h}(z)-\Pi_{A,h}(z_i)$, signed; $A=m,r$',
           title='Different evolution of initially opposing components')
    ax.invert_xaxis();ax.ticklabel_format(style='sci',axis='y',scilimits=(-3,3))
    ax.ticklabel_format(axis='x',style='plain',useOffset=False)
    ax.legend(loc='upper left',fontsize=7)
    ax=axes[1,1]
    colors_sigma={0.:'#333333',.004:'#D55E00',-.004:'#0072B2'}
    for sigma in (0.,.004,-.004):
        for sign in (-1,1):
            for case in [r for r in cases if r['signed_Sigma_requested']==sigma and
                r['signed_Pi_m_requested']==sign*stressmax and r['signed_Pi_r_requested']==-sign*stressmax]:
                rows=sorted((r for r in history if r['case_id']==case['case_id']),key=lambda r:r['step'])
                ax.plot([1/r['a']-1 for r in rows],[r['Pi_total_half'] for r in rows],
                    color=colors_sigma[sigma],ls='-' if sign>0 else '--',lw=1.3,
                    label=rf'$\Sigma_i={sigma:+.4g},\;\Pi_{{m,i}}={sign*stressmax:+.4g}$')
    ax.set(xlabel=r'Mean redshift $z=1/a-1$',ylabel=r'Total stress norm $\Pi_{h}$',
           title='Total norm generated from initial cancellation')
    ax.invert_xaxis();ax.ticklabel_format(style='sci',axis='y',scilimits=(-3,3))
    ax.ticklabel_format(axis='x',style='plain',useOffset=False)
    ax.legend(loc='upper left',fontsize=8)
    save(fig,out.with_name(out.name+'_components'),folder,summary,'separate_component_response_and_cancellation_evolution')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aggregate',required=True)
    parser.add_argument('--out',required=True,help='Basename; writes _slices and _components PNG/PDF/provenance')
    args=parser.parse_args()
    folder=Path(args.aggregate)
    summary=json.loads((folder/'summary.json').read_text())
    if summary['schema'] != 'rei.sigma_pi_split.aggregate.v1':
        raise ValueError('SPLIT_AGGREGATE_REQUIRED')
    cases,history=read_numeric(folder/'cases.csv'),read_numeric(folder/'history.csv')
    if not cases:
        raise ValueError('NO_SPLIT_CASES_TO_PLOT')
    contract=json.loads(CONTRACT.read_text())
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    style()
    plot_slices(cases,contract,folder,summary,out)
    plot_components(cases,history,contract,folder,summary,out)
    print(json.dumps({'figures':[str(out.with_name(out.name+suffix).with_suffix('.png').resolve())
                                 for suffix in ('_slices','_components')]}))


if __name__=='__main__':
    main()
