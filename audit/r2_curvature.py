"""R2 - explicit ^3S_ab and ^3R closed forms, verified against the frame Ricci."""
import json, numpy as np
from core import (ricci3, stf, S3_explicit, R3_explicit, rand_class_a,
                  rand_class_b, EPS, ID, sym)

rng = np.random.default_rng(20260729)
out = {}

# ---- anchor: unit 3-sphere  n_ab = 2 delta_ab, a = 0  ->  Ric = 2 delta, R = 6
N, A = 2.0 * ID, np.zeros(3)
out['S3_anchor_Ric_err'] = float(abs(ricci3(N, A) - 2 * ID).max())
out['S3_anchor_R_err'] = float(abs(np.trace(ricci3(N, A)) - 6.0))

for name, gen in (('classA', rand_class_a), ('classB_jacobi', rand_class_b),
                  ('general_noJacobi', lambda r: (sym(r.normal(size=(3, 3))), r.normal(size=3)))):
    eS, eR = 0.0, 0.0
    for _ in range(400):
        N, A = gen(rng)
        Ric = ricci3(N, A)
        eS = max(eS, float(abs(stf(Ric) - S3_explicit(N, A)).max()))
        eR = max(eR, float(abs(np.trace(Ric) - R3_explicit(N, A))))
    out[f'S3_explicit_err_{name}'] = eS
    out[f'R3_explicit_err_{name}'] = eR

# ---- Wainwright-Ellis class A cross-check:  N = diag(N1,N2,N3)
#      ^3S_+ = (1/6)[ (N1 - N2)(N1 - N3) + ... ] is easiest tested via components
e = 0.0
for _ in range(400):
    n1, n2, n3 = rng.normal(size=3)
    N = np.diag([n1, n2, n3])
    S = stf(ricci3(N, np.zeros(3)))
    # WE (1997) eq. (6.35):  S_+ = (1/6)[ (n2-n3)^2 - n1(2n1-n2-n3) ]
    #                        S_- = (1/(2 sqrt3)) (n3-n2)(n1-n2-n3)
    Sp = (1.0 / 6.0) * ((n2 - n3) ** 2 - n1 * (2 * n1 - n2 - n3))
    Sm = (1.0 / (2 * np.sqrt(3.0))) * (n3 - n2) * (n1 - n2 - n3)
    # S = diag(-2 S_+, S_+ + sqrt3 S_-, S_+ - sqrt3 S_-)
    pred = np.diag([-2 * Sp, Sp + np.sqrt(3) * Sm, Sp - np.sqrt(3) * Sm])
    e = max(e, float(abs(S - pred).max()))
out['WE_classA_Splus_Sminus_err'] = e

# ---- the reviewer's exact wording, term by term (isolate any coefficient error)
def term1(N):  return stf(2 * (N @ N) - np.trace(N) * N)
def term2(N, A):  return stf(np.einsum('cda,c,bd->ab', EPS, A, N))
worst = {}
for coef in (0.0, 1.0, 2.0, -2.0):
    e = 0.0
    for _ in range(200):
        N, A = rand_class_b(rng)
        e = max(e, float(abs(stf(ricci3(N, A)) - term1(N) - coef * term2(N, A)).max()))
    worst[f'coef_{coef:+.0f}'] = e
out['A_term_coefficient_scan'] = worst

print(json.dumps(out, indent=2))
json.dump(out, open('r2_curvature.json', 'w'), indent=2)
