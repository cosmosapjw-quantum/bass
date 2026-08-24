"""
R5 - Bianchi IX D-normalisation: derive Hbar', Sigmabar', Nbar', Omegabar' and
     identify Fbar, by direct chain rule on the dimensionful class-A system.

  D^2 = H^2 + (1/6)(n1 n2 + n1 n3 + n2 n3) ,  3 D^2 = sigma^2 + rho + (1/4) sum n_i^2
  d tau_- / dt = -D          (past directed)
"""
import numpy as np, json
from core import ricci3, stf

rng = np.random.default_rng(20260729)
out = {}


def deriv(H, sig, n, rho, gam):
    """dimensionful RHS of the diagonal class-A system with one non-tilted fluid."""
    S3 = np.diag(stf(ricci3(np.diag(n), np.zeros(3))))
    Hd = -H ** 2 - (sig @ sig) / 3.0 - (rho + 3 * (gam - 1) * rho) / 6.0
    sd = -3 * H * sig - S3
    nd = n * (-H + 2 * sig)
    rd = -3 * H * gam * rho
    return Hd, sd, nd, rd, S3


def sample():
    n = rng.uniform(0.2, 2.0, size=3)
    sig = rng.normal(size=3) * 0.7
    sig -= sig.mean()
    H = float(rng.normal())
    R3 = -0.5 * (2 * (n @ n) - n.sum() ** 2)
    rho = 3 * H ** 2 - 0.5 * (sig @ sig) + 0.5 * R3
    gam = float(rng.uniform(0.5, 1.9))
    return H, sig, n, rho, gam


rows_F, rhs_F = [], []
errs = {'H': 0.0, 'S': 0.0, 'N': 0.0, 'O': 0.0, 'gauss': 0.0, 'D2': 0.0, 'trace': 0.0}
for _ in range(400):
    H, sig, n, rho, gam = sample()
    if rho <= 0:
        continue
    Hd, sd, nd, rd, S3 = deriv(H, sig, n, rho, gam)
    D2 = H ** 2 + (n[0] * n[1] + n[0] * n[2] + n[1] * n[2]) / 6.0
    D = np.sqrt(D2)
    errs['D2'] = max(errs['D2'], abs(3 * D2 - (0.5 * (sig @ sig) + rho + 0.25 * (n @ n))))

    Hb, Sb, Nb, Ob = H / D, sig / D, n / D, rho / (3 * D2)
    S3b = S3 / D2
    errs['gauss'] = max(errs['gauss'],
                        abs((Sb @ Sb) / 6.0 + (Nb @ Nb) / 12.0 + Ob - 1.0))
    errs['trace'] = max(errs['trace'], abs(Hb ** 2 + (Nb[0] * Nb[1] + Nb[0] * Nb[2]
                                                      + Nb[1] * Nb[2]) / 6.0 - 1.0))
    Dd = (H * Hd + (nd[0] * n[1] + n[0] * nd[1] + nd[0] * n[2] + n[0] * nd[2]
                    + nd[1] * n[2] + n[1] * nd[2]) / 12.0) / D
    q = -1.0 - Hd / H ** 2                      # singular at H=0
    qD = 2 * (Sb @ Sb) / 6.0 + 0.5 * (3 * gam - 2) * Ob   # regular: qD = q Hbar^2

    Hbp = -Hd / D2 + Hb * Dd / D2
    Sbp = -sd / D2 + Sb * Dd / D2
    Nbp = -nd / D2 + Nb * Dd / D2
    Obp = -rd / (3 * D2 * D) + 2 * Ob * Dd / D2

    Fb = -Dd / D2 - (1 + qD) * Hb
    errs['qD'] = max(errs.get('qD', 0.0), abs(qD - q * Hb ** 2))
    errs['Fclosed'] = max(errs.get('Fclosed', 0.0), abs(
        Fb - (Nb[0]*Nb[1]*Sb[2] + Nb[0]*Sb[1]*Nb[2] + Sb[0]*Nb[1]*Nb[2]) / 6.0))
    errs['S'] = max(errs['S'], float(np.abs(Sbp - (Sb * ((2 - qD) * Hb - Fb) + S3b)).max()))
    errs['N'] = max(errs['N'], float(np.abs(Nbp + Nb * (qD * Hb + 2 * Sb + Fb)).max()))
    errs['H'] = max(errs['H'], abs(Hbp - (qD * (1 - Hb ** 2) - Fb * Hb)))
    errs['O'] = max(errs['O'], abs(Obp - Ob * ((3 * gam - 2 - 2 * qD) * Hb - 2 * Fb)))

    basis = [(Nb[0]*Nb[1]*Sb[2] + Nb[0]*Sb[1]*Nb[2] + Sb[0]*Nb[1]*Nb[2]) / 6.0,

             qD * Hb * (1 - Hb ** 2), Hb * (1 - Hb ** 2)]
    rows_F.append(basis); rhs_F.append(Fb)

coefF, *_ = np.linalg.lstsq(np.array(rows_F), np.array(rhs_F), rcond=None)
resF = float(abs(np.array(rows_F) @ coefF - np.array(rhs_F)).max())
out['Fbar_basis'] = dict(zip(
    ['(1/6)(N1N2S3+N1S2N3+S1N2N3)', 'qD Hb (1-Hb^2)', 'Hb (1-Hb^2)'], [float(np.round(c, 12)) for c in coefF]))
out['Fbar_fit_maxres'] = resF
out['residuals'] = {k: float(v) for k, v in errs.items()}
print(json.dumps(out, indent=2))
json.dump(out, open('r5e_typeIX_D.json', 'w'), indent=2)
