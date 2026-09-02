# BG-02 plot-based CRAG adversarial audit

The corresponding Wolfram plot source is `BG_02_CRAG_PLOTS.wl`.
The plot was also evaluated in the connected Wolfram 15.0.1 kernel during this
stage.

## 1. Exact off-shell rate separation

Let

\[
\delta_H=\frac{\mathcal H}{H_{\rm geom}^2}.
\]

The plotted curves are exact algebraic identities:

\[
\frac{F_{\rm ADM}-F_{\rm trace}}{H^2}=-\frac12\delta_H,
\]

\[
\frac{F_{\rm trace}-F_{\rm Ray}}{H^2}=-\frac16\delta_H,
\]

\[
\frac{F_{\rm ADM}-F_{\rm Ray}}{H^2}=-\frac23\delta_H.
\]

### Correctness

All three curves cross at the Hamiltonian constraint surface and only there.
Their slopes agree with the exact Wolfram residual identities.

### Retrieval

This behavior is consistent with the constraint-propagation literature: two
on-shell-equivalent formulations need not respond identically to off-shell
constraint drift.

### Augmented check

Changing the sign or coefficient of any one Hamiltonian-residual term breaks
at least one of the three exact identities.  The three curves therefore form a
small mutually checking diagnostic set rather than redundant decoration.

### Generation

A future numerical integrator that records only one expansion-rate formula can
hide formulation-dependent drift.  Integrate one primary rate, but emit all
three and their predicted residual ratios.

### Verdict

`SURVIVING CLAIM` — the three rates are on-shell equivalent and off-shell
diagnostically distinct.

## 2. Connection-index-order adversarial witnesses

The exact plotted witness values are

```text
             I      V       II      IX
locked       0     -6      -1/2     3/2
wrong        0     +4      +3/2     3/2
```

### Correctness

The locked route reproduces the composed W3 witnesses.  The deliberately wrong
route reads canonical `Gamma[[gamma,alpha,beta]]` storage as if it were locked
`Gamma[[alpha,beta,gamma]]` storage.

### Retrieval

The mismatch is fully explained by the exact BASS connection-storage contract;
it is not a change of Bianchi convention or curvature normalization.

### Augmented check

I and isotropic IX are false negatives: both accidentally pass under the wrong
route.  V detects the class-B-vector corruption; II detects the rank-one
`n_B` corruption.  Both are required.

### Generation

Every future geometry-consuming module should include at least one class-B
witness and one nontrivial class-A witness.  A flat and maximally isotropic
pair is insufficient.

### Verdict

`SURVIVING CLAIM` — the locked connection-order adapter is mandatory.

`REJECTED CLAIM` — passing only I and IX validates the connection-curvature
interface.

## Joint narrowed claim

The plots validate algebraic diagnostics and adversarial test selection.  They
do not validate numerical background evolution, tolerance stability,
constraint propagation or all-family runtime behavior.
