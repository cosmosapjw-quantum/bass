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
3. The original diagnostic adapter and PR #13 choose `V=J21-J12`, giving `p8=-V/2`.
4. The PR #13 finite active/passive spin-2 phases are unchanged by this reconciliation.
5. PR #14 and the deferred B2B package transport packed tensors by congruence rather than interpolating node-local Stokes components, so their tensor-geometric results are invariant under `V→-V` relabeling.

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

## Claim boundary

Allowed:

> BASS internal local-screen diagnostics use `H12=(U-iV)/2`, `H21=(U+iV)/2`, hence `packed[8]=-V/2`.

Not claimed:

- IAU/COSMO/HEALPix observed-sky compatibility;
- an observer-direction bridge `n=-e`;
- a global nonsingular dyad atlas;
- an E/B or Wigner convention;
- a change to the basis-free collision, Liouville or remap physics.

## Governance

- Jira: `BASS-2`.
- Control plane: Confluence page `7700482`.
- The `+V/2` local package is superseded for naming only, not deleted.
- Future output adapters must name both propagation/observer direction and map convention explicitly.
