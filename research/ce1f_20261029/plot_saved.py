"""Regenerate publication figures from saved RESULTS, with no science rerun."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parent/'evidence'
d=json.loads((OUT/'RESULTS.json').read_text())
rows=d['rows'];f=[r['refinement'] for r in rows]
plt.rcParams.update({'font.size':10,'axes.labelsize':10,'axes.titlesize':10,
                     'legend.fontsize':8,'lines.linewidth':1.8})
for kind in ['SOURCE','GEOMETRY']:
    fig,ax=plt.subplots(figsize=(3.65,3.15),layout='constrained')
    if kind=='SOURCE':
        upper=[r['certificate']['source_pressure_upper'] for r in rows]
        gap=[r['measured_pressure_max'] for r in rows]
        labels=['Uniform certificate','51-probe quadrature gap']
        ylabel=r'$\max_i |\Delta P_i|$'
    else:
        upper=[r['certificate']['geometry_h_upper'] for r in rows]
        gap=[r['measured_h_max'] for r in rows]
        labels=['Exact-ODE upper bound','Numerical h difference']
        ylabel=r'$\max_i |T_\star\,\Delta H_i|$'
    ax.loglog(f,upper,'o-',label=labels[0])
    ax.loglog(f,gap,'s--',label=labels[1])
    if kind=='GEOMETRY':ax.axhline(d['target_h'],color='black',linestyle=':',label='Declared target')
    ax.set(xlabel='Cell refinement factor',ylabel=ylabel,xticks=f)
    ax.set_xticklabels(f);ax.grid(True,which='both',alpha=.2);ax.legend(loc='best')
    fig.savefig(OUT/f'{kind}_CONVERGENCE.png',dpi=200)
    fig.savefig(OUT/f'{kind}_CONVERGENCE.pdf')
    plt.close(fig)
print('SAVED_DATA_FIGURES_PASS')
