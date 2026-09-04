# PHYS–MATH–CODE Audit — R8B Trusted-Native Differential

## Equation-to-code boundary

| Contract | Owner | R8B role |
|---|---|---|
| positive photon/boson source pair | `bianchi/source_authority.py` | exact same blob on both sides |
| full-grid and spectral-PSTF application | `bianchi/source_adapters.py` | absent in parent, exact blob in candidate |
| native route admission | `bianchi/backend_policy.py` | unchanged; tested under admitted payload |
| backend dispatch and numerical routes | `bianchi/backend.py`, native extension | unchanged; parent/candidate differential |
| solver-loop wiring | production solvers | absent and forbidden in this node |

## Isolation contract

The exact Git comparison must contain one row only:

```text
A  bianchi/source_adapters.py
```

The parent and candidate must have identical `_rustcore` trees, `requirements.lock` blobs and `pyproject.toml` blobs. Separate Python 3.12 virtual environments prevent package-install cross-contamination. Root packages are built from non-Git archive stages so source worktrees remain clean.

## Trusted-payload contract

Both environments must load the same wheel and the installed shared object must hash to:

```text
5d5b8197518d8637b14e0c78b871802ed64f6506c7a95128f31bd52044a98633
```

Any development override or unverified-native diagnostic is fatal. A locally rebuilt or merely importable wheel is not a substitute.

## Runtime obligations

1. parent backend policy/integration/packaging cone: 54/54;
2. candidate backend cone: 54/54;
3. identical empty failure sets;
4. candidate R5+R6+R7 focused suite: 33/33;
5. frozen source, binding, grid-output and PSTF-output identities in two processes;
6. projection-contract mutation changes the output identity;
7. both detached source worktrees remain clean.

## Failure precedence

- exact source, trusted artifact or environment-input mismatch: `STOP_*`;
- parent green / candidate red: candidate-induced regression;
- both red with identical failures: inherited baseline blocker;
- focused or hash failure: R8 protocol defect;
- unverified diagnostic: trusted-native admission failure;
- dirty source worktree: staging/cleanliness failure.

## Open risks after a possible PASS

### P1

- The adapter is still not wired to a real Q Mode B state or arbitrary coefficient hierarchy.
- General nonconstant source multiplication and all-rank nonaxisymmetric projection are untested.
- Projection identity remains caller supplied rather than resolved from a certified registry.

### P2

- Application receipt/result constructors are public frozen dataclasses.
- Vector layout and basis shape remain encoded indirectly by representation and projection hashes.
- No transport-level residual, cutoff-convergence or tolerance-sensitivity plot exists yet.

## Verdict before execution

```text
R8B_SOURCE_AND_RUNNER_CONTRACT_READY_FOR_LOCAL_REPLAY
NO_RUNTIME_PASS_CLAIM
NO_GENERAL_GRID_PSTF_PARITY
NO_SOLVER_OR_SCIENCE_PROMOTION
```
