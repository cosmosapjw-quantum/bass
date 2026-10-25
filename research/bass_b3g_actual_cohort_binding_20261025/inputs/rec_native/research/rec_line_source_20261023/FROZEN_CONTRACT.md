# LINE01 — source-bound line exchange and exact local thick flow

Frozen before new scientific execution, 2026-10-23 (Asia/Seoul).
Parent: REC PR127 HEAD `5185c396b7e07076565ca2f5044a5ccd193e6ee1`.
This is one bounded R1–R10/C1–C10 unit, selected by the next-leaf handoff.

## 1. Question and model

Connect a declared resolved, unpolarized bound–bound source to the already
verified ANGULAR01 escape moments, with explicit number, ionic, internal-energy,
radiation-energy and radiation-tensor injection ledgers. Derive and implement an
exact *local optically thick* population map under held background inputs, avoiding
a time-stepping IVP for that subproblem. This is not a cosmological history solve.

Metric signature is (-,+,+,+). Quantities refer to the non-tilted matter rest
frame and physical volume. Retain c, h=2πℏ and k_B explicitly. SI units are used
except source decimal fields explicitly marked cm^-3 or eV. The background H>0,
S=σ/H (symmetric trace-free), and q(n)=1+n·S·n>0 are prescribed within a step.
Incident f_plus>=0 is direction independent. Populations are unpolarized; no
recoil, fine-structure transfer, frequency diffusion, or time-delayed transport
is added. An injected PSTF rate is not a pre-existing radiation stress state.

## 2. Source cards and physical input

The primary card is an explicitly *effective coincident-line* collapsed 2p
model: g=g_u/g_l=3, E=10.198714553953742 eV from pinned native HyRec,
λ=hc/E, ν=E/h, A=(A_1/2+2A_3/2)/3. NIST H I persistent-line table gives
A_1/2=6.2649e8 s^-1 and A_3/2=6.2648e8 s^-1. A statistical 1:2 sublevel split,
common profile/frequency and common f_plus are imposed closure assumptions.
The two separate NIST fine cards (g=1 and g=2, their own λ,A) are retained.
This aggregate is not an equivalence claim for the actual overlapping doublet.
The n=2 whole-shell g_u=8,A=4.699e8 card is incompatible with n_2p and rejected.
Atomic tabulation uncertainty and collapsed-line model error are not certified by
the angular numerical tolerance. See provenance/COLLAPSED_SOURCE_ADDENDUM.md.

Reuse exactly one complete saved native source snapshot at z=1099.9986525171403,
REC114 `df95a074730ea0d13d609cf88d448f01f4a47ef1`:
`ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv`, blob
`6399b59ca3c97d6c5b1162f83f50a6677fad06ff`. No native solver rerun.
Reconstruct x_2p=xr[1]+3x_1s exp(-E21/TR), with native TR in eV.
Set total blue-boundary occupation to 1/expm1(E21/TR)+Dfplus_Lya explicitly.
The scalar snapshot supplies no angular field; S values are supplied fixtures.
This Planck/stimulated standalone model does not claim source-identical replay
of the native compressed departure formula. A2p_up/down are diffusion exchange
rates, not the bare spontaneous A21. The 3-epoch NPZ lacks complete physical
inputs and is not promoted into three new source states.

Use exact SI c=299792458 m/s, h=6.62607015e-34 J s,
eV=1.602176634e-19 J, k_B=1.380649e-23 J/K; ℏ=h/(2π).
Source decimals and donor bytes remain unchanged.

## 3. Exchange, ownership and finite-opacity moments

Let Δ=g n_l−n_u>0, D=n_u(1+f_plus)−g n_l f_plus,
t=A λ^3 Δ/(8πH). Reuse ANGULAR01 B=<β(t/q)> and
Q=<PSTF(nn)β(t/q)>, β(τ)=-expm1(-τ)/τ.

R=A B D; gross escaped down=A B n_u(1+f_plus)>=0,
gross escaped up=A B g n_l f_plus>=0. Signed net absorption is admitted.
Number ledger: (dn_u,dn_l,dn_gamma)=(-R,+R,+R).
Energy ledger: (du_atom_internal,du_gamma,du_thermal)=(-E R,+E R,0).
Ionic/free-electron yield of this bound–bound process is exactly zero in this
model. It does not supply missing ionization, daughter, electron, neutrino,
stopping, or recoil yields for other processes.
Number PSTF injection is A D Q; energy PSTF injection is E A D Q.
Spatial photon injection is E A D(B I/3+Q), and the odd momentum injection is 0.

Allowed owner mode is `standalone_detached` with `native_line_owner_active=false`
inside this detached calculation. Any request to add this source while that
same native line owner is active must fail explicitly. No production owner
replacement is implemented. Canonical Tvv, real Sobolev, feedback, diffusion,
history, residual and JVP are not modified by this unit.
PR220's compact33 kernel remains a reusable future coupled-population owner;
its 129 runs are neither repeated nor added to this line study.

## 4. Exact local thick population map

Hold N=n_l+n_u,H,S,f_plus fixed for a source substep. Set x=n_u/N,
b=g+1, d(x)=g-bx>0, F=1+b f_plus, x_eq=g f_plus/F,
d0=g/F, y=x−x_eq, κ=8πH/(N λ^3), η=κ F/d0.
Then dx/dt=−κF(x−x_eq)/(g-bx) in the thick model.

z0=−b y0/d0 > -1 and
x(t)=x_eq−(d0/b) W0[z0 exp(z0−ηt)].
The physical principal branch preserves non-inversion and approaches equilibrium
monotonically. Evaluate equivalently via the unique u<=0 root
u+z0 expm1(u)+ω=0, ω=ηΔt,
in [-ω+min(z0,0), min(0,-ω+max(z0,0))].
Its derivative 1+z0 exp(u)>0; this is a scalar algebraic solve, not an IVP.
Use expm1(u) for the signed packet: Δn_gamma=−N y0 expm1(u).
Special branches Δt=0 and y0=0 return exact zero exchange.
The integrated thick PSTF number packet is (2S/15)Δn_gamma.

Gate the entire segment between x0 and x_eq, not only the initial state:
t_min=Aλ^3 N[g-b max(x0,x_eq)]/(8πH).
Require t_min/qmax >= log1p(1/1e-8)=18.420680753952364.
δ=exp(-t_min/qmax) gives finite rate ratio in [1−δ,1].
The finite-opacity flow lies between thick maps at t and (1−δ)t;
their width w bounds absolute population error and E N w bounds energy error.
Log-domain δ must be recorded when exp underflows; a rounded zero is not a
claim of exact finite-opacity equality. Finite tensor packet bounds are supplied
only with their separate proof, not inferred from a scalar relative bound.

## 5. Finite execution plan, frozen before run

No completed campaign is replayed. No cosmological or local IVP is selected.
One production attempt stores raw outputs immutably. Targeted correction may
reuse stored rows; any new rows are counted separately with the original failure.

* 36 source states: 27 effective-card states (3 driving cases emission/LTE/
  absorption, f=0.1; 3 t targets 0.1,1,100; 3 S fixtures isotropic, triaxial
  diag(-0.4,0.1,0.3), and its fixed rotation), 3 native-state angular fixtures,
  and 6 separate fine-card driving fixtures at t=1. N=1e9 m^-3 for constructed
  states; H is set to attain the declared t. Driving populations are x_eq,
  (x_eq+g/(g+1))/2, and x_eq/2.
* 27 local map rows: effective g=3, f in {0,0.1,2}; f=0 uses emission and
  equilibrium, other f uses emission/equilibrium/absorption; ω in {1e-6,0.5,8}
  gives 24 rows. The native state at ω={0.1,1,5} supplies 3 further rows.
  Constructed paths have t_min/qmax=20, with triaxial S. Native path uses
  its stored H,N and imposed S. Comparison uses independent high-precision W0.
* 6 selected new source rows compare phase-space normalization and angular
  moments to the original Einstein class and a direct lab-frame quadrature.
  Normalize cancellation checks by the gross microscopic scale, not tiny net R.
* 2 finite-opacity separable scalar-reference roots (isotropic emission and
  absorption with path threshold 20) check the proved time-bracketing relation.
  Quadratures/root evaluations are counted; this is not time stepping.
* 3 plot tracks ×81 analytic-map samples (243 map outputs) show emission,
  absorption and the actual saved native state's local relaxation. These are
  plot samples of the new local model, not cosmological trajectory runs.
* At most 6 fresh off-grid cases in one independent review; math then code/plot
  review belong to that same pass. No repeat benchmark campaign.

## 6. Acceptance and failure evidence

All results finite; counts/units/source ownership explicit. Sign and positivity
of gross rates must hold. Atomic number and number/energy exchange residuals
are bounded by 64 machine eps times their exchange scale. LTE uses absolute
residual normalized by gross rates, never division by net zero.
Direct source-class phase-space residual <=5e-13 of gross microscopic scale;
6 fresh angular-source comparisons <=5e-10 of corresponding B or B tensor
normalization. High-precision map endpoint error <=5e-11 times initial
departure (plus 64 eps rounding of x_eq); packet error <=5e-13 times N|y0|
plus 64 eps of packet scale. Log-root residual <=5e-13(1+ω+|z0|).
No sign flip or overshoot beyond 64 eps on fractional populations.
The finite-flow references must lie inside the analytic brackets allowing
5e-13 absolute fractional-population numerical slack. Gross scale and any
near-equilibrium conditioning are reported.
Reject nonpositive/NaN parameters, inverted/invalid population, invalid S,
directional contraction, wrong card/population scope, duplicate ownership,
and an insufficient whole-path thick gate. Numeric range outside the tested
contract is not silently certified. No performance target is required.

## 7. Delivery and inherited decisions

A: sources/theory/contract; B: code plus immutable execution evidence;
C: one review, plots, report, DAG and handoff. Each checkpoint is published to
a draft branch and backed up to Dropbox and Drive. Provider acknowledgement,
size, Git blob identity and whole-byte archive verification are separate claims.

Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.
REC119 125main+1control=126 and REI220 127main+2oracle=129 remain distinct.
warm729, THERM02 eight IVPs and prior ANGULAR01 405 rows are reused, not repeated.
Historical first failed REI raw remains local-only. This unit does not complete
all-nuclide nuclear reactions, full thermal closure, or full Bianchi recombination.
