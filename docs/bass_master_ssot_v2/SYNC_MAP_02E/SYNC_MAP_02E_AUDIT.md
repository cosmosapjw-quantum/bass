# SYNC-MAP-02E status

## Current stage

```text
SYNC-MAP-02A  BASS geometry EquationIR                       COMPLETE
SYNC-MAP-02B  REC relation classification                   COMPLETE
SYNC-MAP-02C  REI R3 active-line relation classification    COMPLETE / exact-head CI green
SYNC-MAP-02D  HTT repaired relation classification           COMPLETE_CANDIDATE / exact-head CI green
SYNC-MAP-02E  shared frame/photon EquationIR export          IMPLEMENTED_CANDIDATE
SYNC-MAP-02F  cross-repository semantic graph                BLOCKED_BY_02E_TERMINAL_READBACK
```

## What this stage adds

- six machine-readable, BASS-owned EquationIR records;
- exact consumer bindings across REC, REI, and HTT;
- corrected repaired-02D predecessor identity;
- internal and external dependency DAG;
- Wolfram-compatible semantic hashes;
- Python and Wolfram fail-closed validators;
- exact symbolic and hostile-mutation oracles;
- deterministic dependency/consumer figure.

## What this stage does not add

- numerical BASS background provider;
- global matter-frame tilt;
- finite-electron-frame Thomson collision;
- recombination or reionization microphysics;
- hierarchy truncation or numerical solver;
- mask/beam/estimator response;
- cross-repository semantic equivalence;
- provider, observational, statistical, or science readiness.

## Promotion gate

The stage remains a candidate until all of the following are bound to one exact head:

1. 13/13 Python mutation-sensitive tests;
2. fail-closed export verifier;
3. deterministic SVG byte identity;
4. exact-base changed-path/text hygiene;
5. native Wolfram package and WLT replay;
6. append-only tested-head publication receipt.

---

# SYNC-MAP-02E predecessor-pin audit

## Finding

The final SYNC-MAP-02C R3 receipt pins the HTT relation classification at

```text
06aa29f78c26bcafeb60d85b719a4d3aa5c4c2e8
```

That commit is an ancestor of the repaired SYNC-MAP-02D payload, not its final scientific payload. Five later commits modify the load-bearing classification JSON, Python verifier/tests, and Wolfram module/tests. The repaired payload is

```text
commit 6203b1343a6adb0f53d7abd0667e6d76b80fec53
tree   db49005f8dc77431dc4b76d67d8b7a242877fa46
```

and the append-only receipt head is

```text
7006aaab27834af37d5034f8f1e50943fe85c0f3
```

The repair closes the ninth HTT source pin and explicit STF3/domain mutation guards. The six-formula consumer union is unchanged, but exact predecessor identity is not semantically interchangeable with the pre-repair candidate.

## Decision

SYNC-MAP-02E supersedes the stale cross-pin without rewriting the closed 02C receipt. Its machine export records all three values:

- `pre_repair_commit_superseded = 06aa...`;
- authoritative repaired payload `commit = 6203...`, `tree = db490...`;
- publication/readback head `final_receipt_head = 7006...`.

The fail-closed validators reject a return to `06aa...`.

## Claim boundary

This repair changes federation identity and validation provenance only. It does not add a seventh formula, a background provider, a solver, global tilt, finite-electron collision, observational readiness, or science validity.

---

# SYNC-MAP-02E SciSpace literature lock

## Role

The literature is used only as an independent regression and scope oracle. It does not choose project signs, formula ownership, semantic hashes, Git identity, or claim promotion.

## Admitted primary-source roles

| Source family | Admitted use in SYNC-MAP-02E | Not admitted |
|---|---|---|
| Dai & Chluba, exact CMB aberration kernels | Exact all-orders local-boost context; Doppler-weight `d=1`; full-sky harmonic unitarity and the special absence of full-sky E/B mixing for the thermodynamic-temperature weight | Project sign choice, BASS ownership, consumer admission, processed-mask response |
| Yasini & Pierpaoli, frequency-dependent Doppler/aberration kernels | Regression that generic spectral observables and cut-sky analyses require a different response layer from blackbody thermodynamic temperature | Promotion of the present blackbody pullback to arbitrary frequency-dependent intensity |
| Catena & Notari and related CMB boost analyses | Observation-side context for Doppler/aberration mode coupling and sky-cut effects | Authority for the BASS formula registry or likelihood readiness |
| Fleury, Pitrou & Uzan, light propagation in Bianchi I | Independent redshift and direction-drift regression in a spatially homogeneous anisotropic spacetime | Proof of all eleven Bianchi branches or the project tetrad sign convention |
| Marcori, Pitrou, Uzan & Pereira, redshift/direction drifts | Contrast between observer-velocity dipole structure and shear-induced quadrupole structure | Identification of local observer boost with global matter tilt |
| Mitsou & Yoo, tetrad formalism and matrix kinetic theory | General exact tetrad and photon phase-space foundation | A replacement for the project-derived all-branch homogeneous direction-flow theorem |

## Locked conclusion

The literature supports the *separation* used here:

1. finite local-observer Lorentz pullbacks are output/frame transformations;
2. homogeneous-Bianchi energy and direction flow are forward phase-space transport coefficients;
3. mask, beam, estimator, frequency-dependent intensity, finite-electron collision, global matter tilt, and inference belong to separate downstream layers.

`authority_effect = NONE` for every literature item in this stage.

---

# SYNC-MAP-02E PHYS-MATH audit

## Contract

Conventions are metric signature `(-,+,+,+)`, spatial orientation `epsilon_123=+1`, explicit `c`, `h_P`, and `k_B`, photon propagation direction `e^a`, and outward sky direction `n_sky^a=-e^a`. The local boost has `beta^2<1` and `gamma=(1-beta^2)^(-1/2)`.

The stage exports exactly six BASS-owned EquationIR records:

1. Doppler factor;
2. aberrated outward-sky direction;
3. solid-angle Jacobian;
4. thermodynamic blackbody-temperature pullback;
5. homogeneous photon-energy drift;
6. celestial-sphere direction flow.

## Exact checks

A clean connected Wolfram 15.0.1 run returned zero for ten independent residuals:

```text
aberrated-direction unit norm
doppler inverse chart
deaberration coefficient of n_sky
deaberration coefficient of beta
solid-angle Jacobian
blackbody Planck-argument invariance
n_sky=-e direction adapter
direction-flow tangency
FLRW energy-drift limit
Minkowski energy-drift limit
```

Six structural checks passed: zero-boost Doppler and aberration, regular zero-boost coefficient limit, ambient-factor form of sphere tangency, dimensions, and scope firewall. Seven hostile mutations were detected: wrong Doppler sign, wrong Jacobian power, wrong temperature weight, wrong energy-shear sign, omitted radial compensator, stale four-formula union, and finite-electron-tilt injection.

Clean oracle digest:

```text
60ea9b894f955c2599628ae3ebf51b0e6d3a9ab2c512551fdef86e8c022f254b
```

## Formula and limit ledger

| Formula | Exact content | Dimension | Required limits |
|---|---|---:|---|
| `BASS.FRAME.DOPPLER_FACTOR.001` | `D=gamma(1+beta·n_sky)=gamma(1-v·e/c)` under `n_sky=-e` | 1 | `beta->0: D->1` |
| `BASS.FRAME.ABERRATED_DIRECTION.001` | exact finite Lorentz sky-direction map | 1 | unit norm; inverse by transformed-chart `beta->-beta`; continuous zero-boost extension |
| `BASS.FRAME.SOLID_ANGLE_JACOBIAN.001` | `dOmega_tilde=D^-2 dOmega` | 1 | identity at zero boost |
| `BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001` | `T_tilde(n_tilde)=D T(n)` | K | invariant `h_P nu/(k_B T)` |
| `BASS.PHOTON.ENERGY_DRIFT.001` | `R=-H_geom-sigma_ab e^a e^b` | L^-1 | FLRW `R=-H_geom`; Minkowski `R=0` |
| `BASS.PHOTON.DIRECTION_FLOW.001` | shear + class-B vector + triad rotation + structure-tensor flow | L^-1 | `e_a V^a=0`; zero coefficients imply `V^a=0` |

## Audit findings

- **P0:** none in the bounded six-formula mathematics.
- **P1 closed:** stale 02D predecessor pin; cross-language JSON escaping caused five of six initial semantic hashes to disagree with the repository Wolfram canonicalizer. Hashes were re-sealed using the exact `CanonicalRawJSON` convention, including escaped `/`.
- **P1 open:** native repository-file Wolfram/WLT replay has not yet been run. The connected stateless exact oracle is not represented as a native package replay.
- **P2:** the zero-boost aberration formula contains an apparent `0/0`; the exported domain explicitly uses its continuous extension, and the finite limit is checked.

## Verdict

`PASS_CANDIDATE`: the bounded formula set is mathematically coherent and mutation-sensitive. Terminal stage admission still requires exact-head CI and native repository replay/readback.

---

# SYNC-MAP-02E PHYS-MATH-CODE audit

## Equation-to-code map

| Contract layer | File | Function |
|---|---|---|
| machine authority candidate | `BASS_SHARED_FRAME_PHOTON_EXPORT.json` | six EquationIR records, hashes, dependencies, consumers, scope |
| Python fail-closed validator | `scripts/verify_sync_map02e_shared_export.py` | `validate_export` |
| Python hostile tests | `tests/test_sync_map02e_shared_export.py` | 13 stdlib unit tests |
| Wolfram package validator | `wolfram/BASS/Kernel/IR/SharedFramePhotonExport.wl` | `SharedFramePhotonExportQ` |
| Wolfram exact residual oracle | same module | `SharedFramePhotonExactResiduals` |
| Wolfram WLT surface | `wolfram/BASS/Tests/SYNCMAP02ESharedFramePhotonExport.wlt` | canonical and mutation tests |
| plot generator | `scripts/render_sync_map02e_graph.py` | deterministic dependency/consumer SVG |

## TDD evidence

The RED commit is

```text
d4770f872addc9b73712babb44c675fbda2a19cb
```

with workflow run `33607408741`. It failed at test import because the production verifier did not yet exist. This is the intended missing-feature failure, not a post-hoc passing test.

During local GREEN implementation, the canonical test first exposed an internal dependency-order mismatch for the solid-angle record. The record was corrected to canonical sorted dependency order rather than weakening the test.

## Validation coverage

The Python validator checks:

- exact source parent and successful 02C head;
- repaired 02D payload/tree/final-receipt identity and rejection of the stale pin;
- exact six-formula identity, terms, integer AST coefficients, dimensions, owner, consumers;
- four internal and three external dependency edges, edge closure, and acyclicity;
- per-record dependencies and cross-repository consumer union;
- Wolfram-compatible semantic projection and SHA-256 for every formula and the registry;
- output/global-tilt/collision/background/statistics scope firewall;
- narrowed claim boundary.

The Wolfram validator independently rechecks EquationIR shape, exact signatures, dimensions, consumers, per-record dependencies, canonical hashes, predecessor identity, dependency graph, scope firewall, claim boundary, and exact-zero residuals.

## Remaining verification gap

GitHub CI can run Python, deterministic SVG regeneration, JSON parsing, and exact-base text hygiene. The hosted workflow does not contain a Wolfram kernel. Therefore:

```text
connected stateless exact Wolfram oracle  PASS
cross-language canonical hashes           PASS
native repository package/WLT replay      NOT RUN
```

No terminal completion claim is authorized until the native WLT surface is replayed in the pinned Wolfram environment and its receipt is bound to the candidate head.

## Verdict

`PASS_CANDIDATE_WITH_ONE_P1_VERIFICATION_GAP`. No solver, provider, runtime transport, or consumer semantic-equivalence claim follows from this export.

---

# SYNC-MAP-02E plot-driven CRAG audit

## Figure evolution

1. The first graph used a fan-out of consumer edges and was rejected for visual spaghetti and ambiguous crossings.
2. The second graph separated formula dependencies from a consumer matrix, but the rightmost matrix was clipped by the 1200-pixel view box.
3. The final graph uses a 1400 x 650 view box, a two-panel structure, solid internal arrows, dashed pre-existing BASS.GEO dependencies, and an explicit consumer matrix.

## CRAG result

- **Correctness:** arrows are explicitly dependent-to-required; frame and photon namespaces are visually separated; external geometry dependencies are not falsely included in the six-node registry.
- **Retrieval:** the six rows reproduce the frozen 02C union with the repaired 02D consumer binding.
- **Augmented:** the matrix reveals, without edge clutter, that REI consumes only energy/direction flow while HTT consumes only frame formulas in this stage.
- **Generation:** any later consumer-binding change predicts a matrix-byte change and must trigger the deterministic regeneration check.

## Adversarial reading

The most likely misreading is to interpret the graph as a solver pipeline. The footer therefore states that background providers, global tilt, finite-electron collision, recombination/reionization microphysics, solver runtime, likelihood, and science promotion are excluded.

## Print/readability verdict

`PASS` as a double-column or digital audit figure. It is not approved as a single-column science figure; at approximately 90 mm the matrix text would be unnecessarily small. This limitation has no bearing on the machine export.
