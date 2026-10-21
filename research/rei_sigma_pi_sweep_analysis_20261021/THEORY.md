# ACCEL03 constructive theory notes

## Scope and physical units
The massive component is the unchanged collisionless Vlasov distribution in the C15 owner. Use metric(-,+,+,+), no tilt, LRS axes with sigma=diag(-s,-s,2s). The distribution weights W are constant along the owner comoving momentum labels. With physical momentum p and particle mass m, E_phys=sqrt(m^2 c^4+c^2 p^2), beta^2=c^2 p^2/E_phys^2. Dividing E_phys and c p by the fixed initial k_B T reference gives the E and momentum used below; constants are retained in that mapping and in the owner's conversion from J moments to pressure. No new natural-unit convention is introduced.

x=ln(a/a0), r=exp(-x), u=mu^2,
R2=exp(2b)(1-u)+exp(-4b)u,
t=exp(-4b)u/R2, h=(3t-1)/2,
pbar2=r^2 qbar^2 R2,
E=sqrt(mbar^2+pbar2), w=pbar2/E^2.

The stress moment is J2=r^3 sum W E w h; define J4=r^3 sum W E w^2 h.

## Exact x response of the finite quadrature
At fixed b and fixed W:
d_x pbar2=-2pbar2, d_x E=-E w, d_x(Ew)=(-2+w)Ew, d_x h=0.
Therefore d_x(r^3 Ew h)=r^3 Ew h(-5+w), and
d_x J2=-5J2+J4.
This equality holds for the finite weighted sum itself; no angular or radial limit is exchanged.

## Exact b response and sign
d_b log R2=2(1-3t)=-4h.
Thus d_b log(Ew)=2(1-3t)-w(1-3t)=-2(2-w)h.
Also d_b t=-6t(1-t), hence d_b h=-9t(1-t).
The product rule gives
d_b J2=-r^3 sum W Ew[2(2-w)h^2+9t(1-t)]=-G.
For physical mass shell w in[0,1], t in[0,1] and W>=0, every summand in G is nonnegative. With xdot=H and bdot=s,
dot J2=H(-5J2+J4)-sG.
The fixed owner pressure conversion multiplies this expression by the same constant, so dimensions and work signs are preserved.

Wolfram independently simplified both per-node residuals to0 and found no point with negative bracket on the square0<=w,t<=1. The recorded CAS input/output is evidence/WOLFRAM_RESPONSE.json.

## Isotropic geometry and cancellation release
At b=0 and a separable initial1+alpha_m P2(mu) distribution,
integral_-1^1 (1+alpha_m P2)P2 dmu=2alpha_m/5.
The original Gauss-Legendre angular rule integrates these low-degree polynomials exactly in exact arithmetic. For nonzero alpha_m, the J4/J2 ratio is the radial Ew-weighted average of w and is in[0,1].
The massless limit gives J4=J2 and d_xJ2=-4J2. In the nonrelativistic leading expansion w<<1, J4 is higher order and d_xJ2=-5J2+O(wJ2).

A conditional illustrative comparison, at zero initial shear and for a collisionless massless comparison component with D_r=-D_m, gives
d_x(D_m+D_r)=-D_m+D4=(eta-1)D_m,
where eta=D4/D_m in[0,1]. This identifies a redshift mechanism for cancellation release.
The actual C15 radiation component contains gamma+nu+UV with its recorded collision/emission evolution. Its full cancellation slope must be measured from that complete owner or derived with those terms; the collisionless illustration is not substituted for it. The finite-sum massive identity above remains exact for the owner massive component.

## Stable observable diagnostics
For signed components p and r define A=abs(p)+abs(r).
When A>0 the residual fraction q=abs(p+r)/A lies in[0,1]. For perturbations obeying abs(delta p)<=eps abs(p), abs(delta r)<=eps abs(r), triangle inequality yields abs(delta(p+r))<=eps A. A nonzero total has relative condition A/abs(p+r)=1/q. This is a conditioning statement, not a measured error estimate for the solver. Exact cancellation yields a divergent condition; zero component scale leaves q undefined. New JSON fields use explicit statuses and nulls for undefined/divergent values, preserving the owner's original quantities.

With pi_A=diag(-D_A/3,-D_A/3,2D_A/3), half-contraction norms are abs(D_A)/sqrt(3), sqrt(3)abs(s), and sigma_ab*pi_A^ab=2sD_A. The common factor kappa_t/(sqrt(3)H^2) is applied after signed addition. Absolute residual checks use component scales near cancellation.

A control-subtracted shear response compares runs with the same requested initial shear, physical context, time interval, step count and source/backend/toolchain cohort; zero requested component stresses define the control. This is a contrast of two saved solutions. It does not identify a causal derivative or permit borrowing a different numerical cohort. Missing controls remain undefined; final-minus-initial change is a separate observable.

## Literature and implementation connection
Lesgourgues and Tram, CLASS IV, arXiv:1104.2935, Secs2.1 and3.3–3.4, use momentum-weighted pressure/shear and higher velocity weights for massive species. These motivate checking the extra velocity-weighted stress directly. Their perturbation fluid closure is not used here: the identities above follow from the existing homogeneous finite quadrature.
Original primary source: https://arxiv.org/pdf/1104.2935.
NumPy masked ufunc division and Matplotlib exact-point scatter APIs are reused for the saved-result diagnostics, with initialized masked outputs and explicit unavailable statuses.
The exact formulas are implemented by moment_response.py; portable aggregation and plot value provenance are specified by FROZEN_CONTRACT.md.
