# BASS P0/P1 policy

## P0

A P0 is any defect that can silently change scientific meaning, promote unverifiable authority, corrupt canonical data/evidence, or claim same-physics equivalence when the equations/state/conventions/tolerances/outputs differ.

Examples: sign/unit/frame errors; global-tilt/local-boost substitution; same filename accepted as same artifact despite different bytes; expected-hash rewriting; unbound receipt used for row promotion; comparator marketed as authority; golden/tolerance/test edits made to fit implementation; non-equivalent Rust speedup marketed as same physics.

## P1

A P1 is a major incompleteness or fail-open condition that does not yet demonstrate wrong science but can permit it or misstate readiness.

Examples: missing boundary/limit test; optional dependency contaminating an authority slice; partial implementation marked complete; non-portable sidecar; generated cache contaminating manifest; missing fresh-context review; missing negative test for a declared P0; output support flag not enforced.

## Compile rule

Every anticipated P0/P1 must have at least one executable test, mechanically checkable invariant/assertion, or explicit STOP/BLOCKED gate. A prose warning alone fails plan verification.

## Agent behavior

`DO_NOT_ASK_USER_QUESTIONS` does not authorize guessing. Across any unresolved specification boundary, the agent must stop with `BLOCKED_BY_UNRESOLVED_SPEC` and preserve exact evidence.
