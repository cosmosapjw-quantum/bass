# LINE02 frozen contract — native exclusive Lyα source owner

2026-10-23 Asia/Seoul. Selected next DAG leaf: LINE_NATIVE_OWNER.
R1–R10 and C1–C10 cover one frozen-state source adapter, not a history campaign.

## Scope and source identity

Use REC PR114 df95a074730ea0d13d609cf88d448f01f4a47ef1 and the exact
141089-byte ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv, SHA256
3a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7.
It supplies two real and311 virtual unknowns at z1099.9986525171403.
Reuse original source loader/block assembly where dependency-isolated and feasible.
The original May2012 source and any extracted AST segments are attributed by hash.
All unmodified diffusion, Tvv, feedback/history data remain original.
The current upstream HYREC-2 is a distinct version, not an implicit replacement.

Signature(-,+,+,+), local non-tilted orthonormal frame. Proper time in seconds.
Native H s^-1, nH cm^-3; physical ledger uses nH_SI=1e6*nH m^-3.
Native xr variables and Df are departures, not physical populations/occupation.
TR is held in eV; x2p=xr_p+3*x1s*exp(-E21/TR).
Use native LYA_FACT=4.662899067555897e15 cm^-3 literally.
Modern SI hc reconstruction differs by about2.66e-7 and is separately reported.
Energy E21=10.198714553953742eV times exact eV-to-J; c,hbar,k_B remain explicit.

## Exclusive affine source partition

Native line r0=LYA_FACT*H/(nH*x1s), b0=3*x1s*Dfplus_Lya, s0=r0*b0.
Exactly the native Trr[1,1] contribution r0 and sr[1] contribution s0
are one owner. Retain Beta,2s/2p mixing,two-photon/Raman,virtual diffusion,
Trv/Tvr/Tvv and other source terms. Retain the frozen incoming history values;
the actual history evolution operator is not present and is not replaced.

For full313 matrix M and source s, embed e at real2p index1:
Mstar=M+(r-r0)*e*e^T, sstar=s+(r*b-r0*b0)*e.
Residual Fstar=Mstar*z-sstar. State/parameter JVP with other blocks frozen:
dF=Mstar*dz+e*((z_p-b)*dr-r*db).
r>=0, finite b; the line-parameter derivative is conditional on frozen other
blocks. It is not the full cosmic/state-dependent HyRec Jacobian.

The sandbox adapter is an exclusive replacement. It exposes no additive
LINE01-on-active-native-source mode. Reject duplicate ownership explicitly.
Original inputs remain immutable. This unit does not alter production source.

Let K=Trr-Trv*V^-1*Tvr, c=sr-Trv*V^-1*sv, x=K^-1*c,
v=K^-1*e, a=e^T*v and eta=1+(r-r0)*a.
Then xstar=x+v*((r*b-r0*b0)-(r-r0)*x_p)/eta.
Reconstruct virtual unknowns with the unchanged V solve. eta must be finite
and positive above64eps times its summed scale. Report conditioning.
Rank-one and direct Schur/full313 algebraic solves, not new native runtime or IVPs,
establish equality under this fixed-block contract.

## Native-compatible angular event and ledger

Reuse byte-identical ANGULAR01 B(tau,S),Q(tau,S), S=sigma/H, q=1+n.S.n>0.
Aeff=(6.2649e8+2*6.2648e8)/3 s^-1 is the prior effective coincident2p model.
Set tau=Aeff/r0 so the angular ground-opacity model preserves the native r0.
At a constructed tau, r0=Aeff/tau is an explicitly synthetic coefficient control.
Define C=tau*B, D=tau*Q, rstar=r0*C, bstar=b0.
Native driving is d=xr_p-b0. Event count per H: J=rstar*d.
Energy/count: dn_2p=-nH_SI*J, dn_1s=+nH_SI*J,
dn_gamma=+nH_SI*J; du_internal=-E*nH_SI*J,
du_gamma=+E*nH_SI*J, kinetic_heat=0; ionic/electron yield=0 for this event only.
The native total xe rate can still change indirectly through excited populations.
Tensor injection is E*nH_SI*r0*d*D, with odd momentum zero.
Q/D are probability moments; injection is not a stored stress state.
r*xr_p and r*b0 are signed departure contributions, not nonnegative gross rates.

For tau/qmax>=18.420680753952364, reuse the admitted thick approximation:
C=1, D=2S/15, with delta=exp(-tau/qmax) and saved logdelta when underflowed.
The scalar is unchanged under tracefree shear at this approximation order;
nonzero tensor injection is a separate result. No rounded-zero error claim.
The exact source-coefficient difference propagates through the rank-one identity;
record a conditioning-aware bound when representable, its logarithm otherwise.
Finite-opacity quadrature is used only for the new adapter controls below.
No overlapping-doublet, Planck/stimulated-source or native history equivalence is claimed.

## Frozen finite execution

Use BLAS/OMP threads1. Primary run timeout180s; one fresh independent review
with at most6 off-grid cases. A diagnosed repair preserves original failure/raw
and does not replay successful cases. No new local or cosmological IVP.
No reuse count is promoted into new experiment count.

1. Seven fixed-block owner controls (r/r0,b/b0):
(1,1),(0,1),(.5,1),(2,1),(1,0),(1,.9),(1,1.1).
For each compare rank-one lift, direct2x2 Schur and independent full313 solve.
Baseline reinsertion, original stored-state residual and immutable-block identities
are separately recorded. Dense solve is an algebraic reference, not native replay.
2. Twelve residual/solution JVP directions: at baseline, half-line and blue-plus,
state-only, r-only, b-only and mixed directions; compare independent complex-step
assembled full algebra. State direction scales to native unknowns and parameter
directions to r0,b0. Use step1e-30; distinguish residual and solved-state JVP.
3. Nine angular-owner sources: actual saved scalar state with isotropic, triaxial
S=diag(-.4,.1,.3) and fixed rotation; constructed tau=.3,2,30 with isotropic/triaxial
S. Constructed opacity controls do not represent extra native snapshots.
4. Up to12 explicit invalid-input/duplicate-owner/conditioning domain checks and
two deliberate sign/normalization mutations of the source ledger or owner pair.
Mutations must fail the frozen physical invariant/owner contract.
5. Three figures: actual source partition; affine population/event response for
three r/r0={.5,1,2} tracks over61 b/b0 samples on[.8,1.2] (183 rank-one plot samples);
native/angular number-energy-tensor injection from the already saved source rows.
No new angular grid scan or historic ANGULAR01/LINE01 campaign replay.

## Acceptance before run

- Exact raw hashes for immutable inputs and byte-identical donor.
- Native source reconstruction and unmodified-block identity within64eps
times summed native term scale (byte identity for unchanged copied arrays).
- Baseline net source against70digit source-decimal reference: absolute error
<=5e-13 times the sum of absolute departure contributions. No tiny-net normalization.
- Rank-one/full and Schur/full state max error <=5e-10 in componentwise scale
max(abs(reference_i),1e-30); report real and virtual maxima separately.
Full equation componentwise backward residual <=5e-12 using abs(M)abs(z)+abs(s)
plus machine-tiny. Stored snapshot's residual is measured, not required exact zero.
- Residual/solution JVP scaled discrepancy<=5e-9; also report absolute and scaled
errors. Terms zero by construction use absolute64eps mixed scale, not division by0.
- Number/internal-radiation ledger closes within64eps exchange scale; tracefree
tensor within64eps tensor scale. Angular rotation covariance <=5e-10 of scalar
normalization. Existing quadrature tolerance is not re-certified by this unit.
- Native thick source truncation and propagated bound keep logarithms. Numerical
rounding/source constant/finite-opacity errors remain distinct.
- Signed emission/absorption allowed; physical population/occupation positivity
is assessed within the declared controls without clipping or normalization.
- No performance speedup target. Report actual counts and wall time, not a universal gain.

## Research context, progress and delivery

Latest REC128/119 and REI220 pins unchanged. New REI221
6daf382ee698835e7a141378c232d1d97c1c5cf1 contains separately reported ANGTHERM01
ten trajectories, exact finite221→41 reduction and a remaining Li threshold angular
accuracy obligation. Read reported evidence; do not repeat or add its run counts.
PR220 compact33 remains a downstream population donor, not an excited2p/Tvv substitute.

A source/theory/contract checkpoint; B code/raw results; C single review, actual
PNG inspection, report, DAG/handoff. Git draft publication and dual backups at each.
Final whole-byte verification is separate from upload ACK; no invented all-conversation
survey or global physical completion percentage.

Physical HOLD; REC_U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global_convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.
Historical first-failed REI raw local-only. Conditional21population/effective line
does not complete all-nuclide nuclear/thermal/spectral/metric closure.

