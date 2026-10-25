# Repository operating policy

## Project classification and supported user

`rei_bianchi` is a personal scientific-research codebase. It has one
developer/owner, and that owner is the only supported operator. The default
environment is a trusted local account on a trusted local machine; this is not
a multi-user product, hosted service, or adversarial execution platform.

## Default trust model

Unless the owner explicitly requests a named security task, do not design,
implement, require, or report blockers for:

- authentication, authorization, roles, account separation, or multi-tenant
  isolation;
- hostile same-UID users, malicious local repository configuration, adversarial
  symlink/path replacement, or deliberate local artifact tampering;
- anti-tamper ownership seals, signatures, attestations, custody state machines,
  or redundant hash/manifest layers whose only purpose is adversarial defense;
- product security reviews, automated security gates, dependency/supply-chain
  hardening, secret-scanning infrastructure, or security compliance;
- production-service availability, abuse resistance, or untrusted-input
  hardening that has no concrete role in the owner's research workflow.

The absence of those mechanisms is not an issue, blocker, promotion gate, or
acceptance failure for this repository. Do not introduce them speculatively.

## Research-integrity boundary

Retain only controls that directly support scientific correctness,
reproducibility, recovery, or diagnosis, such as exact model/input/configuration
identity, deterministic seeds, raw-result preservation, numerical invariants,
and minimal hashes or manifests needed to detect accidental corruption. Treat
these as research-integrity tools, not as adversarial security or anti-tamper
requirements, and keep them proportional to the scientific claim.

Historical receipts, manifests, and audit records remain valid evidence of the
work that produced them; this policy does not require deleting or rewriting
them. It does prevent their security-oriented machinery from becoming a
default requirement for new work.

## Baseline operational safety

Platform/system instructions, explicit user scope, credential privacy,
non-destructive filesystem practice, and external-service authorization still
apply. These are execution boundaries for the assistant, not project-level
product security features. Do not add repository security settings or gates
unless the owner explicitly asks for them.

Prioritize physics validity, numerical correctness, algorithmic quality,
reproducibility, performance, and clear scientific claim boundaries.

<!-- BEGIN UNIVERSAL_EXECUTION_TRANSITION_POLICY -->
## Execution-transition and anti-bureaucracy policy

This policy limits optional process expansion. It does not weaken explicit
user requirements, destructive-action safeguards, frozen scientific inputs,
or claim-admission ceilings.

> **Execution-transition rule:** Prevent the permanent-blocker attractor in which repair generates new review surfaces and fresh review continuously discovers adjacent defects without reaching execution. Nonexecution is itself a failure mode: two substantial process-only cycles trigger `PROCESS_STARVATION`. Separate execution permission from claim admission—fail closed on authoritative claims, not on exploratory progress. A blocked state must not leave documentation as the only unlimited action; perform the smallest repair, use a safe exploratory path, defer, or stop. Define a finite trust boundary so verification does not recursively verify its own machinery on every run. Do not mistake contracts, manifests, hashes, reviews, or audit documents for user utility. Every mandatory gate must have a positive `PASS → next executable action` transition and every review loop must have a stopping rule. Distinguish severity from current-task blocking relevance. Real defects receive one targeted repair and regression test; they do not automatically justify new governance layers. If assurance continues increasing while actual implementation, experiment, inference, or scientific progress remains stationary, classify `TRANSITION_POLICY_PATHOLOGY`, freeze optional process work, and resume the shortest safe path to execution.
<!-- END UNIVERSAL_EXECUTION_TRANSITION_POLICY -->

<!-- BEGIN UNIVERSAL_TYPED_IDENTITY_POLICY -->
## Byte identity versus semantic identity policy

> **Typed-identity rule:** A SHA or byte mismatch establishes only `BYTE_IDENTITY_MISMATCH`; never promote it automatically to `SCIENTIFIC_INTEGRITY_FAILURE`. First classify the object as immutable source/input, deterministic generated evidence, numerical/scientific output, or packaging/metadata, then apply the identity relation actually required by the claim. Immutable inputs and contractually deterministic evidence are byte-blocking by default. Numerical outputs must normally be judged by justified residuals, invariants, state/observable agreement, convergence, conditioning, and uncertainty—not hashes or equality of secondary error estimates. Packaging metadata mismatches are non-scientific unless byte-identical packaging is explicitly required. Distinguish result validity, provenance validity, and packaging validity. A stricter-than-necessary test that rejects mathematically equivalent outputs is a false-FAIL defect, not extra safety. Repair the smallest defective binding/test and continue; do not create a new audit or provenance layer solely because bytes differ.
<!-- END UNIVERSAL_TYPED_IDENTITY_POLICY -->

<!-- BEGIN TIERED_SCIENTIFIC_DELEGATION_POLICY -->
## Tiered scientific delegation and cost policy

For multi-agent scientific work, separate authority from mechanical execution.
This is a routing rule for cost-effective scientific work; it does not change
the scope of an approved scientific claim.

- An Astra-tier agent owns problem framing, frozen contracts, source/theory
  intake, numerical/physical acceptance criteria, independent review, failure
  classification, repair authorization, and PASS/HOLD/NO-GO decisions.
- A lower-tier coding agent owns only implementation, targeted tests, bounded
  builds/runs, raw-result preservation, mechanical evidence assembly, and
  implementation documentation that merely reports observed facts.
- Do not assign routine code writing, refactoring, test plumbing, formatting,
  evidence serialization, or a prescribed bounded execution to Astra when a
  complete Astra-authored contract is available. Delegate that work to a
  lower-tier coding agent.
- A lower-tier agent must stop and return to Astra, rather than inventing an
  answer, when an immutable input/source identity is missing, an acceptance
  tolerance or physical convention is ambiguous, a result changes the claim
  boundary, a substantive failure needs interpretation, or a repair would
  change model/solver/closure policy.
- The controller must give the coding agent the frozen base identity, allowed
  paths, limits, commands, controls, and stopping rule. It must then send the
  observed diff and raw outcomes to a fresh Astra-tier reviewer before any
  scoped scientific admission or publication decision.
- Astra review is read-only unless it explicitly authorizes one bounded
  targeted repair. The authorized repair returns to the lower-tier coding
  agent; it is not silently implemented by the reviewer.
- Do not route a task by package name alone or claim a runtime model identity
  that was not observed. Record requested and observed execution identities
  separately when they matter to the evidence.

This rule is satisfied by `Astra contract -> lower-tier execution -> Astra
independent decision -> lower-tier authorized repair, if any`. It prevents
both costly Astra implementation and recursive review without execution.
<!-- END TIERED_SCIENTIFIC_DELEGATION_POLICY -->

<!-- BEGIN AGENT_CAPACITY_RECOVERY_POLICY -->
## Agent-capacity recovery

After `agent thread limit reached`, do not repeat equivalent spawn attempts.
Inventory and reuse a completed compatible agent with `followup_task`, retaining
role separation and independent review of changes it did not implement.
`interrupt_agent` is not deletion and does not prove capacity was reclaimed.
Do not assert an internal scheduler cause without evidence or kill unrelated
processes. Check actual worker progress after request acceptance.

Controller-direct implementation is permitted only with explicit owner approval,
using the frozen contract, existing task identity and cumulative limits. Record
the actual executor; a historical requested model is not runtime evidence.
Missing independent review keeps scientific admission pending, but must not
prevent authorized safe preparation or the next dependency-safe action.
<!-- END AGENT_CAPACITY_RECOVERY_POLICY -->

## Repository checkout for new work

Use this repository's existing checkout as the default location for new work.
Do not create a separate clone or Git worktree unless the owner explicitly
requests one for that task or an already frozen task identity requires its
existing worktree. Preserve dirty and untracked files; inspect branch, HEAD,
remote, and status before changing the checkout. Stage only the paths owned by
the task. This changes the default for new work and does not rewrite historical
worktree-bound evidence or remove an existing active worktree.

