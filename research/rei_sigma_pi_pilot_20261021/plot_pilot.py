#!/usr/bin/env python3
"""Plot the signed half-contraction pilot aggregate without interpolation."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

import numpy as np
os.environ.setdefault('MPLCONFIGDIR', '/tmp/rei_sigma_pi_mplcache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D


def read_numeric(path):
    with Path(path).open() as f:
        result = list(csv.DictReader(f))
    for row in result:
        for k, v in row.items():
            try:
                row[k] = float(v)
            except (ValueError, TypeError):
                pass
    return result


def midpoint_edges(centers):
    centers = np.asarray(centers, dtype=float)
    if len(centers) < 2 or not np.all(np.diff(centers) > 0):
        raise ValueError('STRICTLY_INCREASING_GRID_CENTERS_REQUIRED')
    return np.r_[centers[0] - (centers[1]-centers[0])/2,
                 (centers[:-1]+centers[1:])/2,
                 centers[-1] + (centers[-1]-centers[-2])/2]


def endpoint_grid(cases, contract):
    def signed(magnitudes):
        return sorted({sign*value for value in magnitudes
                       for sign in ((0,) if value == 0 else (-1, 1))})
    sigmas = signed(contract['grid']['Sigma_half'])
    pis = signed(contract['grid']['Pi_half'])
    values = np.full((len(pis),len(sigmas)), np.nan)
    for row in cases:
        values[pis.index(row['signed_Pi_requested']),
               sigmas.index(row['signed_Sigma_requested'])] = row['final_Pi_half']
    return sigmas, pis, np.ma.masked_invalid(values)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--aggregate', required=True, help='Directory with cases.csv, history.csv, summary.json')
    p.add_argument('--out', required=True, help='Figure basename, no extension')
    args = p.parse_args()
    folder = Path(args.aggregate)
    summary = json.loads((folder/'summary.json').read_text())
    cases = read_numeric(folder/'cases.csv')
    history = read_numeric(folder/'history.csv')
    if not cases:
        raise ValueError('NO_CASES_TO_PLOT')
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size':11,'axes.labelsize':11,'axes.titlesize':11,
        'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':9,
        'font.family':'DejaVu Sans','pdf.fonttype':42,'ps.fonttype':42,
        'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':250})
    fig, axes = plt.subplots(2,2,figsize=(12.8,10.6))
    fig.subplots_adjust(left=.09,right=.94,bottom=.19,top=.87,hspace=.39,wspace=.37)
    cmap = plt.get_cmap('coolwarm')
    sigmas = sorted({r['signed_Sigma_requested'] for r in cases})
    pis = sorted({r['signed_Pi_requested'] for r in cases})
    snorm = Normalize(min(sigmas),max(sigmas))
    pnorm = Normalize(min(pis),max(pis))
    ax = axes[0,0]
    for sigma in sigmas:
        subset = sorted((r for r in cases if r['signed_Sigma_requested']==sigma),key=lambda r:r['signed_Pi_requested'])
        ax.plot([r['signed_Pi_requested'] for r in subset],
                [r['final_signed_Pi'] for r in subset],'.-',ms=5,lw=.85,color=cmap(snorm(sigma)))
    ax.set(xlabel=r'Initial signed $\Pi_h$',ylabel=r'Endpoint signed $\Pi_h$',
           title='Stress response at fixed initial shear')
    ax.ticklabel_format(style='sci',axis='both',scilimits=(-3,3))
    fig.colorbar(plt.cm.ScalarMappable(norm=snorm,cmap=cmap),ax=ax,pad=.025,label=r'Initial signed $\Sigma_h$')
    ax = axes[0,1]
    for pi in pis:
        subset = sorted((r for r in cases if r['signed_Pi_requested']==pi),key=lambda r:r['signed_Sigma_requested'])
        ax.plot([r['signed_Sigma_requested'] for r in subset],
                [r['final_signed_Sigma'] for r in subset],'.-',ms=5,lw=.85,color=cmap(pnorm(pi)))
    ax.set(xlabel=r'Initial signed $\Sigma_h$',ylabel=r'Endpoint signed $\Sigma_h$',
           title='Endpoint shear response')
    ax.ticklabel_format(style='sci',axis='both',scilimits=(-3,3))
    fig.colorbar(plt.cm.ScalarMappable(norm=pnorm,cmap=cmap),ax=ax,pad=.025,label=r'Initial signed $\Pi_h$')
    ax = axes[1,0]
    twin = ax.twinx()
    # Isotropic control and all four signed extreme corners.
    maxs,maxp = max(abs(x) for x in sigmas),max(abs(x) for x in pis)
    chosen = [r for r in cases if (r['signed_Sigma_requested']==0 and r['signed_Pi_requested']==0)
              or (abs(r['signed_Sigma_requested'])==maxs and abs(r['signed_Pi_requested'])==maxp)]
    colors = ['#222222','#0072B2','#D55E00','#009E73','#CC79A7']
    handles=[]
    for i,case in enumerate(chosen):
        rows = sorted((r for r in history if r['case_id']==case['case_id']),key=lambda r:r['step'])
        z = [1/r['a']-1 for r in rows]
        color=colors[i%len(colors)]
        ax.plot(z,[r['signed_Sigma'] for r in rows],color=color,lw=1.4)
        twin.plot(z,[r['signed_Pi'] for r in rows],color=color,lw=1.1,ls='--')
        handles.append(Line2D([0],[0],color=color,label=f"({case['signed_Sigma_requested']:+.4g}, {case['signed_Pi_requested']:+.4g})"))
    ax.invert_xaxis()
    ax.set(xlabel=r'Mean redshift $z=1/a-1$',ylabel=r'Signed $\Sigma_h$ (solid)',title='Representative actual trajectories')
    twin.set_ylabel(r'Signed $\Pi_h$ (dashed)')
    for a in (ax,twin):
        a.ticklabel_format(style='sci',axis='y',scilimits=(-3,3))
    ax.ticklabel_format(axis='x',style='plain',useOffset=False)
    ax.legend(handles=handles,title=r'Initial $(\Sigma_h,\Pi_h)$, signed',loc='center left',fontsize=8,title_fontsize=9)
    ax = axes[1,1]
    # Rectangular signed grid with explicit masked missing cells. No fitting or
    # interpolation is used; every visible cell is an actually completed case.
    contract_path = Path(__file__).resolve().parent/'PILOT_CONTRACT.json'
    contract = json.loads(contract_path.read_text())
    fullsig, fullpi, values = endpoint_grid(cases, contract)
    # Coordinates are nonuniform: midpoint edges retain their actual spacing.
    # Missing points remain masked, including completely absent rows/columns.
    image=ax.pcolormesh(midpoint_edges(fullsig)*1e3, midpoint_edges(fullpi)*1e4,
                        values, shading='flat', cmap='viridis', rasterized=True)
    ax.set_xticks(np.asarray(fullsig)*1e3,[f'{s*1e3:g}' for s in fullsig])
    ax.set_yticks(np.asarray(fullpi)*1e4,[f'{s*1e4:g}' for s in fullpi])
    ax.set(xlabel=r'Initial signed $\Sigma_h\;(10^{-3})$',ylabel=r'Initial signed $\Pi_h\;(10^{-4})$',
           title=r'Endpoint physical stress norm $\Pi_h$')
    fig.colorbar(image,ax=ax,pad=.025,label=r'Endpoint $\Pi_h$ (half-contraction)')
    for ax in axes.flat:
        ax.grid(alpha=.16,lw=.5)
    for label,ax in zip('ABCD',axes.flat):
        ax.text(-.16,1.06,label,transform=ax.transAxes,fontweight='bold',fontsize=12)
    fig.suptitle('Conditional Einstein–Boltzmann signed shear–stress pilot\n'
                 +r'Half-contraction norms; warm $a=0.1999\rightarrow0.2$, $z=4.00250125\rightarrow4$',fontsize=14,y=.96)
    footer=(f"{summary['case_count']}/{summary['expected_case_count']} actual cases; {summary['nsteps']} steps; L=8; native 8×8; common positive P₂ seed; all physical stress terms on.\n"
      'Initial gas: 12,000 K, xHII=0.4, xHeII=0.5; massive fraction=0.1, m/T=30; compression and predictor–corrector on.\n'
      'External MD14 stellar source and Case-A escape: full donor/escape Qᵃ closure, full EoR history and convergence remain open.\n'
      f"Owner REI {summary['owner_ref']}; preliminary conditional response. Thermochemical differences are not convergence claims.")
    fig.text(.055,.055,footer,fontsize=9,va='bottom',linespacing=1.5)
    for ext in ('png','pdf'):
        fig.savefig(out.with_suffix('.'+ext))
    plt.close(fig)
    prov={'schema':'rei.sigma_pi.figure_provenance.v1','owner_ref':summary['owner_ref'],
          'science_binding':summary['science_binding'],'summary':summary,
          'inputs':[{ 'path':str((folder/name).resolve()),
                     'sha256':hashlib.sha256((folder/name).read_bytes()).hexdigest()}
                    for name in ('cases.csv','history.csv','summary.json')],
          'coordinate_contract': {'path':str(contract_path),
              'sha256':hashlib.sha256(contract_path.read_bytes()).hexdigest()},
          'plot_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'interpolation':'none; lines connect actual same-coordinate cases; masked endpoint cells',
          'figures':[str(out.with_suffix('.'+ext).resolve()) for ext in ('png','pdf')]}
    out.with_suffix('.provenance.json').write_text(json.dumps(prov,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'png':str(out.with_suffix('.png').resolve()),'pdf':str(out.with_suffix('.pdf').resolve())}))


if __name__=='__main__':
    main()
