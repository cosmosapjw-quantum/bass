# PHYS–MATH audit — R6 hardening RED

## Locked conventions

- metric signature `(-,+,+,+)`;
- spatial orientation `epsilon_123=+1`;
- occupation `f` dimensionless;
- `eta_s_inv`, `kappa_s_inv`, `chi_affine_s_inv`, and `H_s_inv` have dimension `T^-1`;
- Q time is dimensionless with `d_tau=H_s_inv dt` on an expanding interval;
- the primary physical object is the nonnegative pair `(eta,kappa)`;
- `chi_affine=kappa-eta` is derived and signed.

## PM-01 — statistics binding

The current pointwise law is

```text
C_B[f] = eta (1+f) - kappa f.
```

This is the bosonic occupation factor. For a fermionic lane,

```text
C_F[f] = eta (1-f) - kappa f,
```

so

```text
C_B[f] - C_F[f] = 2 eta f.
```

The two agree at `f=0`, which makes a vacuum-only smoke test insufficient. A production authority object must therefore bind the particle/statistics semantics, not only its channel string.

Status: **mathematical requirement established; fresh Wolfram replay unavailable in this stage**.

## PM-02 — integrated moment-map nonidentifiability

Let two spectral cells carry source values `(s1,s2)`. Define

```text
G = w1 s1 + w2 s2
```

and the perturbed pair

```text
s1' = s1+d,
s2' = s2-d w1/w2.
```

Then `G'=G`, while another radial moment map such as

```text
J = w1 s1 + 2 w2 s2
```

changes by `-d w1`. Thus equality under one integrated map does not authorize another integrated map.

Consequence: every integrated source witness must bind its target state, exact moment map, radial-weight family, and source identity.

Status: **PASS by exact algebra; no new numerical claim**.

## PM-03 — signed-zero canonicalization

IEEE binary64 distinguishes the encodings of `+0.0` and `-0.0`, but the present rate contract gives them the same physical meaning. The v1 payload hashes `float.hex()` strings, so keeping the sign bit creates two payload identities for one source.

The R6 physical convention is:

```text
accepted rate == 0.0  -> stored and hashed as +0.0.
```

This is a semantic canonicalization, not a numerical approximation.

Status: **required**.

## PM-04 — finite arithmetic

Input finiteness alone does not imply output finiteness in binary64. The two exposed operations are

```text
eta_per_tau   = eta_s_inv/H_s_inv,
kappa_per_tau = kappa_s_inv/H_s_inv,
C[f]          = eta_s_inv(1+f)-kappa_s_inv f.
```

Very small positive `H_s_inv` or very large finite rates/occupation can overflow. A source authority must not return `inf` or `nan` as though it were an admitted physical rate. R6 therefore requires a typed arithmetic failure after the operation.

Status: **required software realization of a finite-domain mathematical contract**.

## PM-05 — schema transition

R6 adds species/statistics semantics and canonicalizes zero. These are identity-changing semantics. They must not share the v1 payload namespace.

```text
v1  bass.source_authority.constant_pair.v1
v2  bass.source_authority.constant_pair.v2
```

Status: **required**.

## PM-06 — retained controls

The hardening must preserve:

```text
eta=kappa=0       -> C[f]=0,
eta=3,kappa=2,f=5 -> chi_affine=-1 and C[f]=8,
H_s_inv<=0        -> Q-time adapter rejected.
```

The `H_s_inv>0` condition is a chart/domain statement for the current expanding-Q-time adapter, not a theorem covering a Bianchi-IX recollapse crossing.

Status: **already passing at R5; protected by R6 controls**.

## Relation to the attached TEFF papers

Paper I separates radial spectral information from angular information and proves that refinement along one axis does not generally recover the other. Paper II adds number–energy and thermochemical moment maps, but states explicitly that its results are kinematic one-event coarse-graining geometry rather than transport equations or solver closures. Those papers support the refusal to treat one integrated witness as a universal spectral source; they do not provide the missing runtime adapter.

## Verdict

```text
PHYS_MATH_R6_RED_CONTRACT_PASS
NO_NEW_P0_CONTRADICTION
FRESH_WOLFRAM_SERVICE_UNAVAILABLE
AUTHORITY_EFFECT_NONE
```
