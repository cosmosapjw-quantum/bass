# SciSpace literature-role lock — SYNC-MAP-02C R3

**Role:** external methodology and scope cross-check only.

**Authority effect:** `NONE`.

The search question asked which primary papers derive or use the Lorentz
transformation of CMB temperature, aberration and solid angle, and which papers
show that a masked or cut-sky response is not identical to the full-sky
physical pullback.

## Admitted references and bounded roles

1. **Dai & Chluba, “New operator approach to the CMB aberration kernels in
   harmonic space,” arXiv:1403.6117.**
   Admitted for the exact full-sky Lorentz-boost operator and Doppler-weight
   bookkeeping for spin-weighted CMB observables. It supports treating the
   physical pullback as a closed full-sky operator. It does not define the BASS
   project direction sign or prove HTT implementation correctness.

2. **Ferreira & Quartin, “Disentangling Doppler modulation, aberration and the
   temperature dipole in the CMB,” arXiv:2107.10846.**
   Admitted for the distinction between aberration, Doppler modulation,
   temperature-unit conversion and realistic mask/noise response. It supports
   retaining processed estimator response as an HTT-owned downstream extension.

3. **Yasini & Pierpaoli, “Generalized Doppler and aberration kernel for
   frequency-dependent cosmological observables,” Phys. Rev. D 96, 103502
   (2017), DOI 10.1103/PhysRevD.96.103502.**
   Admitted for frequency- and mask-dependent observable response. It does not
   authorize replacing absolute thermodynamic-temperature pullback with a
   frequency-dependent intensity shortcut.

4. **Catena & Notari, “Cosmological parameter estimation: impact of CMB
   aberration,” JCAP 04 (2013) 028, and its JCAP 07 (2013) E01 erratum.**
   Admitted as a warning that pseudo-spectrum/cut-sky comparisons require the
   correct processed response. The erratum is part of the methodological lock;
   the original headline result is not used without it.

5. **Planck Collaboration, “Planck 2013 results. XXVII. Doppler boosting of the
   CMB: Eppur si muove,” arXiv:1303.5087.**
   Admitted for observation-side mode-coupling context only.

## Project-owned conclusions

The literature does not choose project signs or ownership. The exact project
adapter remains

```text
outward sky direction n = -e
D(n) = gamma(1 + beta.n) = gamma(1 - beta.e)
dOmega_tilde/dOmega = D^-2
T_tilde(n_tilde) = D T(n(n_tilde))
```

The full-sky physical formulas belong in the BASS shared export. Mask,
sampling, interpolation, estimator and cut-sky response remain HTT-owned
processed extensions. Global matter tilt is not inferred from this local
observer pullback.

## Not admitted

- project formula ownership or semantic identity;
- current Git or source-byte identity;
- global-tilt implementation;
- finite-electron-tilt collision physics;
- data-fitting readiness or science promotion.
