# G-POL-LIOUVILLE-II-B2A literature boundary

## Primary external checks

1. Lavaux & Wandelt, *Fast CMB lensing using statistical interpolation on the sphere* (2010), arXiv:1003.4984.
   This establishes that arbitrary-spin interpolation on the sphere is a distinct numerical problem and that polarization cannot be treated as an ordinary scalar field.

2. Fabbian & Stompor, *High precision simulations of weak lensing effect on Cosmic Microwave Background polarization* (2013), arXiv:1303.6550.
   This motivates explicit accuracy, refinement and interpolation-error control for pixel-domain polarized remapping.

3. HEALPix `rotate_coord` documentation, version 3.83 (2024-11-13).
   The official API rotates both direction vectors and local Q/U components and returns the local basis-angle change. This is used only as an architectural sanity check that direction transport and spin-frame transport must be coupled.

4. HEALPix `ud_grade` documentation.
   Its warning that Q/U parallel transport is not implemented is retained as a negative design lesson: scalar component averaging is not a polarization remapper.

## BASS-owned authority

The B2A equations and signs are not imported from a map convention. The authority is the BASS packed-nine coherency tensor and PR #13 local Stokes seal. B2A transports the tensor itself by the minimal proper rotation

`J_t = R(e_s -> e_t) J_s R^T`

along the unique shortest great-circle segment, then forms a convex common-screen combination and projects once onto the target screen.

## Explicit non-claims

This checkpoint is not FLINTS, lenS2HAT, a HEALPix interpolation implementation, or a general spin-s interpolation library. It does not construct stencils, choose a sphere grid, define an observed-sky convention, perform E/B transforms, or bound map-level power-spectrum error.
