# BASS REC Source R10 — Certified Scalar Projection Parity GREEN Candidate

## Purpose

R9's exact test-first failure has been observed. R10 supplies the smallest production surface required by that contract: `bianchi/source_parity.py`.

The module certifies a finite-rank scalar real-spherical-harmonic projection and compares the already-qualified R8 full-grid and coefficient source actions under one immutable source, one physical parent, one projection contract, and one independent-variable basis.

## Exact production delta

```text
R9 closeout parent
06693571d98013610bc01565a1f4988bdc673094

R10 source commit
308507f2289b4cd6aabf0d7762e6e12766feb627

tree
a27ff7c010b76cfc42ad0f2ac62049689cbb816a

production delta
A  bianchi/source_parity.py

source blob
a807191ff0baa6851ec7748826a7d4e34b400207
```

No backend, native core, solver loop, dependency lock, source-authority, or R8 adapter file changes in the production commit.

## Bounded mathematical contract

The source remains

```text
C_t[f] = eta*(1+f)-kappa*f = eta-(kappa-eta)*f.
```

The scalar basis is real, orthonormal on `dOmega`, and inherited from complex Condon–Shortley harmonics:

```text
Z_l0     = Y_l0
Z_lm_cos = sqrt(2) Re Y_lm
Z_lm_sin = sqrt(2) Im Y_lm
```

The coefficient order is explicit and the constant unit field has monopole coefficient `sqrt(4*pi)`. The generated tensor-product quadrature uses

```text
N_mu  = L_work+1      Gauss-Legendre
N_phi = 2*L_work+1    uniform periodic azimuth
```

and hashes the actual nodes, weights, mode order, normalization, and unit-field coefficients.

## Local gate

Run:

```bash
bash scripts/research/run_bass_rec_source_r10_green_local.sh
```

Required classification:

```text
PASS_BASS_REC_SOURCE_R10_CERTIFIED_SCALAR_PROJECTION_PARITY_GREEN
focused_49_rc=0
deterministic_parity_receipts=true
adversarial_probe_rc=0
formal_fallback_rc=0
plot_audit_pass=true
clean_worktree=true
```

The runner also creates rank-resolved source residual, Gram defect, and Gram-condition diagnostics and tries SymPy, mpmath, GNU Octave, SageMath, Singular, and Lean/mathlib with bounded timeouts. Optional tools are recorded as unavailable rather than fabricated as passes.

## Claim boundary

Even after a local PASS, the admitted claim is only finite-rank scalar parity for an angularly constant photon/boson source in this certified real-harmonic convention. R10 does not establish transport-time parity, anisotropic source products, project-spin/PSTF production-layout parity, polarized sources, radial/integrated closure, physical REC donor wiring, solver-loop integration, physical faces, provider readiness, likelihood readiness, `PASS_REC_PHYSICAL_SPLIT`, or `PASS_RF04`.
