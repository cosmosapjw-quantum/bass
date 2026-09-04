# BASS REC Source R10A — Projection Authority Hardening Expected RED

## Purpose

R10 passed its exact bounded local behavior gate. The post-GREEN hostile audit nevertheless found that the current `SphereQuadrature`, comparison contract, and report are not yet strong enough to serve as integration-grade authority objects.

R10A is a test-only node. It adds no production implementation. Its sixteen tests preserve three controls and define thirteen missing hardening behaviours:

1. reject stale projection hashes at every public use boundary;
2. reject same-length node/weight tampering;
3. bind the realized basis operator rather than only a convention label;
4. declare the flattened sample layout;
5. separate semantic specification from binary64 realization identity;
6. expose a basis-matrix identity;
7. bind the actual supplied unit-field vector;
8. bind time basis and rate divisor;
9. make `SourceParityContract` factory-only;
10. make `SourceParityReport` factory-only;
11. report tolerance-utilization rather than only absolute residual;
12. state explicitly that continuous positivity is not certified;
13. fail closed above the executed certification envelope.

## Exact ancestry

```text
R10 closeout parent
662f682654f80281a4afd56a28be1ff0d535e2ac

R10A test source
931ce2d4cd499bc388027c36a68c4b72b6c65d6e

tree
3889efcd37f6a30c2e2222856e17e8452c4a52b3

test blob
de2f341ce04b4b061efbdab360525ef87996701d

production source remains
a807191ff0baa6851ec7748826a7d4e34b400207
```

The source commit adds exactly one file:

```text
A  tests/research/test_bass_rec_source_r10a_projection_authority_red.py
```

## Expected local result

```text
PASS_EXPECTED_R10A_PROJECTION_AUTHORITY_HARDENING_RED
inherited survivors       49/49 PASS
R10A tests                16
intended assertion fails  13
passing controls           3
errors/skips               0/0
production diff            none
clean worktree             true
```

The exact runner is:

```text
scripts/research/run_bass_rec_source_r10a_red_local.sh
```

No R10A production change is permitted before that exact result is observed.

## Scope firewall

R10A does not implement a high-L transform, production PSTF registry bridge, anisotropic source product, spin-weighted projection, continuous positivity theorem, state-container source step, transport integration, physical REC donor, provider export, or statistics promotion.
