# G-POL-LIOUVILLE-II-B1 literature and convention boundary

Primary references used as external sanity checks:

- M. Zaldarriaga and U. Seljak, *An All-Sky Analysis of Polarization in the Microwave Background*, arXiv:astro-ph/9609170.  Linear polarization is a spin-2 field on the sphere and is naturally represented by `Q +/- i U`.
- A. Challinor, *Microwave background polarization in cosmological models*, arXiv:astro-ph/9911481.  Covariant tensor polarization provides the basis-independent authority from which component conventions must be derived.
- HEALPix 3.83, *HEALPix conventions* and `rotate_coord`.  The documentation makes the local-basis dependence of Q/U explicit and records finite spin-s rotation formulas.
- HEALPix 3.83, `change_polcconv`.  The IAU/COSMO bridge changes the sign of U and therefore must remain an explicit output-layer conversion rather than an implicit runtime convention.

BASS does not import an external sign convention by name.  The B1 signs are derived from the existing nine-real Hermitian carrier:

`H = 1/2 [[I+Q, U-iV], [U+iV, I-Q]]`.

For a right-handed `(s1,s2,e)` screen and

`s1' = cos(psi)s1 + sin(psi)s2`,
`s2' = -sin(psi)s1 + cos(psi)s2`,

BASS obtains

`(Q+iU)' = exp(-2 i psi)(Q+iU)` for passive basis rotation and
`(Q+iU)' = exp(+2 i psi)(Q+iU)` for active tensor rotation.

No claim is made here about the observer direction `n=-e`, IAU/HEALPix map headers, E/B harmonics, a global dyad atlas, or Wigner-D transport.
