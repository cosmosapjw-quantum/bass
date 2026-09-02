# SYNC-MAP-02C SciSpace Literature-Role Lock

**Role:** `EXTERNAL_METHODOLOGY_AND_SCOPE_CROSS_CHECK_ONLY`  
**Authority effect:** `NONE`  
**Search date:** 2026-09-02

## Search questions

1. Which primary papers establish the exact covariant polarized photon Boltzmann hierarchy and Thomson collision operator in anisotropic or Bianchi cosmologies, and how do they distinguish normal-frame geometry, electron-frame scattering, and observer-frame Lorentz boosts?
2. Which primary papers define physically consistent hydrogen–helium recombination or reionization thermochemistry, free-electron density, Thomson opacity, and multigroup photon redshifting in an expanding cosmological background, and which parts are microphysics rather than spacetime-geometry authority?

## Admitted papers and bounded roles

| Paper | Identifier | Admitted role | Not admitted as |
| --- | --- | --- | --- |
| A. Challinor, *Microwave background polarization in cosmological models* | arXiv:astro-ph/9911481 | general-spacetime PSTF polarization, observer dependence, electron-rest collision context | proof of the project’s Bianchi implementation or REI coupling |
| A. Naruko, C. Pitrou, K. Koyama, M. Sasaki, *Second order Boltzmann equation: gauge dependence and gauge invariance* | arXiv:1304.6929 | tensor-valued distribution, tetrad choice and gauge-scope cross-check | authority for project signs, branch registry or FormulaIR identity |
| J. Portsmouth, E. Bertschinger, *A tensor formalism for transfer and Compton scattering of polarized light* | arXiv:astro-ph/0412094 | electron-rest scattering followed by frame transformation | evidence that REI implements finite-electron-tilt CMB scattering |
| J. Chluba, A. Ravenni, *The Boost Operator: Properties, Computation and Applications* | arXiv:2505.02080 | distinction between radiation-frame boost operators and collision corrections | permission to identify local observer boost with global matter tilt |
| Y. Ali-Haïmoud, C. Hirata, *HyRec: A Fast and Highly Accurate Primordial Hydrogen and Helium Recombination Code* | arXiv:1011.3758 | H/He population and radiation-field microphysics; sparse numerical coupling | authority for Bianchi spacetime geometry or the REI late-time provider |
| E. Switzer, C. Hirata, *Primordial helium recombination I: feedback, line transfer, and continuum opacity* | doi:10.1103/PhysRevD.77.083006 | helium line/continuum microphysics and H-I opacity feedback | proof of current REI numerical validation |
| M. Norman et al., *Fully coupled simulation of cosmic reionization I: numerical methods and tests* | doi:10.1088/0067-0049/216/1/16 | methodological comparison for coupled radiation, thermal and ionization systems | validation of the project’s homogeneous Bianchi coupling or source model |

## Classification consequences

The literature supports the following owner separation:

```text
BASS
  spacetime geometry, background evolution, photon transport schema,
  electron-frame collision schema and observer-output frame transforms

REI
  H/He population state, thermochemistry, multigroup ionizing radiation,
  opacity decomposition, maintenance and capacity gates

adapter boundary
  BASS H/background values -> REI group-redshift and expansion-work operators
  REI n_e/history values   -> future BASS opacity/collision consumers
```

It does not establish that any of these adapter boundaries are currently implemented end-to-end.

## Excluded inferences

- no replacement of exact Git source or project FormulaIR by literature prose;
- no semantic equality from similar notation;
- no finite-electron-tilt Thomson implementation claim;
- no global-tilt or local-observer-boost implementation claim in REI;
- no numerical BASS background lock;
- no first canonical interval or provider admission;
- no data, likelihood or scientific-result promotion.
