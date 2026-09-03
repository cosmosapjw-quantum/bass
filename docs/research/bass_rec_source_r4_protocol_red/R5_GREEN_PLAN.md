# R5 minimal GREEN implementation plan

## Goal

Turn the single expected RED import into GREEN by adding a dependency-light BASS receiving protocol. Do not connect physical REC data or any solver loop yet.

## Allowed implementation

Create exactly:

```text
bianchi/source_authority.py
```

The module should use only the Python standard library.

## Required types

### `SourceFrequencyKind`

```text
POINTWISE_SPECTRAL
SOURCE_INTEGRATED_WITNESS
```

### `SourceStateKind`

```text
FULL_SPECTRAL_GRID
RADIAL_INTEGRATED_ANGULAR_GRID
FINITE_SPECTRAL_PSTF
FINITE_INTEGRATED_J_HIERARCHY
```

### `SourceRepresentationError`

A typed error for a physically underdetermined state/source pairing.

### `SourceAuthorityBundle`

An immutable dataclass with a `constant_pair` constructor. Minimum fields:

```text
eta_s_inv
kappa_s_inv
frame
channel
source_sha256
frequency_kind
payload_sha256
```

Minimum behavior:

- reject nonfinite or negative `eta_s_inv` and `kappa_s_inv`;
- accept either sign of `chi_affine_s_inv=kappa_s_inv-eta_s_inv`;
- reject malformed source hashes and empty frame/channel strings;
- generate a stable canonical payload SHA-256;
- return `(eta_per_tau,kappa_per_tau)` from `rates_per_tau(H_s_inv)`;
- reject nonpositive/nonfinite `H_s_inv`;
- return `eta*(1+f)-kappa*f` from `pointwise_action(f)` for finite nonnegative scalar `f`.

## Required functions

### `required_work_rank(l_out,l_source)`

Return `l_out+l_source` after rejecting booleans, nonintegers and negative ranks.

### `validate_work_rank(l_work,l_out,l_source)`

Return the required rank if `l_work` is sufficient; otherwise raise `ValueError` with all three ranks in the message.

### `require_source_representation_compatibility(frequency_kind,state_kind)`

Rules:

- `POINTWISE_SPECTRAL` is admitted for `FULL_SPECTRAL_GRID` and `FINITE_SPECTRAL_PSTF`;
- `POINTWISE_SPECTRAL` is rejected for `RADIAL_INTEGRATED_ANGULAR_GRID` and `FINITE_INTEGRATED_J_HIERARCHY`;
- `SOURCE_INTEGRATED_WITNESS` is admitted only for the two integrated state kinds in this first protocol.

A later stage may generalize these rules only with a theorem and tests.

## Tests

Run only the focused RED file first. The sequence must be visible:

```text
1. parent test fails because module is absent
2. add minimal module
3. focused test passes
4. run import-boundary and backend-policy regressions
5. run full Python suite only after the focused cone passes
```

Do not edit the test to fit a different implementation after GREEN work starts unless the contract itself is formally amended in a separate commit.

## Mandatory audits after GREEN

### PHYS–MATH

- sign and unit checks;
- zero-source, negative-`chi_affine`, and isotropic-source controls;
- exact time-basis conversion;
- rank-domain validation;
- Mode-A nonidentifiability counterexample.

### PHYS–MATH–CODE

- import remains dependency-light;
- payload hash is deterministic across process runs;
- no backend route or solver behavior changes;
- no implicit NumPy dtype/endianness hash ambiguity;
- no TEFF state mutation;
- no physical REC source admitted.

## Completion criterion

```text
PASS_BASS_REC_SOURCE_R5_PROTOCOL_GREEN
```

means only that the receiving protocol exists and satisfies the focused tests. It does not mean source integration, grid/PSTF parity, recombination completion, RF-04 completion, output readiness, or statistics readiness.
