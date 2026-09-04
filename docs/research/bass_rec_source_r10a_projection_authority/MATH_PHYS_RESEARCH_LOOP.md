# Mathematics/Physics Research Loop after R10

## Objective

Extend the scalar constant-source parity result into a model-independent hierarchy that can eventually support arbitrary practical harmonic rank, anisotropic source multiplication, production PSTF/Wigner layouts, polarized sources, and physical REC donor wiring without confusing algebraic exactness with numerical certification.

This document is a research plan and derivation note. It is not a production implementation claim.

## Loop A — close the projection authority

### A1. Exact discrete transform object

For retained real harmonics `Z_alpha`, define

```text
B_(q,alpha) = Z_alpha(n_q),
W = diag(w_q),
S[a] = B a,
P[f] = B^T W f.
```

The exact finite-dimensional parity statement is

```text
P S = B^T W B = I.
```

The authority object must therefore identify `B` and `W`, not only their construction names.

### A2. Dual identities

Use separate identities:

```text
H_spec: exact semantic declaration
H_real: binary64 nodes, weights and basis matrix
```

A consumer admits the operator only when both identities and all structural invariants validate.

### A3. Independent basis oracle

Validate at least:

```text
Y_00 = 1/sqrt(4*pi),
Y_10 = sqrt(3/(4*pi))*mu,
Z_11c = -sqrt(3/(4*pi))*sqrt(1-mu^2)*cos(phi),
Z_11s = -sqrt(3/(4*pi))*sqrt(1-mu^2)*sin(phi),
```

plus the addition theorem

```text
sum_(real modes at ell) Z_(ell alpha)(n)^2 = (2*ell+1)/(4*pi).
```

The production implementation must not serve as its own oracle.

### A4. Kill criteria

Reject the current design if any of these survive undetected:

```text
same-length weight mutation
same-length node mutation
basis sign/phase mutation
sample-layout mutation
stale stored hash
forged contract/report
```

## Loop B — continuous positivity and realizability

### B1. Analytic sufficient certificate

Write the scalar field as

```text
f(n) = a_00 Y_00(n) + sum_(ell=1)^L a_ell . Y_ell(n).
```

The real addition theorem gives

```text
||Y_ell(n)||_2 = sqrt((2*ell+1)/(4*pi)).
```

Therefore

```text
f(n) >= a_00/sqrt(4*pi)
       - sum_(ell=1)^L sqrt((2*ell+1)/(4*pi))*||a_ell||_2.
```

A sufficient global nonnegativity condition is

```text
a_00 >= sum_(ell=1)^L sqrt(2*ell+1)*||a_ell||_2.
```

A strict inequality gives a positive margin. This certificate is cheap, deterministic, model-independent, and conservative.

### B2. Stronger optional certificates

For states failing the norm bound but expected to remain positive, investigate in order:

1. interval subdivision in `(mu,phi)` with derivative bounds;
2. conversion to a trigonometric polynomial and certified global minimization;
3. sum-of-squares/semidefinite relaxation on the sphere;
4. exact low-rank algebraic critical-point solution.

Do not promote dense-grid sampling to a proof.

### B3. Report semantics

Every parity report should distinguish:

```text
node_positivity_pass
continuous_positivity_certified
positivity_certificate_kind
positivity_margin
```

## Loop C — high-rank numerical transform

### C1. Immediate admission policy

The current direct recurrence remains the low-rank oracle. Its executed certificate ends at `L=8`; that fact must control the public certified path.

### C2. Stable normalized recurrence

Use the fully normalized associated Legendre recurrence derived in the PHYS–MATH audit. It avoids separately generating huge `P_l^m` and tiny factorial normalizations.

### C3. Candidate numerical routes

Evaluate three routes independently:

```text
Route H1: normalized/scaled ALF recurrence + FFT in phi
Route H2: Clenshaw or Fourier-series Legendre synthesis/analysis
Route H3: qualified external SHT backend with an internal low-L oracle
```

For each route measure:

```text
pointwise basis error
B^T W B-I defect
round-trip coefficient error
rotation covariance
addition-theorem residual
runtime and memory
cross-platform realization hashes
```

### C4. Rank ladder

Increase the evidence envelope serially:

```text
L=8 -> 16 -> 32 -> 64 -> 128 -> 256
```

At each level require random, pure-mode, sparse, broadband and adversarial near-pole fixtures. No rank is admitted merely because construction returns finite values.

### C5. Literature methods to inspect first

Method-level seeds identified in the SciSpace pass:

- Wieczorek & Meschede, `SHTools`, DOI `10.1029/2018GC007529` — explicit normalization and Condon–Shortley controls;
- Schaeffer, efficient GL SHTs / SHTns, arXiv `1202.6522` — high-resolution on-the-fly Legendre evaluation;
- Cheong, Park & Kang, DOI `10.1007/s00190-012-0558-3` — stable Fourier-series representation and projection through very high degree;
- Holmes & Featherstone, DOI `10.1007/978-3-662-04709-5_43` — scaled ALFs and Clenshaw-style high-degree synthesis;
- Healy, Kostelec & Rockmore, DOI `10.1023/B:ACOM.0000016431.03652.65` — high-order Legendre transform stability;
- Blais & Soofi, DOI `10.1007/11758532_8` — information conservation and numerical stability in discrete SHTs.

These references do not determine BASS signs, conventions, tolerances or admission.

## Loop D — anisotropic scalar source multiplication

Let the state and source have bandlimits `L_in` and `L_s`:

```text
f(n) = sum_(ell m) f_(ell m) Y_(ell m)(n),
S(n) = sum_(L M) s_(L M) Y_(L M)(n).
```

The product coefficients are

```text
(S f)_(j m)
 = sum_(L M,ell m') s_(L M) f_(ell m')
   G^(j m)_(L M,ell m'),
```

where `G` is the Gaunt/Wigner kernel and the triangle rule requires

```text
|L-ell| <= j <= L+ell,
M+m' = m.
```

The product bandlimit is

```text
L_p <= L_in + L_s.
```

Projection through `L_out` is exactly integrated by the sufficient rule

```text
N_mu  >= ceil((L_in+L_s+L_out+1)/2),
N_phi >= L_in+L_s+L_out+1.
```

For a constant source `L_s=0` and `L_in=L_out=L`, this reproduces R10.

### D1. Required comparisons

1. coefficient-space Gaunt product;
2. oversampled grid multiply and project;
3. Wigner selection-rule oracle;
4. random rotation covariance;
5. alias mutants with one node removed in `mu` or `phi`.

## Loop E — production PSTF/Wigner bridge

The current tuple coefficients are not the production PSTF registry. The next bridge must prove one intertwiner:

```text
U P_PSTF = P_real-harmonic U,
```

with exact normalization, phase, mode order, rank domains and source unit field. The Formula SSOT supplies the generic-rank PSTF/Wigner authority, but the bridge still requires executable layout and hash contracts.

Required test sequence:

```text
pure scalar ranks 0,1,2
random finite-rank tensors
SO(3) covariance
improper-frame parity adapter where applicable
round trip PSTF -> harmonic -> PSTF
source action commutation
```

## Loop F — polarized and spin-weighted extension

After the scalar production bridge closes, repeat with project spin `-2` for `E+iB`:

```text
p^-_(ell m) = (Delta_ell/M_ell) Y^(ell m)_(A_ell) P^(A_ell).
```

The source kernel may couple spin and scalar harmonics. Every ratio `M_lout/M_lin`, common-map sign and Condon–Shortley phase must be applied exactly once. No polarized extension is admitted through scalar analogy alone.

## Loop G — physical REC donor and transport-time parity

Only after R10A, trusted-native differential, production layout parity and state-container parity may the physical donor be wired. The next physical gates are:

```text
pointwise frequency-local source table identity
nonlocal two-photon/Raman kernel identity
electron-frame collision/boost identity
Q-time and physical-time single-division identity
one-step source update parity
short-trajectory convergence
full transport residual closure
```

## Updated serial DAG

```text
R10 bounded local GREEN                         complete
R10A authority expected RED                    current
R10A authority GREEN                           blocked
R10B trusted-native differential               blocked
R11 production PSTF bridge RED/GREEN           blocked
R12 state-container source-step parity         blocked
R13 anisotropic scalar Gaunt product           research-open, code-blocked
R14 spin-weighted/polarized parity              research-open, code-blocked
R15 physical REC donor/source-step wiring       blocked
R16 transport-time and short-trajectory parity  blocked
```

## One load-bearing next step

Execute the exact R10A detached-worktree runner. The only admissible result opening production repair is:

```text
PASS_EXPECTED_R10A_PROJECTION_AUTHORITY_HARDENING_RED
16 tests / 13 assertion failures / 3 passing controls / 0 errors / 0 skips
49 inherited survivors
clean worktree
```
