#!/usr/bin/env python3
"""Render stored native S7 measurements; never execute a physical campaign."""
import argparse
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--analysis',type=Path,required=True)
    parser.add_argument('--out-prefix',type=Path,required=True)
    args=parser.parse_args()
    analysis=json.loads(args.analysis.read_text())
    if analysis['schema'] not in ('bass.native.cohorts.s7.analysis.v1','bass.native.cohorts.s7.analysis.v2'):
        raise ValueError('ANALYSIS_SCHEMA')
    metrics=analysis['metrics']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelsize':11,
                         'axes.titlesize':11,'legend.fontsize':9,'figure.dpi':150,
                         'savefig.dpi':180,'svg.fonttype':'none'})
    fig,axes=plt.subplots(1,2,figsize=(10.0,4.2),layout='constrained')
    ax=axes[0]
    for mode,color,marker,label in [('prior','#666666','o','Prior'),('P2','#2166ac','s','P2: n >= 16 feasible'),('P2P4','#b2182b','^','P2/P4: n = 32 feasible')]:
        rows=sorted([r for r in metrics if r['block']=='angular' and r['b0']==.6 and r['mode']==mode],key=lambda r:r['n_mu'])
        ax.semilogy([r['n_mu'] for r in rows],[abs(r['angular_a_error']) for r in rows],color=color,marker=marker,label=label,lw=1.7,ms=6)
    ax.axhline(1e-6,color='#333333',ls='--',lw=1,label='Declared accuracy target')
    ax.set(xlabel='Native angular rays',ylabel=r'$|\mathcal{A}_{\mathrm{native}}-\mathcal{A}_{\mathrm{iso}}|$',
           xticks=[8,16,32],xlim=(6,34),ylim=(3e-7,.7),title=r'(a) Fixed births: $b_0=0.6$, observed $b=0.8$')
    ax.legend(loc='lower left',frameon=False)
    ax.grid(True,which='major',alpha=.22)
    ax=axes[1]
    rows=sorted([r for r in metrics if r['block']=='slab_bins'],key=lambda r:r['n_energy'])
    for j,label,color,marker in [(0,'Photon number','#2166ac','o'),(1,'Energy','#b2182b','s')]:
        ax.loglog([r['n_energy'] for r in rows],[abs(r['slab_errors_relative_to_before'][j]) for r in rows],color=color,marker=marker,label=label,lw=1.7,ms=6)
    ax.axhline(1e-4,color='#333333',ls='--',lw=1,label='Declared bin-192 target')
    ax.set(xlabel='Native reference-energy bins',ylabel='Spectral error / inventory before absorption',
           xticks=[24,48,96,192],xticklabels=['24','48','96','192'],xlim=(21,220),ylim=(5e-9,3e-3),
           title='(b) Merged cohorts, one fixed-opacity slab')
    ax.minorticks_off();ax.legend(loc='upper right',frameon=False);ax.grid(True,which='major',alpha=.22)
    args.out_prefix.parent.mkdir(parents=True,exist_ok=True)
    outputs=[]
    for suffix in ('.png','.svg'):
        p=args.out_prefix.with_suffix(suffix)
        if p.exists():raise FileExistsError(p)
        fig.savefig(p);outputs.append(p)
    plt.close(fig)
    receipt={'schema':'bass.s7.native.stored_data_figure.v1','analysis_sha256':hashlib.sha256(args.analysis.read_bytes()).hexdigest(),
             'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'physical_campaign_rerun':False,'plot_files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in outputs},
             'caption':'Left: missing P2/P4 points are actual support failures. Right: the direct spectral reference uses the same finite angular rules. Gates do not certify continuum or full reactive history.'}
    p=args.out_prefix.with_suffix('.receipt.json')
    with p.open('x') as f:f.write(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__=='__main__':main()
