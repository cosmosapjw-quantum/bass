# G-POL-LIOUVILLE-II-B2A Design

## Scope

This checkpoint implements a **screen-aware convex-stencil remap core** for the
Type-II polarized Liouville DAG. Interpolation weights and stencil discovery are
inputs; the module owns only the geometry needed to compare polarization tensors
living in different tangent screens.

## Governing geometry

For unit propagation directions `e_s` and `e_d`, the source coherency tensor is
parallel transported along the unique shortest great-circle arc by the minimal
proper rotation `R(e_s -> e_d)`. The real nine-component BASS representative is
transported by `J_d = R J_s R^T`. Exact antipodes are ambiguous and fail closed.

Every source must satisfy `J_s = P(e_s) J_s P(e_s)` within a scale-aware tolerance.
After transport, non-negative weights whose sum is one form a convex combination
on the common departure screen. The result is finally projected once onto
`P(e_d)`. No component-wise node-local Q/U interpolation is allowed in the
production path.

## Interfaces

- `parallel_transport_matrix(from, to, options)`
- `transport_packed_to_direction(packed, from, to, options)`
- `remap_convex_packed(source_directions, source_states, weights, target, options)`

The output includes weight, screen-leakage and path-separation diagnostics.

## Claim boundary

Allowed: shortest-geodesic, common-screen, convex-stencil tensor remapping.

Not allowed: stencil construction for a particular sphere grid, observer-sky
`n=-e` conversion, global dyad atlas, E/B or Wigner transforms, temporal
characteristic integration, collision/Kato composition, or production migration.
