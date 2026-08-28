# RF-03 Matter / Thermodynamics / Tilt Execution Package

Status: `READY_TO_EXECUTE_RF03 / DOCS-ONLY PLAN / DRAFT UNMERGED`

Package ID: `BASS-RF03-MATTER-THERMO-TILT-CLOSURE-20260828-R1`  
Revision: `R1_RF02C_TERMINAL_BASE`

This package opens the next mandatory core-runtime node from the latest closed
RF-02C development head:

```text
branch: agent/architecture/rust-first-rf02c-20260826-r1
head:   dfa17457d402bd441d3fdf786c2d79c529512ee5
tree:   9fc67fb0ba10e091e25a14d7e1fac88b77a0241e
PR:     #36 OPEN / DRAFT
```

It is completely independent of the legacy/backup optimization lane
(BASS-12–15). That lane is neither a dependency nor an input to RF-03 and may
not be cherry-picked into this work.

The exact objective is to implement native collisionless perfect-fluid matter,
thermodynamic force/history support and tilt-domain closure, preserve the
approved equations and state order, remove silent constant-w/Python shortcut
selection from active production routes, and produce a scoped `PASS_RF03`
draft PR.

The package follows the established development guides in a bounded form:

```text
DAG reconstruction
→ source/code-path reality map
→ genuine TDD RED
→ Rust-owned implementation
→ targeted numerical proof
→ PHYS-MATH audit
→ PHYS-MATH-CODE audit
→ four small plots read as evidence + hostile mutations
→ one bounded repair
→ native delta/evidence
→ stacked draft PR
```

It does not create another contract-review loop. After the bounded schema/source
freeze, the same Codex run must proceed to RED and executable implementation.

## Validate

```bash
cd docs/rust_first_runtime/rf03_matter_thermo_tilt_closure_20260828
sha256sum -c MANIFEST.sha256
python validate_package.py
python validate_package.py --live
```

## Exactly one next action

Execute `CODEX_HANDOFF.md`. Create the RF-03 implementation branch from the
exact RF-02C terminal head, complete RF-03 only, open one stacked draft PR, and
stop.
