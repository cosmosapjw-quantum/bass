#!/usr/bin/env python3
from __future__ import annotations

import sys
from symbolica import E, S

failures = 0


def canonical(value) -> str:
    return value.expand().to_canonical_string()


def zero(value) -> bool:
    return canonical(value) == "0"


def check(identity_id: str, value) -> None:
    global failures
    if zero(value):
        print(f"CHECK|{identity_id}|PASS")
    else:
        print(f"CHECK|{identity_id}|FAIL|{canonical(value)}")
        failures += 1


def mutation(mutation_id: str, value) -> None:
    global failures
    if not zero(value):
        print(f"MUTATION|{mutation_id}|PASS")
    else:
        print(f"MUTATION|{mutation_id}|FAIL|0")
        failures += 1


b, x, nu, d = S("b", "x", "nu", "d")
a0, a1, a2, a3 = S("a0", "a1", "a2", "a3")
c00, c10, c01, c20, c11, c02, c30, c21, c12, c03 = S(
    "c00", "c10", "c01", "c20", "c11", "c02", "c30", "c21", "c12", "c03"
)
h, sigmaEE = S("h", "sigmaEE")

check("I02_AXIAL_ABERRATION_UNIT_NORM", E("(x+b)^2+(1-x^2)*(1-b^2)-(1+b*x)^2"))
mu_tilde = E("(x+b)/(1+b*x)")
check("I03_SOLID_ANGLE_JACOBIAN", mu_tilde.derivative(x) - E("(1-b^2)/(1+b*x)^2"))

T0 = a0 + a1*x + a2*x**2 + a3*x**3
xs1 = x - b*(1-x**2)
full_temperature_first_order = (1+b*x)*(a0+a1*xs1+a2*xs1**2+a3*xs1**3)
full_generator = full_temperature_first_order.derivative(b).replace(b, 0)
expected_temperature = x*T0 - (1-x**2)*T0.derivative(x)
check("I05_BLACKBODY_FULL_GENERATOR", full_generator - expected_temperature)
check("I06_BLACKBODY_PRIMITIVE_GAP", full_generator - x*T0 + (1-x**2)*T0.derivative(x))

F0 = c00+c10*nu+c01*x+c20*nu**2+c11*nu*x+c02*x**2+c30*nu**3+c21*nu**2*x+c12*nu*x**2+c03*x**3
nus1 = nu*(1-b*x)
Fpull = c00+c10*nus1+c01*xs1+c20*nus1**2+c11*nus1*xs1+c02*xs1**2+c30*nus1**3+c21*nus1**2*xs1+c12*nus1*xs1**2+c03*xs1**3
spectral_generator = ((1+d*b*x)*Fpull).derivative(b).replace(b, 0)
expected_spectral = x*(d*F0-nu*F0.derivative(nu))-(1-x**2)*F0.derivative(x)
check("I07_SPECTRAL_BOOST_GENERATOR", spectral_generator-expected_spectral)

check("I08_REI_EXACT_SIGMA_RESIDUAL", ((-h)-(-h-sigmaEE))-sigmaEE)

ex, ey, ez, ax, ay, az, ox, oy, oz = S("ex", "ey", "ez", "ax", "ay", "az", "ox", "oy", "oz")
s11, s12, s13, s22, s23, s33 = S("s11", "s12", "s13", "s22", "s23", "s33")
n11, n12, n13, n22, n23, n33 = S("n11", "n12", "n13", "n22", "n23", "n33")
sEE = s11*ex**2+2*s12*ex*ey+2*s13*ex*ez+s22*ey**2+2*s23*ey*ez+s33*ez**2
aE = ax*ex+ay*ey+az*ez
se1, se2, se3 = s11*ex+s12*ey+s13*ez, s12*ex+s22*ey+s23*ez, s13*ex+s23*ey+s33*ez
ne1, ne2, ne3 = n11*ex+n12*ey+n13*ez, n12*ex+n22*ey+n23*ez, n13*ex+n23*ey+n33*ez
radial = sEE+aE
vx = radial*ex-se1-ax+oy*ez-oz*ey-(ey*ne3-ez*ne2)
vy = radial*ey-se2-ay+oz*ex-ox*ez-(ez*ne1-ex*ne3)
vz = radial*ez-se3-az+ox*ey-oy*ex-(ex*ne2-ey*ne1)
e2 = ex**2+ey**2+ez**2
check("I09_DIRECTION_FLOW_TANGENCY", ex*vx+ey*vy+ez*vz-(e2-1)*radial)

pdot, chid, pplus, omega, ii = S("pdot", "chid", "pplus", "omega", "ii")
check("I10_SCREEN_U1_COVARIANCE", (pdot-2*ii*chid*pplus)+2*ii*(omega+chid)*pplus-(pdot+2*ii*omega*pplus))

mutation("M02_WRONG_JACOBIAN_POWER", b*(1-x**2))
mutation("M03_DROP_BLACKBODY_ABERRATION", -(1-x**2)*T0.derivative(x))
mutation("M04_REI_WRONG_SIGN", -2*sigmaEE)
mutation("M05_REI_WRONG_FACTOR", sigmaEE)
mutation("M06_REI_FOREIGN_CONSTANT", 1-sigmaEE)
mutation("M07_DROP_DIRECTION_RADIAL_COMPENSATOR", -sEE-aE)
mutation("M08_SCREEN_CONNECTION_SIGN", -4*ii*chid*pplus)

print("STATUS|PASS" if failures == 0 else "STATUS|FAIL")
sys.exit(0 if failures == 0 else 1)
