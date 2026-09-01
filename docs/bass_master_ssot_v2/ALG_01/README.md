# BASS Master SSOT v2 — ALG-01 Bianchi Algebra Witness Design

**Program ID:** `BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901`  
**Stage:** `ALG_01`  
**Exact parent:** `82776f50869d5c76e1cab4b28734c85f136c1e6f`  
**Parent tree:** `ffe65b1c48f332acdc5a7497b77a75ef64fd7500`  
**Jira owner:** `BASS-17`

## Purpose

This bounded stage converts the common three-dimensional Bianchi Lie-algebra
input into a tested symbolic contract before any Cartan connection, curvature,
Einstein equation or background evolution is derived.

The locked input is

```text
C^gamma_{alpha beta}
 = epsilon_{alpha beta delta} n^{delta gamma}
 + a_alpha delta^gamma_beta
 - a_beta delta^gamma_alpha,

epsilon_123 = +1,
n^{alpha beta} = n^{beta alpha},
n^{alpha beta} a_beta = 0.
```

## Deliverables

- fail-closed `BianchiTypeSpec` IR;
- exact structure-constant generator;
- independent vector and full-tensor Jacobi residuals;
- first Cartan coframe structure-equation renderer and reconstruction check;
- exact canonical witnesses for I, II, V, IX and exceptional VI_-1/9;
- hostile mutations for Jacobi, rank/inertia, Class-B and exceptional constraints;
- Wolfram tests, schemas, audit ledgers and stage receipt;
- GitHub, Dropbox and Atlassian synchronization receipts.

## Canonical-witness firewall

The integer/rational witnesses in this stage are dimensionless algebra
fingerprints. They are never substituted for dimensional physical ONF
magnitudes. Physical `a_alpha` and `n_{alpha beta}` retain dimension `L^-1` in
later geometry and background stages.

## Run

```bash
wolframscript -file wolfram/scripts/run_stage.wls --stage ALG_01
```

## Claim ceiling

```text
ALG_01_BIANCHI_ALGEBRA_WITNESSES_VERIFIED
NO_CARTAN_CONNECTION_OR_CURVATURE_DERIVATION
NO_BACKGROUND_EINSTEIN_MATTER_EQUATIONS
NO_ALL_FAMILY_SOLVER_SUPPORT
NO_GENERIC_ELL_COMPILER_CORRECTNESS
NO_NUMERICAL_PARITY
NO_CROSS_REPOSITORY_COMPATIBILITY
NO_SCIENCE_PROMOTION
NO_PASS_RF04
```
