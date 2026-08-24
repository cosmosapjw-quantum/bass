"""Part B: metric, orthonormal frame, and numerical frame data at t0=0.2."""
import numpy as np
import jax.numpy as jnp
from common import (A0, N2, N3, T0, X0, X0ALT, Theta_base, make_gfun, frame_data,
                    bvec, bdot, struct_consts_3d, maxabs, metricity_residual)

print("=" * 78)
print("PART B: frame data at t0 = %.3g  (base frame ehat_a = e_a / b_a)" % T0)
print("=" * 78)

fd = frame_data(Theta_base, X0)
fd2 = frame_data(Theta_base, X0ALT)

b, bd = bvec(X0[0]), bdot(X0[0])
H_an = jnp.sum(bd / b) / 3.0
sig_an = jnp.diag(bd / b) - H_an * jnp.eye(3)
ahat_an = jnp.array([-A0 / b[0], 0.0, 0.0])
nhat_an = jnp.diag(jnp.array([0.0, N3 * b[1] / (b[0] * b[2]), N2 * b[2] / (b[0] * b[1])]))

print("b(t0)     = ", np.asarray(b))
print("H         = % .12f    (analytic % .12f, diff %.2e)"
      % (fd['H'], H_an, abs(float(fd['H'] - H_an))))
print("sigma     =\n", np.array2string(np.asarray(fd['sig']), precision=12))
print("R         = ", np.array2string(np.asarray(fd['R']), precision=3),
      "   |R| = %.3e" % maxabs(fd['R']))
print("=> found: sigma DIAGONAL (max off-diag %.3e), R = 0 (to %.3e), as expected for"
      % (maxabs(fd['sig'] - jnp.diag(jnp.diag(fd['sig']))), maxabs(fd['R'])))
print("   the diagonal ansatz; the Omega/R terms of the claims are NOT exercised here")
print("   (they are exercised in the supplementary rotated-frame run, part E).")

print("\nframe spatial structure data (used in all claim formulas):")
print("ahat      = ", np.array2string(np.asarray(fd['ahat']), precision=12))
print("nhat      =\n", np.array2string(np.asarray(fd['nhat']), precision=12))

res_tbl = {
    'e0-component of [e0,ea]': fd['checks']['e0-component of [e0,ea]'],
    'e0-component of [ea,eb]': fd['checks']['e0-component of [ea,eb]'],
    'reconstruction C(nhat,ahat) - Chat': fd['checks']['C(nhat,ahat) - Chat'],
    'nhat @ ahat': fd['checks']['nhat @ ahat'],
    'H vs analytic bdot/b': abs(float(fd['H'] - H_an)),
    'sigma vs analytic diag(bdot/b)-H': maxabs(fd['sig'] - sig_an),
    '|R| (expected 0)': maxabs(fd['R']),
    'ahat vs analytic (-A0/b1,0,0)': maxabs(fd['ahat'] - ahat_an),
    'nhat vs analytic diag(0,n3 b2/(b1 b3), n2 b3/(b1 b2))': maxabs(fd['nhat'] - nhat_an),
    'position independence of (H,sig,R)': max(maxabs(fd['K'] - fd2['K']), 0.0),
    'position independence of (nhat,ahat)': max(maxabs(fd['nhat'] - fd2['nhat']),
                                                maxabs(fd['ahat'] - fd2['ahat'])),
}

# frame Chat vs constant C scaled by b-factors: Chat^c_ab = C^c_ab b_c/(b_a b_b)
C3 = struct_consts_3d(X0[1:])
scale = b[:, None, None] / (b[None, :, None] * b[None, None, :])
res_tbl['Chat vs C^c_ab b_c/(b_a b_b)'] = maxabs(fd['Chat'] - C3 * scale)

res_tbl['metricity nabla g = 0 (Christoffel check)'] = metricity_residual(
    make_gfun(Theta_base), X0)

print("\nresidual table (part B):")
for k, v in res_tbl.items():
    print("  %-55s %.3e" % (k, v))

ok = all(v < 1e-10 for v in res_tbl.values())
print("\nPART B VERDICT: %s" % ("PASS" if ok else "FAIL"))
