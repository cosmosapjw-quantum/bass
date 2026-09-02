# SYNC-MAP-02C PHYS–MATH Audit

**Audited record:** `REI_RELATION_CLASSIFICATION_FIX2.json`  
**Verdict:** `PASS_WITH_NARROWED_GROUP_REDSHIFT_SCOPE`  
**Claim effect:** `NONE`

## Steelman

The active REI lineage contains a serious H/He thermochemistry and multigroup-radiation substrate: positive ion-fraction coordinates, free-electron counting, finite-optical-depth transmission, species allocation, signed opacity decomposition, maintenance accounting and a fail-closed absorption-capacity inequality. These are meaningful REI-owned relations rather than placeholders.

## Strongest objection

The code is not a Bianchi reionization transport solver. Its current group-redshift term is scalar and FLRW-like, while the exact homogeneous Bianchi photon energy drift is direction dependent. Without angular multipoles or an explicit closure, replacing the local control Hubble value by a BASS background Hubble value would still omit shear–radiation coupling.

## Conventions and dimensions

| Item | Check | Verdict |
| --- | --- | --- |
| Metric / photon formula authority | BASS formula layer uses `(-,+,+,+)` and `R(e)=-H_geom-sigma_ab e^a e^b` | PASS as external formula authority; not implemented in REI |
| `n_e` | `n_H x_HII+n_He(x_HeII+2 x_HeIII)` | PASS; dimensions `L^-3` |
| future `kappa_T` interface | `kappa_T=sigma_T n_e` | dimensionally `L^-1`; interface identity only |
| finite-τ transmission | `F_g=<exp(-tau_g(E))>_phi` | PASS; dimensionless and bounded for physical `tau>=0` |
| species allocation | normalized absorption weighting | PASS for finite nonzero total optical depth; zero-depth branch remains a code-level obligation |
| expansion work | `3 H p` | PASS only for isotropic pressure in the declared normal/FLRW control; generic tilted energy balance is outside scope |
| capacity gate | `J_H <= M_H+n_H^c(1-X_HII,start)/Delta_t` | PASS as a necessary condition, not a sufficient existence theorem |

## Exact angular-moment audit

For a trace-free shear tensor,

```text
<sigma_ab e^a e^b>_iso = 0.
```

Hence the scalar H-only redshift operator is exact on an exactly isotropic angular subspace. It is not exact once a quadrupole is present. With a trace-free quadrupole `Q_ab`, the unit-sphere moment gives

```text
<(sigma_ab e^a e^b)(Q_cd e^c e^d)> = 2 sigma_ab Q^ab / 15.
```

A concrete trace-free counterexample used

```text
sigma = diag(1,-1,0),
Q     = diag(2,-1,-1),
```

and returned `2/5`, not zero.

The first Wolfram nonzero-predicate check failed because a symbolic equality was wrapped in `Not`; the explicit counterexample and the tensor identity already passed. Replacing that predicate by `Not@PossibleZeroQ[...]` gave a fresh `6/6 PASS`. No physics formula was changed.

## FLRW-control correction

The implemented REI control is

```text
H(z)=H0 sqrt[Omega_m(1+z)^3+Omega_Lambda]
```

with `H0=67.4 km s^-1 Mpc^-1`, `Omega_m=0.315`, and `Omega_Lambda=0.685`. It omits radiation and is therefore a late-time flat-FLRW control, not a generic background authority. The identity

```text
H_with_radiation^2-H_control^2=H0^2 Omega_r a^-4
```

is retained only as a limitation witness; no radiation-inclusive REI code path was found.

## Ranked findings

### P0

None within the bounded relation-classification claim.

### P1

1. **H-only group redshift is not generic Bianchi transport.** Minimal condition: consume the BASS energy-drift and direction-flow formulas and implement an angular hierarchy or explicitly justified closure.
2. **Numerical BASS background lock is absent.** Minimal condition: a typed provider schema, exact pin, units/time-coordinate contract and residual-bearing background history.
3. **FLRW control omits radiation.** This is admissible only as an explicitly scoped control; it cannot silently serve as a high-precision universal background.
4. **Global matter tilt is absent.** `3Hp`, opacity and group redshift remain normal-frame/non-tilted control relations.

### P2

1. The future Thomson-opacity factorization is mathematically sound but has no active REI CMB collision implementation.
2. The finite-τ allocation proof used the finite nonzero-τ domain; the exact zero-depth limiting branch must be verified in code.
3. The capacity inequality is necessary only; passing it would not prove a unique or stable coupled history.

### P3

No notation or dimensional defect changes the current classification.

## Allowed conclusion

`SYNC-MAP-02C` may close as an active-lineage ownership and dependency classification. It may not be cited as Bianchi reionization transport, background coupling, exact Thomson implementation, first canonical interval, provider admission or scientific validation.
