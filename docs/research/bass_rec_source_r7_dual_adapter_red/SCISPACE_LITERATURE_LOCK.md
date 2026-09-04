# SciSpace literature lock — R7 dual adapter

## Role

This literature search tests whether it is methodologically legitimate to use a
harmonic representation for source evaluation and a direct angular
representation for transport, and what must be held fixed before calling the
representations equivalent. It supplies no BASS formula, normalization,
quadrature, source coefficient or admission decision.

## Anchors

### Barichello and Siewert (1998)

**On the Equivalence Between the Discrete Ordinates and the Spherical Harmonics
Methods in Radiative Transfer**  
*Nuclear Science and Engineering*  
DOI: `10.13182/NSE98-A1991`

The equivalence theorem is conditional: the discrete-ordinate quadrature uses
zeros of the associated Legendre functions and the harmonic solution uses
matched generalized Mark boundary conditions. It therefore supports explicit
projection/quadrature identity, not representation equivalence by name.

### Evans (1998)

**The Spherical Harmonics Discrete Ordinate Method for Three-Dimensional
Atmospheric Radiative Transfer**  
*Journal of the Atmospheric Sciences*  
DOI: `10.1175/1520-0469(1998)055<0429:TSHDOM>2.0.CO;2`

SHDOM evaluates the source in a spherical-harmonic representation and
integrates streaming along discrete ordinates. The method validates the hybrid
architecture, while also showing that adaptive resolution and explicit
transforms are load-bearing numerical components.

### Doicu, Efremenko and Trautmann (2013)

**A multi-dimensional vector spherical harmonics discrete ordinate method for
atmospheric radiative transfer**  
*Journal of Quantitative Spectroscopy and Radiative Transfer*  
DOI: `10.1016/J.JQSRT.2012.12.009`

The vector extension combines generalized spherical harmonics and discrete
ordinates for Stokes transport. It supports a future polarized architecture but
does not certify the BASS screen convention, electron-frame collision, or REC
source.

### Doicu et al. (2021)

**Spectral Spherical Harmonics Discrete Ordinate Method**  
*Journal of Quantitative Spectroscopy and Radiative Transfer*  
DOI: `10.1016/J.JQSRT.2020.107386`

The source function is represented spectrally/harmonically while the transfer
equation is integrated along discrete ordinates. This reinforces the need to
bind the source representation, streaming representation and conversion map
separately.

### Karp and Petrack (1983)

**On the spherical harmonics and discrete ordinates methods for
azimuth-dependent intensity calculations**  
*Journal of Quantitative Spectroscopy and Radiative Transfer*  
DOI: `10.1016/0022-4073(83)90033-X`

The exact correspondence occurs at quadrature points tied to associated
Legendre zeros. This is a useful regression for the R7 axisymmetric fixture,
but not an all-geometry numerical parity theorem.

## Consequences for R7

1. A common source equation is not enough; the quadrature/projector and boundary
   convention must be identified.
2. The direct and harmonic states must share a physical parent-state identity
   while retaining different representation identities.
3. Source evaluation can legitimately occur in coefficient space, but only
   with a named unit-field coefficient vector and work-rank policy.
4. A low-degree Gauss–Legendre fixture is an exact first contract test, not a
   production convergence study.
5. Polarized, highly anisotropic, discontinuous, or nonlinear-jump sources need
   separate tests and adaptive-tail evidence.
6. Numerical equivalence must later be checked at common outputs and tolerances;
   a source-level commutation identity alone is insufficient.

## Authority boundary

```text
LITERATURE_SUPPORTS_HYBRID_ARCHITECTURE_AND_VALIDATION_PATTERN
LITERATURE_DOES_NOT_SUPPLY_PROJECT_FORMULAS_OR_ADMISSION
AUTHORITY_EFFECT_NONE
```
