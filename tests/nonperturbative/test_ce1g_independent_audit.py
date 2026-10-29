"""New CE1-G adversarial scientific-contract regressions (independent audit)."""
import numpy as np
import pytest

from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_interval import stored_ray_energy_majorant
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_tabulated_time import certify_tabulated_computed_path


def _model():
    return TabulatedRadiation(
        [0, .5, 1], [0, .25, .75, 1],
        [[.1, .25, .05], [.2, .15, .15]],
        refinement=1, backend='python_oracle',
    )


def test_majorant_recomputed_after_admitted_stored_mass_rebinding():
    """Admitted data rebinding must not reuse an obsolete fourth-derivative cap."""
    source = _model()
    old = stored_ray_energy_majorant(source)
    source.mass = source.mass.copy() * 64.
    new = stored_ray_energy_majorant(source)
    # Multiplication by 64 is exact for these normal binary64 ray masses.
    assert new > 63.999 * old


def test_hermite_cubic_origin_must_match_recorded_left_knot():
    """The initial comparison error must refer to the actual cubic start."""
    source = _model()
    path = rk4_path(source, source.initial_state(), .08, 4,
                    backend='python_oracle')
    path.coefficients[0, 0, 3] += .01
    assert not np.array_equal(path.coefficients[0, 0], path.states[0])
    with pytest.raises(ValueError, match='Hermite.*knot'):
        certify_tabulated_computed_path(source, path, end=.08)


def test_full_panel_fourth_derivative_bound_follows_stored_mass_rebinding():
    """The outward full-panel bound must consume the current stored measure."""
    source = _model()
    path = rk4_path(source, source.initial_state(), .08, 4,
                    backend='python_oracle')
    original = certify_tabulated_computed_path(source, path, end=.08)
    source.mass = source.mass.copy() * 64.
    changed = certify_tabulated_computed_path(source, path, end=.08)
    assert changed['rows'][0]['fourth_derivative_upper'] > (
        2 * original['rows'][0]['fourth_derivative_upper']
    )
    assert changed['source_pressure_upper'] > original['source_pressure_upper']
