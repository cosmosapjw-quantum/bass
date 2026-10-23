"""Render only stored evidence. No integration, tests or source refitting."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
FIG=ROOT/'figures'

def save(fig,name,rows):
    for ext in ('png','svg'):fig.savefig(FIG/f'{name}.{ext}',dpi=160,bbox_inches='tight')
    with (FIG/f'{name}.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    plt.show();plt.close(fig)

def main():
    FIG.mkdir(exist_ok=True)
    names=['fixed_angular_refinement','curved_error_budget','separate_stress_VIII']
    if any((FIG/(name+'.png')).exists() for name in names):raise FileExistsError('preserve previous render')
    with (ROOT/'evidence/frozen_001/refinement.csv').open() as f:table=list(csv.DictReader(f))
    rows=[r for r in table if r['axis']=='angular' and int(r['nmu'])<56]
    fig,ax=plt.subplots(figsize=(7.6,4.8))
    markers=['o','s','^','v','D','x']
    for name,marker in zip(dict.fromkeys(r['case'] for r in rows),markers):
        rr=[r for r in rows if r['case']==name]
        ax.semilogy([int(r['nmu']) for r in rr],[float(r['max_error']) for r in rr],marker=marker,label=name.replace('_',' '))
    ax.axhline(2e-8,linestyle=':',label='Frozen acceptance gate')
    ax.set(xlabel=r'Polar order $n_\mu$; azimuthal order $n_\phi=2n_\mu$',ylabel='Density-scaled moment difference',
           title='Fixed-state angular refinement: six source states',ylim=(1e-16,1))
    ax.grid(True,alpha=.25);ax.legend(fontsize=8,ncol=2,loc='lower left');fig.tight_layout()
    save(fig,names[0],rows)
    curved=json.loads((ROOT/'evidence/curved_002/RESULTS.json').read_text())
    half=json.loads((ROOT/'evidence/time_step_001/RESULTS.json').read_text())
    rows=[];keys=['radial_selected','angular_selected','time_selected','half_step','combined']
    labels=['Radial\n8 to 12','Angular\n14 to 20','Tolerance\n100x tighter','Step cap\n0.04 to 0.02','Combined\ngrid change']
    for family in ['V','VIII']:
        for axis in keys:
            err=next(x['observable_error'] for x in half['cases'] if x['family']==family) if axis=='half_step' else next(x['error'] for x in curved['comparisons'] if x['family']==family and x['axis']==axis)
            rows.append(dict(family=family,axis=axis,error=err,gate=2e-8))
    fig,ax=plt.subplots(figsize=(7.6,4.5));x=np.arange(5)
    for i,family in enumerate(['V','VIII']):
        ax.bar(x+(i-.5)*.34,[r['error'] for r in rows if r['family']==family],width=.32,label='Bianchi '+family)
    ax.axhline(2e-8,linestyle=':',label='Frozen acceptance gate')
    ax.set_yscale('log');ax.set_xticks(x,labels);ax.set_ylim(1e-14,1e-7)
    ax.set(ylabel=r'$\max |X_1-X_2|/(1+\max(|X_1|,|X_2|))$',title='Curved histories: radial, angular and time errors separated')
    ax.grid(True,axis='y',alpha=.25);ax.legend(loc='upper right',fontsize=9);fig.tight_layout()
    save(fig,names[1],rows)
    with np.load(ROOT/'evidence/curved_002/VIII_r12_a20.npz') as f:t=f['tau'];obs=f['observable']
    pm,pr=obs[:,31],obs[:,45]
    rows=[dict(tau=float(a),pi_m_xy=float(b),pi_gamma_xy=float(c),pi_total_xy=float(b+c)) for a,b,c in zip(t,pm,pr)]
    fig,ax=plt.subplots(figsize=(7.6,4.3))
    ax.plot(t,pm,label='Massive momentum-decoupled FD')
    ax.plot(t,pr,linestyle='--',label='Initially isotropic Planck sector')
    ax.plot(t,pm+pr,linestyle='-.',label='Tensor sum')
    ax.set(xlabel=r'Fixed-scale proper time $\tau=ct/L_*$',ylabel=r'Signed $\hat\pi_{xy}=\kappa L_*^2\pi^{\mathrm{phys}}_{xy}$',title='Bianchi VIII: opposing matter and photon stresses')
    ax.grid(True,alpha=.25);ax.legend(fontsize=9);fig.tight_layout()
    save(fig,names[2],rows)
    inputs=[ROOT/'evidence/frozen_001/refinement.csv',ROOT/'evidence/curved_002/RESULTS.json',ROOT/'evidence/time_step_001/RESULTS.json',ROOT/'evidence/curved_002/VIII_r12_a20.npz']
    manifest={'render':'stored-evidence-only','new_IVPs':0,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'plots':names,'new_png':3,'new_svg':3,'new_csv':3,'limitations':'finite grid differences, not certified continuum error; see REFERENCE_CONFIRMATION for stronger Planck reference'}
    (FIG/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
