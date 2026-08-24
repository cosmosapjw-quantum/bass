"""
D15, D16, D17 --- null-bundle optics on a Bianchi background.

  screen basis  E_A (A=1,2):  k.E_A = 0, u.E_A = 0, parallel transported
  optical tidal matrix         T_AB = -R_{a m b n} k^m k^n E_A^a E_B^b
  Jacobi                       d^2 J/dlam^2 = T J ,  J(0)=0, J'(0)=1
  angular diameter distance    d_A = |det J|^{1/2}
  reciprocity (Etherington)    r_A(source->obs) = (1+z) r_A(obs->source)
"""
import sympy as sp, numpy as np, json
from einstein_frame import einstein, I3, I4
from core import EPS, stf, sym

m = einstein(with_rotation=True)
H, n, a, s, R, Gam, Riem, Ric = (m['H'], m['n'], m['a'], m['s'], m['R'],
                                 m['G'], m['Riem'], m['Ric'])
out = {}

from einstein_frame import t as _t
Hd_ = sp.Derivative(H, _t)
sd_ = [sp.Derivative(s[i, j], _t) for i, j in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2))]
SY = [H] + [n[0, 0], n[0, 1], n[0, 2], n[1, 1], n[1, 2], n[2, 2]] \
     + [a[0], a[1], a[2]] + [s[0, 0], s[0, 1], s[0, 2], s[1, 1], s[1, 2]] \
     + [R[0], R[1], R[2]] + [Hd_] + sd_
plain = {x: sp.Symbol('q%d' % i) for i, x in enumerate(SY)}
args = list(plain.values())
fG = sp.lambdify(args, [[[sp.expand(Gam[i][j][k]).subs(plain, simultaneous=True)
                          for k in I4] for j in I4] for i in I4], 'numpy')
fRm = sp.lambdify(args, [[[[Riem[i][j][k][l].subs(plain, simultaneous=True)
                            for l in I4] for k in I4] for j in I4] for i in I4], 'numpy')
fRic = sp.lambdify(args, [[sp.expand(Ric[i, j]).subs(plain, simultaneous=True)
                           for j in I4] for i in I4], 'numpy')

# ---- fast path: Bianchi I, diagonal shear, no rotation (used by the ray runs)
_zero = {}
for _x in [n[0, 0], n[0, 1], n[0, 2], n[1, 1], n[1, 2], n[2, 2],
           a[0], a[1], a[2], R[0], R[1], R[2],
           s[0, 1], s[0, 2], s[1, 2],
           sp.Derivative(s[0, 1], _t), sp.Derivative(s[0, 2], _t),
           sp.Derivative(s[1, 2], _t)]:
    _zero[_x] = 0
_fast_args = [plain[H], plain[s[0, 0]], plain[s[1, 1]], plain[Hd_],
              plain[sd_[0]], plain[sd_[3]]]
_Rm_I = [[[[sp.expand(Riem[i][j][k][l].subs(_zero, simultaneous=True))
            .subs(plain, simultaneous=True) for l in I4] for k in I4]
          for j in I4] for i in I4]
_G_I = [[[sp.expand(Gam[i][j][k].subs(_zero, simultaneous=True))
          .subs(plain, simultaneous=True) for k in I4] for j in I4] for i in I4]
fRm_I = sp.lambdify(_fast_args, _Rm_I, 'numpy')
fG_I = sp.lambdify(_fast_args, _G_I, 'numpy')


def _fastflat(Hv, sig, Hd, sd):
    return [Hv, sig[0], sig[1], Hd, sd[0], sd[1]]
ETA = np.diag([-1.0, 1.0, 1.0, 1.0])


def flat(Hv, N, A, S, Rv, Hd=None, Sd=None):
    """Hd, Sd default to the vacuum-consistent values (Einstein eqs supply them)."""
    if Hd is None:
        Hd = -Hv ** 2 - np.trace(S @ S) / 3.0
    if Sd is None:
        Sd = -3.0 * Hv * S
    return [Hv, N[0, 0], N[0, 1], N[0, 2], N[1, 1], N[1, 2], N[2, 2],
            A[0], A[1], A[2], S[0, 0], S[0, 1], S[0, 2], S[1, 1], S[1, 2],
            Rv[0], Rv[1], Rv[2], Hd,
            Sd[0, 0], Sd[0, 1], Sd[0, 2], Sd[1, 1], Sd[1, 2]]


rng = np.random.default_rng(20260729)


# ======================================================= D16 : tidal matrix
def tidal(Hv, N, A, S, Rv, k, screen, Hd=None, Sd=None):
    """T_AB = -R^a_{m b n} k^m k^n eta_ac E_A^c E_B^b  (screen-projected)."""
    Rm = np.array(fRm(*flat(Hv, N, A, S, Rv, Hd, Sd)), float)  # R^a_{b c d}
    Rl = np.einsum('aa,abcd->abcd', ETA, Rm) if False else \
        np.einsum('ae,ebcd->abcd', ETA, Rm)                    # R_{a b c d}
    T = np.zeros((2, 2))
    for Aa in range(2):
        for Bb in range(2):
            T[Aa, Bb] = -np.einsum('abcd,a,b,c,d->', Rl, screen[Aa], k,
                                   screen[Bb], k)
    return T


def draw():
    N = sym(rng.normal(size=(3, 3)))
    w, V = np.linalg.eigh(N); kk = int(np.argmin(abs(w))); w[kk] = 0.0
    N = V @ np.diag(w) @ V.T
    A = float(rng.normal()) * V[:, kk]
    return (float(rng.uniform(0.5, 2.0)), N, A, stf(rng.normal(size=(3, 3))),
            rng.normal(size=3))


def screen_of(nh):
    """two unit vectors orthogonal to n-hat (and to e_0)."""
    tmp = np.array([1.0, 0.0, 0.0])
    if abs(nh @ tmp) > 0.9:
        tmp = np.array([0.0, 1.0, 0.0])
    e1 = np.cross(nh, tmp); e1 /= np.linalg.norm(e1)
    e2 = np.cross(nh, e1)
    return np.array([[0.0, *e1], [0.0, *e2]])


# trace of the tidal matrix must equal the Ricci focusing term -R_ab k^a k^b
etr = 0.0
for _ in range(200):
    Hv, N, A, S, Rv = draw()
    nh = rng.normal(size=3); nh /= np.linalg.norm(nh)
    E0 = float(rng.uniform(0.5, 2.0))
    k = np.concatenate([[E0], E0 * nh])
    sc = screen_of(nh)
    T = tidal(Hv, N, A, S, Rv, k, sc)
    Rc = np.array(fRic(*flat(Hv, N, A, S, Rv)), float)
    focus = -np.einsum('ab,a,b->', Rc, k, k)
    etr = max(etr, abs(np.trace(T) - focus))
out['D16_trace_tidal_equals_Ricci_focusing'] = etr

# Weyl part is trace-free and symmetric
esym = 0.0
for _ in range(200):
    Hv, N, A, S, Rv = draw()
    nh = rng.normal(size=3); nh /= np.linalg.norm(nh)
    k = np.concatenate([[1.0], nh]); sc = screen_of(nh)
    T = tidal(Hv, N, A, S, Rv, k, sc)
    esym = max(esym, abs(T[0, 1] - T[1, 0]))
out['D16_tidal_is_symmetric'] = esym

# k is null and R_{abcd}k^b k^d k^a = 0 (k is in the kernel)
eker = 0.0
for _ in range(100):
    Hv, N, A, S, Rv = draw()
    nh = rng.normal(size=3); nh /= np.linalg.norm(nh)
    k = np.concatenate([[1.0], nh])
    Rm = np.array(fRm(*flat(Hv, N, A, S, Rv)), float)
    Rl = np.einsum('ae,ebcd->abcd', ETA, Rm)
    eker = max(eker, abs(np.einsum('abcd,a,b,c,d->', Rl, k, k, k, k)))
    eker = max(eker, abs(k @ ETA @ k))
out['D16_null_kernel_and_k_is_null'] = eker

# ======================================================= D15/D17 : integrate
def _pack(E, nh, sc4, J, dJ, Hv, sig, rho, lna, tt):
    """sc4: (2,4) FULL 4-vector screen basis (audit fix F1: the v1.2 version
    transported only the spatial part and pinned E_A^0 = 0, which violates
    parallel transport whenever sc.sigma.n != 0 and biased d_A at O(Sigma^2);
    the 1.5e-3 reciprocity plateau was exactly this defect)."""
    return np.concatenate([[E], nh, sc4.ravel(), J.ravel(), dJ.ravel(),
                           [Hv], sig, [rho], lna, [tt]])


def _unpack(y):
    return (y[0], y[1:4], y[4:12].reshape(2, 4), y[12:16].reshape(2, 2),
            y[16:20].reshape(2, 2), y[20], y[21:24], y[24], y[25:28], y[28])


def make_deriv(g):
    Z3 = np.zeros((3, 3)); z3 = np.zeros(3)

    def dydt(y):
        """d/dt of everything; ray quantities use d/dt = (1/E) d/dlambda."""
        E, nh, sc4, J, dJ, Hv, sig, rho, lna, tt = _unpack(y)
        S = np.diag(sig)
        Hd = -Hv ** 2 - (sig @ sig) / 3.0 - (rho + 3 * (g - 1) * rho) / 6.0
        Sd = np.diag(-3 * Hv * sig)
        fa = flat(Hv, Z3, z3, S, z3, Hd, Sd)
        Gm = np.array(fG(*fa), float)
        p = np.concatenate([[E], E * nh])
        acc = -np.einsum('acb,c,b->a', Gm, p, p)                  # d p^a/dlam
        dE_dl, dP_dl = acc[0], acc[1:]
        dE = dE_dl / E
        dn = (dP_dl - nh * dE_dl) / E ** 2
        # FULL 4-vector parallel transport of the screen basis (audit fix F1)
        dsc4 = np.array([-np.einsum('acb,c,b->a', Gm, s_, p) / E for s_ in sc4])
        Rm = np.array(fRm(*fa), float)
        Rl = np.einsum('ae,ebcd->abcd', ETA, Rm)
        T = np.array([[-np.einsum('abcd,a,b,c,d->', Rl, sc4[Aa], p, sc4[Bb], p)
                       for Bb in range(2)] for Aa in range(2)])
        return _pack(dE, dn, dsc4, dJ / E, (T @ J) / E,
                     Hd, -3 * Hv * sig, -3 * Hv * g * rho, Hv + sig, 1.0)
    return dydt


def run_ray(model, t0, t_end, nsteps=200000):
    g = model['gamma']
    f = make_deriv(g)
    nh = np.array(model['nhat'], float); nh /= np.linalg.norm(nh)
    sc4 = screen_of(nh).copy()                      # (2,4), E_A^0 = 0 initially
    y = _pack(1.0, nh, sc4, np.zeros((2, 2)), np.eye(2), model['H0'],
              np.array(model['Sigma0']) * model['H0'],
              3 * model['H0'] ** 2 * model['Omega0'], np.zeros(3), t0)
    dt = (t_end - t0) / nsteps
    hist = []
    for i in range(nsteps):
        k1 = f(y); k2 = f(y + .5 * dt * k1); k3 = f(y + .5 * dt * k2); k4 = f(y + dt * k3)
        y = y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        y[1:4] /= np.linalg.norm(y[1:4])
        if not np.isfinite(y).all() or y[20] <= 0:      # y[20] = H (v1.3 repack)
            break
        if i % max(1, nsteps // 400) == 0:
            E, nh_, sc4_, J, dJ, Hv, sig, rho, lna, tt = _unpack(y)
            hist.append(dict(z=float(E - 1.0), dA=float(abs(np.linalg.det(J)) ** .5),
                             lna=lna.copy(), t=float(tt), H=float(Hv)))
    return y, hist


# ---- FLRW (EdS) reference
H0 = 1.0; t0 = 2.0 / (3.0 * H0)
mdl = dict(H0=H0, Sigma0=[0, 0, 0], Omega0=1.0, gamma=1.0, nhat=[0, 0, 1])
yF, hF = run_ray(mdl, t0, 0.20 * t0 * 3, nsteps=120000)
zs = np.array([h['z'] for h in hF]); dAs = np.array([h['dA'] for h in hF])
lnas = np.array([h['lna'][0] for h in hF])
ok = (zs > 0.05) & (zs < 1.5) & np.isfinite(dAs)
pred = (2.0 / H0) * (1.0 - 1.0 / np.sqrt(1 + zs[ok])) / (1 + zs[ok])
out['D17_FLRW_EdS_dA_relerr'] = float(np.max(np.abs(dAs[ok] / pred - 1.0)))
out['D14_FLRW_redshift_relerr'] = float(np.max(
    np.abs(np.exp(-lnas[ok]) - (1 + zs[ok])) / (1 + zs[ok])))
out['D14_zmax_reached'] = float(np.max(zs))

# ---- Etherington / reciprocity: r(s->o) = (1+z) r(o->s)
#      integrate a second bundle from the source back toward the observer
def reciprocity(model, t0, t_src, nsteps=120000):
    y1, h1 = run_ray(model, t0, t_src, nsteps=nsteps)
    E, nh_, sc4_, J, dJ, Hv, sig, rho, lna, tt = _unpack(y1)
    z = E - 1.0
    r_os = abs(np.linalg.det(J)) ** .5
    # forward bundle from the source: same worldline, reversed
    g = model['gamma']
    f = make_deriv(g)
    y2 = _pack(1.0, -nh_, screen_of(-nh_).copy(), np.zeros((2, 2)),
               np.eye(2), Hv, sig, rho, np.zeros(3), tt)
    dt = (t0 - tt) / nsteps
    for i in range(nsteps):
        k1 = f(y2); k2 = f(y2 + .5 * dt * k1); k3 = f(y2 + .5 * dt * k2)
        k4 = f(y2 + dt * k3)
        y2 = y2 + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        y2[1:4] /= np.linalg.norm(y2[1:4])
    J2 = _unpack(y2)[3]
    r_so = abs(np.linalg.det(J2)) ** .5
    return z, r_os, r_so


z_, r_os, r_so = reciprocity(dict(H0=H0, Sigma0=[0.2, -0.05, -0.15], Omega0=0.9,
                                  gamma=1.0, nhat=[0.4, -0.3, 0.87]),
                             t0, 0.42 * t0)
out['D17_reciprocity'] = dict(z=float(z_), r_obs_to_src=float(r_os),
                              r_src_to_obs=float(r_so),
                              relerr=float(abs(r_so / ((1 + z_) * r_os) - 1.0)))

# ---- anisotropy: direction dependence is real
res_dir = {}
for lbl, nhat in (('x', [1, 0, 0]), ('y', [0, 1, 0]), ('z', [0, 0, 1])):
    mdl = dict(H0=H0, Sigma0=[0.25, -0.1, -0.15], Omega0=0.9, gamma=1.0, nhat=nhat)
    y, h = run_ray(mdl, t0, 0.35 * t0, nsteps=60000)
    zz = np.array([x['z'] for x in h]); dd = np.array([x['dA'] for x in h])
    i = int(np.argmin(np.abs(zz - 0.4)))
    res_dir[lbl] = dict(z=float(zz[i]), dA=float(dd[i]))
out['D18_at_z0p4'] = res_dir
sp_ = [v['dA'] for v in res_dir.values()]
out['D18_dA_spread_percent'] = float(100 * (max(sp_) - min(sp_)) / np.mean(sp_))
zz_ = [v['z'] for v in res_dir.values()]
out['D18_z_spread_at_fixed_step_percent'] = float(
    100 * (max(zz_) - min(zz_)) / np.mean(zz_))

# screen-basis health after the F1 fix: k.E_A must stay ~0 along the ray
E, nh_, sc4_, J, dJ, Hv, sig, rho, lna, tt = _unpack(yF)
kf = np.concatenate([[E], E * nh_])
out['D15_screen_null_orthogonality_final'] = float(
    max(abs(kf @ ETA @ sc4_[0]), abs(kf @ ETA @ sc4_[1])))

print(json.dumps(out, indent=2, default=str))
json.dump(out, open('d_optical.json', 'w'), indent=2, default=str)
