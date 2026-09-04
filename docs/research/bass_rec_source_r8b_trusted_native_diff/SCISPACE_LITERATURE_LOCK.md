# SciSpace literature lock — R8B

Search question:

> What rigorous conditions are required for discrete-ordinate and spherical-harmonic representations of radiative-transfer source terms to be equivalent, and how should projection, quadrature, truncation, and source multiplication be validated in a same-physics numerical comparison?

## Retrieved methodological anchors

1. L. B. Barichello and C. E. Siewert, *On the Equivalence Between the Discrete Ordinates and the Spherical Harmonics Methods in Radiative Transfer*, Nuclear Science and Engineering (1998), DOI `10.13182/NSE98-A1991`.
   - The equivalence result requires a matched associated-Legendre quadrature and generalized Mark boundary conditions; representation names alone do not imply identical solutions.

2. K. F. Evans, *The Spherical Harmonics Discrete Ordinate Method for Three-Dimensional Atmospheric Radiative Transfer*, Journal of the Atmospheric Sciences 55 (1998), DOI `10.1175/1520-0469(1998)055<0429:TSHDOM>2.0.CO;2`.
   - The source function is represented in spherical harmonics while streaming is solved on discrete ordinates; explicit transforms, resolution control and validation are load-bearing.

3. N. Tominaga, S. Shibata and S. I. Blinnikov, *Time-dependent multi-group multi-dimensional relativistic radiative transfer code based on spherical harmonic discrete ordinate method*, ApJS 219 (2015), DOI `10.1088/0067-0049/219/2/38`.
   - Mixed-frame and multi-group transport requires explicit frame handling and independent validation against test problems and Monte Carlo results.

4. A. Doicu et al., *Spectral Spherical Harmonics Discrete Ordinate Method*, JQSRT 258 (2021), DOI `10.1016/J.JQSRT.2020.107386`.
   - Source representation and discrete-ordinate propagation may be split, but the transform and iterative numerical scheme remain explicit parts of the method.

## Relevance to R8B

These works support the architecture-level requirement that two angular representations be compared under one physical equation, one declared projection/quadrature contract, matched boundary conventions, and controlled numerical resolution. They also support keeping source evaluation, representation transforms and transport integration as separate auditable layers.

They do **not** establish the BASS signs, hashes, source payload, RF-00 artifact identity, test counts, code correctness, or any REC physical-source claim.

```text
authority_effect = NONE_LITERATURE_METHOD_ONLY
```
