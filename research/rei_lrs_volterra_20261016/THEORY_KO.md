# BASS LRS FD96: retarded anisotropic-stress response to initial kinetic quadrupole

2026-10-16 KST. Parent BASS PR168 `03a01d21ed21e7d32737ca5e5f6d889a7203aa70`, original FD96 `bianchi/matter/freestream.py` git blob `8467932c3281f9d426712b3a582f2aae3a484692`. Science lane: source-only non-tilted LRS Bianchi I, collisionless massive Fermi–Dirac q96 canonical momenta and positive initial angular W=1+A P2(mu). The actual REI H/He, photons, nu, electron tilt, anisotropic gamma/nu radiation response and stellar Q^a are NOT implemented by this derivation. Sigma=sqrt(3)|s|/H; s=dot b retains sign.

## Exact moments and linearization

Use x=ln(a/a_ref), r=e^-x, a=a_ref r^-1, m/T_ref≥3, E0=sqrt(m²+r²q²), k=r²q², N=∫dq rw(q)sqrt(m²+q²). Radial rw=q² f_FD(q) dq is exactly the BASS FD96 q96 quadrature. Angular ∫dmu/2, P2=(3mu²-1)/2.

E(b)=sqrt(m²+k[(1-mu²)e^(2b)+mu²e^(-4b)]), W(mu)=1+A P2(mu)≥0.
ρ_m(x,b,A)=r³/N ∫rw∫W E(b); ΔP=P_parallel-P_perp=−(1/2)∂_b ρ_m.
At b=A=0, ρ_A=0, ρ_b=0; with pbar0=r³/(3N)∫rw k/E0,

  α(x)=∂_A ΔP|0=r³/(5N)∫rw k/E0=(3/5)pbar0,
  κ(x)=−∂_b ΔP|0=r³/N ∫rw (2k/E0−2k²/(5E0³))>0.

Exact linear constitutive relation: ΔP=α(x) A−κ(x)b+O(A²,Ab,b²). In fact at b=0 ΔP=α A exactly for all allowed A because W is linear in A. Let R=∫rw(k/E0)(k/E0²)/∫rw(k/E0). For finite mass 0<R<1, so κ=2I(1−R/5)r³/N, and 1/10< α/κ=1/(10−2R)<1/8. This bound and isotropic slope also appear in earlier PR167: they are **reused constraints, not newly claimed results**.

## New linear response and Volterra kernel

Let f_m be the original nonbaryonic massive-matter fraction, C_m=Omega_m*f_m/a_ref³; K=H0² C_m; H_bar(x)²=H0²[Omega_m(1-f_m)/a³+Omega_r/a⁴+Omega_Lambda + C_m ρ_m(x,0,0)]. H_ref=H_FLRW(a_ref). At b=s=A=0, partial_b H=partial_A H=partial_s H=0, hence the exact first variational equation of the BASS source-only Einstein dynamics (with s=H_ref v):

  db_A/dx=s_A/H_bar(x),
  ds_A/dx=−3s_A + (K/H_bar(x))[α(x)−κ(x)b_A(x)].

This gives for small A, b(x,A)=A b_A(x)+O(A²), s(x,A)=A s_A(x)+O(A²) for initial b0=s0=0. Equivalently:

  b_A''+[3+H_bar'/H_bar]b_A'+[K κ/H_bar²]b_A=K α/H_bar²,
  b_A(0)=b_A'(0)=0.

Retarded, causal Volterra representation:

 b_A(x)=g(x)−(T b_A)(x),
 g(x)=∫_0^x G(x,u)α(u)du,
 (Tf)(x)=∫_0^x G(x,u)κ(u)f(u)du,
 G(x,u)=K e^(3u)/H_bar(u) ∫_u^x e^(−3v)/H_bar(v) dv ≥0.

Differentiating w.r.t. x twice recovers the ODE, with G(u,u)=0 and ∂_xG(u,u)=K/H_bar(u)². All causal/frozen-source (linearized) assumptions are explicit. T is a Volterra operator with continuous bounded kernel on finite x∈[0,ln(21/5)]. If M=sup_{0≤u≤x≤X}G(x,u)κ(u), then ||T^n||∞≤(MX)^n/n!, so the Neumann series ∑_{n≥0}(−T)^n g converges independently of contraction q. A finite-n remainder bound is ||g||∞ Σ_{n>N}(MX)^n/n!. It is conservative; numeric discretization incurs an independent integration error. No full non-linear global stability theorem follows from this linear Volterra construction.

A physically interpretable frozen-reference diagnostic is g(x) (A quadrupole stress without shear feedback), versus the actual b_A(x). Since κ>0, the linearized shear source is restoring; the integral response itself is not the instantaneous neutral-anisotropy b_*(x,A) and is not a closure to set s=0.

## Independent mathematical checks

Wolfram symbolic angular μ measure gives four zero residuals for α=k/(5E0), κ=2k/E0−2k²/(5E0³), α−3pbar/5, α/κ−1/(10−2 k/E0²). A diagnostic deliberately integrating uniformly over z=μ² instead of μ produces incorrect nonzero residuals; that wrong measure was rejected and retained in this note rather than certified. For H=H_c exp(−p x), p∈(0,3), the closed-form G=K e^((3+p)u)/H_c²*[exp((p−3)x)−exp((p−3)u)]/(p−3); Wolfram ODE, diagonal and initial derivative identities return {0,0,0}.

## Research relation and boundaries

Heinzle & Uggla, *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations* (2006), CQG 23 3463, is primary context for collisionless anisotropic stresses (non-LRS global dynamics). Lee, Nungesser & Tod, *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology* (arXiv:1911.04937) establishes a related massless asymptotic setting, not this response kernel. No publication novelty or nonperturbative stability theorem asserted.

Next: build two independent numerical realizations (retarded Volterra product integration and exact tangent ODE), compare against original nonlinear BASS PR164/167 at finite A; quantify quadratic truncation and code convergence. Native REI dynamic matter callback not yet admitted.
