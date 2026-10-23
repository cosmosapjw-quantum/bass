"""One layout/label repair from unchanged plotted CSV; retain the first render."""
from pathlib import Path
import os,csv,json,shutil,hashlib
os.environ.setdefault('MPLCONFIGDIR','/tmp/bass-g1b-mpl')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
FIG=ROOT/'figures'
def main():
    old=FIG/'initial_render';old.mkdir(exist_ok=False)
    name='fixed_angular_refinement'
    for ext in ('png','svg','csv'):shutil.copy2(FIG/f'{name}.{ext}',old/f'{name}.{ext}')
    with (FIG/f'{name}.csv').open() as f:rows=list(csv.DictReader(f))
    fig,ax=plt.subplots(figsize=(7.6,5.4))
    for case,marker in zip(dict.fromkeys(r['case'] for r in rows),['o','s','^','v','D','x']):
        rr=[r for r in rows if r['case']==case]
        ax.semilogy([int(r['nmu']) for r in rr],[float(r['max_error']) for r in rr],marker=marker,label=case.replace('_',' '))
    ax.axhline(2e-8,linestyle=':',label='Frozen acceptance gate')
    ax.set(xlabel=r'Polar order $n_\mu$; azimuthal order $n_\phi=2n_\mu$',ylabel='Normalized tensor / number-current difference',
           title='Fixed-state angular refinement: six source states',ylim=(1e-16,1))
    ax.grid(True,alpha=.25);ax.legend(fontsize=8,ncol=3,loc='upper center',bbox_to_anchor=(.5,-.18));fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(FIG/f'{name}.{ext}',dpi=160,bbox_inches='tight')
    plt.show();plt.close(fig)
    (FIG/'REPAIR.json').write_text(json.dumps({'reason':['first legend covered near-floor curves','number-current denominator also used, so clarify label'],
        'same_csv_bytes':(FIG/f'{name}.csv').read_bytes()==(old/f'{name}.csv').read_bytes(),'scientific_reruns':0,'targeted_renders':1,
        'first_python_display':'ClientConnectorError after display; all9 outputs and MANIFEST existed and were inspected; no scientific failure'},indent=2)+'\n')
if __name__=='__main__':main()
