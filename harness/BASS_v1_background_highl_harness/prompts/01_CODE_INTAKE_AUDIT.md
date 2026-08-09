# BASS v1.0 code-intake audit

## Outcome

Create a durable, read-only reconstruction of the uploaded canonical BASS source before
any implementation, dependency installation, build, test, import, or solver execution.

## Preconditions

- `OD001`--`OD004` are resolved with a durable `G-OD0` owner receipt.
- The user has explicitly authorized code intake.
- `contracts/scope_lock.json` is in `CODE_INTAKE_READ_ONLY` with only `code_read=true`;
  all write/build/execute/install/external-write flags remain false.

## Required work

1. Audit archive/repository safety, identity, nested instructions, clean/dirty state,
   submodules/LFS, hashes, and provenance. Do not overlay historical bundles.
2. Reconstruct actual code paths for geometry/background, matter, radiation transport,
   collisions/history, high-ell representation/closure, integration, outputs, and
   backends. Names/docs are claims only.
3. Locate every spatial-perturbation, transfer, stochastic, likelihood, and data path;
   classify it as absent, isolated/non-production, or scope violation.
4. Build equation-to-code and requirement-to-evidence maps for all obligation IDs.
5. Classify tests as smoke, software regression, invariant/limit, convergence,
   cross-backend, output, or release evidence. A pass count is not a physics verdict.
6. Identify placeholders, silent fallbacks, surrogate/toy paths, hard-coded coefficients,
   repair/projection, clipping, unasserted warnings, and missing failure propagation.
7. Produce the minimum dependency/toolchain execution proposal, but do not install or run.

## Outputs

- code snapshot receipt and hash manifest
- actual pipeline map
- equation-to-code map
- obligation coverage matrix
- scope-firewall report
- P0--P3 risk ledger
- proposed first authorized DAG node and required owner approvals

Stop after the read-only audit. Do not implement fixes.
