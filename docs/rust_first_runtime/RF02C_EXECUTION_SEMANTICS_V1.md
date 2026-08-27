# RF-02C Execution Semantics Addendum v1

**Contract ID:** `RF02C-EXECUTION-SEMANTICS-20260826-V1`  
**Base:** PR #33 package-overlay head `b759a42911a7433212c1828bd7625d66f3af2d20`  
**Machine contract:** `docs/rust_first_runtime/RF02C_EXECUTION_CONTRACT_V1.json`  
**Machine-contract SHA-256:** `ab1c8dcef60895af0b5a6214e8b72254a0264e1c0e4ec3b4e02056e1c2e78782`

## 1. Decision

The previous `BLOCKED_BY_UNRESOLVED_SPEC` stop was correct. RF-02C required projection, event, transition, restart, history, and trajectory outcomes that were not mechanically defined.

This addendum closes that ambiguity **only as an RF-02C code contract**. It does not promote formula authority or alter equations, coefficients, state ordering, supported chart labels, references, grids, seeds, scientific claims, or performance claims.

The numerical acceptance scales are not new scientific tolerances:

- projection residual and physical-domain slack are derived from the caller's already-selected background `rtol` and `atol`;
- event-root defaults remain the existing `rtol=1e-10`, `atol=1e-12`;
- the existing class-B exceptional routing tolerance remains `1e-9`;
- the Gauss-Newton update and damping remain unchanged.

## 2. Projection closure

`chart_project` remains the raw RF-02B pointwise candidate used for native/Python parity. A finite returned vector is **not** a solver-admissible success.

RF-02C adds a checked route, `chart_project_checked`, which repeatedly invokes one unchanged Gauss-Newton step, up to eight steps. It records a projection certificate and fails closed.

For ordered equality constraints \(c_i\), define from the initial candidate

\[
s_i = \mathrm{atol}+\mathrm{rtol}\max(1,|c_i(y_0)|),
\qquad
R_k=\max_i\frac{|c_i(y_k)|}{s_i}.
\]

For a chart without equality constraints, \(R_k=0\). A checked projection succeeds only when:

1. every state, residual, and iteration record is finite;
2. \(R_{\rm final}\le 1\);
3. the sequence is non-increasing up to
   \(64\,\epsilon_{\rm f64}\max(1,R_k)\);
4. all chart-specific physical-domain predicates pass with
   \(\delta_{\rm dom}=\mathrm{atol}+\mathrm{rtol}\max(1,\|y\|_\infty)\).

The inequalities are checked, never projected or clipped.

| Chart | Physical-domain predicates |
|---|---|
| `class_a` | \(\Omega\ge-\delta_{\rm dom}\) |
| `class_b` | existing \(|\kappa+9|\ge10^{-9}\) route guard; \(\widetilde\Sigma,\widetilde N,\widetilde A,\Omega\ge-\delta_{\rm dom}\) |
| `exceptional` | \(\Omega\ge-\delta_{\rm dom}\) |
| `type_ix_d`, `type_ix_d_future` | \(\Omega\ge-\delta_{\rm dom}\), \(|\bar H|\le1+\delta_{\rm dom}\), and pairwise \(N_iN_j\ge-\delta_{\rm dom}\) |

There is no automatic projection by default. Explicit `checked_initial` or `checked_chunk_boundary` modes may be added, but any enabled mode must stop on a typed projection failure.

## 3. Event semantics

Each event has a stable `id`, root function, direction in the actual integration direction, numeric priority, terminal flag, and optional transition ID.

For every accepted solver step:

1. locate all armed roots using dense interpolation;
2. choose the earliest root in the integration direction;
3. roots within
   \[
   \tau_{\rm tie}=10^{-12}+10^{-10}
   \max(1,|\tau_a|,|\tau_b|)
   \]
   are simultaneous;
4. break simultaneous ties by lower numeric priority, then declaration order.

Endpoint roots count. Non-finite event values are failures. A restarted event is latched only at the restart left endpoint, so no state or time epsilon nudge is permitted.

Physical-domain margins are terminal boundary events with priorities `0–19`. The Type-IX future recollapse event is

\[
g_{\rm recollapse}=\bar H,\qquad
{\rm direction}=-1,\qquad
{\rm priority}=20.
\]

The selected dense root state is returned and appended exactly once. It is accepted only after finite, equality-residual, and physical-domain checks.

`accepted` and `reached_requested_end` are separate fields. An event-terminated or domain-boundary result may be an accepted trajectory prefix without having reached the requested endpoint.

## 4. Transition and restart boundary

RF-02C freezes exactly one automatic transition:

```text
type_ix_expanding_to_contracting
type_ix_d_future -> type_ix_d_future
state map: identity, bit-preserving
metadata: phase expanding -> contracting
```

No equation or state component changes at maximum expansion. Continuing past the event is an explicit restart from the exact root state.

Automatic `class_a <-> type_ix_d`, `class_b <-> exceptional`, family relabeling, or any unfrozen state reconstruction is forbidden. Such a request returns `UNSUPPORTED_TRANSITION`.

A restart must reuse the exact root time and state, route identities, parameters, state schema, and tolerances. History concatenation removes one byte-identical duplicate root sample. Any mismatch is `RESTART_IDENTITY_MISMATCH`.

## 5. Geometry-history schema

The RF-02C history is normalized background geometry only. It contains:

- route and native identities;
- chart, phase, parameters, tolerances, and state names;
- samples with `tau`, packed state, \(\Omega\), signed equality constraints, normalized residual, and domain margins;
- ordered event and transition records;
- terminal status and typed failure.

For Type IX it additionally records \(\bar H,\Sigma^2\), the D-chart definition residual, and shear trace.

Physical \(H(\tau)\), cosmic time, mean scale factor, thermodynamics, rays, observables, and inference remain separate adapters.

## 6. Frozen trajectory oracles

### Class A flat dust

For \(\gamma=1\), \(N_i=0\), \(\Sigma_-=0\), and \(\Sigma_{+0}=0.3\),

\[
u(\tau)=
\frac{u_0 e^{-3\tau}}
     {1-u_0+u_0e^{-3\tau}},
\quad
u_0=\Sigma_{+0}^2,
\quad
\Sigma_+=\sqrt{u},
\quad
\Omega=1-u.
\]

### Class B equilibrium

At \(\gamma=1.3,\kappa=4\),

\[
(-0.4,\;0.24,\;0,\;0.36,\;\sqrt{2.16})
\]

has zero RHS and Codazzi residual, with \(\Omega=0\).

### Exceptional equilibrium

At \(\gamma=4/3\),

\[
\left(-\frac12,\frac{1}{2\sqrt3},0,0,0,\frac1{\sqrt{12}}\right)
\]

has zero RHS and \(g=0\), with
\(\Sigma^2=K=\Omega=1/3\) and \(q=1\).

A second on-\(g\) dynamic state is frozen in the machine contract for Rust/Python trajectory comparison.

### Type-IX static state

At \(\gamma=2/3\),

\[
(0,0,0,0,\sqrt2,\sqrt2,\sqrt2)
\]

has zero RHS, zero definition and trace residuals, \(\Omega=1/2\), and \(q=0\).

### Type-IX recollapse

For isotropic future evolution with dust, \(\bar H_0=0.8\), and
\(N_1=N_2=N_3=\sqrt{2(1-\bar H_0^2)}\),

\[
\frac{d\bar H}{d\tau}
=-\frac{1-\bar H^4}{4},
\]

so the exact root offset is

\[
\tau_*-\tau_0
=
\log\frac{1+\bar H_0}{1-\bar H_0}
+2\arctan\bar H_0
=
3.546706461783325.
\]

This fixes root direction, returned sample, transition, and restart tests without importing a new scientific model.

## 7. Batch and comparison rules

A trajectory is serial. Parallelism is only across independent members. Input order, member status, event records, and state bytes must be identical between one-thread and multi-thread runs of the same build. A failed member cannot erase or relabel another result, and NaN-only failure signaling is forbidden.

For Rust/Python and restart differentials at shared samples,

\[
E=\max_j
\frac{|y^{\rm Rust}_j-y^{\rm oracle}_j|}
{\mathrm{atol}+\mathrm{rtol}
 \max(1,|y^{\rm Rust}_j|,|y^{\rm oracle}_j|)}
\le 32.
\]

This is a scoped code-comparison budget, not a global forward-error theorem.

## 8. Execution order after this addendum

Resume the original RF-02C ordered steps from the same branch:

1. bind the RF-02B payload to verified default dispatch;
2. close public route/hash/domain bypasses;
3. freeze composite and randomized-JVP receipts;
4. implement the checked projection certificate above;
5. move PyO3 domain bodies out of `lib.rs`;
6. implement the Rust-owned trajectory/event/transition/restart/history/batch path;
7. run only `tests/rf02c/test_background_execution_contract.py` and changed-path closure;
8. build a content-addressed native delta because native bytes changed;
9. perform one bounded fresh-context review;
10. push one stacked draft RF-02C PR and read back exact evidence.

Do not run the full suite, Cargo/Wolfram/timing/GPU reassurance lanes, RF-03+, merge, ready transition, authority promotion, or performance claims.
