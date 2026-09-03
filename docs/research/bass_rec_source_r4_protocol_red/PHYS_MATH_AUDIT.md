# PHYS–MATH audit

## Conventions

- metric signature: `(-,+,+,+)`;
- spatial orientation: `epsilon_123=+1`;
- photon occupation `f` is dimensionless;
- REC source rates `eta_s_inv`, `kappa_s_inv`, `chi_affine_s_inv` have dimension `T^-1`;
- Q integration time `tau` is dimensionless and obeys `d_tau=H_s_inv dt` on the declared lane;
- propagation direction and outward sky direction must remain separately named;
- the positive physical source object is `(eta,kappa)`, while `chi_affine=kappa-eta` is signed.

No convention is imported from documentation prose without matching code/formula evidence.

## Audit ledger

### PM-01 — physical-time/Q-time conversion

For

```text
df/dt = eta_t (1+f) - kappa_t f
```

and `d_tau=H dt`, the dimensionless Q-time rates are

```text
eta_tau   = eta_t/H
kappa_tau = kappa_t/H
chi_tau   = (kappa_t-eta_t)/H.
```

The exact constant-segment affine update is invariant under this conversion. Wolfram gives zero residual and zero residual derivative with respect to `H` after the complete conversion. Status: **PASS**.

### PM-02 — source JVP

The exact instantaneous variation is

```text
delta C = (1+f) delta eta - f delta kappa - (kappa-eta) delta f.
```

Wolfram residual: zero. Status: **PASS**.

### PM-03 — angular product work rank

For an output through `L_out` and a finite-band source coefficient through `L_source`, generic Gaunt coupling requires distribution input through

```text
L_work >= L_out + L_source.
```

The `(2,2,4)` Legendre witness has zero buffered residual, while the same-cutoff mutation retains explicit rank-three/rank-four terms. Status: **PASS**.

### PM-04 — exponential jump tail

A finite-rank optical depth does not imply finite-rank transmission. For example,

```text
tau(mu)=tau0+alpha mu
exp[-tau(mu)]=exp[-tau0] exp[-alpha mu]
```

has generically nonzero coefficients at every rank. The finite product-buffer theorem must not be reused for this nonlinear jump. Status: **PASS, inherited from R2**.

### PM-05 — Mode-A source identifiability

A radial-integrated angular state stores only a weighted spectral integral. Two spectra can share that integral while yielding different frequency-dependent absorption integrals:

```text
Delta G = 0,
Delta A = d w1 (chi1-chi2).
```

The difference vanishes in the grey control. Status: **PASS**.

Consequence: generic REC source action on Mode A is mathematically underdetermined without a source-integrated witness, extra spectral variables, or an explicit closure.

### PM-06 — all-rank formula versus finite numerical rank

The formula SSOT defines all-rank PSTF/Wigner transport. The inspected numerical paths declare finite rank walls and boundary policies. These statements are compatible only when “all rank” is reserved for formula authority and “finite workspace” for numerical evolution. Status: **PASS after claim narrowing**.

### PM-07 — massless and isotropic controls

Required controls for R5/R6:

- `L_source=0` removes the generic angular work-rank buffer;
- isotropic `tau` makes the jump rank preserving;
- `eta=kappa=0` gives exact source-off identity;
- `eta>=0`, `kappa>=0` allows signed `chi_affine` without invalidating the positive pair;
- full spectral grid integration must reduce to a source-integrated witness when that witness is supplied.

Status: **DEFINED, NOT EXECUTED**.

### PM-08 — TEFF scope firewall

Paper I separates radial spectral and angular information losses; Paper II refines the spectral term with number–energy/thermochemical information and supplies conditional realizability and finite-cutoff statements. Both are static one-event state-space results. They neither generate a transport source nor justify replacing the full distribution by a representative. Status: **PASS after role lock**.

## Ranked findings

### P0

None in the committed RED documentation/test slice.

### P1

1. Any implementation that applies a generic spectral source directly to Mode A from `G(e)` alone.
2. Any numerical claim that calls the finite PSTF workspace untruncated.
3. Any source adapter that drops `(eta,kappa)` and rejects the physically allowed signed `chi_affine` branch.
4. Any use of an entropy-selected TEFF representative as an undeclared transport closure.

### P2

1. Missing `H_s_inv` or double application of the Q-time conversion.
2. Same-cutoff angular source projection without an isotropic/sparsity theorem.
3. Finite-rank treatment of anisotropic exponential jumps without a tail receipt.
4. Comparison of spectral `F_A_l(nu)` with integrated `J^(i)_{A_l}` or Mode-A `G(e)` as if they were identical states.

### P3

Notation and branch-lineage ambiguity can still cause the right formula to be attached to the wrong runtime.

## Verdict

```text
PHYS_MATH_RED_CONTRACT_PASS
IMPLEMENTATION_NOT_PRESENT
CLAIM_EFFECT_NONE
```
