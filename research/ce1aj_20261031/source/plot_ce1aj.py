#!/usr/bin/env python3
"""Draw actual CE1AJ Bianchi-I physical dark-response data; no CMB claims."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def rows(n):
    with (ROOT/'data'/n).open(newline='') as f:return list(csv.DictReader(f))
def main():
    tan=rows('CE1AJ_DARK_TANGENT_PHYSICAL.csv')
    fin=rows('CE1AJ_DARK_FINITE_IVP.csv')
    out=ROOT/'figures';out.mkdir(exist_ok=True,parents=True)
    for win,col,name,title in [
        ('micro_certified','dalpha42','CE1AJ_MICRO_FINITE_TRANSFER.png','Certified continuum near-initial dark-to-l4 response'),
        ('full_numeric','dalpha42','CE1AJ_FULL_DARK_ALPHA42.png','Full model numerical dark-to-l4 response'),
        ('full_numeric','dC4','CE1AJ_FULL_C4_RESPONSE.png','Fractional C4 source sensitivity'),
        ('full_numeric','dW','CE1AJ_DARK_WORK_RESPONSE.png','Shear-radiation work source sensitivity')]:
        plt.figure(figsize=(7.4,4.6))
        for gl in (6,8,16):
            r=[x for x in tan if x['window']==win and int(x['GL'])==gl]
            x=np.array([float(z['u']) for z in r])
            y=np.array([float(z[col]) for z in r])
            if win=='micro_certified':x*=1e6;y*=1e6
            plt.plot(x,y,label=f'GL{gl}',lw=1.5)
        if win=='micro_certified':
            plt.plot([0,1],[0,-.5],'k--',label='Exact continuum strict upper -u/2')
        plt.xlabel('u / 1e-6' if win=='micro_certified' else 'u=t/Tstar')
        plt.ylabel(col+(' / 1e-6' if win=='micro_certified' else ''))
        plt.title(title);plt.legend(fontsize=8);plt.grid(alpha=.2);plt.tight_layout()
        plt.savefig(out/name,dpi=160);plt.close()
    plt.figure(figsize=(7.4,4.6))
    for gl in (6,8,16):
        f=[r for r in fin if int(r['GL'])==gl and r['window']=='full_numeric']
        xp=np.array([float(r['u']) for r in f if int(r['sign'])==1])
        ap=np.array([float(r['alpha42']) for r in f if int(r['sign'])==1])
        am=np.array([float(r['alpha42']) for r in f if int(r['sign'])==-1])
        plt.plot(xp,(ap-am)/.002,label=f'nonlinear ± family GL{gl}')
    plt.xlabel('u=t/Tstar');plt.ylabel('central d alpha42/d epsilon')
    plt.title('Genuine nonlinear source family response');plt.legend(fontsize=8)
    plt.grid(alpha=.2);plt.tight_layout()
    plt.savefig(out/'CE1AJ_FINITE_PAIR_VS_TANGENT.png',dpi=160);plt.close()
    print('CE1AJ_REAL_SCIENTIFIC_FIGURES',len(list(out.glob('CE1AJ_*.png'))))
if __name__=='__main__':main()
