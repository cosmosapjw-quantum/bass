#!/usr/bin/env python3
"""Actual CE1AI source-owned scientific figures, no mock curves or visual placeholders."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data';OUT=ROOT/'figures';OUT.mkdir(parents=True,exist_ok=True)

def read(name,gl='16'):
 with (DATA/name).open(newline='') as f:
  return [r for r in csv.DictReader(f) if r['GL']==gl]

def plot_lines(name,title,ylabel,chosen):
 data=read('CE1AI_SOURCE_TANGENT_PHYSICAL.csv')
 fig,ax=plt.subplots(figsize=(9,5))
 for mode,field,label in chosen:
  rr=[r for r in data if r['mode']==mode]
  ax.plot([float(x['u']) for x in rr],[float(x[field]) for x in rr],label=label,linewidth=1.8)
 ax.axhline(0,linewidth=.7,color='gray')
 ax.set(xlabel='Normalized proper time u=t/Tstar',ylabel=ylabel,title=title)
 ax.legend(loc='best');ax.grid(True,alpha=.22);fig.tight_layout()
 fig.savefig(OUT/name,dpi=170);plt.close(fig)


def main():
 plot_lines('CE1AI_DARK_SOURCE_HARMONIC_EMERGENCE.png',
   'Previously invisible l=2,4 source variation becomes visible through Einstein-Vlasov flow',
   'd fractional harmonic coefficient / d epsilon',
   [('DARK_L2L4','dalpha42','d alpha_42'),('DARK_L2L4','dalpha44','d alpha_44'),('DARK_L2L4','dalpha40','d alpha_40')])
 plot_lines('CE1AI_DARK_C2_C4_RESPONSE.png','Dark source mode: physical fractional multipole responses',
   'd C_l / d epsilon', [('DARK_L2L4','dC2','d C2'),('DARK_L2L4','dC4','d C4')])
 plot_lines('CE1AI_5SOURCE_C2_RESPONSE.png','Initial six-cell mass-transfer directions: quadrupole power response',
   'd C2 / d epsilon',[(n,'dC2',n) for n in ('EQ_X','EQ_Y','POL_X','POL_MID','POL_Y')])
 plot_lines('CE1AI_5SOURCE_C4_RESPONSE.png','Initial six-cell mass-transfer directions: l=4 power response',
   'd C4 / d epsilon',[(n,'dC4',n) for n in ('EQ_X','EQ_Y','POL_X','POL_MID','POL_Y')])
 plot_lines('CE1AI_DARK_SHEAR_WORK_RESPONSE.png','Dark angular mode causes downstream shear-radiation work variation',
   'd W / d epsilon',[('DARK_L2L4','dW','shear work response')])
 data=read('CE1AI_HARMONIC_RESPONSE_SINGULAR_VALUES.csv');times=np.array([float(x['u']) for x in data])
 fig,ax=plt.subplots(figsize=(9,5))
 for k in range(1,6):
  vals=np.array([max(float(x[f's{k}']),1e-19) for x in data]);ax.plot(times,vals,label=f's{k}')
 ax.set_yscale('log');ax.set(xlabel='Normalized proper time u=t/Tstar',ylabel='Singular values of 5x5 source-to-harmonic Jacobian',
   title='Numerical fifth response singular value emerges from exact initial rank-four constraint')
 ax.grid(True,alpha=.22);ax.legend();fig.tight_layout();fig.savefig(OUT/'CE1AI_MULTIPOLE_SOURCE_RESPONSE_SPECTRUM.png',dpi=170);plt.close(fig)
 # Independent numerical response matrix visualization at the endpoint.
 tans=read('CE1AI_SOURCE_TANGENT_PHYSICAL.csv')
 names=['EQ_X','EQ_Y','POL_X','POL_MID','POL_Y']
 fields=['dalpha20','dalpha22','dalpha40','dalpha42','dalpha44']
 mx=np.array([[float([r for r in tans if r['mode']==name][-1][field]) for name in names] for field in fields])
 fig,ax=plt.subplots(figsize=(9,5));im=ax.imshow(mx,aspect='auto')
 ax.set(xticks=range(5),xticklabels=names,yticks=range(5),yticklabels=['a20','a22','a40','a42','a44'],
   title='GL16 endpoint physical source-to-l2/l4 response Jacobian')
 for i in range(5):
  for j in range(5):ax.text(j,i,f'{mx[i,j]:+.2f}',ha='center',va='center',fontsize=8,color='black' if abs(mx[i,j])<2 else 'white')
 fig.colorbar(im,ax=ax,label='d alpha / d epsilon');fig.tight_layout();fig.savefig(OUT/'CE1AI_ENDPOINT_HARMONIC_RESPONSE_MATRIX.png',dpi=170);plt.close(fig)
 print('CE1AI_REAL_PHYSICAL_FIGURES',len(list(OUT.glob('CE1AI_*.png'))))

if __name__=='__main__':main()
