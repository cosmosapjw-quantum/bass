"""Single saved-result-only new-unit figure invocation."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def main():
    d=json.loads((ROOT/'results/INVERSION_NET_RESULT.json').read_text())
    fig,axs=plt.subplots(2,2,figsize=(11,7.5),layout='constrained')
    for k,c in [(5126,'#2563a6'),(5127,'#be4d24')]:
        rr=[r for r in d['rows'] if r['index']==k]
        axs[0,0].plot([r['bin'] for r in rr],[r['tau'] for r in rr],'o',color=c,label=str(k))
        axs[0,1].plot([r['bin'] for r in rr],[r['relative_x1s_vs_primary'] for r in rr],'o',color=c,label=str(k))
    axs[0,0].set(xlabel='Native virtual bin',ylabel='Inferred optical depth',title='Twelve stored-triple inverses')
    axs[0,1].set(xlabel='Native virtual bin',ylabel='Relative x1s difference vs bin 273',title='Cross-bin numerical diagnostic')
    f=d['finite_photon'];xx=[];yy=[]
    for s in f['segments']:xx.extend([s['a'],s['b']]);yy.extend([s['j_a'],s['j_b']])
    axs[1,0].plot(xx,yy,'o-',color='#398161');axs[1,0].set(xlabel='Local affine eta coordinate u',ylabel='Net departure occupation j',title='New net Ly-alpha represented trace')
    q=d['QSS_storage'];axs[1,1].bar(['Delta N2s','Delta N2p'],[q['DeltaN2s_per_V0_m3'],q['DeltaN2p_per_V0_m3']],color=['#725b91','#ae7041'])
    axs[1,1].set(ylabel='Inventory change per V0 [m^-3]',title='QSS algebraic storage change; physical refill open')
    for a in axs.flat:a.grid(alpha=.22)
    axs[0,0].legend();axs[0,1].legend()
    fig.suptitle('Native [5126,5127] endpoint inversion and finite photon return\nNumerical diagnostics; physical accuracy radii remain null',fontsize=12)
    fig.savefig(ROOT/'figures/NATIVE_HISTORY_INVERSION_NET.png',dpi=170)
    plt.close(fig)
    (ROOT/'results/PLOT_RECEIPT.json').write_text(json.dumps(dict(source='INVERSION_NET_RESULT.json',scientific_function_calls=0,output='figures/NATIVE_HISTORY_INVERSION_NET.png'),indent=2))
if __name__=='__main__':main()
