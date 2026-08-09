# BASS Route A — A0 context survey

**Survey date:** 2026-08-10

**Decision supported:** define an evidence-safe authority and characterization baseline
before recreating any production solver code.

**Recovery base:** `c9cd8ecb8765649ace77ea8f22890ff4c24153eb`

## Evidence inspected

### Repository and recovered artifacts

- `docs/recovery/RECOVERY_BOUNDARY_20260810.md` and the recovery manifests: primary
  evidence for what survived the interrupted runtime.
- `docs/handoff/CLEAN_REBUILD_DECISION_20260810.md`: the previously proposed Route A/B/C
  decision boundary.
- `docs/specs/LOWELL_BIANCHI_FINAL_CODE_AUDIT_CONTRACT_20260810.txt`: byte-preserved
  user-supplied audit/acceptance rubric, SHA-256
  `de4c4d3d467e91d3f8420b5b2748ee7294db3ca8e809df4045b2f8c2d71881f1`.
- `harness/BASS_v1_background_highl_harness/`: a 72-file harness-only package. Its
  machine state says `solver_code_present=false`, `OD0=BLOCKED`, and all code/build/run
  authorizations false. Historical H0/H1 receipts do not validate a new solver.
- `recovered_sources/legacy_partial/`: an 18-file Rust/Python fragment. It contains real
  source bytes, but its Python baseline and most referenced modules are absent; it is not
  a canonical implementation.
- `docs/recovery/TRANSCRIPT_TASK3_10_STATE_20260809.md`: transcript-only behavioral
  invariants. These may seed future RED tests but are not source or PASS evidence.
- All 15 supplied project sources were inventoried. The research/coding harnesses are
  process templates; the Rust distribution and xAct archive are tools; none is a solver
  baseline.
- The later supplied `Bianchi_Core_Closure_Final.zip` is a formula/provenance package,
  SHA-256 `5909b3cd5632245ecc794532c0f569a59c6ee5a0e741bb307001f1c4e3087a0e`.
  Safe extraction, CRC scanning, its 179-row checksum ledger, and its 21-gate package
  verifier pass. Its formula Git bundle, SHA-256
  `de34f9b643e117f1f1078ce94a8c433d5e33f743a9daa856484c6c6ee537662e`,
  is a complete, prerequisite-free bundle for its advertised ref at commit
  `f63d5ae8faa2ea0c9afd2fee37fe2e7051cf16b0`, tree
  `c2b9e910f4b2a9c0be726059e32cc8411f65cced`; clone and `git fsck --full`
  pass. This does not prove completeness of the producer's original repository. These
  checks establish artifact integrity, not solver readiness or independent reproduction of
  every coefficient.
- The package records homogeneous spectral/bolometric `I,V,E,B` formulae for eleven public
  branches plus the exceptional `VI_-1/9` supplement: 96 equation rows and 824 atomic
  term/source rows. Its own claim policy excludes finite electron tilt, hierarchy
  truncation, recombination/reionization, line of sight, numerical evolution, outputs, and
  inference.
- Visual inspection found that the 45-page SSOT PDF, SHA-256
  `cd9b4e8e092faf9de580c7949ab5af296ed9449af112e01c0f4785ff9ed8045e`,
  clips literal branch equations at the right page edge, including pages 17, 20, 43, and
  44. Formula registries and TeX/Markdown source, not that PDF, must carry coefficients.

### Primary scientific sources

- [Ellis and MacCallum (1969)](https://projecteuclid.org/journals/communications-in-mathematical-physics/volume-12/issue-2/A-class-of-homogeneous-cosmological-models/cmp/1103841345.pdf):
  spatially homogeneous classification and orthonormal-frame foundation.
- [Ellis and van Elst (1998)](https://arxiv.org/abs/gr-qc/9812046) and
  [van Elst and Uggla (1996)](https://arxiv.org/abs/gr-qc/9603026): 1+3 kinematics,
  orthonormal-frame variables, gauge rotation, and convention hazards.
- [Challinor (2000)](https://arxiv.org/abs/astro-ph/9911481): exact polarized radiation
  tensor, Thomson source, and frame transformations. Its propagated almost-FLRW
  hierarchy is not an exact nonlinear Bianchi hierarchy and its signature differs from
  BASS. It treats `I` and `V` as scalar sphere fields; its exact frame law remaps them
  without Stokes-sector mixing, and its Thomson source leaves circular polarization
  decoupled from `I/Q/U`.
- [Maartens, Gebbie, and Ellis (1999)](https://arxiv.org/abs/astro-ph/9808163): exact
  nonlinear unpolarized 1+3 intensity hierarchy with nonlinear Thomson terms; it
  explicitly does not close the polarized problem.
- [Pontzen and Challinor (2007)](https://arxiv.org/abs/0706.2075): Bianchi tetrads,
  group constants, exact geodesic energy/redirection ingredients, and linear near-FLRW
  polarization conventions. It distinguishes time-invariant and evolving orthonormal
  frames and is not a nonperturbative solver specification.
- [CAMB](https://github.com/cmbant/CAMB),
  [CLASS](https://github.com/lesgourg/class_public), and
  [HYREC-2](https://github.com/nanoomlee/HYREC-2): future pinned FLRW regression lanes,
  not authorities for nonlinear Bianchi geometry.
- [NIST 2022 CODATA](https://physics.nist.gov/cuu/pdf/JPCRD2022CODATA.pdf): physical
  constants and SI provenance.

### Official OpenAI incident guidance

- [OpenAI troubleshooting](https://learn.chatgpt.com/docs/reference/troubleshooting): in
  the affected chat, `/` feedback can share the existing session and returns a session ID.
- [OpenAI Support](https://help.openai.com/en/articles/6614161-how-can-i-contact-support):
  the Help Center chat bubble is the private support-contact route.
- [OpenAI sandbox documentation](https://learn.chatgpt.com/docs/sandboxing): ChatGPT Work
  executes commands in a managed isolated environment.
- The inspected official pages document reporting and limited recovery patterns, but no
  blanket SLA or guarantee for restoration of arbitrary historical Work artifacts.

## Findings

### Facts

1. The recovery base contains no `src/bass/` or `bianchi/full/` production tree. The eight
   reported Task 5--9 locators remain unresolved in accessible local objects, GitHub-
   advertised refs, and API-visible repository objects. Server-only snapshots and GitHub
   dangling objects were not enumerable, so the classification remains `MISSING_OR_MASKED`.
2. The preserved high-ell harness fixes useful conventions, family topology, evidence
   semantics, and claim firewalls, but contains no computational API, numerical golden
   corpus, or production tolerance values.
3. Its public family registry contains eleven labels/computational rows
   `I, II, III, IV, V, VI_0, VI_h, VII_0, VII_h, VIII, IX`, retains the public label III
   while mapping its computational algebra to exact `VI_h(h=-1)`, and requires a distinct
   exact `VI_-1/9` supplement/dispatch that is not a twelfth public row.
4. The legacy Rust fragment exposes `bianchi.backend`/`bianchi_rustcore`, five-component
   class-A/class-B charts, and diagonal Bianchi-I ray/optical kernels. It silently
   normalizes several dimensional quantities, uses `kappa=1/h` in its class-B chart, and
   has incomplete failure validation. Its historical tolerance values are not canonical.
5. The low-ell audit rubric asks auditors to inspect perturbation/statistics paths, while
   the high-ell harness permanently excludes spatial perturbations, stochastic primordial
   sectors, likelihoods, and data fitting from v1.0. This must be resolved at the product
   boundary rather than hidden in implementation.
6. No inspected primary source supplies a complete exact, nonlinear, polarized,
   homogeneous Bianchi Einstein--Boltzmann solver. The supplied formula package provides
   a specified project-derived infinite all-rank homogeneous photon operator in its declared
   zero-electron-tilt domain, but not background evolution, finite hierarchy closure,
   finite-tilt collision,
   recombination, or numerical integration. Independent layers must therefore be derived,
   convention-translated, and characterized separately.
7. The formula package uses ray-length rates: `H_geom`, `sigma`, `Omega_triad`, `a_B`,
   `n_B`, and `kappa` have dimension `m^-1`, with `(1/c) partial_t`. A0 uses physical
   proper-time `H`, `sigma`, and future `Omega` in `s^-1`. The required adapter is
   `H_core=H_A0/c`, `sigma_core=sigma_A0/c`, `Omega_core=Omega_A0/c`; proper-time
   structure/collision rates are `c a_B`, `c n_B`, and `c kappa`.
8. Photon `V` is physically allowed in tilted Bianchi V and the other branches as nonzero
   initial or externally sourced circular polarization. Geometry and a finite boost can
   evolve or remap it. Standard geometric optics plus cold, unmagnetized Thomson scattering
   has no `I/E/B -> V` source, so `V=0` remains an exact invariant subspace rather than a
   reason to remove the `V` sector.

### Interpretations adopted by the design candidate

1. Route A should create a new `bass` authority path rather than reconstructing the lost
   `bianchi.full` signatures from conversation text.
2. The low-ell and high-ell materials should become two acceptance profiles over one
   homogeneous geometry/transport core. Spatial perturbation and statistical-fitting
   requirements remain outside Route A v1.0 and cannot block the homogeneous core.
3. Python/NumPy float64 should be the mandatory transparent reference lane. Rust can
   return only after componentwise differential equivalence to that lane; the recovered
   fragment stays read-only.
4. Registry presence must never imply family evolution support. Capability is promoted
   per family and per layer: registry, geometry, background, transport, output, and
   statistics.
5. The Route A v1 scope candidate makes global tilt, photon `I/V/E/B`, collisionless exactly
   massless neutrinos, exact electron-frame Thomson scattering, recombination,
   reionization, and the output-only observer adapter required. The baseline `V=0`
   invariant and nonzero-`V` evolution lanes are both required. Spatial perturbations and
   statistical inference remain outside v1. This new choice does not alter the sealed
   historical OD001--OD004 state.
6. The formula bundle should be pinned as a durable, provenance-locked formula input, not
   copied coefficient-by-coefficient from PDF and not treated as executable solver evidence.
   Project-derived nonlinear polarized coefficients require an independent projection or
   angular-quadrature reproduction lane.

## Alternatives and trade-offs

| Route | Benefit | Load-bearing risk | Decision |
|---|---|---|---|
| New `src/bass` reference core | Lowest provenance risk; clean convention and API ledger | More initial design work | **Selected** |
| Recreate `bianchi.full` first | Superficially resembles the interrupted run | Invents missing Task 3--5 APIs and may be mistaken for recovery | Rejected as canonical route |
| Overlay the Rust fragment | Reuses preserved code bytes | Missing baseline, incompatible normalization, incomplete scope and errors | Quarantined reference only |

## Assumptions and unknowns

- Historic owner decisions OD001--OD004 remain unresolved as historical harness state.
  The A0 candidate makes new Route A defaults but does not rewrite those sealed receipts.
- Exact production high-ell tolerances cannot be selected before a real hierarchy and a
  convergence characterization corpus exist.
- A four-dimensional volume-form sign, spin-basis phase, Stokes-`U` sign, optical-depth
  direction, and sky-direction adapter are deliberately gated before transport work.
- The formula registry contains provenance-rich formula fragments, not a frozen executable
  coefficient AST or runtime gauge selector. The implementation plan must choose an
  independently checked parser/compiler or re-derivation path and keep exact `h=-1/9`
  exceptional dispatch out of the generic `VI_h` runtime path.
- The OpenAI-side snapshot/object store may no longer exist. Only OpenAI can establish
  that; the local classification remains `MISSING_OR_MASKED`.

## Confidence

- **High:** repository state, artifact hashes/integrity, artifact classification, harness
  locks, family registry, photon-`V` scope logic, and source-convention conflicts.
- **Medium:** proposed software boundaries and milestone order; these are new design
  choices rather than recovered facts.
- **Low:** recoverability of the original managed runtime, because no public retention or
  restoration guarantee establishes it.

## Recommended next module

Owner-review the revised A0 authority/characterization design and photon formula-core
intake. Do not write production solver code until the exact revised A0 commit is approved
and a separate implementation plan is accepted.

## Checkpoint

- Active sequence: `context-survey -> brainstorming/design -> writing-plans`.
- Evidence gates satisfied: recovery boundary, formula-package integrity and visual audit,
  artifact/source hierarchy, convention and unit conflicts, photon-`V` scope correction,
  and candidate route comparison are documented above.
- Next required skill: `writing-plans`, only after owner review of the A0 design commit.
- Next check: verify that the owner accepts the namespace, scope boundary, convention
  ledger, characterization corpus, and unresolved transport gates.
- Continuation action: ask user after committing, pushing, and bundling the design
  candidate.
- Next / upcoming task: owner review of the exact A0 candidate commit.
