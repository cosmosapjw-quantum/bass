"""FA03 R9: source-bound exact-rational evaluator for the fixed 36-ray model.

This does not solve transport, integrate a continuous cap, or fit real opacity.
The original R7 binary64 reference coefficients are deliberately read exactly
as dyadic rationals, while the stronger uncertainty consumes the distinct peer
R7 interval certificate through its reviewed interoperability relation.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_SHA = {
    "R7_MAIN_CERTIFICATE.json": "cac2515682821deebe7eb30770a27b30dc7576522c3a1f6101ef0e70e2486adc",
    "R7_PEER_CERTIFICATE.json": "46d588c48b0518648914e7dcc98c04fe3ddca1c861d1bdcb5bfca92a5cc7d874",
    "R7_CROSS_CERTIFICATE.json": "22af9f2b4ec95a4c885fca413c1a3a7a07e5c3db3ed99ef89f70a9c1002bcd2b",
    "R8_RESULT.json": "d1ff491795b40c47a3f1391934be0b6c52f777367fcb02414e59f05c753be246",
}
C3 = Fraction(926402349807, 1953125000000000)
MAX_EPS = Fraction(1, 10)
STOKES_ORDER = ("I", "Q", "U", "V")
DERIVATIVE_ORDER = ("S0", "V0", "W0")

class ContractHold(ValueError):
    pass


def exact(value) -> Fraction:
    """No binary64->decimal guess: caller supplies Fraction, str, or integer."""
    if isinstance(value, float):
        raise ContractHold("HOLD_FLOAT_INPUT_AMBIGUOUS_USE_DECIMAL_STRING_OR_FRACTION")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    raise ContractHold("HOLD_UNSUPPORTED_NUMERIC_ENCODING")


def to_decimal(value: Fraction, precision: int = 35) -> str:
    with localcontext() as ctx:
        ctx.prec = precision
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def sqrt_bracket(x: Fraction, decimal_places: int = 30) -> tuple[Fraction, Fraction]:
    """Proven dyadic/integer enclosing bracket, not rounded floating sqrt."""
    if x < 0: raise ContractHold("HOLD_SQRT_NEGATIVE")
    if decimal_places < 0 or decimal_places > 70: raise ContractHold("HOLD_PRECISION")
    scale = 10 ** decimal_places
    lower_int = isqrt((x.numerator * scale * scale) // x.denominator)
    lower = Fraction(lower_int, scale)
    # An exact square can avoid a needless upper increment.
    upper = lower if lower * lower == x else Fraction(lower_int + 1, scale)
    assert lower * lower <= x <= upper * upper
    return lower, upper


def trace_norm_stokes(vec: tuple[Fraction, ...], decimal_places=30):
    """For Hermitian F=(I sigma0+Q sigma3+U sigma1+V sigma2)/2,
    ||F||_1=max(|I|,sqrt(Q^2+U^2+V^2))."""
    if len(vec) != 4: raise ContractHold("HOLD_STOKES_SHAPE")
    lo, hi = sqrt_bracket(sum(v*v for v in vec[1:]), decimal_places)
    return max(abs(vec[0]),lo), max(abs(vec[0]),hi)


@dataclass(frozen=True)
class FA03Snapshot:
    source_shas: dict
    reference: dict
    main: dict
    peer: dict
    cross: dict
    adopted: dict
    row: tuple[tuple[Fraction, ...], ...]
    radii: tuple[Fraction, Fraction, Fraction]


def load_contract(root: Path = ROOT) -> FA03Snapshot:
    root = Path(root)
    contents = {}
    for filename, h in EXPECTED_SHA.items():
        p = root / "reference" / filename
        if not p.exists(): raise ContractHold("HOLD_MISSING_SOURCE_" + filename)
        data = p.read_bytes()
        if sha256(data).hexdigest() != h:
            raise ContractHold("HOLD_SOURCE_BYTE_IDENTITY_" + filename)
        contents[filename] = json.loads(data)
    main = contents["R7_MAIN_CERTIFICATE.json"]
    peer = contents["R7_PEER_CERTIFICATE.json"]
    cross = contents["R7_CROSS_CERTIFICATE.json"]
    adopted = contents["R8_RESULT.json"]
    if [main["rays"],main["cells_per_ray"]] != [36,64]: raise ContractHold("HOLD_MODEL_RAY_IDENTITY")
    if main["base_parameters"] != {"chi":"1/125","psi":"1/100","delta":"1/50"}:
        raise ContractHold("HOLD_FIXED_OBSERVER")
    if not cross["pass"] or cross["component_interval_mappings"] != 24 or cross["block_containments"] != 6:
        raise ContractHold("HOLD_PEER_INTEROPERABILITY")
    if cross["common_parent_sha256"] != "c040514105fa856b05a8792a628e441a2ad73c991cc253b94b7646425d8bb0e8":
        raise ContractHold("HOLD_FA03_SOURCE_PARENT")
    rows = tuple(tuple(Fraction(int(n),int(d)) for n,d in stokes) for stokes in main["reference_stokes"])
    if len(rows)!=6 or any(len(row)!=4 for row in rows):raise ContractHold("HOLD_COMPONENT_SCHEMA")
    vals = cross["state_checks"]
    if [v["state"] for v in vals] != ["S0","S1","S2","V0","V1","W0"]:
        raise ContractHold("HOLD_STATE_ORDER")
    radii = tuple(Fraction(*map(int, vals[i]["main_reference_error_from_peer_box"])) for i in [0,3,5])
    coef = radii[0]+MAX_EPS*radii[1]+MAX_EPS**2*radii[2]/2
    if coef != exact(adopted["coefficient_error"]):raise ContractHold("HOLD_EXACT_COEFFICIENT_BOUND")
    if coef + C3*MAX_EPS**3 != exact(adopted["total_error"]):
        raise ContractHold("HOLD_R8_GLOBAL_BOUND")
    if not (coef + C3*MAX_EPS**3 < Fraction(475,10**9)):
        raise ContractHold("HOLD_PREDECLARED_ERROR_TARGET")
    return FA03Snapshot(EXPECTED_SHA,contents,main,peer,cross,adopted,rows,radii)


def evaluate(snapshot: FA03Snapshot, epsilon: str | Fraction):
    e=exact(epsilon)
    if abs(e)>MAX_EPS:raise ContractHold("HOLD_EPS_OUTSIDE_SOURCE_DOMAIN")
    s,v,w=[snapshot.row[i] for i in [0,3,5]]
    p=tuple(s[j]+e*v[j]+e*e*w[j]/2 for j in range(4))
    r0,r1,r2=snapshot.radii
    error=r0+abs(e)*r1+e*e*r2/2+C3*abs(e)**3
    assert error<=exact(snapshot.adopted["total_error"])<Fraction(475,10**9)
    plo,phi=sqrt_bracket(sum(z*z for z in p[1:]))
    I=p[0]
    if I-error<=0:raise ContractHold("HOLD_NO_POSITIVE_INTENSITY_LOWER")
    # ||delta F||1 also bounds the length of the three-vector of Stokes components.
    pol_lower=max(Fraction(0),plo-error)
    pol_upper=phi+error
    degree_lower=pol_lower/(I+error)
    degree_upper=pol_upper/(I-error)
    lam_lower=(I-phi)/2-error
    if lam_lower<=0:raise ContractHold("HOLD_NO_PSD_MARGIN")
    return {
        "epsilon_exact":str(e), "predicted_stokes_exact":[str(x) for x in p],
        "predicted_stokes_decimal":dict(zip(STOKES_ORDER,[to_decimal(x,25) for x in p])),
        "Schatten1_error_bound_exact":str(error),"Schatten1_error_bound_decimal":to_decimal(error,25),
        "certified_intensity_interval_exact":[str(I-error),str(I+error)],
        "certified_polarization_amplitude_interval_exact":[str(pol_lower),str(pol_upper)],
        "certified_polarization_degree_interval_exact":[str(degree_lower),str(degree_upper)],
        "certified_polarization_degree_interval_display":[to_decimal(degree_lower,20),to_decimal(degree_upper,20)],
        "certified_minimum_eigenvalue_lower_exact":str(lam_lower),
        "certified_minimum_eigenvalue_lower_decimal":to_decimal(lam_lower,25),
        "angular_continuum_error":None,
        "observer_derivative_numerical_error":None,
        "empirical_opacity_error":None,
        "unit":"dimensionless observer coherency; physical band intensity factor c*t_o*E_*^2*j_*(e_+-e_-)",
        "scope":"FIXED_36_RAY_EXACT_GL3x12_WITH_CONTINUOUS_BAND"
    }


def main():
    import argparse
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--root",type=Path,default=ROOT)
    a.add_argument("--epsilon",default="1/10")
    a.add_argument("--out",type=Path)
    args=a.parse_args()
    x=evaluate(load_contract(args.root),args.epsilon)
    # No mutation unless the user supplied an output path; never overwrite.
    out=args.out
    if out is not None:
        with out.open("x") as f:json.dump(x,f,ensure_ascii=False,indent=2)
    print(json.dumps(x,indent=2))

if __name__=="__main__":main()
