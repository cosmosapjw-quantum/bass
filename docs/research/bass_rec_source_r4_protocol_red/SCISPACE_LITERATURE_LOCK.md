# SciSpace literature lock

## Scope

The literature search was used only to test whether the revised BASS dual-representation plan is methodologically plausible and what evidence a parity claim must contain. It supplies no BASS coefficient, convention, source identity, or admission decision.

## Direct-angle versus harmonic representations

### Barichello and Siewert (1998)

**Title:** On the Equivalence Between the Discrete Ordinates and the Spherical Harmonics Methods in Radiative Transfer  
**Journal:** Nuclear Science and Engineering  
**DOI:** `10.13182/NSE98-A1991`

The paper proves equivalence only under matched quadrature and generalized Mark boundary conditions. It supports a conditional equivalence theorem, not a generic statement that any finite ordinate grid equals any finite harmonic truncation.

### Evans (1998)

**Title:** The Spherical Harmonics Discrete Ordinate Method for Three-Dimensional Atmospheric Radiative Transfer  
**Journal:** Journal of the Atmospheric Sciences  
**DOI:** `10.1175/1520-0469(1998)055<0429:TSHDOM>2.0.CO;2`

SHDOM uses a harmonic source representation together with discrete-ordinate streaming and adaptive refinement. It supports the architecture in which the source and streaming representations differ, provided their transforms and errors are independently controlled.

### Doicu, Efremenko and Trautmann (2013)

**Title:** A multi-dimensional vector spherical harmonics discrete ordinate method for atmospheric radiative transfer  
**Journal:** Journal of Quantitative Spectroscopy and Radiative Transfer  
**DOI:** `10.1016/J.JQSRT.2012.12.009`

This vector extension supports a combined Stokes/harmonic/discrete-ordinate architecture. It does not certify the BASS screen convention, electron-frame kernel, or cosmological source map.

### Abdelmalik, Cai and Pichard (2023)

**Title:** Moment methods for the radiative transfer equation based on phi-divergences  
**Journal:** Computer Methods in Applied Mechanics and Engineering  
**DOI:** `10.1016/j.cma.2023.116454`

The work demonstrates high-order realizability/entropy-aware moment methods with exact quadrature symmetry properties. In BASS it is relevant as an alternative closure and positivity comparison, not as authority to replace the full distribution or the REC source.

## Hierarchy-free and approximation-light cosmological methods

### Kamionkowski (2021)

**Title:** Cosmological perturbations without the Boltzmann hierarchy  
**Journal:** Physical Review D 104, 063512  
**DOI:** `10.1103/PHYSREVD.104.063512`

The photon quadrupoles are recovered from integral equations and compared to the conventional hierarchy. The relevance is methodological: an alternative representation requires a reference comparison at the observable-coupling level, not merely an internal residual.

### Nascimento (2021)

**Title:** Generalized Boltzmann hierarchy for massive neutrinos in cosmology  
**Identifier:** arXiv:2104.00703

The generalized hierarchy integrates momentum dependence into velocity-weighted moments and validates against standard transfer functions. This is closely adjacent to the BASS `J^(i)_{A_l}` lane and reinforces the need to distinguish that finite hierarchy from a spectral `F_{A_l}(nu)` hierarchy.

### Refregier et al. (2017)

**Title:** PyCosmo: An Integrated Cosmological Boltzmann Solver  
**Identifier:** arXiv:1708.05177

PyCosmo uses symbolic generation and sparsity optimization while requiring comparable-accuracy checks against existing codes. This supports the rule that compiler/backend speedups are admitted only under same-equation, same-tolerance and same-observable comparisons.

### CLASSIER line of work

The 2022–2025 integral-equation formulations for non-cold relics replace a truncated hierarchy and validate against fully converged hierarchy solutions. Their relevance is the validation pattern: truncation avoidance is demonstrated through convergence and observable parity, not inferred from the representation name.

## Consequences for BASS

1. A direct-grid/PSTF parity claim must name the exact quadrature, projection, boundary/work-rank policy and source identity.
2. A hybrid source/streaming representation is legitimate, but the interface itself is a load-bearing numerical theorem.
3. Positivity or realizability of a moment representation does not make it source-identical to the full distribution.
4. Avoiding moment closure does not remove finite angular, spectral, interpolation or timestep errors.
5. Alternative hierarchies and integral methods become trustworthy only after converged-reference and observable-level comparison.
6. The BASS Mode-A radial integral requires its own source-integrated theorem; the literature does not license reconstructing a generic spectral source from one stored energy moment.

## Authority boundary

```text
LITERATURE_SUPPORTS_ARCHITECTURE_AND_VALIDATION_PATTERN
LITERATURE_DOES_NOT_SUPPLY_PROJECT_FORMULAS_OR_ADMISSION
```
