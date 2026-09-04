# SciSpace Literature Lock — R8 Dual Adapter

Search question:

> What formal conditions ensure that applying a linear, frequency-local radiative source in discrete-angle space and in spherical-harmonic or PSTF coefficient space yields equivalent projected source terms, and how should basis normalization, quadrature exactness, and truncation be validated?

## Methodological anchors

1. Barichello & Siewert, *On the Equivalence Between the Discrete Ordinates and the Spherical Harmonics Methods in Radiative Transfer*, Nuclear Science and Engineering (1998), DOI `10.13182/NSE98-A1991`.
   - Equivalence is conditional on matched angular quadrature and boundary conventions; representation labels alone are insufficient.

2. Clarke et al., *Space-angle discontinuous Galerkin method for plane-parallel radiative transfer equation*, JQSRT (2019), DOI `10.1016/J.JQSRT.2019.02.027`.
   - Angular-order convergence and exact-solution benchmarks are separate validation obligations.

3. Štěpán, Bestard & Trujillo Bueno, *Near optimal angular quadratures for polarised radiative transfer*, Astronomy & Astrophysics (2020), DOI `10.1051/0004-6361/202037566`.
   - Radiation-tensor accuracy depends on a declared quadrature; fewer directions are admissible only after like-accuracy validation.

4. *Stable Boundary Conditions and Discretization for P_N Equations* (2022), DOI `10.4208/jcm.2104-m2019-0231`.
   - Semi-discrete stability requires preserving the structures of the projected system, not merely matching a few coefficients.

## Effect on the R8 contract

The literature supports the following design constraints:

- bind a numerical projection contract explicitly;
- pass the coefficient representation of the unit field instead of assuming a universal monopole normalization;
- use an exact low-degree quadrature fixture only as a bounded regression;
- distinguish source-level commutation from full transport or boundary-value equivalence;
- reserve general nonaxisymmetric and polarized quadratures for later convergence/parity gates.

The literature does not provide BASS/REC sign, unit, frame, SHA-256, source-data or admission authority.

```text
authority_effect = NONE
```
