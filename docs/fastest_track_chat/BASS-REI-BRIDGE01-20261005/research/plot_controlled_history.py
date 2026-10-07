from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parents[1];out=r/'figures';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.grid':True,'grid.alpha':.22,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,3,figsize=(12.8,4.1))
for n,col,ls in [(1000,'#cc7733','--'),(2000,'#1c668d','-')]:
 z=json.loads((r/f'evidence/history_{n}.json').read_text());t=np.array(z['time_edges_seconds'])/(365.25*86400*1e6);ne=np.array([s['ne_m3'] for s in z['states']]);tau=np.array(z['optical_depth']);tail=z['observer_optical_depth'];dt=np.diff(np.array(z['time_edges_seconds']));p=np.array(z['interval_probability'])
 axs[0].plot(t,ne,color=col,ls=ls,label=f'{n:,} intervals',lw=1.6);axs[1].plot(t,1e4*(tau-tail),color=col,ls=ls,lw=1.6);axs[2].plot((t[1:]+t[:-1])/2,1e18*p/dt,color=col,ls=ls,lw=1.6)
for ax in axs:ax.set_xlabel('Normal time [Myr]')
axs[0].set_ylabel(r'Proper electron density $n_e$ [m$^{-3}$]');axs[0].legend(frameon=False);axs[1].set_ylabel(r'Remaining depth $(\tau-\tau_{\rm tail})\times10^4$');axs[2].set_ylabel(r'Cell-mean visibility $P_i/\Delta t_i$ [$10^{-18}$ s$^{-1}$]')
fig.suptitle('Actual controlled FT03 evolution → BASS Thomson visibility',fontsize=14,y=.99);fig.text(.5,.01,'Static background; RCT OFF; observer tail = 0.2. Cold-Thomson model test, not a cosmological prediction.',ha='center',fontsize=9,color='#454545');fig.tight_layout(rect=[0,.04,1,.92]);fig.savefig(out/'BASS_REI_CONTROLLED_VISIBILITY.png',dpi=180);fig.savefig(out/'BASS_REI_CONTROLLED_VISIBILITY.pdf');plt.close(fig)
