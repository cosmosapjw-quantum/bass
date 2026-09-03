# SYNC-MAP-02F-R2A — BASS formula/consumer role graph

This node is BASS-only. It is a normal-ancestry child of the locally replayed
BASS state-surface node at commit
`6bb65476a87d1ac8daa9f7239d884c369c51ce33`.

No REC, REI, or HTT source is modified or executed by this node. Exact-pinned
consumer source identities are classified as evidence only.

## Count contract

```text
formula-consumer pairs           10
implementation-role rows         11
named source symbols             12
explicit absent implementation    1
```

The pair and role levels are deliberately distinct. The HTT blackbody pair has
two roles:

```text
FULL_FIELD_PULLBACK
  pullback_thermodynamic_temperature_field

PREPULLED_VALUE_PRIMITIVE
  thermodynamic_temperature_pullback
```

The low-level primitive is not the full formula. Its input values must already
have been evaluated at inverse-aberrated source directions.

## Orthogonal relation fields

A single overloaded relation enum is forbidden. Every pair separately records:

```text
algebraic_relation
domain_relation
convention_adapter
unit_parameter_adapter
input_policy
numerical_policy
validity_subspace
authority_effect
parity_status
```

This prevents algebraic equivalence from being confused with implementation
presence, strict-domain equivalence, numerical regularization, or software
parity.

## REI firewall

The generic direction-flow implementation slot is explicitly absent.

For energy drift,

```text
R_REI  = -H
R_BASS = -H - sigmaEE
Delta  = R_REI - R_BASS = sigmaEE
```

The machine contract requires the exact residual

```text
Expand(((-H)-(-H-sigmaEE))-sigmaEE)=0
```

and rejects a merely nonzero check. Generic Bianchi REI photon parity remains
forbidden; the active H-only discretization is a FLRW or exactly isotropic
angular-subspace control.

## State-surface firewall

The parent BASS state registry remains authoritative for state typing:

- `GRID_F_Q_E <-> PSTF_F_AELL_Q` is a representation relation requiring a
  numerical transform certificate;
- `J_I_AELL` and `G_ANGULAR_ENERGY` are noninvertible spectral projections in
  general;
- polarized coherency requires screen-basis transport and a spin-phase
  convention.

## Local validation

```bash
bash scripts/run_sync_map02f_r2a_role_graph_local.sh
```

Expected result:

```text
Python verifier       PASS
Python unittest       9/9
Wolfram MUnit        11/11
failed/not-evaluated  0/0
exit code             0
```

Generated artifacts:

```text
SYNC_MAP_02F_R2A_WOLFRAM_REPLAY_RECEIPT.json
SYNC_MAP_02F_R2A_LOCAL_VALIDATION_SUMMARY.json
SHA256SUMS
```

## Literature role

- Dai & Chluba, arXiv:1403.6117: exact `d=1` boost combines celestial-sphere
  aberration with a Doppler weight.
- Yasini & Pierpaoli, arXiv:1709.08298: spin weight, Doppler weight, and
  frequency spectrum are distinct observable metadata.
- Schween & Reville, DOI 10.1017/S002237782200099X: angular representation
  conversion does not identify frequency-integrated moments with a
  frequency-resolved distribution.

Literature has `authority_effect=NONE` over BASS signs, semantic hashes,
consumer implementation status, or stage promotion.

## Claim boundary

This node types relations and source roles only. It does not establish consumer
runtime parity, grid/PSTF numerical parity, J/G closure, generic REI transport,
polarized screen transport, providers, likelihood readiness, or science
promotion.
