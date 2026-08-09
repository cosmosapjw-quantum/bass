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

### Primary scientific sources

- [Ellis and MacCallum (1969)](https://projecteuclid.org/journals/communications-in-mathematical-physics/volume-12/issue-2/A-class-of-homogeneous-cosmological-models/cmp/1103841345.pdf):
  spatially homogeneous classification and orthonormal-frame foundation.
- [Ellis and van Elst (1998)](https://arxiv.org/abs/gr-qc/9812046) and
  [van Elst and Uggla (1996)](https://arxiv.org/abs/gr-qc/9603026): 1+3 kinematics,
  orthonormal-frame variables, gauge rotation, and convention hazards.
- [Challinor (2000)](https://arxiv.org/abs/astro-ph/9911481): exact polarized radiation
  tensor, Thomson source, and frame transformations. Its propagated almost-FLRW
  hierarchy is not an exact nonlinear Bianchi hierarchy and its signature differs from
  BASS.
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
3. Its canonical family registry contains eleven IDs
   `I, II, III, IV, V, VI_0, VI_h, VII_0, VII_h, VIII, IX`, treats III as the exact
   `VI_h(h=-1)` alias, and requires a distinct exact `VI_-1/9` branch.
4. The legacy Rust fragment exposes `bianchi.backend`/`bianchi_rustcore`, five-component
   class-A/class-B charts, and diagonal Bianchi-I ray/optical kernels. It silently
   normalizes several dimensional quantities, uses `kappa=1/h` in its class-B chart, and
   has incomplete failure validation. Its historical tolerance values are not canonical.
5. The low-ell audit rubric asks auditors to inspect perturbation/statistics paths, while
   the high-ell harness permanently excludes spatial perturbations, stochastic primordial
   sectors, likelihoods, and data fitting from v1.0. This must be resolved at the product
   boundary rather than hidden in implementation.
6. No inspected primary source supplies a complete exact, nonlinear, polarized,
   homogeneous Bianchi Einstein--Boltzmann solver. Independent layers must therefore be
   derived, convention-translated, and characterized separately.

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
5. The Route A v1 scope candidate makes global tilt, photon `I/E/B`, collisionless exactly
   massless neutrinos, exact electron-frame Thomson scattering, recombination,
   reionization, and the output-only observer adapter required. Photon `V`, spatial
   perturbations, and statistical inference are outside v1. This new choice does not alter
   the sealed historical OD001--OD004 state.

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
- The OpenAI-side snapshot/object store may no longer exist. Only OpenAI can establish
  that; the local classification remains `MISSING_OR_MASKED`.

## Confidence

- **High:** repository state, artifact classification, harness locks, family registry,
  and source-convention conflicts.
- **Medium:** proposed software boundaries and milestone order; these are new design
  choices rather than recovered facts.
- **Low:** recoverability of the original managed runtime, because no public retention or
  restoration guarantee establishes it.

## Recommended next module

Write and owner-review the A0 authority/characterization design. Do not write production
solver code until the exact A0 commit is approved and a separate implementation plan is
accepted.

## Checkpoint

- Active sequence: `context-survey -> brainstorming/design -> writing-plans`.
- Evidence gates satisfied: recovery boundary, artifact/source hierarchy, convention
  conflicts, scope conflict, and candidate route comparison are documented above.
- Next required skill: `writing-plans`, only after owner review of the A0 design commit.
- Next check: verify that the owner accepts the namespace, scope boundary, convention
  ledger, characterization corpus, and unresolved transport gates.
- Continuation action: ask user after committing, pushing, and bundling the design
  candidate.
- Next / upcoming task: owner review of the exact A0 candidate commit.
