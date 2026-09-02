#!/usr/bin/env python3
from __future__ import annotations

import sys
import z3

failures = 0


def prove_zero(identity_id: str, expression: z3.ArithRef, constraints: list[z3.BoolRef] | None = None) -> None:
    global failures
    solver = z3.SolverFor("QF_NRA")
    solver.set(timeout=30000)
    if constraints:
        solver.add(*constraints)
    solver.add(expression != 0)
    result = solver.check()
    if result == z3.unsat:
        print(f"CHECK|{identity_id}|PASS")
    else:
        print(f"CHECK|{identity_id}|FAIL|{result}")
        failures += 1


def prove_bool(identity_id: str, proposition: z3.BoolRef) -> None:
    global failures
    solver = z3.SolverFor("QF_NRA")
    solver.set(timeout=30000)
    solver.add(z3.Not(proposition))
    result = solver.check()
    if result == z3.unsat:
        print(f"CHECK|{identity_id}|PASS")
    else:
        print(f"CHECK|{identity_id}|FAIL|{result}")
        failures += 1


def mutation_witness(mutation_id: str, expression: z3.ArithRef, assignments: list[z3.BoolRef]) -> None:
    global failures
    solver = z3.SolverFor("QF_NRA")
    solver.set(timeout=30000)
    solver.add(*assignments)
    solver.add(expression != 0)
    result = solver.check()
    if result == z3.sat:
        print(f"MUTATION|{mutation_id}|PASS")
    else:
        print(f"MUTATION|{mutation_id}|FAIL|{result}")
        failures += 1


b, x, g = z3.Reals("b x g")
mu_tilde_num = x + b
mu_tilde_den = 1 + b*x

# Cross-multiplied exact identities avoid hidden division-by-zero assumptions.
prove_zero(
    "I02_AXIAL_ABERRATION_UNIT_NORM",
    mu_tilde_num**2 + (1 - x**2)*(1 - b**2) - mu_tilde_den**2,
)
prove_zero(
    "I03_SOLID_ANGLE_JACOBIAN",
    mu_tilde_den - b*mu_tilde_num - (1 - b**2),
)
prove_zero(
    "I04_INVERSE_DOPPLER",
    mu_tilde_den - b*mu_tilde_num - (1 - b**2),
)

h, sigmaEE = z3.Reals("h sigmaEE")
rei_difference = (-h) - (-h - sigmaEE)
prove_zero("I08_REI_EXACT_SIGMA_RESIDUAL", rei_difference - sigmaEE)

ex, ey, ez, ax, ay, az, ox, oy, oz = z3.Reals("ex ey ez ax ay az ox oy oz")
s11, s12, s13, s22, s23, s33 = z3.Reals("s11 s12 s13 s22 s23 s33")
n11, n12, n13, n22, n23, n33 = z3.Reals("n11 n12 n13 n22 n23 n33")
sEE = s11*ex**2 + 2*s12*ex*ey + 2*s13*ex*ez + s22*ey**2 + 2*s23*ey*ez + s33*ez**2
aE = ax*ex + ay*ey + az*ez
se1 = s11*ex + s12*ey + s13*ez
se2 = s12*ex + s22*ey + s23*ez
se3 = s13*ex + s23*ey + s33*ez
ne1 = n11*ex + n12*ey + n13*ez
ne2 = n12*ex + n22*ey + n23*ez
ne3 = n13*ex + n23*ey + n33*ez
radial = sEE + aE
vx = radial*ex - se1 - ax + oy*ez - oz*ey - (ey*ne3 - ez*ne2)
vy = radial*ey - se2 - ay + oz*ex - ox*ez - (ez*ne1 - ex*ne3)
vz = radial*ez - se3 - az + ox*ey - oy*ex - (ex*ne2 - ey*ne1)
e2 = ex**2 + ey**2 + ez**2
prove_zero("I09_DIRECTION_FLOW_TANGENCY", ex*vx + ey*vy + ez*vz - (e2 - 1)*radial)

pdot, chid, pplus, omega = z3.Reals("pdot chid pplus omega")
screen_coefficient = (pdot - 2*chid*pplus) + 2*(omega + chid)*pplus - (pdot + 2*omega*pplus)
prove_zero("I10_SCREEN_U1_COVARIANCE", screen_coefficient)

# Domain theorem: gamma>0 and gamma^2(1-beta^2)=1 imply D=gamma(1+beta*mu)>0.
mu = z3.Real("mu")
D = g*(1 + b*mu)
prove_bool(
    "I12_DOPPLER_POSITIVITY_DOMAIN",
    z3.Implies(
        z3.And(b >= 0, b < 1, mu >= -1, mu <= 1, g > 0, g*g*(1 - b*b) == 1),
        D > 0,
    ),
)

mutation_witness("M01_WRONG_DOPPLER_SIGN", -2*g*b*x, [g == 2, b == z3.RealVal("1/10"), x == z3.RealVal("1/3")])
mutation_witness("M02_WRONG_JACOBIAN_POWER", b*(1 - x**2), [b == z3.RealVal("1/2"), x == z3.RealVal("1/3")])
mutation_witness("M04_REI_WRONG_SIGN", -2*sigmaEE, [sigmaEE == 1])
mutation_witness("M05_REI_WRONG_FACTOR", sigmaEE, [sigmaEE == 1])
mutation_witness("M06_REI_FOREIGN_CONSTANT", 1 - sigmaEE, [sigmaEE == 2])
mutation_witness("M07_DROP_DIRECTION_RADIAL_COMPENSATOR", -sEE - aE, [s11 == 1, ex == 1, ey == 0, ez == 0, ax == 0, ay == 0, az == 0])
mutation_witness("M08_SCREEN_CONNECTION_SIGN", -4*chid*pplus, [chid == 1, pplus == 1])

print("STATUS|PASS" if failures == 0 else "STATUS|FAIL")
sys.exit(0 if failures == 0 else 1)
