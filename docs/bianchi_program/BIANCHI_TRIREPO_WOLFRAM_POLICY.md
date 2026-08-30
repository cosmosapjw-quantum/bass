# Bianchi tri-repository Wolfram/xAct policy

- Program ID: `BIANCHI-WOLFRAM-TRIREPO-20260830`
- Policy version: `1.0.0`
- Program state: `DECLARED`
- Scientific authority effect: `NONE`
- Jira Epic: [BASS-16](https://cosmosapjw.atlassian.net/browse/BASS-16)
- Confluence control plane: [Bianchi Unified Wolfram Program](https://cosmosapjw.atlassian.net/wiki/spaces/BA/pages/19464193)

This policy treats `bass`, `rec_bianchi`, and `rei_bianchi` as one governed
scientific-software program. It adopts Wolfram Language plus exact-pinned xAct
as the common symbolic authority. It does not rewrite or demote the existing
Rust, Python, or C numerical runtimes, and it does not promote any current
scientific result.

## Authority split

| Domain | Authority | Required evidence |
|---|---|---|
| Tensor and geometry derivation | Wolfram Language + xAct | Headless `.wl`, exact inputs, conventions, exact residuals, receipt |
| Exact algebra, signs, normalizations, known limits | Wolfram Language; xAct where tensorial | Headless `.wl`, assumptions, canonical receipt |
| Numerical integration and production execution | Existing Rust/Python/C runtime of the owning repository | Tests, numerical parity, runtime receipt |
| Cross-repository contract | This policy plus exact-pinned machine lock | Commit/tree/artifact digests and reviewed adapters |
| Scientific claim | Dual PHYS-MATH and PHYS-MATH-CODE audit after parity | Audit receipts, reference/limit checks, adversarial plots where applicable |

Notebook files may be used for exploration and visualization, but are never
the sole authority. A symbolic result is authoritative only when its headless
source and machine-readable receipt are committed.

## Repository ownership

### `bass`

`bass` owns geometry, background evolution, the Einstein–Boltzmann and
observable solve, the shared frame/gauge/units contract, and cross-repository
orchestration. It consumes exact-pinned REC and REI artifacts and must not
silently reimplement their microphysics.

Jira: [BASS-17](https://cosmosapjw.atlassian.net/browse/BASS-17).

### `rec_bianchi`

`rec_bianchi` owns primordial recombination and the high-redshift
`RecombinationHistory`. A publishable provider artifact must declare at least:

- independent coordinate and orientation (`z`, `a`, or conformal time);
- `x_e = n_e / n_H`, with definition and units;
- optional matter temperature and derivatives;
- validity range, interpolation rule, extrapolation policy, and error envelope;
- producer commit/tree and artifact/manifest digests;
- `contains_astrophysical_reionization = false`.

The current physical-split/source/owner/interface gates remain binding. This
policy does not authorize provider export.

Jira: [BASS-19](https://cosmosapjw.atlassian.net/browse/BASS-19).

### `rei_bianchi`

`rei_bianchi` owns astrophysical reionization, thermochemistry, opacity, and
any published `MatterSource {Omega, q_a, Pi_ab, Q_energy, Q_momentum}`. It
consumes an exact BASS background contract and an exact REC provider lock. It
must not provide a primordial surrogate or silently replace recombination.

The existing fail-closed REC monitoring policy remains binding. This policy
does not authorize the currently blocked REC splice or Bianchi feedback.

Jira: [BASS-18](https://cosmosapjw.atlassian.net/browse/BASS-18).

## Program data flow

1. BASS publishes a background snapshot and the common conventions.
2. REC publishes an immutable primordial recombination history.
3. REI exact-pins the BASS contract and REC artifact, then publishes
   reionization/opacity and any matter-source output.
4. BASS exact-pins both providers, composes the histories, validates the
   overlap/splice, and performs the coupled transport/observable solve.
5. Any fixed-point iteration is owned by BASS and recorded as an exact-pinned
   iteration ledger.

No repository copies another repository's source as an integration mechanism.
Only immutable artifacts and explicit reviewed adapters cross a repository
boundary.

## Common artifact envelope

Every promoted cross-repository artifact must record:

- schema, program, change, contract, and claim-level identifiers;
- producer repository, commit, tree, branch/ref, and role;
- consumer repositories and exact upstream dependency locks;
- artifact path, media type, SHA-256, and manifest SHA-256;
- metric signature, tetrad orientation, gauge, time coordinate, units, and
  frequency convention;
- variables with meaning, frame, units, shape, domain, and ordering;
- validity domain, approximations, assumptions, and known exclusions;
- symbolic script/input/environment/package hashes and exact residuals;
- numerical fixture hash, metrics, tolerances, and parity status;
- authorized and withheld claims;
- Jira key, peer PRs, and Confluence decision locator.

Missing required fields are a contract failure, not an invitation to infer a
default.

## Overlap and splice gate

The REC/REI overlap is not selected implicitly. The adapter must declare an
overlap interval and a deterministic arbitration/blending rule. Before BASS
may consume the result it must verify:

1. identical variable definitions, frame, coordinate orientation, and units;
2. declared interpolation and a fail-closed no-silent-extrapolation rule;
3. positivity/domain constraints and finite values;
4. continuity requirements and explicit tolerances for values and required
   derivatives;
5. conservation/ledger invariants required by the owning stages;
6. exact producer and adapter identities;
7. known-limit and adversarial overlap fixtures.

Failure with an exact-pinned provider is `FAIL_COMPATIBILITY`. A moved remote
head, missing object, or digest mismatch is `BLOCKED_INPUT_IDENTITY`. Neither
may be relabelled as a scientific failure.

## Wolfram/xAct deterministic gate

### W0 — environment and package

- Pin full Wolfram version and `$SystemID`.
- Download xAct from the declared URL and require the exact archive SHA-256.
- Extract into a fresh per-run directory.
- Prepend the directory containing `xAct/` to `$Path`.
- Load the explicit `xAct/xTensor/Kernel/init.m` path.
- Record xTensor version and package-load state.

### W1 — headless capability

Define a manifold and covariant derivative and require xAct to register the
generated Riemann tensor. The thread execution gate is
`XACT-XTENSOR-HEADLESS-CAPABILITY-001`.

### W2 — repository symbolic verification

Run repository-owned headless `.wl` tests over exact-pinned inputs. Require
explicit assumptions and conventions, exact zero residuals for algebraic
identities, and declared known limits. Undefined symbols, unapproved messages,
package mismatch, or missing input hashes fail closed.

### W3 — receipt

Commit the `.wl` source, its SHA-256, all input hashes, Wolfram/xAct identity,
assumptions, residuals, warnings, and status in canonical JSON. Expression
pretty-printing is not a stable equality oracle; gate exact identities by
their residual.

### W4 — implementation and science

A symbolic PASS is not a runtime or science PASS. The owning repository must
then pass numerical parity, reference/known-limit checks, and the required
PHYS-MATH then PHYS-MATH-CODE audits. Plot-driven/adversarial gates remain
mandatory where the stage contract requires them.

## Claim ladder

Claims advance one level at a time:

1. `DECLARED`
2. `SYMBOLIC_VERIFIED`
3. `IMPLEMENTATION_PARITY`
4. `CROSS_REPO_COMPATIBLE`
5. `SCIENCE_VALIDATED`

Passing one level never implies a later level. `BLOCKED`, `NOT_RUN`, and
`FAIL` are distinct terminal states and must be retained verbatim.

## GitHub policy

- Use a new child branch from an exact verified base commit.
- Open a stacked draft PR back to that exact base branch.
- Include the Jira key, Confluence page, exact base/head/tree identities,
  upstream locks, receipt digests, tests, peer PRs, and claim level.
- Do not force-push policy or scientific evidence branches.
- Do not edit or reseal historical immutable packets for an additive policy
  change.
- An interface-changing PR remains draft until all affected peer PRs are
  linked and the program DAG gates pass.
- Merge authorization is separate from policy publication and is not granted
  by this document.

## Atlassian policy

The Jira BASS project is the single execution project. BASS-16 is the program
Epic; BASS-17, BASS-19, and BASS-18 own the three repositories. Jira `Blocks`
links encode REC -> REI, REC -> BASS, and REI -> BASS. The linked Confluence
page is the cross-repository policy and release-ledger system of record.

GitHub remains the code/evidence system of record. The available Atlassian
scope does not expose GitHub-for-Jira/DVCS administration, so URL backlinks are
required and native repository indexing must not be claimed unless an
administrator separately configures and verifies it.

## Current claim boundary

The thread verified Wolfram 15.0.1 and xAct/xTensor 1.3.0 headless capability
using the exact archive recorded in `PROGRAM_LOCK.json`. It also verified a
reduced-equation consistency identity with exact residual zero. These are
capability and reduced-algebra smoke results only.

The following remain withheld: repository-specific tensor audits, generated
formula promotion, numerical parity, REC provider export, REI splice/feedback,
BASS RF04 promotion, cross-repository compatibility, and scientific validity.
