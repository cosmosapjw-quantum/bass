# BASS_B3B_FINITE_LINE_EXCHANGE_20261024 — frozen implementation contract

## Admission and ownership

This is the next opt-in research unit above BASS PR185 at
c2e6f1f80417e62c95e607c80115e89de1925ca9. The current REC pin is
c7cdabd871ab2ef6f722594ff063b8ce8550e6b4 (PR131). Its existing LINE01
thick_local_step is the actual finite atomic-population owner; its blob remains
5ac2a3107b80710504e63705ff16562131b5d1cf. No new receiver is inferred from the
PR131 input-admission report. REC-HISTORY-02R is active in another conversation.

The central fixed authority and latest unchanged AGENTS are recorded in
provenance/CENSUS.json. Use the user's explicit physmath 1.0.0 full R1–R10 and
C1–C10 request; installed cloud 1.3.0 selector defaults do not replace it.

Independent theory review is PASS_SCOPED in reviews/THEORY_REVIEW.md. The actual
Wolfram response in evidence/WOLFRAM_CURRENT_RESPONSE.json returns 19 zero
residual groups. Implementation admission requires actual execution and a
separate independent code/physics/figure review.

## Objects and physical scope

Implement integrated gross counts for a frozen, non-inverted two-level LINE01
source, plus a finite BASS state/packet transaction only when f_plus == 0.
N,H,S,f are frozen during the local proper-time source step; geometry does not
advance. Required domain: N,H>0; f>=0; 0<=x0<g/(g+1); symmetric STF S with
1+lambda_min(S)>0; source-owned whole-path thick gate
t_min/q_max >= log(1+1e8). Use actual source owner validation and map unchanged.

The physical population stock is n_u=N*x and n_l=N*(1-x); the energy partner is
atomic excitation E*n_u. Thermal recoil, ionization and electron yields are zero
in this source model. f_plus is a prescribed incoming boundary occupation. It is
not a finite photon reservoir. General-f integrated gross counts are admitted as
a prescribed-boundary ledger; closed finite-photon-stock absorption is outside
this implementation. An attempted f>0 state commit must fail without mutation.

Canonical origin: matter rest frame, proper time in seconds and proper volume
in m^3. Use explicit frame="rest" and clock="proper_time_dt_dV_invariant".
Source owner mode is standalone_detached, native_line_owner_active=False.
Keep owner, card/population scope, epoch and physical transfer ID explicit.
A physical transfer key (owner, epoch, transfer_id) cannot be charged twice,
including after changing representation labels. Require matching source and
state stock epochs before committing. Reject a mismatched card, source owner,
scope, frame, clock, scale, source H/S, or stale stock. Do not use digests or
new security machinery as a substitute for these physical checks.

## Gross-count algorithm

Let b=g+1, F=1+b*f, xe=g*f/F, de=g/F, k_line=8*pi*H/(N*lambda^3),
eta=k_line*F/de, omega=eta*dt, y0=x0-xe, z0=-b*y0/de.
Call actual thick_local_step at this omega and retain its stable dx/net packet.

For non-LTE use v=-u from the owner. At exact LTE (y0==0), use v=omega:
the upstream u=0 is a net-only shortcut. Set a=-expm1(-v), r=v-a.
For small v, compute r using its bounded alternating Taylor series
v^2*(1/2-v/6+v^2/24-...), with a next-term truncation bound.
For moderate v, v+expm1(-v) is suitable. Never max(0,...) or clip populations.

D_down = N*(1+f)/F * [x0*a + xe*r]
D_up   = N*g*f/F * [(1-x0)*a + (1-xe)*r]
D_net  = -N*dx, from the owner, not rounded gross subtraction.

At LTE, D_down=D_up=N*k_line*f*(1+f)*dt; net=0.
At f=0, D_up=0 and 0<=D_down<=N*x0.
At x0=0,f>0, D_down is O(dt^2) and must remain resolved for representable input.

Preserve owner population/net-energy/STF finite-opacity bounds and their
FLOAT_NOT_INTERVAL qualification. They do not establish a new gross-channel
finite-opacity relative certificate. This unit computes the thick model.

## Exact finite packet representation

Use 6 signed coordinate axes with base weight 1/15 each and 8 signed cube
corners divided by sqrt(3), with base weight 3/40 each. For each direction,
q_j=1+n_j.S.n_j, Delta n_j=D_net*A_j*q_j.
This positive degree-5 cubature exactly reproduces the quadratic thick model's
rest-frame number, zero flux and spatial stress I/3+2*S/15.
It does not determine higher spectral/angular structure or observer-changed
event K(u). The event measure and state measure remain separate.

Use actual BASS kinetic.py (blob1fef508f01479508e5489cf8a167d2aff8184a81) and
core.py (blob3e95a652715b346a47f097fde2131540237390a4), unchanged vendor copies.
With alpha_L=FixedScale.density_factor=kappa_grav*L^2:
k_j=E*n_j/(c*Pstar), m_j=0, Delta w_j=alpha_L*c*Pstar*Delta n_j.
These are finite state weights; do not apply event-rate state reweighting.

Delta rho_gamma=alpha_L*E*D_net, Delta rho_atomic=-Delta rho_gamma.
Delta p_gamma=Delta rho_gamma/3, Delta pi_gamma=Delta rho_gamma*2*S/15.
A finite state increment has L^2 scaling. An interval-average energy source has
kappa_grav*L^3/c scaling and integrating it over Delta tau=c*dt/L gives the same
increment. Source.pi always stores state stress, never PiRate_hat.

## Actual state transaction

Consume a concrete core.State, core.Source, atomic population stock and actual
photon packet stock. Check the photon sector rho/flux/p/pi against its packet
moments, with explicitly reported gross-scale floating tolerances. Atomic
sector must own at least alpha_L*E*n_u of excitation energy. It may include
additional caller-owned constant energy; preserve its pressure/pi in this
recoil-free source substep. Do not create another energy reservoir.

Check h=H*L/c and sigma=h*S (source contract S=sigma_phys/H).
Keep n,a,alpha,h,sigma fixed. Preserve all other sectors. Return copied updated
state, source and packet/population stocks; rejection must leave inputs intact.
A zero-photon stock uses an explicit vacuum branch; no artificial epsilon seed.
Zero weights are allowed in underlying packet moments but are not an admission
to the strict-positive CoupledPackets logarithmic IVP.

Update atomic n_u,n_l and BASS rho together with injected photons. Report
floating conservation residuals normalized to the physically relevant gross
scale. If a nonzero requested population or sector-energy increment is
unrepresentable (e.g. x1==x0 despite stable dx!=0), reject the state commit
explicitly; retain gross/net analytic results as a separate ledger.
No underflow-driven silent deletion, positivity clipping or renormalization.

After commit, state pressure/pi include the new photons. Return zero energy/
momentum transfer for this already-applied interval; do not double-integrate U/J.
The constraint residual before/after must agree to documented floating error
because total rho/flux and geometry are preserved. This does not assert the
initial state solved the constraints.

Use core's five/six-component symmetric/STF representation if needed to encode
analytic identities. Check actual packet tensor consistency on a gross scale;
do not physically project an inconsistent stress tensor.

## Required discriminating validation

Use unittest and bounded independent oracles, not the old campaign or a new
cosmological IVP. Cover:
- independent positive quadrature over v for the integrated original rates,
  ordinary emission, absorption start, near-LTE and exact LTE;
- tiny-v cancellation with a higher precision Decimal or exact series oracle;
- zero duration/empty upper stock, finite donor depletion, nonnegative counts;
- one full versus two half fixed-parameter map AND count composition;
- exact rational second/fourth angular identities and a rotated STF example;
- actual kinetic moments vs predicted state increments, vacuum and occupied
  photon stocks, conservation and unchanged constraint residual;
- correct L^2 finite conversion vs L^3 interval-average rate conversion;
- actual core.Source after commit has correct p/pi and zero already-applied U/J;
- invalid opacity/inversion/q, owner/card/scope/epoch/frame/clock/geometry,
  duplicate physical transfer, insufficient energy and f>0 commit refusal;
- tiny nonrepresentable population/energy advance is explicitly rejected.

One bounded current figure should show gross/net/LTE and finite emission
behavior with axes, units/normalization and actual output data. Keep source
fixtures synthetic and label them; the source code/cards/receiver are actual.

## Execution and completion

No new IVP, no old campaign replay, no recovered archive downloads.
Use lower-tier implementation after this frozen contract (central AGENTS).
New-unit prospective lightweight ceiling: 120 wall seconds across scientific
processes; implementation allocation60s, each process<=30s; reviewer allowance
<=30s; Wolfram call ceiling20s (actual kernel wall0.128027, CPU0.127434).
This is a new bounded work-unit guard, not a restored campaign remaining budget.

remaining_campaign_wall_seconds=null; remaining_campaign_cpu_seconds=null;
budget_reset=false. Historical34.1262904040002 is a partial old wall subtotal.
Prior B3a6.3684287650103215 wall/6.359076642999999 CPU are separate and unchanged.
Record every actual argv/cwd/exit, failures, repairs, measured wall and CPU.
Record orchestration/backup time separately from science or leave unmeasured.

C5–C8 complete only with actual outputs; C9 requires independent acceptance.
Publish only new lane on a new stacked Draft branch after fresh expected-SHA
checks. Each checkpoint's backup/provider ACK and publication identity are
distinct from scientific acceptance. No merge or production activation.

