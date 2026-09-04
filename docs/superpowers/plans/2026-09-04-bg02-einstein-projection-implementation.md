# BG-02 Einstein Projection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement one off-shell Einstein residual and its normal-normal, normal-spatial, spatial-trace, and spatial-PSTF projections in the BASS Wolfram/xAct package, then expose the derived expansion/shear rate adapters without projecting the state onto the Hamiltonian surface.

**Architecture:** The production module is a single BASS-owned `Background` package layered on the exact W2/W3 geometry APIs from PR #91. Every projection is derived from one tensor object \(E_{ab}=G_{ab}+\Lambda g_{ab}-\kappa_G T_{ab}\); homogeneous Bianchi dependence enters only through the existing locked connection and spatial-curvature generators. A Python/JSON registry audits identity, dependencies, dimensions, loader uniqueness, and claim boundaries, while native xTensor/xCoba and a compact homogeneous ONF oracle provide independent validation.

**Tech Stack:** Wolfram Language 15.x, xAct/xTensor 1.3.0, xCoba 0.8.6, Python 3.12 standard library, MUnit, Git/GitHub Actions.

**Spec:** `docs/bass_master_ssot_v2/BG_02/BG_02_IMPLEMENTATION_HANDOFF.md` at design authority commit `ef6d51aad709555737617e2021ba50c553c90b6c`; formula registry blob `88336e03f9761d8e8f75c92f705296abf9ce7725`.

## Global Constraints

- Code ancestry is exactly BASS PR #91 commit `80d271cc528e1a0ffa813ecd3e3fb7610f3fa755`, tree `3fd8818938eaa0988988c6927cff799455a7a31d`.
- PR #120 closeout commit `5ead8c5bcd9af6a37f9f8d7e7431e69887f34730` is a semantic dependency reference, not code ancestry.
- Metric signature is `(-,+,+,+)`.
- \(K_{ab}=+h_a{}^c h_b{}^d\nabla_c n_d=H_{\rm geom}h_{ab}+\sigma_{ab}\).
- Use `kappaG` or `kappa_G = 8 pi G/c^4`; bare `kappa` remains Thomson opacity.
- Preserve \(n^a\nabla_a=(1/c)d/dt\); do not silently adopt natural units.
- Keep physical normal acceleration \(A_a=n^b\nabla_b n_a\) distinct from Bianchi \(a^B_a\).
- Use `ONFRicciTensor` / `ONFScalarCurvature`, or `ConnectionToLockedGammaOrder[LeviCivitaConnection[a,n]]`; do not embed another Koszul formula.
- Keep every rate helper off shell. Never replace or mutate the state using \(\mathcal H=0\).
- Preserve the exceptional \(VI_{-1/9}\) carrier \(N_{22}\Sigma_{12}+(N_{23}-3A)\Sigma_{13}\).
- Every task is BASS-only. No REC, REI, or HTT source mutation is authorized.
- Constraint propagation, matter closure, numerical integration, provider admission, observables, likelihood, science promotion, RF04, and merge/ready transition remain outside this plan.

---

### Task 1: Preserve the exact expected RED

**Files:**
- Create: `docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_IMPLEMENTATION_RED_CONTRACT.json`
- Create: `docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_DESIGN_AUTHORITY_PIN.json`
- Create: `tests/test_bg02_einstein_projection_implementation.py`
- Create: `scripts/run_bg02_einstein_projection_red_local.sh`
- Create: `.github/workflows/bg02-einstein-projection-implementation.yml`

**Interfaces:**
- Consumes: exact PR #91 W2/W3 source files and PR #94 design IDs.
- Produces: a 18-method test contract whose expected RED is `2 passed / 16 failed / 0 errors`, caused only by absent production module and implementation registry.

- [ ] **Step 1: Add the test-only authority checks and missing-surface tests**

The two passing tests must pin the scientific parent and verify the existing loader has no Background implementation. The remaining sixteen tests must assert concrete future properties after first checking that these files exist:

```text
wolfram/BASS/Kernel/Background/EinsteinProjection.wl
docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_IMPLEMENTATION_REGISTRY.json
```

- [ ] **Step 2: Run the RED suite**

Run:

```bash
bash scripts/run_bg02_einstein_projection_red_local.sh \
  artifacts/bg02_einstein_projection_red
```

Expected:

```text
Ran 18 tests
FAILED (failures=16)
errors=0
status=PASS_EXPECTED_RED
wrapper exit code=0
```

- [ ] **Step 3: Commit RED source before any production code**

```bash
git add \
  docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION \
  tests/test_bg02_einstein_projection_implementation.py \
  scripts/run_bg02_einstein_projection_red_local.sh \
  .github/workflows/bg02-einstein-projection-implementation.yml
git commit -m "test(bg02): define Einstein projection implementation RED"
```

### Task 2: Add the production package and loader entry

**Files:**
- Create: `wolfram/BASS/Kernel/Background/EinsteinProjection.wl`
- Modify: `wolfram/BASS/Kernel/init.wl`
- Create: `docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_IMPLEMENTATION_REGISTRY.json`

**Interfaces:**
- Consumes: `BASS`Geometry`` W2/W3 symbols and the 14 PR #94 design formula IDs.
- Produces: one loadable `BASS`Background`` package and an implementation registry.

- [ ] **Step 1: Run only the loader/API tests and confirm they fail**

```bash
python3 -m unittest -v \
  tests.test_bg02_einstein_projection_implementation.BG02EinsteinProjectionImplementationTests.test_production_module_exists \
  tests.test_bg02_einstein_projection_implementation.BG02EinsteinProjectionImplementationTests.test_loader_imports_exactly_one_background_module \
  tests.test_bg02_einstein_projection_implementation.BG02EinsteinProjectionImplementationTests.test_required_public_api_names_are_exposed
```

Expected: three assertion failures caused by missing production source.

- [ ] **Step 2: Create the package header and public usages**

The package must expose exactly:

```wl
BeginPackage["BASS`Background`"];

EinsteinResidualTensor::usage = "...";
EinsteinProjectionRegistry::usage = "...";
HamiltonianProjection::usage = "...";
MomentumProjection::usage = "...";
SpatialTraceProjection::usage = "...";
SpatialPSTFProjection::usage = "...";
SpatialTraceRate::usage = "...";
ADMTraceRate::usage = "...";
RaychaudhuriRate::usage = "...";
ShearLieRate::usage = "...";
ShearProjectedRate::usage = "...";
```

Do not define a second connection or curvature implementation.

- [ ] **Step 3: Add exactly one loader entry**

Append one source to `wolfram/BASS/Kernel/init.wl`:

```wl
FileNameJoin[{root, "Background", "EinsteinProjection.wl"}]
```

The test must reject zero entries and duplicate entries.

- [ ] **Step 4: Add the implementation registry skeleton**

The registry must pin:
- scientific parent commit/tree;
- PR #94 design commit and formula-registry blob;
- all 14 formula IDs;
- every target dimension `L^-2`;
- claim boundary;
- required upstream geometry API names.

- [ ] **Step 5: Re-run focused tests and commit**

```bash
python3 -m unittest -v \
  tests.test_bg02_einstein_projection_implementation.BG02EinsteinProjectionImplementationTests.test_production_module_exists \
  tests.test_bg02_einstein_projection_implementation.BG02EinsteinProjectionImplementationTests.test_loader_imports_exactly_one_background_module \
  tests.test_bg02_einstein_projection_implementation.BG02EinsteinProjectionImplementationTests.test_required_public_api_names_are_exposed
git add wolfram/BASS/Kernel/Background/EinsteinProjection.wl \
        wolfram/BASS/Kernel/init.wl \
        docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_IMPLEMENTATION_REGISTRY.json
git commit -m "feat(bg02): add Einstein projection package surface"
```

### Task 3: Define one off-shell residual and four projections

**Files:**
- Modify: `wolfram/BASS/Kernel/Background/EinsteinProjection.wl`
- Test: `tests/test_bg02_einstein_projection_implementation.py`
- Test: `wolfram/BASS/Tests/BG02EinsteinProjectionImplementation.wlt`

**Interfaces:**
- Consumes: W2 normal/projector/kinematics and spacetime Einstein tensor.
- Produces:
  - `EinsteinResidualTensor[]`
  - `HamiltonianProjection[]`
  - `MomentumProjection[]`
  - `SpatialTraceProjection[]`
  - `SpatialPSTFProjection[]`

- [ ] **Step 1: Add failing tests for a single residual authority**

The source test must require one and only one definition equivalent to:

```wl
E[-a, -b] :=
  EinsteinTensorCD[-a, -b]
  + Lambda[] metric[-a, -b]
  - kappaG[] T[-a, -b]
```

Projection definitions must reference the residual function rather than rebuilding Einstein terms.

- [ ] **Step 2: Define the xTensor matter decomposition symbols**

Register \(\rho,p,q_a,\pi_{ab},\Lambda,\kappa_G\) with the required spatial, symmetric, trace-free constraints and exact dimensions. The implementation registry must preserve:

```text
[kappaG rho] = [kappaG p] = [kappaG q_a] = [kappaG pi_ab] = L^-2
```

- [ ] **Step 3: Derive the four projections from `E_ab`**

Implement:

\[
\mathcal H=n^an^bE_{ab},
\quad
\mathcal M_a=-h_a{}^cn^dE_{cd},
\quad
\mathcal T=\frac13h^{ab}E_{ab},
\quad
\mathcal S_{ab}=E_{\langle ab\rangle}.
\]

Canonicalize through xTensor. Do not substitute \(\mathcal H=0\).

- [ ] **Step 4: Assert reconstruction identities**

The MUnit suite must reconstruct the scalar, vector, trace, and PSTF pieces of the projected residual and verify zero exact residual after declared spatial/PSTF rules.

- [ ] **Step 5: Commit**

```bash
git add wolfram/BASS/Kernel/Background/EinsteinProjection.wl \
        tests/test_bg02_einstein_projection_implementation.py \
        wolfram/BASS/Tests/BG02EinsteinProjectionImplementation.wlt
git commit -m "feat(bg02): derive four projections from one residual"
```

### Task 4: Implement the 14-formula registry

**Files:**
- Modify: `wolfram/BASS/Kernel/Background/EinsteinProjection.wl`
- Modify: `docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_IMPLEMENTATION_REGISTRY.json`
- Create: `scripts/verify_bg02_einstein_projection_implementation.py`

**Interfaces:**
- Consumes: 14 design IDs and existing `BASS`IR`MakeEquationIR`.
- Produces: `EinsteinProjectionRegistry[]` and a fail-closed JSON verifier.

- [ ] **Step 1: Add failing uniqueness/dependency/dimension mutations**

The Python verifier must reject:
- one missing ID;
- a duplicate ID;
- a dangling dependency;
- a target dimension other than `L^-2`;
- scientific parent drift;
- use of bare `kappa` as GR coupling;
- a hand-entered branch equation.

- [ ] **Step 2: Construct every EquationIR record**

Use the exact 14 IDs pinned by PR #94. Dependencies must point to the composed W2/W3 geometry IDs and other BG-02 IDs, never to a Bianchi branch-specific formula table.

- [ ] **Step 3: Add semantic registry metadata**

Each record must include assumptions, derivative kind where relevant, dimensions, known limits, provenance, and the connection-route requirement.

- [ ] **Step 4: Run verifier and commit**

```bash
python3 scripts/verify_bg02_einstein_projection_implementation.py \
  --input docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_IMPLEMENTATION_REGISTRY.json
git add wolfram/BASS/Kernel/Background/EinsteinProjection.wl \
        docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_IMPLEMENTATION_REGISTRY.json \
        scripts/verify_bg02_einstein_projection_implementation.py
git commit -m "feat(bg02): register projection and rate formula identities"
```

### Task 5: Add homogeneous ONF adapters and connection-order guards

**Files:**
- Modify: `wolfram/BASS/Kernel/Background/EinsteinProjection.wl`
- Test: `wolfram/BASS/Tests/BG02EinsteinProjectionImplementation.wlt`

**Interfaces:**
- Consumes:
  - `BASS`Geometry`ONFRicciTensor`
  - `BASS`Geometry`ONFScalarCurvature`
  - `BASS`Geometry`ConnectionToLockedGammaOrder`
  - `BASS`Geometry`LeviCivitaConnection`
- Produces: homogeneous scalar-curvature and momentum adapters without duplicate geometry.

- [ ] **Step 1: Write the V/II connection-order negative tests**

Require the locked route to yield:

```text
Bianchi V    R3 = -6
Bianchi II   R3 = -1/2
```

and the deliberately wrong direct-order route to yield values different from both. The suite must explicitly reject an I+IX-only witness set as insufficient.

- [ ] **Step 2: Implement adapters by calling existing geometry APIs**

Source guards must fail if `EinsteinProjection.wl` contains another Koszul formula or a second `LeviCivitaConnection` body.

- [ ] **Step 3: Add I/V/II/IX positive controls**

Verify:

```text
I   0
V  -6
II -1/2
IX  3/2
```

- [ ] **Step 4: Commit**

```bash
git add wolfram/BASS/Kernel/Background/EinsteinProjection.wl \
        wolfram/BASS/Tests/BG02EinsteinProjectionImplementation.wlt
git commit -m "feat(bg02): bind projections to locked ONF curvature"
```

### Task 6: Add off-shell expansion and shear-rate adapters

**Files:**
- Modify: `wolfram/BASS/Kernel/Background/EinsteinProjection.wl`
- Test: `wolfram/BASS/Tests/BG02EinsteinProjectionImplementation.wlt`

**Interfaces:**
- Produces:
  - `SpatialTraceRate[]`
  - `ADMTraceRate[]`
  - `RaychaudhuriRate[]`
  - `ShearLieRate[]`
  - `ShearProjectedRate[]`

- [ ] **Step 1: Add failing tests for three distinct rate records**

The implementation must expose raw spatial-trace, trace-reversed ADM, and Raychaudhuri forms separately. A test must reject aliases that return one shared expression.

- [ ] **Step 2: Implement the three exact formulas**

\[
F_{\rm trace}
=-\frac{{}^{(3)}R}{12}-\frac32H^2-\frac14\sigma^2
+\frac13(D\!\cdot\!A+A^2)+\frac12\Lambda-\frac12\kappa_Gp,
\]

\[
F_{\rm ADM}
=-\frac{{}^{(3)}R}{3}-3H^2+\frac13(D\!\cdot\!A+A^2)
+\frac{\kappa_G}{2}(\rho-p)+\Lambda,
\]

\[
F_{\rm Ray}
=-H^2-\frac13\sigma^2+\frac13(D\!\cdot\!A+A^2)
-\frac{\kappa_G}{6}(\rho+3p)+\frac{\Lambda}{3}.
\]

- [ ] **Step 3: Verify the off-shell identities**

\[
F_{\rm ADM}-F_{\rm trace}+\frac12\mathcal H=0,
\]

\[
F_{\rm trace}-F_{\rm Ray}+\frac16\mathcal H=0,
\]

\[
F_{\rm ADM}-F_{\rm Ray}+\frac23\mathcal H=0.
\]

Tests must fail if the implementation substitutes \(\mathcal H=0\).

- [ ] **Step 4: Implement derivative-typed shear rates**

Store metadata:

```text
ShearLieRate       derivative_kind = LIE_DERIVATIVE_PSTF
ShearProjectedRate derivative_kind = PROJECTED_COVARIANT_NORMAL_DERIVATIVE
```

and verify the exact adapter identity.

- [ ] **Step 5: Commit**

```bash
git add wolfram/BASS/Kernel/Background/EinsteinProjection.wl \
        wolfram/BASS/Tests/BG02EinsteinProjectionImplementation.wlt
git commit -m "feat(bg02): add off-shell expansion and shear rates"
```

### Task 7: Add known limits and exceptional momentum witness

**Files:**
- Modify: `wolfram/BASS/Tests/BG02EinsteinProjectionImplementation.wlt`
- Modify: `tests/test_bg02_einstein_projection_implementation.py`

**Interfaces:**
- Consumes: production projection/rate APIs.
- Produces: exact limits and adversarial guards.

- [ ] **Step 1: Add flat FLRW and de Sitter tests**

Flat FLRW must recover:

\[
3H^2=\kappa_G\rho+\Lambda,
\qquad
\mathcal L_nH=-\frac{\kappa_G}{2}(\rho+p).
\]

Flat de Sitter must give all three rates zero.

- [ ] **Step 2: Add Kasner vacuum**

With \(\tau=ct\),

\[
H=\frac1{3\tau},
\qquad
\sigma^2=\frac2{3\tau^2},
\]

require:

```text
Hres = 0
F_trace = F_ADM = F_Ray = -1/(3 tau^2)
```

- [ ] **Step 3: Add the exceptional \(VI_{-1/9}\) carrier**

Require exact residual zero for:

\[
D^b\sigma_{3b}
-
\left[N_{22}\Sigma_{12}+(N_{23}-3A)\Sigma_{13}\right].
\]

A mutation deleting \(\Sigma_{13}\) must fail.

- [ ] **Step 4: Commit**

```bash
git add tests/test_bg02_einstein_projection_implementation.py \
        wolfram/BASS/Tests/BG02EinsteinProjectionImplementation.wlt
git commit -m "test(bg02): lock limits and exceptional momentum carrier"
```

### Task 8: Build and replay the complete native xAct source packet

**Files:**
- Create: `wolfram/scripts/run_bg02_einstein_projection_native.wls`
- Create: `scripts/build_bg02_einstein_projection_source_packet.py`
- Create: `scripts/run_bg02_einstein_projection_local.sh`
- Modify: `.github/workflows/bg02-einstein-projection-implementation.yml`

**Interfaces:**
- Consumes: all parent Authority/IR/Bianchi/Geometry sources, production Background source, tests, schemas, and registry.
- Produces: exact source packet, native receipt, local summary, and SHA-256 manifests.

- [ ] **Step 1: Make the packet manifest fail on omissions**

The packet builder must require every parent file from the PR #91 34-file source manifest plus the new BG-02 files. Omitting `Abstract1Plus3.wl`, `ONFConnectionCurvature.wl`, `XCobaCurvatureWitnesses.wl`, or the production module must fail.

- [ ] **Step 2: Run native package registration**

The Wolfram runner must require:

```text
xTensor 1.3.0
xCoba 0.8.6
zero failed
zero not evaluated
```

It must execute the inherited W2/W3 suites and all BG-02 tests in a fresh kernel.

- [ ] **Step 3: Preserve strict JSON receipts**

Write to a temporary path, re-import as `RawJSON`, verify exact fields, atomically rename, and require a nonempty final file.

- [ ] **Step 4: Run full local validation**

```bash
bash scripts/run_bg02_einstein_projection_local.sh \
  artifacts/bg02_einstein_projection
```

Required result:

```text
Python implementation tests 18/18
MUnit BG-02 tests           26/26
all inherited source suites PASS
failed/not evaluated         0/0
native xTensor/xCoba         PASS
SHA256SUMS                   PASS
exit code                       0
```

- [ ] **Step 5: Commit exact source and replay artifacts separately**

```bash
git add scripts wolfram docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION
git commit -m "test(bg02): add complete native xAct replay"
```

### Task 9: Independent audit and bounded publication

**Files:**
- Create: `docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_PHYS_MATH_AUDIT.md`
- Create: `docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_PHYS_MATH_CODE_AUDIT.md`
- Create: `docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_LOCAL_EXACT_REPLAY_CLOSEOUT.json`
- Create: `docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/SHA256SUMS.portable.txt`

**Interfaces:**
- Consumes: exact GREEN source head and native replay artifacts.
- Produces: a bounded implementation closeout without constraint-propagation or numerical-evolution claims.

- [ ] **Step 1: Run PHYS-MATH review**

Audit signs, dimensions, projection definitions, off-shell identities, FLRW/de Sitter/Kasner limits, and \(VI_{-1/9}\) carrier.

- [ ] **Step 2: Run PHYS-MATH-CODE review**

Audit single residual authority, no second Koszul, loader uniqueness, derivative metadata, fail-closed receipts, exact source packet, and no unauthorized cross-repository mutation.

- [ ] **Step 3: Perform plot-driven adversarial diagnostics**

Plot normalized:

\[
\frac{F_{\rm ADM}-F_{\rm trace}}{H^2},
\quad
\frac{F_{\rm trace}-F_{\rm Ray}}{H^2},
\quad
\frac{F_{\rm ADM}-F_{\rm Ray}}{H^2}
\]

against their exact Hamiltonian-residual predictions. The plots are diagnostics, not replacements for exact identities.

- [ ] **Step 4: Seal the exact bytes**

Copy native receipts into Git, create a portable SHA-256 manifest, verify it, and commit.

- [ ] **Step 5: Preserve the claim ceiling**

The final closeout may claim:

```text
BG02_PRODUCTION_PROJECTION_APIS_IMPLEMENTED
BG02_NATIVE_XACT_XCOBA_REPLAY_PASS
BG02_OFF_SHELL_RATE_IDENTITIES_PASS
BG02_CONNECTION_ORDER_GUARDS_PASS
BG02_EXCEPTIONAL_MOMENTUM_CARRIER_PASS
```

It must not claim:

```text
CONSTRAINT_PROPAGATION_VERIFIED
BACKGROUND_NUMERICAL_EVOLUTION
MATTER_DYNAMICS_CLOSED
ALL_FAMILY_BACKGROUND_READY
PROVIDER_ADMISSION
OBSERVABLE_READY
LIKELIHOOD_READY
SCIENCE_VALIDITY
PASS_RF04
```

- [ ] **Step 6: Commit bounded closeout**

```bash
git add docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION
git commit -m "docs(bg02): seal production projection implementation"
```
