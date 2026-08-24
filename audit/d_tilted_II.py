"""
Debt B --- completeness of the CS(II) tilt-stability reduction to {v2, v3}.

At the Collins-Stewart type II fixed point (non-tilted, N = diag(N1,0,0), a = 0,
Sigma = diag(-2S+, S+, S+), S+ = (3g-2)/8), the LINEARISED tilt evolution decouples
from the geometry at first order (P_a is quadratic in v, so dP = 0):

    dv_a/dtau = [(3g-4) delta_ab - Sigma_ab] dv_b   (R = 0, a = 0 here)

giving three eigenvalues
    v1:  3g-4 + 2S+ = 3(5g-6)/4     (crosses 0 at g = 6/5)
    v2:  3g-4 -  S+ = 3(7g-10)/8    (crosses 0 at g = 10/7)
    v3:  same as v2.

Naively v1 destabilises FIRST (6/5 < 10/7).  BUT v1 is FORBIDDEN by the momentum
constraint: for type II the geometric momentum in direction 1 vanishes identically
(G_{01} = eps_{1bc} n_{bd} sigma_c^d = 0 because n = diag(N1,0,0)), so Codazzi reads
    C_1 = G_{01} + q_1 = q_1 = g Omega v_1 = 0   =>   v_1 = 0.
Hence v1 is not tangent to the constraint surface; the physical tilt sink threshold is
10/7 from the {v2, v3} doublet.  This script proves all of that numerically.
"""
import numpy as np, json
import jax
import jax.numpy as jnp
from jax import config
config.update("jax_enable_x64", True)

from bianchi.matter.fluid import TiltedFluid, dv_general, sources
from bianchi.conventions import codazzi_residual, SQRT3

out = {}


def cs_state(g):
    Sp = (3 * g - 2) / 8.0
    Om = 9.0 / 8.0 - 3.0 * g / 16.0
    N1 = np.sqrt(max(9.0 * (2 - g) * (3 * g - 2) / 16.0, 0.0))
    Sigma = np.diag([-2 * Sp, Sp, Sp])
    N = np.diag([N1, 0.0, 0.0])
    A = np.zeros(3)
    return Sigma, N, A, Om, Sp, N1


# ---- (1) unconstrained tilt Jacobian eigenvalues vs g -----------------------
def tilt_jacobian(g):
    Sigma, N, A, Om, Sp, N1 = cs_state(g)

    def f(v):
        fl = TiltedFluid.of(g, Om, v)
        src = sources(fl, jnp.asarray(Sigma), jnp.asarray(A))
        return dv_general(fl, src, jnp.asarray(Sigma), jnp.asarray(N),
                          jnp.asarray(A), jnp.zeros(3))

    return np.asarray(jax.jacfwd(f)(jnp.zeros(3)))


rows = {}
for g in (0.9, 1.1, 6 / 5, 1.3, 10 / 7, 1.5, 1.8):
    J = tilt_jacobian(g)
    ev = np.sort(np.linalg.eigvals(J).real)
    rows[f"g={g:.4f}"] = dict(
        eig=np.round(ev, 8).tolist(),
        v1_pred=round(3 * (5 * g - 6) / 4, 8),
        v23_pred=round(3 * (7 * g - 10) / 8, 8))
out['unconstrained_tilt_eigenvalues'] = rows

# check the analytic identification
e_v1 = e_v23 = 0.0
for g in np.linspace(0.7, 1.9, 40):
    J = tilt_jacobian(float(g))
    ev = np.sort(np.linalg.eigvals(J).real)
    # v1 is the isolated eigenvalue, v2=v3 the doublet
    v23 = 3 * (7 * g - 10) / 8
    v1 = 3 * (5 * g - 6) / 4
    preds = np.sort([v1, v23, v23])
    e_v1 = max(e_v1, float(np.abs(ev - preds).max()))
out['tilt_eigenvalues_match_analytic'] = e_v1

# ---- (2) v1 is forbidden by the momentum (Codazzi) constraint ----------------
# C_1 = geometric G_{01} + fluid q_1.  Show d C_1 / d v_1 = g Omega != 0, so v1 is
# transverse to the constraint surface (not a free perturbation direction).
def codazzi_C(g, v):
    """jax-traceable: returns C_a = geometric G_0a - q_flux_a (constraint residual)."""
    Sigma, N, A, Om, Sp, N1 = cs_state(g)
    fl = TiltedFluid.of(g, Om, v)
    src = sources(fl, jnp.asarray(Sigma), jnp.asarray(A))
    return codazzi_residual(jnp.asarray(Sigma), jnp.asarray(N),
                            jnp.asarray(A), src["q_flux"])


g0 = 1.25
Sigma, N, A, Om, Sp, N1 = cs_state(g0)
# geometric momentum of type II in each direction (v=0)
Gmom = np.asarray(codazzi_residual(jnp.asarray(Sigma), jnp.asarray(N),
                                   jnp.asarray(A), None))
out['type_II_geometric_momentum_at_CS'] = np.round(Gmom, 12).tolist()   # all 0
# gradient of C wrt each v-direction at v=0
Jc = np.asarray(jax.jacfwd(lambda v: codazzi_C(g0, v))(jnp.zeros(3)))
out['dCodazzi_dv_at_CS'] = np.round(Jc, 8).tolist()
out['v1_constraint_gradient'] = float(abs(Jc[0, 0]))        # = g Omega, != 0
out['v1_forbidden'] = bool(abs(Jc[0, 0]) > 1e-6)
out['3_gamma_Omega_check'] = float(3 * g0 * Om)             # = |Jc[0,0]| (q_flux = 3 g Omega v/Gp)

# ---- (3) the physical (constraint-tangent) tilt sink threshold is 10/7 -------
# On the constraint surface v1 = 0; the surviving {v2,v3} doublet crosses at 10/7.
def constrained_tilt_max_eig(g):
    J = tilt_jacobian(g)
    # project out v1 (constrained): take the {v2,v3} block
    blk = 0.5 * (J[1:, 1:] + J[1:, 1:].T)
    return float(np.max(np.linalg.eigvalsh(blk)))


out['constrained_threshold_scan'] = {
    f"g={g:.4f}": round(constrained_tilt_max_eig(g), 8)
    for g in (1.3, 10 / 7 - 1e-4, 10 / 7, 10 / 7 + 1e-4, 1.5)}
out['constrained_crosses_at_10_7'] = abs(constrained_tilt_max_eig(10 / 7)) < 1e-9

# ---- (4) geometric (non-tilt) sector is stable for 2/3 < g < 2 ---------------
# linearise the class-A type II geometry at CS(II) in the invariant N2=N3=0 subspace
from bianchi.charts import class_a as ca


def geom_max_eig(g):
    Sp = (3 * g - 2) / 8.0
    N1 = np.sqrt(max(3 * (2 - 4 * Sp) * Sp, 1e-12))
    y0 = jnp.asarray([Sp, 0.0, N1, 0.0, 0.0])

    def rhs_arr(v, gm):
        st = ca.StateA(v[0], v[1], v[2], v[3], v[4])
        d = ca.rhs(0.0, st, {"gamma": gm})
        return jnp.stack([d.Sigma_p, d.Sigma_m, d.N1, d.N2, d.N3])

    # refine fixed point
    v = y0
    for _ in range(50):
        F = rhs_arr(v, g)
        J = jax.jacfwd(lambda w: rhs_arr(w, g))(v)
        v = v - jnp.linalg.lstsq(J, F, rcond=None)[0]
    J = np.asarray(jax.jacfwd(lambda w: rhs_arr(w, g))(v))
    # type II invariant subspace = (Sp, Sm, N1); N2,N3 are type-changing
    sub = np.linalg.eigvals(J[np.ix_([0, 1, 2], [0, 1, 2])])
    return float(np.max(sub.real)), float(np.max(np.abs(rhs_arr(v, g))))


geom = {}
for g in (0.8, 1.0, 1.2, 1.4, 1.6, 1.8):
    me, res = geom_max_eig(g)
    geom[f"g={g:.2f}"] = dict(max_real_eig=round(me, 6), fixed_point_res=round(res, 12))
out['geometric_sector'] = geom
out['geometric_stable_throughout'] = all(v["max_real_eig"] < 1e-6 for v in geom.values())

print(json.dumps(out, indent=2, default=str))
json.dump(out, open('d_tilted_II.json', 'w'), indent=2, default=str)
