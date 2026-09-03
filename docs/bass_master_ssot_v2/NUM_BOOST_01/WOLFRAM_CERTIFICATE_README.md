# NUM-BOOST-01 standalone Wolfram certificate

## Scope

This create-only evidence lane starts from the exact `SYNC-MAP-02F R2 RED` head

```text
bff74a1383f0d113621bd49936d2eebed3264707
```

and adds a standalone Wolfram package and top-level MUnit test file. It does not modify PR #99, PR #101, REC, REI, HTT, any provider, or any scientific claim.

Files:

```text
wolfram/standalone/BASSNumBoostCertificate.wl
wolfram/standalone/BASSNumBoostCertificate.wlt
wolfram/standalone/run_numboost_certificate.wls
```

## Locked conventions

```text
metric signature          (-,+,+,+)
boost rapidity            eta=arctanh(v/c), dimensionless
angular multipole rank    ell
physical ray length       s=c t; never called ell
Doppler weight            d=1 in the finite-unitary boost sector
spin sectors              s=0 and s=+/-2 supported
```

The package does not implement gravitational polarization-screen transport. The local-observer Lorentz boost and Bianchi screen-basis transport remain separate nodes.

## Exact generator

For fixed spin `s` and azimuthal index `m`,

```text
G |s,ell,m>
 = B_s(ell+1,m)|s,ell+1,m>
 - B_s(ell,m)|s,ell-1,m>,

B_s(ell,m)
 = sqrt[((ell^2-m^2)(ell^2-s^2))/(4 ell^2-1)].
```

The finite fixed-`m` Galerkin generator is real skew-symmetric for `d=1`. The `+2` and `-2` matrices are identical because the coefficient depends on `s^2`.

## Finite-buffer theorem

For output cutoff `T`, work cutoff `W=T+B`, and `r=B+1`,

```text
Q_W G^k P_T = 0                         for k<r
P_T G^k P_T = P_T (P_W G P_W)^k P_T    for k<2r.
```

The unique shortest path has coefficient

```text
Product[B_s(j,m), {j,T+1,W+1}].
```

For the exact fixture `s=0,m=0,T=2,W=4`, its square is

```text
32000/539.
```

## State and covariance residuals

With

```text
B_W = Q_W G P_W,
```

the state and covariance defects are

```text
r_W   = B_W y_W,
R_C,W = B_W C_W + C_W B_W^dagger.
```

For Hermitian `C_W`,

```text
||R_C,W||_F^2
 = 2 Tr[B_W^dagger B_W C_W^2]
 = 2 Sum_m B_s(W+1,m)^2 Sum_alpha |C[(s,W,m),alpha]|^2.
```

The covariance source-tail identity is

```text
||C-P C P||_F^2
 = 2||Q C P||_F^2 + ||Q C Q||_F^2.
```

Hence an anisotropic or Bianchi covariance cannot be certified from diagonal high-ell power alone; the cross-tail block `Q C P` is load-bearing.

## BipoSH bridge

For an ordered `(ell1,ell2)` covariance block, the package constructs

```text
U[(L,M),(m1,m2)]
 = (-1)^m2 <ell1 m1, ell2 -m2 | L M>.
```

The exact fixture verifies both `U U^dagger=I` and `U^dagger U=I`, so the covariance Frobenius norm is the Euclidean norm of the corresponding BipoSH coefficient vector.

For `kappa_L=||A_L||_2^2` and a certified coefficient error `epsilon_L`,

```text
|kappa_L-kappa_L_approx|
 <= (2 sqrt(kappa_L_approx)+epsilon_L) epsilon_L.
```

## Gaussian likelihood bridge

Let

```text
C_exact = C_approx^(1/2) (I+A) C_approx^(1/2),
rho     = ||A||_2 < 1.
```

Then

```text
|log det C_exact-log det C_approx|
 <= -n log(1-rho),

|x^T(C_exact^-1-C_approx^-1)x|
 <= rho/(1-rho) x^T C_approx^-1 x,

D_KL[N(0,C_exact)||N(0,C_approx)]
 <= n[-rho-log(1-rho)]/2,

D_KL
 <= ||A||_F^2/[4(1-rho)].
```

A covariance Frobenius certificate `epsilon_F` and an approximate covariance spectral floor `lambda_min` imply the fail-closed bound

```text
rho <= epsilon_F/lambda_min.
```

No Gaussian likelihood certificate is issued unless this ratio is below one.

For a fixed processed operator `M`,

```text
||M deltaC M^dagger||_F <= ||M||_2^2 ||deltaC||_F.
```

HTT must therefore provide a processed-operator gain bound, or a certified numerical upper bound, before the full-sky covariance certificate can become a processed-likelihood certificate.

## Fresh Wolfram evidence

The connected Wolfram 15.0.1 kernel successfully executed the underlying exact fixtures in separate calls:

```text
finite-buffer structure                    3/3 PASS
covariance/source-tail identities          3/3 PASS
BipoSH unitarity and Parseval              3/3 PASS
spin +/-2 and adjacent covariance          3/3 PASS
Gaussian likelihood/KL fixture bounds      5/5 PASS
aggregate                                 17/17 PASS
```

Preserved harness history:

1. a single large integrated call returned HTTP 502;
2. the first BipoSH iterator construction was malformed;
3. unguarded Clebsch-Gordan calls emitted nonphysical-entry messages;
4. the selection-rule-guarded reconstruction was message-free and exact;
5. direct `Get` from the raw GitHub URL failed, so exact repository-file replay remains pending.

The `.wlt` contains top-level `VerificationTest` expressions, not tests hidden inside one `Module`. The runner also fails unless the package self-check reports exactly `17/17`.

## Primary-source role

- Dai & Chluba, arXiv:1403.6117: unitary `d=1` spin-weighted boost operator, exact harmonic recursions, rapidity evolution.
- Jawecki, Auzinger & Koch, arXiv:1809.03369: defect-based computable upper bounds for matrix-exponential approximations.
- Hajian & Souradeep, arXiv:astro-ph/0501001: BipoSH coefficients as Clebsch-Gordan combinations of covariance entries.

These sources support methodology and regression. They do not choose BASS signs, owner identities, semantic hashes, consumer parity, or provider/science admission.

## Run locally

```bash
wolframscript -file wolfram/standalone/run_numboost_certificate.wls
```

Native MUnit discovery:

```wl
TestReport["wolfram/standalone/BASSNumBoostCertificate.wlt"]
```

## Claim boundary

```text
STANDALONE_WL_SOURCE_CREATED
SESSION_LEVEL_WOLFRAM_17_OF_17_PASS

NO_NATIVE_EXACT_FILE_REPLAY
NO_GIT_STAGE_PASS
NO_DROPBOX_REPLAY
NO_EXTERNAL_CAS_REPLAY_OF_THIS_FILE
NO_NUM_BOOST_RUNTIME_IMPLEMENTATION
NO_OFF_DIAGONAL_RUNTIME_CONVERGENCE
NO_LIKELIHOOD_READY
NO_PROVIDER_OR_SCIENCE_PROMOTION
```
