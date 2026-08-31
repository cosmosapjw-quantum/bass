# BASS RF04 mathematical authority closure

**Date:** 2026-08-31  
**Repository:** `cosmosapjw-quantum/bass`  
**Stack base:** PR #68 head `289a2d31d6fae38122191be73ec9c9d28acaf4d7`  
**Scientific base:** PR #66 head `e660451975f3fa3bd3d9a7b5ebf5d73cc544f1ac`  
**Status preserved:** `PASS_RF04_SCALAR_RAW_SLICE_PROOF`; overall `NO_PASS_RF04`.

This package closes the formula-level questions that can be settled without changing or running production code. It does **not** claim native operator parity, numerical convergence, trajectory closure, asymptotic-preserving behavior, performance, GPU validity, or RF04 promotion.

## 1. Authority, conventions, and blocker census

Metric signature is \((- + + +)\), \(\epsilon_{123}=+1\), and \(c\) is explicit. The normal-frame photon momentum is
\[
p^a=\frac{\epsilon_\gamma}{c}(n^a+e^a),\qquad e^ae_a=1,\qquad n_ae^a=0 .
\]
The SSOT collision theorem is cold, non-tilted, electron-rest Thomson scattering. Finite electron tilt below is therefore a derived Lorentz-frame adapter around that theorem, not a silent widening of it.

| ID | Formula question | Result here | Residual work |
|---|---|---|---|
| M1 | Rust cross-product ray flow versus SSOT \(V^a\) | **CLOSED** | numerical regression |
| M2 | full-tensor screen generator and packed circular-polarization sign | **CLOSED** | bind source tests |
| M3 | fixed-chart geometric generator \(A\) | **CLOSED** | discretize on source-owned grid |
| M4 | finite-tilt Thomson and opacity normalization | **CLOSED conditional on named opacity convention** | bind runtime opacity owner |
| M5 | boosted measure and collision left functional | **CLOSED** | quadrature verification |
| M6 | positive/constant-preserving/conservative remap conditions | **CLOSED** | construct actual remap |
| M7 | Kato connection and invalid extra-\(K\) split | **CLOSED** | code-path enforcement |
| M8 | frozen \(A+C\) differential and Strang defect | **CLOSED** | dense/native comparison |
| M9 | rigorous floating support interval | **CLOSED** | outward-rounded implementation |
| M10 | raw versus post-projection leakage | **CLOSED** | expose raw diagnostic |
| H1 | q1/q3 and high-\(\ell\) closure | **NOT DERIVABLE FROM CURRENT AUTHORITY** | source trajectory/closure needed |
| C1 | telemetry, typed failures, PyO3, nonfinite boundaries | **CODING/RUNTIME** | authenticated LOCAL-01 |
| C2 | convergence, AP/stiff, trajectory, performance, GPU, RF05 | **NUMERICAL/CODING** | later DAG nodes |

Thus every identifiable **formula-only** blocker in the active RF04/LOCAL-02 path is addressed below. The project remains `NO_PASS_RF04` because implementation and numerical gates are open.

## 2. M1 — direction-flow equivalence

Define
\[
q_\sigma:=\sigma_{ab}e^ae^b,\qquad s^a:=-\sigma^a{}_be^b+q_\sigma e^a,
\]
so \(e_as^a=0\). The Rust lane uses
\[
W=\Omega_{\rm triad}+a^B\times e+n^B e-\frac{\operatorname{tr}n^B}{2}e+e\times s,
\qquad \dot e=W\times e .
\]
Using
\[
(a^B\times e)\times e=e(a^B\!\cdot e)-a^B,
\quad (e\times s)\times e=s,
\quad (n^Be)\times e=-e\times(n^Be),
\]
and noting that the trace term is parallel to \(e\),
\[
\boxed{\dot e=(q_\sigma+a^B\!\cdot e)e-\sigma e-a^B+\Omega_{\rm triad}\times e-e\times(n^Be)} .
\]
This is exactly the SSOT flow and satisfies \(e\cdot\dot e=0\). The trace of \(n^B\) cancels from direction transport but remains in the screen component rate:
\[
\boxed{\omega_{\rm scr}=e\cdot W=e\cdot\Omega_{\rm triad}+e\cdot n^Be-\tfrac12\operatorname{tr}n^B.}
\]
All geometric rates have dimension \(L^{-1}\).

## 3. M2–M3 — basis-free coherency, packed \(V\), and geometric generator

Let
\[
{\cal F}_{ab}=S_{ab}+iA_{ab},\qquad S^T=S,\quad A^T=-A,\quad {\cal F}=P(e){\cal F}P(e),
\]
where \(P_{ab}=h_{ab}-e_ae_b\). The nine-real carrier stores six entries of \(S\) and three of \(A\); its physical screen subspace is four-real-dimensional.

For a positively oriented screen dyad \((u,v)\), \(v=e\times u\), \(u\times v=e\),
\[
f=\frac12\begin{pmatrix}I+Q&U-iV\\U+iV&I-Q\end{pmatrix}.
\]
Therefore
\[
I=u{\cal F}u+v{\cal F}v,\quad Q=u{\cal F}u-v{\cal F}v,\quad U=2uSv,
\quad \boxed{V=-2uAv}.
\]
Equivalently \(A_{ab}=-(V/2)\epsilon_{abc}e^c\). In source order
\[
(S_{11},S_{22},S_{33},S_{12},S_{13},S_{23},A_{23},A_{31},A_{12}),
\]
a pure circular component obeys
\[
\boxed{(A_{23},A_{31},A_{12})=-\frac V2(e_1,e_2,e_3)}.
\]

Let \(\widehat W x=W\times x\), and \(s=ct\). Along a characteristic,
\[
\boxed{\frac{d{\cal F}}{ds}=[\widehat W,{\cal F}]+4R{\cal F}},
\qquad R=-H-\sigma_{ab}e^ae^b .
\]
Lowering to screen components gives \(+\omega_{\rm scr}[J_2,f]\), where \(J_2=\left(\begin{smallmatrix}0&1\\-1&0\end{smallmatrix}\right)\), and hence
\[
\delta I=\delta V=0,\quad \delta Q=2\omega_{\rm scr}U,\quad
\delta U=-2\omega_{\rm scr}Q,
\quad \boxed{\delta(Q+iU)=-2i\omega_{\rm scr}(Q+iU)}.
\]

On a fixed angular chart the frozen bolometric geometric generator is
\[
\boxed{(A{\cal F})(e)=-V^aD^{S^2}_a{\cal F}(e)+[\widehat W(e),{\cal F}(e)]+4R(e){\cal F}(e)},
\qquad V=W\times e.
\]
No separate Kato term belongs to this physical generator. If runtime uses dimensionless \(\tau\), define \(\chi=ds/d\tau\), so
\[
A_\tau=\chi A_s,\qquad C_\tau=\chi C_s.
\]
The adapter `expansion = 1` needs an explicit normalization such as \(\chi H=1\). The observed-sky adapter is separately \(\hat n_{\rm obs}=-e\).

## 4. M4 — finite-electron-tilt Thomson

Let
\[
u_e^a=\gamma(n^a+v^a),\qquad \gamma=(1-v^2)^{-1/2},\qquad
q(e)=1-v\cdot e,\qquad D(e)=\gamma q(e).
\]
Then
\[
\epsilon'_\gamma=-cp\cdot u_e=D\epsilon_\gamma,
\]
and
\[
e'=\frac{e+\left[\frac{\gamma-1}{v^2}(v\cdot e)-\gamma\right]v}{D},
\qquad d\Omega'=D^{-2}d\Omega.
\]
Let \({\cal S}_v:\operatorname{screen}(e)\to\operatorname{screen}(e')\). Exact symbolic reduction gives
\[
{\cal S}_v^T{\cal S}_v=P(e),\qquad {\cal S}_v{\cal S}_v^T=P(e').
\]
The bolometric boost is
\[
\boxed{(B_v{\cal F})(e')=D^4{\cal S}_v{\cal F}(e){\cal S}_v^T}.
\]
With
\[
T_{\rm Th}[X](e')=\frac{3}{8\pi}P(e')\left[\int d\Omega''X(e'')\right]P(e')-X(e'),
\]
proper-density opacity gives
\[
\kappa_{\rm rest}=n_{\rm rest}\sigma_T,
\qquad \boxed{C_v=\kappa_{\rm rest}M_DB_v^{-1}T_{\rm Th}B_v},
\]
with loss \(-\kappa_{\rm rest}D{\cal F}\). Normal-frame density gives
\[
n_n=\gamma n_{\rm rest},\quad \kappa_n=\gamma\kappa_{\rm rest},\quad
\boxed{\kappa_{\rm rest}D=\kappa_nq},
\]
and
\[
\boxed{(C_v{\cal F})(e)=\kappa_nqD^{-4}{\cal S}_v^T
T_{\rm Th}[B_v{\cal F}](e'){\cal S}_v}.
\]
Thus the generated Rust prefactor \(q\) is correct iff external opacity means \(\kappa_n\); proper-density opacity requires the extra \(\gamma\). The boosted equilibrium is
\[
\boxed{{\cal F}_{\rm eq}(e)=\tfrac12D^{-4}P(e)},\qquad C_v[{\cal F}_{\rm eq}]=0.
\]
Global electron tilt is forward-model physics; local observer boost is output-only.

## 5. M5–M6 — measure, collision invariant, and remap contract

The electron-frame quadrature weights induced by a normal-frame rule \((e_i,w_i)\) are
\[
\boxed{w'_i=w_i/D_i^2}.
\]
Since \({\cal S}_v\) is a screen isometry and \(\int d\Omega'\operatorname{tr}T_{\rm Th}[X]=0\), the \(\kappa_n\) collision generator has the left null functional
\[
\boxed{\ell_v({\cal F})=\frac1{4\pi}\int d\Omega\,q(e)\operatorname{tr}{\cal F}(e)},
\qquad
\boxed{\ell_v(y)=\frac1{4\pi}\sum_iw_iq_i\operatorname{tr}y_i}.
\]
Indeed,
\[
\ell_v(C_v{\cal F})=\frac{\kappa_n}{4\pi\gamma^2}
\int d\Omega'\operatorname{tr}T_{\rm Th}[B_v{\cal F}]=0.
\]
This explains the source-owned \(q\)-weighted functional and forbids replacing it by an unweighted sum or a row-sum check.

A remap must be typed by what it transports. For a scalar pullback/interpolant \(y_{\rm out}=Ry_{\rm in}\), constant preservation is
\[
\boxed{R\mathbf1=\mathbf1}.
\]
For a conservative density pushforward between quadratures,
\[
\boxed{w_{\rm out}^TR=w_{\rm in}^T}.
\]
For the same grid this is \(w^TR=w^T\). These are independent conditions: row stochasticity does not imply weighted conservation.

Scalar positivity requires \(R_{ij}\ge0\). A sufficient polarized cone-preserving form is
\[
({\cal R}{\cal F})_i=\sum_jr_{ij}U_{ij}{\cal F}_jU_{ij}^\dagger,
\qquad r_{ij}\ge0,
\]
where \(U_{ij}\) is the declared screen association. A nonnegative matrix with a nonnegative inverse is monomial; hence a nontrivial dissipative positive mixing remap cannot be exactly and positively reversed. Reversibility tests must be restricted to permutation/isometric transport or replaced by consistency and convergence tests.

## 6. M7 — Kato connection and rejection of the extra-\(K\) path

For any differentiable projector \(P^2=P\),
\[
P\dot PP=0.
\]
Define
\[
\boxed{K=[\dot P,P]=\dot PP-P\dot P}.
\]
Then
\[
\boxed{\dot P=[K,P]}.
\]
If \(\dot U=KU\), then \(P(t)=U(t)P(0)U(t)^{-1}\). For a physical state \(\dot y=Ly\) and moving-coordinate variable \(z=U^{-1}y\),
\[
\boxed{\dot z=U^{-1}(L-K)Uz}.
\]
Thus \(K\) is a moving-subspace connection, not an additional physical interaction.

For the source-owned rank-one equilibrium projector,
\[
P_vy=r_v\frac{\ell_v(y)}{\ell_v(r_v)},\qquad r_v={\cal F}_{\rm eq},
\]
the code expression \(\dot v[(\partial_vP_v)P_v-P_v(\partial_vP_v)]y\) is exactly \(Ky\). This projector is not assumed Euclidean-orthogonal, so no generic skew-adjoint claim is made.

An uncompensated composition
\[
e^{hK/2}e^{hC/2}e^{hG}e^{hC/2}e^{hK/2}
\]
has first-order generator \(G+C+K\). It equals intended \(A+C\) only if \(G\) was explicitly defined as \(A-K\) in the same coordinates. That compensation was not established in the rejected path, so it changes the physics at \(O(h)\).

## 7. M8 — frozen differential and splitting defect

The first LOCAL-02 comparison must be
\[
\boxed{\lim_{h\to0}\frac{\Phi_h(y)-y}{h}=(A+C)y}
\]
against an independently assembled dense oracle on the same nondegenerate grid and carrier, with \(A\ne0\), \(C\ne0\), and \([A,C]\ne0\).

Only after this passes is Strang composition admissible:
\[
S_h=e^{hA/2}e^{hC}e^{hA/2}.
\]
Exact BCH reduction gives
\[
\boxed{\log S_h=h(A+C)-\frac{h^3}{24}[A,[A,C]]-\frac{h^3}{12}[C,[A,C]]+O(h^5)}.
\]
This gives local \(O(h^3)\) and global \(O(h^2)\) under the usual smooth finite-dimensional assumptions; it proves neither stiffness robustness nor AP behavior.

Required differential mutants are: uncompensated added \(K\); node/rank permutation; omitted \(D^{-2}\) measure; screen-map orientation mismatch; and a missing/extra \(\gamma\) from an opacity-convention swap.

## 8. M9 — rigorous floating-point support bound

For a three-term IEEE-binary64 dot product, with unit roundoff \(u=2^{-53}\),
\[
\gamma_3=\frac{3u}{1-3u}=3.330669073875470729\ldots\times10^{-16},
\]
and
\[
|\operatorname{fl}(x\cdot y)-x\cdot y|\le\gamma_3\sum_{i=1}^3|x_iy_i|.
\]
Let \(\delta_{\rm in}\) bound uncertainty already present in normalized inputs and define
\[
\Delta_\mu=\gamma_3\sum_i|\hat x_i\hat y_i|+\delta_{\rm in}.
\]
A rigorous support interval uses directed outward rounding:
\[
\boxed{\mu_{\rm lo}=\operatorname{nextDown}(\hat\mu-\Delta_\mu),\qquad
\mu_{\rm hi}=\operatorname{nextUp}(\hat\mu+\Delta_\mu)}
\]
clipped to \([-1,1]\). For \(\beta\ge0\), \(D=\gamma(1-\beta\mu)\) decreases with \(\mu\), so its lower bound uses \(\mu_{\rm hi}\), with every intermediate operation outward-rounded. For signed \(\beta\), evaluate all interval endpoints. One `nextDown` after a rounded dot product is not a proof.

## 9. M10 — raw and post-projection leakage

Let \(P=P(e)\) and \({\cal F}_{\rm raw}\) be an unprojected output. A raw transversality diagnostic can be defined as
\[
\boxed{\lambda_{\rm pre}=\frac{\|(I-P){\cal F}_{\rm raw}\|_F+\|{\cal F}_{\rm raw}(I-P)\|_F}
{\max(\|{\cal F}_{\rm raw}\|_F,\epsilon_{\rm scale})}}.
\]
After \({\cal F}_{\rm post}=P{\cal F}_{\rm raw}P\), exact arithmetic gives
\[
(I-P){\cal F}_{\rm post}=0,\qquad {\cal F}_{\rm post}(I-P)=0.
\]
A post-projection number therefore measures projection arithmetic/storage residual, not raw transport leakage. It must be separated from Hermiticity defect, minimum screen eigenvalue/PSD defect, and trace/intensity. The current `max_screen_leakage` path projects first and cannot support a raw-transport leakage claim.

## 10. Limits, dimensions, and claim boundary

- Zero geometry: \(H=\sigma=a^B=n^B=\Omega=0\Rightarrow A=0\).
- FLRW normal frame: \(R=-H\), \(V=0\), and bolometric brightness scales as \(e^{-4\int Hds}\), after the branch-appropriate invariant-frame pullback.
- No tilt: \(v=0\Rightarrow D=q=1\), \(e'=e\), \({\cal S}=P\), and the collision reduces to the electron-rest theorem.
- Pure triad rotation is a component-frame action, not observer-independent creation of polarization.
- \(A_s,C_s,H,\sigma,a^B,n^B,\Omega,\kappa\sim L^{-1}\); \(A_\tau,C_\tau\) are dimensionless rates if \(\tau\) is dimensionless.

This package supports only:

> The continuum formula contract needed to assemble a scoped, frozen, same-carrier Type-II polarized geometric-plus-Thomson differential has been explicitly derived and symbolically checked.

It does **not** support `PASS_RF04`, native/PyO3 differential parity, an implemented remap, q1/q3 or high-\(ell\) closure, trajectory/convergence/AP/stiff claims, performance/GPU claims, inference, or finite-temperature/recoil/Klein–Nishina/recombination/reionization physics.
