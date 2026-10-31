#!/usr/bin/env python3
"""CE1AK six actual source-locked scientific physics figures."""
import csv,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parent.parent
FIG=ROOT/'figures';FIG.mkdir(parents=True,exist_ok=True)
with (ROOT/'data'/'CE1AK_STRESS_EINSTEIN.csv').open(newline='') as f:
    rows=list(csv.DictReader(f))

def draw(name,window,cols):
    rr=[r for r in rows if r['GL']=='16' and r['window']==window]
    times=np.array([float(r['u']) for r in rr])
    fig,ax=plt.subplots(figsize=(8.4,4.7))
    for field,title in cols:
        ax.plot(times,np.array([float(r[field]) for r in rr]),label=title)
    ax.set(xlabel='Normalized proper time u=t/Tstar',
           ylabel='Per unit dark-source parameter epsilon',title=name)
    ax.legend();ax.grid(alpha=.25);fig.tight_layout()
    fig.savefig(FIG/(name.replace(' ','_')+'.png'),dpi=150);plt.close(fig)

def main():
    draw('CE1AK_exact_sixth_source_evolution','original_horizon',
         [('T_xxy','sixth xxy'),('T_xyz','sixth xyz')])
    draw('CE1AK_dark_pressure_delay','jet_resolved',
         [('dP1','delta Px'),('dP2','delta Py'),('dP3','delta Pz')])
    draw('CE1AK_dark_expansion_delay','jet_resolved',
         [('dh1','delta h1'),('dh3','delta h3')])
    draw('CE1AK_shear_work_jet','jet_resolved',[('dW','delta W')])
    draw('CE1AK_dark_energy_jet','jet_resolved',[('dE','delta E')])
    draw('CE1AK_full_horizon_energy_work','original_horizon',
         [('dE','delta E'),('dW','delta W')])
    print('CE1AK_ACTUAL_PHYSICAL_PLOTS',len(list(FIG.glob('*.png'))))
if __name__=='__main__':main()
