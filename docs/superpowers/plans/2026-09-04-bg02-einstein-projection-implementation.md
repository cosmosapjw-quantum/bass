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

implement:

\[
\mathcal H=n^an^bE_{ab},
\quad
\mathcal M_a=-h_a{}^cn^dE_{cd},
\\quad
\mathcal T=\frac13h^{ab}E_{ab},
\\quad
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
python3 scripts/verify_bg02_einstein_projection_implementation.py \(€€´µ¥¹ÁÕĞ‘½Ì½‰…ÍÍ}µ…ÍÑ•É}ÍÍ½Ñ}ØÈ½	|ÀÉ}%5A159QQ%=8½	|ÀÉ}%5A159QQ%=9}I%MQId¹©Í½¸)¥Ğ…‘İ½±™É…´½	ML½-•É¹•°½	…­É½Õ¹½¥¹ÍÑ•¥¹AÉ½©•Ñ¥½¸¹İ°p(€€€€€€€‘½Ì½‰…ÍÍ}µ…ÍÑ•É}ÍÍ½Ñ}ØÈ½	|ÀÉ}%5A159QQ%=8½	|ÀÉ}%5A159QQ%=9}I%MQId¹©Í½¸p(€€€€€€€ÍÉ¥ÁÑÌ½Ù•É¥™å}‰œÀÉ}•¥¹ÍÑ•¥¹}ÁÉ½©•Ñ¥½¹}¥µÁ±•µ•¹Ñ…Ñ¥½¸¹Áä)¥Ğ½µµ¥Ğ€µ´€‰™•…Ğ¡‰œÀÈ¤èÉ•¥ÍÑ•ÈÁÉ½©•Ñ¥½¸…¹É…Ñ”™½ÉµÕ±„¥‘•¹Ñ¥Ñ¥•Ìˆ)€((ŒŒŒQ…Í¬€Ôè‘¡½µ½•¹•½ÕÌ=9…‘…ÁÑ•ÉÌ…¹½¹¹•Ñ¥½¸µ½É‘•ÈÕ…É‘Ì((¨©¥±•Ìè¨¨(´5½‘¥™äèİ½±™É…´½	ML½-•É¹•°½	…­É½Õ¹½¥¹ÍÑ•¥¹AÉ½©•Ñ¥½¸¹İ±€(´Q•ÍĞèİ½±™É…´½	ML½Q•ÍÑÌ½	ÀÉ¥¹ÍÑ•¥¹AÉ½©•Ñ¥½¹%µÁ±•µ•¹Ñ…Ñ¥½¸¹İ±Ğ((¨©%¹Ñ•É™…•Ìè¨¨(´½¹ÍÕµ•Ìè(€€´	MM•½µ•ÑÉå=9I¥¥Q•¹Í½É€(€€´	MM•½µ•ÑÉå=9M…±…ÉÕÉÙ…ÑÕÉ•€(€€´	MM•½µ•ÑÉå½¹¹•Ñ¥½¹Q½1½­•‘…µµ…=É‘•É€(€€´	MM•½µ•ÑÉå1•Ù¥¥Ù¥Ñ…½¹¹•Ñ¥½¹€(´AÉ½‘Õ•Ìè¡½µ½•¹•½ÕÌÍ…±…ÈµÕÉÙ…ÑÕÉ”…¹µ½µ•¹ÑÕ´…‘…ÁÑ•ÉÌİ¥Ñ¡½ÕĞ‘ÕÁ±¥…Ñ”•½µ•ÑÉä¸((´lt€¨©MÑ•À€Äè]É¥Ñ”Ñ¡”X½%$½¹¹•Ñ¥½¸µ½É‘•È¹•…Ñ¥Ù”Ñ•ÍÑÌ¨¨()I•ÅÕ¥É”Ñ¡”±½­•É½ÕÑ”Ñ¼å¥•±è()Ñ•áĞ)	¥…¹¡¤X€€€HÈ€ô€´Ø)	¥…¹¡¤%$€€HÌ€ô€´Ä¼È)€()…¹Ñ¡”‘•±¥‰•É…Ñ•±äİÉ½¹œ‘¥É•Ğµ½É‘•ÈÉ½ÕÑ”Ñ¼å¥•±Ù…±Õ•Ì‘¥™™•É•¹Ğ™É½´‰½Ñ ¸Q¡”ÍÕ¥Ñ”µÕÍĞ•áÁ±¥¥Ñ±äÉ•©•Ğ…¸$­%`µ½¹±äİ¥Ñ¹•ÍÌÍ•Ğ…Ì¥¹ÍÕ™™¥¥•¹Ğ¸((´lt€¨©MÑ•À€Èè%µÁ±•µ•¹Ğ…‘…ÁÑ•ÉÌ‰ä…±±¥¹œ•á¥ÍÑ¥¹œ•½µ•ÑÉäA%Ì¨¨()M½ÕÉ”Õ…É‘ÌµÕÍĞ™…¥°¥˜¥¹ÍÑ•¥¹AÉ½©•Ñ¥½¸¹İ±€½¹Ñ…¥¹Ì…¹½Ñ¡•È-½ÍéÕ°™½ÉµÕ±„½È„Í•½¹1•Ù¥¥Ù¥Ñ…½¹¹•Ñ¥½¹€‰½‘ä¸((´lt€¨©MÑ•À€Ìè‘$½X½%$½%`Á½Í¥Ñ¥Ù”½¹ÑÉ½±Ì¨¨()Y•É¥™äè()Ñ•áĞ)$€€€À)X€€´Ø)%$€´Ä¼È)%`€€Ì¼È)€((´lt€¨©MÑ•À€Ğè½µµ¥Ğ¨¨()‰…Í )¥Ğ…‘İ½±™É…´½	ML½-•É¹•°½	…­É½Õ¹½¥¹ÍÑ•¥¹AÉ½©•Ñ¥½¸¹İ°p(€€€€€€€İ½±™É…´½	ML½Q•ÍÑÌ½	ÀÉ¥¹ÍÑ•¥¹AÉ½©•Ñ¥½¹%µÁ±•µ•¹Ñ…Ñ¥½¸¹İ±Ğ)¥Ğ½µµ¥Ğ€µ´€‰™•…Ğ¡‰œÀÈ¤è‰¥¹ÁÉ½©•Ñ¥½¹ÌÑ¼±½­•=9ÕÉÙ…ÑÕÉ”ˆ)€((ŒŒŒQ…Í¬€Øè‘½™˜µÍ¡•±°•áÁ…¹Í¥½¸…¹Í¡•…ÈµÉ…Ñ”…‘…ÁÑ•ÉÌ((¨©¥±•Ìè¨¨(´5½‘¥™äèİ½±™É…´½	ML½-•É¹•°½	…­É½Õ¹½¥¹ÍÑ•¥¹AÉ½©•Ñ¥½¸¹İ±€(´Q•ÍĞèİ½±™É…´½	ML½Q•ÍÑÌ½	ÀÉ¥¹ÍÑ•¥¹AÉ½©•Ñ¥½¹%µÁ±•µ•¹Ñ…Ñ¥½¸¹İ±Ğ((¨©%¹Ñ•É™…•Ìè¨¨(´AÉ½‘Õ•Ìè(€€´MÁ…Ñ¥…±QÉ…•I…Ñ•mu€(€€´5QÉ…•I…Ñ•mu€(€€´I…å¡…Õ‘¡ÕÉ¥I…Ñ•mu€(€€´M¡•…É1¥•I…Ñ•mu€(€€´M¡•…ÉAÉ½©•Ñ•‘I…Ñ•mu€((´lt€¨©MÑ•À€Äè‘™…¥±¥¹œÑ•ÍÑÌ™½ÈÑ¡É•”‘¥ÍÑ¥¹ĞÉ…Ñ”É•½É‘Ì¨¨()Q¡”¥µÁ±•µ•¹Ñ…Ñ¥½¸µÕÍĞ•áÁ½Í”É…ÜÍÁ…Ñ¥…°µÑÉ…”°ÑÉ…”µÉ•Ù•ÉÍ•4°…¹I…å¡…Õ‘¡ÕÉ¤™½ÉµÌÍ•Á…É…Ñ•±ä¸Ñ•ÍĞµÕÍĞÉ•©•Ğ…±¥…Í•ÌÑ¡…ĞÉ•ÑÕÉ¸½¹”Í¡…É••áÁÉ•ÍÍ¥½¸¸((´lt€¨©MÑ•À€Èè%µÁ±•µ•¹ĞÑ¡”Ñ¡É•”•á…Ğ™½ÉµÕ±…Ì¨¨()ql)}íqÉ´ÑÉ…•ô(ôµq™É…ííõyì Ì¥õIõìÄÉôµq™É…ŒÌÉ!xÈµq™É…ŒÄÑqÍ¥µ…xÈ(­q™É…ŒÄÌ¡p…q‘½Ñp…­xÈ¤­q™É…ŒÄÉq1…µ‰‘„µq™É…ŒÄÉq­…ÁÁ…}À°)qt()ql)}íqÉ´5ô(ôµq™É…ííõyì Ì¥õIõìÍô´Í!xÈ­q™É…ŒÄÌ¡p…q‘½Ñp…­xÈ¤(­q™É…íq­…ÁÁ…}õìÉô¡qÉ¡¼µÀ¤­q1…µ‰‘„°)qt()ql)}íqÉ´I…åô(ôµ!xÈµq™É…ŒÄÍqÍ¥µ…xÈ­q™É…ŒÄÌ¡p…q‘½Ñp…­xÈ¤(µq™É…íq­…ÁÁ…}õìÙô¡qÉ¡¼¬ÍÀ¤­q™É…íq1…µ‰‘…õìÍô¸)qt((´lt€¨©MÑ•À€ÌèY•É¥™äÑ¡”½™˜µÍ¡•±°¥‘•¹Ñ¥Ñ¥•Ì¨¨()ql)}íqÉ´5ôµ}íqÉ´ÑÉ…•ô­q™É…ŒÄÉqµ…Ñ¡…° ôÀ°)qt()ql)}íqÉ´ÑÉ…•ôµ}íqÉ´I…åô­q™É…ŒÄÙqµ…Ñ¡…° ôÀ°)qt()ql)}íqÉ´5ôµ}íqÉ´I…åô­q™É…ŒÈÍqµ…Ñ¡…° ôÀ¸)qt()Q•ÍÑÌµÕÍĞ™…¥°¥˜Ñ¡”¥µÁ±•µ•¹Ñ…Ñ¥½¸ÍÕ‰ÍÑ¥ÑÕÑ•Ìp¡qµ…Ñ¡…° ôÁp¤¸((´lt€¨©MÑ•À€Ğè%µÁ±•µ•¹Ğ‘•É¥Ù…Ñ¥Ù”µÑåÁ•Í¡•…ÈÉ…Ñ•Ì¨¨()MÑ½É”µ•Ñ…‘…Ñ„è()Ñ•áĞ)M¡•…É1¥•I…Ñ”€€€€€€‘•É¥Ù…Ñ¥Ù•}­¥¹€ô1%}I%YQ%Y}AMQ)M¡•…ÉAÉ½©•Ñ•‘I…Ñ”‘•É¥Ù…Ñ¥Ù•}­¥¹€ôAI=)Q}=YI%9Q}9=I51}I%YQ%Y)€()…¹Ù•É¥™äÑ¡”•á…Ğ…‘…ÁÑ•È¥‘•¹Ñ¥Ñä¸((´lt€¨©MÑ•À€Ôè½µµ¥Ğ¨¨()‰…Í )¥Ğ…‘İ½±™É…´½	ML½-•É¹•°½	…­É½Õ¹½¥¹ÍÑ•¥¹AÉ½©•Ñ¥½¸¹İ°p(€€€€€€€İ½±™É…´½	ML½Q•ÍÑÌ½	ÀÉ¥¹ÍÑ•¥¹AÉ½©•Ñ¥½¹%µÁ±•µ•¹Ñ…Ñ¥½¸¹İ±Ğ)¥Ğ½µµ¥Ğ€µ´€‰™•…Ğ¡‰œÀÈ¤è…‘½™˜µÍ¡•±°•áÁ…¹Í¥½¸…¹Í¡•…ÈÉ…Ñ•Ìˆ)€((ŒŒŒQ…Í¬€Üè‘­¹½İ¸±¥µ¥ÑÌ…¹•á•ÁÑ¥½¹…°µ½µ•¹ÑÕ´İ¥Ñ¹•ÍÌ((¨©¥±•Ìè¨¨(´5½‘¥™äèİ½±™É…´½	ML½Q•ÍÑÌ½	ÀÉ¥¹ÍÑ•¥¹AÉ½©•Ñ¥½¹%µÁ±•µ•¹Ñ…Ñ¥½¸¹İ±Ñ€(´5½‘¥™äèÑ•ÍÑÌ½Ñ•ÍÑ}‰œÀÉ}•¥¹ÍÑ•¥¹}ÁÉ½©•Ñ¥½¹}¥µÁ±•µ•¹Ñ…Ñ¥½¸¹Áå€((¨©%¹Ñ•É™…•Ìè¨¨(´½¹ÍÕµ•ÌèÁÉ½‘ÕÑ¥½¸ÁÉ½©•Ñ¥½¸½É…Ñ”A%Ì¸(´AÉ½‘Õ•Ìè•á…Ğ±¥µ¥ÑÌ…¹…‘Ù•ÉÍ…É¥…°Õ…É‘Ì¸((´lt€¨©MÑ•À€Äè‘™±…Ğ1I\…¹‘”M¥ÑÑ•ÈÑ•ÍÑÌ¨¨()±…Ğ1I\µÕÍĞÉ•½Ù•Èè()ql(Í!xÈõq­…ÁÁ…}qÉ¡¼­q1…µ‰‘„°)qÅÅÕ…)qµ…Ñ¡…°1}¹ ôµq™É…íq­…ÁÁ…}õìÉô¡qÉ¡¼­À¤¸)qt()±…Ğ‘”M¥ÑÑ•ÈµÕÍĞ¥Ù”…±°Ñ¡É•”É…Ñ•Ìé•É¼¸((´lt€¨©MÑ•À€Èè‘-…Í¹•ÈÙ…ÕÕ´¨¨()]¥Ñ p¡qÑ…ÔõÑp¤°()ql) õq™É…ŒÅìÍqÑ…Õô°)qÅÅÕ…)qÍ¥µ…xÈõq™É…ŒÉìÍqÑ…ÕxÉô°)qt()É•ÅÕ¥É”è()Ñ•áĞ)!É•Ì€ô€À)}ÑÉ…”€ô}4€ô}I…ä€ô€´Ä¼ ÌÑ…ÕxÈ¤)€((´lt€¨©MÑ•À€Ìè‘Ñ¡”•á•ÁÑ¥½¹…°p¡Y%}ì´Ä¼åõp¤…ÉÉ¥•È¨¨()I•ÅÕ¥É”•á…ĞÉ•Í¥‘Õ…°é•É¼™½Èè()ql)y‰qÍ¥µ…}ìÍ‰ô(´)q±•™Ñm9}ìÈÉõqM¥µ…}ìÄÉô¬¡9}ìÈÍô´Í¥qM¥µ…}ìÄÍõqÉ¥¡Ñt¸)qt()µÕÑ…Ñ¥½¸‘•±•Ñ¥¹œp¡qM¥µ…}ìÄÍõp¤µÕÍĞ™…¥°¸((´lt€¨©MÑ•À€Ğè½µµ¥Ğ¨¨()‰…Í )¥Ğ…‘Ñ•ÍÑÌ½Ñ•ÍÑ}‰œÀÉ}•¥¹ÍÑ•¥¹}ÁÉ½©•Ñ¥½¹}¥µÁ±•µ•¹Ñ…Ñ¥½¸¹Áäp(€€€€€€€İ½±™É…´½	ML½Q•ÍÑÌ½	ÀÉ¥¹ÍÑ•¥¹AÉ½©•Ñ¥½¹%µÁ±•µ•¹Ñ…Ñ¥½¸¹İ±Ğ)¥Ğ½µµ¥Ğ€µ´€‰Ñ•ÍĞ¡‰œÀÈ¤è±½¬±¥µ¥ÑÌ…¹•á•ÁÑ¥½¹…°µ½µ•¹ÑÕ´…ÉÉ¥•Èˆ)€((ŒŒŒQ…Í¬€àè	Õ¥±…¹É•Á±…äÑ¡”½µÁ±•Ñ”¹…Ñ¥Ù”áĞÍ½ÕÉ”Á…­•Ğ((¨©¥±•Ìè¨¨(´É•…Ñ”èİ½±™É…´½ÍÉ¥ÁÑÌ½ÉÕ¹}‰œÀÉ}•¥¹ÍÑ•¥¹}ÁÉ½©•Ñ¥½¹}¹…Ñ¥Ù”¹İ±Í€(´É•…Ñ”èÍÉ¥ÁÑÌ½‰Õ¥±‘}‰œÀÉ}•¥¹ÍÑ•¥¹}ÁÉ½©•Ñ¥½¹}Í½ÕÉ•}Á…­•Ğ¹Áå€(´É•…Ñ”èÍÉ¥ÁÑÌ½ÉÕ¹}‰œÀÉ}•¥¹ÍÑ•¥¹}ÁÉ½©•Ñ¥½¹}±½…°¹Í¡€(´5½‘¥™äè€¹¥Ñ¡Õˆ½İ½É­™±½İÌ½‰œÀÈµ•¥¹ÍÑ•¥¸µÁÉ½©•Ñ¥½¸µ¥µÁ±•µ•¹Ñ…Ñ¥½¸¹åµ±€((¨©%¹Ñ•É™…•Ìè¨¨(´½¹ÍÕµ•Ìè…±°Á…É•¹ĞÕÑ¡½É¥Ñä½%H½	¥…¹¡¤½•½µ•ÑÉäÍ½ÕÉ•Ì°ÁÉ½‘ÕÑ¥½¸	…­É½Õ¹Í½ÕÉ”°Ñ•ÍÑÌ°Í¡•µ…Ì°…¹É•¥ÍÑÉä¸(´AÉ½‘Õ•Ìè•á…ĞÍ½ÕÉ”Á…­•Ğ°¹…Ñ¥Ù”É••¥ÁĞ°±½…°ÍÕµµ…Éä°…¹M!´ÈÔØµ…¹¥™•ÍÑÌ¸((´lt€¨©MÑ•À€Äè5…­”Ñ¡”Á…­•Ğµ…¹¥™•ÍĞ™…¥°½¸½µ¥ÍÍ¥½¹Ì¨¨()Q¡”Á…­•Ğ‰Õ¥±‘•ÈµÕÍĞÉ•ÅÕ¥É”•Ù•ÉäÁ…É•¹Ğ™¥±”™É½´Ñ¡”AH€ŒäÄ€ÌĞµ™¥±”Í½ÕÉ”µ…¹¥™•ÍĞÁ±ÕÌÑ¡”¹•Ü	´ÀÈ™¥±•Ì¸=µ¥ÑÑ¥¹œ‰ÍÑÉ…ĞÅA±ÕÌÌ¹İ±€°=9½¹¹•Ñ¥½¹ÕÉÙ…ÑÕÉ”¹İ±€°a½‰…ÕÉÙ…ÑÕÉ•]¥Ñ¹•ÍÍ•Ì¹İ±€°½ÈÑ¡”ÁÉ½‘ÕÑ¥½¸µ½‘Õ±”µÕÍĞ™…¥°¸((´lt€¨©MÑ•À€ÈèIÕ¸¹…Ñ¥Ù”Á…­…”É•¥ÍÑÉ…Ñ¥½¸¨¨()Q¡”]½±™É…´ÉÕ¹¹•ÈµÕÍĞÉ•ÅÕ¥É”è()Ñ•áĞ)áQ•¹Í½È€Ä¸Ì¸À)á½‰„€À¸à¸Ø)é•É¼™…¥±•)é•É¼¹½Ğ•Ù…±Õ…Ñ•)€()%ĞµÕÍĞ•á•ÕÑ”Ñ¡”¥¹¡•É¥Ñ•\È½\ÌÍÕ¥Ñ•Ì…¹…±°	´ÀÈÑ•ÍÑÌ¥¸„™É•Í ­•É¹•°¸((´lt€¨©MÑ•À€ÌèAÉ•Í•ÉÙ”ÍÑÉ¥Ğ)M=8É••¥ÁÑÌ¨¨()]É¥Ñ”Ñ¼„Ñ•µÁ½É…ÉäÁ…Ñ °É”µ¥µÁ½ÉĞ…ÌI…İ)M=9€°Ù•É¥™ä•á…Ğ™¥•±‘Ì°…Ñ½µ¥…±±äÉ•¹…µ”°…¹É•ÅÕ¥É”„¹½¹•µÁÑä™¥¹…°™¥±”¸((´lt€¨©MÑ•À€ĞèIÕ¸™Õ±°±½…°Ù…±¥‘…Ñ¥½¸¨¨()‰…Í )‰…Í ÍÉ¥ÁÑÌ½ÉÕ¹}‰œÀÉ}•¥¹ÍÑ•¥¹}ÁÉ½©•Ñ¥½¹}±½…°¹Í p(€…ÉÑ¥™…ÑÌ½‰œÀÉ}•¥¹ÍÑ•¥¹}ÁÉ½©•Ñ¥½¸)€()I•ÅÕ¥É•É•ÍÕ±Ğè()Ñ•áĞ)AåÑ¡½¸¥µÁ±•µ•¹Ñ…Ñ¥½¸Ñ•ÍÑÌ€Äà¼Äà)5U¹¥Ğ	´ÀÈÑ•ÍÑÌ€€€€€€€€€€€ÈØ¼ÈØ)…±°¥¹¡•É¥Ñ•Í½ÕÉ”ÍÕ¥Ñ•ÌAML)™…¥±•½¹½Ğ•Ù…±Õ…Ñ•€€€€€€€€€À¼À)¹…Ñ¥Ù”áQ•¹Í½È½á½‰„€€€€€€€€AML)M!ÈÔÙMU5L€€€€€€€€€€€€€€€€€€AML)•á¥Ğ½‘”€€€€€€€€€€€€€€€€€€€€€€€À)€((´lt€¨©MÑ•À€Ôè½µµ¥Ğ•á…ĞÍ½ÕÉ”…¹É•Á±…ä…ÉÑ¥™…ÑÌÍ•Á…É…Ñ•±ä¨¨()‰…Í )¥Ğ…‘ÍÉ¥ÁÑÌİ½±™É…´‘½Ì½‰…ÍÍ}µ…ÍÑ•É}ÍÍ½Ñ}ØÈ½	|ÀÉ}%5A159QQ%=8)¥Ğ½µµ¥Ğ€µ´€‰Ñ•ÍĞ¡‰œÀÈ¤è…‘½µÁ±•Ñ”¹…Ñ¥Ù”áĞÉ•Á±…äˆ)€((ŒŒŒQ…Í¬€äè%¹‘•Á•¹‘•¹Ğ…Õ‘¥Ğ…¹‰½Õ¹‘•ÁÕ‰±¥…Ñ¥½¸((¨©¥±•Ìè¨¨(´É•…Ñ”è‘½Ì½‰…ÍÍ}µ…ÍÑ•É}ÍÍ½Ñ}ØÈ½	|ÀÉ}%5A159QQ%=8½	|ÀÉ}A!eM}5Q!}U%P¹µ‘€(´É•…Ñ”è‘½Ì½‰…ÍÍ}µ…ÍÑ•É}ÍÍ½Ñ}ØÈ½	|ÀÉ}%5A159QQ%=8½	|ÀÉ}A!eM}5Q!}=}U%P¹µ‘€(´É•…Ñ”è‘½Ì½‰…ÍÍ}µ…ÍÑ•É}ÍÍ½Ñ}ØÈ½	|ÀÉ}%5A159QQ%=8½	|ÀÉ}1=1}aQ}IA1e}1=M=UP¹©Í½¹€(´É•…Ñ”è‘½Ì½‰…ÍÍ}µ…ÍÑ•É}ÍÍ½Ñ}ØÈ½	|ÀÉ}%5A159QQ%=8½M!ÈÔÙMU5L¹Á½ÉÑ…‰±”¹ÑáÑ€((¨©%¹Ñ•É™…•Ìè¨¨(´½¹ÍÕµ•Ìè•á…ĞI8Í½ÕÉ”¡•……¹¹…Ñ¥Ù”É•Á±…ä…ÉÑ¥™…ÑÌ¸(´AÉ½‘Õ•Ìè„‰½Õ¹‘•¥µÁ±•µ•¹Ñ…Ñ¥½¸±½Í•½ÕĞİ¥Ñ¡½ÕĞ½¹ÍÑÉ…¥¹ĞµÁÉ½Á……Ñ¥½¸½È¹Õµ•É¥…°µ•Ù½±ÕÑ¥½¸±…¥µÌ¸((´lt€¨©MÑ•À€ÄèIÕ¸A!eLµ5Q É•Ù¥•Ü¨¨()Õ‘¥ĞÍ¥¹Ì°‘¥µ•¹Í¥½¹Ì°ÁÉ½©•Ñ¥½¸‘•™¥¹¥Ñ¥½¹Ì°½™˜µÍ¡•±°¥‘•¹Ñ¥Ñ¥•Ì°1I\½‘”M¥ÑÑ•È½-…Í¹•È±¥µ¥ÑÌ°…¹p¡Y%}ì´Ä¼åõp¤…ÉÉ¥•È¸((´lt€¨©MÑ•À€ÈèIÕ¸A!eLµ5Q µ=É•Ù¥•Ü¨¨()Õ‘¥ĞÍ¥¹±”É•Í¥‘Õ…°…ÕÑ¡½É¥Ñä°¹¼Í•½¹-½ÍéÕ°°±½…‘•ÈÕ¹¥ÅÕ•¹•ÍÌ°‘•É¥Ù…Ñ¥Ù”µ•Ñ…‘…Ñ„°™…¥°µ±½Í•É••¥ÁÑÌ°•á…ĞÍ½ÕÉ”Á…­•Ğ°…¹¹¼Õ¹…ÕÑ¡½É¥é•É½ÍÌµÉ•Á½Í¥Ñ½ÉäµÕÑ…Ñ¥½¸¸((´lt€¨©MÑ•À€ÌèA•É™½É´Á±½Ğµ‘É¥Ù•¸…‘Ù•ÉÍ…É¥…°‘¥…¹½ÍÑ¥Ì¨¨()A±½Ğ¹½Éµ…±¥é•è()ql)q™É…í}íqÉ´5ôµ}íqÉ´ÑÉ…•õõí!xÉô°)qÅÕ…)q™É…í}íqÉ´ÑÉ…•ôµ}íqÉ´I…åõõí!xÉô°)qÅÕ…)q™É…í}íqÉ´5ôµ}íqÉ´I…åõõí!xÉô)qt()……¥¹ÍĞÑ¡•¥È•á…Ğ!…µ¥±Ñ½¹¥…¸µÉ•Í¥‘Õ…°ÁÉ•‘¥Ñ¥½¹Ì¸Q¡”Á±½ÑÌ…É”‘¥…¹½ÍÑ¥Ì°¹½ĞÉ•Á±…•µ•¹ÑÌ™½È•á…Ğ¥‘•¹Ñ¥Ñ¥•Ì¸((´lt€¨©MÑ•À€ĞèM•…°Ñ¡”•á…Ğ‰åÑ•Ì¨¨()½Áä¹…Ñ¥Ù”É••¥ÁÑÌ¥¹Ñ¼¥Ğ°É•…Ñ”„Á½ÉÑ…‰±”M!´ÈÔØµ…¹¥™•ÍĞ°Ù•É¥™ä¥Ğ°…¹½µµ¥Ğ¸((´lt€¨©MÑ•À€ÔèAÉ•Í•ÉÙ”Ñ¡”±…¥´•¥±¥¹œ¨¨()Q¡”™¥¹…°±½Í•½ÕĞµ…ä±…¥´è()Ñ•áĞ)	ÀÉ}AI=UQ%=9}AI=)Q%=9}A%M}%5A159Q)	ÀÉ}9Q%Y}aQ}a=	}IA1e}AML)	ÀÉ}=}M!11}IQ}%9Q%Q%M}AML)	ÀÉ}=99Q%=9}=II}UIM}AML)	ÀÉ}aAQ%=91}5=59QU5}II%I}AML)€()%ĞµÕÍĞ¹½Ğ±…¥´è()Ñ•áĞ)=9MQI%9Q}AI=AQ%=9}YI%%)	-I=U9}9U5I%1}Y=1UQ%=8)5QQI}e95%M}1=M)11}5%1e}	-I=U9}Id)AI=Y%I}5%MM%=8)=	MIY	1}Id)1%-1%!==}Id)M%9}Y1%%Qd)AMM}IÀĞ)€((´lt€¨©MÑ•À€Øè½µµ¥Ğ‰½Õ¹‘•±½Í•½ÕĞ¨¨()‰…Í )¥Ğ…‘‘½Ì½‰…ÍÍ}µ…ÍÑ•É}ÍÍ½Ñ}ØÈ½	|ÀÉ}%5A159QQ%=8)¥Ğ½µµ¥Ğ€µ´€‰‘½Ì¡‰œÀÈ¤èÍ•…°ÁÉ½‘ÕÑ¥½¸ÁÉ½©•Ñ¥½¸¥µÁ±•µ•¹Ñ…Ñ¥½¸ˆ)€(