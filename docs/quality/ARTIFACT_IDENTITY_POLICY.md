# BASS artifact identity policy

Artifact identity is an atomic tuple:

```text
(filename, size_bytes, sha256)
```

A filename alone never establishes identity. A receipt may support a decision
only when its `subject` tuple matches the observed artifact and its `source`
tuple matches the declared reference. Missing or mismatched binding is
`UNBOUND_HISTORICAL_EVIDENCE`.

## Identity classes

| Class | Object | Authoritative comparison | SHA-mismatch disposition |
|---|---|---|---|
| A | Immutable source or input | Exact bytes | Hard-block the byte-identity claim. Content equivalence cannot excuse it. |
| B | Deterministic generated evidence | Exact deterministic bytes or a declared deterministic tree digest | Hard-block when deterministic identity is part of the evidence contract. Generated caches and unmanifested files fail closed. |
| C | Scientific or numerical content | Explicit scientific/content criteria | A container SHA difference is not a scientific failure. Pass only when all declared invariants, residuals, parity, convergence, or other justified criteria pass. |
| D | Packaging or build metadata | Reproducibility requirements | Record a packaging finding. Hard-block only when byte-identical packaging is explicitly authoritative. |

`BYTE_IDENTITY_MISMATCH` is a byte-identity signal. It is never automatically
promoted to `SCIENTIFIC_INTEGRITY_FAILURE`. A and B remain hard-blocking where
their contracts make byte identity authoritative; C requires scientific
criteria; D remains a packaging/reproducibility finding unless the request sets
`byte_identity_authoritative`.

## Fail-closed codes

- `ARTIFACT_IDENTITY_COLLISION`: one filename is presented with a different
  size or SHA-256 where A/B exact identity is authoritative; P0.
- `BLOCKED_INPUT_REQUIRED`: a required artifact, sidecar, or manifested member
  is absent.
- `UNBOUND_HISTORICAL_EVIDENCE`: the receipt does not bind exact observed
  subject and declared source tuples; P0.
- `NON_PORTABLE_SIDECAR`: a sidecar names an absolute, parent-relative, or
  platform-specific path. This blocks portable verification but is not a
  scientific-integrity verdict.
- `CACHE_CONTAMINATION`: a deterministic evidence tree contains Python cache
  output. This blocks class B evidence identity without changing immutable
  archive bytes or physics claims.
- `BLOCKED_CONTENT_CRITERIA_REQUIRED`: class C equivalence was requested without
  a nonempty set of explicit criteria whose statuses are all `PASS`.
- `PASS_CONTENT_EQUIVALENCE`: distinct container bytes passed the declared
  scientific/content criteria. It does not assert byte-identical packaging.
- `PACKAGING_METADATA_MISMATCH`: nonblocking class D byte difference when exact
  packaging bytes are not authoritative.

## Interfaces

`scripts/verify_artifact_identity.py --request REQUEST.json` accepts schema
`bass-artifact-identity-request-v1` and emits one deterministic JSON result with
schema `bass-artifact-identity-result-v1`. Exit status is `0` for a pass or
nonblocking packaging finding, `2` for a blocked/incomplete verification, and
`3` for a P0 identity failure. `--self-test` exercises exact class A and
non-scientific class D handling.

`scripts/verify_allowed_diff.py --base SHA --contract ACTIVE_WORK_UNIT.json`
compares committed, staged, working-tree, and untracked paths with the exact
base. Forbidden patterns take precedence over allowed patterns. Any forbidden
or non-allowlisted path emits `FORBIDDEN_REFERENCE_MUTATION` and exits `3`.
