# BASS REC Source R9 — finite-rank nonaxisymmetric grid/PSTF parity RED

## Status

R8B passed under the admitted RF-00 payload:

```text
PASS_BASS_REC_SOURCE_R8B_TRUSTED_NATIVE_PARENT_CANDIDATE_NONREGRESSION
parent backend    54/54
candidate backend 54/54
candidate focused 33/33
development override unset
clean worktrees true
```

R9 is test-only. It defines the missing finite-rank nonaxisymmetric grid-to-real-harmonic parity contract. It adds no production parity module, solver wiring, REC atomic source, anisotropic source product, integrated-state closure, polarization source, face, provider, likelihood, or inference path.

## Bounded target

For one band-limited scalar occupation field and one angularly constant photon/boson source,

```text
C[f] = eta*(1+f)-kappa*f = eta-(kappa-eta)*f,
```

the following two routes must agree:

```text
real-harmonic coefficients
  -> synthesize to an explicit angular grid
  -> apply the R8 full-grid source
  -> project back

real-harmonic coefficients
  -> apply the R8 spectral-PSTF/coefficient source directly
```

The regression basis is a declared orthonormal real Condon-Shortley basis on `dOmega`, with canonical mode order

```text
(l,0,m0), (l,1,cos), (l,1,sin), ..., (l,l,cos), (l,l,sin).
```

The constant unit field has coefficient `sqrt(4*pi)` in the `(0,0,m0)` slot.

## Quadrature contract

For work rank `L_work`, the first tensor-product rule uses

```text
N_mu  = L_work + 1       (Gauss-Legendre)
N_phi = 2*L_work + 1     (uniform periodic)
```

and hashes the nodes, weights, azimuths, basis convention, ordering, and rank. For the bounded band-limited parity problem this integrates the projected products through rank `L_work`. Underresolved latitude or azimuth rules must be rejected rather than silently accepted.

## Expected RED

The exact test source commit contains no `bianchi/source_parity.py`. The local runner must observe:

```text
16 tests
14 assertion failures
0 errors
0 skips
2 passing controls
```

The controls preserve exact affine-projector linearity and the already-qualified R8 adapter. Only that exact fingerprint opens the minimal R10 GREEN.
