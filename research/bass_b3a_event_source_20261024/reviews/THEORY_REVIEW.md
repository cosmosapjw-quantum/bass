# BASS B3a independent theory review

Unit: `BASS_B3A_EVENT_SOURCE_20261024`  
Reviewer: separately delegated agent `/root/b3a_theory_review`  
Decision: **PASS_SCOPED with the explicit conventions and axis-boost scope below.**  
Review method: independent analytic antipodal contraction and exact rational arithmetic. This is a fresh independent agent review; it does not establish that a different model architecture was used.

## Evidence and retained provenance

The reviewer inspected the user-supplied B3a formulas, fixtures, and historical verification summary in the current conversation. The original Wolfram source/call/output transcript was not supplied to this reviewer as a full raw artifact. Accordingly its historical test counts are attributed to the user's receipt, rather than represented as newly inspected raw output.

Preserved historical sequence: the initial reference kernel had **7 failures among 16 checks**, caused by `NumberQ` rejecting exact radicals; the stated `NumericQ` plus exact-real repair subsequently passed **16/16**. A separate constrained-source set passed **4/4**. A trial undeclared-vector warning was repaired. The user's receipt reports zero residuals for the general formula, trace and dimensional checks, one actual Wolfram figure, zero new IVPs, zero historical campaign replays, and independent-model review `NOT_RUN` at that historical checkpoint. Nothing in this new review rewrites those initial failures or makes them first-attempt passes.

Fresh execution: `python3 /workspace/scratch/fe69646d3c76/b3a_work/reviews/check_event_rate_exact.py`, working directory `/workspace/scratch/fe69646d3c76`, exit code 0. Its companion `THEORY_EXACT_CHECKS.json` records **23 exact assertions passed**, zero failed, 0.005570141001953743 s wall and 0.005566643 s CPU. These are checks of this review's independent pair-contraction formulas, separate from the historical Wolfram 16+4 checks. New IVPs=0; old campaign replays=0. Remaining historical wall/CPU budgets stay null and `budget_reset=false`.

A current-turn Python execution probe returned `PYTHON_PASS` (3.12.14). SymPy was absent (`find_spec('sympy') is None`); the review continued with the Python standard library. No historical service error was inherited.

## 1. Conventions that make the dimensional formulas unambiguous

Use signature `(-,+,+,+)`, coordinates `x^0=ct`, and a dimensionless future observer `u^a u_a=-1`. Photon energy measured by that observer is `E(u)=-c u_a p^a>0`.

Here `dR` is the differential photon event rate **per invariant time-volume `dV_4/c`**, which is locally `dt_proper dV_proper`, with any momentum/angular marks included in the measure. Its SI unit after integrating momentum marks is `m^-3 s^-1`. If instead a provider gives events per geometric four-volume `dV_4` (unit `m^-4`), multiply its rate by `c` before using the equations below. Merely saying “per spacetime volume” leaves this factor unspecified.

Then

\[
Q^a=\int p^a\,dR,\qquad
K^{ab}(u)=c\int\frac{p^ap^b}{-u\cdot p}\,dR
         =c^2\int\frac{p^ap^b}{E(u)}\,dR.
\]

`Q^0` and `Q^i` have the common units of force per volume; `cQ^0` is energy per volume per time. `K` has units of energy per volume per time, equivalently pressure per time. If the symbol for the observer is instead a physical four-velocity `U^a=c u^a` with `U.U=-c^2`, the correct equivalent formula is `K^{ab}=c^2 integral p^a p^b/(-U.p) dR`.

Let `h^a_b=delta^a_b+u^a u_b`. Exact identities are

\[
g_{ab}K^{ab}=0,\qquad K^{ab}u_b=-cQ^a,\qquad
\dot{\mathcal E}(u)=-c u_aQ^a=h_{ab}K^{ab},
\]

\[
\Pi^{ab}_{\rm rate}(u)
=h^a{}_c h^b{}_d K^{cd}(u)-\frac13h^{ab}\dot{\mathcal E}(u).
\]

The zero trace follows from null momenta, not a closure. These identities also hold for a signed net event measure.

## 2. Tensor transformation versus changing the observer argument

For fixed geometric observer `u`, `K(u)` is a genuine rank-two tensor. Under a basis change `Lambda`,

\[
K'(\Lambda u)=\Lambda K(u)\Lambda^T.
\]

The target clock in the new observer rest basis is `(1,0,0,0)`. In general it is a different geometric observer from `Lambda u`; therefore the corresponding denominator must be changed. Calling the tensor law itself incorrect would misstate the issue. The incorrect operation is identifying `Lambda K(u_old) Lambda^T` with `K(u_new)` while leaving the physical observer argument implicit.

For the fixture convention the positive boost is

\[
p'^0=\gamma(p^0+\beta p^x),\qquad
p'^x=\gamma(p^x+\beta p^0).
\]

It describes target components for which the formerly isotropic source has positive x momentum. Reversing the passive-boost sign reverses `Q^x`; the diagonal pressure results depend on `beta^2`.

An instantaneous state's number-density weight on a new spatial hypersurface transforms as `w_new=w E_new/E`. The scalar event measure already counts events per invariant time-volume, so applying that density factor to `dR` counts the observer effect twice. A provider supplying rates per emitter proper time, per coordinate time, or per particle must first specify its density and clock conversion; those rates cannot silently be identified with invariant volumetric `dR`.

## 3. Independent exact fixture derivation

Write rest photons as `p=(E/c)(1,n)` and normalize the total rest event rate to `P/E`; thus `P` is rest energy emitted per proper volume per proper time. Both angular rules have `<n>=0` and `<n_i n_j>=delta_ij/3`. Consequently both give

\[
\frac{cQ}{P}=(1,0,0,0),\qquad
\frac{K^{ij}(u_{\rm rest})}{P}=\frac13\delta^{ij}.
\]

For **an x-axis boost `boldsymbol beta=(beta,0,0)`**, antipodal pairing gives

\[
\frac{cQ'}P=(\gamma,\gamma\beta,0,0),\qquad
\frac{K_A^{ij}}P=
\operatorname{diag}\!\left(
 \frac{\gamma(1+2\beta^2)}3,
 \frac1{3\gamma},\frac1{3\gamma}\right),
\]

\[
\frac{K_B^{ij}}P=
\operatorname{diag}\!\left(
 \frac{\gamma(1+\beta^2)}{3-\beta^2},
 \frac1{\gamma(3-\beta^2)},
 \frac1{\gamma(3-\beta^2)}\right).
\]

For B the x-direction cosine is `+/-s`, `s=1/sqrt(3)`. The nontrivial contraction is

\[
\frac12\left[\frac{(\beta+s)^2}{1+\beta s}
             +\frac{(\beta-s)^2}{1-\beta s}\right]
=\frac{\beta^2+s^2-2\beta^2s^2}{1-\beta^2s^2}
=\frac{1+\beta^2}{3-\beta^2}.
\]

Both spatial traces are `gamma P`. Subtracting that common trace divided by three gives

\[
\frac{\Pi_{A,xx}}P=\frac{2\gamma\beta^2}{3},\qquad
\frac{\Pi_{B,xx}}P=\frac{4\gamma\beta^2}{3(3-\beta^2)},
\]

with yy and zz equal to minus half the respective xx component. Therefore

\[
\boxed{\frac{\Pi_{A,xx}-\Pi_{B,xx}}P
=\frac{2\beta^2}{3\gamma(3-\beta^2)}}\qquad
(|\beta|<1,\ \boldsymbol\beta=(\beta,0,0)).
\]

At `beta=3/5`, `gamma=5/4`, these reproduce exactly

\[
\frac{cQ'}P=(5/4,3/4,0,0),\quad
\frac{\Pi_A}P=\mathrm{diag}(3/10,-3/20,-3/20),
\]

\[
\frac{\Pi_B}P=\mathrm{diag}(5/22,-5/44,-5/44),\quad
\frac{\Delta\Pi}P=\mathrm{diag}(4/55,-2/55,-2/55).
\]

All denominators are strictly positive for subluminal boosts. At beta=0, each anisotropic rate vanishes; the xx difference begins at `2 beta^2/9`. As `|beta| -> 1`, the absolute difference tends to zero although each individual xx rate diverges like gamma. This limiting comparison does not license evaluation at a null observer.

Using `Lambda K(u_rest) Lambda^T` as the target-clock rate instead would give

\[
\frac{cQ_{\rm wrong}}P=
\left(\gamma^2(1+\beta^2/3),\frac43\gamma^2\beta,0,0\right)
=(7/4,5/4,0,0)
\]

at beta=3/5. Its mismatch with the directly transformed four-vector is an exact diagnostic.

## 4. Required scope correction: beta magnitude does not fix the general direction

The expression in the box is general in the scalar x-directed boost parameter. The two finite rules have cubic symmetry, not full rotational symmetry of their higher angular moments. Consequently it must not be described as an arbitrary-direction formula depending only on `|boldsymbol beta|`.

An exact counterexample uses `boldsymbol beta=(1/5,2/5,2/5)` with the same magnitude 3/5 and gamma 5/4. Independent antipodal contraction yields

\[
\frac{\Delta\Pi_{xx}}P=-\frac{286408}{10384605}
\simeq-0.02758005720968684,
\]

instead of the x-aligned value `4/55`. The full exact matrix is saved in `THEORY_EXACT_CHECKS.json`; its trace is zero. This correction is closed by explicitly adding the x-axis qualification. A general-vector API may use the covariant integral or the direct event sum without that scalar shortcut.

## 5. Sector ownership, absorption and the BASS map

For gross emission the event measure is nonnegative, and the photon spatial `K` is positive semidefinite. The STF pressure rate is signed even in that case. For net source accounting write `dR_net=dR_emit-dR_absorb` and retain the two owner records separately; net `K` and net energy injection need not be nonnegative. Positivity clipping would change the source equation.

Four-momentum conservation requires the physically identified partner to carry `Q_partner=-Q_gamma` for the same event, frame and time-volume convention. This alone does not specify a matter pressure-rate tensor, a donor's internal energy decomposition, its evolving mass, or its admissible state domain. In particular the donor's anisotropic stress is not determined by assigning it `-PiRate_gamma`. Recombination may draw on a specified combination of kinetic and atomic binding energy; the split has to be read from the selected owner's actual source contract.

With fixed `L`, `tau=ct/L`, `kappa=8 pi G/c^4`, and physical energy density convention `rho_hat=kappa L^2 rho_phys`, the dimensional conversion is

\[
U=\frac{\kappa L^3}{c}\dot{\mathcal E},\qquad
J^i=\kappa L^3 f^i,\qquad
\widehat\Pi^{ij}_{\rm rate}
=\frac{\kappa L^3}{c}\Pi^{ij}_{\rm rate,phys}.
\]

All three right-hand-side quantities are dimensionless in the tau equation. An existing state stress `Source.pi = kappa L^2 pi_phys` is different from its rate; the current source API must decide how a kinetic source increment modifies the state. No direct replacement by `PiRate_hat` follows from the conversion formula.

## 6. Scope and outstanding integration obligation

This local angular counterexample preserves G1B's massless collisionless radial reduction: that reduction fixes the angular distribution and uses momentum homogeneity; A versus B changes the angular event measure. No new obstruction to the radial result, no general collision closure, and no literature novelty/no-go claim is made.

The analytic formulas and exact reference checks above are `derived` and independently `implementation-verified` at the stated fixture scope. Admission of a nonzero physical source still requires one inspected REC/HE owner's concrete event measure, frame, clock, gross-emission/absorption split, and internal-energy partner. This reviewer has not inspected such an owner and does not certify that integration. B1/B2 acceptance gaps, historical budget unknowns, coupled IVPs, restart, merge and production remain outside this theory decision.
