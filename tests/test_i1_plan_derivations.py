"""I1-계획 · class A 특성곡선 선유도의 상시 게이트 (64차) — (T1)–(T4) 박제."""
import sympy as sp

from audit.i1_characteristics_derivation import (
    dipole_curvature_coupling, orthonormal_form_symbolic,
    quadrupole_curvature_coupling, type_ii_symbolic, type_ix_exact_point)


def test_t1_type_ii_pins_index_order():
    good, bad = type_ii_symbolic()
    assert all(r == 0 for r in good)
    assert sp.simplify(bad[1]) != 0 and sp.simplify(bad[2]) != 0


def test_t1_type_ix_exact_point_zero():
    resid, C = type_ix_exact_point()
    assert all(r == 0 for r in resid)
    assert len(C) == 6


def test_t2_t3_orthonormal_we_form_and_invariance():
    resid, mag = orthonormal_form_symbolic()
    assert all(r == 0 for r in resid)
    assert mag == 0


def test_t4_multipole_selection_rules():
    assert all(x == 0 for x in dipole_curvature_coupling())
    assert quadrupole_curvature_coupling() == 0
