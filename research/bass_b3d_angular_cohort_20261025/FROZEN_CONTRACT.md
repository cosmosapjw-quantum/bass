# BASS_B3D_ANGULAR_COHORT_20261025 — frozen contract v1

## R1/C1: scope and reuse

Use the explicitly selected physmath-research-loop **1.0.0**. Central fixed
authority is rei_bianchi 0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17, current
observation 9600a605f6380bc2262d0cfce5ff00290e594a5a. AGENTS blob
429a5a13ee75b1222bc50627f8d5973d01dd21c4 and fixed/current BASS handoff blob
55c86aabe97702d6b64631c5f24a9d1a9563820e are unchanged. BASS parent PR187 is
Draft/open/unmerged, HEAD 0a088e1f8fca6618107525e687f930406ca32d18. No merge
or production activation. Root alone controls remote publication.

Current REC135 52226bb8d3ac99e7de2bd7934ab30e6fb3f257fe preserves a prior
BASS_B3C_BOUNDED_F0_BACKGROUND_20261024 handoff/admission. It reports scoped
time-splitting completion, 12 IVPs, 6 focused tests and 27 gates. Those are
owner-reported historical results, not current re-executions. The selected
3 NPZ and 6 source modules remain byte-identical. No old archive/NPZ download
or campaign replay. The prepared B3c1 alternative is superseded before its
first numerical execution; retain its theory, code and actual S0 upload ACKs.

The new contribution is **one photon cohort's continuum angular moments versus
the actual positive 14-ray rule after a prescribed diagonal redshift**. A
positive degree-7 26-ray candidate is evaluated on the same cohort. This isolates
angular discretization from time-splitting error. It does not implement a new
IVP, integrate an atomic source, reconstruct an actual REC trajectory, or close
native finite absorption. The current LINE01 finite receiver trace, clock,
finite donor and exclusive native atomic owner contract remains open.

## R2/R3: physical normalization and fixed labels

Metric (-,+,+,+). Use actual unchanged H_LYA_EFFECTIVE_2P energy
E_b=10.198714553953742 eV converted by the owner EV_J, with c explicit.
Pstar=E_b/c; n_b=1 m^-3 is a unit test cohort density. L=1 m is a fixed units
reference, not a fitted cosmological length. alphaL=8*pi*G*L^2/c^4 uses the
unchanged core.FixedScale. The hydrogen rest tetrad is also the normal tetrad.
There is no tilt, frame boost, polarization, recoil, line width or new bath.

Birth direction n labels the same photons throughout. Let S_b be symmetric
trace-free, q(n)=1+n^T S_b n>0, and normalized sphere average
<g>=(4*pi)^-1 integral g dOmega. Then <q>=1. The birth number measure is
n_b*q(n)*dOmega/(4*pi). All photons have energy E_b and represent the outgoing
side E_b-0 of the unresolved line, already counted as a cohort. No dR event
rate or Source/U/J/PiRate is created or transformed in this unit.

Freeze isotropic logarithmic expansion a=2/5 and B=diag(3/10,-1/10,-1/5).
For eta in [0,1], C=exp(-eta*B), R=exp(-a)*C, D=det(R)=exp(-3*a).
The cohort map is p=(E_b/c)*R*n; its physical number measure is multiplied by
D only. The optional parameter chi in R(chi)=exp[-chi*(a*I+eta*B)] specifies
an algebraic redshift path, not proper time or tau. No event duration is needed.
Every a+eta*b_i>=1/5, so photon energies decrease along chi and the outgoing
support never feeds the blue face in this prescribed model.

Use birth labels in all angular integrals: no extra solid-angle Jacobian in
this parameterization. If changing to current n'=R*n/|R*n|, the correct
Jacobian is dOmega'=det(R)/|R*n|^3*dOmega; document it without double-counting.
This cosmological density dilution is neither a Lorentz state Doppler weight
nor an invariant event-rate clock transformation.

Let rho_star=alphaL*E_b*n_b*D*exp(-a), a positive common dimensionless scale.
The normalized energy and pressure are

    F = <q(n)*|C*n|>,
    P = C * <q(n)*n*n^T/|C*n|> * C^T,
    pi = P - I*F/3.

Physical number density is n_b*D; normalized stress-energy has T00=F,
T0i=0 by antipodal symmetry, Tij=Pij. Physical SI T is E_b*n_b*D*exp(-a)
times this tensor; BASS tensor is rho_star times it. trace(P)=F identically.
At eta=0, F=1 and P=I/3+2*S_b/15, including anisotropic birth emission.

## R4/R5: exact quadrature result and constructive alternative

The actual parent finite_exchange.cubature14 supplies six axis rays with
weight1/15 and eight cube corners with weight3/40. Preserve that code unchanged.
It is exact for all sphere polynomials of total degree<=5. With Delta=Q14-<.>,

    Delta(nx^6)=4/315,
    Delta(nx^4*ny^2)=-2/315,
    Delta(nx^2*ny^2*nz^2)=4/315.

Degree-5 birth accuracy does not imply exact nonlinear redshifted moments.
For diagonal trace-free B and fixed symmetric trace-free S, the generic leading
errors in normalized quantities are

    F14-F = -eta^2/35 * sum_i S_ii*b_i^2 + O(eta^3),
    P14_ii-P_ii = eta*(2/105)*(3*S_ii*b_i-tr(S*B)) + O(eta^2),
    P14_ij-P_ij = -eta*(4/105)*(b_i+b_j)*S_ij + O(eta^2), i!=j.

For S=0, energy begins at cubic and pressure at quadratic order, unless a
specific coefficient cancels. Exact coefficients will be recorded in theory
and Wolfram evidence before numerical runs. The statement concerns this
finite quadrature, not a strong physical no-go for collisionless reduction.

Construct Q26 from six axes w=1/21, twelve face diagonals w=4/105 and eight
cube corners w=9/280. Verify degree<=7 exactness independently in Wolfram and
the scoped numerical checks. This rule is a candidate on the selected cohort;
it is not identified with the actual REC35x26 inventory, nor installed into
production. Report its errors without presupposing a uniform 2e-8 pass.

## R7/C3: fixtures, references and frozen acceptance

Primary source matrices: ANISO S_b=B/2=diag(.15,-.05,-.10), and ISO S_b=0.
For both, eta=[0,1/128,1/64,1/32,1/16,1/4,1]. The words ISO/ANISO refer to
the birth angular source; the transport is anisotropic when eta>0.
The minimum q over these primary spheres is .9. No random fixtures.

Reference: normalized full-sphere Gauss-Legendre mu in[-1,1] and uniform
azimuth phi in[0,2*pi), Nmu=[16,32,64], Nphi=2*Nmu. Positive weights. Do not
reuse the 14-rule to produce the continuum reference. Independently cross-check
the aligned worst-eta fixture with first-octant tensor-product Gauss-Legendre
32x32 over mu in[0,1], phi in[0,pi/2]. This octant check is appropriate only
for diagonal S,C. The final continuum numerical reference is64x128.

An analytic quadrature truncation bound is also required. Put
z=n^T(C^T*C/a0-I)n, a0=(rmax^2+rmin^2)/2,
delta=(rmax^2-rmin^2)/(rmax^2+rmin^2)<=tanh(1/2)<1, where r here denotes
eigenvalues of C. Use K=40 binomial expansions of sqrt(1+z) and its inverse.
For p=+/-1/2, remainder <= |binomial(p,K+1)|*delta^(K+1)/(1-delta).
The64x128 product rule exactly integrates the polynomial terms of total
degree<=2K+4=84 in exact arithmetic. Therefore ideal-node errors are bounded
by 2*sqrt(a0)*tail_sqrt for F, and
2*rmax^2/sqrt(a0)*tail_inverse for each P component. Report these bounds
separately from floating node/summation error; no interval certification claim.

Independent closed-form oracle: S=0, C=diag(exp(-3/20),exp(-3/20),exp(3/10)).
Writing u=Cxx, v=Czz and d=v^2-u^2>0,

    F = [v + (u^2/sqrt(d))*asinh(sqrt(d)/u)]/2,
    Pzz = v^2/(2*d)*[v-(u^2/sqrt(d))*asinh(sqrt(d)/u)],
    Pxx=Pyy=(F-Pzz)/2.

This oracle adds no IVP. Include its exact isotropic limit separately.

Rotation fixture at eta=1 uses the exact proper rotation
O=[[3/5,-4/5,0],[4/5,3/5,0],[0,0,1]]. Rotate S and C by O.
When the physical system and quadrature rays co-rotate, require tensor
covariance. Separately keep the14/26 rays fixed while rotating the physical
pair and report orientation sensitivity. The latter is quadrature error and
must not be described as failure of coordinate/Lorentz covariance.

For approximate X and continuum Y, frozen errors are
abs(F_X-F_Y)/F_Y, maxabs(P_X-P_Y)/F_Y,
maxabs(pi_X-pi_Y)/F_Y, and maxabs(T_X-T_Y)/F_Y.
Never divide by a small individual stress component or rest-mass energy.

Numerical admission gates:

1. Rule weights positive, normalized; birth F/P identities, flux0,
   trace(P)=F, actual kinetic tensor mapping and co-rotation agree within
   512*machine_epsilon on the common normalized energy scale. Source/copy
   identity must remain exact; no change to parent/vendor code.
2. Reference32/64, octant/full-sphere and analytic-axial differences <=2e-12
   on normalized energy scale. Report16/32 too without fitting noise orders.
   Every selected K40 ideal-node truncation bound must be <=2e-12.
3. Actual physical packet check uses core.FixedScale(L=1), Pstar=E_b/c,
   birth k=n, w=alphaL*E_b*n_b*A*q; drift k=R*n,w=D*w,mass0.
   Compare unchanged kinetic.moments/tensor to direct rule formulas and
   physical number n_b*D. No source transaction and no duplicated event energy.
4. Leading14 coefficients at eta=1/128 agree within5% in max-component norm
   relative to the nonzero exact leading coefficient. Use direct saved
   differences and exact rational theory, not fitted coefficients. For S=0
   include its nonzero exact cubic energy/quadratic pressure coefficients.
5. Report p=log2(error(2eta)/error(eta)) for adjacent small eta. Admit orders
   only when BOTH normalized errors exceed4096*machine_epsilon; otherwise
   null/ROUNDING_UNRESOLVED. Finest resolved14 triplet must demonstrate
   ANISO energy[1.8,2.2], ANISO pressure[.8,1.2], ISO energy[2.8,3.2],
   ISO pressure[1.8,2.2]. Q26 orders are reported diagnostically unless their
   exact nonzero coefficient and resolved range establish a stronger claim.
6. The2e-8 angular accuracy benchmark is a **reported comparison**, not a
   requirement that14 or26 pass. Retain every failing case. Success of this
   research unit means valid error quantification and a controlled reference,
   not adjusting a fixture, tolerance or grid to hide a14-rule error.
7. Reject nonfinite/nonreal input, non-STF S, nonpositive q, or nonpositive
   transport eigenvalues in the bounded scientific interface. Unsupported
   native incident trace/atomic source is outside this interface. No clipping.

## C4–C10: implementation, resource and delivery

Lower-tier coding agent owns new lane code/tests/vendor/results only. Copy
the actual parent finite_exchange.py and required unchanged dependencies,
including actual core/kinetic, and record exact parent/copied identities.
Implement a small angular cohort module, focused scientific tests, metered
runner and JSON/CSV/PNG outputs. No temporal solver or old campaign calls.
Use vectorized quadrature; keep float64 and package versions explicit. Plot
14/26 angular errors with the2e-8 benchmark, exact leading-error ratios and
fixed-grid orientation sensitivity. Zero values remain zero in data; no fake
floor in scientific rows. Mask true zeros only for logarithmic plotting and
label masks. Draw original numerical outputs, not a generated illustration.

One focused new test process, one bounded cohort/reference sweep, and one
summary/plot process suffice unless an observed failure justifies a targeted
repair. Preserve exact argv/cwd/UTC/stdout/stderr/exit/environment/source hashes
and wall/CPU for every scientific child. Run one thread, per process at most
30 wall/20 CPU seconds; lower-tier cumulative60wall/40CPU, reviewer20wall/10CPU,
symbolic20wall/10CPU. Combined current-turn scientific guard120wall/60CPU
includes superseded B3c1 Wolfram0.082713wall/0.082161CPU. Historical remaining
wall/CPU=null and budget_reset=false. Prior34.1262904040002 seconds is a
partial subtotal, not a balance. Prior B3b2 and owner-reported B3c resources
remain separate. New IVPs=0, old campaign replay=0, old archive/NPZ downloads=0.

R6 independent contract review precedes numeric execution. Root preserves S0
on Git/Drive/Dropbox before issuing execution ACK. C9 reads actual code/raw
results/figure before scientific admission. Different-model scientific review
remains NOT_RUN unless actually performed; a lower-tier implementer is not an
independent different-model scientific reviewer. Each substantive failure gets
one targeted repair and affected verification, with unchanged scientific gates.

Publish only this scoped new unit on a new stacked Draft branch using an actual
fresh expected SHA and force=false. Current user authorization covers this new
unit; do not retry the previously rejected old B3c publication or claim its
NO_ACK as a current successful Git result. S0/S1/S2 are cumulative receipts,
not20 separate uploads. Keep science, Git blob readback, provider upload ACK
and remote full restore status separate. Full remote archive restore NOT_RUN.

Overall BASS physical completion remains null. B1 exact old pytest argv/cwd
UNKNOWN, B2 selected V/VIII tau[0,.8] gate2e-8, B3a event-clock distinction,
B3b2 bootstrap qualification and inverse-repair history remain intact.
B3c is now prior owner-reported PASS_SCOPED; B3d claims only the selected
angular domain. Native finite absorption, calibrated REC coupling, B4 restart
and B5 general-domain validation remain separate open obligations.
