"""Independent physical/cell-integration contracts for the CE1-F source."""
from fractions import Fraction

import mpmath as mp
import numpy as np
import pytest
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp

from bianchi.nonperturbative.einstein_tabulated_source import (
    TabulatedRadiation, certified_tabulated_energy, certified_tabulated_pressure,
    certified_tabulated_geometry, _trig_pi)

MU = [0., .5, 1.]
PHI = [0., .25, .75, 1.]
ENERGY = [[.1, .25, .05], [.2, .15, .15]]


def model(refinement=1):
    return TabulatedRadiation(MU, PHI, ENERGY, refinement=refinement,
                             backend='python_oracle')


def independent_cell_rule(mu, phi, energy, order=24):
    """Integrate ORIGINAL cell densities, never call the barycenter helpers."""
    t, w = leggauss(order)
    rays, masses = [], []
    for i, (a, b) in enumerate(zip(mu[:-1], mu[1:])):
        z = a+(t+1)*(b-a)/2
        for j, (c, d) in enumerate(zip(phi[:-1], phi[1:])):
            ph = np.pi/2*(c+(t+1)*(d-c)/2)
            zz, pp = np.meshgrid(z, ph, indexing='ij')
            rr = np.sqrt(1-zz*zz)
            rays.append(np.column_stack([(rr*np.cos(pp)).ravel(),
                                          (rr*np.sin(pp)).ravel(), zz.ravel()]))
            masses.append((float(energy[i][j])*np.outer(w, w)/4).ravel())
    n = np.concatenate(rays)
    mass = np.concatenate(masses)
    x = n*n
    def moments(ell):
        ell = np.asarray(ell)
        b = np.exp(-2*ell)
        r = np.sqrt(x@b)
        v = np.exp(-ell.sum())
        return float(v*(mass@r)), v*b*np.einsum('q,qi->i', mass/r, x)
    return moments


def exact_stored_moments(source, ell):
    """90-digit independent evaluation of exact recorded ray/mass formula."""
    with mp.workdps(90):
        b = [mp.exp(-2*mp.mpf(float(e))) for e in ell]
        v = mp.exp(-sum(mp.mpf(float(e)) for e in ell))
        E, P = mp.mpf(0), [mp.mpf(0) for _ in range(3)]
        for row, w in zip(source.n, source.mass):
            x = [mp.mpf(float(n))**2 for n in row]
            r = mp.sqrt(sum(a*c for a, c in zip(b, x)))
            E += mp.mpf(float(w))*r
            for i in range(3):
                P[i] += mp.mpf(float(w))*b[i]*x[i]/r
        return +v*E, [+v*p for p in P]


def test_directed_trig_covers_endpoints_and_interior_maximum():
    with mp.workdps(90):
        for q in [Fraction(0), Fraction(1, 7), Fraction(1, 2),
                  Fraction(7, 8), Fraction(1), Fraction.from_float(.49999999999999994)]:
            for kind in ('sin', 'cos'):
                z = _trig_pi(q, kind)
                exact = getattr(mp, kind)(mp.pi*q.numerator/q.denominator)
                if q in (0, Fraction(1, 2), 1):
                    # mpmath pi is finite; use exact known special values.
                    exact = (1 if q == Fraction(1, 2) else 0) if kind == 'sin' else (
                        1 if q == 0 else -1 if q == 1 else 0)
                assert mp.mpf(z.lower) <= exact <= mp.mpf(z.upper)


def test_initial_isotropic_energy_pressure_and_midpoint_mutation():
    s = TabulatedRadiation([0, 1], [0, 1], [[.9]], backend='python_oracle')
    cert = certified_tabulated_pressure(s, [0, 0, 0])
    with mp.workdps(90):
        E, P = exact_stored_moments(s, [0, 0, 0])
        exact = mp.mpf(.9)/3
        assert all(abs(p-exact) <= mp.mpf(b) for p, b in zip(P, cert['pressure_upper']))
    assert cert['bound_max'] < 2e-15
    # Geometric midpoint mu=.5 gives Pz=E/4, violating the centered rule.
    midpoint_gap = float(.9*(Fraction(1, 3)-Fraction(1, 4)))
    assert midpoint_gap > cert['bound_max']*1e10
    E, P = s.moments([.06, .06, .06])
    np.testing.assert_allclose(E, .9*np.exp(-.24), rtol=5e-15)
    np.testing.assert_allclose(P, E/3, rtol=5e-15)


def test_cell_means_ranges_and_same_physical_input_under_refinement():
    a, b = model(1), model(4)
    assert a.continuum_energy == b.continuum_energy
    assert sum(c.energy for c in b.cells) == a.continuum_energy
    assert len(b.cells) == 16*len(a.cells)
    # Initial-reference tolerance is below ordinary GL/BLAS summation noise.
    # Integrate the original angular factors independently at90 decimal digits.
    with mp.workdps(90):
        exact = [mp.mpf(0) for _ in range(3)]
        for i, (aa, bb) in enumerate(zip(MU[:-1], MU[1:])):
            aa, bb = mp.mpf(aa), mp.mpf(bb)
            z2 = mp.quad(lambda z: z*z, [aa, bb])/(bb-aa)
            for j, (cc, dd) in enumerate(zip(PHI[:-1], PHI[1:])):
                cc, dd = mp.mpf(cc)*mp.pi/2, mp.mpf(dd)*mp.pi/2
                cx = mp.quad(lambda p: mp.cos(p)**2, [cc, dd])/(dd-cc)
                cy = mp.quad(lambda p: mp.sin(p)**2, [cc, dd])/(dd-cc)
                for k, term in enumerate([(1-z2)*cx, (1-z2)*cy, z2]):
                    exact[k] += mp.mpf(ENERGY[i][j])*term
        exact = np.array([float(x) for x in exact])
    for s in (a, b):
        np.testing.assert_allclose(s.moments([0, 0, 0])[1], exact, atol=8e-16, rtol=0)
        for c in s.cells:
            for mean, bounds in zip(c.means, c.ranges):
                assert bounds.lower <= mean.upper and mean.lower <= bounds.upper


def test_uniform_box_contains_independent_continuum_pressures():
    s = model(4)
    ref = independent_cell_rule(MU, PHI, ENERGY, order=32)
    cert = certified_tabulated_pressure(s, [.2, .2, .2])
    rng = np.random.default_rng(7031)
    for ell in [[0, 0, 0], [.2, .01, .12], [.2, .2, .2], *rng.uniform(0, .2, (12, 3))]:
        error = abs(s.moments(ell)[1]-ref(ell)[1])
        assert np.all(error <= np.asarray(cert['pressure_upper']))
    assert certified_tabulated_pressure(model(8), [.2]*3)['bound_max'] < cert['bound_max']/3


def test_exact_energy_and_nonunit_stored_ray_mass_corrections():
    s = TabulatedRadiation([0, 1], [0, 1], [[.9]], backend='python_oracle')
    # Exercise the terms on amplified stored-data perturbations, not just ulps.
    s.n = s.n.copy()*1.02
    s.mass = s.mass.copy()*1.01
    en = certified_tabulated_energy(s)
    ref = independent_cell_rule([0, 1], [0, 1], [[.9]], order=36)
    cert = certified_tabulated_pressure(s, [.08]*3)
    with mp.workdps(90):
        E, _ = exact_stored_moments(s, [0, 0, 0])
        assert mp.mpf(en['stored_real_lower']) <= E <= mp.mpf(en['stored_real_upper'])
        assert mp.mpf(en['energy_max_upper']) >= E > mp.mpf(.9)
    assert np.all(abs(s.moments([.06, .01, .03])[1]-ref([.06, .01, .03])[1])
                  <= cert['pressure_upper'])
    assert en['continuum_vs_stored_real_upper'] > .02
    assert cert['parts_max_upper']['stored_ray'] > .01
    assert cert['parts_max_upper']['stored_mass'] > .005


def test_source_trace_energy_continuity_initial_constraint_and_coupling():
    s = model(4)
    ell = np.array([.04, .01, .025])
    E, P = s.moments(ell)
    assert abs(P.sum()-E) < 5e-16
    step = 2e-6
    for j in range(3):
        d = np.eye(3)[j]*step
        derivative = (s.moments(ell+d)[0]-s.moments(ell-d)[0])/(2*step)
        assert abs(derivative+E+P[j]) < 2e-10
    y = s.initial_state()
    h = y[3:]
    assert abs(h[0]*h[1]+h[0]*h[2]+h[1]*h[2]-s.energy0) < 5e-16
    bound = certified_tabulated_geometry(s, end=.04)
    ref = independent_cell_rule(MU, PHI, ENERGY, order=24)
    def rhs(t, z):
        hh = z[3:]
        return np.r_[hh, -hh.sum()*hh+ref(z[:3])[1]]
    # Same binary initial state, so actual initial error is smaller than bound.
    a = solve_ivp(s.rhs, [0, .04], y, method='DOP853', rtol=2e-12, atol=2e-14)
    b = solve_ivp(rhs, [0, .04], y, method='DOP853', rtol=2e-12, atol=2e-14)
    assert a.success and b.success
    assert max(abs(a.y[3:, -1]-b.y[3:, -1])) < bound['geometry_h_upper']
    assert bound['time_integration_error_included'] is False


def test_nonuniform_partition_zeros_and_owned_input():
    w = np.array([[0., .1], [.8, 0.]])
    s = TabulatedRadiation([0, .17, 1], [0, .61, 1], w, backend='python_oracle')
    w[:] = 0
    assert s.continuum_energy == Fraction.from_float(.1)+Fraction.from_float(.8)
    assert len(s.cells) == 2
    for array in (s.n, s.mass, s.mu_edges, s.phi_fraction_edges, s.cell_energy):
        assert array.flags.writeable is False
    with pytest.raises(ValueError):
        s.mass[0] = -1
    ref = independent_cell_rule([0, .17, 1], [0, .61, 1], [[0., .1], [.8, 0.]])
    cert = certified_tabulated_pressure(s, [.1]*3)
    assert np.all(abs(s.moments([.1, .02, .07])[1]-ref([.1, .02, .07])[1])
                  <= cert['pressure_upper'])


@pytest.mark.parametrize('mu,ph,w,ref', [
    ([.1, 1], [0, 1], [[1]], 1),
    ([0, .5, .5, 1], [0, 1], [[1], [1], [1]], 1),
    ([0, 1], [0, 1], [[-1]], 1),
    ([0, 1], [0, 1], [[0]], 1),
    ([0, 1], [0, 1], [[float('nan')]], 1),
    ([0, 1], [0, 1], [[1j]], 1),
    ([0, 1], [0, 1], [[1, 2]], 1),
    ([0, 1], [0, 1], [[1]], True),
    ([0, 1], [0, 1], [[1]], 1.5),
    ([0, 1], [0, 1], [[1]], 0),
])
def test_invalid_physical_data_rejected(mu, ph, w, ref):
    with pytest.raises(ValueError):
        TabulatedRadiation(mu, ph, w, refinement=ref, backend='python_oracle')


def test_explicit_backend_and_comparison_domain():
    with pytest.raises(ValueError, match='backend'):
        TabulatedRadiation([0, 1], [0, 1], [[1.]])
    s = model()
    for upper in [[-.1, .1, .1], [3, 0, 0], [np.inf]*3]:
        with pytest.raises(ValueError):
            certified_tabulated_pressure(s, upper)
    for T in [0, -.1, .3, np.nan]:
        with pytest.raises(ValueError):
            certified_tabulated_geometry(s, end=T)
    with pytest.raises(ValueError):
        s.initial_state([1, 0, 0])
    with pytest.raises(TypeError):
        certified_tabulated_pressure(object(), [0, 0, 0])
