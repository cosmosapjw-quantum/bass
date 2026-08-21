# G-POL-LIOUVILLE-II-B2B Design

## Goal

Add a concrete, deterministic, fail-closed icosphere grid/departure adapter on top of the B2A common-screen convex tensor-remap core.

## Scope

B2B provides four reference-layer services:

1. deterministic recursively refined icosphere vertices and oriented triangular faces;
2. deterministic radial-ray face location with convex barycentric weights and edge/vertex tie-breaking;
3. backward characteristic tracing to a departure direction using the already sealed PR #11 Liouville characteristic;
4. a one-step semi-Lagrangian adapter that locates the departure stencil, calls B2A, and transports the remapped tensor forward to the target direction.

The runtime remains a reference implementation. It is intentionally O(number of faces) per locator query and does not claim production lookup performance.

## Geometry

For a spherical triangle with unit vertices `v0,v1,v2` and a unit query direction `e`, solve

`[v0 v1 v2] y = e`.

If `s=sum(y)>0`, the ray intersects the planar hull face at

`lambda e = sum_i w_i v_i`,

where

`w_i=y_i/s`, `lambda=1/s`.

The direction lies in the closed spherical triangle when all `w_i` are non-negative within tolerance. Tiny negative weights are clamped to zero and renormalized. If several faces accept an edge/vertex query, choose the lexicographically smallest sorted vertex triple. No nearest-neighbour fallback is allowed.

## Mesh

The concrete grid begins from an outward-oriented regular icosahedron. Each refinement splits every face into four using normalized edge midpoints. Midpoints are deduplicated with an ordered edge map. For level `L`:

- vertices: `10*4^L + 2`;
- faces: `20*4^L`;
- every undirected edge has incidence two.

Input mesh validation checks finite/unit vertices, valid distinct indices, outward nondegenerate orientation, and closed two-manifold edge incidence.

## Semi-Lagrangian order

For target direction `e_{n+1}`:

1. integrate the characteristic backward from `(state_{n+1}, e_{n+1})` to obtain departure direction `e_d`;
2. locate `e_d` in the icosphere and obtain a convex three-node stencil;
3. call B2A to parallel-transport the three source tensors to `e_d`, convexly interpolate them, and project once;
4. integrate the remapped tensor forward from `e_d` to the target time;
5. fail closed if the forward endpoint direction does not recover `e_{n+1}` within tolerance.

## Error separation

Tests report separately:

- characteristic departure error against an analytic solid-body rotation;
- interpolation/remap error at the exact departure direction;
- combined semi-Lagrangian error;
- forward/backward repeated-remap diffusion.

## Claim boundary

Allowed: deterministic icosphere grid, face locator, convex stencil, Type-II/generic departure wrapper, and reference semi-Lagrangian one-step adapter.

Not allowed: arbitrary input-node triangulation in Rust, HEALPix/IAU/COSMO output, antipodal routing, high-order/non-convex interpolation, conservative flux form, E/B or harmonic validation, production performance, or full collision/Kato/Liouville composition.
