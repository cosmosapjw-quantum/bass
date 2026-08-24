# G-KRYLOV-ADAPT hostile-repair audit

## Verdict and claim boundary

The repaired checkpoint is an **adaptive truncated Krylov exp / phi1 numerical
reference backend with residual-controlled requested targets and fail-closed
budgets**.

That sentence is deliberately narrower than a forward-error theorem.  The
controller accepts against a projected residual estimate.  Neither the default
action nor the caller-divided residual-budget action certifies global relative
forward error for an arbitrary nonnormal semigroup.  The test suite retains an
exact-similarity counterexample that returns `Ok` outside a forward target and
labels it `forward_certified=false` with machine-readable residual-only target
semantics.

This repair does not claim exact KIOPS parity, arbitrary phi combinations,
production speedup, production migration readiness, cross-family generality,
or a polarized Liouville solver.

## API contract

- `adaptive_expm_action`: matrix-free exponential action.
- `adaptive_phi1_action`: standalone `phi1(t A)b`; its requested scale is not
  obtained by controlling `t phi1(t A)b` and dividing by `t`.
- `adaptive_t_phi1_action`: direct `t phi1(t A)b` action.
- `kato_aem2_step_adaptive`: uses the direct scaled-phi action for both forcing
  terms.
- `adaptive_expm_action_with_residual_budget_divisor`: an explicit caller
  heuristic that divides the internal residual budget; it is not named or
  documented as an amplification bound or a forward certificate.

The returned telemetry distinguishes attempted and accepted residual ratios:
`max_attempt_error_ratio`, `max_accepted_error_ratio`, and
`last_accepted_error_ratio`.  It also carries `nonfinite_rejections` through
aggregate Kato statistics and all stats-bearing failure paths.

## Numerical and failure-semantics repairs

The hostile repair closes the following executable defects found after the
original PR receipt:

1. small-|t| standalone phi1 tolerance amplification;
2. overflow-prone vector norms and false happy breakdown;
3. zero-work success for small nonzero times;
4. time-significant residuals discarded by an absolute breakdown floor;
5. an ill-scaled augmented projected exponential whose off-diagonal `t` term
   dominated Pade scaling;
6. fail-open NaN time/input/options at early returns;
7. unbounded/nonfinite Pade scaling;
8. incomplete basis, nonfinite, budget, Kato, and dimension-mismatch ledgers;
9. reject/accept basis-shrink and tau-growth saw-tooth behavior;
10. ambiguous forward-target language for nonnormal operators.

The large-system lane uses IOP(2) when `m_max < n`.  The small full-capacity
lane uses two-pass full MGS.  Rejected states reuse and extend the existing
projection before reducing the substep.  Accepted steps recover tau under
hysteresis that prevents simultaneous tau growth and basis shrink.

Finite projected/Ritz arithmetic failures are rejected and retried under the
controller.  A nonfinite physical callback result is a distinct fatal error.
Exhausted accepted-step or rejection budgets return an error carrying the full
work ledger.

## Fresh hostile evidence

All values below are produced by executable Rust source in
`runtime/rust/typeii/tests/` under the locked offline RustCore crate.

- public regression: 5/5;
- hostile regression: 33/33;
- small-time standalone phi1 (`n=48`, `m_max=16`,
  `t={1e-6,1e-8,1e-10,1e-12,-1e-8}`): maximum observed L2 error
  `2.3190080331548624e-15` against requested target
  `4.70758498113147e-12`;
- inverse-time scalar scaling through `|t|=1e16`: error
  `1.1102230246251565e-16`;
- inverse-scaled symmetric Hadamard lane: error
  `1.654866465237975e-13` at `m_max=12`, and
  `1.1474169730238064e-15` at `m_max=24`, against target
  `4.908620047119475e-10`;
- controller lane: 104 accepted, 22 rejected, 832 matvecs, maximum basis 8,
  19 tau reductions, 67 recoveries, and zero joint tau-growth/basis-shrink
  events;
- 64-by-64 block-skew precursor, frequencies `0.1..300`, `m_max=12`:
  global L2 error `6.150718919799523e-12` against target
  `4.6121145083305985e-10`, 436 accepted, 88 rejected, 5232 matvecs,
  maximum basis 12, and no budget exhaustion;
- nonnormal Jordan negative control: forward error
  `1.8199636343638716e-9` against `1e-10`, explicitly reported as
  `ResidualEstimateOnly` rather than silently promoted to a forward guarantee;
- caller-divided Jordan lane: fail-closed at the 4096 accepted-step budget;
- exact-similarity divided-residual negative control: forward ratio
  `1.2766...`, explicitly `forward_certified=false`.

## Reproducibility boundary

The public five-test source, hostile source, deterministic fixture generator,
fixture reconstruction source, and negative-control sources are all retained.
The generator records SplitMix64 seed `0x424153535f484f53` and the exact
binary64 reconstruction convention.  Its opacity schedule is a declared
receipt-constrained surrogate, not recovered original SahaHistory authority.

Rust and Cargo are 1.94.1.  `Cargo.lock` SHA-256 is
`d500208e9353ade1cb74693918598846628219e6e7bd2e2bce9ec85e29eb6310`.
The existing archive warnings remain separate from new-code warnings; the
repair introduces no new warning.

## Open risks

- P0: none.
- P1: none.
- P2: projected-residual control remains heuristic for general nonnormal
  forward error; IOP(2) orthogonality telemetry is diagnostic, not a forward
  certificate; production performance has not been benchmarked.

## Next DAG node

The next stacked node is `G-PRE-LIOUVILLE-SAFETY-II`.  Production migration
and `G-POL-LIOUVILLE-II` remain blocked until that safety layer and the later
transport implementation are reviewed independently.
