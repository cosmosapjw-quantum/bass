"""
D8, D11, D12 --- collisionless (free-streaming) species on a Bianchi background.

Bianchi I exact statement (verified in d_transport.py):
    the covariant momentum components in the invariant basis are constant,
        p_i = a_i P^i = const ,      E = sqrt(m^2 + sum_i (p_i/a_i)^2)
so every moment is a fixed-domain quadrature:

    rho    = (1/V) * Int d^3p_i  E        f0(p_i)
    p      = (1/V) * Int d^3p_i (|P|^2/3E) f0(p_i)
    pi_ab  = (1/V) * Int d^3p_i (P_a P_b - |P|^2 d_ab/3)/E  f0(p_i)
    V      = a1 a2 a3

Verification: energy conservation for a species with q_a = 0,
    rho' + 3H(rho + p) + sigma_ab pi^ab = 0
must hold identically along the flow (this is nabla^a T_ab = 0, b = 0).
"""
import numpy as np, json, itertools

out = {}
rng = np.random.default_rng(20260729)

# --------------------------------------------------- quadrature grid in p_i
NR, NANG = 96, 24          # radial x angular (Lebedev-free: product Gauss)
xr, wr = np.polynomial.legendre.leggauss(NR)
xc, wc = np.polynomial.legendre.leggauss(NANG)                 # cos theta
phi = 2 * np.pi * (np.arange(NANG) + 0.5) / NANG
wphi = np.full(NANG, 2 * np.pi / NANG)

# radial map q in (0, inf):  q = L * (1+x)/(1-x)
L = 3.0
q = L * (1 + xr) / (1 - xr)
dq = wr * 2 * L / (1 - xr) ** 2

st = np.sqrt(1 - xc ** 2)
NHAT = np.stack([np.outer(st, np.cos(phi)).ravel(),
                 np.outer(st, np.sin(phi)).ravel(),
                 np.outer(xc, np.ones_like(phi)).ravel()], axis=-1)   # (NANG^2, 3)
WANG = np.outer(wc, wphi).ravel()


def moments(a_vec, mass, f0):
    """rho, p, pi_ab for a free-streaming species with initial distribution f0(q)."""
    a_vec = np.asarray(a_vec, float)
    V = float(np.prod(a_vec))
    P = (q[:, None, None] * NHAT[None, :, :]) / a_vec[None, None, :]   # P^i = p_i/a_i
    P2 = np.einsum('rai,rai->ra', P, P)
    E = np.sqrt(mass ** 2 + P2)
    w = (dq[:, None] * q[:, None] ** 2) * WANG[None, :] * f0(q)[:, None] / V
    rho = float((w * E).sum())
    pr = float((w * P2 / (3 * E)).sum())
    pi = np.einsum('ra,rai,raj->ij', w / E, P, P) - np.eye(3) * (w * P2 / (3 * E)).sum()
    return rho, pr, pi


def f_FD(q_):                       # relativistic Fermi-Dirac, T = 1
    return 1.0 / (np.exp(np.minimum(q_, 700.0)) + 1.0)


# =================================================== isotropic limits
a_iso = np.array([1.0, 1.0, 1.0])
r0, p0, pi0 = moments(a_iso, 0.0, f_FD)
out['D12_isotropic_pi_is_zero'] = float(np.abs(pi0).max())
out['D12_massless_w'] = float(p0 / r0)
r1, p1, _ = moments(a_iso * 2.0, 0.0, f_FD)
out['D12_massless_rho_scaling_exponent'] = float(np.log(r1 / r0) / np.log(0.5))
rm0, pm0, _ = moments(a_iso, 50.0, f_FD)
rm1, pm1, _ = moments(a_iso * 2.0, 50.0, f_FD)
out['D8_nonrel_rho_scaling_exponent'] = float(np.log(rm1 / rm0) / np.log(0.5))
out['D8_nonrel_w'] = float(pm0 / rm0)

# =================================================== anisotropic: pi_ab sign
a_an = np.array([1.3, 0.9, 0.85])
ra, pa, pia = moments(a_an, 0.0, f_FD)
out['D12_anisotropic_pi_diag'] = np.round(np.diag(pia) / ra, 8).tolist()
out['D12_pi_is_tracefree'] = float(abs(np.trace(pia)) / ra)

# =================================================== D12 : energy conservation
def run(mass, Sigma0, nsteps=40000, T=0.6, include_pi=True):
    """Bianchi I + free-streaming species; check rho' + 3H(rho+p) + sigma.pi = 0."""
    lna = np.zeros(3)
    H = 1.0
    sig = np.array(Sigma0, float) * H
    dt = T / nsteps
    worst = 0.0
    hist = []
    for i in range(nsteps):
        a_vec = np.exp(lna)
        rho, pr, pi = moments(a_vec, mass, f_FD)
        # geometry
        Hd = -H ** 2 - (sig @ sig) / 3.0 - (rho + 3 * pr) / 6.0
        sd = -3 * H * sig + (np.diag(pi) if include_pi else 0.0)
        # numerical d rho/dt from the quadrature itself
        h = 1e-6
        rp, _, _ = moments(np.exp(lna + h * (H + sig)), mass, f_FD)
        rm_, _, _ = moments(np.exp(lna - h * (H + sig)), mass, f_FD)
        drho = (rp - rm_) / (2 * h)
        resid = drho + 3 * H * (rho + pr) + float(np.einsum('ij,ij->', np.diag(sig), pi))
        worst = max(worst, abs(resid) / max(rho, 1e-30))
        lna += dt * (H + sig); H += dt * Hd; sig += dt * sd
        if i % (nsteps // 60) == 0:
            hist.append(dict(lnl=float(lna.mean()), Sig=float(np.sqrt((sig @ sig)
                                                                     / (6 * H ** 2)) * np.sqrt(3)),
                             H=float(H)))
        if H <= 0 or not np.isfinite(H):
            break
    return worst, hist


w1, h1 = run(0.0, [0.15, -0.05, -0.10], nsteps=4000, T=0.4)
out['D12_energy_conservation_relresid_massless'] = w1
w2, h2 = run(3.0, [0.15, -0.05, -0.10], nsteps=4000, T=0.4)
out['D12_energy_conservation_relresid_massive'] = w2

# =================================================== shear damping (Misner)
_, hd_on = run(0.0, [0.20, -0.08, -0.12], nsteps=3000, T=0.5, include_pi=True)
_, hd_off = run(0.0, [0.20, -0.08, -0.12], nsteps=3000, T=0.5, include_pi=False)
out['D12_shear_damping'] = dict(
    Sigma_final_with_freestreaming=hd_on[-1]['Sig'],
    Sigma_final_perfect_fluid=hd_off[-1]['Sig'],
    ratio=hd_on[-1]['Sig'] / hd_off[-1]['Sig'])

# =================================================== small-anisotropy law
# pi_ab ~= -C * sigma_ab / H  for |Sigma| << 1  -> identify C for massless FD
Cs = {}
for d in (0.05, 0.02, 0.01, 0.004, 0.002):
    lna = np.array([2 * d, -d, -d])                # traceless: volume preserved
    rho, pr, pi = moments(np.exp(lna), 0.0, f_FD)
    Cs[f'delta={d}'] = float(pi[0, 0] / (rho * lna[0]))
out['D12_sudden_response_pi_over_rho_dlna'] = {k: round(v, 8) for k, v in Cs.items()}
out['D12_sudden_response_limit_vs_-8/15'] = float(
    abs(Cs['delta=0.002'] + 8.0 / 15.0))
# massive gas: coefficient must go to 0 in the nonrelativistic limit
rho_m, _, pi_m = moments(np.exp(np.array([0.004, -0.002, -0.002])), 60.0, f_FD)
out['D8_sudden_response_massive'] = float(pi_m[0, 0] / (rho_m * 0.004))

print(json.dumps(out, indent=2, default=str))
json.dump(out, open('d_kinetic.json', 'w'), indent=2, default=str)
