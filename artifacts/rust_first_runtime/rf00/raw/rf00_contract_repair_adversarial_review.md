# RF-00 bounded adversarial change review

## Verdict

`BLOCKED_REPAIR_REQUIRED`

The implementation commit is a clean, Python-only descendant of the required
start, and the focused receipts support most of the intended policy repair.
Three bounded contract defects remain. The first two block the requested RF-00
closeout; the third is a policy-matrix consistency concern that should be fixed
in the same single repair-closeout.

## Review identity and method

- Reviewed commit: `8101fc47c4bccdcb2bfb0b17c5d27a9231f33a91`
- Parent/start: `4fd541967341f81999a5d1b7147dbb04849ade22`
- Reviewed tree: `24771914743935caf8eb516e5a7cfdd3fb96d810`
- Scope: all 84 changed paths plus directly referenced RF-00 evidence and import
  dependencies.
- Method: static diff/source inspection and readback of the coordinator's
  existing proof logs only. No test, build, benchmark, Wolfram command, Git
  mutation, or remote mutation was run by this reviewer.

## Confirmed blockers

### RF00-REVIEW-B1 — performance acceptance authority remains in summaries

The primary timing bytes are now honest: the chart case at
`artifacts/rust_first_runtime/rf00/raw/rf00_paired_repair_final.json:38-48`,
the cold-import case at the same file's `2580-2589`, and the aggregate decision
at `5089-5092` carry `evidence_class=EXPLORATORY_ONLY` and
`acceptance_claim=NONE`; the log records that the benchmark was not rerun. The
measured chart ratio `1.0303681533929716` is preserved.

However, two authority-facing summaries still turn those same measurements
into a PASS:

- `artifacts/rust_first_runtime/rf00/EVIDENCE.json:196-210` says
  `PASS_NO_STATISTICALLY_SUPPORTED_REGRESSION_ABOVE_5_PERCENT` and retains a
  `1.05` acceptance ceiling.
- `docs/rust_first_runtime/HANDOFF.md:15` says the paired no-regression gate
  passes.

The evidence index and handoff also still bind the pre-repair implementation at
`artifacts/rust_first_runtime/rf00/EVIDENCE.json:25-36` and
`docs/rust_first_runtime/HANDOFF.md:7-8`. That identity staleness is expected
before final closeout, but it must not survive delivery.

Smallest fix: make the evidence index and handoff say
`EXPLORATORY_ONLY`/`acceptance_claim=NONE`, retain ratios and intervals only as
observations, remove the ceiling/PASS decision, and refresh their source/head
bindings and digests after the repair commit. Do not rerun the benchmark.

### RF00-REVIEW-B2 — native-required routes still eagerly load optional stacks

The package root is lazy and the minimal smoke proves one verified
`background.chart_rhs` call with only NumPy plus the native wheel. That does not
close AUD-12 for the committed native-required route inventory. Five route
modules cross into JAX or SymPy before backend selection or native dispatch:

- `bianchi/analysis/mixmaster.py:24-36` imports the diffrax/JAX integration,
  Kasner, chart, conventions, then calls `require_jax_x64` at module import;
  selection for native route `mixmaster.bounce_sequence` occurs only at
  `bianchi/analysis/mixmaster.py:113-126`.
- `bianchi/matter/coupled_tilted.py:30-42` loads JAX and JAX/SymPy-backed oracle
  modules at import, although its native-only wrappers begin at
  `bianchi/matter/coupled_tilted.py:225-240`.
- `bianchi/matter/coeff_kernel.py:18-22` imports `pstf_coeff`; that dependency
  loads SymPy at `bianchi/matter/pstf_coeff.py:49-52` before native-only wrappers
  at `bianchi/matter/coeff_kernel.py:63-97` can call typed policy.
- `bianchi/routing.py:32-33` imports `algebra`, which imports `conventions` at
  `bianchi/algebra.py:20`; `conventions` initializes JAX at
  `bianchi/conventions.py:23-36` before native-only routing reaches
  `require_native` at `bianchi/routing.py:118-122` or the second wrapper.
- `bianchi/observables/cmb_pattern.py:26` imports the unused geodesics module;
  its chain imports `conventions` and `rays.frame`, whose module-scope JAX load
  occurs at `bianchi/rays/frame.py:18-20`, before
  `observable.cmb_pattern_diag` selects a backend at
  `bianchi/observables/cmb_pattern.py:40-54`.

This contradicts the requirement that optional JAX/diffrax/SciPy/SymPy load
only after an explicit optional frontend/oracle selection. It also means a
minimal production install can fail with a `python-oracle` installation hint
while importing a route inventoried as `native_required` and, for several of
these, `python_oracle=unsupported`.

Current proof cannot falsify the defect:

- `tests/test_rf00_optional_dependencies.py:40-64` blocks optional imports only
  while importing `bianchi`, `backend_policy`, and `backend`.
- `logs/changed_module_imports.log` imported changed modules in the full
  optional environment.
- `logs/fresh_minimal_install_and_smoke.log` exercised only
  `background.chart_rhs` after the three lightweight imports.

Smallest fix: keep each route's native adapter and NumPy-only input preparation
dependency-light; move JAX/diffrax/SymPy imports behind the explicit oracle
branch or into a lazily imported oracle helper. Remove the unused CMB geodesics
import. Where shared constants/adapters currently live in JAX/SymPy modules,
split only their byte-identical NumPy data preparation into a dependency-light
module; do not port or alter physics. Extend the existing import-blocking test
to import every native-required route module (and perform the smallest native
route smoke where feasible) while rejecting all optional roots. The existing
focused CI job will then exercise the actual AUD-12 boundary.

## Confirmed concern

### RF00-REVIEW-C1 — `auto_diagnostic` can select a nonexistent oracle

`PUBLIC_ROUTE_INVENTORY` correctly marks native-only routes' explicit oracle
state `unsupported` at `bianchi/backend_policy.py:406-425`. Explicit
`python_oracle` and `force_python` requests enforce that. But when the native
module is unavailable, `select_backend` returns a `PYTHON_ORACLE` selection for
every `AUTO_DIAGNOSTIC` request at `bianchi/backend_policy.py:738-748` without
checking `capability.python_oracle_supported`.

For routes such as `q.fast.evolve` or `coeff_kernel.lhs_grid`, that selection
has no Python implementation and contradicts the committed matrix. Although
the current direct wrappers call `require_native` and do not take this branch,
the public selector can expose an impossible state.

Smallest fix: before returning the auto-selected oracle, raise the existing
typed `BackendPolicyError` when `python_oracle_supported` is false; add one
focused native-only/missing-extension case.

## Nonblocking confirmations

- The raw affinity-only receipt and benchmark driver are honestly
  `EXPLORATORY_ONLY`; no benchmark rerun is needed.
- The inspected diff changes no `_rustcore`, Cargo manifest/lock, generated
  Rust, native wheel/ABI, numerical formula, tolerance, reference, grid, seed,
  or solver constant.
- Production package code contains no direct `bianchi_rustcore` import and the
  historical `USE_RUST` markers are lazy; no import-time native probe was found
  in the declared route closure.
- Installed-payload file fingerprints, distribution ownership, typed
  fail-closed errors, and the explicit noisy development override are present
  in `bianchi/backend_policy.py:616-655` and `829-864`.
- Static inspection plus `logs/oracle_and_route_focus.log` (39 PASS) supports
  transitive explicit Python-oracle propagation through tilted initial state,
  RHS/exact/reference, Type-V, mixmaster, ray, and R5c focused paths.
- `logs/policy_optional_route.log` records 62 PASS. The workflow trigger set
  covers dispatch/package/lock/bootstrap changes and its focused selectors
  include tilted, Type-V, mixmaster, ray, and R5c; the remaining CI gap is the
  minimal-route import boundary in B2, not missing selector families.

No other confirmed blocker or scientific discrepancy was found in this single
bounded review round.
