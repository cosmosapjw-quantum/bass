# BASS REC Source R8B — Trusted-Native Parent/Candidate Differential

## Purpose

The exact R8 local GREEN replay has passed. This node asks the next, narrower question:

> Does adding the dependency-light constant-pair receiving adapter change any existing backend behavior when the R7 parent and R8 candidate are executed under the same already-admitted RF-00 native payload?

It is a repository-level provenance and nonregression gate. It is not a new source-physics derivation and it does not wire the adapter into a solver.

## Exact comparison

```text
R7 parent
4431edef61351bfba49a5781db3005d4a0308d05

R8 production candidate
ed630f3b8b02531af0f392b722e6636c14a41864

source diff
A  bianchi/source_adapters.py
```

The candidate leaves `source_authority.py`, `_rustcore`, `requirements.lock`, `pyproject.toml`, backend dispatch and solver loops unchanged.

## Trusted native payload

```text
artifact commit
50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda

wheel SHA-256
99bd0596642dd31ca82080fb24306cd9bf3f6dd1ad3f68a1380f77378e266302

installed shared-object SHA-256
5d5b8197518d8637b14e0c78b871802ed64f6506c7a95128f31bd52044a98633
```

`BASS_ALLOW_UNVERIFIED_NATIVE_DEV` must be absent. Parent and candidate use separate Python 3.12 virtual environments, the same locked requirements, the same wheel bytes and root packages built from non-Git `git archive` staging directories.

## Gate

The runner requires:

```text
parent backend cone       54/54 PASS
candidate backend cone    54/54 PASS
candidate focused suite   33/33 PASS
failure sets              identical
trusted shared object     exact on both sides
unverified diagnostics    zero
source/output hashes      deterministic and frozen
source worktrees          clean
```

It also emits `r8b_plot_data.json` and `r8b_differential_audit.svg`. The plot is a compact execution diagnostic, not a physical observable.

## Local entry point

```bash
bash scripts/research/run_bass_rec_source_r8b_trusted_native_diff_local.sh
```

Expected classification:

```text
PASS_BASS_REC_SOURCE_R8B_TRUSTED_NATIVE_PARENT_CANDIDATE_NONREGRESSION
```

## Claim boundary

A PASS says only that the bounded R8 adapter coexists with the admitted native backend without changing the tested backend cone. It does not establish general grid/PSTF numerical parity, nonaxisymmetric arbitrary-rank source multiplication, physical REC microphysics, solver-loop wiring, integrated-state closure, a physical directional face, provider output, statistics readiness, `PASS_REC_PHYSICAL_SPLIT`, or `PASS_RF04`.
