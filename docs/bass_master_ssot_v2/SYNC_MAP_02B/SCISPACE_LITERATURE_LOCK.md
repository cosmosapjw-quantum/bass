# SYNC-MAP-02B SciSpace literature lock

This literature lock is methodological and physical-regression support only. It does not select project conventions, Git authority, formula ownership, source blobs, semantic hashes, or provider readiness.

## Adopted bounded roles

### Challinor, *Microwave background polarization in cosmological models*

- Supports the coordinate-independent PSTF polarization formalism, observer dependence, and exact 1+3 covariant radiation variables.
- Supports treating screen/polarization transport as a common theorem rather than rederiving it independently in every microphysics repository.
- Does **not** establish the byte identity, exact index ordering, or production use of the BASS/REC implementation.
- Its displayed hierarchy is almost-FRW and therefore is not used as authority for the exact homogeneous nonlinear Bianchi hierarchy.

### Fleury, Pitrou and Uzan, *Light propagation in a homogeneous and anisotropic universe*

- Supports direction-dependent redshift and direction drift in a spatially homogeneous anisotropic spacetime, with an independent Bianchi-I geometric-optics route.
- Serves as a limit/regression source for separating anisotropic background drift from observer aberration.
- Does **not** supply the all-eleven-type BASS structure-constant generator or REC moving-face microphysics.

### Pitrou, Uzan and Pereira, *Direction and redshift drifts for general observers and their applications in cosmology*

- Supports separating observer peculiar-velocity aberration from anisotropic-shear contributions.
- Supports the firewall between common observer/frame transformations and REC-owned hydrogen-frame/source-face specialization.
- Does **not** prove equality of the REC Python formulas to BASS EquationIR records; that requires project-local exact canonicalization.

### Santana et al., *Evolution of the electric field along null rays for arbitrary observers and spacetimes*

- Supports a covariant observer-dependent screen/polarization transport viewpoint in geometrical optics.
- Serves only as a qualitative and tensor-structural cross-check.
- Does **not** establish Thomson collision coefficients, Bianchi branch predicates, or numerical solver validity.

### Pontzen and Challinor, *Bianchi model CMB polarization and its implications for CMB anomalies*

- Supports a homogeneous-Bianchi radiative-transfer and polarization regression in the nearly-FRW regime, including recombination/reionization context.
- Is explicitly treated as a restricted-regime regression rather than authority for exact nonlinear, finite-tilt, or arbitrary-family dynamics.

## Excluded authority uses

The literature does not determine:

- the locked project signature `(-,+,+,+)` or `epsilon_123=+1`;
- whether a REC occurrence is an import, specialization, extension, or duplicate;
- GitHub/Dropbox/Atlassian authority boundaries;
- the exact BASS semantic hash;
- physical 26-direction face admission;
- REC provider readiness, cross-repository compatibility, numerical parity, or science validity.

## Stage conclusion

The literature supports the conceptual separation

```text
BASS common frame/photon theorem
  -> REC hydrogen-frame specialization
  -> REC moving Doppler face and event surfaces
```

but the four common BASS formulas must still be exported as canonical EquationIR records before exact cross-repository import locks can replace the current algebraic residual evidence.
