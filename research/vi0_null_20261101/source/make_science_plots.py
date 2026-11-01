"""BASS source-owned numerical scientific plots from already saved physical data."""
from __future__ import annotations
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT/'plots';out.mkdir(exist_ok=True,parents=True)
    with (ROOT/'data'/'VI0_NULL_MOMENT_HISTORY.csv').open(newline='') as f:
        rows=list(csv.DictReader(f))
    key='case'; selected=[r for r in rows if int(r[key])==0]
    grids=('AXIS6','LEBEDEV26','GL8x16')
    fig,ax=plt.subplots(figsize=(8.2,5.1))
    for g in grids:
        d=[r for r in selected if r['grid']==g]
        ax.plot([float(x['u']) for x in d],[float(x['rho_tracer']) for x in d],label=g)
    t=np.linspace(0,.2,41)
    ax.plot(t,np.exp(-4*t),linestyle='--',label='isotropic exponential reference')
    ax.set(xlabel='Hubble-normalized time',ylabel='non-gravitating tracer energy density',title='Original VI0 background: physical null photon energy')
    ax.legend();fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(out/f'VI0_LIOUVILLE_ENERGY_CASE0.{ext}',dpi=170)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.2,5.1))
    for g in grids:
        d=[r for r in selected if r['grid']==g]
        ax.plot([float(x['u']) for x in d],[(float(x['sky_weight_sum'])-1) for x in d],label=g)
    ax.set(xlabel='Hubble-normalized time',ylabel='transported angular cell area / 4π minus 1',title='Angular Jacobian: finite-grid measure drift')
    ax.legend();fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(out/f'VI0_ANGULAR_WEIGHT_JACOBIAN_CASE0.{ext}',dpi=170)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.2,5.1))
    d=[r for r in selected if r['grid']=='GL8x16']
    for k in ('I_quad_xy','I_quad_xz','I_quad_yz'):
        ax.plot([float(x['u']) for x in d],[float(x[k]) for x in d],label=k)
    ax.set(xlabel='Hubble-normalized time',ylabel='tracer pressure off-diagonal moment',title='Actual VI0 collisionless photon anisotropic stress (test field)')
    ax.legend();fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(out/f'VI0_NULL_QUADRUPOLE_CASE0.{ext}',dpi=170)
    plt.close(fig)
    print('PLOTTED',len(list(out.glob('*.png'))),'PNG',len(list(out.glob('*.svg'))),'SVG')
if __name__=='__main__':main()
