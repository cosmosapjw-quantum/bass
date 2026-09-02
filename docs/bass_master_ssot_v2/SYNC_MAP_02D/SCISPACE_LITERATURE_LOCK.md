# SYNC-MAP-02D SciSpace Literature-Role Lock

## Scope

This lock records the role of primary CMB literature in classifying the exact
`htt_base` WU-010/WU-011 local-observer boost surfaces. Literature is used for
formula regression and processed-estimator methodology. It does not decide
repository ownership, exact project signs, Git identities, provider admission,
or scientific claim promotion.

## Admitted primary papers

### Dai & Chluba (2014)

**Reference:** Liang Dai and Jens Chluba, *New operator approach to the CMB
aberration kernels in harmonic space*, Physical Review D **89**, 123504
(2014), DOI `10.1103/PhysRevD.89.123504`, arXiv:1403.6117.

**Admitted role:** exact full-sky harmonic Lorentz-boost regression. The paper
supports treating Doppler-weight-one thermodynamic CMB temperature as a
special exact boost representation and distinguishes the full-sky boost
operator from later experiment-specific processing.

**Not admitted:** BASS ownership, HTT code correctness, a global matter-frame
tilt, a Bianchi background, or cut-sky estimator validation.

### Ferreira & Quartin (2021)

**Reference:** Pedro da Silveira Ferreira and Miguel Quartin, *Disentangling
Doppler modulation, aberration and the temperature dipole in the CMB*,
Physical Review D **104**, 063503 (2021), DOI
`10.1103/PhysRevD.104.063503`, arXiv:2107.10846.

**Admitted role:** methodology for separating Doppler modulation, aberration,
and dipole effects under realistic beam, noise, and mask processing. This
supports classifying the processed HTT path as an observation-side estimator
response rather than as the same mathematical object as the exact full-sky
Lorentz theorem.

**Not admitted:** validity of the particular HTT estimator, empirical beta,
boost subtraction, global tilt, or Bianchi attribution.

### Pereira, Yoho, Starkman & Stuke (2010)

**Reference:** Thiago S. Pereira, Amanda Yoho, Glenn D. Starkman, and Maik
Stuke, *Effects of a Cut, Lorentz-Boosted Sky on the Angular Power Spectrum*,
arXiv:1009.4937.

**Admitted role:** warning that a sky cut can expose first-order boost effects
that are absent from the corresponding full-sky diagonal power-spectrum
summary. This supports a dedicated cut-sky response layer and rejects
identifying a full-sky kernel with the processed estimator.

**Not admitted:** a claim that a power-spectrum calculation alone validates
harmonic coefficients or the current low-ell response implementation.

### Gruetjen & Shellard (2014)

**Reference:** H. F. Gruetjen and E. P. S. Shellard, *Towards efficient and
optimal analysis of CMB anisotropies on a masked sky*, Physical Review D
**89**, 063008 (2014), DOI `10.1103/PhysRevD.89.063008`, arXiv:1212.6945.

**Admitted role:** mask-induced mode-coupling and augmented-estimator
methodology. This supports treating mask/beam/filter/nuisance operations as a
matrix-valued response layer with its own conditioning and identifiability
questions.

**Not admitted:** formula authority for the Lorentz boost or validation of the
HTT numerical thresholds.

## Classification consequence

The literature supports the following separation:

```text
exact full-sky Lorentz/frame theorem
  = common BASS formula authority

HTT exact local-observer implementation
  = consumer implementation and independent oracle

mask/beam/pixel/weighted-fit/nuisance response
  = HTT-owned processed extension
```

No paper found in this bounded search licenses replacing global cosmological
tilt, finite-electron-tilt Thomson scattering, or Bianchi background dynamics
with an output-side observer boost.

## Authority boundary

```text
authority_effect = NONE
repository_owner_selection = PROJECT_CONTROLLED
exact_signs_and_conventions = PROJECT_CONTROLLED
semantic_equivalence = NOT_PROMOTED_BY_LITERATURE
empirical_or_science_claim = NOT_PROMOTED
```
