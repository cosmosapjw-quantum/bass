# XBOOST-01 external-package triangulation and DAG reconciliation

## Status

```text
EXACT_PACKAGE_DOWNLOAD_IDENTITY             PASS 7/7
SOURCE_OR_FORMULA_INSPECTION                PASS 6/7
ACTUAL_PACKAGE_RUNTIME                      PASS 4/7
PYTHON_PACKAGE_RUNTIME                      NOT RUN
GITHUB_ACTIONS_RUNNER_ALLOCATION            FAIL_INFRASTRUCTURE
SYNC_MAP_02F_R2_SEMANTIC_CLOSEOUT           NOT EARNED
AUTHORITY_EFFECT                            NONE
```

This evidence-only lane is a Draft child of BASS PR #101 at exact commit
`32b8a89abbeaad5503cf0dfc59cfa5633a53ec3b`. It does not repair the PR #102
semantic-schema/MUnit RED and does not change any BASS/REC/REI/HTT physical
formula or consumer implementation.

## Package-role split

Three concurrently created external-package lanes are complementary rather
than interchangeable:

```text
PR #103  broad external-CAS contract on the PR #102 R2-RED ancestry
PR #104  XBOOST-01: Lorentz/null-vector/d=1 harmonic package evidence
PR #105  XCAS-01: tensor/GR/scalar-CAS package evidence
```

No lane is an automatic semantic winner. After `02E-R1` and `02F-R2` are
corrected, receipts may be imported by role. Competing formula or graph bytes
must not be merged merely because independent packages agree.

## Exact package evidence

### SymEngine 0.14.1

The PyPI source distribution was downloaded by Wolfram and matched

```text
SHA-256 4e9e4b4ec56371c2151803ae0403dab07dd1c74ce88e9abca433bebeb6e2f0f0
bytes   938282
```

The package runtime was not executed: the GitHub job never received a runner
and the connected Wolfram evaluator exposes neither `python3` nor a working
Python external evaluator. Distribution identity is not relabelled as an
exact-CAS runtime PASS.

### pylorentz 0.3.3

The exact PyPI source distribution matched

```text
SHA-256 4dcc3716d1f858e39acd637ff9333352142a9abf968e3451a9759dd66b2c5da6
bytes   12259
```

The release source uses signature `(+,-,-,-)` and the boost matrix convention
for the vector measured in a frame moving in the supplied direction. A fresh
Wolfram reconstruction of that source gives, for a photon propagating with
`mu=e.beta_hat`,

\[
E'=\gamma E(1-\beta\mu),\qquad
\mu'=\frac{\mu-\beta}{1-\beta\mu}.
\]

Exact residuals:

```text
null four-momentum                         0
boosted spatial-direction norm             0
forward/inverse aberration composition     0
outward-sky n=-e Doppler adapter            0
```

The wrong-sign mutation is

\[
\Delta E_{\rm wrong}
=\frac{2\beta E\mu}{\sqrt{1-\beta^2}},
\]

which is generically nonzero. This is source-formula reconstruction, not a
Python package-runtime claim.

### CosmoBoost 1.1.6

The PyPI wheel matched

```text
SHA-256 0532cb213647e1033d4bd98248c3e39400b648582e0773d5a0cb2f76994e65cb
bytes   328655
```

The wheel sources independently expose the `d=1`, `s=0` kernel, rapidity
`eta=arctanh(beta)`, the Dai--Chluba generator, and

\[
{}_{s}B_{\ell m}
=\sqrt{\frac{(\ell^2-s^2)(\ell^2-m^2)}{4\ell^2-1}}.
\]

For the scalar monopole-to-dipole channel,

\[
B_{10}=\frac1{\sqrt3},
\]

and the package's Bessel approximation gives

\[
J_1\!\left(2B_{10}\operatorname{arctanh}\beta\right)
=\frac{\beta}{\sqrt3}
+\frac{\beta^3}{6\sqrt3}+O(\beta^5).
\]

At zero boost, `J_delta(0)` reproduces the identity band. This is a
source-level `d=1,s=0` harmonic regression only. The wheel runtime was not
executed because no GitHub runner was allocated.

### FeynCalc 10.2.1

The official release zipball was downloaded and loaded in Wolfram 15.0.1:

```text
SHA-256 6cbad87f2c032795533c77a3257893bfac8dbd85b70c5a09a0112d810c2e3c79
bytes   8429794
load    PASS
```

With FeynCalc signature `(+,-,-,-)`, let

\[
n^2=1,\quad e^2=b^2=-1,\quad n\!\cdot e=n\!\cdot b=0,
\quad e\!\cdot b=-\mu.
\]

For `p=E(n+e)` and `u=gamma(n+beta b)`, the independent package gives

\[
p^2=0,\qquad u^2=1,\qquad p\!\cdot u=E\gamma(1-\beta\mu),
\]

with exact residual zero. BASS uses the overall-sign-opposite metric
`(-,+,+,+)`, so this result is admitted only after the explicit metric
adapter.

### Tensor/GR package lane

PR #105 separately records successful connected-Wolfram package results:

```text
STensor 1.0.1                Minkowski G_ab=0; Bianchi-I G_00 residual 0
OGRe 2.0.0                   full diagonal Bianchi-I Einstein residuals 0
GeneralRelativityTensors     same independent coordinate-tensor residuals 0
```

These are independently implemented tensor packages but share the Wolfram
algebra kernel. They strengthen implementation diversity, not algebra-engine
independence.

## Primary-literature role lock

Direct primary-source reading fixes the scope:

- Dai and Chluba, arXiv:1403.6117: exact nonperturbative aberration kernels;
  the full-sky operator is unitary for Doppler weight `d=1`, and the special
  no-`E/B`-mixing result is not a generic `d` statement.
- Yasini and Pierpaoli, arXiv:1709.08298: observable classes carry distinct
  spin and Doppler weights. Thermodynamic temperature has `(s,d)=(0,1)`,
  specific intensity `(0,3)`, bolometric intensity `(0,4)`, occupation number
  `(0,0)`, polarized temperature `(+-2,1)`, and polarized intensity `(+-2,3)`.
- Challinor, arXiv:astro-ph/9911481: polarization requires an explicit screen
  projector and screen-basis transformation; scalar aberration alone is not
  a polarized transport theorem.
- Fleury, Pitrou and Uzan, arXiv:1410.8473: Bianchi propagation, direction
  drift and Jacobi/optical transport are separate from a final local observer
  Lorentz transform.

Consequently the scalar six-formula export does not silently acquire spectral,
polarized, global-tilt, finite-electron-collision or Bianchi-optics scope.

## PHYS-MATH audit

### PASS within scope

- The two Doppler charts agree under `n_sky=-e`.
- The project and external-package metric signatures are connected by an
  explicit overall-sign adapter.
- The null-vector, aberration-inverse and measured-energy residuals vanish.
- CosmoBoost's `d=1,s=0` small-beta coefficient agrees with the analytic
  `beta/sqrt(3)` magnitude.
- The ray-length parameter remains `s=ct`; `ell` is reserved for angular
  multipole rank.
- External package agreement does not change FormulaIR ownership.

### P0/P1 boundaries

- P0: none of these packages repairs the missing orthogonal relation schema or
  the zero-test MUnit discovery defect in PR #101/102.
- P1: CosmoBoost's `d=1,s=0` source does not validate frequency-dependent or
  polarized kernels.
- P1: pylorentz and FeynCalc validate Lorentz kinematics, not electron-rest
  Thomson collision conjugation.
- P1: the connected tensor packages share the Wolfram algebra engine and are
  not four independent CAS engines.

## PHYS-MATH-CODE audit

### Genuinely established

```text
exact release/distribution identity        7/7
source or formula inspection               6/7
actual package runtime                     4/7
hostile wrong-sign Lorentz mutation        detected
package roles and authority firewalls      machine-recorded
```

### Not established

```text
SymEngine runtime
pylorentz Python runtime
CosmoBoost Python runtime
cross-repository consumer software parity
02F-R2 semantic graph closeout
provider or solver admission
```

GitHub Actions runs for PR #104 and PR #105 both created jobs with
`runner_id=0` and `steps=[]`; a rerun reproduced the same state. This is
classified as a runner-dispatch/infrastructure failure. It is not evidence
that package installation or the tested formulas fail.

## Plot/coverage reading

The deterministic coverage matrix is stored in
`EXTERNAL_ORACLE_COVERAGE_R1.svg` and its source table in
`EXTERNAL_ORACLE_COVERAGE_R1.csv`.

Reading:

1. Download identity is saturated: `7/7`.
2. Source/formula inspection is nearly saturated: `6/7`; SymEngine runtime is
   the only deliberately unpromoted cell.
3. Actual package runtime is `4/7`, entirely on the connected Wolfram route.
4. Adding more package names now has lower information gain than fixing the
   owner FormulaIR and R2 semantic/MUnit contract.
5. The shared-Wolfram runtime cluster is not an independent-algebra-engine
   cluster; the existing SymPy, GNU Octave and standard-library axes remain
   necessary.

## Updated DAG

```text
PRIMARY OWNER / SEMANTIC LANE

02E-R1 semantic hardening
  -> normal ancestry composition into 02F
  -> satisfy PR #102 R2 schema and exact-count MUnit RED
  -> 02F bounded semantic closeout
  -> {SYNC-REC-01, SYNC-REI-01, SYNC-HTT-01A}
  -> SYNC-GATE-01 manual only

PARALLEL NON-AUTHORITATIVE EVIDENCE LANES

PR #103 broad external-CAS contract donor ---------\
PR #104 XBOOST-01 Lorentz/harmonic packages -------+-> role-filtered receipt import after 02F-R2
PR #105 XCAS-01 tensor/GR/scalar-CAS packages -----/
```

External-package lanes do not block `02E-R1` or `02F-R2`, and agreement in
those lanes cannot waive an owner-semantic defect.

## Completeness

| Work unit | Completion | Disposition |
| --- | ---: | --- |
| External package acquisition/identity | 100% | 7/7 |
| Lorentz/null-vector source reconstruction | 100% | bounded PASS |
| `d=1,s=0` harmonic source regression | 100% | bounded PASS |
| Connected Wolfram tensor/package runtime | 100% of attempted four | bounded PASS |
| Python external-package runtime | 0% | runner infrastructure blocked |
| XBOOST-01 evidence lane | 75% | source/runtime split preserved |
| XCAS-01 evidence lane | approximately 70% | package receipts exist; CI aggregate blocked |
| 02E-R1 owner semantic hardening | not closed | primary blocker |
| 02F-R2 implementation | 0% | RED contract exists |
| Formula federation end-to-end | approximately 55--60% | no consumer bindings or gate |
| Full scientific solver program | unchanged, approximately 18--25% | no promotion |

## Recommended next step

`SYNC_MAP_02E_R1_SEMANTIC_HARDENING_AND_02F_R2_COMPOSITION` is the next
load-bearing node. It must fix the owner FormulaIR and exact-count MUnit path,
not add a fourth external package lane.

## Claim boundary

Authorized:

```text
EXTERNAL_PACKAGE_IDENTITIES_VERIFIED
PYLORENTZ_SOURCE_FORMULA_RECONSTRUCTION_PASS
COSMOBOOST_D1_S0_SOURCE_FORMULA_RECONSTRUCTION_PASS
FEYNCALC_RUNTIME_LORENTZ_CONTRACTION_PASS
CONNECTED_WOLFRAM_TENSOR_PACKAGE_WITNESSES_PASS
EXTERNAL_ORACLE_LANES_ROLE_RECONCILED
```

Withheld:

```text
SYNC_MAP_02F_COMPLETE
CROSS_REPOSITORY_CONSUMER_PARITY
GLOBAL_MATTER_TILT
FINITE_ELECTRON_TILT_COLLISION
POLARIZATION_SCREEN_TRANSPORT
SPECTRAL_BOOST_COMPLETENESS
BACKGROUND_OR_PROVIDER_ADMISSION
ARBITRARY_L_SOLVER_VALIDATION
OBSERVATIONAL_OR_STATISTICAL_READINESS
SCIENCE_VALIDITY
PASS_RF04
```
