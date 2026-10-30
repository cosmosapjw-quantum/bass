from pathlib import Path
import csv, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'figures').mkdir(parents=True, exist_ok=True)
with (ROOT/'data'/'COUPLED_SIXCELL_DENSE_TIME_SKY.csv').open() as f:
 rows=[r for r in csv.DictReader(f) if r['GL']=='64']
u=np.array([float(r['u']) for r in rows]); C4=np.array([float(r['C4_fractional']) for r in rows]);raw=np.array([float(r['C4_raw_energy']) for r in rows]);
fig,ax=plt.subplots(figsize=(8.5,4.9));ax.plot(u,C4/C4[0],label=r'Fractional normalized $C_4^{\alpha}(u)/C_4^{\alpha}(0)$',linewidth=1.8);ax.plot(u,raw/raw[0],label=r'Raw bolometric $C_4^{U}(u)/C_4^{U}(0)$',linewidth=1.8);ax.axhline(1,linestyle=':',linewidth=.8)
ax.set_xlabel(r'Proper time $u=t/T_\star$');ax.set_ylabel('Ratio to original initial sky');ax.set_title('BASS CE1-AE: original source, opposite l=4 energy and pattern trends');ax.grid(alpha=.2);ax.legend();fig.tight_layout();
fig.savefig(ROOT/'figures'/'CE1AE_ORIGINAL_GL64_C4_PATTERN_VS_ENERGY.png',dpi=185);plt.close(fig)
res=json.loads((ROOT/'data'/'CONTINUOUS_TIME_INTEGRATED_PHYSICS.json').read_text())['data'];orders=[6,8,16,64]
fig,ax=plt.subplots(figsize=(8.5,4.9))
for i in range(3):
 vals=[res[str(n)]['time_Gram_eigenvalues_numeric'][i] for n in orders]
 ax.plot(orders,vals,marker='o',label=rf'$\lambda_{i+1}(G_{{GL}})$')
ax.set_yscale('log');ax.set_xticks(orders);ax.set_xlabel('Original six-cell Gauss–Legendre order');ax.set_ylabel(r'Deterministic time-integral Gram eigenvalues (dimensionless $du$)');ax.set_title('Three temporal l=4 modes across actual coupled Einstein–Vlasov sources');ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(ROOT/'figures'/'CE1AE_INTEGRAL_L4_THREE_MODES_GL_CONVERGENCE.png',dpi=185);plt.close(fig)
for p in sorted((ROOT/'figures').glob('*.png')):print(p.name,p.stat().st_size)
