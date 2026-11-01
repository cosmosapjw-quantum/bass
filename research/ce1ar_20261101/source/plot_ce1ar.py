"""Scientific plots from actually executed CE1AR parent-owner data, not new IVPs."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
DATA=ROOT/'data'
FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)

def read(name):
 with (DATA/name).open(newline='') as f:return list(csv.DictReader(f))

beams=read('CE1AR_FIXED_Z_BEAMS.csv')
responses=read('CE1AR_FIXED_Z_RESPONSE.csv')
axes=('x','y','z')
fig,ax=plt.subplots(figsize=(7.4,4.6))
for d in axes:
 r=sorted((x for x in beams if x['GL']=='24' and x['eps']=='0.0' and x['direction']==d), key=lambda x:float(x['z_target']))
 ax.plot([float(q['z_target']) for q in r],[float(q['D_A_over_cTstar']) for q in r],marker='o',label=f'{d} axis')
ax.plot([float(q['z_target']) for q in r],[float(q['equal_volume_isotropic_D_A']) for q in r],ls='--',color='black',label='equal-volume isotropic proxy')
ax.set(xlabel='Observed redshift z',ylabel=r'$D_A/(cT_\star)$',title='Source-owned GL24 Bianchi-I fixed-z angular distance')
ax.legend();fig.tight_layout()
for ext in ('.png','.svg'):fig.savefig(FIG/('CE1AR_fixed_z_DA_axes'+ext),dpi=175)
plt.close(fig)

fig,ax=plt.subplots(figsize=(7.4,4.6))
for d in axes:
 r=sorted((x for x in beams if x['GL']=='24' and x['eps']=='0.0' and x['direction']==d),key=lambda x:float(x['z_target']))
 ax.plot([float(q['z_target']) for q in r],[100*float(q['fractional_anisotropy_vs_isotropic_proxy']) for q in r],marker='o',label=d)
ax.axhline(0,color='grey',lw=.8);ax.set(xlabel='Observed redshift z',ylabel=r'$100[D_A/D_{A,iso\,proxy}-1]$ (%)',title='Geometric anisotropy, not an observational likelihood')
ax.legend();fig.tight_layout()
for ext in ('.png','.svg'):fig.savefig(FIG/('CE1AR_fixed_z_anisotropy'+ext),dpi=175)
plt.close(fig)

fig,ax=plt.subplots(figsize=(7.4,4.6))
for d in axes:
 r=sorted((x for x in responses if x['GL']=='24' and x['direction']==d),key=lambda x:float(x['z_target']))
 xx=np.array([float(q['z_target']) for q in r]); yy=1e9*np.array([float(q['central_secant_D_A_at_fixed_z']) for q in r]);
 direct=1e9*np.array([float(q['direct_D_A_secant_at_fixed_emission_clock']) for q in r]);
 ax.plot(xx,yy,marker='o',label=f'{d}: fixed-z total')
 ax.plot(xx,direct,ls=':',label=f'{d}: fixed emitter')
ax.axhline(0,color='grey',lw=.8);ax.set(xlabel='Observed redshift z',ylabel=r'$10^9\,\partial_\epsilon[D_A/(cT_\star)]$',title='Implicit emission-clock correction dominates source response')
ax.legend(fontsize=8,ncol=2);fig.tight_layout()
for ext in ('.png','.svg'):fig.savefig(FIG/('CE1AR_fixed_z_clock_decomposition'+ext),dpi=175)
plt.close(fig)
print('science figures:',[x.name for x in FIG.iterdir()])
