# RF-02C Codex Continuation — V2 Event/Restart Semantics Closed

Start only from:

```text
repository: cosmosapjw-quantum/bass
branch: agent/architecture/rust-first-rf02c-20260826-r1
required parent head: <read live branch after the V2 semantics commit>
pre-V2 parent: 11c6c7ad58257575cf3ccca482ec6f52c37a0d85
```

Read in this order:

1. `docs/rust_first_runtime/RF02C_EXECUTION_CONTRACT_V2.json`
2. `docs/rust_first_runtime/RF02C_EXECUTION_SEMANTICS_V2.md`
3. `tools/audit/rf02c_semantics_v2.py`
4. `tools/audit/rf02c_event_root_oracle_v2.py`
5. the audit-compiled RF-02C work unit

The V2 machine contract SHA-256 is `804826b9d5ce2f3333de0558447e351a8050dc8147d268e8a6055b6c5669e51c`. V2 is complete and supersedes V1; do not merge V1 event/restart/history prose back into V2.

## Mandatory implementation boundary

Implement exactly the closed built-in event AST registry. Do not accept Python callbacks, caller Rust closures/function pointers, arbitrary user events, transcendental root expressions, or min/max/abs branching expressions.

The authoritative event representation is the V2 certified dyadic piecewise cubic-Hermite carrier. Compile every built-in event AST to degree-<=6 polynomials, convert f64 coefficients to exact dyadic rationals, perform square-free decomposition plus exact Sturm isolation, enumerate tangential/multiple roots, apply direction filtering, and fail closed on carrier/root representation failures.

Domain events use raw margins. Projection and accepted-sample validation use certificate margins. Store both.

The restart latch uses the stored `epsilon_g`; it is not recomputed. The Type-IX recollapse event is segment-terminal, transition-bearing, trajectory-nonterminal, and one-shot. Follow the atomic history order and store one root sample only.

## TDD order

1. Add failing tests for the callback-free registry, multiple/tangential/endpoint/continuum roots, raw-vs-certificate separation, latch rearm sides, and recollapse history order.
2. Implement the polynomial/event substrate without wiring it into integration.
3. Wire carrier certification and event selection into the Rust-owned trajectory loop.
4. Wire transition/restart/history.
5. Run only RF-02C targeted tests and changed-path closure. Do not run full suite for reassurance.
6. If native bytes change, produce the required content-addressed delta and exact remote restore evidence.
7. Freeze, perform one fresh review, repair only verified P0/P1 findings, and open one stacked draft PR only after all required evidence is GREEN.

## Stop conditions

Stop rather than guess on any expression outside V2, carrier depth exhaustion, unrepresentable root, transition outside the single Type-IX identity/phase transition, formula/tolerance/reference/state-order change, or mismatch between stored root bytes and restart input.

Claim ceiling remains `PASS_SCOPED_BACKGROUND_EXECUTION`; it is not earned by the V2 contract commit alone.
