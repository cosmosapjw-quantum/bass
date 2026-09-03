# NUM-BOOST-01 R3 — PSD, support, and roundoff hardening

This create-only research lane is a child of BASS Draft PR #108 exact head
`8ea1f7eaa9d703baa9cfb7a4d0678e410ce9d6d4`. It adds numerical-contract
hardening only. It does not change the six BASS owner FormulaIR records, any
REC/REI/HTT source, a provider, a production solver, or a scientific claim.

## Findings

### 1. Hermitian symmetrization is an orthogonal projection

For a raw square matrix `M`,

```text
H=(M+M^dagger)/2,
K=(M-M^dagger)/2.
```

For every Hermitian target covariance `C`,

```text
||M-C||_F^2=||H-C||_F^2+||K||_F^2.
```

Thus explicit symmetrization cannot increase Frobenius error relative to an
actually Hermitian target. The anti-Hermitian norm remains a required diagnostic
and must never be silently discarded.

### 2. A covariance eigenvalue floor is not automatically a numerical repair

For Hermitian `H=U diag(lambda_i) U^dagger`, clipping to a declared floor
`delta>0` gives

```text
Pi_delta(H)=U diag(max(lambda_i,delta)) U^dagger.
```

This is projection onto the convex set `C >= delta I`. It is nonexpansive only
relative to a target already known to belong to that same set. If the physical
model is known only to be PSD, a positive floor changes the model and must be
recorded as regularization.

In particular, if `lambda_min(H)<0`,

```text
||Pi_delta(H)-H||_2/delta
 >= (delta-lambda_min(H))/delta > 1.
```

Therefore an indefinite matrix cannot certify itself as likelihood-ready merely
by clipping its own eigenvalues and using the clipping distance against the new
floor. Either reject it, use an independently authorized physical/noise floor,
or provide an upstream backward-error proof against a known SPD target.

### 3. Weyl SPD guard

If an approximate Hermitian covariance has minimum eigenvalue `lambda_min` and
an independent spectral error bound `epsilon`, then the unknown exact covariance
is certified SPD only when

```text
lambda_min > epsilon >= 0.
```

Equality is not enough.

### 4. Retained-support compression must verify full support

Let `R^dagger R=I` and `P=R R^dagger`. Compression to `R` is equivalent to a
full-space degenerate Gaussian likelihood only if

```text
C_exact  = P C_exact P,
C_approx = P C_approx P,
(I-P)(mu_exact-mu_approx)=0,
(I-P)(x-mu_exact)=0,
(I-P)(x-mu_approx)=0,
```

and both compressed covariances are positive definite.

The parent PR #108 compression API checked only isometry and compressed SPD. A
counterexample with `C=diag(2,3,5)` and `R` retaining the first two coordinates
passes the old compressed-SPD check while silently dropping

```text
quadratic-form contribution = 4/5,
log-determinant contribution = log(5).
```

The new guard rejects such input.

### 5. Approximate support bases and projector drift

For a full-column-rank raw basis `R0`, the polar repair

```text
R=R0 (R0^dagger R0)^(-1/2)
```

satisfies `R^dagger R=I`. If

```text
epsilon_G=||R0^dagger R0-I||_2 < 1,
```

then

```text
||R0-R||_2 <= 1-sqrt(1-epsilon_G).
```

For orthogonal projectors `P` and `P_hat`,

```text
||P C P-P_hat C P_hat||_2
 <= 2 ||C||_2 ||P-P_hat||_2,

||P mu-P_hat mu||_2
 <= ||mu||_2 ||P-P_hat||_2.
```

These are explicit support-drift ledgers. They do not authorize inferring the
nuisance support anew from a noisy covariance. The preferred authority is a
frozen nuisance/design operator with exact provenance.

## Added Wolfram source

```text
wolfram/standalone/BASSNumBoostPSDSupportRoundoff.wl
wolfram/standalone/BASSNumBoostPSDSupportRoundoff.wlt
wolfram/standalone/run_psd_support_roundoff.wls
```

The WLT contains top-level `VerificationTest` expressions and the runner fails
unless the package self-check reports exactly `16/16`.

## Fresh connected-Wolfram evidence

Wolfram 15.0.1 executed an independent compact reconstruction of the package
fixtures:

```text
checks passed 16/16
failed         0
all passed     true
```

Exact fixtures include:

```text
negative-floor self-certification theorem       true
Hermitian floor-repair Frobenius norm squared   9/100
projector gap                                   3/5
outside-support quadratic discrepancy           4/5
outside-support logdet discrepancy               log(5)
```

This is session-level formula evidence. The exact committed file has not yet
been loaded by path and the WLT has not yet been executed through native
`TestReport`.

## Literature role

- Goulart, Nakatsukasa & Rontsis, arXiv:1908.01606, supports explicit accuracy
  analysis for numerical projection onto the PSD cone.
- Cai & Zhang, arXiv:1605.00353, supports treating retained-subspace drift as a
  separate singular-subspace perturbation problem.

Literature has `authority_effect=NONE`: it does not choose BASS conventions,
source ownership, semantic hashes, provider status, or scientific claims.

## Claim boundary

```text
PSD_SUPPORT_ROUNDOFF_SOURCE_CREATED
SESSION_WOLFRAM_16_OF_16_PASS

NO_NATIVE_EXACT_FILE_REPLAY
NO_GITHUB_WOLFRAM_RUNTIME_PASS
NO_DROPBOX_REPLAY
NO_PRODUCTION_COVARIANCE_REPAIR_POLICY
NO_HTT_LIKELIHOOD_READY
NO_PROVIDER_OR_SCIENCE_PROMOTION
```
