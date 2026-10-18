# S1 | BASS source-age photon stress (non-tilted LRS Bianchi I)

**Parent scientific source:** BASS PR169 `6fb32b51390e4f722692505bf7a3ace2448aada6`; original FD96 Killing-momentum mechanism remains unchanged. These are separate **massless collisionless source-born photons**, not an additional FD96 massive component nor the original REI photo-reaction calculation. Signature `(-,+,+,+)` and proper time `t`, with `x=ln(a/a_ref)` (a_ref=1/21), metric `ds²=-c²dt²+a²[e^{-2b}(dx²+dy²)+e^{4b}dz²]`, signed shear `s=dot b=H db/dx`, public `Sigma=sqrt(3)|s|/H`. `Ppar-Pperp=Delta`, `pi=diag(-Delta/3,-Delta/3,2Delta/3)`.

## Exact Killing characteristic of a born-isotropic photon cohort

For emission at `u<=x`, let `d=b(x)-b(u)` and birth inclination `mu in [-1,1]`, distributed isotropically in **birth-local** orthonormal momentum coordinates. Along a collisionless characteristic the covariant components of momenta are conserved, and

```
R(mu,d) = sqrt[(1-mu²)e^(2d) + mu²e^(-4d)]
E(x;u)/E_birth = exp[-(x-u)] R
mu_local(x;u) = mu exp(-2d)/R.
```

If a homogeneous isotropic cohort has physical bolometric energy density `rho_birth` at its birth time, the subsequent physical bolometric moments are

```
rho_cohort(x;u)=rho_birth exp[-4(x-u)] F(d)
Delta_cohort(x;u)=rho_birth exp[-4(x-u)] D(d)
F(d)=1/2 integral_{-1}^1 R(mu,d) dmu
D(d)=1/2 integral_{-1}^1 [mu²e^(-4d) -(1-mu²)e^(2d)/2]/R(mu,d) dmu.
```

No separate angular Jacobian is multiplied in this birth-coordinate integral, since the invariant phase-space number Jacobian was used to obtain `exp[-3(x-u)]` and the angular integration is done at the birth epoch. Equivalently `D(d)=<R P2(mu_local)>`.

For any finite real `d`, with `X=e^(2d)(1-mu²)` and `Z=e^(-4d)mu²`,

```
F'(d)=-2 D(d)
R''(d)=[X²+14XZ+4Z²]/R³ >0 almost everywhere,
F''(d)>0, F(0)=1, F'(0)=D(0)=0.
```

**Consequences:** `F(d)>=1` and `sign D(d)=-sign d` for `d!=0`. For every born-isotropic positive population, shear deformation raises its instantaneous photon energy density compared to a hypothetical exactly isotropic fixed-birth-history redshift, and its quadrupole pressure difference opposes the *net deformation since birth*, not necessarily the instantaneous shear rate (when b oscillates). Do not interpret this as a new universal kinetic no-go or an opacity-containing REI theorem.

Wolfram exact expansion around d=0:

```
F(d)=1+(8/5)d²-(16/21)d³+O(d⁴)
D(d)=-(8/5)d+(8/7)d²+O(d³).
```

## Arbitrary source-age injection and exact covariant energy ledger

Let `S(x)>=0` be externally supplied **physical isotropic bolometric energy injected per unit physical volume per unit log scale x**, with units identical to rho. A proper-time emissivity is converted by `S=j_proper/H`, not treated as one fixed-time burst. This source is *specified* and independent of directional photon phase space and b in this construction. Let `rho_old>=0` be the old photons at x=0, isotropic at `b0=b(0)`; then

```
rho(x)=rho_old e^-4x F[b(x)-b0]
      +integral_0^x du S(u)e^-4(x-u)F[b(x)-b(u)]
Delta(x)=rho_old e^-4x D[b(x)-b0]
        +integral_0^x du S(u)e^-4(x-u)D[b(x)-b(u)].
```

Differentiation of the lower-limit boundary (where F(0)=1, D(0)=0) gives the **exact** continuity/energy-work identity

```
drhodx=-4rho+S-2 b'(x)Delta,
      =-3(rho+pbar)-sigma_ab pi^ab/H+S,
pbar=rho/3,   sigma_ab pi^ab=2s Delta.
```

`S` belongs to the *external emitter* and needs an opposite emission ledger; this isolated module does not supply the stellar/gas reaction or momentum Q^a. Thomson, anisotropic absorption, Verner thresholds, reionization chemistry and polarization are NOT implemented.

## Linear nonlocal memory, exact two-state moment compression

When `epsilon=max_{0<=u<=x}|b(x)-b(u)|` is small, define the reference isotropic energy and the first birth-deformation moment

```
U=rho_old e^-4x + integral_0^x S(u)e^-4(x-u)du
M=rho_old b0 e^-4x + integral_0^x S(u)e^-4(x-u)b(u)du.
```

These obey **local**, non-stiff first-order equations

```
U'=-4U+S,     M'=-4M+S b,
U(0)=rho_old, M(0)=rho_old b0.
```

The *nonlocal* linear pressure is recovered from only U,M and instantaneous b:

```
Delta^(1)(x)=-(8/5)[U(x)b(x)-M(x)],
      =-(8/5){rho_old e^-4x[b(x)-b0]
        +integral S(u)e^-4(x-u)[b(x)-b(u)]du}.
```

`rho=U+O(epsilon²)` and `Delta=Delta^(1)+O(epsilon²)` at finite bounded x. If b(x) is nondecreasing from b0 and S>=0, Delta<=0 and the kinetic photons act as a retarded viscous-type **shear damping source**. If b changes sign or turns, no general instantaneous sign follows. `rho>=U` holds exactly.

The unweighted cohort moments are a **linearized source-age closure**, not an exact reduction of the nonlinear angular f(mu) or arbitrary angle-dependent/multifrequency opacity. It should only be passed to REI as a **read-only diagnostic** until the transport-source/energy-owner and any double-counted background Omega_r are resolved.

## Literature anchor, distinct from new code/originality claims

- Fleury, Pitrou & Uzan, *Light propagation in a homogeneous and anisotropic universe*, Phys. Rev. D **91**, 043511 (2015), DOI 10.1103/PhysRevD.91.043511: conserved Bianchi-I photon momenta, exact redshift and directional drift.
- Heinzle & Uggla, *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations*, CQG **23**, 3463 (2006), DOI 10.1088/0264-9381/23/10/016: original collisionless Bianchi source dynamics.
- BASS PR169 original linear massive FD96 response and REI PR159/167 source age native work are explicitly separate. No claim that above general kinetic identities are literature-new.

## S1 verification and next task

Wolfram exact checks: `R'+2 L=0`, `D(0)=0`, `D'(0)=-8/5`, `R''-(X²+14XZ+4Z²)/R³=0`, `F` series first three coefficients `{0,8/5,-16/21}`. Next build cancellation-resistant quadrature, independent memory-state ODE reference, deterministic tests and only then evaluate on original BASS PR169 history.
