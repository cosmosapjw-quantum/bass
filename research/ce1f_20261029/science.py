"""Reproduce the bounded CE1-F physical and numerical campaign."""
import importlib.util
import json
import platform
import sys
import time
from fractions import Fraction
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mpmath as mp
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.special import eval_legendre

from bianchi.nonperturbative.einstein_tabulated_source import (
    TabulatedRadiation, certified_tabulated_geometry)

BASE = Path(__file__).resolve().parent
OUT = BASE/'evidence'
OUT.mkdir(exist_ok=True)
ROOT = BASE.parents[1]
spec = importlib.util.spec_from_file_location('independent_ce1f', ROOT/'tests/nonperturbative/test_einstein_tabulated_source.py')
refs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refs)
MU, PHI, ENERGY = refs.MU, refs.PHI, refs.ENERGY
T = .08
TARGET = 1e-5
t0, c0 = time.perf_counter(), time.process_time()


def continuum_initial():
    with mp.workdps(90):
        E = sum(mp.mpf(float(x)) for row in ENERGY for x in row)
        sx, sy = mp.mpf(.2), mp.mpf(-.13)
        sz = -(sx+sy)
        H = mp.sqrt((E+(sx*sx+sy*sy+sz*sz)/2)/3)
        return np.r_[np.zeros(3), [float(H+s) for s in (sx, sy, sz)]]


def integrate(moments, y0, rtol=2e-13, atol=2e-15, sign=1):
    def rhs(t, y):
        h = y[3:]
        return np.r_[h, -h.sum()*h+sign*moments(y[:3])[1]]
    sol = solve_ivp(rhs, [0, T], y0, method='DOP853', rtol=rtol, atol=atol,
                    dense_output=True)
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol


reference = refs.independent_cell_rule(MU, PHI, ENERGY, order=32)
reference48 = refs.independent_cell_rule(MU, PHI, ENERGY, order=48)
initial = continuum_initial()
refsol = integrate(reference, initial)
refsol48 = integrate(reference48, initial)
refloose = integrate(reference, initial, rtol=2e-10, atol=2e-12)
times = np.linspace(0, T, 101)
refy = refsol.sol(times)
quad_history_gap = float(np.max(abs(refy-refsol48.sol(times))))
tol_history_gap = float(np.max(abs(refy-refloose.sol(times))))
rng = np.random.default_rng(615237)
rows, histories = [], {}
for f in (1, 2, 4, 8, 16):
    source = refs.model(f)
    cert = certified_tabulated_geometry(source, end=T)
    box = np.array(cert['geometry_box_upper'])
    probes = np.r_[rng.uniform(0, 1, (48, 3))*box, [box, box/2, [0, 0, 0]]]
    pressure_gaps = [abs(source.moments(ell)[1]-reference48(ell)[1]) for ell in probes]
    pressure_gap = float(np.max(pressure_gaps))
    sol = integrate(source.moments, source.initial_state())
    y = sol.sol(times)
    gap = np.max(abs(y[3:]-refy[3:]), axis=0)
    Eg = np.array([source.moments(y[:3, k])[0] for k in range(len(times))])
    h = y[3:]
    constraint = h[0]*h[1]+h[0]*h[2]+h[1]*h[2]-Eg
    bc = cert['source_certificate']['parts_max_upper']
    omitted_cell_term_bound = bc['stored_ray']+bc['stored_mass']
    omitted_term_violations = int(sum(np.max(g) > omitted_cell_term_bound for g in pressure_gaps))
    row = dict(refinement=f, rays=len(source.cells), certificate=cert,
               measured_pressure_max=pressure_gap, measured_h_max=float(max(gap)),
               measured_constraint_max=float(max(abs(constraint))),
               positive_expansion_min=float(y[3:].min()),
               omitted_cell_term_bound=omitted_cell_term_bound,
               omitted_term_mutation_violations=omitted_term_violations,
               pressure_probes=len(probes))
    assert pressure_gap <= cert['source_pressure_upper']
    assert max(gap) <= cert['geometry_h_upper']
    assert np.all(y[:3] <= box[:, None]+1e-14)
    histories[f] = dict(h_error=gap.tolist(), constraint=constraint.tolist())
    rows.append(row)
    print(f"refinement={f} cells={len(source.cells)} pressure_upper={cert['source_pressure_upper']:.9g} h_upper={cert['geometry_h_upper']:.9g} measured_h={max(gap):.9g}", flush=True)

chosen = rows[-1]
assert chosen['certificate']['geometry_h_upper'] < TARGET
assert chosen['omitted_term_mutation_violations'] > 0

# Sign mutation: negative pressure in the metric RHS must break constraint law.
mutant = integrate(reference, initial, sign=-1)
ym = mutant.sol(times)
hm = ym[3:]
constraint_mutant = hm[0]*hm[1]+hm[0]*hm[2]+hm[1]*hm[2]-np.array([
    reference(ym[:3, k])[0] for k in range(len(times))])
sign_mutation_max = float(max(abs(constraint_mutant)))
assert sign_mutation_max > 1e-3

# Independent80-digit axisymmetric continuum integrals for a different table.
axis = TabulatedRadiation([0, .35, 1], [0, 1], [[.25], [.65]], refinement=4,
                         backend='python_oracle')
ell = [.03, .03, .07]
with mp.workdps(80):
    bx, bz = mp.exp(-2*mp.mpf(ell[0])), mp.exp(-2*mp.mpf(ell[2]))
    volume = mp.exp(-sum(mp.mpf(e) for e in ell))
    energy, px, pz = mp.mpf(0), mp.mpf(0), mp.mpf(0)
    for aa, bb, ww in [(0., .35, .25), (.35, 1., .65)]:
        a, b, w = mp.mpf(aa), mp.mpf(bb), mp.mpf(ww)
        r = lambda z: mp.sqrt(bx*(1-z*z)+bz*z*z)
        energy += w*mp.quad(r, [a, b])/(b-a)
        px += w*bx*mp.quad(lambda z: (1-z*z)/(2*r(z)), [a, b])/(b-a)
        pz += w*bz*mp.quad(lambda z: z*z/r(z), [a, b])/(b-a)
    exact_axis = [str(volume*energy), str(volume*px), str(volume*px), str(volume*pz)]
    from bianchi.nonperturbative.einstein_tabulated_source import certified_tabulated_pressure
    axis_certificate = certified_tabulated_pressure(axis, [.08]*3)
    storedE, storedP = refs.exact_stored_moments(axis, ell)
    for p, exact, bound in zip(storedP, [volume*px, volume*px, volume*pz], axis_certificate['pressure_upper']):
        assert abs(p-exact) <= mp.mpf(bound)

# Initial higher moments demonstrate that the physical table is not a finite-l fit.
z, w = np.polynomial.legendre.leggauss(32)
high_l = {}
for l in (6, 8, 10):
    value = 0.
    for i, (a, b) in enumerate(zip(MU[:-1], MU[1:])):
        mu = a+(z+1)*(b-a)/2
        value += sum(ENERGY[i])*float(w@eval_legendre(l, mu))/2
    high_l[str(l)] = value
assert all(abs(v) > 1e-6 for v in high_l.values())

slope = float(-np.polyfit(np.log([r['refinement'] for r in rows[1:]]),
                         np.log([r['certificate']['geometry_h_upper'] for r in rows[1:]]), 1)[0])
result = dict(scope='CE1-F_TABLE_DEFINED_CONTINUUM_SCOPED',
    input=dict(mu=MU, phi_fraction=PHI, energy=ENERGY, meaning='synthetic declared cell energies, not measured sky',
               exact_binary_energy=str(refs.model().continuum_energy), shear=[.2, -.13, -.07], end=T),
    target_h=TARGET, rows=rows, independent_reference_order32_vs48_history_max=quad_history_gap,
    reference_tolerance_2e_10_vs_2e_13_history_max=tol_history_gap,
    axisymmetric_80digit=dict(ell=ell, energy_and_pressures=exact_axis, certificate=axis_certificate),
    high_legendre_energy_moments=high_l, observed_geometry_bound_refinement_order=slope,
    mutations=dict(sign_constraint_max=sign_mutation_max,
                   omitted_cell_term_all_levels_detected=all(r['omitted_term_mutation_violations']>0 for r in rows),
                   midpoint_isotropic_z_error=.9/12),
    scientific_calls=dict(coupled_ivp=9, pressure_probes=255, high_precision_axisymmetric=1,
                          inherited_historical_science_campaigns=0),
    environment=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__, mpmath=mp.__version__,
                     platform=platform.platform(), seed=615237),
    time_error_certified=False, upper_dag='9/15', production_ready=False, merge_ready=False,
    wall_seconds=time.perf_counter()-t0, cpu_seconds=time.process_time()-c0)
(OUT/'RESULTS.json').write_text(json.dumps(result, indent=2))
(OUT/'HISTORY.json').write_text(json.dumps(dict(times=times.tolist(), histories=histories,
    sign_mutant_constraint=constraint_mutant.tolist()), indent=2))

plt.rcParams.update({'font.size': 10, 'axes.labelsize': 10, 'axes.titlesize': 10,
                     'legend.fontsize': 8, 'lines.linewidth': 1.8})
fvals = [r['refinement'] for r in rows]
fig, ax = plt.subplots(figsize=(3.65, 3.15), layout='constrained')
ax.loglog(fvals, [r['certificate']['source_pressure_upper'] for r in rows], 'o-', label='Uniform certificate')
ax.loglog(fvals, [r['measured_pressure_max'] for r in rows], 's--', label='Independent quadrature gap')
ax.set(xlabel='Cell refinement factor', ylabel='Maximum pressure error', xticks=fvals)
ax.set_xticklabels(fvals)
ax.grid(True, which='both', alpha=.2)
ax.legend(loc='best')
fig.savefig(OUT/'SOURCE_CONVERGENCE.png', dpi=200)
fig.savefig(OUT/'SOURCE_CONVERGENCE.pdf')
plt.close(fig)

fig, ax = plt.subplots(figsize=(3.65, 3.15), layout='constrained')
ax.loglog(fvals, [r['certificate']['geometry_h_upper'] for r in rows], 'o-', label='Exact-ODE upper bound')
ax.loglog(fvals, [r['measured_h_max'] for r in rows], 's--', label='Numerical h difference')
ax.axhline(TARGET, color='black', linestyle=':', label='Declared target')
ax.set(xlabel='Cell refinement factor', ylabel='Maximum |Tstar delta H|', xticks=fvals)
ax.set_xticklabels(fvals)
ax.grid(True, which='both', alpha=.2)
ax.legend(loc='best')
fig.savefig(OUT/'GEOMETRY_CONVERGENCE.png', dpi=200)
fig.savefig(OUT/'GEOMETRY_CONVERGENCE.pdf')
plt.close(fig)
print('CE1F_SCIENCE_PASS', 'bound_order', slope, 'wall_s', result['wall_seconds'], flush=True)
