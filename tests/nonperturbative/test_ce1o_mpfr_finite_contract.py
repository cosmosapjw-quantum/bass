"""CE1-O: directly called MPFR interval constructors must not admit NaNs/Inf."""
import math
import pytest
from bianchi.nonperturbative.einstein_interval import Interval

@pytest.mark.parametrize('literal', ["nan", "NaN", "+nan", "inf", "-inf", "Infinity", "-Infinity"])
def test_decimal_does_not_admit_nonfinite_mpfr_numbers(literal):
    with pytest.raises(ValueError, match="Nonfinite|nonfinite|finite"):
        Interval.decimal(literal)

def test_nan_would_make_contains_zero_vacuously_true_before_repair():
    # This is a direct certificate-soundness precondition, not an arithmetic tolerance.
    with pytest.raises(ValueError, match="finite"):
        Interval.decimal("nan").contains(0)

@pytest.mark.parametrize('literal', ['0', '-0', '.1', '1.234e-200', '-7.1e13'])
def test_finite_decimals_preserve_inclusion(literal):
    x=Interval.decimal(literal)
    assert math.isfinite(x.lower) and math.isfinite(x.upper)
    assert x.lower <= x.upper

def test_direct_unordered_mpfr_payload_fails_boolean_certificate_checks():
    # Attack internal state through native FFI, not through the defended parser.
    from bianchi.nonperturbative.einstein_interval import _lib, D, U
    import ctypes as C
    z=Interval._empty()
    assert _lib.mpfr_set_str(z.a.ptr(),b'nan',10,D)==0
    assert _lib.mpfr_set_str(z.b.ptr(),b'nan',10,U)==0
    with pytest.raises(ValueError,match='Nonfinite'):
        z.contains(0)
    with pytest.raises(ValueError,match='Nonfinite'):
        z.is_nonnegative()

def test_native_exponential_overflow_fails_closed_at_boolean_gate():
    # Large finite MPFR input may overflow MPFR exponent range upon exp.
    z=Interval.decimal('1e1000000').exp()
    with pytest.raises(ValueError,match='Nonfinite'):
        z.contains(0)
    with pytest.raises(ValueError,match='Nonfinite'):
        z.is_nonnegative()
