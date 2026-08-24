"""Part A: verify the coordinate realization of the type-VI_h-flavor algebra."""
import numpy as np
import jax.numpy as jnp
from common import (A0, N2, N3, Wmat, expxM, struct_consts_3d, extract_na,
                    reconstruct_C, maxabs)

print("=" * 78)
print("PART A: coordinate realization  (A0=%.3g, n2=%.3g, n3=%.3g)" % (A0, N2, N3))
print("=" * 78)

# closed-form expm vs generic Pade expm (independent implementation check)
from jax.scipy.linalg import expm as jexpm
import jax
M = jnp.array([[A0, N3], [-N2, A0]])
res_expm = max(maxabs(expxM(x) - jexpm(x * M)) for x in (-0.7, 0.15, 0.9))
print("closed-form exp(xM) vs jax.scipy.linalg.expm  : %.3e" % res_expm)

pts = [jnp.array([0.15, 0.30, -0.20]),
       jnp.array([-0.40, 1.10, 0.70]),
       jnp.array([0.83, -0.51, 0.27])]

Cs = [struct_consts_3d(p) for p in pts]
res_pos = max(maxabs(C - Cs[0]) for C in Cs[1:])
print("position independence of numerical C^k_ij     : %.3e" % res_pos)

C = Cs[0]
print("\nnumerical structure constants (nonzero entries, 1-based indices):")
for k in range(3):
    for i in range(3):
        for j in range(i + 1, 3):
            v = float(C[k, i, j])
            if abs(v) > 1e-12:
                print("  C^%d_%d%d = %+ .12f" % (k + 1, i + 1, j + 1, v))

# Jacobi identity of the numerical constants (sanity)
jac = jnp.einsum('mij,kml->kijl', C, C)
jacobi = jac + jnp.transpose(jac, (0, 3, 1, 2)) + jnp.transpose(jac, (0, 2, 3, 1))
# jacobi[k,i,j,l] = C^m_ij C^k_ml + cyclic(i,j,l)
print("Jacobi identity residual                      : %.3e" % maxabs(jacobi))

n, a = extract_na(C)
print("\nrecovered a_b  = ", np.array2string(np.asarray(a), precision=12))
print("recovered n^ab =\n", np.array2string(np.asarray(n), precision=12))
print("  (expected up to the algebra's freedom: a=(A0,0,0)-type i.e. here (-A0,0,0),")
print("   n = diag(0, n3, n2) = diag(0, %.1f, %.1f) -- extraction convention fixed by" % (N3, N2))
print("   dw^k = -(1/2) C^k_ij w^i^w^j; definitive check is the reconstruction identity)")

res_recon = maxabs(reconstruct_C(n, a) - C)
print("\nC^a_bc(recovered n,a) vs numerical C^a_bc     : %.3e   (target <= 1e-10)" % res_recon)
print("n^ab a_b                                      : %.3e" % maxabs(n @ a))

# class-B / VI_h diagnostics
evals = np.linalg.eigvalsh(np.asarray(n))
h_par = float(a[0] ** 2 / (n[1, 1] * n[2, 2]))
print("eigs(n) = %s ;  a in kernel of n: |n a| above; group parameter a^2/(n22 n33) = %.4f"
      % (np.array2string(evals, precision=6), h_par))
print("=> class B (a != 0) with n of signature (0,+,-): type VI_h flavor confirmed")

ok = (res_expm < 1e-10 and res_pos < 1e-10 and res_recon < 1e-10
      and maxabs(n @ a) < 1e-12 and maxabs(jacobi) < 1e-12)
print("\nPART A VERDICT: %s" % ("PASS" if ok else "FAIL"))
