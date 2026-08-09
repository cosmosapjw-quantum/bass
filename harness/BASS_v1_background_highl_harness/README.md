# BASS v1.0 background/high-ell Work harness

This is a fail-closed, pre-code harness for BASS (Bianchi Anisotropy System Solver) v1.0.
It governs an exact/nonlinear spatially homogeneous Bianchi background and a finite,
configurable angular hierarchy. It does **not** authorize spatial perturbations,
primordial stochastic modes, transfer-function fitting, likelihoods, or data analysis.

Packaged state: the harness has been adapted and statically validated; solver code is not
included and was not ingested, built, executed, or modified. The authoritative live phase
is always the matching value in `contracts/scope_lock.json` and `state/run_state.json`;
the manifest retains only the immutable packaged initial phase.

## Layout

- `AGENTS.md`: durable operating rules.
- `contracts/`: phase-aware scope/state machine, evidence schema, conventions, family and
  high-ell registries, scientific obligations, owner decisions, and oracle lock.
- `state/`: machine-readable DAG, gates, claims, and run state.
- `policies/`: provenance, independence, retry, and toolchain rules.
- `prompts/`: bounded prompts for code intake, implementation-era work, and external
  symbolic/numerical jobs.
- `tools/`: standard-library-only static validators; no solver execution.
- `audit/`: input inventory and audit evidence.
- `evidence/`, `reviews/`, `receipts/`: producer evidence, independent attestations, and
  final gate outcomes.

## Static check

```bash
python3 tools/validate_harness.py
python3 -m unittest discover -s tests -v
```

These commands validate only the harness and the freshness of its H0/H1 evidence graph.
Each H0/H1 static log records the exact governing-file snapshot before and after its
commands, plus the immutable shell-free argv/cwd plan and its SHA-256, so an earlier PASS
log cannot be reissued against modified harness bytes and a no-op command cannot impersonate
the declared checks.
The evidence graph is intentionally bound to this Work harness path and resolved Python
runtime. A relocated copy must reissue H0/H1 evidence rather than treating old execution
logs as current.
They are not evidence that any BASS physics or runtime claim has passed. They may be run
from the harness root; the test suite also resolves from its parent directory.
