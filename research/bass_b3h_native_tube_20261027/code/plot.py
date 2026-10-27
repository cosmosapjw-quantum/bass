"""New figure only, from newly saved selected tube data; no science recomputation."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
a=np.genfromtxt(ROOT/'results/TUBE_TRACE.csv',delimiter=',',names=True)
r=json.loads((ROOT/'results/TUBE_RESULT.json').read_text())
fig,axes=plt.subplots(2,1,figsize=(7,6),layout='constrained')
axes[0].plot(a['u']/r['native_clock']['delta_eta'],a['f_in'],label='native incoming total')
axes[0].plot(a['u']/r['native_clock']['delta_eta'],a['departure'],label='strict-past PL row 140')
axes[0].plot(a['u']/r['native_clock']['delta_eta'],a['wien'],label='native Wien')
axes[0].set(ylabel='Occupation f',title='Native Lyalpha finite incoming tube: z = 1100 cell')
axes[0].legend()
axes[1].plot(a['u']/r['native_clock']['delta_eta'],a['J_volume'],label='common reference volume: exp(3u)')
axes[1].plot(a['u']/r['native_clock']['delta_eta'],a['energy_weight'],label='pulled-back energy: exp(4u)')
axes[1].set(xlabel='Native local clock u / delta eta',ylabel='Dimensionless integration weight')
axes[1].legend()
fig.savefig(ROOT/'figures/NATIVE_INCOMING_TUBE.png',dpi=160)
print('Saved figures/NATIVE_INCOMING_TUBE.png from results/TUBE_TRACE.csv')
