"""One saved-result-only plot. No physics modules imported or evaluated."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
v=json.loads((ROOT/'results/FINITE_CHANNEL_RESULT.json').read_text())
o=v['finite_owners'];cor=v['baseline_correction'];groups=o['channel_groups']
labels=['Bound-free','2s / 2p mixing','Two-photon / Raman','Core diffusion','Virtual diffusion','Ly-beta / gamma','Ly-alpha']
keys=['bound_free','mixing','two_photon_Raman','core_diffusion','virtual_diffusion','Lybeta_gamma','Lyalpha']
counts=[float(groups[k]['atomic_change'][1][0])+float(groups[k]['atomic_change'][2][0]) for k in keys]
counts.extend([float(o['interface_storage'][0][0]),float(o['interface_storage'][1][0])]);labels+=['Storage: delta Ns','Storage: delta Np']
fig,ax=plt.subplots(1,3,figsize=(18,7),layout='constrained')
colors=['#3566A5' if x>=0 else '#B64A42' for x in counts];colors[-2:]=['#B47A16','#B47A16']
ax[0].barh(range(len(counts)),counts,color=colors);ax[0].set_yticks(range(len(counts)),labels);ax[0].invert_yaxis();ax[0].set_xscale('symlog',linthresh=1e-12)
ax[0].set_xlim(-40000,40000);ax[0].set_xticks([-1e4,-1,-1e-8,0,1e-8,1,1e4],labels=[r'$-10^4$',r'$-1$',r'$-10^{-8}$','0',r'$10^{-8}$','1',r'$10^4$']);ax[0].minorticks_off();ax[0].axvline(0,color='black',linewidth=.8);ax[0].set_xlabel('Signed change of interface count per V0 (symlog)');ax[0].set_title('Atomic channels and resolved finite storage')
for j in [-2,-1]:ax[0].annotate(f'{counts[j]:+.4e}',(counts[j],len(counts)+j),xytext=(-80,-4),textcoords='offset points',fontsize=9,color='#805400')
energies=[float(x) for x in o['event_sector_energy_J_m3'][1:]];enlabels=['Atomic internal','Gas kinetic','Ambient radiation','Ly-alpha']
ax[1].bar(enlabels,energies,color=['#B64A42' if x<0 else '#3566A5' for x in energies]);ax[1].axhline(0,color='black',linewidth=.8);ax[1].tick_params(axis='x',rotation=25);ax[1].set_ylabel('Signed event energy per V0 [J m^-3]');ax[1].set_title('Separate event-energy owners')
ax[1].text(.02,.02,'Common V0 = 1 m^3\nGeometry work is stored separately',transform=ax[1].transAxes,fontsize=10,va='bottom')
old=float(cor['old_net_count_reference']);new=float(cor['new_net_count']);corr=float(cor['DeltaN_correction'])
ax[2].bar(['Saved native baseline','New finite model'],[old,new],color=['#777777','#3566A5']);ax[2].set_ylabel('Net Ly-alpha photons per V0 [m^-3]');ax[2].set_title('Baseline reuse and additional correction');ax[2].set_ylim(0,max(old,new)*1.25)
for j,x in enumerate([old,new]):ax[2].text(j,x,f'{x:.8f}',ha='center',va='bottom',fontsize=11)
ax[2].text(.5,.92,f'Added correction = {corr:+.8f} photons / V0',transform=ax[2].transAxes,ha='center',fontsize=11)
for a in ax:a.grid(axis='x' if a==ax[0] else 'y',alpha=.2);a.set_axisbelow(True)
fig.suptitle('Frozen-left activity-clock QSS channel completion — saved finite result',fontsize=16)
path=ROOT/'results/FINITE_CHANNEL_COMPLETION.png';fig.savefig(path,dpi=160);plt.close(fig)
print(json.dumps(dict(path=str(path),source='results/FINITE_CHANNEL_RESULT.json',panels=3,scientific_evaluations=0,core_rhs_calls=0)))
