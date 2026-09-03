# Repository-wide code audit

## 1. Method and evidence boundary

This audit pins the code-bearing RF-04 branch at commit `380ce6fe6aebe0c76c59c0d2a0f8707aac0ce14c`, tree `0062a719173dc0c40dcc1202ab0d305f8fe2e2bb`.

Evidence levels are kept separate:

1. **tree census** — a path/blob/size inventory of the Python, Rust, runtime, compiler, test, audit and workflow trees;
2. **source read** — direct inspection of load-bearing implementation files;
3. **static inference** — conclusions forced by code signatures and call paths;
4. **dynamic evidence** — only pre-existing, pinned repository receipts; no new local execution is claimed here.

README prose and comments are treated as claims unless the executable path agrees.

## 2. Lineage reconstruction

The repository is not a single linear “latest code” object.

- `main` is a recovery/minimal tree and is not the scientific implementation parent.
- PR #70 contains the active RF-04 code-bearing runtime lineage and retains `NO_PASS_RF04`.
- later RF-04 mapping work is primarily documentation/authority material and does not silently replace the runtime parent used here.
- the formula-SSOT/compiler hardening lineage is distinct and must not be mistaken for an admitted public runtime.
- REC source physics remains a cross-repository authority and is not copied into BASS in this RED stage.

## 3. Python package census and classification

### 3.1 Geometry, routing and background

Load-bearing modules:

- `bianchi/algebra.py`
- `bianchi/routing.py`
- `bianchi/scalar_charts.py`
- `bianchi/charts/class_a.py`
- `bianchi/charts/class_b.py`
- `bianchi/charts/exceptional.py`
- `bianchi/charts/type_ix_d.py`
- `bianchi/charts/general.py`
- `bianchi/charts/class_a_tilted.py`
- `bianchi/charts/class_b_tilted.py`
- `bianchi/charts/class_a_tilted_multi.py`
- `bianchi/constraints.py`
- `bianchi/constraint_rates.py`

Findings:

- Eleven public Bianchi labels and the exceptional VI_-1/9 sector are routable.
- Non-tilted class-A, class-B, exceptional and Type-IX-D charts are real executable paths.
- `general.py` supplies an arbitrary symmetric-N/A orthonormal-frame carrier and monitors Gauss, trace, Codazzi and Jacobi constraints, but type-sign preservation is not automatically exact in that generic chart.
- Global tilt is implemented in separate class-A and class-B charts. It is not uniformly identical across families: exceptional tilted routing is absent; class-A multi-fluid tilt is Python-only and not default-routed; class-B tilted signature reconstruction contains an explicit unsupported path.
- The family registry is broader than family-by-family validated output coverage.

Verdict: **broad but uneven background support**, not “all eleven families equally production-ready.”

### 3.2 Backend and public-route control

Load-bearing modules:

- `bianchi/backend.py`
- `bianchi/backend_policy.py`
- `bianchi/runtime.py`
- `_rustcore/src/python/*`
- `runtime/rust/typeii/*`

Findings:

- backend selection is typed and mostly fail-closed; explicit Python-oracle and Rust-required routes are distinguished.
- the route inventory includes background, hierarchy, tilted and Q paths.
- the inspected public Type-II route remains v1-oriented; the RF-04 polarized-v2 implementation is still a RED/not-implemented scaffold and the authorized public-v2 mapping is the active blocker recorded by PR #70.
- `bianchi/runtime.py` is a workspace/substrate module, not a numerical solver implementation.

Verdict: **good route-governance substrate, incomplete RF-04 public composition**.

### 3.3 Distribution and moment representations

#### Legacy direct distribution grid

`bianchi/matter/grid_boltzmann.py` stores `F[r,a]=f(q_r,n_a)` on a finite radial/angular grid. It avoids moment closure, but the inspected slice is massless Bianchi I with a bounded Thomson test configuration.

#### Radial-integrated angular grid

`bianchi/matter/grid_coupled.py` and Q Mode A transport an energy-weighted angular density, not the full spectrum. This lane avoids hierarchy closure but cannot reconstruct arbitrary frequency-dependent source action.

#### Full spectral Q grid

`bianchi/q/modeb.py`, `q/fast.py`, `q/transport.py`, and Rust `qevolve.rs` transport the full discretized distribution `f(q_hat,q)`. The grid is finite, but there is no moment closure. The comoving representation makes the collisionless characteristic particularly simple; residual angular/radial remap, quadrature and timestep errors remain.

#### PSTF/moment lanes

- `bianchi/matter/hierarchy.py` and Rust `kinetic/hierarchy.rs` evolve the Lewis–Challinor `J^(i)_{A_l}` hierarchy in a finite `l_max,i_max` workspace.
- the upper-`i` edge uses a geometric extrapolation closure;
- unavailable `l+2` sectors at the rank boundary are treated as zero;
- dense PSTF projection is generated through `l=5` in Rust;
- coefficient-space kernels avoid `3^l` storage but the committed table wall is `L_KERNEL_MAX=10`.
- `bianchi/matter/pstf_coeff.py` and the formula SSOT supply generic-rank algebra and all-rank equations; this is not equivalent to an unbounded numerical state.

Verdict:

```text
full distribution grid, no moment closure       implemented
finite PSTF numerical hierarchy                 implemented
all-rank PSTF formula authority                  implemented
numerical PSTF hierarchy without truncation      not implemented
all-family dual-representation parity            not established
```

### 3.4 Einstein–matter coupling and species

Load-bearing modules:

- `bianchi/matter/kinetic_einstein.py`
- `bianchi/matter/coupled_class_a.py`
- `bianchi/matter/coupled_tilted.py`
- `bianchi/q/coupled.py`
- `bianchi/q/species.py`
- Rust `kinetic/coupled.rs`, `kinetic/qevolve.rs`

Findings:

- Q couples angular-grid moments to the homogeneous Einstein source and monitors Gauss/Codazzi/Jacobi residuals.
- a species abstraction exists and distinguishes grid species from exact-fluid species.
- the inspected general multi-species Python abstraction is not by itself proof of a fully coupled, full-spectrum, all-species production evolution path; some fluid source state is carried through narrow/private fields.
- neutrino support exists in legacy hierarchy/grid abstractions, but no CMB-like perturbation/output pipeline is inferred from that fact.

Verdict: **serious homogeneous Einstein–kinetic machinery, uneven multi-species closure and validation**.

### 3.5 Collision, polarization and electron motion

Load-bearing modules:

- `bianchi/q/collide.py`
- `bianchi/q/polarization.py`
- `bianchi/q/polstate.py`
- `bianchi/q/boost.py`
- `bianchi/q/electron.py`
- `bianchi/q/electron_rate.py`
- `bianchi/q/electron_validity.py`
- `bianchi/q/electron_trajectory.py`
- Rust `kinetic/collide_exact.rs`, `grid_collide.rs`, `pol_collide.rs`

Findings:

- exact finite-step cold Thomson exponentials exist for scalar and polarized grid carriers.
- the polarized state transports a screen tensor and has explicit Stokes diagnostics.
- constant finite electron bulk velocity is handled by boost to the electron rest frame, collision, and inverse boost in the Q path.
- the trajectory/validity modules are substantially more careful than a constant-velocity shortcut, but explicitly stop short of production solver/Rust ABI wiring and do not certify a trajectory-wide polarized differential kernel.
- the formula SSOT remains cold, non-tilted electron-rest Thomson authority. Therefore constant-velocity Q implementation and all-rank formula authority have different admitted scopes.

Verdict: **strong instantaneous/constant-bulk collision implementation; dynamic electron-trajectory production authority remains open**.

### 3.6 Recombination-history coupling

Load-bearing modules:

- `bianchi/thermo/history_api.py`
- `bianchi/thermo/recombination.py`
- `bianchi/q/rate.py`
- `bianchi/q/model.py`
- `bianchi/q/fast.py`

Findings:

- an ionization history can now drive the collision opacity at each integration step.
- the internal/phenomenology H-anchor lanes are explicitly separated.
- this closes a time-dependent Thomson-rate path, not the general REC source problem.
- no representation-neutral emission/absorption/jump bundle is consumed by both the full spectral grid and spectral PSTF paths.

Verdict: **opacity-history wiring exists; generic recombination source wiring does not**.

### 3.7 Numerics

Load-bearing modules:

- `bianchi/integrate.py`
- `bianchi/q/integrate.py`
- `bianchi/q/fast.py`
- `bianchi/q/runtime.py`
- Rust ODE/Krylov/transport modules

Findings:

- Python background integration offers adaptive Diffrax methods and events.
- Q uses Strang composition with RK/residual transport and exact collision substeps; the Rust whole-loop path avoids Python step overhead.
- Q event localization uses a bounded reference strategy rather than a globally certified dense interpolant.
- one Q Jacobian path is finite-difference instrumentation, not an analytic source Jacobian.
- deterministic reduction/checkpoint machinery exists.
- repository receipts show serious local regression work, but no new end-to-end convergence matrix is executed in this stage.

Verdict: **strong research numerics with path-specific maturity; not one uniformly certified solver**.

### 3.8 Observables and statistics

Load-bearing modules:

- `bianchi/observables/cmb_pattern.py`
- `bianchi/observables/distances.py`
- `bianchi/observables/sn.py`
- `bianchi/q/stats.py`

Findings:

- `cmb_pattern.py` computes a background anisotropic-redshift temperature pattern and a `C_l` summary.
- it explicitly is not a perturbation solver;
- it does not retain a full `a_lm` output object;
- no unified `T,Q,U`, `a_lm^(T,E,B)`, deterministic/stochastic/local-boost split, covariance likelihood, or enforced fitting gate was found on the inspected code-bearing parent.

Verdict: **selected background observables only; not statistics-ready**.

### 3.9 Compiler, formula and generated-runtime layers

The repository contains SymIR, lowering, DAE, derivative, structural, oracle, runtime, test and validation packages. The committed verification record reports WSC-0/WSC-1 and leaves later graph/compiler stages separate. Standalone Type-II runtime code has substantial primitive tests and receipts, but the full public polarized trajectory composition remains blocked.

Verdict: **advanced derivation/compiler substrate, not interchangeable with admitted production runtime**.

## 4. New source-adapter theorem forced by the code

Let Mode A store

```text
G = w1 f1 + w2 f2
```

for two spectral cells. Choose a second spectrum

```text
f1' = f1 + d
f2' = f2 - d w1/w2.
```

Then `G'=G`, but a frequency-dependent absorption coefficient gives

```text
A' - A = d w1 (chi1 - chi2).
```

This is generically nonzero. It vanishes exactly in the grey control `chi1=chi2`.

Therefore a generic spectral REC source is:

- directly admissible on the full spectral grid;
- exactly projectable onto spectral PSTF multipoles with sufficient work rank;
- **not identifiable from Mode A state alone**.

This is the main plan correction produced by the repository-wide audit.

## 5. Revised risk ranking

### P0

None introduced by this documentation-only stage.

### P1

1. treating Mode A as source-equivalent to full spectral Mode B;
2. calling finite numerical PSTF evolution “untruncated”;
3. implementing a cross-repository source adapter on the wrong lineage or through the blocked RF-04 v2 route;
4. discarding the positive `(eta,kappa)` pair in favor of a sign-restricted net opacity;
5. conflating constant electron bulk velocity with trajectory-wide finite-electron-tilt authority;
6. promoting selected background `C_l` output to harmonic/statistical readiness.

### P2

1. source-product aliasing when `L_work < L_out + L_source`;
2. anisotropic exponential jumps truncated without a tail receipt;
3. SI physical-time rates injected into Q `tau` evolution without division by `H_s_inv`;
4. comparing the full spectral grid with a radially integrated angular state as though they were the same representation;
5. mixing formula/compiler completion with public runtime completion.

### P3

Documentation naming, duplicated historical plans and broad package metadata can mislead unless the exact branch and lane are printed.

## 6. Correct next step

The DAG-correct next step is not source implementation. It is the committed test-only RED contract in this branch. Only after the absence and required semantics are visible as a reproducible failing test may the minimal BASS-owned protocol be implemented.
