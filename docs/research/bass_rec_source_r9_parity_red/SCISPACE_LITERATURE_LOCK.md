# SciSpace literature lock — R9

Search question:

> What rigorous sampling, quadrature, truncation, normalization, and alias-control conditions are required for a finite-rank nonaxisymmetric spherical-harmonic representation of a radiative-transfer source to agree with a discrete angular-grid evaluation under the same physical source law?

Retrieved methodological anchors:

1. Barichello & Siewert, *On the Equivalence Between the Discrete Ordinates and the Spherical Harmonics Methods in Radiative Transfer*, Nuclear Science and Engineering (1998), DOI `10.13182/NSE98-A1991`.
   The nonaxisymmetric equivalence result requires a matched associated-Legendre quadrature and compatible generalized Mark boundary conditions; method names alone do not imply equality.

2. Evans, *The Spherical Harmonics Discrete Ordinate Method for Three-Dimensional Atmospheric Radiative Transfer*, J. Atmos. Sci. 55 (1998), DOI `10.1175/1520-0469(1998)055<0429:TSHDOM>2.0.CO;2`.
   Source representation, discrete-ordinate streaming, transforms, adaptive resolution, and validation are separate load-bearing components.

3. Jekeli, *Spherical harmonic analysis, aliasing, and filtering*, Journal of Geodesy 70 (1996), DOI `10.1007/BF00873702`.
   Regular-grid harmonic analysis can remain biased even for band-limited data unless aliasing and analysis weights are treated explicitly.

4. Favennec et al., *Ad hoc angular discretization of the radiative transfer equation*, JQSRT 225 (2019), DOI `10.1016/J.JQSRT.2018.12.032`.
   Angular discretization must be validated against solution accuracy; a nominally denser or more convenient angular mesh is not automatically better.

Relevance:

- explicit basis, quadrature, resolution, and boundary/projection identities are necessary;
- underresolution must be exposed rather than hidden by a tolerance;
- grid/harmonic source parity is a separate layer from streaming/evolution parity.

These papers do not determine BASS signs, hashes, RF-00 payload identity, normalization, tolerances, or REC microphysics.

```text
authority_effect = NONE_LITERATURE_METHOD_ONLY
```
