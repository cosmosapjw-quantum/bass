"""CE1-R inspect immutable workflow-artifact Rust derivative atlas (not a CI producer).

Computes C2/C4 and their analytic time slopes from saved BASS-native CSV,
checks Simpson time-integral closure, compares angular resolutions and plots.
This post-processing is binary64 model-data analysis; no interval/likelihood.
"""
import argparse,csv,io,json,zipfile
from pathlib import Path
import numpy as np

CHANNELS=('stored_ref8','stored_ref16','gl24','gl40')

def alms(row,l,der=False):
    pre='da' if der else 'a'
    return np.array([complex(row[f'{pre}_{l}_{m}_re'],row[f'{pre}_{l}_{m}_im']) for m in range(-l,l+1)])

def C(row,l):
    v=alms(row,l);return float(np.vdot(v,v).real/(2*l+1))

def Cp(row,l):
    v=alms(row,l);vp=alms(row,l,True)
    return float(2*np.vdot(v,vp).real/(2*l+1))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--zip',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    results={'schema':'bass.ce1r.liouville_atlas_final.v1','source_type':'normal-frame unpolarized energy sky, NOT CMB temperature',
             'channels':{},'comparisons':{},'upper_dag':'9/15','production_ready':False}
    plot=[]
    with zipfile.ZipFile(args.zip) as z:
        assert z.testzip() is None
        for chan in CHANNELS:
            rows=[{k:float(v) for k,v in rec.items()} for rec in csv.DictReader(io.StringIO(z.read(chan+'.csv').decode()))]
            orig=json.loads(z.read(chan+'.json'))
            assert len(rows)==41 and orig['states']==41 and len(rows[0])>100
            t=np.array([v['u'] for v in rows]);dt=float(t[1]-t[0]);assert np.max(abs(np.diff(t)-dt))<2e-15
            obj={'rays':orig['rays'],'Eprime_final':rows[-1]['Eprime'],'C':{},'Cprime':{},'simpson_closure_gap':{},'max_validation_error':orig['errors']}
            for l in (2,4):
                cs=np.array([C(r,l) for r in rows]);dcs=np.array([Cp(r,l) for r in rows]);
                integ=dt/3*(dcs[0]+dcs[-1]+4*dcs[1:-1:2].sum()+2*dcs[2:-1:2].sum())
                gap=abs(integ-(cs[-1]-cs[0]));
                obj['C'][str(l)]={'initial':float(cs[0]),'final':float(cs[-1]),'delta':float(cs[-1]-cs[0])}
                obj['Cprime'][str(l)]={'initial':float(dcs[0]),'final':float(dcs[-1]),'min':float(dcs.min()),'max':float(dcs.max())}
                obj['simpson_closure_gap'][str(l)]=float(gap)
                # Temporal check is not a new error enclosure; tolerance adopted before sampling.
                assert gap<5e-10,(chan,l,gap)
                plot.append((chan,l,t,dcs))
            results['channels'][chan]=obj
    for l in (2,4):
        ref=results['channels']['gl40']['Cprime'][str(l)]['final']
        for chan in CHANNELS[:-1]:
            actual=results['channels'][chan]['Cprime'][str(l)]['final']
            results['comparisons'][chan+'_vs_gl40_C'+str(l)+'prime']={
                'signed_difference':float(actual-ref),'relative_absolute_difference':float(abs(actual-ref)/abs(ref))}
    (out/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for l in (2,4):
        fig,ax=plt.subplots(figsize=(7.1,4.3))
        for chan,ll,t,dcs in plot:
            if ll==l:ax.plot(t,dcs,label=chan)
        ax.set_xlabel('Proper time  u = t/T*')
        ax.set_ylabel(f'dC{l}/du  (energy-sky units squared)')
        ax.set_title(f'BASS Rust: {"quadrupole" if l==2 else "hexadecapole"} energy-sky evolution')
        ax.grid(alpha=.25);ax.legend(fontsize=8)
        fig.tight_layout();fig.savefig(out/f'CE1R_C{l}_PRIME.png',dpi=180);plt.close(fig)
    print(json.dumps(results,indent=2)[:12000])
    print('CE1R_S2_SIMPSON_LIOUVILLE_C2_C4_CLOSURE_PASS')
    return results
if __name__=='__main__':main()
