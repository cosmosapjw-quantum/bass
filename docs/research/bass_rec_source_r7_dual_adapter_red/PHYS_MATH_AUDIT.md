# PHYS–MATH audit — R7 dual-adapter RED

## Conventions and dimensions

- metric signature: `(-,+,+,+)`;
- spatial orientation: `epsilon_123=+1`;
- photon occupation: `[f]=1`;
- physical-time source rates: `[eta]=[kappa]=T^-1`;
- signed affine coefficient: `chi_affine=kappa-eta`, `[chi_affine]=T^-1`;
- Q time: `d_tau=H_s_inv dt`, with `[H_s_inv]=T^-1`;
- ray-length coefficient: divide a physical-time rate by explicit `c`, giving
  dimension `L^-1`.

The source authority remains the positive pair `(eta,kappa)`. No projection of
`chi_affine` onto the nonnegative cone is allowed.

## PM-01 — distribution/coefficient commutation for a constant pair

Let a linear angular basis have coefficients `f_alpha`, and let
`unit_field_alpha` be the coefficients of the constant function one. For

```text
C[f] = eta - chi_affine f,
```

linearity of projection gives

```text
Pi C[f]
  = eta Pi[1] - chi_affine Pi[f]
  = eta unit_field_alpha - chi_affine f_alpha.
```

Thus grid application and coefficient-space application commute exactly on a
shared projection domain. This conclusion depends on the explicit unit-field
coefficients; it does not assume a universal numerical monopole normalization.

Status: **PASS as exact linear algebra; implementation absent by design.**

## PM-02 — axisymmetric Legendre fixture

The first numerical fixture uses

```text
f(mu) = 0.9 P0(mu) + 0.2 P1(mu) - 0.1 P2(mu) + 0.05 P3(mu)
eta=3, kappa=2, chi_affine=-1.
```

Therefore

```text
C[f] = 3 + f
```

and its Legendre coefficients are

```text
(3.9, 0.2, -0.1, 0.05).
```

Four-node Gauss–Legendre quadrature is exact for polynomials through degree
seven. Projection of this degree-three source against `P_l`, `l<=3`, therefore
has no quadrature remainder in exact arithmetic.

Status: **PASS as an independent survivor control.**

## PM-03 — stimulated-emission mutation

Dropping the bosonic `+eta f` term changes the source from

```text
eta*(1+f)-kappa*f
```

to

```text
eta-kappa*f.
```

The exact mutation residual is

```text
eta*f.
```

It vanishes in the vacuum and is therefore invisible to an `f=0` smoke test.
The fixture `eta=3`, `f=5` gives a residual of `15`.

Status: **PASS; non-vacuum test required.**

## PM-04 — time-basis conversion

For `d_tau=H_s_inv dt`,

```text
C_tau[f] = C_t[f]/H_s_inv.
```

With `eta=3`, `kappa=2`, `f=5`, `H_s_inv=4`, the physical-time source is `8`
and the Q-time source is `2`.

For the ray-length convention `(1/c) partial_t`,

```text
C_length[f] = C_t[f]/c.
```

The test uses `c=2` as an exact unit fixture, giving `4`. This is not a natural-
unit declaration; the production adapter must accept the explicit physical
speed of light or another explicitly named unit-consistent value.

Status: **PASS as algebra and dimensional analysis; implementation absent.**

## PM-05 — rank condition

The first slice has an angularly constant source coefficient, `L_source=0`.
It therefore requires only

```text
L_work >= L_out.
```

For a later finite-band anisotropic source,

```text
L_work >= L_out + L_source
```

is required generically. An anisotropic exponential jump is not finite-band in
general and is excluded from this stage.

Status: **PASS after scope narrowing.**

## PM-06 — integrated-state firewall

A radial-integrated angular state or a finite integrated `J^(i)` hierarchy does
not contain the spectral data needed for a generic frequency-dependent source.
R7 admits only the full spectral grid and spectral PSTF coefficients. Existing
`IntegratedMomentMapBinding` remains necessary but is not itself a spectral
reconstruction theorem.

Status: **PASS.**

## PM-07 — source/frame/projection identity

Two numerical results are comparable only when they share:

- the source payload identity;
- the physical parent-state identity;
- the projection-contract identity;
- the time-basis convention.

Their representation identities must differ, because one result is a grid and
the other is a coefficient state. Equality of representation hashes would be a
provenance error, not stronger parity.

Status: **PASS.**

## Ranked findings

### P0

None in the test-only slice.

### P1

1. assuming a universal numerical value for the unit-field monopole;
2. comparing grid and PSTF outputs without a shared projection-contract hash;
3. applying physical-time rates directly in Q time or ray length;
4. treating an integrated state as spectrally complete;
5. promoting the constant-pair commutation fixture to a physical REC source or
   general anisotropic-source theorem.

### P2

1. using same-cutoff projection when a later anisotropic source has nonzero
   angular rank;
2. accepting a bare 26-direction vector without quadrature and parent identity;
3. testing only the vacuum, which misses stimulated-emission mutations;
4. silently substituting `c=1` at the SI/ray-length boundary.

## Verdict

```text
PHYS_MATH_R7_RED_CONTRACT_PASS
IMPLEMENTATION_ABSENT_EXPECTED_RED
NO_PHYSICAL_SOURCE_OR_NUMERICAL_PARITY_CLAIM
```
