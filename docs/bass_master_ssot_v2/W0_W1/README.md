# BASS Master SSOT v2 — W0/W1 Authority Scaffold

**Program ID:** `BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901`  
**Stage:** `W0_W1`  
**Formula-stack base:** `0ac9f7e0ce8ff88dc7f4487a97e21be2863af207`  
**Base tree:** `8775d24f8ddc607be20879873d845e8568acfe15`  
**Jira owner:** `BASS-17`

This is the smallest durable Wolfram/xAct scaffold required before a Bianchi
background formula is derived.

## Scope

W0 owns exact Wolfram/xAct runtime identity and a fail-closed loader.

W1 owns:

- the convention lock;
- the physical-dimension registry;
- deterministic canonical serialization;
- exact-scalar semantic ASTs;
- equation and stage-receipt IRs;
- headless tests and public JSON schemas.

It does not derive geometry, Einstein equations, matter evolution, Bianchi
branch equations, photon hierarchy coefficients, observables, local boosts or
likelihoods.

## Run

```bash
wolframscript -file wolfram/scripts/run_stage.wls --stage W0_W1
```

A sealed local archive can be supplied with `--xact-source`.

## Gate IDs

- `BASS-WOLFRAM-ENV-001`
- `BASS-CONVENTION-LOCK-001`
- `BASS-DIMENSION-REGISTRY-001`
- `BASS-IR-ROUNDTRIP-001`
- `BASS-EQUATION-IR-001`
- `BASS-STAGE-RECEIPT-IR-001`

## Claim ceiling

```text
W0_W1_SYMBOLIC_INFRASTRUCTURE_VERIFIED
NO_BACKGROUND_TENSOR_DERIVATION
NO_IMPLEMENTATION_PARITY
NO_CROSS_REPOSITORY_COMPATIBILITY
NO_SCIENCE_PROMOTION
NO_PASS_RF04
```
