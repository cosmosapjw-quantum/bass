# R116-NATIVE-COLD-THOMSON-HARMONIC-EXACT-01

Bounded C1–C10 coding loop after HTT R115 188ca33d0813082ce23c6ce7a6d9419ef942c540.
Baseline BASS 4abb1d3b81a68711aa3438570f5a80f8cca42216; REC 6ad757d232a9833e984d18657d169766b27e33a4.
No REC/REI physics or inference gate changes. Cold elastic Thomson, bolometric,
real symmetric transverse coherency, expanding normal clock, beta=v/c<1.
All existing routes remain the default/unchanged. Opt in via
--route harmonic-continuum --harmonic-lmax L --harmonic-work-lmax W.
Angular quadrature remains for diagnostic sampled positivity, REC and output;
it does not assemble the new collision gain or solve the implicit cell.

## C1–C4: construction and numerical method

With propagation dyad m_+=t+i p, e×m_+=-i m_+, let D=gamma(1-beta.e)
and J the screen map of the existing ray kernel. Then
D J m_+=gamma m_++gamma beta×(e×m_+)-k beta(beta.m_+)
=K_+ m_+, with K_+=gamma I-i gamma [beta×]-k beta beta^T,
k=gamma²/(1+gamma), and K_-=conj K_+.
Wolfram vector triple product identity returned {0,0,0}.
Thus the Frobenius adjoint W=M* of M f=integral D² J f J^T dOmega
is W S=D² P J^T S J P. Its scalar trace is tr(L)-e^T L e
plus the antisymmetric linear term, L=K_+^T S K_-.
Its spin+2 field is m_+^T K_+^T S K_+ m_+.
Because m_+ is a spin-one l=1 vector harmonic, its quadratic product has
spin two and l=2. The scalar has l<=2. Algebraic equatorial Fourier
coefficient extraction uses the existing Wigner convention; no angular grid.
Use the orthonormal symmetric matrix basis (xx,yy,zz,xy,xz,yz), with
off-diagonal entries 1/sqrt(2). Stokes inner product: half the I product
plus one quarter of each signed spin product. This computes M exactly
on l<=2; G=(3/8pi) D^-5 W. No expansion in beta, no axial rotation.
Literature context: Dai & Chluba arXiv:1403.6117; Pitrou arXiv:1902.09456;
Challinor arXiv:astro-ph/9911481. This factorization is a direct derivation.

For implicit stage d, R=(1+d D)^-1:
 S=(I-d M R G)^-1 M R f; f1=R f+d R G S.
The scalar multiplier beta.e uses rank-one spin Gaunt couplings and
is Hermitian. On padded band W, CG inverts normalized I-t beta.e,
with continuum spectrum bounded below by 1-t|beta|. Recompute residual
including l=W+1, because a rank-one multiplier can excite exactly one
extra band. Reject if ||r||/((1-t|beta|)||x||)>1e-10; CG target 2e-14.
This is a per-inverse residual-based estimate, not a rigorous total
forward-error certificate (Gaunt roundoff, repeated inversions,
source conditioning and projection also matter). W<=256 explicit.
Compute D^-5 by five solves, retain padded first SDIRK stage through
second stage, then project output to L. No intermediate L projection.
The method approximates the continuum resolvent, not the resolvent of
P_L C P_L. For thin stages use f1=f+d(RG S-D R f); for SDIRK form
second input f+(1+sqrt2)(f1-f), avoiding O(1) cancellation.
Source condition and residual checked; positivity of truncated output
is sampled, not mathematically certified. No clipping or silent fallback.
Fixed recoil beta=(p0+p1)/(gamma0+gamma1) exchanges exact l=0,1 moments
with stream zero, and records continuum source tensors gain_map=None.
Subdivide on excessive acceleration/ill-conditioned source/sampled PSD failure.
Replay evaluates the unprojected rational cell along rays; finite L projection
between cells is a distinct error and must be measured separately.

## C5–C9 implementation and checks

Files: harmonic_collision.rs, field.rs, solve.rs, homogeneous_sky example,
tests/r116_continuum.rs. Added explicit route, signed reality/spin guards,
transactional recoil, continuum events, residual guard and stable thin step.
Initial API/route tests failed because feature absent. Two actual defects
were reproduced before repair: 2000 thin equilibrium SDIRK cells drifted
8.574474463785009e-12; malformed spin slots were accepted. See final log
for repaired result. Old ray and harmonic-grid routes not rewritten.
Single-cell test compares signed I,+2,-2 coefficients and stage source
tensors with independent existing ray collision on 64x128 grid, L=6,
d=0.3, beta vectors including off-axis and axial 0.85, both BE/SDIRK2.
Additional coupled recoil route comparison, invalid input and thin limit.
smoke.py exercises 12 families, FLRW control (observer boost remains on),
stronger tilt, VIstar time refinement, W refinement, and old R114 binary
byte regression. Not a new long/high-l recombination validation.

Commands:
 cargo test --release --locked --manifest-path _rustcore/Cargo.toml
 cargo test --release --locked --manifest-path _rustcore/Cargo.toml --examples
 cargo test --release --locked --manifest-path _rustcore/Cargo.toml --test r116_continuum -- --nocapture
 cargo build --release --locked --manifest-path _rustcore/Cargo.toml --example homogeneous_sky
 python3 research/r116_continuum_collision/smoke.py NEW_BINARY R114_BINARY NEW_OUTPUT_DIR

## C10 boundary and next work

Do not replace production grid route based on these tests. CG + repeated
Gaunt assembly + repeated recoil iterations may be much slower at small L.
Next optimize by caching rank-one coefficient couplings and using
axis-aligned tridiagonal direct resolvents with stable SO(3) action, or
reusing rational approximants. Benchmark at equal accuracy and physical
band/working band, certify stronger PSD and long optical-depth histories.
T1 coupled H/He/thermal chemistry, T2 global stiff second order, T4
frequency dependence, and T5 dispatch remain separate. No calibrated nulls,
ensemble covariance or R78 promotions. Native subagent tools not exposed;
serial implementation and independent existing numerical oracle.
