"""Part D: CLAIM 2 (Maxwell curl sign) -- THE discriminator, base frame."""
import numpy as np
import jax.numpy as jnp
from jax import jacfwd
from common import (X0, Theta_base, frame_data, make_Ffun, divF, dF_comps,
                    Edot_solved, Bdot_solved, claim2_candidates, crossm, maxabs,
                    bvec, A0)

print("=" * 78)
print("PART D: CLAIM 2 -- source-free Maxwell in the orthonormal frame [base frame]")
print("  Edot_a = -2H E_a + sig_ab E^b + (RxE)_a - (n_ab B^b +- eps_abc a^b B^c)")
print("  Bdot_a = -2H B_a + sig_ab B^b + (RxB)_a + (n_ab E^b +- eps_abc a^b E^c)")
print("  NEW claim: relative sign +  |  OLD code: relative sign -")
print("=" * 78)

t0 = float(X0[0])
E0v = jnp.array([0.3 + 0.1 * t0, -0.2, 0.15 * t0])     # example fields at t0
B0v = jnp.array([0.1, 0.25 - 0.1 * t0, -0.3])
print("E(t0) =", np.asarray(E0v), "  B(t0) =", np.asarray(B0v))

fd = frame_data(Theta_base, X0)
AE, curl_new, curl_old = claim2_candidates(fd)

# ---- solve nu=spatial div F = 0 for Edot, and (dF)_{0ij}=0 for Bdot
Ed_max, ME, resE = Edot_solved(Theta_base, X0, E0v, B0v)
Bd_max, MB, resB = Bdot_solved(Theta_base, X0, E0v, B0v)
print("\nlinear solves: cond(M_E)=%.2f, cond(M_B)=%.2f; back-substituted residuals %.1e / %.1e"
      % (np.linalg.cond(np.asarray(ME)), np.linalg.cond(np.asarray(MB)), resE, resB))

Ed_new = AE @ E0v - curl_new @ B0v
Ed_old = AE @ E0v - curl_old @ B0v
Bd_new = AE @ B0v + curl_new @ E0v
Bd_old = AE @ B0v + curl_old @ E0v

print("\nEdot from Maxwell (solved) :", np.array2string(np.asarray(Ed_max), precision=12))
print("Edot candidate NEW  (+eps) :", np.array2string(np.asarray(Ed_new), precision=12))
print("Edot candidate OLD  (-eps) :", np.array2string(np.asarray(Ed_old), precision=12))
print("Bdot from Maxwell (solved) :", np.array2string(np.asarray(Bd_max), precision=12))
print("Bdot candidate NEW  (+eps) :", np.array2string(np.asarray(Bd_new), precision=12))
print("Bdot candidate OLD  (-eps) :", np.array2string(np.asarray(Bd_old), precision=12))

sampres = {
    'Edot: NEW (+eps)': maxabs(Ed_max - Ed_new),
    'Edot: OLD (-eps)': maxabs(Ed_max - Ed_old),
    'Bdot: NEW (+eps)': maxabs(Bd_max - Bd_new),
    'Bdot: OLD (-eps)': maxabs(Bd_max - Bd_old),
}
print("\nsample residual table (max-abs over 3 components):")
for k, v in sampres.items():
    print("  %-18s %.3e" % (k, v))

# ---- full linear maps (Edot = LEE E + LEB B, Bdot = LBB B + LBE E) via jacfwd
fE = lambda E, B: Edot_solved(Theta_base, X0, E, B)[0]
fB = lambda E, B: Bdot_solved(Theta_base, X0, E, B)[0]
LEE = jacfwd(fE, 0)(E0v, B0v); LEB = jacfwd(fE, 1)(E0v, B0v)
LBE = jacfwd(fB, 0)(E0v, B0v); LBB = jacfwd(fB, 1)(E0v, B0v)

# linearity spot-check (affine with zero offset)
lin = max(maxabs(fE(2.0 * E0v, 0.5 * B0v) - (LEE @ (2.0 * E0v) + LEB @ (0.5 * B0v))),
          maxabs(fB(-1.3 * E0v, 0.7 * B0v) - (LBE @ (-1.3 * E0v) + LBB @ (0.7 * B0v))))
print("\nlinearity of solved (Edot,Bdot) in (E,B): %.3e" % lin)

matres = {
    'LEE vs (-2H I + sig + Rx)': maxabs(LEE - AE),
    'LBB vs (-2H I + sig + Rx)': maxabs(LBB - AE),
    'LEB vs -curl_NEW': maxabs(LEB + curl_new),
    'LEB vs -curl_OLD': maxabs(LEB + curl_old),
    'LBE vs +curl_NEW': maxabs(LBE - curl_new),
    'LBE vs +curl_OLD': maxabs(LBE - curl_old),
}
print("\nmatrix-level residual table (max-abs entry):")
for k, v in matres.items():
    print("  %-28s %.3e" % (k, v))
print("\nextracted curl matrix  -LEB (should equal curl):")
print(np.array2string(np.asarray(-LEB), precision=12))
print("curl_NEW = nhat + [ahat x]:")
print(np.array2string(np.asarray(curl_new), precision=12))
print("curl_OLD = nhat - [ahat x]:")
print(np.array2string(np.asarray(curl_old), precision=12))
print("duality check |(-LEB) - (LBE)| = %.3e  (same curl operator in both equations)"
      % maxabs(-LEB - LBE))

# ---- Gauss laws: nu=0 divergence component and purely spatial dF component
def D0_fun(E, B, Ed, Bd):
    F = make_Ffun(Theta_base, E, B, Ed, Bd, t0=X0[0])
    return divF(Theta_base, F, X0)[0]

def dF123_fun(E, B, Ed, Bd):
    F = make_Ffun(Theta_base, E, B, Ed, Bd, t0=X0[0])
    return dF_comps(F, X0, [(1, 2, 3)])[0]

Edv = jnp.array([0.1, 0.0, 0.15]); Bdv = jnp.array([0.0, -0.1, 0.0])
args = (E0v, B0v, Edv, Bdv)
g0 = [jacfwd(D0_fun, i)(*args) for i in range(4)]
g3 = [jacfwd(dF123_fun, i)(*args) for i in range(4)]
ah = fd['ahat']; b = bvec(X0[0])
s3 = float(b[0] * b[1] * b[2] * jnp.exp(2.0 * A0 * X0[1]))   # theta^1^theta^2^theta^3 coeff

cE = float(g0[0] @ ah / (ah @ ah))
cB = float(g3[1] @ ah / (ah @ ah))
gauss = {
    'D^0 grad wrt E ortho to ahat |gE - cE*ahat|': maxabs(g0[0] - cE * ah),
    'D^0 grad wrt B': maxabs(g0[1]),
    'D^0 grad wrt Edot': maxabs(g0[2]),
    'D^0 grad wrt Bdot': maxabs(g0[3]),
    '(dF)_123 grad wrt B ortho to ahat |gB - cB*ahat|': maxabs(g3[1] - cB * ah),
    '(dF)_123 grad wrt E': maxabs(g3[0]),
    '(dF)_123 grad wrt Edot': maxabs(g3[2]),
    '(dF)_123 grad wrt Bdot': maxabs(g3[3]),
}
print("\nGauss-law structure (gradients of the two constraint components):")
for k, v in gauss.items():
    print("  %-48s %.3e" % (k, v))
print("  D^0      = cE * (ahat.E) with cE = %+.12f  (compare +2: diff %.1e)"
      % (cE, abs(cE - 2.0)))
print("  (dF)_123 = cB * (ahat.B) with cB = %+.12f ;  cB / (vol factor s3=%.6f) = %+.12f"
      % (cB, s3, cB / s3), " (compare -2: diff %.1e)" % abs(cB / s3 + 2.0))
print("  => both constraints are scalar multiples of ahat.E and ahat.B resp.;")
print("     claimed Gauss laws a.E = 0, a.B = 0 confirmed up to nonzero multiples.")

# constrained configuration: ahat.E = ahat.B = 0 (E1=B1=0) must satisfy both exactly
Ec = jnp.array([0.0, 0.4, -0.25]); Bc = jnp.array([0.0, 0.3, 0.55])
print("  constrained config (a.E=a.B=0): |D^0| = %.3e, |(dF)_123| = %.3e"
      % (abs(float(D0_fun(Ec, Bc, Edv, Bdv))), abs(float(dF123_fun(Ec, Bc, Edv, Bdv)))))

# ---- robustness: repeat the discriminating solve at a second spatial point
from common import X0ALT
Ed2, _, _ = Edot_solved(Theta_base, X0ALT, E0v, B0v)
Bd2, _, _ = Bdot_solved(Theta_base, X0ALT, E0v, B0v)
print("\nsecond spatial point X0ALT: |Edot_max(X0ALT) - NEW| = %.3e, |Bdot - NEW| = %.3e"
      % (maxabs(Ed2 - Ed_new), maxabs(Bd2 - Bd_new)))

# ---- verdict
new_worst = max(sampres['Edot: NEW (+eps)'], sampres['Bdot: NEW (+eps)'],
                matres['LEB vs -curl_NEW'], matres['LBE vs +curl_NEW'])
old_best = min(sampres['Edot: OLD (-eps)'], sampres['Bdot: OLD (-eps)'],
               matres['LEB vs -curl_OLD'], matres['LBE vs +curl_OLD'])
print("\nSIGN VERDICT: NEW(+eps) worst residual %.3e ; OLD(-eps) best residual %.3e" %
      (new_worst, old_best))
if new_worst < 1e-9 and old_best > 1e-2:
    print("PART D VERDICT: NEW claim (+eps_abc a^b X^c) CONFIRMED; OLD (-eps) REFUTED.")
elif old_best < 1e-9 and new_worst > 1e-2:
    print("PART D VERDICT: OLD sign (-eps) confirmed; NEW claim REFUTED.")
else:
    print("PART D VERDICT: AMBIGUOUS -- investigate.")
