"""Part C: CLAIM 1 (photon geodesic transport) vs exact coordinate geodesics."""
import numpy as np
import jax.numpy as jnp
from common import X0, Theta_base, claim1_test, frame_data, maxabs

print("=" * 78)
print("PART C: CLAIM 1 -- dE/dt = -E(H + sig_ab n^a n^b),")
print("        dP^a/dt = -(H d + sig - Om)^a_b P^b - E * P^a(nhat)   [base frame]")
print("=" * 78)

rng = np.random.default_rng(20260729)
dirs = []
for _ in range(3):
    v = rng.normal(size=3)
    dirs.append(jnp.asarray(v / np.linalg.norm(v)))

fd = frame_data(Theta_base, X0)
print("frame data at X0: H=%.6f, |R|=%.2e (Omega term inert here)" %
      (fd['H'], maxabs(fd['R'])))

hs = (1e-6, 5e-7)
worst = {'exact': 0.0, hs[0]: 0.0, hs[1]: 0.0, 'rich': 0.0}
print("\nper-direction residuals  |numeric d(E,P)/dt - CLAIM1|  (max over 4 components):")
print("%-34s %10s %12s %12s %12s %12s" %
      ("direction nhat", "|g(p,p)|", "exact(jvp)", "FD h=1e-6", "FD h=5e-7", "Richardson"))
for d in dirs:
    r = claim1_test(Theta_base, X0, d, E0=1.0, hs=hs)
    print("%-34s %10.1e %12.3e %12.3e %12.3e %12.3e" %
          (np.array2string(np.asarray(d), precision=4, suppress_small=True),
           abs(r['null']), r['res_exact'], r['res_fd'][hs[0]], r['res_fd'][hs[1]],
           r['res_rich']))
    worst['exact'] = max(worst['exact'], r['res_exact'])
    worst[hs[0]] = max(worst[hs[0]], r['res_fd'][hs[0]])
    worst[hs[1]] = max(worst[hs[1]], r['res_fd'][hs[1]])
    worst['rich'] = max(worst['rich'], r['res_rich'])

# show a full component breakdown for the first direction
r = claim1_test(Theta_base, X0, dirs[0], E0=1.0, hs=hs)
print("\ncomponent breakdown, direction 1  (order: dE/dt, dP^1/dt, dP^2/dt, dP^3/dt):")
print("  numeric exact : ", np.array2string(np.asarray(r['exact']), precision=12))
print("  CLAIM 1       : ", np.array2string(np.asarray(r['claim']), precision=12))
print("  FD(h=1e-6)-exact consistency: %.3e ;  P^a - E nhat^a at start: %.3e"
      % (r['fd_vs_exact'][hs[0]], r['P_vs_Edirn']))

ok = worst['exact'] < 1e-10 and worst['rich'] < 1e-6 and worst[hs[0]] < 1e-6
print("\nworst-case: exact %.3e | FD(1e-6) %.3e | FD(5e-7) %.3e | Richardson %.3e"
      % (worst['exact'], worst[hs[0]], worst[hs[1]], worst['rich']))
print("PART C VERDICT (CLAIM 1, H/sigma/P-quadratic terms; Omega inert): %s"
      % ("PASS" if ok else "FAIL"))
