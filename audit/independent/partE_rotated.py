"""Part E (supplementary): time-rotated orthonormal frame => R != 0.
Exercises the Omega^a_b term of CLAIM 1 and the (RxE),(RxB) terms of CLAIM 2,
which are inert in the diagonal base frame. Same metric, frame ehat'_a = Lam(t)_ab ehat_b.
"""
import numpy as np
import jax.numpy as jnp
from jax import jacfwd
from common import (X0, Theta_base, Theta_rot, make_gfun, frame_data, claim1_test,
                    Edot_solved, Bdot_solved, claim2_candidates, Pquad, maxabs)

print("=" * 78)
print("PART E (supplementary): rotated frame -- activates R/Omega terms")
print("=" * 78)

g1 = make_gfun(Theta_base)(X0); g2 = make_gfun(Theta_rot)(X0)
print("same metric from both frames: |g_rot - g_base| = %.3e" % maxabs(g1 - g2))

fd = frame_data(Theta_rot, X0)
print("R' = ", np.array2string(np.asarray(fd['R']), precision=8),
      "  |R'| = %.4f  (nonzero as intended)" % maxabs(fd['R']))
print("frame-data consistency checks:", {k: "%.1e" % v for k, v in fd['checks'].items()})
print("nhat' non-diagonal now: max off-diag = %.4f ; ahat' = %s"
      % (maxabs(fd['nhat'] - jnp.diag(jnp.diag(fd['nhat']))),
         np.array2string(np.asarray(fd['ahat']), precision=6)))

# ---------------- CLAIM 1 in the rotated frame
rng = np.random.default_rng(20260729 + 1)
dirs = []
for _ in range(3):
    v = rng.normal(size=3)
    dirs.append(jnp.asarray(v / np.linalg.norm(v)))

hs = (1e-6, 5e-7)
print("\nCLAIM 1 residuals in rotated frame (Omega term ACTIVE):")
print("%-34s %12s %12s %12s %14s" % ("direction", "exact(jvp)", "FD h=1e-6",
                                     "Richardson", "dE/dt-eq only"))
worst_exact, worst_E = 0.0, 0.0
rows_lhs, rows_omp = [], []
for d in dirs:
    r = claim1_test(Theta_rot, X0, d, E0=1.0, hs=hs)
    resE_only = abs(float(r['exact'][0] - r['claim'][0]))
    print("%-34s %12.3e %12.3e %12.3e %14.3e" %
          (np.array2string(np.asarray(d), precision=4, suppress_small=True),
           r['res_exact'], r['res_fd'][hs[0]], r['res_rich'], resE_only))
    worst_exact = max(worst_exact, r['res_exact'])
    worst_E = max(worst_E, resE_only)
    # Omega-sign fit: dP/dt + (H I + sig) P + E*Pq = c * (Om @ P); claim => c = +1
    pf0 = r['pf0']; P0 = pf0[1:]
    lhs = (r['exact'][1:] + (fd['H'] * jnp.eye(3) + fd['sig']) @ P0
           + pf0[0] * Pquad(d, fd['nhat'], fd['ahat']))
    rows_lhs.append(np.asarray(lhs)); rows_omp.append(np.asarray(fd['Om'] @ P0))
L = np.concatenate(rows_lhs); Wv = np.concatenate(rows_omp)
c_fit = float(L @ Wv / (Wv @ Wv))
print("Omega-coefficient fit over 9 components: c = %+.12f (claim -(H+sig-Om)P => c=+1);"
      % c_fit)
print("  fit residual |lhs - c*(Om P)| = %.3e, |Om P| scale = %.3f"
      % (float(np.max(np.abs(L - c_fit * Wv))), float(np.max(np.abs(Wv)))))
wrong_om = 0.0
for d in dirs:  # residual if the Omega sign were flipped: -(H+sig+Om)P
    r = claim1_test(Theta_rot, X0, d, E0=1.0, hs=hs)
    alt = r['claim'][1:] - 2.0 * (fd['Om'] @ r['pf0'][1:])
    wrong_om = max(wrong_om, maxabs(r['exact'][1:] - alt))
print("  residual with flipped Omega sign (-(H+sig+Om)P): %.3e  (O(1) => sign fixed)"
      % wrong_om)

# ---------------- CLAIM 2 in the rotated frame
t0 = float(X0[0])
E0v = jnp.array([0.3 + 0.1 * t0, -0.2, 0.15 * t0])
B0v = jnp.array([0.1, 0.25 - 0.1 * t0, -0.3])
AE, curl_new, curl_old = claim2_candidates(fd)   # AE includes +crossm(R') now

fE = lambda E, B: Edot_solved(Theta_rot, X0, E, B)[0]
fB = lambda E, B: Bdot_solved(Theta_rot, X0, E, B)[0]
LEE = jacfwd(fE, 0)(E0v, B0v); LEB = jacfwd(fE, 1)(E0v, B0v)
LBE = jacfwd(fB, 0)(E0v, B0v); LBB = jacfwd(fB, 1)(E0v, B0v)

matres = {
    'LEE vs (-2H I + sig + R\'x)': maxabs(LEE - AE),
    'LBB vs (-2H I + sig + R\'x)': maxabs(LBB - AE),
    'LEB vs -curl_NEW': maxabs(LEB + curl_new),
    'LEB vs -curl_OLD': maxabs(LEB + curl_old),
    'LBE vs +curl_NEW': maxabs(LBE - curl_new),
    'LBE vs +curl_OLD': maxabs(LBE - curl_old),
}
print("\nCLAIM 2 matrix residuals, rotated frame (R x terms ACTIVE in LEE/LBB):")
for k, v in matres.items():
    print("  %-28s %.3e" % (k, v))
# flipped-R diagnostic
from common import crossm
AE_wrong = AE - 2.0 * crossm(fd['R'])
print("  LEE vs AE with flipped R sign: %.3e  (O(1) => (RxE) sign fixed)"
      % maxabs(LEE - AE_wrong))

claim2_ok = (matres['LEE vs (-2H I + sig + R\'x)'] < 1e-9
             and matres['LBB vs (-2H I + sig + R\'x)'] < 1e-9
             and matres['LEB vs -curl_NEW'] < 1e-9 and matres['LBE vs +curl_NEW'] < 1e-9
             and matres['LEB vs -curl_OLD'] > 1e-2 and matres['LBE vs +curl_OLD'] > 1e-2)
claim1_stated_fails = worst_exact > 1e-2
claim1_flipped_ok = (abs(c_fit + 1.0) < 1e-9 and wrong_om < 1e-9 and worst_E < 1e-9)
print("\nPART E FINDINGS:")
print("  dE/dt equation (no Omega): still exact, worst residual %.3e" % worst_E)
print("  CLAIM 2 incl. (RxE),(RxB) with R'!=0: %s"
      % ("CONFIRMED (NEW +eps also reconfirmed, OLD refuted)" if claim2_ok else "PROBLEM"))
if claim1_stated_fails and claim1_flipped_ok:
    print("  CLAIM 1 dP/dt AS STATED (-(H d + sig - Om)P): REFUTED when Omega != 0,")
    print("    residual O(1) = %.3f; Omega-coefficient fit c = %+.12f (claim: +1)." %
          (worst_exact, c_fit))
    print("    CORRECTED equation dP^a/dt = -(H d + sig + Om)^a_b P^b - E P^a(nhat)")
    print("    [equivalently +(R x P)_a, matching the master rule and the CLAIM-2 (RxX)")
    print("    terms] holds to %.3e." % wrong_om)
else:
    print("  CLAIM 1 with Omega active: worst %.3e, c_fit %+.6f" % (worst_exact, c_fit))

# --- NET verdict (added when ported into the repo, v1.4): partE PASSES iff it
#     (a) confirms the Maxwell R-terms and +eps curl sign, and (b) confirms the
#     CORRECTED transport sign +(R x P) = +Omega (which report v1.3 now states).
#     The refutation of the *stale* -Omega form is a confirmation of the fix, not a
#     failure of the independent check.
_netpass = claim2_ok and claim1_flipped_ok and (wrong_om < 1e-9)
print("\nPART E VERDICT: %s  (Maxwell R-terms + +eps confirmed; transport corrected"
      " to +(R x P) and confirmed to %.1e)" % ("PASS" if _netpass else "FAIL", wrong_om))
import sys as _sys
_sys.exit(0 if _netpass else 1)
