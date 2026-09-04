# BG-02 Native Gauss–Codazzi Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current component-only BG-02 oracle with one actual xTensor Einstein residual whose four 1+3 projections are proven equal to the PR #94 component formulas under the exact PR #91 Gauss–Codazzi sign conventions.

**Architecture:** Keep the current scalar/component formulas as a separately labelled oracle. Add a native xTensor layer that registers matter and residual tensors on the W2 spacetime, proves structural projector identities, applies executable Gauss/Codazzi/Ricci projection rules, and emits four native-minus-component residuals. Native xAct is the primary gate; SymPy, mpmath, Octave, SageMath, Singular and Lean are independent corroboration lanes and cannot prevent the native receipt from being collected.

**Tech Stack:** Wolfram Language 15.0, xAct/xTensor 1.3.0, xCoba 0.8.6, xPerm 1.2.4, Python 3.12 standard library, MUnit, optional SymPy/mpmath/Octave/SageMath/Singular/Lean 4 + Mathlib.

**Spec:** `docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_ADVERSARIAL_AUDIT_20260904.md` and PR #94 `docs/bass_master_ssot_v2/BG_02/BG_02_IMPLEMENTATION_HANDOFF.md` at commit `ef6d51aad709555737617e2021ba50c553c90b6c`.

## Global Constraints

- Scientific code ancestry is PR #91 commit `80d271cc528e1a0ffa813ecd3e3fb7610f3fa755`, tree `3fd8818938eaa0988988c6927cff799455a7a31d`.
- Metric signature is `(-,+,+,+)`.
- `K_ab = +h_a^c h_b^d nabla_c n_d = H_geom h_ab + sigma_ab`.
- `q_a = -h_a^c T_cd n^d`.
- `kappa_G = 8 pi G/c^4`; bare `kappa` remains reserved for opacity.
- The geometric derivative is `nabla_n`; physical time is a separate adapter satisfying `nabla_n=(1/c)d/dt`.
- Physical normal acceleration `A_a` and Bianchi structure vector `a_B_a` are distinct typed objects.
- Production curvature uses only PR #91 geometry APIs. Wrong-order and mutation routes are test-only.
- No rate helper may substitute `Hres -> 0` or mutate the state onto a constraint surface.
- Native xAct execution is never serially blocked by optional auxiliary CAS tools.
- No merge, ready-for-review transition, provider admission, numerical evolution, science promotion or RF04 claim is authorized by this plan.

---

### Task 1: Establish the adversarial RED and correct the claim surface

**Files:**
- Create: `tests/test_bg02_native_bridge_adversarial.py`
- Modify: `docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_IMPLEMENTATION_REGISTRY.json`
- Modify: PR #124 title/body only; keep Draft

**Interfaces:**
- Consumes: current PR #124 component source.
- Produces: a named RED contract that rejects component-oracle promotion.

- [ ] **Step 1: Write RED tests for the present P0/P1 defects**

The tests must reject all of the following source patterns:

```python
FORBIDDEN = [
    'EinsteinResidualTensor[vars_:Automatic] := residualComponents',
    '"dependency_graph_closed"->True',
    '"single_off_shell_residual_authority"->True',
    '"second_koszul_implementation_absent"->True',
    'TrueQ[A_normal=!=a_B]',
    '(N22 Sigma12+(N23-3 A)Sigma13)-('
]
```

They must also reject `wrongOrderScalarCurvature` in the production module, `state[_] := <||>`, and `Lookup[..., r]` fallbacks that return an association instead of `Failure`.

- [ ] **Step 2: Run the RED**

```bash
python3 -S -m unittest -v tests.test_bg02_native_bridge_adversarial
```

Expected: failures proving the current implementation is component-only and circular. Record the exact failing test IDs; do not freeze an arbitrary failure count.

- [ ] **Step 3: Correct registry status without claiming implementation**

Set:

```json
{
  "status": "COMPONENT_ORACLE_ONLY_NATIVE_XTENSOR_BRIDGE_REQUIRED",
  "implementation_layer": "COMPONENT_FORMULA_ORACLE",
  "native_tensor_api_admitted": false
}
```

- [ ] **Step 4: Commit**

```bash
git add tests/test_bg02_native_bridge_adversarial.py \
  docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_IMPLEMENTATION_REGISTRY.json
git commit -m "test(bg02): reject component-oracle promotion"
```

### Task 2: Split the component oracle from the native tensor API

**Files:**
- Create: `wolfram/BASS/Kernel/Background/EinsteinProjectionComponentOracle.wl`
- Create: `wolfram/BASS/Kernel/Background/EinsteinProjectionXTensorBridge.wl`
- Modify: `wolfram/BASS/Kernel/Background/EinsteinProjection.wl`
- Modify: `wolfram/BASS/Kernel/init.wl`

**Interfaces:**
- Produces: `BASS`Background`EinsteinProjectionComponentOracle` and a native bridge package surface.

- [ ] **Step 1: Move the existing scalar/component formulas unchanged**

Expose a component oracle association with explicit metadata:

```wl
<|
  "representation" -> "COMPONENT_FORMULA_ORACLE",
  "native_xtensor_equivalent" -> False,
  "HamiltonianProjection" -> ...,
  "MomentumProjection" -> ...,
  "SpatialTraceProjection" -> ...,
  "SpatialPSTFProjection" -> ...
|>
```

Malformed associations return `Failure["InvalidBG02State", ...]`. Missing required keys return `Failure["MissingBG02Component", ...]`.

- [ ] **Step 2: Make the facade fail closed until the native layer is loaded**

The public `EinsteinResidualTensor` must no longer be implemented by the component association. Before native registration it returns:

```wl
Failure["NativeXTensorResidualUnavailable", <|
  "component_oracle_available" -> True,
  "native_bridge_status" -> "PENDING"
|>]
```

- [ ] **Step 3: Load one component source and one native bridge source exactly once**

The loader must contain one entry for each new file and no duplicate Background source.

- [ ] **Step 4: Run focused tests and commit**

```bash
python3 -S -m unittest -v \
  tests.test_bg02_native_bridge_adversarial.BG02NativeBridgeAdversarialTests.test_tensor_api_is_not_component_association \
  tests.test_bg02_native_bridge_adversarial.BG02NativeBridgeAdversarialTests.test_state_and_lookup_fail_closed
git add wolfram/BASS/Kernel/Background wolfram/BASS/Kernel/init.wl
git commit -m "refactor(bg02): separate component oracle from tensor bridge"
```

### Task 3: Register the actual xTensor residual and structural projections

**Files:**
- Modify: `wolfram/BASS/Kernel/Background/EinsteinProjectionXTensorBridge.wl`
- Create: `wolfram/BASS/Tests/BG02EinsteinProjectionStructural.wlt`

**Interfaces:**
- Consumes: `CreateAbstract1Plus3Geometry[]`, `BASSW2metric`, `BASSW2CD`, `BASSW2n`.
- Produces: one native residual expression and four native projection expressions.

- [ ] **Step 1: Add failing structural MUnit tests**

Require exact tests for:

```text
n^a n_a = -1
h_a^b n_b = 0
h_a^c h_c^b = h_a^b
h_a^a = 3
n^a M_a = 0
n^a S_ab = 0
h^ab S_ab = 0
S_[ab] = 0
E_ab reconstruction residual = 0
```

- [ ] **Step 2: Register matter and coupling objects**

Use unique BG-02 symbols on `BASSW2M4`:

```wl
BASSBG02T[-w2a,-w2b]
BASSBG02Lambda[]
BASSBG02KappaG[]
```

`BASSBG02T` is symmetric. `Lambda` and `kappaG` are scalars.

- [ ] **Step 3: Define the residual as an expression, not an independent free tensor**

```wl
EinsteinResidualTensor[-a_, -b_] :=
  EinsteinBASSW2CD[-a,-b]
  + BASSBG02Lambda[] BASSW2metric[-a,-b]
  - BASSBG02KappaG[] BASSBG02T[-a,-b]
```

- [ ] **Step 4: Define the projector and four projections**

```wl
h[-a_, b_] := delta[-a,b] + BASSW2n[-a] BASSW2n[b]
HNative[] := BASSW2n[a] BASSW2n[b] EinsteinResidualTensor[-a,-b]
MNative[-a_] := -h[-a,b] BASSW2n[c] EinsteinResidualTensor[-b,-c]
TNative[] := h[a,b] EinsteinResidualTensor[-a,-b]/3
SNative[-a_,-b_] := h[-a,c] h[-b,d] EinsteinResidualTensor[-c,-d]
  - TNative[] h[-a,-b]
```

Canonicalize with `Expand`, `ContractMetric`, and `ToCanonical` under the W2 normal/projector rules.

- [ ] **Step 5: Run structural replay and commit**

```bash
wolframscript -file wolfram/scripts/run_bg02_structural_projection.wls
```

Expected: all named structural residuals exactly zero; no Gauss–Codazzi claim yet.

### Task 4: Prove matter and cosmological-constant projection signs

**Files:**
- Modify: `wolfram/BASS/Kernel/Background/EinsteinProjectionXTensorBridge.wl`
- Modify: `wolfram/BASS/Tests/BG02EinsteinProjectionStructural.wlt`

**Interfaces:**
- Produces: exact decomposition rules for `rho`, `q_a`, `p`, and `pi_ab`.

- [ ] **Step 1: Add RED tests for the decomposition**

With

```text
T_ab = rho n_a n_b + 2 n_(a q_b) + p h_ab + pi_ab,
```

require `q_a` and `pi_ab` spatial, `pi^a_a=0`, and `pi_[ab]=0`.

- [ ] **Step 2: Verify the matter contribution**

For `-kappa_G T_ab`, require native projection residuals:

```text
Hamiltonian  + kappa_G rho = 0
Momentum     + kappa_G q_a = 0
Trace        + kappa_G p = 0
PSTF         + kappa_G pi_ab = 0
```

- [ ] **Step 3: Verify the Lambda contribution**

For `Lambda g_ab`, require:

```text
Hamiltonian + Lambda = 0
Momentum = 0
Trace - Lambda = 0
PSTF = 0
```

- [ ] **Step 4: Commit**

```bash
git add wolfram/BASS/Kernel/Background/EinsteinProjectionXTensorBridge.wl \
  wolfram/BASS/Tests/BG02EinsteinProjectionStructural.wlt
git commit -m "test(bg02): prove matter and Lambda projection signs"
```

### Task 5: Implement executable Gauss–Codazzi/Ricci bridge rules

**Files:**
- Create: `wolfram/BASS/Kernel/Geometry/GaussCodazziProjectionRules.wl`
- Create: `wolfram/BASS/Tests/BG02GaussCodazziProjectionRules.wlt`
- Modify: `wolfram/BASS/Kernel/Background/EinsteinProjectionXTensorBridge.wl`
- Modify: `wolfram/BASS/Kernel/init.wl`

**Interfaces:**
- Consumes: PR #91 W2 equation IDs `W2-CURV-001..003` and the W2 kinematic model.
- Produces: typed replacement rules for projected Einstein curvature terms.

- [ ] **Step 1: Pin the exact W2 sign coefficients**

Fail unless the W2 registry contains:

```text
Gauss:              R3_abcd + K_ac K_bd - K_ad K_bc
Codazzi:            D_a K_bc - D_b K_ac
Contracted scalar:  R3 = R4 + 2 R_nn + K_ab K^ab - K^2
```

- [ ] **Step 2: Define typed geometric placeholders**

Register spatial scalar curvature, spatial Ricci PSTF, spatial derivative of `K_ab`, normal acceleration, and Lie derivative objects with their symmetries and dimensions. Do not represent them as untyped global symbols.

- [ ] **Step 3: Generate four bridge expressions**

Derive rather than retype the final formulas:

```text
Delta_H    = HNative - HComponent
Delta_M_a  = MNative_a - MComponent_a
Delta_T    = TNative - TComponent
Delta_S_ab = SNative_ab - SComponent_ab
```

Use the W2 coefficient registry to construct the replacement rules and record the source equation IDs in every receipt.

- [ ] **Step 4: Add mutation tests**

Each of these must make at least one bridge residual nonzero:

```text
flip Gauss K_ac K_bd coefficient
flip Codazzi orientation
remove A_<a A_b>
replace Lie derivative by projected derivative without adapter
change q_a sign
```

- [ ] **Step 5: Commit**

```bash
git add wolfram/BASS/Kernel/Geometry/GaussCodazziProjectionRules.wl \
  wolfram/BASS/Tests/BG02GaussCodazziProjectionRules.wlt \
  wolfram/BASS/Kernel/Background/EinsteinProjectionXTensorBridge.wl \
  wolfram/BASS/Kernel/init.wl
git commit -m "feat(bg02): derive native Gauss-Codazzi projection bridge"
```

### Task 6: Add homogeneous ONF and exceptional VI_-1/9 dual witnesses

**Files:**
- Create: `wolfram/BASS/Tests/BG02HomogeneousDualWitnesses.wlt`
- Modify: `wolfram/BASS/Kernel/Background/EinsteinProjectionXTensorBridge.wl`

**Interfaces:**
- Consumes: `ONFRicciTensor`, `ONFScalarCurvature`, locked connection-order adapter.
- Produces: independent homogeneous component witnesses.

- [ ] **Step 1: Move all wrong-order calculations out of production**

Delete `wrongOrderScalarCurvature` from the production module. Recreate the wrong-order route only inside the test file.

- [ ] **Step 2: Verify I/V/II/IX scalar curvature**

```text
I = 0
V = -6
II = -1/2
IX = 3/2
```

Require V and II to reject the deliberately wrong storage order.

- [ ] **Step 3: Derive the exceptional momentum carrier**

Specialize the native momentum projection to the exceptional `VI_-1/9` branch and require its third component to reduce to

```text
N22 Sigma12 + (N23 - 3 A) Sigma13.
```

Delete `Sigma13` in a mutant and require a nonzero residual.

- [ ] **Step 4: Commit**

```bash
git add wolfram/BASS/Kernel/Background/EinsteinProjectionXTensorBridge.wl \
  wolfram/BASS/Tests/BG02HomogeneousDualWitnesses.wlt
git commit -m "test(bg02): add homogeneous and exceptional dual witnesses"
```

### Task 7: Refactor execution and receipts around the primary physics gate

**Files:**
- Create: `scripts/run_bg02_native_xact_diagnostic_local.sh`
- Create: `scripts/run_bg02_auxiliary_cas_audit_local.sh`
- Modify: `wolfram/scripts/run_bg02_einstein_projection_native.wls`
- Create: `tests/test_bg02_execution_transition_contract.py`

**Interfaces:**
- Produces: independent native and auxiliary receipts.

- [ ] **Step 1: Test that auxiliary CAS cannot block native execution**

Use fake Sage/Singular/Lean executables that timeout or fail. The native runner must still execute and publish its own receipt.

- [ ] **Step 2: Activate pinned xAct before full BASS init**

Load `Authority/Environment.wl`, call `ActivatePinnedXAct`, load xCoba explicitly, then load full `init.wl`. Verify `$Packages`, exact versions, and real definitions.

- [ ] **Step 3: Route every exit through one atomic writer**

Every result, including activation and package failures, writes temporary strict JSON, re-imports it, verifies the observed values, and atomically renames it.

- [ ] **Step 4: Replace count-only admission with named-test admission**

Record:

```text
required_test_ids
observed_test_ids
failed_test_ids
not_evaluated_test_ids
required_test_id_hash
```

Final native admission requires exact ID-set equality, no failures, no not-evaluated tests, and all four bridge residuals zero.

- [ ] **Step 5: Commit**

```bash
git add scripts/run_bg02_native_xact_diagnostic_local.sh \
  scripts/run_bg02_auxiliary_cas_audit_local.sh \
  wolfram/scripts/run_bg02_einstein_projection_native.wls \
  tests/test_bg02_execution_transition_contract.py
git commit -m "fix(bg02): decouple native xAct from auxiliary CAS"
```

### Task 8: Add proper-length/physical-time adapter and dimensional checks

**Files:**
- Create: `wolfram/BASS/Kernel/Background/PhysicalTimeAdapter.wl`
- Create: `wolfram/BASS/Tests/BG02PhysicalTimeAdapter.wlt`
- Modify: `docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_IMPLEMENTATION_REGISTRY.json`

**Interfaces:**
- Consumes: geometric rates with dimension `L^-2`.
- Produces: explicitly named `d/dt` rates.

- [ ] **Step 1: Keep native geometric rates unchanged**

`SpatialTraceRate`, `ADMTraceRate`, `RaychaudhuriRate`, and shear rates remain `nabla_n` quantities.

- [ ] **Step 2: Add explicit conversion**

For any scalar geometric rate `F = nabla_n H`, expose

```text
dH/dt = c F.
```

For tensor rates, apply the same single factor of `c` after fixing derivative kind.

- [ ] **Step 3: Add dimension tests and commit**

```bash
git add wolfram/BASS/Kernel/Background/PhysicalTimeAdapter.wl \
  wolfram/BASS/Tests/BG02PhysicalTimeAdapter.wlt \
  docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_IMPLEMENTATION_REGISTRY.json
git commit -m "feat(bg02): add explicit physical-time adapter"
```

### Task 9: Full native replay, dual audit and bounded closeout

**Files:**
- Create: `docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_PHYS_MATH_AUDIT.md`
- Create: `docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_PHYS_MATH_CODE_AUDIT.md`
- Create: `docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_NATIVE_CLOSEOUT.json`

**Interfaces:**
- Consumes: exact bridge source and all receipts.
- Produces: implementation-only closeout.

- [ ] **Step 1: Run native xAct first**

```bash
bash scripts/run_bg02_native_xact_diagnostic_local.sh \
  artifacts/bg02_native_xact
```

Required: exact test-ID set; failed/not-evaluated empty; structural and four bridge residuals zero; V/II and VI_-1/9 witnesses pass.

- [ ] **Step 2: Run auxiliary CAS independently**

```bash
bash scripts/run_bg02_auxiliary_cas_audit_local.sh \
  artifacts/bg02_auxiliary_cas
```

A failed optional lane blocks only its corresponding corroboration claim, not the already collected native receipt.

- [ ] **Step 3: Run PHYS-MATH audit**

Audit signs, dimensions, reconstruction, Gauss/Codazzi/Ricci coefficients, FLRW/de Sitter/Kasner limits, acceleration terms, matter projections and exceptional branch.

- [ ] **Step 4: Run PHYS-MATH-CODE audit**

Audit source authority, absence of hard-coded positive gates, absence of duplicate curvature code, input failure semantics, named-test receipts, exact ancestry and no unauthorized cross-repository mutation.

- [ ] **Step 5: Commit exact bytes and keep Draft**

Allowed closeout claim:

```text
BG02_NATIVE_XTENSOR_GAUSS_CODAZZI_BRIDGE_PASS
BG02_COMPONENT_ORACLE_PARITY_PASS
BG02_HOMOGENEOUS_DUAL_WITNESSES_PASS
```

Still forbidden:

```text
CONSTRAINT_PROPAGATION_VERIFIED
BACKGROUND_NUMERICAL_EVOLUTION
MATTER_DYNAMICS_CLOSED
PROVIDER_ADMISSION
OBSERVABLE_READY
LIKELIHOOD_READY
SCIENCE_VALIDITY
PASS_RF04
READY_OR_MERGE
```
