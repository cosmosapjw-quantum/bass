"""Six actual KM2O second-gain scientific plots + exact 12,000 bin data CSV."""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def make(source,outdir):
    source=Path(source);out=Path(outdir);out.mkdir(exist_ok=True,parents=True)
    d=json.loads(source.read_text());rec=d['measurements']
    if len(rec)!=10:raise ArithmeticError('expected source-owned 10 actual physical epochs')
    edges=np.linspace(-.5,.5,1201);centers=(edges[:-1]+edges[1:])/2
    rows=[]
    for x in rec:
        if len(x['spectral_bins'])!=1200:raise ArithmeticError('source spectrum not 1200 bins')
        for i,v in enumerate(x['spectral_bins']):
            rows.append(dict(grid=x['grid'],u=x['u'],logfreq=float(centers[i]),
                             bin_second_gain_rate=float(v),second_gain_density_per_logfreq=float(v/(edges[i+1]-edges[i]))))
    if len(rows)!=12000:raise ArithmeticError('physical bins missing')
    with (out/'KM2O_12000_SECOND_THOMSON_PHYSICAL_FREQ_ROWS.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    names=[
        ('second_gain_energy_rate','second_gain_energy_rate','Second Thomson gain rate (original BASS unit / normal u)'),
        ('second_gain_polarization','second_gain_linear_polarization_mean','Mean linear polarization in second gain'),
        ('second_gain_mean_logfreq','normal_frequency_centroid','Second gain mean log-frequency'),
        ('second_gain_sigma_logfreq','frequency_sigma_logbin','Second gain frequency standard deviation'),
        ('second_gain_frame_work','first_scatter_loss_rate','Normal first-order loss vs second gain source rate')]
    plots=[]
    for name,key,ylabel in names[:4]:
        fig,ax=plt.subplots(figsize=(7.6,4.5))
        for grid in ('GL12','GL16'):
            cases=[x for x in rec if x['grid']==grid]
            ax.plot([x['u'] for x in cases],[x[key] for x in cases],marker='o',label=grid)
        ax.set_xlabel('Original Einstein-P8 normal time u=t/Tstar');ax.set_ylabel(ylabel);ax.legend();ax.grid(alpha=.2);fig.tight_layout()
        fig.savefig(out/(name+'.png'),dpi=145);plt.close(fig);plots.append(name+'.png')
    fig,ax=plt.subplots(figsize=(7.6,4.5))
    for grid in ('GL12','GL16'):
        cases=[x for x in rec if x['grid']==grid]
        ax.plot([x['u'] for x in cases],[x['second_gain_energy_rate'] for x in cases],marker='o',label=grid+' gain')
        ax.plot([x['u'] for x in cases],[x['first_scatter_loss_rate'] for x in cases],ls='--',marker='.',label=grid+' loss')
    ax.set_xlabel('Original Einstein-P8 normal time u');ax.set_ylabel('Normal-frame collision source rate (BASS/u)');ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout()
    fig.savefig(out/'second_gain_vs_first_loss.png',dpi=145);plt.close(fig);plots.append('second_gain_vs_first_loss.png')
    fig,ax=plt.subplots(figsize=(7.6,4.5))
    for grid in ('GL12','GL16'):
        x=[a for a in rec if a['grid']==grid and a['k']==40][0]
        ax.plot(centers,np.asarray(x['spectral_bins'])/(edges[1]-edges[0]),label=grid)
    ax.set_xlim(-.25,.16);ax.set_xlabel('ln(nu_normal/nu_Lya) at u=.25');ax.set_ylabel('First-order photons: second gain d-rate / d log-frequency');ax.legend();ax.grid(alpha=.2);fig.tight_layout()
    fig.savefig(out/'second_gain_frequency_profile.png',dpi=145);plt.close(fig);plots.append('second_gain_frequency_profile.png')
    receipt=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                 observed_physical_epochs=len(rec),source_frequency_bins=len(rows),
                 scientific_figures=plots)
    (out/'SOURCE_FIGURE_PROVENANCE.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('KM2O_REAL_PHYSICS_PLOTS',len(plots),'EPOCHS',len(rec),'FREQUENCY_ROWS',len(rows),flush=True)
    return receipt

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();make(a.source,a.output)
