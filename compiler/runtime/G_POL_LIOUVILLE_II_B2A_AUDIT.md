# G-POL-LIOUVILLE-II-B2A hostile audit

## Verdict

**PASS as a shortest-geodesic, common-screen, convex-stencil tensor-remap core.**

The checkpoint is deliberately narrower than a full angular remapper. It consumes already-selected source directions and non-negative interpolation weights; grid-specific stencil discovery and departure-point integration remain for B2B.

## Physics and geometric contract

Conventions:

- spacetime signature remains `(-,+,+,+)`;
- propagation directions and interpolation weights are dimensionless;
- packed coherency entries retain the bolometric intensity dimension;
- PR #13 remains the Stokes-sign authority, including canonical `packed[8]=-V/2`.

For unit directions `e_s` and `e_t`, B2A computes the minimal proper rotation about `e_s x e_t`. Acting on tangent vectors, this is Levi-Civita parallel transport along the unique shortest great-circle segment. For a packed coherency tensor,

`J_t = R J_s R^T`.

Every source is required to satisfy `J_s=P(e_s)J_sP(e_s)` within a scale-aware tolerance. Transported tensors are combined only after they share the target screen. Weights are finite, non-negative, and sum to one within an explicit tolerance. The accumulated tensor is projected exactly once onto `P(e_t)`.

Exact or near antipodes fail closed because the shortest path and its spin-frame phase are not unique.

## TDD and hostile evidence

The first RED failed on the unresolved `typeii_polarized_remap` module. Production code was added only after the geometry/failure tests existed.

Three implementation mutations were tested:

1. skip common-screen transport: rejected by the gauge-invariance/fixture suite;
2. remove the negative-weight guard: rejected by the convexity suite;
3. remove final target projection: the first mutation survived because the initial implementation projected every source separately. The architecture was then repaired to transport raw physical tensors, interpolate, and project once at the target. The same mutation was rerun and rejected.

The third result is retained because it exposed a tautological test path and led to a stronger single-projection implementation.

## Fresh numerical evidence

Pinned Rust/Cargo 1.94.1, exact crate root and offline lock:

- B2A Rust: 12/12 (11 unit + 1 independent fixture);
- independent Python/SciPy: 8/8;
- remote-PR13-compatible full RustCore: 239/239;
- changed-file `rustfmt --check`: PASS;
- failures: 0.

Independent fixture:

- Rust/SciPy packed-output max error: `1.1102230246251565e-16`;
- minimum source/target dot: `0.9363406575547659`;
- tensor roundtrip max error in Rust: `6.661338147750939e-16`;
- independent Python roundtrip max error: `1.6653345369377348e-16`.

Gauge negative control:

- common-screen tensor result is invariant under unrelated source-dyad gauges;
- naïve node-local component Q/U averaging has error `1.0817171333574376` in the finite witness.

Spatial symmetric-stencil errors for angular offsets `(0.2,0.1,0.05,0.025)` are

`(4.036517987148547e-3, 1.0116565311996117e-3, 2.5307227001925003e-4, 6.3277954170049e-5)`

with ratios

`(3.990008330556702, 3.9975005207906014, 3.9993750325612663)`.

This supports second-order spatial consistency for the tested analytic l=1/spin-2-amplitude witness. It is not a grid-global convergence theorem.

## Independent-oracle separation

The Python fixture uses `scipy.spatial.transform.Rotation.from_rotvec`, not the Rust Rodrigues implementation. An additional `solve_ivp` test integrates the embedded-sphere Levi-Civita parallel-transport equation and agrees with the shortest-rotation route to the stated tolerance. A generator byte-identity regression also caught and repaired the raw-generator-versus-rustfmt fixture mismatch; the generator now requires and executes pinned `rustfmt` before declaring canonical output.

## Safety and invariants

The supplied regression covers:

- exact unpolarized monopole preservation;
- covariantly constant polarized tensor preservation;
- source-dyad gauge invariance;
- V=0 preservation;
- coherency-cone preservation under convex interpolation;
- target-screen projection and diagnostics;
- nonfinite directions/states/weights;
- non-unit directions;
- negative and non-normalized weights;
- exact and near-antipodal fail-closed paths;
- removal of tolerated source roundoff leakage at final projection.

## Risk ledger

### P0

None found in the tested B2A contract.

### P1

None found in the tested B2A contract.

### P2

- No sphere-grid/stencil generator is included. Accuracy therefore depends on the caller-supplied convex stencil.
- Shortest-geodesic transport is intentionally undefined near antipodes; a later atlas/path-routing layer must make that choice explicitly.
- Convexity protects the cone for physical source tensors, but B2A does not prove a global cone theorem for later non-convex high-order interpolation.
- No map-level E/B leakage or power-spectrum benchmark exists because observed-sky and harmonic conventions remain outside scope.

## Claim boundary

Allowed:

> BASS has a fail-closed common-screen convex remap core that parallel-transports packed physical coherency tensors along unique shortest sphere geodesics before interpolation.

Not allowed:

- complete fixed-grid or semi-Lagrangian angular solver;
- HEALPix/IAU/COSMO output compatibility;
- global nonsingular spin-frame atlas;
- E/B or Wigner transport;
- map-level accuracy or power-spectrum claims;
- temporal Liouville plus remap convergence;
- collision/Kato/Liouville composition;
- full G-POL-LIOUVILLE-II closure;
- production migration.

## Next DAG node

`G-POL-LIOUVILLE-II-B2B`: add a concrete sphere-grid departure/stencil adapter, atlas-transition metadata, forward/backward remap and diffusion-versus-time-error gates. Node C then composes Liouville, collision, Kato and raw/AP policies.
