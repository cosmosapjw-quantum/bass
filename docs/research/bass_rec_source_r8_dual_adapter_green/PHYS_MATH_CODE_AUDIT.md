# PHYS–MATH–CODE Audit — R8 Constant-Pair Dual Adapter

## Equation-to-code map

| Contract | Code path |
|---|---|
| `C_t[f]=eta-(kappa-eta)f` on explicit samples | `apply_constant_pair_to_full_spectral_grid` |
| `C_alpha=eta*1_alpha-(kappa-eta)f_alpha` | `apply_constant_pair_to_spectral_pstf` |
| physical/Q/ray-length conversion | `_rate_divisor`, `_scaled_finite` |
| pointwise-state firewall | `require_dual_adapter_target` |
| constant-source rank guard | `validate_work_rank(..., l_source=0)` |
| application provenance | `SourceApplicationReceipt`, `_application_hash` |

## Implemented and used

- Standard-library-only receiving module.
- Exact reuse of the qualified `SourceAuthorityBundle`; no new rate object.
- Full-grid inputs are finite nonnegative occupations.
- Coefficient and unit-field vectors are finite and equal-length.
- Physical, Q-time and ray-length inputs are mutually exclusive and fail closed.
- Output identity includes output values, source payload, state parent, representation, projection contract, time basis, divisor and adapter parameters.
- Integrated `G(e)` and `J^(i)` targets remain rejected.

## P0/P1 findings

No source-level P0 contradiction was found against the executed R7 test contract.

Open P1 items:

1. Exact local R8 GREEN execution is not yet observed.
2. The low-order Legendre fixture is not a full nonaxisymmetric PSTF/Wigner parity proof.
3. The adapter is not connected to a real BASS state object or solver update path.
4. `projection_contract_sha256` is caller supplied; registry-backed projector lookup is deferred.
5. A physical REC donor and source-to-binding cross-identity check are absent.

## P2 findings

- Application receipt/result constructors are public immutable dataclasses rather than factory-only authority objects.
- The first coefficient adapter treats the vector layout as caller-declared and does not encode a basis-shape schema beyond `representation_sha256` and `projection_contract_sha256`.
- Subnormal/underflow policy is not specialized beyond finite binary64 checks.
- Native acceleration is deliberately absent; this is not a performance path.

## Regression boundary

The local runner requires:

```text
R5+R6+R7 = 33/33 PASS
source and coefficient output hashes deterministic
projection-contract mutation changes output identity
adversarial input probes PASS
source worktree clean
```

After that, the required repository-level gate is a trusted-native parent/candidate differential. Solver wiring and numerical parity remain later nodes.

## Verdict

The change is a minimal receiving adapter candidate consistent with the bounded R7 contract. It must remain Draft and unmerged until exact local GREEN and post-GREEN nonregression receipts are observed.
