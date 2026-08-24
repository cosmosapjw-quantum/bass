# G-POL-LIOUVILLE-II-A literature and authority boundary

## Primary external references

1. A. Challinor, *Microwave background polarization in cosmological models*,
   arXiv:astro-ph/9911481.
   The paper supplies the exact 1+3 covariant polarization-tensor viewpoint and
   the PSTF route.  This checkpoint uses only the tensor-valued, ray-level
   collisionless transport principle; it does not claim the projected hierarchy.

2. J. Portsmouth and E. Bertschinger, *A tensor formalism for transfer and
   Compton scattering of polarized light*, arXiv:astro-ph/0412094.
   The covariant coherency/polarization tensor motivates retaining a basis-free
   screen tensor rather than declaring a Q/U component convention prematurely.

3. C. Pitrou, *The radiative transfer at second order: a full treatment of the
   Boltzmann equation with polarization*, arXiv:0809.3036.
   This supplies an independent tensor-valued Liouville/collision architecture
   and the distinction between the exact distribution-level equation and later
   PSTF/normal-mode projection.

4. E. Mitsou and J. Yoo, *Tetrad formalism for exact cosmological observables*,
   arXiv:1908.10757.
   This supports the tetrad/matrix-kinetic formulation and reinforces that an
   observer-angle/output map is a separate layer.  No observer-space observable
   is claimed here.

5. A. Iserles, H. Z. Munthe-Kaas, S. P. Nørsett and A. Zanna,
   *Lie-group methods*, Acta Numerica 9 (2000) 215–365.
   This supports advancing an SO(3)-acted state by a Lie-group method so that
   orthogonality and geometric constraints are retained under discretization.

## Project formula authority

The implementation is lowered from the existing BASS homogeneous null-ray and
screen-tensor authority:

- `d ln epsilon/dlambda = -H - sigma_ab e^a e^b`;
- `e_dot = -sigma.e + sigma_ee e - a + (a.e)e - e x(n.e) + Omega x e`;
- `W = Omega + a x e + n.e - tr(n)e/2`;
- `omega_scr = e.W`;
- basis-free screen transport by the same spatial rotation that carries the ray
  and its screen.

The Type-II adapter uses the declared co-rotating diagonal-`n` chart.  In the
exact Type-I boundary, that chart loses its eigenframe authority; an off-diagonal
shear therefore fails closed rather than selecting a hidden frame.

## Deliberate non-claims

This checkpoint is not:

- a fixed-grid angular advection/remap scheme;
- a sign-locked Stokes Q/U or E/B component implementation;
- a collision + Kato + Liouville composition;
- a PSTF or harmonic hierarchy;
- an observer/local-boost output map;
- cross-family or production solver support.
