# ACCEL02 theory: preserve the discrete measure, reduce repeated arithmetic

2026-10-21, Asia/Seoul. Status at Stage A: algebra derived and independently
checked with Wolfram; native implementation and numerical admission pending.
The full frozen implementation and acceptance contract is FROZEN_CONTRACT.md.

## 1. Evidence reused and the next obligation

The warm C15 pilot already contains729 cases,243 passing groups and47,385
history rows over a=0.1999→0.2. Independent matter and radiation stress seeds
are retained. The ACCEL01 exact cache and completed-case planner are reused.
Current BASS PR177 and REI PR214 changed documentation only; the original pilot
subtree and11 inspected Python files agree with the prior snapshot. Latest
C21M98/125 results belong to the PR147 collisionless z=20→4 family and do not
validate this warm source/chemistry model. See intake/LATEST_DELTA.json and
intake/BACKUP_DELTA.json for exact source/read coverage and claim separation.

The remaining selected obligation is computation on a cache miss. The original
owner evaluates the same three finite-mass moments on3072 points, materializes
several96×32 arrays, and reduces them. No timing profile is claimed. The source
structure establishes repeated reflection-pair arithmetic and makes a local
substitution possible without altering the model, grid or coupled solver.

## 2. Conventions and dimensional boundary

The spacetime signature is(-+++). The existing owner uses x=ln(a/a0), with
x,b,q and m/T dimensionless. Its physical reference density supplies the units
after quadrature. This work does not set physical c,hbar,k_B to1 in the
reported physical equations. For the time-rate Einstein convention used by the
owner, kappa_t=8pi G/c^2=3*KAPPA. The half-contraction norm is
|A|_h=sqrt(A_ab A^ab/2); the Frobenius norm is sqrt(2) times this norm.

In the orthonormal LRS frame,

    sigma^i_j = diag(-s,-s,2s),
    pi_A^i_j  = diag(-D_A/3,-D_A/3,2D_A/3),
    Sigma_signed = sqrt(3)*s/H,
    Pi_A_signed  = kappa_t*D_A/(sqrt(3)*H^2),
    sigma_ab*pi_A^ab = 2*s*D_A.

Matter is the pinned nonbaryonic massive Vlasov component. Radiation contains
gamma, massless nu and the evolved UV contribution. Alpha_m and alpha_r remain
independent; gamma and nu share alpha_r in this pilot. Sum D_m+D_r before
taking the total norm; never sum component norms. Neither the source grouping
nor its small signed cancellation residual is changed by the new kernel.

## 3. Existing finite quadrature

Let r=exp(-x), u_j=mu_j^2 and define

    R_j^2 = exp(2b)*(1-u_j) + exp(-4b)*u_j,
    p_ij^2 = r^2*q_i^2*R_j^2,
    E_ij = sqrt(m^2+p_ij^2),
    v_ij^2 = p_ij^2/E_ij^2,
    ubar_j = exp(-4b)*u_j/R_j^2,
    P2(z) = (3*z^2-1)/2.

The stored original weights are

    W_ij(alpha_m) = (rw_i/norm)*wmu_j*(1+alpha_m*P2(mu_j)).

The96 radial points and32 angular points are exactly those constructed by the
pinned MassiveRadialGrid. Its finite sums are

    J0 = r^3 sum_ij W_ij E_ij,
    J1 = r^3 sum_ij W_ij E_ij v_ij^2,
    J2 = r^3 sum_ij W_ij E_ij v_ij^2*(3*ubar_j-1)/2.

J1 is the spatial pressure trace in these normalized units; J2 is the LRS
pressure difference. The physical owner uses rho_ref*J0 and rho_ref*J2.
The nonlinear H, radiation hierarchy and chemistry are still evaluated at each
actual trajectory state; only this component quadrature is replaced.

## 4. Reflection folding theorem and its domain

The original Gauss–Legendre nodes and weights satisfy
mu_(31-j)=-mu_j and wmu_(31-j)=wmu_j. The P2 seed is even. Every kernel above
depends on mu through mu^2, hence K_i(−mu)=K_i(mu). Therefore in exact arithmetic

    sum_(j=0..31) W_ij K_ij
      = sum_(j=0..15) [W_ij+W_i,31-j] K_ij.

The identity retains all32 nodes and their measure. It does not replace the
rule with leggauss(16), approximate the radial dependence, or impose isotropic
stress. Anisotropy b and signed alpha_m remain unrestricted within the owner
domain. The native preparation explicitly checks the actual paired arrays;
the proof is not used as permission to assume parity for a different source.
Odd angular data, tilt or a changed closure requires a different backend.

NumPy's existing leggauss construction symmetrizes nodes/weights. The runtime
check is still useful because the mathematical identity applies to the arrays
actually supplied to the native call. Input parity and source identity are
scientific prerequisites, not a generic adversarial security mechanism.

The structural count is3072→1536 distinct energy/square-root evaluations per
cache miss. Three moment accumulators share each energy and pressure factor.
The16 angular factors can be prepared once per call. This is an operation
count, not a2x wall-time prediction; Python/ctypes overhead, chemistry, adaptive
ODE work, compilation and worker scheduling remain outside this count.

## 5. Positivity and two differential identities

For the complete continuum angular interval P2 lies in[-1/2,1]. Consequently
1+alpha_m*P2 is nonnegative for -1<=alpha_m<=2. For positive quadrature weights,
m>0 and real x,b, one has0<=v^2<=1 and0<=ubar<=1. Termwise bounds give

    0 <= J1 <= J0,             -J1/2 <= J2 <= J1.

These bounds survive the finite quadrature itself. They are valuable signed
stress diagnostics but do not establish the accuracy of the quadrature relative
to the continuum Vlasov integral.

The distribution weights are fixed in the conserved momentum coordinates.
At fixed b, d_x E=-p^2/E. At fixed x,

    d_b R^2 = 2 exp(2b)(1-u)-4 exp(-4b)u
             = -4 R^2*(3*ubar-1)/2,
    d_b E = -2*(p^2/E)*(3*ubar-1)/2.

Differentiating the SAME finite sums, not an additional continuum approximation,
therefore yields

    d_x J0 = -3 J0 - J1,        d_b J0 = -2 J2.

Along the owner's trajectory dx/dt=H and db/dt=s,

    d_t(rho_ref*J0) = -H*(3 rho_m + pressure_trace_m) -2*s*D_m.

Since pressure_trace_m=3*p_m, this has the collisionless energy-balance form
rho_dot_m+3H(rho_m+p_m)+sigma_ab*pi_m^ab=0 with the pinned units. This proves
the consistency of the quadrature stress-work sign within its assumptions.
It does not supply a radiation/UV/donor-escape Q^a closure.

Wolfram returned parity residuals[0,0,0], both derivative residuals0,
contraction2*dd*ss, no counterexample to the P2 bound, and alpha in[-1,2].
Its context service failed internally; the actual language evaluator succeeded.
The precise code and returned text are in evidence/WOLFRAM_CHECK.json.

## 6. Summation, cancellation and acceptance

There are two distinct cancellations: signed P2 terms inside J2, and D_m+D_r
outside the kernel. Folding changes a reduction order, so numerical comparison
is needed even though the finite sums agree algebraically. The native evaluator
uses compensated accumulation and retains the original external component sum.

Higham1993 analyzes summation conditioning and shows why a relative error in a
nearly vanishing sum is unsuitable as the only criterion [P1]. Ogita, Rump and
Oishi2005 describe Neumaier's compensated variant and its leading error control
for a sum of floating-point inputs [P2, Eq.1.3]. The new implementation reuses
that published algorithmic idea with attribution; it does not import a large
solver library or copy a proprietary implementation.

For computed summands t_l and unit roundoff u, the cited Neumaier bound has
the form u*|sum t_l| + (0.75*n^2+n)*u^2*sum|t_l|, under its stated arithmetic
assumptions and3*n*u<=1. It concerns the reduction of already-computed terms;
it is not a bound for transcendental evaluation, quadrature truncation, the
whole Einstein–Boltzmann trajectory or general model error.

The acceptance contract instead fixes an empirical componentwise envelope
|delta J_k|/J0_owner <=64*eps64 (eps64=2^-52) on140 specified points, with
signed absolute comparisons of coupled observables and all original gates.
In particular, no relative error division by a cancelling J2 or Pi_total is
used. The tolerances were frozen before the new native results were observed.
The small3-point finite-difference check tests the derivative identities, not
convergence. Five2-step warm comparisons test the new code connection; the
original64-step729 results remain the pilot evidence.

The compiler must retain compensation arithmetic. GCC documents that Ofast
enables fast-math and that ffp-contract=off disables contraction [P3]. The
recipe uses explicit no-fast-math/no-contraction options, and records the actual
compiler, flags and loaded binary. There is no blanket claim of SIMD emission:
strict reductions may constrain automatic vectorization. The delivered gain is
fusion, reflection reuse, fewer large temporaries and process-level parallelism.

## 7. Integration and resource accounting

ACCEL01 caches exactly repeated binary64(x,b) within one immutable model.
Native models keep that mechanism and insert a native evaluator only on cache
misses. A distinct backend namespace binds source, loader, build recipe,
contract and actual library. Thus a changed reduction cannot inherit a false
byte-equivalence claim from the original exact-cache backend.

The existing scheduler admits independent pending cases using current CPU and
memory availability. It already supports64CPU/128GiB target caps, thread1 per
worker, shared-resource observation and partial-case restart. The new kernel
does not create a second scheduler or nested OpenMP pool. The completed729 plan
still exits pending0 before build/load/job creation. A busy NCP host permits a
smaller admitted batch; unrelated Codex sessions do not require global shutdown.

The local observed limit is8CPU/8GiB. The separately discovered C21M receipt
historically reports64affinity CPUs,61workers and about80.20GiB available out
of about125.78GiB; this is not a current live NCP probe or an allocation to us.

## 8. Primary sources and claim ceiling

- [P1] N.J.Higham, The Accuracy of Floating Point Summation, SIAM J.Sci.Comput.
  14(4),783–799(1993), DOI10.1137/0914050.
  https://nhigham.com/wp-content/uploads/2023/10/high93s.pdf
- [P2] T.Ogita, S.M.Rump, S.Oishi, Accurate Sum and Dot Product,
  SIAM J.Sci.Comput.26(6),1955–1988(2005), DOI10.1137/030601818.
  https://www.tuhh.de/ti3/paper/rump/OgRuOi05.pdf
- [P3] GCC official optimization documentation:
  https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html
- [P4] NumPy2.3.5 installed leggauss source, inventoried in CODE_GAP_SURVEY.md;
  official source location:
  https://github.com/numpy/numpy/blob/v2.3.5/numpy/polynomial/legendre.py
- [S] Pinned C15 owner and MassiveRadialGrid paths, function-level source map,
  original model contracts and newer-family exclusions are in the intake files.

SciSpace supplied bibliographic discovery, Exa supplied primary author pages,
the primary PDFs and GCC documentation were opened directly, and Wolfram
performed the stated algebra. No abstract's historical speedup number is
transferred to this code. The eventual strongest admissible claim is same-
quadrature local numerical equivalence with tested warm integration, subject
to the actual StageB/C evidence. Full EoR, non-LRS, fullQ^a, convergence and a
measured NCP speedup remain open.
