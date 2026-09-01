# BASS Formula SSOT v2 — CONV-00 + ALG-01 Witness Design

- Stage ID: `BASS-SSOT-V2-CONV00-ALG01-20260901`
- Status: `PASS_CONV00_ALG01_SCOPED_SYMBOLIC_WITNESS`
- Claim ceiling: `SYMBOLIC_WITNESS_ONLY_NO_BACKGROUND_RHS_NO_RUNTIME_NO_RF04_PROMOTION`
- Jira: `BASS-16` / `BASS-17`; provider gates remain `BASS-18`, `BASS-19`
- Parent plan: [BASS Formula SSOT v2](https://cosmosapjw.atlassian.net/wiki/spaces/BA/pages/20611074)

This is the first bounded derivation node of Formula SSOT v2. It imports the existing exact homogeneous polarized-photon SSOT and eleven-branch atlas without rewriting them.

## Completed scope

1. Canonical frame, sign, orientation, sky/propagation-direction, unit and rate registry.
2. Exact `TimeRate <-> RayLengthRate` adapters.
3. Universal Bianchi structure generator
   `C^gamma_{alpha beta}=epsilon_{alpha beta delta} n^{delta gamma}+a_alpha delta^gamma_beta-a_beta delta^gamma_alpha`.
4. Orthonormal-frame Koszul connection
   `Gamma_{alpha beta gamma}=(C_{alpha beta gamma}-C_{beta gamma alpha}+C_{gamma alpha beta})/2`.
5. Exact generic identities: structure antisymmetry, metric compatibility, torsion reconstruction, and
   `J^gamma_123=2 n^{gamma beta} a_beta`.
6. Exact witness gates for I, II, V, IX and exceptional `VI_-1/9`.
7. Adversarial nearby invalid records with nonzero residuals.

## Withheld

No spatial curvature, Einstein tensor, Hamiltonian/Codazzi system, background RHS/DAE, matter plugin, arbitrary-L production compiler, runtime source mutation, REC/REI integration, or RF04/science promotion is claimed.

## Reproduce

```bash
wolframscript -file research/formula_ssot_v2/stages/CONV00_ALG01_WITNESS_DESIGN_20260901/wolfram/run_stage.wl
```

For offline replay set `BASS_XACT_ARCHIVE=/absolute/path/xAct_1.3.0.tgz`. The archive must hash to `7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be`.
