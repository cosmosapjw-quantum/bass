# G-POL-LIOUVILLE-II-B1 design

## Goal

Seal the finite tensor-to-Stokes convention used by the Type-II polarized runtime before any angular remap or harmonic projection is allowed.

## Authority

The existing nine-real carrier embeds a Hermitian three-dimensional coherency tensor.  On a validated local screen dyad `(s1,s2,e)`, B1 defines

`H = 1/2 [[I+Q,U-iV],[U+iV,I-Q]]`.

The implementation exposes tensor/Stokes roundtrip, finite passive basis rotation, finite active tensor rotation, handedness metadata, and fail-closed validation.

## Non-goals

No sky atlas, `n=-e` output bridge, IAU/COSMO conversion, E/B transform, Wigner kernel, angular interpolation, collision composition, or statistics output is included.
