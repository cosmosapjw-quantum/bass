# BASS Master SSOT v2 — ALG-01 witness design

**Program ID:** `BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901`  
**Stage:** `ALG_01`  
**Exact predecessor:** `82776f50869d5c76e1cab4b28734c85f136c1e6f`  
**Predecessor tree:** `ffe65b1c48f332acdc5a7497b77a75ef64fd7500`

This stage is the test-first design and verification layer for the common
Bianchi algebra/Cartan generator. It is restricted to five witnesses:

- I;
- II;
- V;
- IX;
- the exceptional dynamical sector `VI_-1/9`, recorded as a sector of `VI_h`
  rather than a twelfth public algebra label.

The intended generator chain is

```text
BianchiTypeSpec
  -> canonical witness
  -> C^gamma_{alpha beta}
  -> Jacobi residual
  -> orthonormal-frame Levi-Civita connection
  -> spatial Riemann/Ricci witness values
  -> xAct/project Riemann-convention adapter
```

This stage does not derive the spacetime Einstein equations, background
matter evolution, chart dynamics, photon hierarchy coefficients, numerical
solver, REC/REI splice, observer transforms or `htt_base` outputs.

## TDD gate

`wolfram/BASS/Tests/ALG01/WitnessDesign.wlt` is committed before the public
ALG-01 APIs. The RED result must be recorded before implementation.

## Claim ceiling

```text
ALG01_WITNESS_DESIGN_ONLY
NO_BACKGROUND_EINSTEIN_DERIVATION
NO_ALL_BRANCH_BACKGROUND_SUPPORT
NO_GENERIC_ELL_COMPILER_CORRECTNESS
NO_IMPLEMENTATION_PARITY
NO_CROSS_REPOSITORY_COMPATIBILITY
NO_SCIENCE_VALIDITY
NO_PASS_RF04
```
