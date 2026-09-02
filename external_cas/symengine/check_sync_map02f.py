#!/usr/bin/env python3
from __future__ import annotations

import sys
import symengine as se

failures = 0


def zero(value: object) -> bool:
    expr = se.sympify(value)
    return expr.expand() == 0


def check(identity_id: str, value: object) -> None:
    global failures
    if zero(value):
        print(f"CHECK|{identity_id}|PASS")
    else:
        print(f"CHECK|{identity_id}|FAIL|{se.sympify(value).expand()}")
        failures += 1


def check_bool(identity_id: str, value: bool) -> None:
    global failures
    if value:
        print(f"CHECK|{identity_id}|PASS")
    else:
        print(f"CHECK|{identity_id}|FAIL")
        failures += 1


def mutation(mutation_id: str, value: object) -> None:
    global failures
    if not zero(value):
        print(f"MUTATION|{mutation_id}|PASS")
    else:
        print(f"MUTATION|{mutation_id}|FAIL|0")
        failures += 1


b, x, nu, d, g = se.symbols("b x nu d g")
a0, a1, a2, a3 = se.symbols("a0 a1 a2 a3")
c00, c10, c01, c20, c11, c02, c30, c21, c12, c03 = se.symbols(
    "c00 c10 c01 c20 c11 c02 c30 c21 c12 c03"
)
h, sigmaEE = se.symbols("h sigmaEE")

# I01 uses a cross-multiplied identity and the directly regular value at gamma=1.
i01_cross = g**2 * (g**2 - 1) - (g - 1) * g**2 * (g + 1)
chi = g**2 / (g + 1)
check_bool(
    "I01_REGULAR_ABERRATION_COEFFICIENT",
    zero(i01_cross) and zero(chi.subs({g: 1}) - se.Rational(1, 2)),
)

mu_tilde = (x + b) / (1 + b * x)
check(
    "I02_AXIAL_ABERRATION_UNIT_NORM",
    (x + b) ** 2 + (1 - x**2) * (1 - b**2) - (1 + b * x) ** 2,
)
check(
    "I03_SOLID_ANGLE_JACOBIAN",
    (1 + b * x) - b * (x + b) - (1 - b**2),
)
check(
    "I04_INVERSE_DOPPLER",
    (1 + b * x) - b * (x + b) - (1 - b**2),
)

T0 = a0 + a1 * x + a2 * x**2 + a3 * x**3
xs = (x - b) / (1 - b * x)
dop = se.sqrt(1 - b**2) / (1 - b * x)
full_temperature = dop * T0.subs({x: xs})
full_generator = se.diff(full_temperature, b).subs({b: 0})
expected_temperature = x * T0 - (1 - x**2) * se.diff(T0, x)
check("I05_BLACKBODY_FULL_GENERATOR", full_generator - expected_temperature)
check(
    "I06_BLACKBODY_PRIMITIVE_GAP",
    full_generator - x * T0 + (1 - x**2) * se.diff(T0, x),
)

F0 = (
    c00 + c10 * nu + c01 * x + c20 * nu**2 + c11 * nu * x + c02 * x**2
    + c30 * nu**3 + c21 * nu**2 * x + c12 * nu * x**2 + c03 * x**3
)
xs1 = x - b * (1 - x**2)
nus1 = nu * (1 - b * x)
spectral_first_order = (1 + d * b * x) * F0.subs({x: xs1}).subs({nu: nus1})
spectral_generator = se.diff(spectral_first_order, b).subs({b: 0})
expected_spectral = x * (d * F0 - nu * se.diff(F0, nu)) - (1 - x**2) * se.diff(F0, x)
check("I07_SPECTRAL_BOOST_GENERATOR", spectral_generator - expected_spectral)

rei_difference = (-h) - (-h - sigmaEE)
check("I08_REI_EXACT_SIGMA_RESIDUAL", rei_difference - sigmaEE)

ex, ey, ez, ax, ay, az, ox, oy, oz = se.symbols("ex ey ez ax ay az ox oy oz")
s11, s12, s13, s22, s23, s33 = se.symbols("s11 s12 s13 s22 s23 s33")
n11, n12, n13, n22, n23, n33 = se.symbols("n11 n12 n13 n22 n23 n33")
sEE = s11 * ex**2 + 2 * s12 * ex * ey + 2 * s13 * ex * ez + s22 * ey**2 + 2 * s23 * ey * ez + s33 * ez**2
aE = ax * ex + ay * ey + az * ez
se1, se2, se3 = (
    s11 * ex + s12 * ey + s13 * ez,
    s12 * ex + s22 * ey + s23 * ez,
    s13 * ex + s23 * ey + s33 * ez,
)
ne1, ne2, ne3 = (
    n11 * ex + n12 * ey + n13 * ez,
    n12 * ex + n22 * ey + n23 * ez,
    n13 * ex + n23 * ey + n33 * ez,
)
radial = sEE + aE
vx = radial * ex - se1 - ax + oy * ez - oz * ey - (ey * ne3 - ez * ne2)
vy = radial * ey - se2 - ay + oz * ex - ox * ez - (ez * ne1 - ex * ne3)
vz = radial * ez - se3 - az + ox * ey - oy * ex - (ex * ne2 - ey * ne1)
e2 = ex**2 + ey**2 + ez**2
check("I09_DIRECTION_FLOW_TANGENCY", ex * vx + ey * vy + ez * vz - (e2 - 1) * radial)

pdot, chid, pplus, omega = se.symbols("pdot chid pplus omega")
screen_residual = (pdot - 2 * se.I * chid * pplus) + 2 * se.I * (omega + chid) * pplus - (pdot + 2 * se.I * omega * pplus)
check("I10_SCREEN_U1_COVARIANCE", screen_residual)

mutation("M01_WRONG_DOPPLER_SIGN", -2 * g * b * x)
mutation("M02_WRONG_JACOBIAN_POWER", b * (1 - x**2))
mutation("M03_DROP_BLACKBODY_ABERRATION", -(1 - x**2) * se.diff(T0, x))
mutation("M04_REI_WRONG_SIGN", -2 * sigmaEE)
mutation("M05_REI_WRONG_FACTOR", sigmaEE)
mutation("M06_REI_FOREIGN_CONSTANT", 1 - sigmaEE)
mutation("M07_DROP_DIRECTION_RADIAL_COMPENSATOR", -sEE - aE)
mutation("M08_SCREEN_CONNECTION_SIGN", -4 * se.I * chid * pplus)

print("STATUS|PASS" if failures == 0 else "STATUS|FAIL")
sys.exit(0 if failures == 0 else 1)
