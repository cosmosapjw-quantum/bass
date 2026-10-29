"""Contract tests for exact-real stored initial energy in CE1-F geometry."""
from decimal import Decimal, localcontext
from fractions import Fraction
import pytest
from bianchi.nonperturbative.einstein_tabulated_source import (
    TabulatedRadiation, certified_tabulated_geometry, certified_tabulated_energy,
)


def decimal_fraction(f):
    return Decimal(f.numerator) / Decimal(f.denominator)


def stored_exact_real_initial_energy(source):
    """Independent >80 decimal digit evaluation of binary64 mass/ray formula."""
    with localcontext() as c:
        c.prec = 110
        return sum((decimal_fraction(Fraction.from_float(float(w))) *
                    decimal_fraction(sum((Fraction.from_float(float(q))**2 for q in ray), Fraction())).sqrt()
                    for w, ray in zip(source.mass, source.n)), Decimal(0))


def test_one_cell_reproduces_parent_undercap_and_fixed_contract():
    source = TabulatedRadiation(('0', '1'), ('0', '1'), (('0.9',),), backend='python_oracle')
    exact = stored_exact_real_initial_energy(source)
    old_cap = max(Decimal(source.exact_energy.numerator)/Decimal(source.exact_energy.denominator),
                  Decimal.from_float(float(source.energy0)))
    assert exact > old_cap, 'Witness must reproduce strict old-certificate premise failure'
    result = certified_tabulated_geometry(source, end=.08)
    assert result['energy_max_semantics'] == 'OUTWARD_UPPER_EXACT_REAL_CONTINUUM_AND_STORED_INITIAL'
    assert Decimal.from_float(result['energy_max_upper']) >= exact


@pytest.mark.parametrize('refinement', [1,2,4,8])
def test_initial_energy_cap_contains_exact_real_stored_source_at_each_refinement(refinement):
    source = TabulatedRadiation(
        ('0','.5','1'), ('0','1/3','2/3','1'),
        (('0.09','0.15','0.06'),('0.20','0.12','0.18')),
        refinement=refinement, backend='python_oracle')
    r = certified_tabulated_geometry(source, end=.08)
    exact = stored_exact_real_initial_energy(source)
    assert Decimal.from_float(r['energy_max_upper']) >= exact
    assert Decimal.from_float(r['energy_max_upper']) >= decimal_fraction(source.exact_energy)
    assert r['geometry_h_upper'] > 0


def test_energy_certificate_absolute_gap_covers_stored_real_difference():
    s=TabulatedRadiation(('0','1'),('0','1'),(('0.9',),),backend='python_oracle')
    e=certified_tabulated_energy(s)
    exact=stored_exact_real_initial_energy(s)
    with localcontext() as c:
        c.prec=110
        cont=decimal_fraction(s.exact_energy)
        assert Decimal.from_float(e['exact_real_discrete_difference_upper'])>=abs(exact-cont)
