# PHYS-MATH-CODE audit — BASS-8B.2B.1

## Equation-to-code map

| Contract | Code |
|---|---|
| frozen authority hashes and constants | `RateDualAuthority` |
| typed Hubble-time input | `NormalHubbleRateJet` |
| paired inverse-aberrated nodes and tangent | `_paired_direction_jet` |
| `alpha`, `D_i`, `nu_i` and jets | `bind_direction_dependent_rate_dual` |
| full generator `(alpha gamma) C_q` | `RateDualBinding.apply_full_generator` |
| full paired left invariant | `RateDualBinding.left_functional` |
| normalized moving projector | `RateDualBinding.project` |
| exact vacuum quotient | `CollisionOffRateDualBinding` |
| hostile rate/dual mutations | `rate_mutations`, `apply_mutated_generator` |

## Frozen inputs

```text
E2 electron-rate owner
27fe46756023380078fc503e8fe2ea5e976504314e206f55613d06af61f4be1a

BASS-8B.2A state-jet source
31ff41590b3083c825a1faa7efd04bfa168d0a9ae6add08ba3f6c5c1a444db62

BASS-8B.2B.0 carrier source
0a46342eefce177c4bd1a41fd24bb95ea2bf964f2efdc06eb7836940eef3530f
```

The source fails closed if any frozen owner identity differs.

## TDD and local verification

- Twelve recorded RED/GREEN increments.
- Final focused suite: `17/17 PASS`.
- Exact SymPy witness: PASS.
- Stateless Wolfram witness: PASS.
- Randomized audit: 500 generic-vector cases through `|beta|<=0.75`.
- Source/input arrays in the bound receipt are detached and read-only.
- Receipt metadata retains coordinate, binding, schedule, Hubble provenance,
  raw density/H inputs, derivative side, and all non-promotion flags.

## Numerical adversarial results

```text
max node-unit residual                 2.220446049250313e-16
max direct E2-rate residual            2.220446049250313e-16
max rate-log-derivative residual       1.1102230246251565e-16
max correct left-null relative defect  3.4371302506130754e-17
max randomized SO(3) residual          4.939779000334593e-15
max global-scalar projector residual   0
```

Hostile mutations:

- omit direction factor: detected 500/500;
- double Doppler: detected 500/500;
- unchanged left: detected 500/500;
- omit gamma: detected 499/499 cases where `gamma-1>1e-8`; it is intentionally
  indistinguishable at the zero-tilt limit.

## Code risks

### P1

1. Exact import-and-call parity against the restored E2 owner has not yet run in
   this sandbox.  `host_replay/run_from_repo_checkpoint.sh` is the blocking gate.
2. `H_n,H_dot_n` has typed provenance but no VI0-specific background-owner pin;
   this blocks row promotion, not the local rate algebra.

### P2

1. The rank-9 storage remains a redundant embedding of the 4N physical screen
   carrier; 2B.0 owns that restriction.
2. Complete derivatives of weights, screen maps, equilibrium carrier, left dual,
   and projector are deferred to 2B.2.
3. No JAX/Rust/production runtime is wired.

### P3

- Numerical sweeps do not establish a continuum or near-luminal theorem.

## Verdict

```text
LOCAL_CANDIDATE_GREEN__EXACT_E2_HOST_PARITY_REQUIRED
```

## Pure-Python frontend / Rust backend correction

The first local exact-E2 parity attempt failed before parity collection because
`run_exact_e2_host_parity.sh` explicitly imported `jax`.  The restored legacy
`bianchi/__init__.py` also forces JAX x64 at package import time.  Neither is a
physical dependency of the frozen E2 rate owner; the E2 predecessor test itself
contains a focused no-optional-stack loader for this reason.

The bounded correction is verification-only:

- remove JAX from the parity smoke-import contract;
- do not put the legacy authority root on `PYTHONPATH`;
- load exact `electron.py` and `electron_rate.py` through
  `host_replay/pure_python_e2_loader.py`;
- execute no `bianchi`, `bianchi.q`, or `bianchi.thermo` initializer;
- reject attempted imports of JAX/JAXlib/Equinox/Diffrax;
- preserve exact E2 owner hashes and predecessor tests;
- keep unrelated collision/Rust seams fail-closed.

Synthetic RED/GREEN coverage proves that package initializers which raise on
execution are bypassed and that missing owner files or contaminated import
state fail closed.  The exact restored-E2 parity marker remains required before
bounded authority promotion.
