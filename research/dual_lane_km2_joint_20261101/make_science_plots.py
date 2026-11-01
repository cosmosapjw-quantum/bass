"""Source-owned science plots for KM2 photon emission/scattering chronology.
Each plot independent, no multi-axes collage. Neutral Matplotlib default colors.
"""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
FIG=HERE/'figures'
FIG.mkdir(parents=True,exist_ok=True)
data=json.loads((HERE/'results'/'KM2_FIRST_SCATTER_JOINT_RESULTS.json').read_text())
rec={(r['gl'],r['k']):r for r in data['data']}

# Positive double-time energy contributions; no fictitious count probability.
with np.load(HERE/'results'/'KM2_FIRST_SCATTER_JOINT_GL16_U40.npz',allow_pickle=False) as z:
    joint=z['joint_emission_scatter_energy'];em=z['emission_time'];sc=z['scattering_time']
idx_s,idx_e=np.nonzero(joint)
fig,ax=plt.subplots(figsize=(8.5,5.1))
plot=ax.scatter(em[idx_e],sc[idx_s],c=np.log10(joint[idx_s,idx_e]),s=8,marker='s',linewidths=0,rasterized=True)
fig.colorbar(plot,ax=ax,label=r'$\log_{10}$ observer-energy contribution')
ax.plot([0,.25],[0,.25],linestyle=':',linewidth=1)
ax.set_xlabel(r'Emitted proper time $u_\mathrm{em}$')
ax.set_ylabel(r'Exactly-one scatter time $u_\mathrm{sc}$')
ax.set_xlim(0,.25);ax.set_ylim(0,.25)
ax.set_title('Original GL16 Ly-alpha emission x Thomson scattering, U=0.25')
fig.tight_layout();fig.savefig(FIG/'emission_scatter_joint_GL16.png',dpi=180);fig.savefig(FIG/'emission_scatter_joint_GL16.svg');plt.close(fig)

x=rec['GL16',40]['emission_groups'];inds=np.arange(5)
labels=[str(r['source_emission_bin']).replace('0.0','0').replace('0.05','0.05') for r in x]
fig,ax=plt.subplots(figsize=(8.4,4.8))
ax.bar(inds,[r['fraction'] for r in x])
ax.set_xticks(inds,labels,rotation=0)
ax.set_ylabel('Fraction of exactly-one-scattered observer energy')
ax.set_xlabel('Original packet emission time bin (dimensionless u)')
ax.set_ylim(bottom=0)
ax.set_title('Original emission age composition of observed first scattering')
fig.tight_layout();fig.savefig(FIG/'emission_group_energy_GL16.png',dpi=180);fig.savefig(FIG/'emission_group_energy_GL16.svg');plt.close(fig)

fig,ax=plt.subplots(figsize=(8.4,4.8))
ax.plot(inds,[100*r['mean_pol'] for r in x],'o-')
ax.set_xticks(inds,labels)
ax.set_xlabel('Original packet emission time bin (dimensionless u)')
ax.set_ylabel('Mean linear polarization of emission-conditioned field (%)')
ax.set_title('Polarized Thomson imprint depends on original emission epoch')
fig.tight_layout();fig.savefig(FIG/'emission_group_polarization_GL16.png',dpi=180);fig.savefig(FIG/'emission_group_polarization_GL16.svg');plt.close(fig)

fig,ax=plt.subplots(figsize=(8.4,4.8))
ax.plot(inds,rec['GL16',40]['emission_group_logfrequency_centroids'],'o-')
ax.set_xticks(inds,labels)
ax.set_xlabel('Original packet emission time bin (dimensionless u)')
ax.set_ylabel(r'Mean $\ln(\nu/\nu_{\mathrm{Ly}\alpha})$ at observer')
ax.set_title('Source-conditioned observer spectral centroids (packet estimator)')
fig.tight_layout();fig.savefig(FIG/'emission_group_logfrequency_GL16.png',dpi=180);fig.savefig(FIG/'emission_group_logfrequency_GL16.svg');plt.close(fig)

fig,ax=plt.subplots(figsize=(8.4,4.8))
for gl in ('GL12','GL16'):
    records=[rec[gl,k] for k in (8,16,24,32,40)]
    u=[r['u_obs'] for r in records]
    ax.plot(u,[r['mean_emission_time'] for r in records],marker='o',label=gl+' mean emission')
    ax.plot(u,[r['mean_scatter_time'] for r in records],marker='s',linestyle='--',label=gl+' mean scatter')
ax.plot([0,.25],[0,.25],linestyle=':',linewidth=1,label='observation time')
ax.set_xlabel('Observation time U')
ax.set_ylabel('Mean original source and collision time u')
ax.set_title('Coupled emission/scattering chronology across original snapshots')
ax.legend(fontsize=9)
fig.tight_layout();fig.savefig(FIG/'emission_scatter_chronology.png',dpi=180);fig.savefig(FIG/'emission_scatter_chronology.svg');plt.close(fig)
print('FIGURES',len(list(FIG.glob('*.png'))),'PNG',len(list(FIG.glob('*.svg'))),'SVG')
