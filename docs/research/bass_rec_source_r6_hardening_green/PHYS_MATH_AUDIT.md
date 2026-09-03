# PHYS–MATH audit — R6 authority hardening GREEN candidate

## Conventions and domain

- metric signature remains `(-,+,+,+)`;
- this protocol acts on a dimensionless photon occupation `f`;
- physical-time source rates satisfy
  `[eta]=[kappa]=[chi_affine]=T^-1`;
- `chi_affine:=kappa-eta` is signed although `eta,kappa>=0`;
- Q time obeys `d_tau=H_s_inv dt` on the explicit expanding domain
  `H_s_inv>0`;
- this node is scalar/unpolarized source metadata and does not alter the
  formula-SSOT polarized Thomson hierarchy.

## PM-01 — photon/boson source identity

The physical law is

```text
C_B[f] = eta(1+f)-kappa f.
```

With `chi_affine=kappa-eta`,

```text
C_B[f] = eta-chi_affine f.
```

The implementation evaluates the latter form.  Their exact real-arithmetic
residual is identically zero.  The affine form avoids a needless `inf-inf`
intermediate when large emission and absorption contributions nearly cancel;
it does not alter the equation.

Status: **PASS BY EXACT ALGEBRA; runtime replay pending**.

## PM-02 — statistics binding

For a fermion source,

```text
C_F[f] = eta(1-f)-kappa f,
C_B[f]-C_F[f] = 2 eta f.
```

The difference vanishes at vacuum occupation and is generally nonzero away from
vacuum.  Therefore a generic unlabeled source object is unsafe.  R6 binds the
constant pair to `photon` and `boson` and includes both labels in the canonical
payload hash.

Status: **PASS AT SOURCE-CONTRACT LEVEL**.

## PM-03 — signed zero

For nonnegative physical rates and occupations, IEEE-754 `+0.0` and `-0.0`
represent the same physical value.  Retaining their sign in `float.hex()` would
split one source into two payload identities.  R6 maps every accepted zero to
positive zero before storage and hashing.

This is exact canonicalization of a physically identical point, not a tolerance
projection or clipping of a nonzero rate.

Status: **PASS AT SOURCE-CONTRACT LEVEL**.

## PM-04 — Q-time conversion

On the declared expanding interval,

```text
d_tau = H_s_inv dt,
eta_per_tau = eta_s_inv/H_s_inv,
kappa_per_tau = kappa_s_inv/H_s_inv.
```

Dimensions are

```text
[eta_s_inv]=[kappa_s_inv]=[H_s_inv]=T^-1,
[eta_per_tau]=[kappa_per_tau]=1.
```

`H_s_inv<=0` and nonfinite `H_s_inv` remain outside this adapter.  A Bianchi-IX
recollapse crossing requires a different time chart; it is not silently
extended here.

Status: **PASS IN DECLARED DOMAIN; runtime replay pending**.

## PM-05 — finite arithmetic

Finite mathematical inputs do not guarantee a finite binary64 quotient or
product.  R6 rejects nonfinite results from

```text
eta_s_inv/H_s_inv,
kappa_s_inv/H_s_inv,
eta-(kappa-eta)f
```

through `SourceArithmeticError`.

Underflow to a finite zero is not rejected in this node.  That policy is
consistent with the test contract but remains a later numerical-sensitivity
question if these scalars are ever wired into a solver.

Status: **PASS AT SOURCE-CONTRACT LEVEL; solver-scale study deferred**.

## PM-06 — integrated moment-map nonidentifiability

Let one stored aggregate use weights `(w1,w2)` and another use `(w1,2w2)`.
The spectral perturbation

```text
s1' = s1+d,
s2' = s2-d w1/w2
```

preserves the first aggregate but changes the second by `-d w1`.  Hence a
source-integrated witness is not representation-free.  R6 binds it to one exact
state kind, moment map, radial-weight family, and source identity.

This binding certifies identity of the declared projection.  It does not prove
that the corresponding reduced source is a dynamically accurate closure.

Status: **PASS AT SOURCE-CONTRACT LEVEL**.

## PM-07 — controls

Required unchanged controls:

```text
eta=kappa=0        -> C[f]=0,
eta=3,kappa=2,f=5  -> chi_affine=-1 and C[f]=8,
H_s_inv=4          -> (eta_tau,kappa_tau)=(eta/4,kappa/4),
L_source=0         -> L_work=L_out.
```

R6 changes identity and admission semantics, not these physical controls.

## Ranked findings

### P0

None found in the source-level GREEN candidate.

### P1

1. Exact Python execution of the GREEN candidate is still required.
2. The integrated binding records a source hash but no adapter yet compares it
   to an actual incoming REC bundle; solver wiring remains forbidden.

### P2

1. Frame and channel remain normalized strings rather than registry-backed
   identifiers.
2. Underflow/subnormal sensitivity is not yet quantified.
3. The v2 canonical payload has no frozen externally replayed golden hash yet.

### P3

The term `integrated witness` may still be misread as a closure proof; it is
only target-specific provenance and compatibility metadata.

## Verdict

```text
PHYS_MATH_R6_GREEN_SOURCE_PASS
LOCAL_RUNTIME_AND_ADAPTER_EVIDENCE_PENDING
AUTHORITY_EFFECT_PROTOCOL_ONLY
```
