# G1B: continuous spectra, controlled tails and exact massless radial separation

## Source identity and physical units

Use the unchanged G1A normal tetrad, signature (-,+,+,+), epsilon_123=+1,
kappa=8 pi G/c^4, tau=ct/L_*, k=p_phys/P_* and m=m_phys c/P_*.
With P_*=k_B T_ref/c, q is the initial momentum magnitude cp/(k_B T_ref).
The source occupation is F_F(q)=1/(exp(q)+1), or F_B(q)=1/(exp(q)-1).
The massive FD distribution is momentum-decoupled; it is not an equilibrium
Fermi gas with exp(sqrt(q^2+m^2)-mu/T). No chemical potential is introduced.
Planck refers to massless unpolarized occupation, with a separately specified
amplitude; it supplies no polarization, Thomson or spectral collision closure.

For a quantum occupation with spin multiplicity g and occupation amplitude eta (not thermodynamic fugacity),
the physical number measure is g eta P_*^3/(2 pi hbar)^3 F(q) q^2 dq dOmega.
The G1A dimensionless weight multiplies this by kappa L_*^2 c P_*.
Our convenient initial energy amplitude A_rho writes the same measure as
A_rho F(q) q^2 g_ang(n) dq dOmega/(4 pi Z_m), with
Z_m=integral_0^infty q^2 sqrt(m^2+q^2) F(q)dq and <g_ang>=1.
Thus A_rho=4 pi kappa L_*^2 c g eta P_*^4 Z_m/(2 pi hbar)^3.
Changing A_rho at fixed T_ref generally changes eta; arbitrary amplitude and a
literal equilibrium blackbody at fixed T_ref are not independent physical inputs.
Here amplitudes define a normalized kinetic benchmark, not a fitted CMB cosmology.

Z_m is fixed once for all numerical grids. NORMALIZERS.json uses 65-digit mpmath
integrals for m=3,30 and exact zeta identities for massless cases. The tests compare
these constants to a separate SciPy infinite-domain scalar integration. No rule
is rescaled to force rho=1. Positive quadrature approximates the same continuous
initial distribution at every resolution.

The parent's 1/(exp(min(q,700))+1) is retained byte-exact as a finite-node source.
As an extension to all q it tends to a nonzero constant, so its continuum number
and energy integrals diverge. This does not invalidate its finite quadrature.
The new continuous source is evaluated with exp(-q)/(1+exp(-q)) or
exp(-q)/[-expm1(-q)]. Underflow at extreme q is a representation fact, not a
new physical floor. Admitted finite nodes lie below Q=48; their weights are positive.
At q=0 the Planck occupation diverges, but q^2 F_B(q) tends to zero and is continued
by that value. No infrared cutoff is needed for the moments computed here.

## Radial moments and omitted initial tails

Let I_p=integral q^p F(q)dq. At zero chemical potential,
I_p^B=Gamma(p+1) zeta(p+1) for p>0,
I_p^F=(1-2^(-p)) Gamma(p+1) zeta(p+1) for p>0.
In particular I2_B=2 zeta(3), I3_B=pi^4/15, I2_F=3 zeta(3)/2,
I3_F=7 pi^4/120. These definitions include the Gamma factor, unlike normalized
Fermi-integral conventions. Primary mathematical reference: NIST DLMF 25.12.11,
25.12.14-16, https://dlmf.nist.gov/25.12 .

For q>=Q>0, F_F(q)<=exp(-q), F_B(q)<=exp(-q)/(1-exp(-Q)). Therefore
B_p^F(Q)=Gamma(p+1,Q), B_p^B(Q)=Gamma(p+1,Q)/(1-exp(-Q)) bound the omitted
radial moment. For integer p, Gamma(p+1,Q)=p! exp(-Q) sum_{j=0}^p Q^j/j!.
For p=2,3 the polynomials are Q^2+2Q+2 and Q^3+3Q^2+6Q+6.

On a COMMON prescribed geometry suppose |k(t;q,n)|<=K q and
w(t)/w(0)<=J. Since sqrt(m^2+|k|^2)<=m+Kq and g_ang is positive with mean one,

  delta rho <= A_rho J [m B_2(Q)+K B_3(Q)]/Z_m
            <= A_rho J [m B_2(Q)+K B_3(Q)]/max(m I2,I3).

Also |delta flux|_2<=delta rho, ||delta P||_F<=delta rho and
||delta pi||_F<=sqrt(2/3) delta rho. These inequalities follow by positivity and
the rank-one pressure/STF norm. No cancellation is used to shrink their bounds.

The characteristic's curvature and rotation terms are perpendicular to k, so
(d/dtau)log|k|=-h-nhat.sigma.nhat, and logweight'=-3h+2a.k/E.
In |h|<=2, ||sigma||2<=1, |a|<=.5 on [0,.8], K<=exp(3tau),J<=exp(7tau).
This is a conditional analytic source-tail bound. Guard checks at evaluated states
are not an interval proof of that continuous envelope. More importantly it is NOT
an error bound between two self-consistently coupled spacetime solutions: their
fields differ, so a stability/Gronwall or validated evolution argument is still
needed to promote this to a nonlinear history bound. Time/grid comparisons below
provide separate finite numerical evidence. Binary64 evaluations of the analytic
bounds are not outward-rounded interval certificates.

## Exact radial reduction for collisionless massless transport

For m=0, write the G1A force as V(k). It obeys V(q v)=q V(v), while the logweight
rate obeys D(q v)=D(v), for q>0. The spatial-curvature numerator has degree two and
the mass-shell denominator has degree one; expansion/shear/rotation terms have
degree one. This is valid for the general Bianchi geometry in the stated frame,
not only Bianchi I. The new Wolfram symbolic checks returned {{0,0,0},0}.

With separable initial F(q) g_ang(n), k(t;q,n)=q v(t,n) and the density Jacobian
J(t,n) is independent of q. Let C(n)=A_rho g_ang(n)/(4 pi Z_0). Then per dOmega,

  N^0=C J I2,    N^a=C J I2 v^a/|v|,
  T^00=C J I3 |v|, T^0a=C J I3 v^a,
  T^ab=C J I3 v^a v^b/|v|.

The representative qbar=I3/I2, kbar=qbar v, wbar=C J I2 exactly reproduces all of
these number-current and stress-energy components at every time. Both weights
and momenta retain their G1A conventions. The same proof applies after a local
Lorentz boost because it is homogeneous in a massless four-momentum. That boost
is not by itself a globally tilted Einstein solution.

The next spectral moment, however, uses I4 rather than I3^2/I2. By Cauchy-Schwarz
I3^2<=I2 I4, strictly for these non-monochromatic spectra. Thus a number-and-energy
matched representative still loses higher spectral information. It cannot be fed
to energy-dependent absorption, recoil, emission or collisions as an exact source.
This reduction only removes radial nodes from the present collisionless N^a/T^ab
problem. It does not remove angular resolution or certify a continuum limit.

## Numerical comparisons and initial constraints

Positive composite Gauss-Legendre radial integration uses [0,4,12,24,48]; positive
GL(mu) times periodic midpoint(phi) samples the full sphere. The initial angular
FD factor is 1+n^T A n with symmetric tracefree A and 1+lambda_min(A)>0. It is a
specified decoupled angular perturbation, not a thermodynamic temperature tensor.
Planck starts isotropic; its later anisotropic stress is derived from transport.

Frozen-state radial comparisons fix angular resolution, and angular comparisons
fix radial resolution. The reference is another high-resolution discrete rule,
not an exact value except for the independent MP55 LRS Planck oracle. T^ab errors
are scaled by the reference energy density; number-current errors by reference
number density. This avoids division by a small/cancelling STF component.

New Class-B V and Class-A VIII IVPs use full non-diagonal tensors and separate
massive and Planck sectors. Initial shear and structure tensors commute, and V
has sigma*a=0, giving zero total Codazzi flux initially. The positive distribution
is antipodally even at the initial epoch, but its off-diagonal angular shape is
not invariant under every individual coordinate reflection. Each grid constructs h0 from its own
quadrature density; the resulting h0 error is part of the continuum-discretization
error, not removed by fitting a density normalization. Core rho/flux evolve
independently, and both their mismatch with kinetic moments and the constraints
recomputed from those moments are retained. Initial constraints do not replace
subsequent kinetic consistency checks.

Primary physical context (not a convergence certificate for this implementation):
Nungesser et al., arXiv:1305.7347; Okabe et al., arXiv:1106.4807;
Lee, Nungesser and Tod, arXiv:1911.04937. Discovery metadata in SciSpace has some
indexing years different from original arXiv dates; arXiv identities govern.
