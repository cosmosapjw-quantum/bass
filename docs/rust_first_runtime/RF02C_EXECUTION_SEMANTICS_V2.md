# RF-02C Execution Semantics Addendum v2

**Contract ID:** `RF02C-EXECUTION-SEMANTICS-20260826-V2`  
**Required preimplementation parent:** `11c6c7ad58257575cf3ccca482ec6f52c37a0d85`  
**Machine contract:** `docs/rust_first_runtime/RF02C_EXECUTION_CONTRACT_V2.json`  
**Machine-contract SHA-256:** `804826b9d5ce2f3333de0558447e351a8050dc8147d268e8a6055b6c5669e51c`  
**Superseded v1 SHA-256:** `ab1c8dcef60895af0b5a6214e8b72254a0264e1c0e4ec3b4e02056e1c2e78782`

## Decision

The second `BLOCKED_P0_SEMANTICS` stop was correct. V1 named a `root_function`, dense interpolation, a zero neighborhood, and a terminal transition, but did not compile those words into a finite executable algebra.

V2 is a complete code-contract replacement for V1. It changes no Einstein/background equation, chart state order, family label, formula authority, scientific claim, reference, grid, seed, or existing solver tolerance. The formula SSOT remains outside solver construction and numerical evolution; this addendum governs only execution semantics.

## Callback-free event algebra

RF-02C accepts only a closed polynomial AST with `state`, frozen `parameter`, pinned `const_f64_bits`, `add`, `sub`, `mul`, and `neg`. Python callbacks, caller-provided Rust closures/function pointers, transcendental expressions, branching expressions, and arbitrary public user events are unsupported. The built-in domain margins and the Type-IX recollapse event are literal expression trees in the machine contract.

## Authoritative event carrier

One accepted BDF step is covered by certified dyadic piecewise cubic-Hermite state carriers. Endpoints come from the solver dense state; endpoint derivatives come from the frozen chart RHS. A subsegment is accepted only when both normalized midpoint state defect and every armed event-expression defect are at most `0.25`. Otherwise it is bisected, up to depth `24`; exhaustion is the typed failure `EVENT_CARRIER_CERTIFICATE_FAILURE`.

The event carrier, not an arbitrary callback and not undocumented diffsol interpolation internals, defines event roots.

## Exhaustive multiple and tangential roots

Substituting a cubic carrier into a built-in expression yields a polynomial of degree at most six. Every binary64 coefficient is converted to its exact dyadic rational. The implementation must perform exact square-free decomposition and exact Sturm isolation on each certified subsegment. Thus all distinct carrier roots are enumerated, including repeated and tangential roots. Strict sign-change sampling is forbidden as a completeness argument.

A tangential root is always present in detector evidence. It fires only for direction `0`; directed `-1/+1` events require the corresponding exact sign crossing. An identically zero polynomial is represented as `CONTINUUM_ZERO`, not an invented finite root list.

## Raw boundary versus numerical certificate

For every physical predicate,

\[
 g_{\rm raw}(y)\ge 0,
 \qquad
 \delta_{\rm dom}(y)=\mathrm{atol}+\mathrm{rtol}\max(1,\lVert y\rVert_\infty),
 \qquad
 g_{\rm cert}(y)=g_{\rm raw}(y)+\delta_{\rm dom}(y).
\]

Domain events locate `g_raw = 0`. Projection and accepted-sample validation use `g_cert >= 0`. Therefore solver tolerances may widen the numerical certificate but may not move the physical event surface. History stores both values.

## Event-value tolerance and restart latch

For the selected atomic event polynomial `p(theta)=sum p_k theta^k`,

\[
 \epsilon_g=\mathrm{event\_atol}+
 \mathrm{event\_rtol}\max\!\left(1,\sum_k|p_k|\right).
\]

This binary64 value and its bits are stored once in the event record and restart latch. Rearming is detected on the certified carrier itself by exact roots of `p-epsilon_g` or `p+epsilon_g`, so an event can leave the zero band and encounter another raw root inside the same accepted BDF step. Internal step endpoints are additional assertions, not the sole rearm detector. The recollapse event is one-shot and permanently consumed after its transition.

## Recollapse terminal/transition/history order

`type_ix_recollapse` is segment-terminal but not trajectory-terminal. The atomic order is:

1. truncate the accepted step at the root;
2. append one expanding-phase root sample;
3. append the event record referencing that sample;
4. append the identity-state phase transition at the same sample;
5. close the expanding segment as `TRANSITION_REQUIRED`;
6. if the requested endpoint is later, start the contracting segment at the identical stored tau/state bytes without a duplicate sample;
7. if the root is the requested endpoint, return `COMPLETED_AT_TRANSITION` without a continuation segment.

This resolves the previous contradiction between `terminal=true` and a transition-bearing event.

## Claim boundary

Passing the V2 contract validator and exact root-oracle self-test resolves only the specification blocker. It does not earn `PASS_SCOPED_BACKGROUND_EXECUTION`. That claim still requires the Rust implementation, native provenance closure, targeted trajectory/event/restart/history tests, content-addressed native delta, fresh review, and remote evidence.
