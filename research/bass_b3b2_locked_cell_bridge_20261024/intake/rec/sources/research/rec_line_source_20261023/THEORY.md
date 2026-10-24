# LINE01 constructive derivation: a source-owned line and exact local thick step

Date: 2026-10-23. Role: R4/R5 construction, not the fresh independent review.
Inherited angular implementation: ANGULAR01, REC PR127,
5185c396b7e07076565ca2f5044a5ccd193e6ee1.
Source ownership and tabulated constants are recorded separately in
[LINE_SOURCES.json](provenance/LINE_SOURCES.json) and [SOURCE_SYNTHESIS_KO.md](provenance/SOURCE_SYNTHESIS_KO.md).

**Selected model.** One unpolarized, isolated, two-level component with a supplied,
isotropic blue-boundary photon occupation and quasi-stationary Sobolev transfer.
The exact finite-opacity angular source is the reference operator. Its uniformly
thick reduction admits an exact, conservative local population step with a
finite-opacity trajectory bracket. The step freezes its background and excludes
cosmological dilution during this source substep.

The final parent selection is the source-qualified effective coincident-line
collapsed 2p card (g=3) in FROZEN_CONTRACT.md and
[COLLAPSED_SOURCE_ADDENDUM.md](provenance/COLLAPSED_SOURCE_ADDENDUM.md).
The initial source recommendation was a separate NIST J=1/2 component; its card
and the J=3/2 card remain explicit finite validation fixtures. The effective
aggregate imposes statistical 1:2 sublevel populations and a common frequency,
profile and incident occupation. All derivations below hold for general g>0.
This does not establish equivalence with actual overlapping doublet transfer.
Tabulated atomic-data precision, the effective line assumption and numerical
escape tolerances are separate error sources. The symbol κ in this theory
means F=1+(g+1)f_plus in FROZEN_CONTRACT.md; the latter's frequency scale is
8πH/(Nλ³). No physical definition differs between the two notations.

## 1. Candidate choice and typed domain

Two actual physical closures were considered.

| Candidate | What it closes | Decision |
|---|---|---|
| Quasi-stationary isolated two-level Sobolev component | Profile-averaged occupation and an effective escaping exchange from declared populations and incident occupation | Selected, with exact finite-opacity \(B,Q\) as reference and a gated thick reduction |
| Time-dependent, overlapping, multilevel polarized line transport | Stored line radiation, feedback, redistribution, component overlap and radiation evolution | Deferred until the corresponding population, spectral and collision owners are supplied |

The thick expression and frozen-\(B\) step below are reductions/integrators of
the first model; they are not additional physical closures.

Use proper time \(t_{\rm p}\) in seconds and a matter-comoving orthonormal frame.
The physical densities \(n_l,n_u\) have units \({\rm m}^{-3}\) and count all
magnetic substates of their specified levels. Define
\[
g=\frac{g_u}{g_l}>0,\qquad
\Delta=g n_l-n_u>0,\qquad
N=n_l+n_u>0,
\]
\[
\nu_\ell=\frac{c}{\lambda},\qquad
\epsilon_\ell=h\nu_\ell=\frac{2\pi\hbar c}{\lambda},\qquad
C_S=\frac{A\lambda^3\Delta}{8\pi}
=\frac{A c^3\Delta}{8\pi\nu_\ell^3}.
\]
Here \(A,C_S,H,\sigma_{ij}\) have units \({\rm s}^{-1}\). Define the real symmetric,
tracefree tensor \(S_{ij}=\sigma_{ij}/H\), with
\[
H>0,\qquad q(\boldsymbol n)=1+S_{ij}n_i n_j>0,\qquad
\tau_0=\frac{C_S}{H},\qquad \tau_{\boldsymbol n}=\frac{\tau_0}{q(\boldsymbol n)}.
\]
Thus \(q_{\min}=1+\lambda_{\min}(S)>0\) and
\(q_{\max}=1+\lambda_{\max}(S)\). The inherited sign convention is
\(-d\ln\nu/dt_{\rm p}=Hq\) along a local geodesic ray. The formula does not assert
that a ray direction remains fixed over a finite cosmological trajectory.

Let \(f_+\ge0\) be the **isotropic blue-boundary** occupation per unpolarized photon
state. It is not automatically the Planck occupation and may require feedback
ownership. The occupation convention is
\[
I_\nu=\frac{2h\nu^3}{c^2}f_\nu.
\]
The factor two counts photon polarizations. Population inversion \(\Delta\le0\),
a contracting ray \(q\le0\), a direction-dependent incident spectrum and aligned
atomic populations are outside this selected operator.

The stimulated-emission-preserving isotropic formulas follow
[Hirata and Forbes, arXiv:0903.4925v2, §II.B, equations (1)–(3)](https://arxiv.org/pdf/0903.4925).
The occupation/profile conventions and limitations are discussed by
[Chluba and Sunyaev, arXiv:0810.1045, §3.2.2, equation (35b)](https://arxiv.org/pdf/0810.1045).
The angular substitution and tensor map below are direct derivations using
ANGULAR01, not quotations of a Bianchi result from those papers.

## 2. Eliminate the stationary line occupation before forming the source

The line source occupation is
\[
f_S=\frac{n_u}{\Delta}.
\]
At fixed source and a common emission/absorption profile, use a ray optical-depth
coordinate \(\xi\). The transfer solution across the resonance is
\[
f(\xi,\boldsymbol n)=f_S+(f_+-f_S)e^{-\xi},\qquad
f_{{\rm out},\boldsymbol n}
=f_+ e^{-\tau_{\boldsymbol n}}
+f_S(1-e^{-\tau_{\boldsymbol n}}).
\]
A profile average is the optical-depth average for this declared Sobolev model.
It gives
\[
\bar f_{\boldsymbol n}
=f_S+(f_+-f_S)\beta_{\boldsymbol n},\qquad
\beta_{\boldsymbol n}
=\frac{1-e^{-\tau_{\boldsymbol n}}}{\tau_{\boldsymbol n}}.
\]
With \(\langle F\rangle=(4\pi)^{-1}\int F\,d\Omega\), define
\[
B=\langle\beta_{\boldsymbol n}\rangle,\qquad
Q_{ij}=\left\langle(n_i n_j-\delta_{ij}/3)\beta_{\boldsymbol n}\right\rangle.
\]
Then \(\bar f=(1-B)f_S+Bf_+\). The local Einstein net downward rate is
\[
A\{n_u(1+\bar f)-g n_l\bar f\}
=A(n_u-\Delta\bar f).
\]
Substituting the stationary occupation gives the central factorization:
\[
\boxed{
D=n_u-\Delta f_+
=n_u(1+f_+)-g n_lf_+,\qquad
R=A B D.
}
\]
\(D\) has units \({\rm m}^{-3}\), and \(R\) has units
\({\rm m}^{-3}{\rm s}^{-1}\). \(R>0\) is net downward transition and net escaping
line-photon creation; \(R<0\) is the opposite exchange.

There is an independent phase-space normalization check. The unpolarized number
density per \(d\nu\,d\Omega\) is \(2\nu^2f/c^3\). The local redward frequency speed
is \(Hq\nu\). The downstream-minus-upstream photon crossing rate is consequently
\[
\frac{dR}{d\Omega}
=\frac{2Hq}{\lambda^3}(f_{{\rm out},\boldsymbol n}-f_+)
=\frac{2Hq}{\lambda^3}(f_S-f_+)(1-e^{-\tau_{\boldsymbol n}})
=\boxed{\frac{AD}{4\pi}\beta_{\boldsymbol n}}.
\]
This verifies the \(8\pi\) normalization without treating \(Q\) as an absolute
radiation density. It defines an effective escaping exchange after the
quasi-stationary resonance radiation has been eliminated.

A useful pair of nonnegative **effective reservoir channels** is
\[
R_\downarrow=AB\,n_u(1+f_+),\qquad
R_\uparrow=AB\,g n_lf_+,\qquad R=R_\downarrow-R_\uparrow.
\]
Their direction-resolved versions replace \(B\) by
\(\beta_{\boldsymbol n}/(4\pi)\). They are not the full microscopic counts of all
trapped absorptions and reemissions at the internal occupation \(\bar f\).

## 3. Detailed balance, photon/atomic ledger and tensor injection

For \(f_+>0\), since \(A,B>0\),
\[
R=0
\quad\Longleftrightarrow\quad
\frac{n_u}{g n_l}=\frac{f_+}{1+f_+}.
\]
If, additionally, a source owner prescribes a Planck blue-boundary field,
\[
f_+=\frac{1}{\operatorname{expm1}[\epsilon_\ell/(k_B T_b)]},
\]
then detailed balance is
\[
n_u=g n_l e^{-\epsilon_\ell/(k_B T_b)}.
\]
Use the same \(\epsilon_\ell=2\pi\hbar c/\lambda\) in both expressions. For
\(f_+=0\), equilibrium has \(n_u=0\). No local balance identity proves global LTE.

The source contributions at fixed local volume are
\[
(\dot n_u,\dot n_l,\dot n_\gamma)_\ell=(-R,+R,+R).
\]
Atom number is conserved. A bound-bound transition changes neither nuclear
identity nor ionic charge, and supplies no free-electron yield. Thus it does not
complete the requested larger ionic-yield closure.

Choose the lower-level internal energy as zero:
\(u_{\rm at,int}=\epsilon_\ell n_u\). The source energy ledger is
\[
\boxed{
(\dot u_{\rm at,int},\dot u_\gamma,\dot u_{\rm th})_\ell
=(-\epsilon_\ell R,+\epsilon_\ell R,0).
}
\]
The zero thermal term belongs to the declared narrow-line, recoil-free,
collision-free energy model. It is not permission to neglect the accumulated
effects of recoil or energy-changing redistribution in a full trapped-line
calculation. Per-scattering recoil smallness alone would not bound many
scatterings. Emission draws atomic excitation energy; adding the same emitted
energy as gas heating would double count.

Because \(\beta_{\boldsymbol n}\) is even in \(\boldsymbol n\), the dipole injection
vanishes. The photon number PSTF source is \(\mathcal J_{ij}=ADQ_{ij}\). The energy
pressure source and its tracefree part are
\[
\dot P_{\gamma,ij}|_\ell
=\epsilon_\ell AD(B\delta_{ij}/3+Q_{ij}),\qquad
\boxed{\mathcal S_{\pi,ij}
=\dot\pi_{\gamma,ij}|_\ell=\epsilon_\ell ADQ_{ij}}.
\]
Their units are \({\rm J\,m^{-3}\,s^{-1}}\). These are injection rates into the
effective escaping-radiation ledger, not a stored radiation stress, matter stress,
or the complete microscopic collision tensor of line photons. For negative \(D\)
the source removes a directional radiation contribution; a signed source need
not itself be positive semidefinite. Each gross channel separately has a
nonnegative angular measure.

If an external evolution uses physical densities,
\[
\dot n_u+3Hn_u=-R,\qquad
\dot n_l+3Hn_l=R.
\]
For an expanding comoving volume \(V\propto a^3\),
\(d(Vn_u)/dt_{\rm p}=-VR\). An actual homogeneous radiation energy evolution has
its own dilution and shear-work terms, e.g.
\[
\dot u_\gamma+4Hu_\gamma+\sigma_{ij}\pi_\gamma^{ij}
=\epsilon_\ell R
\]
when the geodesic homogeneous frame eliminates the other flux terms. This
equation is not solved here. Geometry, spectral transport and line-photon
storage are distinct owners. The fixed incident \(f_+\) is an imposed radiation
reservoir; a negative signed photon packet is not a guarantee that an arbitrary
finite closed photon bath remains nonnegative.

The quasi-stationary elimination requires the radiation profile to relax on a
shorter scale than changes in its backgrounds/populations. When that fails,
restore line-photon storage and frequency transport; one cannot repair it by
relabeling \(R\) as a complete thermal source.

## 4. Uniformly thick cancellation, bounds and signed limits

ANGULAR01 supplies
\[
B_0=\frac1{\tau_0},\qquad Q_{0,ij}=\frac{2S_{ij}}{15\tau_0},
\qquad r=\exp[-\tau_0/q_{\max}],
\]
\[
0\le B_0-B\le\frac r{\tau_0},\qquad
\|Q_0-Q\|_F\le\sqrt{\frac23}\frac r{\tau_0},\qquad
B\ge\frac{1-r}{\tau_0}.
\]
Substitution of the actual opacity coefficient therefore yields
\[
\boxed{R_0=\frac{8\pi H}{\lambda^3}(f_S-f_+)},\qquad
\boxed{\mathcal J_{0,ij}
=\frac{16\pi}{15\lambda^3}\sigma_{ij}(f_S-f_+)}.
\]
Multiply \(\mathcal J_0\) by \(\epsilon_\ell\) for the energy PSTF injection.
Einstein \(A\) cancels at fixed populations and fixed background in this
uniformly thick reduction. It still controls the optical-depth validity gate;
populations in a larger coupled network may also depend on \(A\).

For either sign of \(D\),
\[
|R_0-R|\le A|D|\frac r{\tau_0},\qquad
\|\mathcal J_0-\mathcal J\|_F
\le A|D|\sqrt{\frac23}\frac r{\tau_0}.
\]
For \(D\ne0\), division by \(|R|\) gives respective bounds
\(r/(1-r)\) and \(\sqrt{2/3}\,r/(1-r)\). At \(D=0\) every source vanishes;
the appropriate certificate is absolute zero, not a relative \(0/0\).

A requested scalar relative operator error \(\varepsilon>0\) is guaranteed by
\[
\frac{\tau_0}{q_{\max}}\ge
\log(1+\varepsilon^{-1}).
\]
For \(\varepsilon=10^{-8}\) this is \(18.420680753952364\). This analytic
truncation certificate does not certify source-data uncertainty, physical model
error, input conditioning or floating-point interval accuracy.

The inherited Jensen comparison \(B\le\beta(\tau_0)\) implies
\(|R|\le A|D|\beta(\tau_0)\). A signed inequality for \(R\) reverses when \(D<0\);
using its absolute value avoids the incorrect “suppression means smaller signed
number” inference.

As \(\tau_0\to0^+\), \(B\to1\) and \(Q\to0\), giving the ordinary optically thin
Einstein net exchange and isotropic source. As \(\Delta\to0^+\), \(f_S\) can
diverge while the undivided defect \(D\) remains finite. Calculate \(D\) without
dividing by \(\Delta\), and do not use the thick formula unless its actual gate
passes. The selected API rejects \(\Delta\le0\); a limiting formula is not a
population-inversion implementation.

## 5. A stable source variable and equilibrium conditioning

For \(x=n_u/N\), put
\[
b=g+1,\qquad \kappa=1+b f_+,\qquad
x_{\rm eq}=\frac{g f_+}{\kappa}.
\]
Then
\[
\boxed{D=N\kappa(x-x_{\rm eq})},\qquad
\Delta=N(g-bx),\qquad
0\le x<\frac gb,\qquad
g-bx_{\rm eq}=\frac g\kappa>0.
\]
The non-inverted domain is an invariant interval for both local models below.

Subtracting separately accumulated large gross rates near balance loses
relative accuracy of their small net. Prefer an input departure
\(y=x-x_{\rm eq}\) when it is owned by the source model, and calculate every
signed ledger from the same \(D\). For a strictly positive population and
\(f_+>0\), an alternative affinity is
\[
\alpha=\log\frac{n_u}{g n_l}+\log(1+1/f_+),\qquad
D=g n_l f_+\,\operatorname{expm1}(\alpha).
\]
For widely different channel magnitudes, use log-channel values
\[
L_P=\log n_u+\log(1+f_+),\qquad
L_M=\log g+\log n_l+\log f_+.
\]
If \(L_P\ge L_M\),
\(D=e^{L_P}[-\operatorname{expm1}(L_M-L_P)]\); otherwise use the analogous
negative expression with \(P,M\) exchanged. Explicit zero branches are required.
Neither log subtraction nor an algebraic reexpression can restore precision
already absent from the supplied populations. Near-equilibrium numerical
acceptance should use a gross activity scale, e.g.
\[
\mathcal A=AB[n_u(1+f_+)+g n_l f_+],
\]
together with an absolute floor, rather than a relative error divided by a nearly
zero \(R\).

## 6. Exact local thick population flow

Freeze \(N,H,S,f_+\), line constants and the source convention during a local
proper-time step. \(H\) remains the supplied frequency-drift coefficient, while
cosmological density dilution is intentionally absent from this source substep.
No new cosmological IVP is implied. The finite-opacity reference is
\[
\dot x=-A\kappa B(x)(x-x_{\rm eq}).
\]
Its thick reduction retains the population dependence of opacity:
\[
B_0(x)=\frac{8\pi H}{A\lambda^3N(g-bx)},\qquad
\dot x=-\frac{a(x-x_{\rm eq})}{g-bx},\qquad
a=\frac{8\pi H\kappa}{N\lambda^3}.
\]
Here \(a\) has units \({\rm s}^{-1}\); no \(A\) occurs in the reduced drift.
Set
\[
y=x-x_{\rm eq},\qquad d_0=\frac g\kappa>0.
\]
Then \(g-bx=d_0-by\), and
\[
\boxed{\dot y=-\frac{a y}{d_0-by}}.
\]
The drift has the opposite sign to \(y\). Its only equilibrium is \(y=0\);
its denominator stays positive throughout the interval from \(x_0\) to
\(x_{\rm eq}\). The solution is monotone and cannot cross equilibrium.

For \(y_0\ne0\), separate variables:
\[
\int_{y_0}^{y(t)}\left(\frac{d_0}{y}-b\right)dy=-a t,
\]
\[
\boxed{d_0\log\left|\frac{y(t)}{y_0}\right|-b[y(t)-y_0]=-a t}.
\]
Define \(z_0=-b y_0/d_0\) and \(\omega=a t/d_0\). Since
\(d_0-by_0>0\), \(z_0>-1\). The explicit solution is
\[
\boxed{
y(t)=-\frac{d_0}{b}W_0\!\left[z_0 e^{z_0-\omega}\right],\qquad
x(t)=x_{\rm eq}+y(t).
}
\]
For \(y_0=0\), return \(x(t)=x_{\rm eq}\) exactly.

**Branch proof.** If \(y_0>0\), then \(-1<z_0<0\) and
\(z_0e^{z_0-\omega}\in(-1/e,0)\). On the principal real branch,
\(W_0(z_0e^{z_0})=z_0\); increasing \(t\) moves the argument toward zero and
decreases \(y\) continuously to zero. If \(y_0<0\), then \(z_0>0\), so the
argument and \(W_0\) remain positive while \(y<0\) increases to zero.
No \(W_{-1}\) branch is needed. \(t=0\) returns the initial state. The
non-inverted domain and nonnegative level populations are preserved.

Near equilibrium \(\dot y=-(a/d_0)y+O(y^2)\): the small-departure decay rate is
\(8\pi H\kappa^2/(gN\lambda^3)\). For \(f_+=0\), \(x_{\rm eq}=0\) and only
downward relaxation is possible. When \(x_0\) approaches the inversion boundary
from below, the drift becomes large; this is a conditioning and physical-domain
warning, not a license to extend beyond positive opacity.

## 7. Stable scalar root equivalent to Lambert W

The closed form is useful for analysis. A monotone scalar root avoids overflow
from \(z_0e^{z_0-\omega}\) and computes small signed packets without subtracting
nearby endpoint populations.

For \(y_0\ne0\), introduce \(u=\log|y(t)/y_0|\le0\). The implicit equation is
\[
\boxed{F(u)=u+z_0\operatorname{expm1}(u)+\omega=0}.
\]
For every \(u\le0\),
\[
F'(u)=1+z_0e^u>0
\]
because \(z_0>-1\). A finite bracket is
\[
L=-\omega+\min(z_0,0),\qquad
U=\min\{0,-\omega+\max(z_0,0)\}.
\]
One has \(L\le U\le0\), \(F(L)\le0\le F(U)\). To see the endpoint signs:
for \(z_0<0\), \(F(L)=z_0e^L\le0\) and
\(F(U)=z_0\operatorname{expm1}(-\omega)\ge0\); for \(z_0\ge0\), the lower
sign follows from \(F(-\omega)=z_0\operatorname{expm1}(-\omega)\le0\), and the
upper endpoint is either zero with \(F(0)=\omega\ge0\), or
\(-\omega+z_0\) with \(F(U)=z_0e^U\ge0\).
Consequently a bounded monotone root solve has a unique physical solution.

Obtain the increment directly:
\[
\boxed{\delta x=y_0\operatorname{expm1}(u)},\qquad
x_1=x_0+\delta x,\qquad
\Delta n_\gamma=-N\delta x.
\]
Use exact branches for \(t=0\) and \(y_0=0\). This is an algebraic local update,
not an ODE integrator or a new cosmological trajectory. A numerical implementation
still needs finite iteration/tolerance limits and bounded finite inputs.
The exact formula does not supply a floating-point interval certificate.

For a direct Lambert implementation, the negative-\(z_0\) case can form the
argument from
\(-\exp[\log(-z_0)+z_0-\omega]\); its exponent is at most \(-1\), so overflow
is absent. For \(z_0>0\), one may instead solve
\(w+\log w=\log z_0+z_0-\omega\) on \(w>0\), or use a real Wright-omega
implementation. Near the branch point, the domain margin and endpoint rounding
need explicit handling. The monotone \(u\) representation keeps the same
physical branch without an exponential of a large positive argument.

## 8. Conservative integrated packet

The thick normalized angular shape is constant during this local step:
\[
K_{ij}\equiv\frac{Q_{0,ij}}{B_0}=\frac{2S_{ij}}{15}.
\]
Thus the exact integrated **thick-model** source packet is
\[
\boxed{
\Delta n_\gamma=N(x_0-x_1),\quad
\Delta u_\gamma=\epsilon_\ell\Delta n_\gamma,\quad
\Delta u_{\rm at,int}=-\epsilon_\ell\Delta n_\gamma,\quad
\Delta u_{\rm th}=0,
}
\]
\[
\boxed{
\Delta\pi_{\gamma,ij}
=\epsilon_\ell\Delta n_\gamma\,K_{ij},\qquad
\Delta P_{\gamma,ij}
=\epsilon_\ell\Delta n_\gamma(\delta_{ij}/3+K_{ij}).
}
\]
Take all changes from one common signed population increment. This is algebraic
conservation in the declared operator; summation roundoff remains a numerical
matter. The packet can be negative for absorption. It records the change from
the supplied incident radiation, not an independently nonnegative photon count.

The angular second moment \(\delta_{ij}/3+2S_{ij}/15\) is positive definite in
the allowed domain: each shear eigenvalue exceeds \(-1\), so each eigenvalue
of this shape exceeds \(1/5\). Equivalently it is the second moment of the
nonnegative thick angular measure \(q\,d\Omega/(4\pi)\).
This positivity belongs to a positive gross channel; multiplying by a negative
net packet reverses its sign.

## 9. Whole-path gate and finite-opacity trajectory certificate

An initial-state gate alone need not suffice when absorption increases \(x\)
and reduces \(\Delta\). Both finite-opacity and thick scalar flows stay between
their common initial state and \(x_{\rm eq}\). Their smallest path opacity is
therefore at
\[
x_{\max}=\max(x_0,x_{\rm eq}),\qquad
T_{\rm path}
=\frac{A\lambda^3N[g-bx_{\max}]}{8\pi Hq_{\max}}.
\]
Let
\[
\delta=e^{-T_{\rm path}},\qquad 0\le\delta<1.
\]
At every state on the path,
\[
\Theta(x)\equiv\frac{B(x)}{B_0(x)}
=1-\left\langle q e^{-\tau_0(x)/q}\right\rangle
\in[1-\delta,1].
\]
The finite-opacity drift is exactly the thick drift multiplied by
\(\Theta(x)>0\). Let \(\Phi_t(x_0)\) denote the exact thick solution and let
\(x_f(t)\) denote the finite-opacity reference with the same fixed background.

**Travel-time proof.** Along either monotone branch, take positive distance
along the motion. If \(T_0(x)\) and \(T_f(x)\) are the times to reach the same
intermediate state \(x\), then
\[
T_f(x)=\int_{x_0}^{x}\frac{dx'}{F_0(x')\Theta(x')},\qquad
T_0(x)=\int_{x_0}^{x}\frac{dx'}{F_0(x')},
\]
where the orientation makes both integrals nonnegative. The pointwise speed
bound gives
\[
T_0(x)\le T_f(x)\le\frac{T_0(x)}{1-\delta}.
\]
Invert these monotone travel-time maps. For downward relaxation,
\[
x_0>x_{\rm eq}:\qquad
\boxed{\Phi_t(x_0)\le x_f(t)\le\Phi_{(1-\delta)t}(x_0)}.
\]
For upward relaxation,
\[
x_0<x_{\rm eq}:\qquad
\boxed{\Phi_{(1-\delta)t}(x_0)\le x_f(t)\le\Phi_t(x_0)}.
\]
At equilibrium all three quantities coincide. Equivalently,
\[
|\Phi_t-x_{\rm eq}|
\le|x_f(t)-x_{\rm eq}|
\le|\Phi_{(1-\delta)t}-x_{\rm eq}|.
\]
This is a finite-time trajectory statement proved from scalar monotonicity,
not a reinterpretation of the instantaneous relative rate error.

The exact computable bracket width
\[
w(t)=|\Phi_t-\Phi_{(1-\delta)t}|
\]
bounds \(|x_f-\Phi_t|\). Since the thick speed magnitude decreases along either
branch,
\[
w(t)\le\delta t\,M_0,\qquad
M_0=\frac{a|y_0|}{d_0-by_0}.
\]
The common packet errors satisfy
\[
|\Delta n_{\gamma,f}-\Delta n_{\gamma,0}|\le Nw(t),\qquad
|\Delta u_{\gamma,f}-\Delta u_{\gamma,0}|\le\epsilon_\ell Nw(t).
\]
The bracket is usually more useful than the coarse speed bound.

If the parent selects the ANGULAR01 relative operator tolerance \(\varepsilon\),
enforce \(T_{\rm path}\ge\log(1+\varepsilon^{-1})\). Then
\(\delta\le\varepsilon/(1+\varepsilon)\); replacing \((1-\delta)t\) by
\((1-\varepsilon)t\) is a weaker valid comparison for \(0<\varepsilon<1\).
Clearly distinguish \(\delta\), the fractional speed deficit, from
\(\varepsilon\), a bound relative to the finite-opacity rate.

The tensor packet also admits a separate finite-opacity bound. From the angular
bounds, with \(K=2S/15\) and \(c_Q=\sqrt{2/3}\),
\[
\left\|\frac{Q}{B}-K\right\|_F
\le(\|K\|_F+c_Q)\frac{\delta}{1-\delta}
\equiv C_{\rm shape}
\]
uniformly along the path. Since the source has a fixed sign, its integrated
total variation is its net population change. Therefore
\[
\|\Delta\pi_{\gamma,f}-\Delta\pi_{\gamma,0}\|_F
\le \epsilon_\ell N\left[
\|K\|_F w(t)+|x_0-x_f(t)|C_{\rm shape}\right]
\]
The thick solution has travelled at least as far as the finite-opacity solution
on either monotone branch. Hence
\[
|x_0-x_f(t)|\le|x_0-\Phi_t(x_0)|\le|x_0-x_{\rm eq}|,
\]
and the sharper fully computable packet certificate is
\[
\boxed{
\|\Delta\pi_{\gamma,f}-\Delta\pi_{\gamma,0}\|_F
\le \epsilon_\ell N\left[
\|K\|_F w(t)+|x_0-\Phi_t(x_0)|C_{\rm shape}\right].
}
\]
Omit \(\epsilon_\ell\) for the photon-number PSTF packet. This bound holds for
both net emission and net absorption. It separates trajectory error from
angular-shape error and still concerns source packets, not radiation propagation
after injection.

## 10. Optional frozen-\(B\) step and finite acceptance implications

If a caller instead freezes \(B_*,Q_*\) at a selected state, the exact solution
of that different discretized substep is
\[
x_1=x_{\rm eq}+(x_0-x_{\rm eq})e^{-A\kappa B_*t},
\]
\[
\delta x=(x_{\rm eq}-x_0)
[-\operatorname{expm1}(-A\kappa B_*t)].
\]
It is a convex combination of \(x_0\) and \(x_{\rm eq}\), so preserves the
domain. Its integrated tensor is
\(\epsilon_\ell N(x_0-x_1)Q_*/B_*\).
It is exact for frozen \(B\), not for changing finite-opacity \(B(x)\).
LINE01 selects the state-dependent thick step of §§6–9 as the stronger useful
simplification; this frozen variant is retained only as an explicitly distinct
baseline, not as an unlabelled exact substitute.

A bounded implementation can be accepted against algebraic and model checks
without rerunning a cosmological campaign:

1. Positive opacity, every-ray expansion, finite data and the whole-path gate
   are validated before invoking the thick local step.
2. Local balance returns zero common source/packet; both signs of net exchange
   use nonnegative effective forward/reverse channels.
3. Atomic number and the atomic-internal/radiation energy ledger use one common
   signed increment; ionic yield and thermal kinetic heat are zero by the model.
4. The scalar endpoint lies between its initial value and equilibrium. The
   implicit residual and/or a separately evaluated Lambert endpoint establish
   the algebraic step; their tolerance must account for near-equilibrium scaling.
5. A finite-opacity comparison uses the derived endpoint bracket and separate
   tensor-shape allowance, not an unsupported trajectory-relative tolerance.
6. The tabulated source-data accuracy, complete line-transport accuracy, and
   floating-point error are reported independently from the analytic thick bound.

The parent owns the finite case count, thresholds and resource cap before any
science execution. The two dimensionless Wolfram illustrations below are scalar
formula evaluations, not old campaign repeats or cosmological IVPs.

## 11. Actual Wolfram evidence

[WOLFRAM_LINE01_RECEIPTS.json](provenance/WOLFRAM_LINE01_RECEIPTS.json) contains the actual
requests and full responses: one context query and two evaluator calls. The
context query succeeded; generic searches returned no spontaneous-\(A\) or
Bianchi-source formula authority. Its historical SpectralLineData examples
were not adopted for the new atomic source lock.

The first evaluator returned exact zero residuals for the profile average,
Einstein source, directional phase-density normalization, both thick
cancellations, population defect, frozen step, number/energy cancellation,
implicit thick ODE, Lambert-W ODE and equilibrium-domain identity. Its
detailed-balance equivalence returned True. It also emitted generic
MinValue/MaxValue feasibility messages during symbolic simplification;
the raw messages are preserved rather than relabelled as a clean tool pass.

A second targeted call returned zero algebraic residuals for balance,
cross-multiplication, the implicit ODE and the Lambert-W derivative. It also
evaluated two illustrative dimensionless endpoints at \(g=3,f_+=0.1\) and
\(a t/d_0=1\). This \(g=3\) illustration is a generic dimensionless mathematics example.
The final effective collapsed source also has g=3, but its measured/pinned
state inputs and closure assumptions are fixed separately in FROZEN_CONTRACT.md.

| \(x_0\) | \(x_{\rm eq}\) | \(x(t)\) | Branch parameter \(z_0\) |
|---:|---:|---:|---:|
| 0.5 | 0.214285714285714286 | 0.284594927169056457 | -0.533333333333333333 |
| 0.05 | 0.214285714285714286 | 0.142462753554850820 | 0.306666666666666667 |

Both endpoints lay between initial state and equilibrium. Initial \(W_0\)
identities and implicit residuals evaluated to zero. Wolfram emitted
N::meprec messages while trying to assign relative precision to those vanishing
numerical residuals; this is retained as a precision warning and is not an
independent interval certificate. No additional CAS calls were made to suppress
or cosmetically remove these messages.

The travel-time comparison, normalized tensor-packet bound and stable \(u\)
bracket are analytic derivations in this document; they were not separately
submitted to Wolfram. Fresh review remains the parent's independent review task.

## 12. Boundary to the next coupled unit

The present deliverable supplies an actual number/energy/tensor map and an
exact local reduced step. It requires source owners for \(n_l,n_u,H,\sigma,f_+\)
before any claimed physical history. It does not manufacture excited-state
populations from a pilot that stores only aggregate ion fractions, infer them
from NIST intensity, or silently map a whole-\(n=2\) shell onto a \(2p\) level.

A coupled next unit must account for the complete selected population convention,
overlapping Ly-alpha components or a justified collapsed line, source/sink
feedback, photon storage where needed, non-line heating/cooling, and ionic
yields. The present zero thermal source does not close the total energy budget.

Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.
Historical first failed REI raw remains local-only. No historical
REC126/REI129/warm729/405 calculation was repeated.

