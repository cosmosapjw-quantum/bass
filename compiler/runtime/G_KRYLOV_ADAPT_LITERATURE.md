# G-KRYLOV-ADAPT literature and algorithm boundary

The implementation is informed by, but is not a port or parity claim for:

- J. Niesen and W. M. Wright, *A Krylov subspace algorithm for evaluating the
  phi-functions appearing in exponential integrators*, ACM TOMS 38 (2012),
  Algorithm 919 / `phipm`;
- S. Gaudreault, G. Rainwater, and M. Tokman, *KIOPS: A fast adaptive Krylov
  subspace solver for exponential integrators*, JCP 372 (2018).

Ideas used by the BASS reference backend are matrix-free Krylov projection,
augmented projected exponentials, IOP(2), residual-estimate-driven basis/time
adaptation, rejected-state reuse/extension, and fail-closed work budgets.

BASS-specific safety policy:

- `m_max < n`: genuinely truncated IOP(2) lane;
- full-capacity small systems: two-pass full MGS reference fallback;
- projected/Ritz nonfinite candidate: reject, extend, then reduce tau;
- nonfinite physical callback: distinct fatal error;
- acceptance telemetry separates attempted from accepted residual ratios;
- basis shrink and tau recovery use hysteresis to avoid reject saw-tooth;
- tolerance requests below the binary64 arithmetic floor fail closed;
- target semantics are explicitly residual-estimate-only, including the
  caller-divided residual-budget heuristic.

Not implemented or claimed:

- exact KIOPS algorithm or parameter parity;
- arbitrary simultaneous phi-function combinations;
- rigorous global relative forward error for arbitrary nonnormal semigroups;
- wall-clock production speedup or production tuning;
- any change to the Type-II physics, collision law, or frame conventions;
- production migration readiness.
