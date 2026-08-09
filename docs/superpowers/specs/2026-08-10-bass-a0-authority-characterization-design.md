# BASS Route A — A0 Authority and Characterization Freeze Design

**Document status:** `A0A_SPEC_CANDIDATE`

**Milestone-status rule:** this label identifies the intended content; it does not assert
that review, commit, push, or bundle gates have passed. Those facts are established only
by the external, hash-bound A0A delivery receipt.

**Base commit:** `c9cd8ecb8765649ace77ea8f22890ff4c24153eb`

**Scope:** design and characterization contract only; no production solver code

**Promotion rule:** this document becomes `A0_FROZEN` only after the owner explicitly
approves the exact commit SHA containing it. A later amendment requires a new commit,
reason, and downstream invalidation note.

**Normative companions:**

- `docs/a0/FIRST_SLICE_API_V1.md` and `contracts/a0/first_slice_api_v1.json`;
- `contracts/a0/route_a_v1_scope.json`;
- `docs/a0/EQUATION_LEDGER_V1.md`;
- `contracts/a0/characterization_v1.json`.

The Markdown files are the human review surface. The JSON files are the machine-readable
contract fixtures. A disagreement fails closed; neither representation silently overrides
the other.

## 1. Purpose and identity

Route A is an evidence-first clean rebuild after exact recovery of the interrupted Task
3--10 implementation failed. `A0` means **Route A authority and characterization gate**.
It is new and must not be conflated with the historical harness nodes `OD0` or `IA0`.

A0 has two sub-gates:

1. `A0A_CANDIDATE`: evidence survey, design and all normative companions, incident
   request, manifest, hash-bound independent review, commit, remote verification, and
   bundle exist.
2. `A0B_OWNER_FREEZE`: the owner approves the exact candidate commit. Only then may an
   implementation plan be written. Production code, build, solver execution, dependency
   installation, or scientific claim promotion is not authorized by A0A.

## 2. Evidence boundary

### Governing inputs

1. This approved A0 design, once promoted, governs the new Route A tree.
2. The user-supplied low-ell audit contract governs hostile acceptance and claim honesty,
   but is not an API or equation source.
3. The preserved high-ell JSON contracts supply candidate conventions, family topology,
   convergence structure, and evidence semantics. Their historical receipts do not
   validate new code.
4. Primary literature supplies equations only through an explicit convention-translation
   ledger.
5. Fresh analytic, symbolic, and numerical characterization evidence validates each new
   implementation layer.

### Non-governing inputs

- Transcript Task 6--10 behavior is RED-test seed only.
- `recovered_sources/legacy_partial/` is read-only comparative material only.
- `bianchi_phase_r` may be a pinned, read-only oracle only; it cannot be imported into the
  production dependency graph.
- README claims, historical test counts, performance numbers, and conversation summaries
  are not implementation evidence.

## 3. Selected design decisions

### A0-D001 — Canonical namespace

The production namespace is `bass`, installed from `src/bass/`. No new production module
is created under `bianchi.full`. If compatibility is later required, a separately tested
`bianchi` adapter may call public `bass` APIs; it may not contain an independent physics
path or silently change units, signs, shapes, tolerances, or errors.

### A0-D002 — First executable slice

The first implementation slice is:

`convention types -> exact family registry -> FLRW state -> Hamiltonian/continuity/Raychaudhuri residuals -> analytic characterization cases`.

It does not restore the five transcript-named `bianchi.full` modules, integrate an angular
hierarchy, perform recombination, or fit data. The next geometry slice after this one is
Bianchi I plus Kasner and anisotropic-redshift characterization.

### A0-D003 — Family scope

All eleven canonical family IDs and the exact exceptional `VI_-1/9` branch exist in the
registry from the first slice. Runtime support is promoted independently. A registry row
alone is never called background-ready.

Canonical topology:

- Class A: `I`, `II`, `VI_0`, `VII_0`, `VIII`, `IX`.
- Class B: `III`, `IV`, `V`, generic `VI_h`, `VII_h`.
- `III` is the exact `VI_h(h=-1)` alias and is not double-counted.
- Generic `VI_h` covers the real domain `h<0`, excluding the exact values `-1` and
  `-1/9`; generic `VII_h` covers the real domain `h>0`.
- `VI_-1/9` is an exact exceptional branch with its own dispatch and evidence.
- `VI_0` and `VII_0` are exact boundary branches. Exact aliases, boundaries, and the
  exceptional branch use tagged rational dispatch. A finite binary64 value may parameterize
  a generic branch, but it never selects a special branch by equality or proximity.

### A0-D004 — Low-ell/high-ell relationship

BASS Route A v1.0 is one **exact/nonlinear spatially homogeneous** Einstein--matter--
radiation solver with configurable finite angular resolution. The low-ell and high-ell
materials are acceptance profiles over the same core, not separate solvers.

Spatial `k` modes, SVT/gauge perturbations, stochastic primordial spectra, transfer
functions, likelihoods, posteriors, and real-data fitting are outside Route A v1.0. Any
section of the low-ell hostile-audit rubric that presupposes those paths is marked
`NOT_APPLICABLE_V1`, not silently implemented or used to weaken the homogeneous checks.
Deterministic Bianchi sky outputs may be added later, but statistics readiness remains a
separate gated layer.

### A0-D005 — Reference and accelerated backends

The mandatory authority implementation is transparent Python/NumPy float64. A Rust/PyO3
backend is optional and non-release-blocking until a later owner decision. It must consume
the same serialized state and pass componentwise same-equation, same-input, same-tolerance,
same-output differential tests. The supplied Rust fragment remains `READ_ONLY_REFERENCE`.

### A0-D006 — Repository and release status

The GitHub repository remains public as authorized. Public visibility does not imply
scientific release, API stability, or publication-grade status. No credential, proprietary
data, observational dataset, or unreviewed runtime capture may be committed.

### A0-D007 — Route A v1 sector scope

The first executable slice is background-only, but the Route A v1 target is fixed now.
Global tilt, photon `I/E/B`, collisionless exactly massless neutrinos, exact electron-frame
Thomson scattering, recombination, reionization, and the output-only local-observer adapter
are `IN_V1_REQUIRED` and release-blocking after their respective gates. Photon `V` is
`OUT_OF_SCOPE_V1`. Every required sector begins `LOCKED_PENDING_EVIDENCE`; inclusion is a
scope commitment, not an implementation claim.

The complete disposition, dependencies, enabling gate, and claim effect are frozen in
`contracts/a0/route_a_v1_scope.json`. This new Route A decision does not mutate or satisfy
historical OD001--OD004, OD0, or IA0. A0B authorizes planning only. Production-source
creation requires a later plan approval and explicit `A1_IMPLEMENTATION_AUTHORIZATION`.
Local observer boost is never accepted as a substitute for global tilt.

### A0-D008 — External oracles

`bianchi_phase_r` commit `539fcd6acc81dfd19d05951c2c5cbc3602eda077` is a candidate
read-only oracle. CAMB, CLASS, HYREC-2, and xAct are also oracle lanes only after exact
versions/commits, inputs, conventions, and output units are pinned. Agreement between two
lanes that share a derivation is not independent proof.

### A0-D009 — Versioned first-slice API

The only first-slice public import surface is `bass.api.v1`; `bass.__init__` does not
re-export provisional internals. Exact symbols, signatures, records, units, status/error
semantics, family parameter dispatch, immutable ownership, and canonical serialization are
frozen in `docs/a0/FIRST_SLICE_API_V1.md` and
`contracts/a0/first_slice_api_v1.json`. Implementation planning may decompose internals but
may not invent or change that public surface without an owner-reviewed A0 amendment.

## 4. Authority hierarchy and equation ledger

Each executable equation receives a stable ID and a ledger row with:

- project equation in BASS conventions;
- primary source and exact equation/section locator;
- source signature, Riemann sign, orientation, frame, normalization, and units;
- explicit algebraic transformation into BASS conventions;
- dimensional check;
- symbolic identity/proof artifact when applicable;
- analytic characterization IDs;
- code symbol and test locator after implementation;
- invalidation dependencies.

The equations frozen by the first slice are not deferred: their IDs, exact primary-source
equation/page locators, validity regimes, geometrized-to-SI transformations, dimensional
checks, and mutation checks are present in `docs/a0/EQUATION_LEDGER_V1.md`. In particular,
the FLRW `H`-dot residual is a derived combination of the Raychaudhuri and Gauss equations,
not a claimed verbatim transcription of either source.

Authority order for a conflict is:

1. owner-approved BASS convention and scope lock;
2. algebraically derived project equation with a reviewed conversion ledger;
3. primary literature in its stated validity regime;
4. independently implemented analytic/CAS/numerical oracle;
5. quarantined historical code or transcript seed.

No source is copied across a signature, handedness, frame, or normalization boundary
without a visible adapter. Challinor's exact polarization tensor and collision source, for
example, are valuable primary sources but use a different metric signature from BASS; the
almost-FLRW propagated hierarchy in that paper is not promoted to an exact Bianchi
hierarchy.

## 5. Convention and dimensional lock

### 5.1 Spacetime and frame

| Item | BASS Route A convention |
|---|---|
| Metric | `(-,+,+,+)` |
| Normal | future-directed `n^a n_a=-1` |
| Spatial projector | `h_ab=g_ab+n_a n_b` |
| Spatial orientation | `epsilon_123=+1` in the declared oriented orthonormal spatial frame |
| Riemann | `R^rho_{ sigma mu nu}=partial_mu Gamma^rho_{nu sigma}-partial_nu Gamma^rho_{mu sigma}+Gamma^rho_{mu lambda}Gamma^lambda_{nu sigma}-Gamma^rho_{nu lambda}Gamma^lambda_{mu sigma}` |
| Ricci | `R_sigma nu=R^rho_{ sigma rho nu}` |
| Einstein equation | `G_ab+Lambda g_ab=(8 pi G/c^4) T_ab` |
| Physical derivative | `D_t f := c n^a nabla_a f`; every overdot below means `D_t` |
| Kinematic expansion | `Kkin_ab := c h_a^c h_b^d nabla_c n_d = H h_ab + sigma_ab` |
| ADM relation | `KADM_ab := -h_a^c h_b^d nabla_c n_d = -Kkin_ab/c` |
| Shear scalar | `sigma2=(1/2) sigma_ab sigma^ab` |

Here `n^a` is a dimensionless unit normal, so `n^a nabla_a` has inverse-length
dimension and `D_t` is differentiation with respect to physical proper time in seconds.
`Kkin_ab` is a rate, not ADM extrinsic curvature. Its trace is `Theta`,
`H := Hgeom := Theta/3`, and
`sigma_ab := Kkin_ab-H h_ab` is spatial, symmetric, and trace-free. The homogeneous
normal is hypersurface orthogonal, so its vorticity vanishes. This definition fixes the
sign that later shear propagation and anisotropic redshift must use.

The induced derivative is
`D_a X... := h_a^b h... nabla_b X...`. Its intrinsic Riemann tensor uses the same
displayed Riemann sign with `D` in place of `nabla`; `R3` is the corresponding scalar
contraction with `h_ab`. Normal-frame matter projections are
`rho_E := T_ab n^a n^b`, `p := (1/3) h^ab T_ab`,
`q_a := -h_a^c T_cd n^d`, and the spatial symmetric trace-free projection `pi_ab`.
Thus tilted matter enters `rho_E` through the normal-frame projection rather than a
matter-rest-frame density.

The preserved frame-connection display notation is retained only through named slots:

`GammaFrame[derivative=a, field=b, inner=c] := g(e_c, nabla_{e_a} e_b)`.

Array code must use those semantic axis names. It may not infer the derivative or output
slot from conventional Christoffel index placement. Coordinate Christoffels are a distinct
object with named slots `[output, derivative, field]`.

### 5.2 Homogeneous structure constants

The canonical commutator decomposition is

\[
C^\gamma{}_{\alpha\beta}
=\epsilon_{\alpha\beta\delta}n_B^{\delta\gamma}
+a_{B\alpha}\delta^\gamma{}_\beta
-a_{B\beta}\delta^\gamma{}_\alpha .
\]

The registry uses the diagonal-`n_B` class-B gauge and
`a_B^2=h n_2 n_3`, with `n_B^{alpha beta}a_{B beta}=0`. A registry representative may
choose `n_B=diag(n_1,n_2,n_3)` and `a_B=(a,0,0)`, but A0 deliberately does not canonicalize
the remaining scale, eigenvalue ordering, or sign/parity orbit. Such a representative must
carry explicit frame-orientation and parity metadata and is not canonically serializable
until the geometry representative gate freezes those choices. The invariant
time-independent frame and the evolving physical orthonormal frame are distinct types. Any
map between them carries its matrix, determinant sign, parity action, and time dependence
explicitly.

### 5.3 Photon and frames

\[
p^a=\frac{\epsilon}{c}(n^a+e^a),\qquad e^a e_a=1,\qquad n_a e^a=0 .
\]

The normal-frame measured energy is `epsilon_n := -c p_a n^a`. Electron-frame and
observer-frame energies and directions are defined by separate future transport adapters;
neither may overwrite `epsilon_n` or the forward-model normal-frame direction.

Transport variables are normal-frame variables; collision and visibility variables are
electron-frame variables. Global tilt is forward-model state. A local observer boost is an
output-only map. The spin phase, Stokes-`U` sign, sky-direction reversal, spacetime volume
orientation, and optical-depth integration direction require a dedicated transport adapter
contract before any polarization/collision implementation.

### 5.4 Units

No implicit natural units are allowed. `c`, `G`, `hbar`, and `k_B` remain explicit where
dimensionally relevant. Physical constants come from a versioned CODATA record; `c` is
exact in SI and the uncertainty/source of `G` is retained as metadata.

Baseline physical dimensions are:

- `t`: s; `Hgeom`, `sigma_ab`: s^-1;
- `rho_energy`, `pressure`: J m^-3;
- spatial three-curvature `R3`: m^-2; `Lambda`: m^-2;
- photon energy `epsilon`: J; momentum components: kg m s^-1.

Expansion-normalized variables and a dimensionless time such as `d tau=Hgeom dt` may
exist only in an explicit adapter type. They cannot share a constructor with dimensional
state.

The dimensionful Hamiltonian residual is

\[
\mathcal R_H
=3H^2-\sigma^2+\frac{c^2}{2}\,{}^{(3)}R
-\frac{8\pi G}{c^2}\rho_{\rm E}-\Lambda c^2,
\qquad [\mathcal R_H]={\rm s}^{-2}.
\]

For FLRW, the first slice also characterizes

\[
\dot\rho_{\rm E}+3H(\rho_{\rm E}+p)=0,
\qquad
\dot H+\frac{4\pi G}{c^2}(\rho_{\rm E}+p)
-\frac{c^2}{6}\,{}^{(3)}R=0 .
\]

Every code path reports both the raw dimensionful residual and its declared dimensionless
normalization. A dimensionless number without the raw residual and scale is not evidence.

## 6. Canonical data and API contract

The normative public surface is the symbol/signature table in
`docs/a0/FIRST_SLICE_API_V1.md`, mirrored by the validated fixture
`contracts/a0/first_slice_api_v1.json`. The rules below constrain that table; they are not
permission for an implementation plan to add unnamed public symbols.

### 6.1 Types and shapes

- Reference real dtype: IEEE-754 binary64 (`float64`). Float32 is rejected at authority
  boundaries; extended/complex types require separate APIs.
- Spatial vector: exact shape `(3,)`.
- Spatial rank-2 tensor: exact shape `(3,3)`.
- Time series: leading exact time axis `(n_time, ...)`; implicit broadcasting is forbidden.
- Exact family aliases, boundaries, and exceptional values use `fractions.Fraction` tags.
  Generic `VI_h`/`VII_h` values may be `Fraction`, exact built-in `float`, or NumPy
  `float64`; floats parameterize only an already named generic family and never dispatch
  an alias, boundary, or exceptional branch.
- Bool, string, complex, object dtype, ragged arrays, nonfinite values, and hostile scalar
  or array subclasses are rejected at validated public boundaries.

Inputs are copied into canonical little-endian, C-contiguous binary64 storage and negative
zero is canonicalized to positive zero. Public arrays are deeply immutable: their storage
is backed by immutable bytes, not merely a writable array view whose `writeable` flag was
cleared. First-slice exported records contain scalar fields and immutable tuples, not public
arrays. Canonical framing and hashing are byte-for-byte frozen in the API companion;
canonical JSON is UTF-8, NFC, sorted-key, compact, contains no floating values, and forbids
NaN/Infinity.

Angular multipole memory layout is not frozen by the background slice. It requires its own
spin/multipole design gate; no provisional layout may become a public API by accident.

### 6.2 Error semantics

Invalid input never becomes a NaN row, empty successful history, silent fallback, or bare
`ok=true/false`. The public error taxonomy is:

- `ConventionError`: incompatible frame, sign, orientation, or unit adapter;
- `ShapeTypeError`: dtype, shape, subclass, serialization, or immutability violation;
- `DomainError`: invalid physical or exact-family domain;
- `ConstraintViolation`: finite input outside an explicitly enforced constraint budget;
- `IntegrationFailure`: numerical method fails or terminates outside its declared event;
- `ConvergenceFailure`: refinement contract fails;
- `UnsupportedSector`: requested capability has not been promoted;
- `BackendMismatch`: accelerated/reference lanes violate equivalence.

Expected numerical outcomes use a structured result status enum; programming/contract
violations raise typed exceptions. Every non-success includes a stable code and bounded
diagnostic metadata. Raw credentials, full hostile objects, and arbitrary exception text are
never serialized into evidence.

For the first slice specifically, finite residual misses return per-channel `FAIL`; boundary,
convention, type, nonfinite/subnormal, family-domain, and serialization violations raise the
exact exception/code mapping in the API companion. No error class or status member may be
selected ad hoc during implementation.

## 7. Characterization corpus

### 7.1 First-slice mandatory cases

| ID | Case | Exact conditions and expected identities |
|---|---|---|
| `A0-GEO-001` | Euclidean spatial frame | `h_alpha beta=delta_alpha beta`; projector/idempotence, symmetry, trace, and orientation identities |
| `A0-GEO-002` | Abelian type I registry | `a_B=0`, `n_B=0`, `C=0`, Jacobi exactly zero |
| `A0-GEO-003` | All-family structural registry | exact class, alias, boundary, h-domain, Jacobi, and no-floating-dispatch checks for all 11 IDs plus `VI_-1/9` |
| `A0-FLRW-001` | Minkowski | `H=sigma=R3=rho_E=p=Lambda=0`; all three residuals exactly zero |
| `A0-FLRW-002` | Flat de Sitter | `rho_E=p=R3=sigma=0`, `H=c sqrt(Lambda/3)`; Hamiltonian and H-dot residuals zero |
| `A0-FLRW-003` | Flat dust | `a proportional t^(2/3)`, `H=2/(3t)`, `p=0`, `rho_E=3 c^2 H^2/(8 pi G)` |
| `A0-FLRW-004` | Flat radiation | `a proportional t^(1/2)`, `H=1/(2t)`, `p=rho_E/3`, `rho_E=3 c^2 H^2/(8 pi G)` |
| `A0-FLRW-005` | Milne curvature sentinel | `a=c t`, `H=1/t`, `dH/dt=-1/t^2`, `R3=-6/(c^2 t^2)`, and `rho_E=p=sigma=Lambda=0`; all residuals zero |
| `A0-BI-001` | Kasner handoff case | `sum p_i=sum p_i^2=1`, `H=1/(3t)`, `sigma_i=(p_i-1/3)/t`, `sigma2=1/(3t^2)`, `R_H=0` |

`A0-FLRW-005` is mandatory in the first slice and is the curvature-sign/coefficient
sentinel. `A0-BI-001` is specified in A0 but implemented only in the next Bianchi-I slice.
Other open-FLRW embeddings, LRS families, class-B Codazzi propagation, exact `h` aliases, anisotropic
redshift, polarization, collision nullspaces, and hierarchy closure become mandatory in
their respective later slices.

### 7.2 Residual and tolerance semantics

Let `u=2^-53` be binary64 unit roundoff. Exact integer/rational registry identities and
structural zeros are tested exactly before conversion to floating point.

For an O(1) binary64 algebraic identity in the first slice, the characterization guard is

`abs(error) <= 64*u + 256*u*reference_scale`.

Here `reference_scale=max(1, fsum(abs(reference_term_i)))`; its term list must be declared by
the fixture rather than chosen after evaluation. This is a characterization threshold, not
a production ODE or high-ell tolerance.

For each first-slice dimensionful FLRW residual channel, the frozen budget is

`A_c=0` in the channel's units and `R_c=1024*u`.

A channel passes only

\[
|r_c|\le A_c+R_c S_c,
\]

where `A_c>=0`, `R_c>0`, and `S_c=fsum(abs(term_i))` over the fixed, ordered actual terms in
`contracts/a0/characterization_v1.json`. Residuals use `fsum(term_i)`. If `S_c=0`, PASS
requires `r_c==0.0` exactly and the relative value is `null`; otherwise the relative value
is `abs(r_c)/S_c`. Inputs and nonzero primitive/intermediate terms must be normal binary64
numbers. Zero is allowed; subnormal input or a nonzero result rounded into the subnormal
range returns `E_SUBNORMAL_UNSUPPORTED`. Nonfinite terms, overflow, scale-construction
failure, an empty term list/comparison, or underflow to zero fail closed. Signed zero is
canonicalized before hashing but both signs compare equal to exact zero.

The fixture also freezes negative controls: flipping or removing either curvature term
must fail the Milne case; changing the ADM/kinematic sign, an explicit `c` power, a source
projection, or a term-list member must fail at least one dimensional, analytic, or mutation
check. Zero-scale, cancellation, subnormal, overflow, nonfinite, and empty-comparison paths
are mandatory tests.

Production ODE, backend, quadrature, and high-ell values are not guessed from the legacy
fragment. They require empirical characterization, an analytic scale, and at least three
refinement levels. High-ell comparisons must use a common retained bulk, separate each
species/spin row, reserve a closure guard band, and inspect componentwise infinity norm,
Parseval-weighted L2, per-ell profile, outer-shell mass, and reflection indicators.

## 8. Claim and review policy

Capability states are independent:

`registry-only -> geometry-ready -> background-ready -> transport-ready -> output-ready -> statistics-ready`.

Each promotion requires fresh producer evidence, a different-lane review, a receipt bound
to exact governing hashes, and negative controls. Test count is never a substitute for a
physics claim. A family aggregate is true only when every claimed leaf is promoted.

The old high-ell harness remains an immutable historical/reference lane until an approved
transplant plan creates new fingerprints. Sealed H0/H1 PASS records are not reused after
relocation or any governed change.

## 9. Durable milestone protocol

Every Route A milestone must complete, in order:

1. pin the base commit and exact allowed path set;
2. create `manifests/A0_CANDIDATE_FILE_MANIFEST_V1.tsv` before commit. Its header declares
   its own path and `self_excluded=true`; sorted rows contain decimal byte count, lowercase
   SHA-256, and repository-relative path for every other changed file;
3. prove `changed_paths(base, staged_tree) = manifest_rows union {manifest_path}`, run fresh
   relevant validation, and stage only the allowed paths;
4. compute the staged Git tree OID. Independent reviewers inspect that exact staged tree and
   bind an external attestation to the base SHA, tree OID, manifest path/hash, reviewer lane,
   verdict, and findings. Any byte change invalidates the attestation and restarts steps 2--4;
5. commit from the unchanged index and prove the commit's parent equals the pinned base and
   its tree equals the reviewed tree. If a post-commit check rejects that candidate, retain
   the rejected commit under a non-milestone local ref and build a replacement candidate
   from the original pinned base in a fresh branch/worktree. Never amend, reset, force-push,
   or stack a repair on the rejected candidate; rerun steps 1--9 for the replacement;
6. non-force push to the milestone branch and require `git ls-remote` equality with the full
   intended SHA;
7. re-read every changed remote blob and compare it with the in-repository manifest, then
   separately record the self-excluded manifest's hash;
8. create and `git bundle verify` a bundle containing the milestone ref; clone-test it in a
   fresh temporary directory and recheck commit, tree, parent, and manifest/path-set equality;
9. deliver the bundle, its SHA-256, the external review attestation, and command evidence to
   the owner. An external delivery manifest excludes itself and its SHA-256 is communicated
   out of band.

This explicit self-exclusion is the only manifest exception; generated receipts cannot
silently expand it. No milestone may be reported durable before steps 1--9. `main`, release tags, and public
release claims are unchanged unless separately authorized. An OpenAI recovery result, if
it later appears, enters a quarantine branch and is compared; it never overwrites Route A.

## 10. A0 acceptance criteria

A0A passes only if:

- the context survey, this design, all normative companions, incident request, and
  self-excluding manifest exist in one commit;
- draft-token, contradiction, scope, link, JSON/source-anchor, and forbidden-claim scans
  pass;
- independent physics and evidence/API reviewers bind the final staged tree and find no
  unresolved P0/P1 issue; the commit tree must equal that reviewed tree;
- the branch push, every-remote-blob hash comparison, bundle verification, and clean
  clone-test pass;
- no production source, historical harness receipt, legacy overlay, `main`, tag, or release
  claim changes.

A0B passes only when the owner approves the exact A0A commit SHA. If any selected decision
above is rejected, A0B remains blocked and the candidate is amended rather than partially
treated as frozen.

## 11. Explicit non-goals

- reconstructing or claiming recovery of Task 3--10 source;
- executing the solver, xAct, CAMB, CLASS, HyRec, or the Rust fragment;
- installing dependencies or toolchains;
- selecting production high-ell cutoffs/tolerances before characterization;
- implementing spatial perturbations, stochastic spectra, likelihoods, or data fitting;
- optimizing before a transparent same-equation reference path exists;
- merging to `main` or making a release.

## 12. Owner review checklist

Approval of the exact candidate commit affirms all of the following together:

1. canonical `src/bass` namespace and adapter-only future `bianchi` compatibility;
2. homogeneous-only v1.0 and the low-ell/high-ell single-core boundary;
3. all-family registry with per-layer, per-family claim promotion;
4. metric/Riemann/frame/structure/photon/unit conventions above;
5. binary64 Python reference, immutable canonical bytes, typed errors, and no silent
   fallback;
6. first FLRW residual slice followed by Bianchi I;
7. Rust fragment as read-only reference and external codes as pinned oracle lanes only;
8. public GitHub visibility without release-status promotion;
9. the v1 scope matrix makes global tilt, photon `I/E/B`, exactly massless neutrinos,
   exact electron-frame Thomson, recombination, reionization, and the local-output adapter
   required; photon `V` and spatial/statistical sectors are out of scope;
10. deferred transport conventions and production high-ell tolerances remain hard gates;
11. A0B authorizes planning only; implementation still requires an approved plan and
    explicit A1 authorization.
