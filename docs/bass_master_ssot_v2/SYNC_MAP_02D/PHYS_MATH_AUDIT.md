# SYNC-MAP-02D PHYS–MATH Audit

## Verdict

`PASS_WITH_STRICT_LOCAL_OBSERVER_AND_FORMULA_CLASSIFICATION_BOUNDARIES`

This audit supports only the classification of exact HTT WU-010/WU-011
formula occurrences. It does not certify a BASS shared EquationIR export,
cosmological global tilt, finite-electron-tilt scattering, data fitting, or
Bianchi inference.

## Locked conventions and dimensions

```text
metric signature              (-,+,+,+)
photon propagation direction  e
outward sky direction         n=-e
active observer boost         +beta
beta                           v/c, |beta|<1
Lorentz factor                 gamma=(1-beta^2)^(-1/2)
Doppler factor                 D=gamma(1+beta.n)
thermodynamic Doppler weight   d=1
```

`n`, `beta`, `gamma`, `D`, and the solid-angle Jacobian are dimensionless.
The temperature pullback preserves the temperature unit. No natural-unit
identification is required.

## Formula ledger

### Exact Doppler charts

Current claim:

```text
D(n)=gamma(1+beta.n)=1/[gamma(1-beta.n_tilde)]
```

Actual evidence: the exact source implements both chart forms; the stateless
Wolfram residual is zero under `0<beta^2<1` and the unit-direction domain.

Strongest failure mode: reversing the boosted-chart sign would remain
superficially finite but would not equal the unboosted chart.

Minimal support condition: exact zero chart residual plus a sign mutation that
is nonzero. Both are present.

### Aberration and inverse aberration

Current claim: the HTT vector formulas define mutually inverse unit-sphere
maps for the active `+beta` observer convention.

Actual evidence: Wolfram gives zero for the aberrated unit-norm residual and
for both independent coefficients of the composed inverse map.

Strongest failure mode: silently projecting a non-unit output back to the
sphere could conceal a coefficient or denominator error.

Minimal support condition: algebraic unit norm and inverse identities before
any numerical normalization. The HTT source rejects non-unit input and does
not apply a silent output projection.

### Solid-angle Jacobian

Current claim:

```text
dOmega_tilde/dOmega = D(n)^(-2)
```

Actual evidence: differentiating the aligned angular characteristic
`mu_tilde=(mu+beta)/(1+beta mu)` gives an exact zero residual against `D^-2`.

Strongest failure mode: using `D^-1`, which has the right qualitative sign but
wrong measure weight.

Minimal support condition: exact Jacobian residual and a wrong-power mutation.
Both are present.

### Blackbody temperature pullback

Current claim:

```text
T_tilde(n_tilde)=D T(n(n_tilde))
```

Actual evidence: HTT applies Doppler weight one after inverse aberration and
requires strictly positive absolute thermodynamic temperature.

Strongest failure mode: applying the API to a signed anisotropy, arbitrary
frequency-dependent intensity, a foreground field, or a spectral distortion.

Minimal support condition: keep this as a restricted BASS frame theorem plus
an HTT positivity/unit adapter. The classification does so.

### First-order quadrupole response

Current claim:

```text
3 beta_<a Q_bc> n^a n^b n^c - (4/5)(Q.beta).n
 = 3(beta.n)Q_nn - 2(Q.beta).n.
```

Actual evidence: the exact STF3 plus dipole decomposition has zero Wolfram
residual. Separate omission mutations leave nonzero residuals:

```text
omit l=1:  -(4/5)(Q.beta).n
omit l=3:  3(beta.n)Q_nn-(6/5)(Q.beta).n
```

Strongest failure mode: retaining only the visually prominent octupole or only
the induced dipole.

Minimal support condition: both sectors must remain in the independent oracle.
They do.

## Known limits

- `beta=0`: aberration is identity, `D=1`, the Jacobian is one, and the
  first-order response vanishes.
- Constant positive temperature: finite local boost generates the usual
  Doppler pattern; this is not a global matter-frame tilt.
- Full-sky `d=1`: the exact Lorentz object is distinct from the subsequent
  mask/beam/pixel/weighted-fit operator.
- The classification contains no photon-geodesic time evolution and therefore
  cannot stand in for `BASS.PHOTON.DIRECTION_FLOW.001` or
  `BASS.PHOTON.ENERGY_DRIFT.001`.

## Hidden-assumption audit

1. The source sky is blackbody thermodynamic temperature, not generic
   intensity.
2. WU-010/WU-011 are scalar-temperature paths; processed polarization is not
   classified as implemented.
3. The observer velocity is an output-frame parameter and does not enter the
   BASS background or matter equations.
4. The first-order STF response does not justify an empirical beta estimator
   without nuisance/covariance modelling.
5. Literature relations have `authority_effect=NONE`.

## Ranked findings

```text
P0  none in the bounded relation/formula classification
P1  none in the six exact identities after corrected aggregation
P2  processed-polarization, frequency-dependent and finite-electron-tilt
    generalizations remain outside scope and must not be inferred
P2  02E shared export remains blocked until the independent 02C REI map closes
P3  native repository-file Wolfram replay remains a later durability check;
    the present exact algebra was run in a stateless connected evaluator
```

## Final boundary

```text
ALLOWED
  HTT local-observer formulas classified
  BASS common owner versus HTT consumer/oracle split
  HTT processed extensions separated

NOT ALLOWED
  shared formula export
  global matter tilt
  finite-electron-tilt Thomson
  empirical beta or subtraction
  Bianchi attribution
  provider/data/statistics/science promotion
```
