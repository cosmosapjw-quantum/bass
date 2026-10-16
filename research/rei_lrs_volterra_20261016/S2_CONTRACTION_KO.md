# S2: analytic contraction of the BASS LRS retarded kinetic response

The theory and code in `THEORY_KO.md` and `lrs_retarded.py` concern only the exact first variation at initial A=b=s=0, holding the original nonkinetic cosmic radiation isotropic and setting massive collisionless matter `f_m` from nonbaryonic Omega_m. Parent identities are BASS PR164/167/168. This is not a novel collision operator.

## A source-independent positive upper bound

Set a=a_ref exp(x), `H_d²=H0² Ω_m (1−f_m)/a_ref³`, `K=H0² Ω_m f_m/a_ref³`, `q_0` the conserved radial q. At isotropy, k(x)=q_0²exp(−2x) and E(x)=sqrt(m²+k(x)). The positive momentum integrand for κ is

`F(k)=2k/E * [1−k/(5E²)]`;  κ(x)=[exp(−3x)/N] ∫rw F(k(x)).

For x>=0: E(x)>=exp(−x) E(0), and (1−k(x)/(5E(x)²)) / (1−k(0)/(5E(0)²)) <= 5/4. Hence F(k(x))<= (5/4)exp(−x)F(k(0)), and **κ(x)<= (5/4)κ(0)exp(−4x)**. No source fit to H/He photons enters this inequality.

The true isotropic source-conserving background has H(x)>=H_d exp(−3x/2), because dust, radiation, cosmological constant and kinetic density terms are each nonnegative. Thus the retarded Green function obeys

`G(x,u) <= [2K/(3H_d²)] exp(3u)[1−exp(−3(x−u)/2)]`, 0<=u<=x.

Consequently the positive integral Volterra feedback operator T has rigorous sup-norm bound

`||T||∞ <= q(X)=[5/6][f_m/(1−f_m)] κ(0) [1−exp(−X)]` for 0<=x<=X.

This bound discards the positive [1−exp(−3(x−u)/2)] factor, so it is deliberately conservative. In the BASS/REI studied case f_m=.1 and X=ln(21/5), exact FD96 radial q96 source quadrature gives:

| m/T_ref | κ(0) | proven q(X) |
|---:|---:|---:|
| 3 | 0.9177269078226861 | 0.06474263899983676 |
| 30 | 0.027907886116247387 | 0.001968810308024507 |
| 300 | 0.00028745348769992847 | 0.00002027890565784328 |

Since q<1, Picard iterates B_(n+1)=g−T B_n converge, and for their **exact continuous operator**, the a posteriori remainder is `||B−B_n||∞ <= q/(1−q) ||B_n−B_(n−1)||∞`. The discrete Simpson product integration has an *additional* quadrature error that is not covered by this bound. General f_m near the full available nonbaryonic budget need not satisfy q<1: do not extend this contraction theorem to all allowed f_m, and never use it as a nonlinear/shear stability theorem.

## Constructive numerical representation

The causal Volterra integrals are evaluated as two cumulative Simpson quadratures, O(N) per iteration. A completely independent DOP853 integration solves the linear signed-shear system. Parent BASS PR164's nonlinear Einstein solution and its existing tangent variables provide a third physically distinct comparison. The Volterra operator's positive-memory structure preserves the sign of gravitational forcing at each source evaluation; however exact positivity of the *backreacted solution* for every source/domain is not inferred from a positive first kernel without an additional argument.

## Stage S2 execution

`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m unittest -v test_retarded` -> **15 PASS, exit 0**, real 0.341 s. Original source norms (m=3,30,300), PR167 α/κ derivatives, parent PR164 mass-energy H(a), μ angular measure, Volterra causality, Green power law, global κ bound, product Simpson convergence, actual parent variational endpoint and quadratic nonlinear remainder all checked. Original parent tests and new native Rust were not rerun in this stage. Exact expression-derived Wolfram S1 checks remain separately pinned.
