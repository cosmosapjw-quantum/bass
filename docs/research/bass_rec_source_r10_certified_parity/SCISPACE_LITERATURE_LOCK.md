# SciSpace Literature Lock — R10

Search question:

> Which rigorous numerical conditions ensure stable, alias-free finite-rank transformations between a Gauss–Legendre times uniform-azimuth angular grid and real spherical-harmonic coefficients, including normalization, mode ordering, Gram-matrix conditioning, and underresolved-quadrature failure detection?

Methodological anchors:

1. Slevinsky, *Fast and backward stable transforms between spherical harmonic expansions and bivariate Fourier series* (2017, arXiv:1705.05448). The transform is a structured change of basis whose numerical stability depends on well-conditioned connection matrices and stable orthogonal-polynomial transforms.
2. Blais & Soofi, *Spherical harmonic transforms using quadratures and least squares*, DOI `10.1007/11758532_8`. Quadrature and least-squares routes must be assessed for information conservation and numerical stability rather than identified by name alone.
3. Blais, *Discrete Spherical Harmonic Transforms: Numerical Preconditioning and Optimization*, DOI `10.1007/978-3-540-69387-1_74`. High-degree reliability requires explicit numerical conditioning and preconditioning analysis.
4. Jekeli, *Spherical harmonic analysis, aliasing, and filtering*, DOI `10.1007/BF00873702`. Regular-grid harmonic analysis can remain biased for band-limited fields when analysis weights and aliases are not treated explicitly.
5. Wieczorek & Meschede, *SHTools: Tools for Working with Spherical Harmonics*, DOI `10.1029/2018GC007529`. Normalization and Condon–Shortley phase are explicit API choices, and Gauss–Legendre grids are distinct certified sampling surfaces.
6. Schaeffer, *Efficient spherical harmonic transforms aimed at pseudospectral numerical simulations*, DOI `10.1002/GGGE.20071`. Accuracy and performance of Gauss–Legendre SHTs must be measured together; implementation speed does not replace transform validation.

Consequences for R10:

- basis normalization, phase, mode order, nodes, and weights must be data, not prose;
- `B^T W B≈I`, residual-versus-rank, and conditioning should be recorded;
- one-node underresolution must fail visibly rather than be hidden by tolerance adjustment;
- a future optimized library may replace the reference implementation only under same-contract differential tests.

These papers provide methodology only. They do not determine BASS source signs, hashes, state identities, tolerance, REC microphysics, or release admission.

```text
authority_effect = NONE_LITERATURE_METHOD_ONLY
```
