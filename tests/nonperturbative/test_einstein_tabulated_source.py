"""CE1-F: finite-cell angular table is its own physical continuum density."""
import math
from fractions import Fraction
import numpy as np
import pytest
from scipy.integrate import solve_ivp
from bianchi.nonperturbative.einstein_tabulated_source import (
    TabulatedRadiation, certified_tabulated_pressure,
    certified_tabulated_energy, certified_tabulated_geometry,
)

EDGES_MU=('0','0.5','1')
EDGES_PHI=('0','0.3333333333333333333333333333333333333333333333','0.6666666666666666666666666666666666666666666667','1')
ENERGIES=(('0.09','0.15','0.06'),('0.2','0.12','0.18'))


def source(refine=1, energies=ENERGIES, **kwargs):
    return TabulatedRadiation(EDGES_MU,EDGES_PHI,energies,refinement=refine,backend='python_oracle',**kwargs)


def test_positive_cell_input_and_exact_physical_energy():
    s=source()
    assert s.exact_energy==sum(map(Fraction,sum((list(row) for row in ENERGIES),[])))
    assert s.energy0>0 and np.all(s.mass>0)
    assert s.n.shape==(len(s.mass),3)
    assert s.physical_representation=='EIGHT_REFLECTED_PIECEWISE_CONSTANT_CELLS'
    assert abs(s.exact_energy-Fraction(4,5))==0
    for mu,phi,w in s.original_cells:
        assert mu[0]<mu[1] and phi[0]<phi[1] and w>=0


def test_isotropic_one_cell_pressure_exact_at_initial_geometry():
    s=TabulatedRadiation(('0','1'),('0','1'),(('0.9',),),backend='python_oracle')
    assert s.exact_energy==Fraction(9,10)
    e,p=s.moments([0,0,0]);assert abs(e-.9)<2e-15
    assert max(abs(p-.3))<5e-15
    cert=certified_tabulated_pressure(s,[0,0,0],[0,0,0])
    assert cert['max_pressure_upper']<1e-12


def test_finite_cell_refinement_preserves_table_and_improves_certificate():
    s1=source(1);s2=source(2);s4=source(4)
    assert s1.exact_energy==s2.exact_energy==s4.exact_energy
    assert len(s4.mass)==16*len(s1.mass)
    assert sum(w for _,_,w in s4.cells)==s4.exact_energy
    b1=certified_tabulated_pressure(s1,[0,0,0],[.07,.07,.07])
    b2=certified_tabulated_pressure(s2,[0,0,0],[.07,.07,.07])
    b4=certified_tabulated_pressure(s4,[0,0,0],[.07,.07,.07])
    assert b1['max_pressure_upper'] > b2['max_pressure_upper'] > b4['max_pressure_upper']>0


def test_positive_gapped_or_malformed_input_rejected_without_clipping():
    with pytest.raises(ValueError):source(energy_bad=1)
    with pytest.raises(ValueError):source(energies=(('0.1','0.2','0.3'),('0.1','-0.1','0.3')))
    with pytest.raises(ValueError):TabulatedRadiation(('0','.4'),('0','1'),(('1',),),backend='python_oracle')
    with pytest.raises(ValueError):TabulatedRadiation(('0','1'),('0','1'),(('1',),))
    with pytest.raises(ValueError):source(refine=0)
    with pytest.raises(ValueError):source(refine=30)


def test_signed_direction_normalization_and_initial_energy_gap():
    s=source()
    energy=certified_tabulated_energy(s)
    assert energy['continuum_energy_exact']=='4/5'
    assert Fraction.from_float(energy['energy_error_upper'])>=abs(s.exact_energy-Fraction.from_float(s.energy0))
    assert energy['energy_error_upper']<1e-12
    assert not energy['float64_time_integrator_certified']


def test_finite_geometry_source_bound_falsifiable_against_independent_reference():
    from numpy.polynomial.legendre import leggauss
    s=source()
    cert=certified_tabulated_pressure(s,[0,0,0],[.07,.07,.07])
    assert cert['method']=='CENTERED_CELL_VARIANCE_PLUS_STORED_RAY'
    assert cert['max_pressure_upper']>0 and cert['max_pressure_upper']<.1
    for ell in [[0,0,0],[.012,.04,.025],[.07,.07,.07]]:
        fine=independent_continuum_moments(s,ell,polar_nodes=28,az_nodes=28)
        gap=np.abs(fine[1]-s.moments(ell)[1])
        assert np.all(gap<=cert['pressure_upper'])


def independent_continuum_moments(s,ell,polar_nodes=28,az_nodes=28):
    """Independent original-cell tensor integral; never uses source barycenters."""
    mu_nodes,mu_w=__import__('numpy').polynomial.legendre.leggauss(polar_nodes)
    ph_nodes,ph_w=__import__('numpy').polynomial.legendre.leggauss(az_nodes)
    ell=np.asarray(ell,float);b=np.exp(-2*ell);vol=np.exp(-sum(ell))
    energy=0.;p=np.zeros(3)
    for mu_range,ph_range,w in s.original_cells:
        a,z=map(float,mu_range);c,d=map(float,ph_range)
        mu=a+(mu_nodes+1)*(z-a)/2
        phi=(c+(ph_nodes+1)*(d-c)/2)*(np.pi/2)
        mu2=mu[:,None]**2
        n2=np.stack(np.broadcast_arrays((1-mu2)*np.cos(phi[None,:])**2,
                     (1-mu2)*np.sin(phi[None,:])**2,mu2),axis=-1)
        radial=np.sqrt(np.einsum('...i,i->...',n2,b))
        quad=mu_w[:,None]*ph_w[None,:]/4
        energy+=float(w)*vol*np.sum(quad*radial)
        p+=float(w)*vol*b*np.einsum('ab,abi->i',quad/radial,n2)
    return energy,p


def test_bounded_coupled_einstein_vlasov_geometry():
    s=source(2)
    r=certified_tabulated_geometry(s,end=.08)
    assert r['status']=='SCOPED_TABULATED_COUPLED_SOURCE_ENCLOSURE'
    assert r['source_pressure_upper']>0
    assert r['geometry_h_upper']>r['initial_rate_upper']
    assert not r['time_integrator_error_included']
    assert r['geometry_h_upper']<.1
    sol=solve_ivp(s.rhs,(0,.08),s.initial_state(),method='DOP853',rtol=1e-11,atol=1e-13)
    assert sol.success
    assert np.isfinite(sol.y).all()


def test_cell_mean_is_not_geometric_midpoint_mutation():
    # For the full first octant the real angular mean is (1/3,1/3,1/3),
    # whereas the geometric midpoint gives qz^2=1/4.
    s=TabulatedRadiation(('0','1'),('0','1'),(('1',),),backend='python_oracle')
    assert abs(s.n[0,2]**2-1/3)<5e-16
    assert abs((.5**2)-(1/3))>0.08
    assert certified_tabulated_pressure(s,[0,0,0],[0,0,0])['max_pressure_upper']<1e-12
