# SYNC-MAP-02C — Active REI Relation Classification

**Stage:** `SYNC_MAP_02C_REI_RELATION_CLASSIFICATION`  
**Status:** `PASS_WITH_BACKGROUND_PROVIDER_BLOCKER_AND_SHARED_FORMULA_EXPORT_GAPS`  
**Authority effect:** `NONE`  
**Observed:** 2026-09-02 15:30 KST

## 1. Exact scope

This stage classifies the active `rei_bianchi` scientific lineage against the BASS semantic formula line. It does not repair the REI runtime bridge, implement a numerical BASS background lock, admit a provider, or change a scientific claim.

Exact inputs:

```text
BASS relation parent PR #95
f1eab555b42ebfaa3aa9d4021e097750aa0dfd96

BASS FormulaIR parent PR #93
6587c081932d1dddda586781825d242616ca1357
14 formulas
registry d08082e38227c7731c103b26ba8cb029bbf212759f03e64ff1c8ac8ae7f1ab51

REI scientific PR #32
commit f4eb2c893ce6449f8899ab6f02c83421fc7c7019
tree   16d060d45ddfa401e4a5c22f9ca53cf65399ff51
src    f1708900abe8a912637d87ab506c7273b50266ae
```

All 22 paths in the exact REI `src` tree were enumerated. Nine load-bearing source files were inspected formula-by-formula. This is not historical all-branch deduplication and is not represented as semantic adjudication of every byte in all 22 source files.

## 2. Strongest current claim and strongest objection

The strongest defensible claim is that REI already contains a substantial, fail-closed H/He thermochemistry, multigroup transmission, opacity-decomposition and feasibility-gate substrate, together with exact BASS/REC custody machinery.

The strongest objection is equally clear: the active source explicitly does **not** implement a numerical BASS lock. Its physical evolution paths still use local FLRW-control Hubble closures. Consequently, this code is not evidence of Bianchi-background-coupled reionization, even though its microphysical and ledger layers are nontrivial.

## 3. Classification result

Eleven active relations were classified:

| Class | Count | Meaning |
| --- | ---: | --- |
| `PINNED_ARTIFACT_IMPORT_REQUIRED` | 2 | exact external BASS/REC authority and numerical BASS background lock |
| `BASELINE_CONTROL_ORACLE` | 1 | local FLRW Hubble closure, authority effect `NONE` |
| `ADAPTER_SPECIALIZATION` | 2 | REI-owned group-redshift and expansion-work discretizations requiring BASS `H` |
| `OWNED_EXTENSION` | 5 | electron density, ion-fraction chart, finite-τ transmission, species allocation, signed opacity decomposition |
| `OWNED_FEASIBILITY_GATE` | 1 | absorption–chemistry capacity inequality |

No active relation is classified as a BASS geometry duplicate.

## 4. BASS fourteen-formula matrix

```text
BASS geometry FormulaIR formulas                 14
NO_ACTIVE_REI_REDERIVATION_DETECTED              14
DEPENDENCY_ONLY                                   0
DUPLICATE_AUTHORITY                               0
```

The inspected REI source contains no implementation of the Bianchi connection, Riemann tensor, Ricci tensor, scalar curvature, Gauss–Codazzi identities, W2 projector, or W2 kinematic authority. The BASS integration substrate is a custody and reference-graph boundary, not a competing geometry implementation.

## 5. Physical ownership

### 5.1 BASS-owned or BASS-required

- exact external BASS authority pins;
- a numerical BASS background provider/lock;
- the Hubble/expansion value consumed by REI group-redshift and expansion-work adapters;
- the four already identified frame/photon formulas needed by REC and later HTT synchronization.

### 5.2 REI-owned

The active code explicitly contains the H/He electron-density relation

```text
n_e = n_H x_HII + n_He (x_HeII + 2 x_HeIII),
```

a positive ion-fraction state chart, finite-optical-depth group transmission,

```text
F_g = <exp[-tau_g(E)]>_phi,
```

species absorption allocation,

```text
A_sg = <[1-exp(-tau)] tau_s/tau>_phi / <1-exp(-tau)>_phi,
```

signed opacity-component decomposition, and the fail-closed necessary capacity condition

```text
J_H <= M_H + n_H^c (1-X_HII,start) / Delta_t.
```

These are REI microphysics, closure, discretization or validation relations. They are not Bianchi geometry authority.

### 5.3 Baseline-only controls

The FLRW Hubble functions in `b2b_physical_model.py`, `monolithic_model_b2a.py`, and the opacity receipt path are controls. They are useful for baseline recovery and isolated microphysics tests. They must not be promoted into a generic Bianchi background or used as evidence of geometry feedback.

## 6. SciSpace role lock

The literature search was admitted only as an external scope and methodology cross-check.

- Challinor's covariant PSTF formalism supports separating observer/tetrad dependence from the polarized transfer hierarchy.
- Naruko, Pitrou, Koyama and Sasaki emphasize the tetrad choice and gauge properties of tensor-valued photon distributions.
- Portsmouth and Bertschinger derive scattering first in the electron rest frame and then transform between frames.
- HyRec and precision helium-recombination work place H/He population evolution, free-electron history and line/continuum transfer in the microphysics layer.
- Fully coupled reionization literature treats radiation, thermal and ionization equations as a coupled numerical system, not as spacetime-geometry authority.

These papers do not supersede project conventions, FormulaIR identities, source blobs, or the exact BASS/REI ownership boundary.

## 7. Wolfram exact audit

The first stateless pass returned `14/15` because the audit used an incorrect Wolfram Jacobian expression. The physical relations and graph checks passed. The harness failure was retained, and only the derivative-construction expression was repaired.

Fresh final pass:

```text
Wolfram 15.0.1 for Linux x86-64
15 checks
15 passed
0 failed
xAct required: false
```

The exact checks cover:

- the H/He electron-density Jacobian `{n_H,n_He,2 n_He}`;
- detection of the wrong singly-ionized HeIII coefficient;
- the future interface identity `kappa_T=sigma_T n_e` and its dimension `L^-1` without claiming code implementation;
- the exact difference between a matter+Λ FLRW control and a radiation-inclusive control;
- finite-τ transmission/absorption partition;
- species-allocation normalization;
- preservation of the signed opacity residual;
- relation-class count;
- proposal-DAG closure, acyclicity and full topological coverage;
- preservation of the first-interval/provider gate;
- prohibition on promoting the FLRW control to BASS authority.

Impact-graph digest:

```text
42d69bdff4bcdea946f8c1a6d34d7de7d986b95887c78dda44b4933dc8f47bd8
```

The two Thomson-opacity checks are future interface checks only. They do not establish an exact electron-frame CMB collision path in REI.

## 8. DAG correction

The REI scan does **not** add another shared frame/photon EquationIR duplicate. It instead exposes a different contract class: numerical background-provider admission.

Therefore the old single convergence idea is split:

```text
REC/HTT common frame-photon gaps
  -> FED.SHARED_FRAME_PHOTON_EXPORT
  -> {SYNC_REC, SYNC_HTT, any formula-level REI consumer}

BASS.GEOMETRY
  -> BASS.BG02_IMPLEMENT
  -> BASS.BACKGROUND_PROVIDER_SCHEMA_AND_EXACT_LOCK
  -> REI.BASS_NUMERICAL_BACKGROUND_LOCK
  -> REI.FIRST_CANONICAL_INTERVAL
```

The background lock must not be disguised as an EquationIR formula export, and the frame/photon export must not be delayed by REI thermochemistry.

## 9. Newly opened and still blocked nodes

Newly completed:

```text
FED.MAP02C_REI
```

Newly opened:

```text
FED.SHARED_FRAME_PHOTON_EXPORT
BASS.BG02_IMPLEMENT                 already independently READY
```

Still blocked:

```text
REI.BASS_NUMERICAL_BACKGROUND_LOCK
  blocked on BG-02 implementation and exact external pins

REI.FIRST_CANONICAL_INTERVAL
  blocked on runtime bridge, background lock and accepted capacity path

REI.PROVIDER_EXPORT
  blocked on first canonical interval
```

## 10. Claim boundary

Authorized:

```text
SYNC_MAP_02C_ACTIVE_REI_RELATIONS_CLASSIFIED
SYNC_MAP_02C_NO_ACTIVE_REI_GEOMETRY_DUPLICATE_AUTHORITY_DETECTED
SYNC_MAP_02C_REI_MICROPHYSICS_ADAPTER_AND_CONTROL_ROLES_SEPARATED
SYNC_MAP_02C_WOLFRAM_15_OF_15_PASS
SYNC_MAP_02C_BACKGROUND_LOCK_DAG_EDGE_IDENTIFIED
```

Withheld:

```text
REI_BIANCHI_GEOMETRY_IMPLEMENTATION
BASS_NUMERICAL_BACKGROUND_LOCK
GLOBAL_TILT
LOCAL_OBSERVER_BOOST
EXACT_ELECTRON_FRAME_THOMSON_CMB_PATH
FIRST_CANONICAL_INTERVAL
REI_PROVIDER_EXPORT
CROSS_REPOSITORY_SEMANTIC_EQUIVALENCE
OFFICIAL_DAG_MUTATION
SCIENCE_VALIDITY
PASS_RF04
```

## 11. Recommended next bounded node

The next federation node is:

```text
FED.SHARED_FRAME_PHOTON_EXPORT
```

It should export exactly the four already established BASS-owned frame/photon formulas, then provide exact FormulaIR pins to REC and HTT. In parallel, the BASS physics lane should implement BG-02; only after that should a numerical background-provider schema and REI lock be attempted.
