# RF-03 Implementation Plan — Matter, Thermodynamics and Tilt Closure

## 0. Source of truth

Use this precedence:

1. exact RF-02C terminal ref `dfa17457d402bd441d3fdf786c2d79c529512ee5` / tree `9fc67fb0ba10e091e25a14d7e1fac88b77a0241e`;
2. compiled RF-03 work unit in
   `docs/audits/science_system_differential_20260826/WORK_UNITS.json`;
3. executable source at that tree;
4. this package;
5. prose summaries.

The backup optimization lane is not a predecessor and must not be imported.

## 1. Current code-path reality

At the frozen base:

- `_rustcore/src/thermo/` already owns `dof`, `dof_table`, and Fermi-Dirac
  kernels.
- `_rustcore/src/matter/` and `_rustcore/src/tilt/` do not exist.
- `bianchi/matter/tilted_rust.py` provides the current single-call Rust
  hierarchy surface, but Python still supplies geometry rows, PSTF operators
  and bases.
- `tilted.integrate`, `tilted.rhs`, and `tilted.force_and_matrix` are registered
  through `th_*` symbols and retain an explicit transitional classification.
- the public temperature reference enforces
  `g_*s(T) T^3 ell^3 = const` for its non-tilted local-equilibrium regime and
  warns against double-counting directional redshift; tilted species require
  the existing Gamma-aware convention.

The first implementation artifact must be
`artifacts/rust_first_runtime/rf03/SCHEMA_AND_ROUTE_FREEZE.json`. It is a
bounded extraction from current source, not a new theory contract. Produce it
and immediately continue to failing tests in the same run.

## 2. Physical contract to preserve

- metric signature `(-,+,+,+)`;
- explicit current state order and units;
- `u^a u_a = -1`;
- `rho >= 0`;
- finite boosts with `|v| < 1`;
- consistent hatted/unhatted variables;
- current gamma/w and closure-mode conventions;
- current entropy and temperature conventions within their declared regime;
- no directional-redshift double counting;
- no new EOS or species family.

Known limits required in tests:

- zero tilt;
- exact constant-w oracle as explicit reference only;
- constant `g_*s` interval gives `T ∝ ell^-1`;
- zero expansion/force limits where defined;
- approach to the finite-boost boundary must fail typed rather than produce
  NaN or hidden clipping.

## 3. Architecture

Suggested owned modules, adaptable only within the exact allowlist:

```text
_rustcore/src/matter/
  mod.rs
  state.rs
  eos.rs
  force.rs

_rustcore/src/tilt/
  mod.rs
  state.rs
  invariants.rs

_rustcore/src/thermo/
  existing dof.rs / dof_table.rs / fd.rs
  history_force.rs or another source-derived equivalent

_rustcore/src/python/
  rf03_matter.rs
  rf03_thermo.rs
  rf03_tilt.rs
```

`_rustcore/src/lib.rs` may contain only module declaration and registration
wiring for RF-03. Numerical bodies belong in owned modules.

Preserve existing public Python call shapes where they are part of the current
contract. Add `bianchi/tilt/` only as a thin typed public model/adapter layer;
do not duplicate the numerical equations in Python.

`bianchi/backend_policy.py` may change only after native tests are GREEN and
only to describe the exact supported symbols/domain and explicit oracle or
transitional behavior.

## 4. TDD RED

Before implementation, add focused failures for:

1. native-only production matter route is absent or reaches the Python/constant-w
   shortcut;
2. force/JVP/C-path native parity is not yet satisfied;
3. negative density, nonfinite state and `|v| >= 1` are typed failures;
4. unsupported EOS/model is rejected before coercion;
5. explicit constant-w oracle remains callable but production default cannot
   select it;
6. logarithmic density versus logarithmic mean scale has nontrivial,
   source-consistent cooling;
7. RF-02C trajectory plus matter cannot yet complete the RF-03 contract;
8. one-thread/N-thread identity is not yet demonstrated.

Preserve the genuine RED output under RF-03 artifacts. Do not manufacture a RED
by changing expected values after implementation.

## 5. Implementation order

1. Freeze the actual source-derived state schema, model list, units, route
   inventory and equation-to-code map.
2. Implement immutable typed Rust state structures and domain validation.
3. Implement EOS/thermodynamic force and analytic JVP from the frozen source
   formulas.
4. Implement tilt normalization and hatted/unhatted adapters.
5. Move existing `th_*` numerical bodies out of `lib.rs` where they belong to
   RF-03; retain only wiring.
6. Wire thin PyO3 adapters and preserve public input/output shapes.
7. Make production routing native for the exact supported set; keep any
   retained Python/constant-w path explicit and test-only.
8. Compose one RF-02C background trajectory with native matter without a Python
   inner-step callback.
9. Implement typed physical-domain terminal outcomes and deterministic batches.

Do not expand to recombination/reionization, collisional photon physics,
performance optimization or new EOS families.

## 6. Targeted proof

Run only:

```bash
source /mnt/data/rust_1_94_1_env.sh

cd _rustcore
cargo test --release rf03_

cd ..
pytest -q tests/rf03
pytest -q tests/rf03 -k \
  'invalid or hostile or fallback or superluminal or domain'
```

Run directly invalidated RF-02C interface tests only. Do not run the full suite.

Required proof objects:

- force/JVP/C-path residual table;
- physical-domain and known-limit ledger;
- one RF-02C + native-matter trajectory;
- 1-thread/N-thread byte-identity result;
- exact public route and fallback inventory;
- native wheel/delta/restore receipt.

## 7. Plot-driven adversarial check

Generate only four compact diagnostics:

1. native/oracle force and JVP residual versus state scale;
2. `log rho` versus `log ell`, with the expected local slope/limit annotated;
3. `u^a u_a + 1`, density margin and `1-|v|^2` along a trajectory;
4. `g_*s(T) T^3 ell^3` invariant in the declared temperature regime.

Read the plots as evidence. Store `PLOT_AUDIT.json` with:

- figure intent and units;
- observed residual/limit behavior;
- whether the plot narrows or rejects the claim;
- results of sign, Gamma/normalization, superluminal and silent-fallback
  mutations;
- residual overlap/legibility check.

A figure failure is a numerical finding, not a request for aesthetic
overengineering.

## 8. Mandatory bounded dual audit

First PHYS-MATH:

- definitions, signs, normalization, units/dimensions;
- known limits;
- regularity, positivity and finite-boost domain;
- hidden assumptions and special cases.

Then PHYS-MATH-CODE:

- equation-to-code mapping;
- actual route ownership;
- native/oracle comparison;
- numerical stability/sensitivity;
- public API and regression boundary;
- test sufficiency.

Triage findings as `BLOCK_NOW`, `FIX_SOON`, `BACKLOG`, or `IGNORE`.
Repair only reproduced P0/P1 defects, then perform at most one differential
repair review.

## 9. Delivery

Use the pre-authorized role-based commit sequence:

```text
1. feat(rf03): add native matter thermo and tilt closure
2. fix(rf03): close bounded matter-tilt review findings       # optional
3. chore(rf03): bind terminal evidence and native delta       # if native bytes changed
```

No amend, squash, rebase or force push.

Open one draft PR:

```text
head: agent/architecture/rust-first-rf03-20260828-r1
base: agent/architecture/rust-first-rf02c-20260826-r1
```

Read back exact head/tree, changed paths, focused workflow runs, artifact
identity and native restore evidence. Do not merge or mark ready.
