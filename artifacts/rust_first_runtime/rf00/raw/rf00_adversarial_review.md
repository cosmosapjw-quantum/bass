# RF-00 independent adversarial review

- Review range: `0cdcdbf20c867e9e29ef68ed1849f97d8af44ac4..d95ba12331e8677f23b4f22bfd03328f1c5bf4c0`
- Candidate tree: `bcc140a10e6a16edae69b5fbba959fa0270adcf3`
- Authority read: `docs/rust_first_runtime/SPEC.json`, especially RF-00 lines 664-686 and backend policy lines 354-409.
- Method: one read-only diff/source/evidence review. No tests, builds, benchmarks, Wolfram commands, staging, commits, or remote mutations were performed.
- Verdict: **BLOCKER**. Five RF-00 acceptance blockers remain.

## Findings

### BLOCKER B1 — explicit Python oracle is transitively native on supported inputs

Evidence:

- `bianchi/backend.py:240-243` sends the facade's explicit oracle path to `hierarchy.J_moment(...)` without `backend="python"`.
- `bianchi/matter/hierarchy.py:190-216` defaults that nested call back through `select_backend`, so supported `(l,i,f0)` domains execute Rust.
- `bianchi/backend.py:294-300` calls `integrate_hierarchy` for the explicit hierarchy oracle, while `bianchi/matter/hierarchy.py:518,530-532` initializes and diagnoses it with default-policy `J_moment` calls.
- The same composition defect occurs for derived transport: `bianchi/backend.py:377-399` enters the Python module, but `bianchi/matter/viscous_derived.py:82,115,119,136` calls default-policy `H.J_moment`.
- `tests/test_backend_integration.py:98-108` compares values but does not prove that the oracle side avoided the native module. It can therefore pass as Rust-versus-Rust.

Impact: RF-00 requires an independent, explicit Python oracle (`SPEC.json:346,370-373,681`). The current contract can conceal a native defect on precisely the differential paths intended to expose it.

Smallest fix: propagate one explicit oracle child policy through every nested call in these facade routes. At minimum, pass `backend="python"` in `backend.j_moment`; add a backend/oracle parameter to `integrate_hierarchy` and the derived-transport helpers, and propagate it to every nested `J_moment` call. Do not change formulas or tolerances.

Smallest affected proof: inject a native module whose numerical symbols raise, then call the explicit oracle forms of `backend.j_moment`, a very small collisionless `backend.hierarchy_integrate`, `backend.transport_coefficients`, and `backend.viscous_cross_validate`; require correct finite Python results and zero native calls. Retain one native-result control for each changed facade family.

### BLOCKER B2 — a committed native route bypasses the typed policy matrix

Evidence:

- `bianchi/backend_policy.py:304` declares `q.polstate.collide_modeb` as a native-capable route.
- `bianchi/q/polstate.py:261-279` never calls `select_backend`: only the exact string `"python"` selects the oracle; every other value, including a typo, directly imports and invokes `bianchi_rustcore`.

Impact: this public selection-bearing route does not provide typed missing/ABI errors, cannot be governed by the committed matrix, and silently treats an unknown policy as Rust. The matrix is descriptive rather than authoritative for this route.

Smallest fix: preserve the public `backend="rust"|"python"` compatibility surface, map it explicitly to `RUST_REQUIRED`/`PYTHON_ORACLE`, reject every unknown value with `BackendPolicyError`, and use `select_backend("q.polstate.collide_modeb", ...)` before dispatch.

Smallest affected proof: focused cases for explicit Python with zero native probes; missing extension; incompatible extension; unknown selector; and unchanged installed native output. Add `bianchi/q/polstate.py` and its focused test to the RF-00 workflow path/test closure.

### BLOCKER B3 — a Python shadow can be accepted as native and falsely bound to installed r2

Evidence:

- `bianchi/backend_policy.py:310-323` returns no native origin for a pure-Python module.
- `bianchi/backend_policy.py:359-379` performs ABI checks only when an origin was found, then returns `AVAILABLE` even when `origin is None`.
- `bianchi/backend_policy.py:577-594` fingerprints files located from installed distribution metadata independently of the module actually imported.
- `bianchi/backend_policy.py:620-625` sets `r2_bound` from loader availability, version, and that independent fingerprint, without binding the loaded shared-object origin to the fingerprinted distribution file.

Impact: a `PYTHONPATH` shadow/wrapper with the expected symbols can be executed as “Rust”; if a genuine r2 distribution is also installed elsewhere, the capability report can state `installed_native_r2_verified=true` for bytes that are not the executing module. This violates fail-closed native identity and provenance honesty.

Smallest fix: require a real extension-module origin (including the supported nested maturin layout) for `AVAILABLE`; bind the actual loaded shared-object resolved path and digest to the corresponding distribution-owned file before setting any r2-derived fields. Keep direct-URL archive metadata explicitly distinct from observed wheel archive bytes.

Smallest affected proof: pure-Python top-level shadow; pure-Python wrapper shadowing an installed distribution; nested maturin extension with matching origin; mismatched nested ABI suffix; and genuine installed-r2 origin/hash binding. The first two must fail typed and must never report r2 verified.

### BLOCKER B4 — an inherited integrated Rust/Python proof became vacuous

Evidence:

- `bianchi/matter/tilted_terms.py:37-38` states that `USE_RUST` is diagnostic only and numerical dispatch never reads it.
- `tests/test_r5a_tilted_terms_rust.py:90-100` still toggles `TT.USE_RUST` and labels the resulting two calls as Rust and Python trajectories. Both calls now follow the same path, so bit equality proves nothing.

Impact: the RF-00 dispatch edit invalidated this proof without replacing it. Simply changing the test to the R5b Python backend would also resurrect the retired cancellation-sensitive endpoint error-scalar equality and would violate the closed R5b contract.

Smallest fix: remove the obsolete global-toggle trajectory assertion and replace it with a direct, stable supported-operator/no-fallback proof using explicit typed selection. Do not introduce an endpoint error-of-error comparator or change any numerical threshold.

Smallest affected proof: the replacement R5a test plus the existing focused `tilted_terms` operator parity cases only. Reuse the closed R5b state/operator/science receipt; do not rerun or rewrite it.

### BLOCKER B5 — capability report labels configured environment as actual thread-pool size

Evidence:

- `bianchi/backend_policy.py:597-607` reads only `RAYON_NUM_THREADS`; without it the value is `None`, and after global Rayon initialization it can differ from the actual pool.
- `bianchi/backend_policy.py:666,681,715,731` reports that value as `rayon_threads` and `thread_pool_size`.
- RF-00 requires the field (`SPEC.json:396-408,672`), and RISK-07 stops when pool identity or size is absent (`SPEC.json:1248-1253`).

Impact: a normal environment can report no pool size, while a changed environment can report a value that is not the initialized runtime. This is configuration intent, not a runtime capability receipt.

Smallest fix: expose actual Rayon pool identity/size from the loaded extension (for example, a narrow PyO3 runtime-capability call using the runtime's effective thread count) and label environment configuration separately. If native/PyO3 bytes change, apply the required r3 artifact rule; r2 cannot cover those bytes.

Smallest affected proof: fresh subprocess receipts with the environment unset and with two predeclared thread settings, requiring non-null effective size and honest configured-versus-effective fields. Then run only the native change closure mandated by the task (locked/offline Cargo test, focused native policy proof, wheel build/import) and produce r3.

## Challenged areas without an RF-00 blocker

### NON_BLOCKER N1 — module-global fast path

`bianchi/backend.py:50-70,91-100` prebinds a complete module and bypasses per-call selection for the default path. For a fixed process, a genuinely loaded compatible extension cannot subsequently become missing or ABI-incompatible; cold-import failure leaves the cache empty and reaches typed selection. The test reset seam does not reset `_FACADE_NATIVE`, so injected post-import missing-module tests cannot establish default-path behavior. After B3 binds real extension identity, add one fresh-process cold-import default-path case rather than adding per-call overhead.

### NON_BLOCKER N2 — nested maturin/build version metadata

The supported bootstrap and CI entry points pin maturin 1.14.1 (`bootstrap.sh:50-54`, `.github/workflows/rf00-backend-policy.yml:27-29,71-83`), and pip enforces the built wheel tag. `_rustcore/pyproject.toml:2` remains a broad PEP-517 build declaration, but the documentation does not nominate direct isolated PEP-517 building as the unified entry point. `bootstrap.sh:38-45` should also check `cargo 1.94.1`, because maturin invokes the PATH cargo; this is hardening unless that helper is declared an exact reproduction authority.

### NON_BLOCKER N3 — root package discovery/data

`pyproject.toml:16-21` includes the runtime packages and both non-Python runtime payloads found under `bianchi/` (`gaunt_tables.npz`, `riemann_frame.pkl`). The exact native distribution dependency is present at `pyproject.toml:10-14`; no package-data omission was found.

### NON_BLOCKER N4 — workflow download boundary and trigger breadth

Network resolution is confined to setup/build steps (`.github/workflows/rf00-backend-policy.yml:47-48,71-92`); proof steps set `PIP_NO_INDEX=1` and native Cargo offline (`:49-57,93-102`). The path filter omits several dispatch-bearing modules, so include every file repaired for B1/B2/B4; this is needed for those repairs but no hidden test-time download was found.

### NON_BLOCKER N5 — native-r2 reuse predicate at the reviewed candidate

The committed diff does not change Cargo manifests/lock/config/vendor, Rust/generated Rust/PyO3, wheel, ABI, toolchain, or native fixture bytes. The candidate's present mechanical conclusion `REUSED_NATIVE_R2_NO_R3` is valid. B5's smallest complete repair would change PyO3/native bytes and would therefore invalidate that conclusion and require r3.

### NON_BLOCKER N6 — benchmark, secrets, and scope

The benchmark is non-default, compares the exact paired refs with a shared native payload, and makes no Candidate-B speedup claim. `git diff --check` was clean; a targeted credential/key/token-pattern review found no candidate secret. No formula, tolerance, reference, Cargo lock, generated Rust, or Wolfram execution change appears in the reviewed commit.

## Review close

Decision: `CONTINUE_CHANGED_CELL`. Repair B1-B5 within the single allowed repair-closeout, rerun only the affected proof named above, and do not request a second independent review round.
