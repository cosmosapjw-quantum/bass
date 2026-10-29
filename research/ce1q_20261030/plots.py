#!/usr/bin/env python3
"""Evidence figures for model-derived unpolarized energy sky, not a CMB dataset."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt

def rows(path):
 with Path(path).open(newline='') as f:return [{k:float(v) for k,v in x.items()} for x in csv.DictReader(f)]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--data',required=True);ap.add_argument('--output',required=True)
 args=ap.parse_args();root=Path(args.data);out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
 src=json.loads((root/'results.json').read_text())
 cases={k:rows(root/f'{k}_alm.csv') for k in src['channels']}
 ci=cases['gl40'][-1]
 fig,ax=plt.subplots(figsize=(7.5,4.2))
 for c in ('stored_ref1','stored_ref4','stored_ref8','stored_ref16'):
  rr=src['channels'][c];gg=src['channels']['gl40']
  ax.scatter(int(c.replace('stored_ref','')),rr['final_C4']/gg['final_C4'],label=c)
 ax.axhline(1,color='0.5',ls='--',label='GL40 numeric reference')
 ax.set(xlabel='Stored ray refinement f (6 f² positive-octant rays)',ylabel=r'$C_4^U(f)/C_4^U(\mathrm{GL40})$',title='Hexadecapole quadrature bias, unchanged six physical cells')
 ax.set_yscale('log');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(out/'l4_source_refinement.png',dpi=180);plt.close(fig)
 fig,ax=plt.subplots(figsize=(7.5,4.4))
 for l,m in [(2,0),(2,2),(4,0),(4,4)]:
  u=np.array([r['u'] for r in cases['gl40']]); y=np.array([r[f'a_{l}_{m}_re']/r['E'] for r in cases['gl40']])
  ax.plot(u,y,label=rf'$a_{{{l}{m}}}^U/E$')
 ax.set(xlabel=r'$u=t/T_\star$',ylabel=r'$a_{\ell m}^{U}/E$',title='Observer-frame sky harmonics from BASS Einstein–Vlasov history')
 ax.legend();fig.tight_layout();fig.savefig(out/'harmonic_time_evolution.png',dpi=180);plt.close(fig)
 fig,ax=plt.subplots(figsize=(7.0,4.1))
 gl=cases['gl40'][-1];ell=np.arange(0,5)
 cl=[]
 for l in ell:cl.append(sum(gl[f'a_{l}_{m}_re']**2+gl[f'a_{l}_{m}_im']**2 for m in range(-l,l+1))/(2*l+1)/gl['E']**2)
 ax.bar(ell,cl)
 ax.set(xlabel=r'Multipole $\ell$',ylabel=r'$C_\ell^U/E^2$ (model, not observed CMB)',title='Physical angular-energy harmonic power at u=0.08',xticks=ell)
 ax.set_yscale('symlog',linthresh=1e-23);fig.tight_layout();fig.savefig(out/'endpoint_angular_spectrum.png',dpi=180);plt.close(fig)
 npz=np.load(root/'gl40_observer_sky_map.npz');theta=npz['theta'];az=npz['azimuth'];I=npz['energy_per_solid_angle']
 # Center observed longitude in [-pi,pi] and normalized isotropy 4pi I/E=1.
 lat=np.pi/2-theta;lon=(az+np.pi)%(2*np.pi)-np.pi
 indices=np.argsort(lon); img=(4*np.pi*I/gl['E'])[:,indices]
 fig=plt.figure(figsize=(9.4,4.5));ax=fig.add_subplot(111,projection='mollweide')
 im=ax.pcolormesh(lon[indices],lat,img,shading='auto',rasterized=True,cmap='viridis')
 ax.grid(True,alpha=0.35);ax.set_title('Continuous six-cell collisionless angular energy sky (4π U/E), u=0.08')
 fig.colorbar(im,ax=ax,shrink=.78,label=r'$4\pi U/E$ (isotropic = 1)')
 fig.tight_layout();fig.savefig(out/'observer_energy_sky.png',dpi=180);plt.close(fig)
 print('CE1Q_FIGURES_GENERATED',len(list(out.glob('*.png'))))
if __name__=='__main__':main()
