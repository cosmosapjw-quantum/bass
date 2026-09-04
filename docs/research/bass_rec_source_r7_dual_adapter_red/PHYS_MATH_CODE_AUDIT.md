# PHYS–MATH–CODE audit — R7 dual-adapter RED

## Equation-to-code boundary

| Object | Existing owner | R7 status |
|---|---|---|
| positive photon/boson source pair | `bianchi.source_authority` | implemented and R5/R6 qualified |
| full spectral/angular distribution state | Q Mode B and legacy grid paths | implemented numerical carriers; no REC adapter |
| spectral PSTF coefficient algebra | `bianchi.matter.pstf_coeff` and formula/compiler layers | implemented algebra; no REC adapter |
| integrated angular-energy state | Q Mode A / coupled grid | intentionally excluded |
| finite integrated `J^(i)` hierarchy | hierarchy paths | intentionally excluded |
| time/ray-length conversion | source protocol has Q-time primitive | common typed adapter absent |
| source application receipt | none | expected RED |

## Missing implementation

The future receiving module is:

```text
bianchi/source_adapters.py
```

It must be a BASS-owned type/unit/identity adapter. It must not duplicate:

- REC atomic-rate calculation;
- the BASS full-grid transport solver;
- the existing PSTF/Gaunt generator;
- integrated-state closures;
- physical-face reconstruction.

## R7 test obligations

1. expose a typed physical-time/Q-time/ray-length basis;
2. apply the R6 constant positive pair pointwise to a full-spectral grid;
3. apply the same pair to coefficient states using caller-supplied unit-field
   coefficients;
4. bind both results to the same source payload, parent state and projection
   contract;
5. retain distinct representation identities;
6. reproduce the axisymmetric Legendre commutation fixture;
7. reject insufficient work rank;
8. reject integrated state kinds;
9. reject missing or ambiguous identity/time inputs;
10. produce deterministic, input-sensitive result receipts.

Two tests are independent controls and must remain green when the adapter module
is absent: the qualified R6 source authority and exact low-order Legendre
projection.

## Expected first failure

Every adapter test imports `bianchi.source_adapters` inside the test body. At the
pinned parent the module is absent, so the intended result is:

```text
12 tests run
10 assertion failures
0 errors
2 passing controls
```

A collection error or an unrelated import failure is not an admissible RED.

## Minimal R8 implementation boundary

The first GREEN may add only:

```text
bianchi/source_adapters.py
```

plus narrowly necessary test/receipt updates. Recommended properties:

- standard-library-only production module;
- frozen/slotted result and receipt objects;
- factory-controlled identity validation;
- scalar/sequence binary64 finite checks;
- canonical SHA-256 based on explicit schema, `float.hex()`, shape/order and all
  authority fields;
- no import from Q, compiler, Rust, REC, SciPy or optional backends;
- no route-table or solver-loop change.

## Regression cone after GREEN

1. R5 source-authority survivors;
2. R6 hardening suite;
3. R7 dual-adapter suite;
4. source/binding/result hashes in two fresh processes;
5. backend policy/integration/packaging parent–candidate differential under the
   trusted RF-00 payload;
6. clean source worktrees with root build in non-Git staging.

## Risks

### P1

- one representation receives a rescaled or mutated source pair;
- a coefficient adapter assumes an undocumented monopole normalization;
- result receipts omit projection or parent-state identity;
- grid and PSTF paths use different time bases;
- the adapter is prematurely wired into a production solver.

### P2

- output hashes omit shape/order or signed-zero canonicalization;
- the test fixture is mistaken for generic nonconstant-source parity;
- a bare 26-node vector is admitted as a physical face;
- R8 imports heavy optional dependencies into the top-level package;
- ray-length conversion silently uses natural units.

### P3

Naming the coefficient route `PSTF` can obscure whether a specific code path is
dense-tensor PSTF, canonical `2l+1` coefficients, or Wigner coefficients. The
representation SHA and projection-contract SHA must carry that distinction.

## Verdict

```text
PHYS_MATH_CODE_R7_EXPECTED_RED_CONTRACT_PASS
NO_PRODUCTION_CODE_CHANGED
NO_ADAPTER_IMPLEMENTED
NO_SOLVER_OR_SCIENCE_PROMOTION
```
