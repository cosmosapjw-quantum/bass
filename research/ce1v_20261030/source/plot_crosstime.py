"""Physical CE1-V two-epoch angular energy statistics, no spectral temperature."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]


def plot():
 for ell in (2,4):
  fig,ax=plt.subplots(figsize=(7.2,5.3))
  arr=np.load(ROOT/'data'/'GL8_two_time_rotation_average.npz')
  u=arr['u'];z=arr[f'rho{ell}']
  im=ax.imshow(z,origin='lower',extent=[u[0],u[-1],u[0],u[-1]],aspect='auto')
  fig.colorbar(im,ax=ax,label=f'Cross-epoch pattern cosine $r_{ell}(u,v)$')
  ax.set(xlabel='Proper epoch v=t/T*',ylabel='Proper epoch u=t/T*',
       title=f'GL8 physical Einstein-Vlasov: normalized sky $\\ell={ell}$')
  fig.tight_layout();fig.savefig(ROOT/'figures'/f'GL8_r{ell}_two_time.png',dpi=165)
  plt.close(fig)
 fig,ax=plt.subplots(figsize=(7.3,4.5))
 for ell in (2,4):
  arr=np.load(ROOT/'data'/'GL8_two_time_rotation_average.npz')
  ax.plot(arr['u'],arr[f'D{ell}_squared'][0,:],label=rf'$D_{{{ell}}}^2(0,u)$')
 ax.set(xlabel='Proper epoch u=t/T*',ylabel='Squared fractional angular-pattern difference',
        title='Physical GL8 sky drift (fixed normal tetrad axes)')
 ax.grid(alpha=.25);ax.legend();fig.tight_layout()
 fig.savefig(ROOT/'figures'/'GL8_fractional_sky_drift.png',dpi=165)
 plt.close(fig)
if __name__=='__main__':plot()
