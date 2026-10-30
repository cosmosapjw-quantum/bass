#!/usr/bin/env python3
"""Plots from actual CE1-AA physical time samples and source bounds, not simulations."""
from pathlib import Path
import csv,json,matplotlib
from fractions import Fraction
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path(__file__).resolve().parents[1];D=R/'data';P=R/'figures';P.mkdir(exist_ok=True)
S=json.loads((D/'SCIENCE_RESULTS.json').read_text())
for n in (6,8):
    with (D/f'GL{n}_CUMULATIVE_41_PREFIX_SPECTRA.csv').open() as f:rows=list(csv.DictReader(f))
    t=np.array([float(x['last_u']) for x in rows]);v=np.array([float(x['lambda2_numeric']) for x in rows]);e=np.array([float(Fraction(x['source_weyl_upper_decimal'])) for x in rows]);
    plt.figure(figsize=(7.4,4.6))
    plt.plot(t,v,label=r'original stored GL: $\lambda_2$ (numerical visualization)')
    plt.plot(t,e,label=r'$N\,\epsilon_{K_4}$ (prior source-only rigorous upper)')
    u=S['channels'][str(n)]['first_certified_nonzero_continuum_secondary_mode_time']
    plt.axvline(u,ls='--',label=f'first certified positive source mode u={u:.3f}')
    plt.xlabel(r'last proper-time sample $u=t/T_*$');plt.ylabel(r'Gram eigenvalue / bound');plt.title(f'BASS GL{n}: fixed DOP853 geometry, continuum angular source')
    plt.yscale('symlog',linthresh=1e-10);plt.legend(fontsize=8);plt.tight_layout();plt.savefig(P/f'GL{n}_SECOND_MODE_SOURCE_CERTIFICATION.png',dpi=180);plt.close()
    p=D/f'GL{n}_MPFR192_K4_1681.csv'
    with p.open() as f:lines=list(csv.DictReader(f))
    a=np.array([0.5*(float(x['K4_delta_lbound_float_outward'])+float(x['K4_delta_ubound_float_outward'])) for x in lines]).reshape(41,41)
    plt.figure(figsize=(5.8,5.0));plt.imshow(a,origin='lower',extent=[0,.08,0,.08],aspect='equal')
    plt.colorbar(label=r'$K_{4}^{\delta}(u,v)$, MPFR192 directed enclosure midpoint')
    plt.xlabel(r'$v=t/T_*$');plt.ylabel(r'$u=t/T_*$');plt.title(f'GL{n}: original source sky at stored geometry')
    plt.tight_layout();plt.savefig(P/f'GL{n}_MPFR192_K4_SKY.png',dpi=180);plt.close()
print('PLOTS',[(p.name,p.stat().st_size) for p in P.glob('*.png')])
