# P246 birth quadrature: exact geometry and the next shear-response coefficient

Date: 2026-10-20. Independent theory task within the BASS S11 continuation.
Baseline: `cosmosapjw-quantum/bass@d0c0313d6c063037fd8e067744aee66235df1a58`,
`research/bass_isotropy_response_20261018/`.

The existing S3 kernel, source-frame convention, P8 response coefficient, and
S8 precision-failure classification are reused. This note supplies a constructive
P246 support test, the finite-dimensional KL existence/uniqueness argument and
solver contract, and an independently derived fourth-order response coefficient.
It does not change the original `angular_p24.py` or `balance_p24.rs`.

## 1. Scope and the actual new construction

The metric has signature `(-,+,+,+)` and scale factors
`a_perp=a exp(-b)`, `a_parallel=a exp(2b)`. Write `d=b(x)-b(u)` and let
`mu` be a fixed direction in the birth source frame, with `z=mu^2`.
The positive normalized birth weights remain fixed after injection. The physical
stock, its directions and its previous birth weights are never inputs to this
projection operation.

The proposed operation minimizes the KL divergence from a positive,
reflection-symmetric prior on that same support while enforcing

\[
M_2=M_4=M_6=0,\qquad M_0=1.
\]

This is equivalent to matching the first three `z` moments of the isotropic
measure `dmu/2`:

\[
\sum_j\beta_j(z_j,z_j^2,z_j^3)=(1/3,1/5,1/7),\qquad
\sum_j\beta_j=1,\qquad\beta_j>0.                 \tag{1}
\]

Here `j` labels reflection orbits and duplicate `z` values are grouped. Within
each group, the original prior proportions are retained. For an exact reflection
pair with equal prior masses, the new pair masses are equal. This is the general
mathematical grouping statement; the isolated S11 implementation accepts only
strictly sorted distinct stored directions and rejects duplicate directions
rather than rewriting its input support. The target and all
features are dimensionless; no choice of `c`, `hbar`, or `k_B` is required.

## 2. An exact linear-cost support certificate

Let `0 <= z_1 < ... < z_m <= 1` be the distinct support values and define

\[
T=(1/3,1/5,1/7),\qquad v(z)=(z,z^2,z^3),
\]

\[
J(a,b,c)=\frac17-\frac{a+b+c}{5}
       +\frac{ab+ac+bc}{3}-abc.
                                                        \tag{2}
\]

`J` is the isotropic expectation of `(z-a)(z-b)(z-c)`.
For `m >= 4`, equation (1) has an all-positive solution precisely when

\[
L_i=J(z_1,z_i,z_{i+1})>0,
       \quad i=2,\ldots,m-1,                         \tag{3a}
\]

\[
U_i=-J(z_i,z_{i+1},z_m)>0,
       \quad i=1,\ldots,m-2.                         \tag{3b}
\]

Only `2m-4` cubic expectations are required after sorting and grouping.

### Proof of the facet characterization

Every four distinct points `v(z_j)` are affinely independent: the augmented
coordinate matrix is a Vandermonde matrix with nonzero determinant. Thus, for
`m>=4`, their convex hull has dimension three. A supporting plane intersects the
moment curve through a polynomial of degree at most three. A triangular facet
therefore has a polynomial proportional to
`(z-z_i)(z-z_j)(z-z_k)` with three distinct support roots.

For the polynomial to have one sign on all remaining ordered support points,
each sign-changing interior interval must contain no other support point.
The possible triples are exactly an adjacent pair together with the first
endpoint, or an adjacent pair together with the last endpoint. The signs chosen
in (3) are nonnegative on every support point and strictly positive on at least
one point outside that facet. These are all facets of the convex hull.

Necessity follows by taking the expectation under all-positive weights.
Sufficiency follows because strict satisfaction of all facet inequalities places
`T` in the interior of the convex hull. To see that interior membership yields
positive mass on every support vertex, let `vbar` be their uniform mean. For
sufficiently small `epsilon>0`,
`T_epsilon=(T-epsilon*vbar)/(1-epsilon)` remains in the convex hull. Any convex
representation of `T_epsilon`, mixed with the uniform distribution with mass
`epsilon`, represents `T` with all masses positive.

This is a specialization of finite-support moment geometry, not a new general
exclusion theorem. Negative facet values provide local infeasibility witnesses
for the supplied support. If every facet slack is nonnegative and at least one is zero, the target is on
the boundary and some support mass must vanish, contradicting this operation's
all-positive contract. A zero slack alone does not establish feasible boundary
membership if another slack is negative.

### Rank-deficient supports

The affine rank is `min(m-1,3)`. It must not be inferred by dropping numerically
small singular values.

For `m=3`, solve the unique masses from moments 0, 1 and 2. Then require all
masses positive and the exact affine compatibility `J(z_1,z_2,z_3)=0`.
For `m=2`, compatibility requires

\[
z_1+z_2=6/7,\qquad z_1z_2=3/35,
\]

with positive masses matching the mean. The support is the squared-node support
of ideal GL4. For `m=1`, the target has positive variance `4/45`, so no match
exists. A rank-deficient compatible problem has unique orbit masses here and
does not need a nonidentifiable three-parameter dual solve.

When stored binary64 `mu` values are interpreted exactly, use
`Fraction.from_float(mu)**2`, rather than the rounded product `mu*mu`, in the
certificate. A monic cubic with dyadic coefficients cannot have isotropic expectation
zero because the `1/7` term cannot cancel against terms with denominators
dividing `15*2^k`. Thus exact binary supports with at most three distinct `z`
values cannot satisfy all three exact targets. This arithmetic fact is a support
diagnostic, not a reason to loosen the output moment gate. Conservative native
code may report rank-ambiguous input as unresolved instead of implementing the
symbolic rank branches.

### Fixed exact controls

The following orbit support uses binary-exact direction cosines:

\[
\mu_{j,\ge0}=(0,1/2,3/4,1),\quad
z=(0,1/4,9/16,1),
\]

\[
\beta=(286/945,\ 32/105,\ 2048/6615,\ 61/735).
                                                        \tag{4}
\]

All masses are positive and the four moments in (1) match exactly.
Split each nonzero orbit into equal `+mu/-mu` masses.

A useful stronger-constraint negative control is

\[
\mu_{j,\ge0}=(0,1/4,1/2,1).
\]

Its minimum P24 lower gap is `1/30` and its upper gap is `2/15`, so the P24 target lies
strictly inside that lower-dimensional moment hull. Its P246 lower cubic facet
is `-1/42`. The unique formal P246 masses include `-2048/945`; this is an exact
witness for that support, not an admissible output.

## 3. The positive KL minimizer and a simultaneous solver

Let `q_j>0`, `sum q_j=1` and `phi_j=(P2(mu_j),P4(mu_j),P6(mu_j))`.
For a strictly feasible full-rank support, minimize

\[
\mathcal K(\beta\Vert q)=\sum_j\beta_j\log(\beta_j/q_j)
\]

First impose the equalities in (1) on the closed simplex with `beta_j>=0`.
Compactness gives a minimizer and strict convexity gives uniqueness.
If a candidate minimizer has a zero mass, mixing it
with an all-positive feasible distribution gives an entropy directional
derivative tending to `-infinity` at that zero entry. Hence the minimizer itself
is strictly positive. The finite-dimensional multiplier equations give

\[
\beta_j(\lambda)=\frac{q_j e^{\lambda\cdot\phi_j}}
                         {\sum_kq_k e^{\lambda\cdot\phi_k}}.
                                                        \tag{5}
\]

With `psi(lambda)=log sum_j q_j exp(lambda.phi_j)`,

\[
\nabla\psi=\langle\phi\rangle_\beta,\qquad
\nabla^2\psi=\operatorname{Cov}_\beta(\phi,\phi).   \tag{6}
\]

The covariance is positive definite on `m>=4` distinct supports: a zero
quadratic form would make a cubic linear combination of the Legendre features
constant on four or more distinct points, forcing every coefficient to vanish.
Consequently the dual minimizer is finite and unique.

These mean-map and covariance identities are standard finite exponential-family
results. A checked primary source is Wainwright and Jordan, *Graphical Models,
Exponential Families, and Variational Inference*, Sections 3.5.1–3.6, Proposition
2, Proposition 3 and Theorem 1 in the author-hosted version:
https://people.eecs.berkeley.edu/~jordan/sail/readings/wainwright-jordan-fnt.pdf
(read 2026-10-20, PDF pages 67–73).

The implementation contract is a simultaneous damped Newton solve, with a
centered covariance assembled directly as a sum of positive weighted outer
products. Solve the small linear system rather than forming a matrix inverse.
Evaluate (5) with a shifted log-sum-exp. All proposed iterates must retain finite
exponents, positive final masses, and exact reflection pairing.

The existing nested P24 solver separately asks its inner P2 solve to attain
`atol/8` and can hit binary64 resolution even when the final moment gate is
attainable. A simultaneous solve removes that nested stopping requirement. It
does not by itself prove that every feasible input is well conditioned.

An 80–100 decimal digit reference route can use exact rational features from
the supplied `mu` bytes, Decimal log/exp and the same simultaneous equations.
This gives a useful independent answer when binary64 objective differences or
gradient cancellation limit progress. It is a precision change of the new
algorithm, not a change of the source or physical acceptance criterion.

If a fixed invertible whitening transform is used, transform both the features
and target. In particular, centering the features by their prior mean changes
the transformed target: solving for zero transformed mean would otherwise solve
the wrong constraint. Dynamic Cholesky solves of the covariance avoid that
bookkeeping trap.

After rounding the output to binary64, certify the original *unnormalized*
moments using exact rational arithmetic:

\[
|\sum_i\alpha_i-1|\le3/10^{15},\qquad
|\sum_i\alpha_iP_\ell(\mu_i)|\le3/10^{15},
\quad\ell=2,4,6.                                    \tag{7}
\]

Do not divide the moments by the measured weight sum before applying (7).
Retain the prior/input bytes, all positive output weights, parity, internal
precision and stationarity residual, and distinguish exact support geometry
from the finite moment gate on rounded weights. Native outward interval
preflight may accept only definitely positive facet intervals; intervals that
straddle zero remain unresolved and are suitable inputs for the exact reference.

## 4. Reused P8 response and a new next-order diagnostic

S3 defines

\[
R=\sqrt{e^{2d}(1-z)+e^{-4d}z},\qquad
D=\frac{e^{-4d}z-e^{2d}(1-z)/2}{R},
\quad F=\langle R\rangle,\quad G=\langle D\rangle,
\quad\mathcal A=G/F.
\]

The conserved spatial momenta used to obtain this map are independently
supported by Fleury, Pitrou and Uzan, *Light propagation in a homogeneous and
anisotropic universe*, Section IV A, equations (4.1)–(4.5):
https://www2.iap.fr/users/pitrou/publi/1410.8473.pdf
(read 2026-10-20). The present even-pressure kernels specialize their
`beta_i=(-b,-b,2b)` geometry and are unaffected by ray-orientation sign.

The exact identity `F'=-2G` and the previously derived P8 coefficient are
reused. Writing `R=sum_n r_n(z)d^n`, the independent Fraction computation uses

\[
r_n=\frac12\left\{\frac{2^n(1-z)+(-4)^nz}{n!}
                       -\sum_{k=1}^{n-1}r_kr_{n-k}\right\},
\qquad D^{(n)}(0)=-\frac{(n+1)!}{2}r_{n+1}.
\]

At the next order it gives

\[
\begin{split}
D^{(4)}(0)={}&-\frac{320}{77}P_0+\frac{4528}{143}P_2
 +\frac{10080}{143}P_4-\frac{116640}{1309}P_6\\
 &-\frac{172800}{2717}P_8+\frac{3265920}{46189}P_{10}.
\end{split}                                             \tag{8}
\]

Its independent polynomial form is

\[
-\frac12+\frac{1563}{2}z-9675z^2+29565z^3
 -\frac{66825}{2}z^4+\frac{25515}{2}z^5.
\]

The pole and equator give respectively `16` and `-1/2`, agreeing with the
fourth derivatives of `exp(-2d)` and `-exp(d)/2`.

Under exact P246 matching, division by `F` yields

\[
\begin{split}
\mathcal A_\alpha(d)={}&-\frac85d+\frac87d^2
 +\left(\frac{368}{175}+\frac{288}{143}M_8\right)d^3\\
 &+\left(-\frac{248}{77}-\frac{7200}{2717}M_8
                         +\frac{136080}{46189}M_{10}\right)d^4
 +O(d^5).
\end{split}                                             \tag{9}
\]

Thus the leading error relative to the continuum isotropic angular measure is

\[
\mathcal A_\alpha-\mathcal A_{\rm iso}
=\frac{288}{143}M_8d^3
 +\left(-\frac{7200}{2717}M_8+\frac{136080}{46189}M_{10}\right)d^4
 +O(d^5).                                               \tag{10}
\]

The `d^3` term is already in S3. The `d^4` term supplies a new signed diagnostic:
subtracting the measured P8 cubic contribution and dividing by `d^4` should
approach the coefficient displayed in (10). A finite-d comparison must still
use the actual kernel integrals and the existing S6 bounds/refinement evidence.
Moment order alone gives no monotone pointwise improvement at arbitrary `d`.
For rounded outputs, the small accepted M2/M4/M6 residuals also contribute and
must be included when taking an extremely small-d limit.

## 5. Actual independent verification and remaining work

`exact_p246_derivation.py` uses Python's standard-library Fraction arithmetic,
without importing the project projector. It checks the reused third derivative,
the new fourth derivative, pole/equator limits, the normalized response, the
positive dyadic control and all four moments, and the facet criterion against
independent exhaustive tetrahedron barycentric representations on eleven small
fixed supports. All **25 checks passed** in the recorded execution, exit code 0.
These are mathematical assertions, not 25 physical histories.

Raw results: `EXACT_DERIVATION_CHECKS.json`. Its record includes the exact source
SHA256, Python version, rational coefficients, every support and facet slack,
and the independent barycentric coverage. No completed S9/S10 or S8 campaign,
ODE, native spectral calculation, or benchmark was called.

The root and Rust implementation still require their own changed-code tests,
rounded-output certificates, S8 failed-birth input comparison if available,
and scoped code review. The historical `INNER_P2_PRECISION_LIMIT` remains an
accurate result for the old algorithm. A successful new algorithm on its saved
input may close that particular solver obligation without replacing the old
raw failure or implying a completed native spectral history.

## Publication and runtime recovery provenance

The original and fresh recovery mathematical receipts are stored under `evidence/theory/`. The fresh `EXACT_DERIVATION_CHECKS_RECOVERY_R1.json`, with actual process stdout/stderr in the same directory, is the admitted execution evidence after the runtime interruption. The original result was reconstructed and admitted as historical identity only after its SHA256 matched the previously retained hash exactly; its reconstruction is not a new measurement. `evidence/theory/RECOVERY_RECEIPT.json` records both paths. The present 25 checks are one new mathematical unit, never S9/S10 or a native history replay.
