# B1 Polarization Authority Reconciliation — 2026-08-21

## Verdict

**RECONCILED.** The basis-free BASS rank-9 coherency carrier does not intrinsically select a Stokes-`V` sign. It stores

```text
p8 = (J12 - J21)/2.
```

The project local-screen diagnostic convention is fixed as

```text
H = 1/2 [[I+Q, U-iV], [U+iV, I-Q]]
p8 = -V/2
```

for a right-handed screen `(s1,s2,e)` with `s1 × s2 = e`.

This is the convention already used by PR #13. A later local work-package adapter used

```text
H_alt = 1/2 [[I+Q, U+iV], [U-iV, I-Q]]
p8 = +V/2,
```

which is internally consistent only after the relabeling `V_alt=-V`. It is retained as historical evidence but classified `SUPERSEDED_ALTERNATIVE_CONVENTION`.

## Authority chain

1. The original polarization authority defines a basis-free Hermitian screen tensor with six symmetric and three antisymmetric real components.
2. The packed carrier fixes the antisymmetric coordinate `p8=(J12-J21)/2`; it does not name that coordinate `V`.
3. PR #13 chooses `V=J21-J12`, giving `p8=-V/2`.
4. Before this correction, `compiler/validation/typeii_polarized_runtime.py` encoded and decoded the alternative `p8=+V/2` label. This PR now changes both adapter signs to the PR #13 convention.
5. The PR #13 finite active/passive spin-2 phases are unchanged by this reconciliation.
6. PR #14 and the deferred B2B package transport packed tensors by congruence rather than interpolating node-local Stokes components, so their tensor-geometric results are invariant under `V→-V` relabeling.

Pinned upstream authority hashes from the PR #8 generator:

```text
_rustcore/src/kinetic/pol_collide.rs
c6cb5099b139a4f04a5693d1f07ae8bffd90acc9b5ffd32579532a2dce5fe202

audit/p3_polarized_thomson.py
eb5ba68a22c88f88026bdd27898e5b6e03abae901f7aa9a0982389f5d7436255

audit/p9_boost_screen.py
8ab2545b535cf89a3cf2b3ae45d2d0a8e9df0d8a1e6695f979dd29dd60f8aed9

bianchi/q/polstate.py
3ebabbfe264a50dfe2fd0a2e39c279b201a6911a9711abd9f698f9ad53264da1

docs/P-DERIVATION.md
a25e1f897a71efbba02f3d971dd36fcff8c20f3b3abfb36c9cb06401681fd91d
```

## Executable witnesses

The reconciliation regression requires:

- canonical `e=z`, pure circular state: `packed[8]=-V/2`;
- generic tensor→Stokes→tensor roundtrip for positive, negative and zero `V`;
- rest-frame Thomson collision does not mix a pure-`V` input into `Q/U`;
- the superseded `+V/2` embedding is explicitly detected as the opposite label.

## Corrective implementation and replay

The implementation delta is confined to the existing Python
validation/diagnostic adapter:

```text
compiler/validation/typeii_polarized_runtime.py
encoder: +V/2 -> -V/2
decoder: +2 u A v -> -2 u A v
```

The corrected file has SHA-256
`d660afe25e60fbf4350d5ac25711dc8e64ad2ba02258d55238c315a8af1f4696`
and Git blob `3dfc86dea2f0c20c09c467068e9dc2084cfeb1cd`.

Fresh corrective replay on 2026-08-22 produced:

```text
exact-head reconciliation RED       2 failed, 2 passed
corrected reconciliation            4 passed
independent complex-Hermitian oracle 6 passed
full public Python repository        93 passed
exact Rust Stokes target              9 passed
recovered G-RUNTIME-KATO-II target    4 passed
full locked/offline Rust stack      227 passed
```

The recovered historical runtime authority bundle has SHA-256
`0b0cf2637a65c96c3024820ffb2a3feecfa43d94b659a4649b9cbf141c22364f`.
Its test and fixture bytes match the receipt hashes
`599aa392adffd59d85e54136296a596ff8ea0324df4c1efeccca751f7a98abf1`
and `5737dead724b86ead64cc25f9e00802973df1eb2abbdc92a5e7c095df1378ef1`.
The full Rust replay used Rust/Cargo 1.94.1, `--locked --offline`, and
`Cargo.lock` SHA-256
`d500208e9353ade1cb74693918598846628219e6e7bd2e2bce9ec85e29eb6310`.

## Claim boundary

Allowed:

> BASS internal local-screen diagnostics use `H12=(U-iV)/2`, `H21=(U+iV)/2`, hence `packed[8]=-V/2`.

Not claimed:

- IAU/COSMO/HEALPix observed-sky compatibility;
- an observer-direction bridge `n=-e`;
- a global nonsingular dyad atlas;
- an E/B or Wigner convention;
- a change to the basis-free collision, Liouville or remap physics.

This audit verifies the local convention correction and its regression gates.
It does not by itself approve merge, close BASS-2, or open Join J1.

## Governance

- Jira: `BASS-2`.
- Control plane: Confluence page `7700482`.
- The `+V/2` local package is superseded for naming only, not deleted.
- Future output adapters must name both propagation/observer direction and map convention explicitly.
