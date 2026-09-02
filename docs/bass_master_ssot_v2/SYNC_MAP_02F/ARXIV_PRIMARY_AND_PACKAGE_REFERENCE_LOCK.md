# SYNC-MAP-02F arXiv-primary and package-reference lock

## Authority rule

Primary papers and external packages are independent regression sources only.
They do not choose BASS signs, Formula IDs, source ownership, Git identity,
consumer admission, numerical parity, or scientific claim promotion.

## Directly read arXiv primary sources

### Dai and Chluba — arXiv:1403.6117

Role admitted:

- exact harmonic-space Lorentz aberration kernels;
- arbitrary spin weight `s` and Doppler weight `d`;
- full-sky unitarity for `d=1`;
- exact recursion and independent rapidity-ODE algorithms;
- no full-sky E/B mixing if and only if `d=1`.

Project implication:

- BASS owns common full-sky Doppler/aberration/Jacobian formulas;
- HTT owns mask, beam, pixelization and processed-estimator extensions;
- full-sky identities do not establish cut-sky consumer parity.

### Challinor — arXiv:astro-ph/9911481

Role admitted:

- coordinate-independent PSTF polarization multipoles;
- exact observer dependence and general-spacetime polarized radiative-transfer
  structures;
- almost-FRW hierarchy as a regression, not a nonlinear all-Bianchi solver.

Project implication:

- the formula SSOT can use the general screen/PSTF structure;
- the displayed almost-FRW hierarchy cannot by itself admit the BASS
  nonlinear homogeneous background or an all-family runtime.

### Fleury, Pitrou and Uzan — arXiv:1410.8473

Role admitted:

- exact null geodesics, redshift and direction drift in Bianchi I;
- independent optical/Jacobi-matrix checks in a homogeneous anisotropic model.

Project implication:

- useful Bianchi-I regression for energy and direction characteristics;
- not evidence for the remaining ten public Bianchi families.

### Marcori, Pitrou, Uzan and Pereira — arXiv:1805.12121

Role admitted:

- separation of observer-velocity dipole from anisotropic-shear quadrupole in
  direction/redshift drift;
- explicit observer-versus-cosmological-anisotropy firewall.

Project implication:

- local observer boost must remain distinct from global matter tilt and
  forward anisotropic transport.

## Downloadable independent package probe

### CosmoBoost

Official repository:

```text
https://github.com/syasini/CosmoBoost
commit be29be2e9ba10424314f826a32e79008bdc2d2be
cosmoboost/blueprints.py blob 50d4de3261b02fc0118beb5a1799d8fe7729750f
```

The pinned source exposes a generalized kernel with configurable Doppler
weight `d`, spin weight `s`, boost velocity `beta`, `lmax`, and ODE/Bessel
methods. It is admitted only as an external local-observer aberration-kernel
reference.

The CI reference job shall:

1. clone the exact Git commit;
2. verify the `blueprints.py` Git blob;
3. parse the source AST without importing heavy optional dependencies;
4. attempt a versioned PyPI source/wheel download;
5. preserve download/import failures as package-compatibility evidence rather
   than reinterpret them as BASS formula failures.

## Explicit exclusions

None of the references above establishes:

```text
consumer implementation parity
finite-electron-tilt Thomson collision
primordial recombination or late reionization provider admission
11-family numerical solver support
background evolution
hierarchy truncation convergence
line-of-sight output readiness
statistics or data-fitting readiness
science validity
PASS_RF04
```
