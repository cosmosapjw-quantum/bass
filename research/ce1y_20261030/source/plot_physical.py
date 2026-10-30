"""Render selected CE1-Y physics directly from saved source-locked numerical data."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; OUT=ROOT/'figures'; OUT.mkdir(exist_ok=True)

# Three separate plots: no multi-panel tricks.
for n in (6,8):
    arr=np.load(DATA/f'GL{n}_STEPS16_two_time_arrays.npz')
    k=arr['K4delta_RK4'];t=arr['u']
    plt.figure(figsize=(6.5,5.3))
    plt.imshow(k,origin='lower',extent=[t[0],t[-1],t[0],t[-1]],aspect='equal')
    plt.colorbar(label=r'$K_4^\delta(u,v)$')
    plt.xlabel(r'Proper time $u=t/T_*$');plt.ylabel(r'Proper time $v=t/T_*$')
    plt.title(f'BASS GL{n}, 16-panel Hermite, exact-source native Rust sky')
    plt.tight_layout();plt.savefig(OUT/f'GL{n}_N16_K4_PHYSICAL.png',dpi=170);plt.close()
arr=np.load(DATA/'GL8_STEPS4_two_time_arrays.npz');t=arr['u']
f=arr['K4delta_error_empirical']
plt.figure(figsize=(6.5,5.3))
plt.imshow(f,origin='lower',extent=[t[0],t[-1],t[0],t[-1]],aspect='equal')
plt.colorbar(label=r'RK4 4-panel - DOP853 $K_4^\delta$')
plt.xlabel(r'$u=t/T_*$');plt.ylabel(r'$v=t/T_*$')
plt.title('GL8 same physical source: empirical path-representation gap')
plt.tight_layout();plt.savefig(OUT/'GL8_RK4_N4_MINUS_DOP_K4.png',dpi=170);plt.close()
print('SCIENTIFIC_FIGURES',[(x.name,x.stat().st_size) for x in OUT.iterdir()])
