# SYNC-MAP-02C PHYS–MATH–CODE Audit

**Audited record:** `REI_RELATION_CLASSIFICATION_FIX2.json`  
**Verdict:** `PASS_CLASSIFICATION / IMPLEMENTATION_BLOCKERS_PRESERVED`  
**Claim effect:** `NONE`

## Code-path reality map

| Code path | Actual role | Classification |
| --- | --- | --- |
| `bass_integration_substrate.py` | exact local Git-object custody, reference-only graph and descriptor publication | implemented governance substrate; explicitly no numerical BASS lock |
| `b2b_physical_model.py` | late-time flat-FLRW H/He photon-group control and residual | implemented control; explicitly no Bianchi geometry |
| `monolithic_model_b2a.py` | H/He OTS thermochemistry and electron-density path | implemented REI microphysics path |
| `multigroup_hhe_transmission.py` | finite-τ transmission and species allocation | implemented closure path; not angular Bianchi transport |
| `phase_space_kernel_b2c0.py` | numerical maintenance closure | implemented numerical closure; not astrophysical topology calibration |
| `absorption_decomposition.py` | physical opacity components plus signed unattributed residual | implemented diagnostic decomposition; residual not a physical extinction coefficient |
| `primary_exact_zero_model.py` | positive state chart, exact-zero G3 carrier, expansion work | implemented REI state/thermal path under control assumptions |
| `matched_history_feasibility_gate.py` | hard absorption–chemistry capacity precondition | implemented necessary fail-closed gate |
| `reiaff1.py` | restart ownership and certificate-graph contract | implemented governance/runtime contract; no scientific promotion |

## Equation-to-code correspondence

### Strong correspondence

- `n_e=n_H x_HII+n_He(x_HeII+2x_HeIII)` maps directly to `electron_density`.
- finite-τ transmission and species allocation map directly to the multigroup transmission module.
- the signed residual decomposition maps directly to the absorption-decomposition output contract.
- the capacity inequality maps directly to the feasibility gate and blocks rather than repairs an infeasible target.

### Partial correspondence

- `red_out=Hubble*redshift_coeff` is a real used code path, but represents only the FLRW/isotropic angular control. It is not a discretization of the full Bianchi phase-space operator.
- `expansion_work=3Hp` is a real used term, but its current state contract excludes generic global tilt and anisotropic stress work.

### Absent correspondence

- no numerical BASS background provider/lock;
- no Bianchi connection or curvature implementation in REI;
- no direction-dependent ionizing-photon characteristic;
- no angular multipole closure carrying `sigma_ab Q^ab`;
- no exact electron-frame CMB Thomson block;
- no global-tilt or local-observer-boost path;
- no passed first canonical interval or provider export.

## Identity and source evidence

The exact REI PR #32 source tree contains 22 source files. Nine load-bearing files were bound to Git blob SHA-1 identities. The bounded audit enumerated every source path but does not claim semantic adjudication of every source byte or historical all-branch deduplication.

The active source contains no competing implementation of the fourteen BASS geometry FormulaIR entries. Therefore the bounded matrix result is:

```text
NO_ACTIVE_REI_REDERIVATION_DETECTED = 14
DUPLICATE_AUTHORITY                 = 0
```

This is an active-lineage result, not a global repository-history theorem.

## Verification reality

### Completed

- direct source and blob readback from exact REI head;
- SciSpace methodology/scope cross-check;
- Wolfram algebra/graph pass `15/15` after one preserved Jacobian-harness repair;
- Wolfram angular-moment pass `6/6` after one preserved symbolic-nonzero-predicate repair;
- Dropbox raw-byte recovery candidate validation `26/26`, later superseded;
- Dropbox raw-byte Fix1 validation `24/24`, later superseded by Fix2;
- deterministic relation-class CSV and SVG;
- deterministic corrected impact-DAG SVG;
- PHYS–MATH and PHYS–MATH–CODE audits.

### Not completed

- repo-local Python verifier execution: `NOT_RUN_ENVIRONMENT_CLIENT_ERROR`;
- native xAct replay: not required for this source-classification node and not run;
- raw GitHub JSON import in the connected Wolfram kernel: `ENVIRONMENT_GAP_RAW_GITHUB_IMPORT`;
- runtime bridge repair;
- BASS background provider replay;
- numerical interval or provider replay.

The Python environment gap must not be relabeled as a verifier pass. The Dropbox replay verifies the compact recovery projections, not byte identity with the canonical GitHub Fix2 object.

## Regression and mutation checks

| Mutation | Expected failure | Result |
| --- | --- | --- |
| HeIII counted with one electron | wrong electron-density Jacobian | detected |
| FLRW control described as radiation-inclusive | docs exceed code | detected and corrected in Fix1 |
| nonzero radiation quadrupole treated as H-only redshift | missing shear coupling | detected and corrected in Fix2 |
| signed opacity residual exponentiated | nonphysical effective extinction | prohibited by source contract |
| internal graph digest treated as authority admission | self-authentication | prohibited by custody/reference graph design |
| first interval bypassed before provider export | promotion without execution | prohibited by impact DAG |

## Ranked software-contract findings

### P0

None for the bounded classification artifact.

### P1

1. `REI.ANISOTROPIC_GROUP_REDSHIFT_CLOSURE` is absent and must block Bianchi-coupled interval claims.
2. `BASS.BACKGROUND_PROVIDER_SCHEMA_AND_EXACT_LOCK` is absent and must precede the REI background lock.
3. The runtime bridge remains stopped on undeclared `ntpath` and independently blocks the interval.
4. The committed Python verifier has not run in this execution environment.

### P2

1. The compact Dropbox records are structurally replayable but not byte-identical to the canonical GitHub Fix2 delta.
2. The relation-class plot can be misread as implementation maturity unless its ownership-only caption is retained.
3. Nine-file deep inspection does not imply complete semantic review of all 22 source files.

## Minimal conditions for the next claims

| Claim | Minimum missing evidence |
| --- | --- |
| relation classification complete | current Fix2 + restored receipt + publication readback |
| shared formula export complete | four FormulaIR records, semantic hashes, dependencies and exact consumer pins |
| BASS background provider ready | BG-02 implementation, constraints/residuals, typed history schema, units/time adapter and exact replay |
| REI Bianchi group transport ready | BASS background lock plus angular hierarchy/closure with shear coupling and cutoff/closure convergence |
| first canonical interval | runtime bridge, capacity path, background lock, anisotropic redshift closure and numerical receipts |
| provider export | first interval plus independent audit and exact consumer contract |

## Final code verdict for this node

The ownership classification is supportable. The scientific coupling is not. The correct output is a more restrictive DAG, not a claim that REI already consumes BASS physics.
