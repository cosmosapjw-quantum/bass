# Post-GREEN hostile audit — R10 scalar projection parity

## Disposition

The exact local R10 runner passed its declared bounded gate. This audit does not revoke that result. It narrows the claim and identifies authority defects that must be fixed before a trusted-native R10 differential, production PSTF-layout admission, or solver/state wiring.

```text
SURVIVES
  L=0,1,2,3,4,6,8 scalar constant-source parity
  one real Condon-Shortley convention on dOmega
  same-implementation synthesis/projection
  declared GL x uniform-phi rule

WITHHELD
  projection object as an integration-grade authority
  arbitrary-rank numerical certification
  production PSTF-layout parity
  continuous-sphere positivity
  transport or physical REC source parity
```

## Evidence read back

- focused tests: 49/49;
- maximum parity residual through L=8: `1.4226467226485795e-14`;
- maximum Gram infinity defect: `5.662137425588298e-15`;
- maximum Gram infinity condition estimate: `1.0000000000000364`;
- two-process parity receipts: identical;
- declared mutation probes: pass;
- SymPy/mpmath/Octave/SageMath/Singular: pass in the local runner;
- Lean executable present, but Mathlib unavailable on its search path;
- source worktree: clean.

## Root-cause analysis

### P1-01 — the projection hash is not the realized projection operator

`SphereQuadrature.create` hashes nodes, weights, convention text, mode order and the canonical unit field. It does not hash the evaluated basis matrix, the basis-algorithm version, or the flattened sample layout. A defect in `_real_harmonic`, or a consumer that interprets samples with a different flattening order, can therefore retain the same `projection_contract_sha256` while changing the actual operator.

**Required correction:** split semantic specification and binary64 realization identities. Bind at least:

```text
projection_spec_sha256
projection_realization_sha256
basis_matrix_sha256
sample_layout = mu_major_phi_minor
basis_algorithm_id
quadrature_algorithm_id
```

### P1-02 — use-time quadrature integrity is not fail-closed

`_validated_quadrature` checks type, rank and array lengths only. A frozen dataclass can still be altered through low-level `object.__setattr__`, deserialization, or a forged object. Same-length node/weight mutations and a stale or forged projection hash are then accepted.

**Required correction:** recompute and compare semantic/realization identities at every public use boundary; revalidate finite ordered nodes, positive weights, dimensions, symmetry, weight sums and declared resolution.

### P1-03 — the actual unit field is omitted from the comparison contract

`compare_constant_pair_grid_and_pstf` accepts a caller-supplied `unit_field_coefficients`. The direct coefficient source uses it, but `_build_contract` does not hash it. A normalization mutation can therefore change the calculation while preserving `contract_sha256`; only the later report hash changes.

**Required correction:** include the actual unit-field SHA and a canonical/noncanonical flag in the comparison contract. Diagnostic noncanonical vectors may remain allowed only with `require_pass=false` and must never reuse the canonical contract identity.

### P1-04 — time basis and divisor are not part of `SourceParityContract`

The PR description says the parity contract binds time basis and divisor. The current `SourceParityContract` does not; those fields appear only in `SourceParityReport`. Physical-time and Q-time comparisons can therefore share one contract hash.

**Required correction:** either rename the current object to an angular/source contract and document that narrower role, or include `time_basis` and `rate_divisor_hex` in the contract. The latter is preferred for a single comparison authority.

### P1-05 — contract and report objects can be forged

`SourceParityContract` and `SourceParityReport` are public frozen dataclasses with generated constructors. A caller can instantiate internally inconsistent objects and supply arbitrary SHA strings. Frozen-after-construction is not valid-by-construction.

**Required correction:** factory-only construction, internal hash recomputation, and public validation helpers.

### P1-06 — synthesis and projection share one harmonic implementation

A common phase, normalization, recurrence or mode-order defect can cancel in a synthesis/projection round trip. The current independent formal lanes verify the affine source algebra and Gauss-Legendre moments, but do not independently validate the implemented real harmonics pointwise.

**Required correction:** add a second harmonic oracle in the test runner. Minimum checks:

```text
selected modes against SciPy/SymPy spherical harmonics
addition theorem sum_m |Y_lm|^2=(2l+1)/(4pi)
reflection/azimuth phase identities
bounded Wigner/Gaunt selection rules
```

### P1-07 — the API accepts ranks beyond the executed certification envelope

Runtime evidence covers `L<=8`, while the public builder accepts every finite nonnegative rank. The unscaled associated-Legendre recurrence and direct Gram inversion are not justified at arbitrary high degree/order.

**Required correction:** introduce an evidence-bound certification ceiling for the current implementation, initially `L<=8`, or require an explicit numerical certificate for larger ranks. This is an admission ceiling, not an architectural commitment. A later high-L lane should use scaled ALFs, Clenshaw/Fourier methods, or a qualified SHT library.

### P2-01 — sampled positivity is not continuous positivity

The full-grid route checks synthesized occupation only at the quadrature nodes. Positivity at finitely many nodes does not prove nonnegativity everywhere on the sphere for a general band-limited polynomial.

**Required correction:** report `continuous_positivity_certified=false` unless a separate realizability/positivity certificate is supplied. Do not use R10 as a physical-state positivity theorem.

### P2-02 — the plot does not display the actual scaled acceptance criterion

Parity acceptance is

```text
|r_i| <= atol + rtol*max(|g_i|,|p_i|)
```

but the plot shows one flat `2e-13` line. This is not the same threshold for nonunit-amplitude coefficients.

**Required correction:** record and plot the maximum tolerance-utilization ratio

```text
max_i |r_i|/(atol+rtol*scale_i)
```

with admission at `<=1`.

### P2-03 — semantic and byte identities are conflated

The current projection SHA includes binary64 nodes produced by Newton iteration and libm. It is a realization identity, not a portable semantic identity. Same semantic construction can receive different hashes on another platform, while one code-level basis defect can leave the hash unchanged.

**Required correction:** maintain two explicitly named identities: exact semantic specification and realized floating operator.

### P2-04 — current result is not production PSTF parity

R10 compares a private real-harmonic tuple layout, not the actual BASS PSTF coefficient registry, Wigner adapter, Q Mode B state container, or evolution loop.

**Required correction:** keep the next state/registry bridge separate from R10A hardening and require its own TDD RED.

## Correction order

```text
R10 local bounded GREEN                          PASS
  -> R10A projection-authority hardening RED     NEXT
  -> R10A GREEN                                  blocked on executed RED
  -> R10B trusted-native differential            blocked
  -> R11 production PSTF-registry bridge RED     blocked
  -> R12 state-container source-step parity      blocked
```

## Literature-guided high-rank route

The current direct recurrence is appropriate only as a low-rank correctness oracle. High-rank work should evaluate scaled associated-Legendre recurrences, Clenshaw synthesis, Fourier-series/Wigner-d transforms, preconditioned discrete SHTs, or qualified SHT libraries. The literature has method-level relevance only and no authority over BASS signs, hashes or admission.

## Final audit verdict

```text
R10_BOUNDED_BEHAVIOR_PASS
R10_AUTHORITY_HARDENING_REQUIRED
NO_R10B_OR_SOLVER_WIRING_YET
NO_PHYSICAL_REC_OR_ALL_RANK_NUMERICAL_CLAIM
```
