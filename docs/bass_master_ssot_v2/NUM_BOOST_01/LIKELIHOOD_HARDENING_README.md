# NUM-BOOST-01 R2 — covariance and Gaussian-likelihood hardening

This create-only child of BASS Draft PR #107 hardens the standalone numerical
certificate. It does not change PR #99/101/102, any owner FormulaIR, provider,
solver, or scientific claim.

## Exact parent

```text
PR #107 head
1aa4dadffa7b44ff07b39a36a973c66047112345

parent package blob
f38eafdd7fd8c64bf4fb37ff8b59d4b762bc7448
```

## P1 contract defects found in the parent package

The parent functions `CovarianceSourceTailData` and
`CovarianceBoundaryResidualClosedForm` use identities that are valid for a
Hermitian covariance and an orthogonal cutoff projector, but the APIs do not
enforce those assumptions.

For Hermitian `C` and orthogonal `P`, with `Q=I-P`,

```text
||C-P C P||_F^2
 = 2||Q C P||_F^2 + ||Q C Q||_F^2.
```

For a general non-Hermitian matrix the correct decomposition is

```text
||C-P C P||_F^2
 = ||P C Q||_F^2 + ||Q C P||_F^2 + ||Q C Q||_F^2.
```

A fresh Wolfram counterexample gives `29-34=-5` for the old Hermitian-only
formula on `C={{1,2},{3,4}}`, `P=diag(1,0)`.

Likewise, for `C=P C P=C^dagger` and `B=Q B P`,

```text
R_C = B C + C B^dagger,

||R_C||_F^2
 = 2 Tr(B^dagger B C^2).
```

The hardening package fails closed unless the Hermiticity, projector, and
support obligations hold.

## Mean-aware Gaussian bridge

The earlier certificate assumes equal exact and approximate means. Bianchi and
global-tilt inference generally carries a deterministic mean template, so mean
error must have a separate ledger.

Let

```text
A = C_approx^(-1/2) (C_exact-C_approx) C_approx^(-1/2),
m = C_approx^(-1/2) (mu_exact-mu_approx),
rho = ||A||_2 < 1.
```

Then exactly

```text
D_KL[N(mu_exact,C_exact) || N(mu_approx,C_approx)]
 = 1/2 [Tr A - log det(I+A) + ||m||^2].
```

Consequently

```text
D_KL <= n/2[-rho-log(1-rho)] + ||m||^2/2,

D_KL <= ||A||_F^2/[4(1-rho)] + ||m||^2/2.
```

For fixed data, define

```text
z = C_approx^(-1/2)(x-mu_approx).
```

A conservative absolute bound for the change in `-2 log likelihood` is

```text
n[-log(1-rho)]
+ rho/(1-rho) (||z||+||m||)^2
+ 2||z||||m|| + ||m||^2.
```

All quantities after whitening are dimensionless.

## Nuisance projection and singular covariance

A nuisance projection can make the full-space covariance singular. The
likelihood certificate must then operate on a common retained subspace, not by
silently substituting a full-space pseudoinverse.

Let `R` have orthonormal columns spanning the common retained support:

```text
R^dagger R = I,
C_bar = R^dagger C R,
mu_bar = R^dagger mu,
x_bar = R^dagger x.
```

Both compressed covariances must be positive definite. If exact and approximate
support projectors differ, or the mean difference has a component outside the
common range, the certificate fails closed. On common support, compressed
quadratic forms and log determinants equal the corresponding pseudoinverse and
pseudodeterminant expressions.

## Fresh Wolfram evidence

Separate exact Wolfram 15.0.1 calls established:

```text
Hermitian source-tail identity                   PASS
non-Hermitian old-formula counterexample         residual -5
general non-Hermitian decomposition              PASS
Hermitian boundary-residual closed form          PASS
mean-aware Gaussian KL decomposition             PASS
spectral and Frobenius KL bounds                 PASS
fixed-data likelihood bound                      PASS
common-subspace pseudoinverse equivalence        PASS
common-subspace pseudodeterminant equivalence    PASS
```

The exact committed `.wl/.wlt` files have not yet been loaded by path and run
through `TestReport`; this remains a native-replay gate.

## Literature role

SciSpace was used to locate literature on Gaussian KL properties, covariance
perturbation, singular subspaces, and covariance operators. These sources
support the methodology and scope only. They do not choose BASS conventions,
Git identity, semantic hashes, or claim promotion.

## Claim boundary

```text
STANDALONE_HARDENING_SOURCE_CREATED
SESSION_WOLFRAM_IDENTITIES_PASS

NO_NATIVE_EXACT_FILE_REPLAY
NO_GITHUB_WOLFRAM_RUNTIME_PASS
NO_DROPBOX_REPLAY
NO_PROCESSED_HTT_LIKELIHOOD_READY
NO_PROVIDER_ADMISSION
NO_SCIENCE_PROMOTION
```
