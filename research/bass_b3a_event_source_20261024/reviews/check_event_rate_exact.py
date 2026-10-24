"""Independent exact pair-contraction checks for BASS B3a.

All arrays here are K/P or c Q/P, hence dimensionless. The accompanying
review retains c in the dimensional equations. No IVP or campaign replay.
"""
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import platform
import time


def moments(beta, gamma, fixture):
    """Exact antipodal-pair contraction, avoiding irrational cube coordinates.

    A: n = +/- e_j. B: n = +/- s/sqrt(3), s_x=1, s_y,z=+/-1.
    If n=+/-sqrt(v)*s, Lorentz spatial momentum is a+/-sqrt(v)*z.
    The antipodal average of pp/p0 is the rational expression below.
    """
    beta = list(map(F, beta))
    gamma = F(gamma)
    beta2 = sum(x*x for x in beta)
    if gamma*gamma*(1-beta2) != 1 or gamma < 1:
        raise ValueError("inconsistent exact timelike boost")
    a = [gamma*x for x in beta]
    k = (gamma-1)/beta2 if beta2 else F(0)
    if fixture == "A":
        directions = [(1,0,0),(0,1,0),(0,0,1)]
        v = F(1)
    elif fixture == "B":
        directions = [(1,sy,sz) for sy,sz in product((-1,1), repeat=2)]
        v = F(1,3)
    else:
        raise ValueError("unknown fixture")
    pairs = []
    for s in directions:
        t = sum(beta[i]*s[i] for i in range(3))
        z = [s[i]+k*beta[i]*t for i in range(3)]
        denom = gamma*(1-v*t*t)
        assert denom > 0
        pairs.append([[
            (a[i]*a[j]+v*z[i]*z[j]-v*t*(a[i]*z[j]+a[j]*z[i]))/denom
            for j in range(3)] for i in range(3)])
    pressure = [[sum(x[i][j] for x in pairs)/len(pairs)
                 for j in range(3)] for i in range(3)]
    pi = [[pressure[i][j]-(gamma/3 if i == j else 0)
           for j in range(3)] for i in range(3)]
    return {"Q": [gamma]+a, "pressure": pressure, "pi": pi}


def diag(x, y, z):
    return [[x,0,0],[0,y,0],[0,0,z]]


def sub(A, B):
    return [[A[i][j]-B[i][j] for j in range(3)] for i in range(3)]


def serial(obj):
    if isinstance(obj, F):
        return str(obj)
    if isinstance(obj, dict):
        return {k: serial(v) for k,v in obj.items()}
    if isinstance(obj, list):
        return [serial(v) for v in obj]
    return obj


def main():
    wall0, cpu0 = time.perf_counter(), time.process_time()
    checks = []
    def check(name, condition):
        checks.append({"name": name, "pass": bool(condition)})
        if not condition:
            raise AssertionError(name)
    restA=moments((0,0,0),1,"A")
    restB=moments((0,0,0),1,"B")
    check("equal_rest_Q", restA["Q"] == restB["Q"] == [1,0,0,0])
    check("equal_rest_pressure", restA["pressure"] == restB["pressure"] == diag(F(1,3),F(1,3),F(1,3)))
    A=moments((F(3,5),0,0),F(5,4),"A")
    B=moments((F(3,5),0,0),F(5,4),"B")
    check("boosted_Q", A["Q"] == B["Q"] == [F(5,4),F(3,4),0,0])
    check("axis_PiRate_A", A["pi"] == diag(F(3,10),F(-3,20),F(-3,20)))
    check("axis_PiRate_B", B["pi"] == diag(F(5,22),F(-5,44),F(-5,44)))
    check("axis_difference", sub(A["pi"],B["pi"]) == diag(F(4,55),F(-2,55),F(-2,55)))
    wrongQ=[F(5,4)**2*(1+F(3,5)**2/3), F(4,3)*F(5,4)**2*F(3,5),0,0]
    check("wrong_fixed_u_identification", wrongQ == [F(7,4),F(5,4),0,0] and wrongQ != A["Q"])
    # Rational beta,gamma parametrization: beta=2t/(1+t^2), gamma=(1+t^2)/(1-t^2).
    for t in (F(0),F(1,9),F(1,3),F(1,2),F(3,4),F(9,10),F(-1,3)):
        b=2*t/(1+t*t)
        g=(1+t*t)/(1-t*t)
        a=moments((b,0,0),g,"A")
        bcase=moments((b,0,0),g,"B")
        wanted=2*b*b/(3*g*(3-b*b))
        check("axis_formula_t="+str(t), a["pi"][0][0]-bcase["pi"][0][0] == wanted)
        check("null_trace_t="+str(t), all(sum(case["pressure"][i][i] for i in range(3))==g for case in (a,bcase)))
    genericA=moments((F(1,5),F(2,5),F(2,5)),F(5,4),"A")
    genericB=moments((F(1,5),F(2,5),F(2,5)),F(5,4),"B")
    genericDelta=sub(genericA["pi"],genericB["pi"])
    check("generic_direction_distinguishes_axis_formula", genericDelta[0][0] == F(-286408,10384605) and genericDelta[0][0] != F(4,55))
    check("generic_delta_trace_zero", sum(genericDelta[i][i] for i in range(3)) == 0)
    result={
        "method":"exact rational antipodal-pair contraction; independent of supplied WL implementation",
        "execution_class":"lightweight_algebra_only",
        "python": platform.python_version(),
        "fixture_axis":{"A":A,"B":B,"wrongQ":wrongQ},
        "generic_direction":{"beta":[F(1,5),F(2,5),F(2,5)],"gamma":F(5,4),"delta_pi":genericDelta},
        "checks":checks,"passed":len(checks),"failed":0,
        "new_IVPs":0,"old_campaign_replays":0,
        "remaining_campaign_wall_seconds":None,
        "remaining_campaign_cpu_seconds":None,"budget_reset":False,
        "wall_seconds":time.perf_counter()-wall0,
        "cpu_seconds":time.process_time()-cpu0,
    }
    path=Path(__file__).with_name("THEORY_EXACT_CHECKS.json")
    path.write_text(json.dumps(serial(result),indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ("passed","failed","wall_seconds","cpu_seconds","new_IVPs","old_campaign_replays")}))


if __name__ == "__main__":
    main()
