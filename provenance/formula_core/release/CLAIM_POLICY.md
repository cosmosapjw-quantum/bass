# Bianchi CC22 claim policy and scope release gate

## Release verdict

```text
FORMULA-LEVEL CLAIM POLICY = FROZEN
NATIVE END-TO-END WOLFRAM REPLAY HERE = UNVERIFIED
DIRECT MakeTraceless RESULT AUTHORITY = NOT CLAIMED
SOLVER / FULL-COMPTON / MICROPHYSICS / INFERENCE READINESS = NOT CLAIMED
```

This policy freezes what may and may not be claimed from the closed CC00--CC21 formula-only core. It does not reopen or alter a theorem.

## Canonical release language

We present an exact formula-level treatment of homogeneous, nonperturbative polarized photon Liouville transport on the eleven public Bianchi backgrounds, with exceptional VI_-1/9 retained as a dynamical supplement rather than a twelfth algebra type. Under a cold, non-tilted electron-rest Thomson collision assumption, the result includes generic all-rank scalar and polarized PSTF hierarchies, an equivalent project-spin/Wigner representation, and literal spectral and brightness branch formulae.

Reproducibility evidence is formula-level and uses a hybrid plugin-assisted clean orchestration: source-hash-validated fresh stateless-Wolfram receipts are combined with clean local symbolic orchestration. The shell command does not itself invoke the ChatGPT Wolfram plugin, and the packaged native wolframscript path was not executed in this environment. Do not describe this as a native end-to-end Wolfram replay completed here. The xTensor/xCoba/xTras packages and the MakeTraceless symbol/definition were verified; the authority trace-free identity was checked independently with xTensor rather than by a direct MakeTraceless output replay.

Recoil and thermal Comptonization, Klein-Nishina corrections, finite electron tilt, recombination/reionization microphysics, hierarchy truncation, line-of-sight integration, solver construction, numerical evolution, observable outputs, likelihoods and inference are outside the closed core.

## Allowed headline claims

| ID | Claim | Closed evidence | Minimal conditions |
|---|---|---|---|
| `HC01` | Exact homogeneous nonperturbative polarized Liouville transport | CC03, CC04 | Spatial homogeneity.; Metric signature (-,+,+,+), epsilon_123=+1, and the locked screen/tetrad conventions.; Sufficient regularity for the distribution and angular projections.; Collision scope, when present, is the cold non-tilted electron-rest Thomson block. |
| `HC02` | Cold, non-tilted electron-rest Thomson scattering | CC05 | Cold electron distribution.; Electron bulk tilt is zero in the authority frame.; Elastic Thomson limit. |
| `HC03` | Generic all-rank scalar and polarized PSTF hierarchy | CC06, CC07, CC08, CC09 | Scalar multipoles have ell>=0; polarized multipoles have ell>=2.; Endpoint condition [epsilon_gamma X_Aell]_0^infinity=0 for bolometric integration.; Finite-rank and random checks are regression evidence only, not the all-rank authority. |
| `HC04` | Equivalent project-spin/Wigner representation | CC10, CC11 | ProjectSpinY[s]=StandardSpinY[-s].; Wigner ordering is (ell_out,L_geometry,ell_in).; The common-map sign is applied exactly once. |
| `HC05` | Explicit eleven public Bianchi branches | CC13, CC14, CC15, CC17, CC19 | Public label III is retained while its computational equivalence to VI_h(h=-1) is recorded.; Generic class-B N23 remains until an explicit proper-frame gauge is chosen.; Generic Type-IX N_STF is not replaced by its optional closed-FLRW locus. |
| `HC06` | Exceptional VI_-1/9 dynamical supplement | CC16, CC17, CC19 | The supplement is not counted as a twelfth Bianchi algebra type.; The exceptional algebraic and momentum constraints are retained.; The witness gauge is not promoted to the full branch. |
| `HC07` | Formula SSOT and literal formula atlas | CC18, CC19 | All 96 explicit equations and 824 atomic term/source rows are present.; No coefficient is hand-edited outside the frozen registry.; CC12-SA-001 remains visible. |
| `HC08` | Formula-level hybrid plugin-assisted replay evidence | CC20, CC21-P1-001, CC21-P2-001 | The shell orchestration validates fresh checksum-gated plugin receipts but does not itself invoke the ChatGPT Wolfram plugin.; The packaged native wolframscript path was not executed in this environment.; xTensor/xCoba/xTras and the MakeTraceless symbol/definition were verified; the authority trace-free identity was independently checked with xTensor rather than by a direct MakeTraceless output replay. |

Every headline must be paired with its minimal conditions and with the replay/hostile gates recorded in `Bianchi_CC22_Headline_Claim_Evidence_Map.json`.

## Forbidden claims

| ID | Forbidden phrase or claim family | Reason | Named negative gate |
|---|---|---|---|
| `FC01` | `full Einstein--Boltzmann solver` | No Einstein/background evolution, truncation, numerical integrator, line-of-sight or output pipeline is part of the formula core. | `NC01_FULL_EINSTEIN_BOLTZMANN_SOLVER` |
| `FC02` | `solver-ready` | The closed work is formula-level; solver interfaces and numerical stability are unverified. | `NC03_SOLVER_READY` |
| `FC03` | `numerically mature` | No production numerical evolution or convergence campaign is included. | `NC04_NUMERICALLY_MATURE` |
| `FC04` | `output-ready` | No observable-output or line-of-sight pipeline is closed. | `NC05_OUTPUT_READY` |
| `FC05` | `perturbation-ready` | No perturbation implementation or gauge-ready solver contract is closed. | `NC06_PERTURBATION_READY` |
| `FC06` | `statistics-ready` | No likelihood, covariance or inference layer is included. | `NC07_STATISTICS_READY` |
| `FC07` | `all microphysics exact` | The collision authority is cold electron-rest Thomson only; recombination and other microphysics are excluded. | `NC02_ALL_MICROPHYSICS_EXACT` |
| `FC08` | `full Compton exact` | Thermal, recoil and generalized Compton/Kompaneets effects are outside scope. | `NC08_FULL_COMPTON_EXACT` |
| `FC09` | `Klein--Nishina complete` | Klein-Nishina corrections are excluded. | `NC09_KLEIN_NISHINA` |
| `FC10` | `finite-electron-tilt complete` | The collision theorem assumes non-tilted electrons. | `NC10_FINITE_TILT` |
| `FC11` | `recombination/reionization complete` | Atomic recombination and reionization modules are separate future extensions. | `NC11_RECOMBINATION_REIONIZATION` |
| `FC12` | `line-of-sight complete` | No line-of-sight integration is implemented. | `NC12_LINE_OF_SIGHT` |
| `FC13` | `inference-ready` | No parameter inference or statistical release is included. | `NC13_INFERENCE_READY` |
| `FC14` | `native end-to-end Wolfram replay completed here` | CC20 used hybrid plugin-assisted orchestration; the native wolframscript path was packaged but not executed here. | `NC14_NATIVE_WOLFRAM_OVERCLAIM` |
| `FC15` | `direct MakeTraceless API replay is the authority witness` | xTras availability and definition were verified, while the authority trace-free identity was checked independently with xTensor. | `NC15_MAKETRACELESS_OVERCLAIM` |

The exact insertions `full Einstein--Boltzmann solver` and `all microphysics exact` are release-blocking and must fail `NC01_FULL_EINSTEIN_BOLTZMANN_SOLVER` and `NC02_ALL_MICROPHYSICS_EXACT`, respectively.

## Future extensions, not current claims

| ID | Extension | Minimum new evidence required |
|---|---|---|
| `EX01` | Finite-electron-tilt collision operator | Derive and validate the boosted electron-rest collision operator with independent frame and conservation gates. |
| `EX02` | Recombination and reionization microphysics | Couple checksum-addressed atomic/radiative-transfer modules without altering the closed formula core. |
| `EX03` | Hierarchy truncation and line-of-sight integration | Define closure, truncation-error and gauge/frame contracts, then validate against exact hierarchy limits. |
| `EX04` | Numerical solver and observable outputs | Implement a stable solver, convergence tests, restart state, output normalization and independent regression. |
| `EX05` | Thermal/recoil/Klein-Nishina Compton physics | Replace the Thomson-only collision block with a separately derived and source-regressed collision authority. |
| `EX06` | Likelihood and statistical inference | Require validated observables, covariance, data provenance and inference-specific audits. |

Finite electron tilt and line-of-sight integration are separate future extensions. They cannot be implied by the present formula closure.

## CC21 narrowing propagation

1. `CC21-P1-001`: use **hybrid plugin-assisted clean orchestration**. Do not claim a native end-to-end Wolfram replay was completed in this environment.
2. `CC21-P2-001`: claim xTensor/xCoba/xTras dependency and `MakeTraceless` symbol/definition availability, plus an independent xTensor trace-free witness. Do not claim a direct `MakeTraceless` output was used as the authority result.
3. The two qualifications must appear in the SSOT, literal atlas, abstract-ready prose and this policy.

## Source and amendment policy

- `CC12-SA-001` is an explicit project-scoped source amendment and may not be silently absorbed.
- MGE supports the exact nonlinear scalar-intensity regression in its declared variables; it is not the source of the complete polarized hierarchy.
- Challinor supplies general-spacetime PSTF polarization structure while the displayed hierarchy is almost-FRW.
- Pontzen--Challinor is a nearly-FRW Bianchi regression and cannot delete exact nonlinear project channels.
- Pitrou's broader thermal/recoil Compton treatment defines an out-of-scope extension boundary, not a license to call the present collision block full Compton.

## Nonblocking release notes

- The CC20 residual heatmap has a low-contrast bottom annotation; its absolute scale and hash audit remain valid.
- The long SSOT retains overfull equation boxes; the compact atlas is the publication-readable literal formula artifact.

## Transition condition

CC23 may package the final formula-only closure only after the machine-readable allowed/forbidden policies, negative tests, cross-artifact propagation audit and final comparator all pass.
