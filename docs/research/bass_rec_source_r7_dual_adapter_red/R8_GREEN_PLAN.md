# R8 minimal GREEN plan

## Goal

Turn the exact R7 adapter RED into GREEN without wiring any production solver.

## Allowed production change

Create exactly:

```text
bianchi/source_adapters.py
```

The module should remain standard-library-only and should not be imported from
`bianchi.__init__` in this first slice.

## Required API

```text
SourceTimeBasis
  PHYSICAL_TIME
  Q_TIME
  RAY_LENGTH

SourceAdapterError
SourceApplicationReceipt
SourceApplicationResult

require_dual_adapter_target
apply_constant_pair_to_full_spectral_grid
apply_constant_pair_to_spectral_pstf
```

## Required behavior

1. accept only the qualified R6 `SourceAuthorityBundle` with
   `POINTWISE_SPECTRAL`, `photon`, `boson` semantics;
2. preserve the immutable source payload and primary source hash;
3. apply the pointwise affine source to finite scalar sequences;
4. apply the coefficient action
   `eta*unit_field_coefficients-chi_affine*state_coefficients`;
5. require explicit state-parent, representation and projection-contract hashes;
6. keep grid and PSTF representation hashes distinct while permitting one
   shared physical parent-state hash;
7. support physical-time, Q-time and ray-length rates with exactly one typed
   conversion;
8. reject integrated states and insufficient work rank;
9. reject nonfinite inputs and outputs;
10. compute a deterministic output receipt from schema, ordering, binary64
    values and all authority fields.

## First fixture only

The GREEN is limited to an angularly constant source pair. It must not add a
nonconstant source field, Gaunt multiplication, frequency interpolation,
nonlocal kernel, polarization or solver integration.

## Test sequence

```text
1. replay the exact expected R7 RED
2. add bianchi/source_adapters.py
3. run R5+R6 survivors (21 tests)
4. run R7 suite (12 tests)
5. run two-process output-hash identity
6. run adversarial mutations
7. run trusted-payload backend parent/candidate differential
8. verify clean worktrees and non-Git package staging
```

## Completion label

```text
PASS_BASS_REC_SOURCE_R8_CONSTANT_PAIR_DUAL_ADAPTER_GREEN
```

This label means only that the first constant-pair receiving adapters satisfy
the declared source-level contract. It does not mean physical REC integration,
general anisotropic source support, full grid/PSTF convergence or parity,
physical directional-face admission, provider export, or statistics readiness.
