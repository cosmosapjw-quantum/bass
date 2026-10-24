# B3b finite LINE01 exchange: independent construction and review

Reviewer: `/root/b3b_theory_review`.
Method: direct algebra and inspection of the actual unchanged REC `exchange_source`,
`solve_log_flow`, `thick_local_step`, and BASS `FixedScale`, `State`, `Source`,
`constraints`. No scientific Python suite, IVP, prior-campaign replay, or remote
mutation was performed by this reviewer. Parent performs the separately recorded
Wolfram check and implementation validation.

The supplied physmath research-loop 1.0.0 R5/R6 definitions are applied. This is one
independent theory pass. The implemented finite transaction will need its own
bounded code/evidence review; this document does not pre-admit unexecuted code.

## 1. Source-qualified problem and decision

**Theory verdict: PASS_SCOPED for the frozen-coefficient optically thick LINE01
map, integrated gross counts, and canonical-rest-frame emission transaction.**

The actual REC owner is an exclusive detached two-level source. It already owns
the finite atomic populations through `LineState` and `thick_local_step`.
Its `f_plus` is prescribed incoming boundary occupation. A general finite closed
photon bath is not supplied by this API. Thus the general-f gross-count formula
below is a valid prescribed-boundary ledger; the closed BASS photon-stock
transaction can first be admitted on the f_plus=0 emission pathway, where no
photon donor is required.

All statements below use the same selected source card and population scope,
N>0, H>0, f>=0, fixed symmetric trace-free S with q(n)=1+n.S.n>0, and
0<=x0<g/(g+1). N, H, S and f are frozen during this local source interval.
The existing whole-path thick-opacity gate remains authoritative. Its default
threshold is log(1+1/1e-8), not an arbitrary new tolerance.

This exact local map is a reduced source substep. It does not solve background
evolution, native history propagation, finite bath depletion at f>0, or thermal
recoil. No new strong no-go or literature novelty claim is made.

## 2. Reduced equation and population flow

Set

\[
b=g+1,\quad F=1+bf,\quad x_e=\frac{gf}{F},\quad
d_e=\frac gF,\quad k=\frac{8\pi H}{N\lambda^3},\quad
\eta=\frac{kF}{d_e}=\frac{kF^2}{g}.
\]

Here x=n_u/N, and the positive opacity factor is d(x)=g-bx. The actual thick
source obeys

\[
\dot x=-\frac{kF(x-x_e)}{g-bx}.
\]

With y=x-x_e, y0=x0-x_e, z0=-b y0/d_e and omega=eta*dt, its non-equilibrium
solution is y1=y0*exp(u), where

\[
u+z_0\operatorname{expm1}(u)+\omega=0,\qquad u\leq0.
\]

The owner returns the stable increment dx=y0*expm1(u). The physical domain gives
z0>-1, so the derivative of the root function is 1+z0*exp(u)>0 on u<=0.
There is a unique root and the population moves monotonically toward xe without
crossing it. Both endpoints remain inside [0,g/b). The owner computes its opacity
bound using max(x0,xe), which bounds the entire path.

Introduce v=-u>=0, a(v)=1-exp(-v), r(v)=v-a(v). The flow identity becomes

\[
\omega=v+z_0a(v),\qquad \Delta x=-y_0a(v).
\]

At exact equilibrium y0=0, the logarithmic ratio y1/y0 is undefined. The
existing owner deliberately returns u=0 because its net packet is zero.
For gross counting, the analytic continuous extension is **v=omega**, obtained
from z0=0 in the root equation. This is a downstream interpretation requirement,
not a defect in the owner's original net-packet API. At dt=0, v=0.

## 3. Integrated gross channels: algebra and stable positive form

The angle-integrated thick rates per proper volume are

\[
\dot D_\downarrow=Nk(1+f)\frac{x}{g-bx},\qquad
\dot D_\uparrow=Nkgf\frac{1-x}{g-bx}.
\]

They are separately nonnegative. Since

\[
\frac{dt}{du}=-\frac{d_e-b y_0e^u}{kF},
\]

the common opacity factor cancels in each integral, giving

\[
D_\downarrow=\frac{N(1+f)}F[x_ev+y_0a(v)],
\]

\[
D_\uparrow=\frac{Ngf}F[(1-x_e)v-y_0a(v)].
\]

The stable implementation form contains only nonnegative summands:

\[
\boxed{D_\downarrow=\frac{N(1+f)}F[x_0a(v)+x_e r(v)]},
\]

\[
\boxed{D_\uparrow=\frac{Ngf}F[(1-x_0)a(v)+(1-x_e)r(v)]}.
\]

Here a(v)=-expm1(-v). Near v=0, compute r without subtracting two nearly equal
O(v) numbers:

\[
r(v)=v^2\sum_{m=0}^{\infty}\frac{(-v)^m}{(m+2)!}
=\frac{v^2}{2}-\frac{v^3}{6}+\frac{v^4}{24}-\cdots.
\]

A bounded alternating-series evaluation for 0<=v<=1/2, with the next term as
an absolute truncation bound, is sufficient; outside that interval direct
v+expm1(-v) has moderate subtraction conditioning. This is a positive analytic
construction, not a post-computation max(0,.) repair. Physical underflow or an
unrepresentable requested increment must be diagnosed explicitly.

Using the root identity also yields the proposed alternative expressions

\[
D_\downarrow=N(1+f)[kf\Delta t-\Delta x],\qquad
D_\uparrow=Nf[k(1+f)\Delta t-\Delta x].
\]

They are algebraically correct but unsuitable as the primary floating-point
implementation near an absorption start x0=0. There the down count is O(dt^2)
and the first alternative subtracts equal leading O(dt) terms.

The signed net count must retain the owner's stable independent value

\[
D_{\rm net}=D_\downarrow-D_\uparrow
=Ny_0a(v)=-N\Delta x.
\]

Near detailed balance, do not reconstruct that small net value by subtracting
large rounded gross counts. Check their difference using a gross normalization,
and use the stable net count for the conservative state increments.

### Essential limiting cases

1. **LTE:** x0=xe, v=omega. Both gross counts equal
   N*k*f*(1+f)*dt, which is positive for f,dt>0, while the net is exactly zero.
   Interpreting the owner's u=0 shortcut as the gross elapsed clock would be wrong.
2. **Zero incident occupation:** f=0, xe=0. D_up=0,
   D_down=N*x0*a(v)=-N*dx, and 0<=D_down<=N*x0. The finite atomic upper population
   supplies every created photon; no incoming photon reservoir is needed.
3. **Absorption from x0=0:** for f>0,
   D_down=N(1+f)*xe*r(v)/F=O(v^2), while D_up has an O(v) term. The positive form
   resolves the small real emission without clipping or signed cancellation.
4. **Zero step:** dt=0 implies both counts and all state increments are exactly0.
5. **Empty upper population with f=0:** both counts stay0 for any admitted duration.

## 4. Semigroup and count composition

For frozen parameters, the unique autonomous flow satisfies
T(dt2,T(dt1,x0))=T(dt1+dt2,x0). For nonzero y0, the log decrements add:
v_total=v1+v2. After the first step y1=y0*exp(-v1), and

\[
a(v_1+v_2)=a(v_1)+e^{-v_1}a(v_2).
\]

Substitution into the primitive gross formulas shows
D_down,total=D_down,1+D_down,2 and likewise for D_up. At LTE, the counts are
linear in dt and the result follows directly. This property is appropriate for
one full versus two half source-step validation with identical frozen data.

The finite-opacity model already has a source-owned endpoint/population and
net-energy/STF envelope. Reuse that envelope with its original limitations.
It is not automatically a relative error certificate for each new integrated
gross channel. The formulas in this section are exact for the reduced thick
model; any broader gross finite-opacity bound would require its own derivation.

## 5. Positive 14-direction exact cubature for the thick packet

Use six signed coordinate axes, each with weight1/15, and eight cube corners
(+/-1,+/-1,+/-1)/sqrt(3), each with weight3/40. Denote directions n_j and base
weights A_j. Direct component counting gives

\[
\sum_j A_j=1,\quad
\sum_j A_j n_{ji}n_{jk}=\delta_{ik}/3,
\]

\[
\sum_j A_j n_{ji}n_{jk}n_{j\ell}n_{jm}
=\frac{\delta_{ik}\delta_{\ell m}+\delta_{i\ell}\delta_{km}
+\delta_{im}\delta_{k\ell}}{15}.
\]

For example, the xx fourth moment is2/15+(3/5)/9=1/5, and the xxyy moment is
(3/5)/9=1/15. Every odd monomial through degree5 vanishes by sign symmetry.
These identities prove exact integration of spherical polynomials through degree5.

For q_j=1+n_j.S.n_j, continuum positivity is checked by the source owner
(1+lambda_min(S)>0), not merely at the14 nodes. The packet weights

\[
\Delta n_j=D_{\rm net} A_j q_j
\]

are nonnegative on the f=0 emission branch. Because traceS=0, they obey

\[
\sum_j\Delta n_j=D_{\rm net},\quad
\sum_j\Delta n_j n_j=0,\quad
\sum_j\Delta n_j n_jn_j^T
=D_{\rm net}(I/3+2S/15).
\]

The proof uses arbitrary symmetric STF S, including rotated triaxial S. Thus
number current and stress-energy match the continuous quadratic thick source
exactly in exact arithmetic. This is a degree-specific cubature fact, not
generic convergence of the full angular distribution. Fourteen packets do not
certify later nonlinear collisions, higher multipoles, or a different spectral
source. No execution-time speedup follows from the node-count reduction alone.

## 6. Actual BASS finite-state transaction and units

Let alpha_L=kappa_grav*L^2 with kappa_grav=8*pi*G/c^4. Then alpha_L has units
m^3/J, so alpha_L*E*D_net is a dimensionless BASS energy-density increment.
For a chosen fixed physical momentum scale Pstar,

\[
\mathbf k_j=\frac{E}{cP_\star}\mathbf n_j,\quad m_j=0,\quad
\Delta w_j=\alpha_L cP_\star\Delta n_j.
\]

These are actual G1B kinetic **state** weights. Their moments are

\[
\Delta\rho_\gamma=\alpha_L E D_{\rm net},\quad
\Delta\mathbf q_\gamma=0,
\]

\[
\Delta p_\gamma=\alpha_L E D_{\rm net}/3,\qquad
\Delta\pi_\gamma=\alpha_L E D_{\rm net}(2S/15).
\]

The finite atomic receiver changes n_u by -D_net and n_l by+D_net, with
Delta rho_atomic,int=-alpha_L*E*D_net, zero thermal change and zero momentum
exchange in the canonical rest frame. Unchanged atomic rest-mass/background
energy, if present in the caller, remains separate and must not be replaced by
the excitation ledger.

The rate/state conversion is consistent:

\[
\int U\,d\tau
=\int\frac{\kappa_{\rm grav}L^3}{c}\dot E\frac{c\,dt}{L}
=\kappa_{\rm grav}L^2\Delta E.
\]

Thus a finite state update uses L^2, while instantaneous Source transfer fields
use L^3/c. Similarly, the integrated PiRate changes the radiation state pi;
PiRate_hat itself is not a replacement for that state pi.

At fixed h,sigma,n,a,alpha, BASS's actual Hamiltonian and Codazzi constraints
depend on total rho and total flux. The above closed rest-frame transfer keeps
both totals invariant, so it leaves these constraint residuals unchanged in
exact arithmetic. It does not keep the evolution RHS unchanged: the newly
created radiation pressure and pi enter subsequent evolution normally.

After committing the finite increment, return the updated state stresses with
zero transfer fields for that already-applied interval, or otherwise ensure the
same transfer is not integrated again through the B3a U/J source. Use the physical
(owner,epoch,transfer_id) uniqueness convention already repaired in B3a.

A zero increment must preserve the stock without creating fake epsilon-weight
photons. An initially empty photon stock needs an explicit vacuum branch; the
underlying kinetic helper requires nonempty arrays and should only be called
after real packets exist. Never manufacture a seed population for this purpose.

For extremely small steps, the owner's stable nonzero dx can coexist with a
rounded endpoint x1==x0. A receiver must not claim resolved population depletion
solely from the stable packet. Use a declared finite-precision conservation
scale/error bound or reject an unrepresentable requested state transaction;
retain the separate stable increment. This is numerical resolution, not grounds
to clip counts or populations. Tests should include one such edge case.

## 7. State boost and the event-clock boundary

Once the rest-frame created packet is defined as a state on its specified slice,
the existing kinetic state boost w_new=w*E_new/E is correct. Because the14-node
rule matches its N and T, boosting all packet states preserves the same Lorentz
transformation of those matched tensors in exact arithmetic.

This does not authorize replacing B3a's invariant event-rate weights by those
state weights. A target-observer rate K(u) has a changed rational denominator
and is not integrated exactly by this degree5 polynomial rule in general.

Likewise, a boost of the completed rest-slice state is not automatically a
finite simultaneous collision transaction over a different observer's time
interval. A boosted slice cuts a time-dependent source worldtube differently.
In particular, a rest-frame transfer changes the total spatial pressure while
preserving rest-frame total energy; blindly boosting that finite stress change
does not imply unchanged target-slice T00. The current finite transaction should
therefore require the canonical matter-rest frame and proper-time interval.
Observer-transformed state snapshots can be exposed separately with that meaning.

## 8. Bounded implementation acceptance obligations

1. Use the actual unchanged source card/map and preserve its full-path thickness
   admission, owner, population scope, SI units and canonical source frame/clock.
2. Test stable gross counts at LTE, f=0, x0=0 absorption start, small dt, zero dt,
   and an ordinary off-LTE source against an independent positive integral or
   sufficiently precise algebraic reference. Check net/gross with a gross scale.
3. Verify frozen-parameter population and count semigroup using one full and two
   half intervals; this is a local map check, not a new cosmological IVP.
4. Verify the14-node moment identities on diagonal and rotated STF S; preserve
   q positivity through the actual source's continuum-domain validator.
5. On f=0, verify finite atomic depletion, photon-number increase, energy balance,
   source-derived pi increment and the original BASS constraint residuals.
6. Verify vacuum/zero-update behavior without artificial photon seeds, and retain
   a stated policy for unrepresentable tiny state changes.
7. Test physical-unit/Pstar rescaling, wrong source identity/frame/clock, duplicate
   commit and f>0 closed-stock refusal. A prescribed-f gross ledger may still be
   evaluated without pretending to advance a closed bath.
8. Keep new tests small and tied to these changed dependencies. Reuse B3a exact
   A/B, old G1B science and existing donor evidence; no old campaign replay.

Final scientific scope: a constructive conservative finite-emission interface
using a real atomic population owner and actual BASS photon state moments, plus
general prescribed-boundary integrated gross counts. Actual history calibration,
general finite-bath absorption and coupled background evolution retain their
separate input and execution requirements.
