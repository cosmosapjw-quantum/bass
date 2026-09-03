# PHYS–MATH–CODE audit

## 1. Equation-to-code map

| Physics object | Current BASS path | Reality classification |
|---|---|---|
| Eleven-family algebra carrier | `bianchi.algebra`, `bianchi.q.group` | implemented registry/carrier |
| Orthogonal backgrounds | `bianchi.charts.class_a`, `class_b`, `exceptional`, `type_ix_d`, `general` | implemented, family maturity uneven |
| Global tilt | `class_a_tilted`, `class_b_tilted`, `class_a_tilted_multi` | implemented in bounded chart families; not uniform |
| Full spectral distribution grid | `bianchi.q.modeb`, Rust `qevolve` | implemented finite grid without moment closure |
| Radial-integrated angular grid | `bianchi.q.coupled.QState`, `matter.grid_coupled` | implemented but spectrally incomplete state |
| Finite PSTF/J hierarchy | `matter.hierarchy`, Rust `kinetic.hierarchy` | implemented with explicit finite boundaries/closure |
| Generic coefficient algebra | `matter.pstf_coeff`, Rust `coeff_hier`, generated tables | implemented finite committed table plus formula generator |
| Scalar Thomson exponential | `q.collide`, Rust `collide_exact` | implemented |
| Polarized screen-tensor collision | `q.polarization`, `q.polstate`, Rust `pol_collide` | implemented bounded Q path |
| Constant electron bulk velocity | boost/collide/inverse-boost in `q.polstate` | implemented |
| Dynamic electron trajectory authority | `q.electron_trajectory`, `q.electron_validity` | authority/validation layer, not production-wired |
| Recombination opacity history | `q.rate` -> `q.model` -> `q.fast`/`q.modeb` | implemented rate schedule |
| Generic REC emission/absorption/jump source | no BASS module | absent |
| Harmonic T/E/B output split and fitting gate | no unified path found | absent |

## 2. Why the missing protocol belongs in BASS

REC should own source physics and provenance. BASS must own the adapter because only BASS knows which numerical state is being advanced:

- full spectral grid;
- radial-integrated angular grid;
- spectral PSTF workspace;
- integrated J hierarchy.

A REC-side adapter cannot safely infer these distinctions from provider output alone. The BASS protocol is therefore a receiving-side type and unit firewall, not a duplication of REC microphysics.

## 3. Current code-path blockers

### PMC-01 — no receiving source type

There is no `bianchi.source_authority` module and no immutable BASS-owned object that binds source rates, time basis, frame, channel, spectral kind and provenance. Status: **EXPECTED RED**.

### PMC-02 — Mode A and Mode B share frontend language but not source information

`q.model` calls both “Mode A” and “Mode B” under one frontend. Mode A stores an integrated angular density; Mode B stores the spectrum. A generic source adapter attached above this split could silently apply invalid physics to Mode A. Status: **P1 BLOCKER**.

### PMC-03 — PSTF labels span distinct numerical objects

The repository contains:

- spectral all-rank PSTF formula authority;
- finite `J^(i)` moment hierarchy;
- dense rank-5 PSTF projectors;
- coefficient kernels with a rank-10 table wall;
- standalone Type-II finite-state runtime primitives.

A protocol using one unqualified `PSTF` enum would be ambiguous. Status: **P1 DESIGN REQUIREMENT**.

### PMC-04 — unit boundary is not represented by a type

REC source rates are physical `s^-1`. Q uses dimensionless `tau` and dimensionless collision rates. Existing opacity scheduling performs its own conversion, but a general source bundle has no common typed conversion owner. Status: **P1 BLOCKER**.

### PMC-05 — public RF-04 v2 route remains blocked

The production adapter must not be smuggled through the unfinished RF-04 polarized-v2 public route. The R5 protocol must remain dependency-light and independent of that route. Status: **P1 LINEAGE FIREWALL**.

### PMC-06 — output layer cannot validate the future source yet

There is no full `a_lm^(T,E,B)` split or fitting gate on the inspected parent. Source-adapter success must therefore stop at state/source parity and must not be promoted to statistics readiness. Status: **P1 CLAIM FIREWALL**.

## 4. TDD boundary

The committed test imports the missing receiving protocol and specifies only the first-green semantics:

1. retain nonnegative `eta_s_inv` and `kappa_s_inv`;
2. derive signed `chi_affine_s_inv`;
3. convert exactly to Q time;
4. provide the pointwise constant-pair action;
5. enforce distinct representation kinds;
6. reject a pointwise spectral source on the radial-integrated state;
7. enforce the angular work-rank guard;
8. retain a stable source payload identity.

It does not require physical REC source data or any production integration.

## 5. Test sufficiency

The RED test is sufficient to establish that the receiving protocol is absent and to freeze the minimal public semantics. It is not sufficient for:

- grid/PSTF numerical parity;
- source Jacobian parity;
- nonconstant frequency interpolation;
- anisotropic jump-tail convergence;
- polarized source action;
- dynamic electron trajectory wiring;
- family/output/statistics validation.

These remain later nodes.

## 6. Regression risks for the first GREEN

1. importing heavy optional dependencies from the top-level package;
2. changing backend selection or public RF-04 route tables;
3. adding a permissive Mode-A fallback;
4. using NumPy arrays in source hashes without canonical byte/shape/dtype rules;
5. normalizing away negative `chi_affine`;
6. accepting malformed provenance hashes;
7. conflating `s^-1`, ray-length `m^-1`, and dimensionless per-`tau` rates;
8. making TEFF diagnostics state-mutating.

## 7. Required R5 implementation shape

Recommended minimum:

```text
bianchi/source_authority.py
```

Dependency policy:

- standard library only for the first GREEN;
- immutable dataclasses/enums;
- finite scalar validation;
- canonical SHA-256 payload;
- no direct import of Q, compiler, Rust, REC, SciPy or optional backends;
- no production wiring.

## 8. Verdict

```text
PHYS_MATH_CODE_AUDIT_PASS_FOR_EXPECTED_RED
PRODUCTION_SOURCE_ADAPTER_ABSENT
NO_IMPLEMENTATION_OR_SCIENCE_PROMOTION
```
