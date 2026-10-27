# Native saved-history inverse and finite Lyα return — execution contract

Owner: root Astra. Frozen 2026-10-27 (Asia/Seoul). This is the next selected
scientific unit after B3h F3, not a replay of its completed computation.

## Scope, sources, and authority

The user selected a full theory R1–R10 and coding C1–C10 loop, including current
branch/repository/backup synthesis, per-stage publication/backup accounting,
independent review, non-force expected-SHA publication, and a copyable handoff.
That explicit selection overrides the current skill's bare-invocation one-stage
default. The original central DAG remains 27/88 until an original node is
actually admitted. Branch-local alternative 29/88 and 32/88 counts are observations.

Base BASS F3: 29dcf5ab94ae8b84bf8e3f31dddb31ce719929b1.
Current central: 55202663275cd0607c968129b33de805d06f5d8b, retaining
5abe0d19df95db730e3e33bae0373c81ba37ce89 and CR_N5 after 12f6007a.
Latest central AGENTS blob: 429a5a13ee75b1222bc50627f8d5973d01dd21c4.
Before each node, re-read current HEAD, AGENTS identity, and parallel-work status;
record a compact observation and adapt only the affected unit if they change.
No new checkout/worktree. No modification of old B3g/B3h scientific artifacts.

Immutable REC source d6dbe39a4923439547c01695d9020ba39367ea90:
`data/pr05b2_source_history_v060.npz`, 35239470 bytes,
SHA256 d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1.
Exact original hydrogen.c SHA256
421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b.
Triple input packet SHA256
7d6e85bf2e759500d3e7d7249de5892bcc34ce7af77f08de10ae1607eacf19ef.
Lyman input packet SHA256
5a01a3dfab10f07450c828e0ca141a8dc69f40e713a57b71aae378c41e1ed8f3.
Input packets are in next_atomic_intake. Existing B3h S1 input and result bytes
are reused with their recorded identities. The original A2/F2 and 512 cohorts,
two earlier B3i RHS consumptions, old tests/consume/plot, and native solver runs
are retained without replay.

## Constructive inverse

Use bins 273 (primary), 272,267,268,269,309 (independent cross-bin diagnostics)
at native indices 5126 and 5127. All lie outside diffusion [100,180). Candidate
selection used only saved right-snapshot conditioning; right x1s, Gamma, and
tau are validation-only, never inversion inputs or fitted constants.

For each stored triple let D=fout-fin, B=favg-fin, r=B/D. Require D != 0,
1/2 < r < 1, and infer positive tau by a bracketed monotone inverse of

    F(tau) = 1/(1-exp(-tau)) - 1/tau.

Use stable expm1/series evaluation; F'(tau)=1/tau^2-
1/(4*sinh(tau/2)^2)>0. The original native code uses a different quadratic
branch at tau<=1e-6; selected inferred endpoints must remain above that
boundary. Do not silently clip an invalid triple or substitute an ideal formula
inside the native approximation branch.

Reconstruct native Gamma, TR, nH, H, and lambda from the original source,
table literals, constants, and native z operation order in the packet. Then

    x1s = 8*pi*H*tau / (Gamma*lambda^3*nH_cm3).
    yp = xr_p/x1s = 3*dout_Lya.
    ys_beta = dout_Lyb*exp(E32/TR).
    ys_gamma = dout_Lyg*exp(E42/TR).
    x2p = x1s*(yp + 3*exp(-E21/TR)).
    x2s = x1s*(ys_beta + exp(-E21/TR)).

Also derive ys from each virtual equilibrium where well conditioned:
feq=fin+D/(1-exp(-tau)), Cs=-Tvr_s, Cp=-Tvr_p,
ys_virtual=(Gamma*feq-Cp*yp)/Cs. Report cancellation/conditioning; do not
average bad bins into a seemingly accurate state. Reconstructed states are
numerical inverses of stored source outputs, not byte-identical original states.
Retain native-z and exact-real affine eta clocks as distinct source conventions.

Primary binary64 inverse and independent 70-digit reference must be separate
implementations. Report per-bin inverse sensitivity, root bracket, observed
cross-bin spread, and numerical rounding-model propagation. A rounding model
of 32 binary64 ulps for each stored/reconstructed trace may be used for a
diagnostic enclosure; explicitly label its assumption and do not call it an
end-to-end rigorous source error certificate. Exact-stored-input inverse error
and assumed forward-rounding uncertainty are separate quantities.

## New finite photon result and atomic storage diagnostic

On the same native scalar FLRW q=1 interval [5126,5127], use the previous S1
incoming-face tube, same reference volume V0, clock eta=eta0+i*h, and its
saved Nin/Uin. Use actual stored Lyα outgoing departure PL between the two
new endpoints. In the net spectrum j=dout_Lya_PL-din_retarded_PL, the native
Wien terms cancel. Split at the existing retarded interpolation breakpoint.

    Delta N0 = G integral exp(3u)*j(u) du
    Delta U0 = G*E21_J integral exp(4u)*j(u) du
    Nout0 = Nin0(saved) + Delta N0
    Uout0 = Uin0(saved) + Delta U0.

Evaluate net integrals directly, never by subtracting separately large
incoming/outgoing integrals. Use an analytic/stable PL-exponential primitive
and independent high-precision quadrature. Reuse saved high-precision incoming
strings where available. Transport the outgoing and net photon tensors with
the existing B3g operator and native R=exp(-h)I. This is new transport of a
new finite measure, not replay of the completed incoming consume.

Return photon T and finite energy-momentum exchange/four-force with different
names and units. Isotropic T=diag(U,U/3,U/3,U/3); its pressure is not a
spatial four-force. If a force density per proper time is reported, specify
the common-volume integral and elapsed proper time, and distinguish it from
the endpoint tensor. B3i consumption requires a completely owned selected
transaction; report actual invocation count and leave it uncalled if an owner
remains absent.

Compute per-V0 endpoint 1s,2s,2p stock and atomic internal energy with nH_ref
from the previous tube. The native code uses x1s=1-xe and QSS excited states;
do not silently assert exact species normalization including tiny excited
stocks. Derive the finite QSS storage defect: instantaneous algebraic channel
balance does not itself supply the endpoint change of 2s/2p inventory. Report
the Lyα required refill, the algebraic QSS complement, and the finite storage
defect as distinct terms. Do not invent a physical replenishment channel from
an unowned residual. Native direct recoil/heat/ionization owners are the source
model's zero terms, with that restricted model scope. Physical temporal,
eS/en/eE/geometry/total radii remain null.

## Acceptance, controls, resource limit, stopping rule

Frozen numerical targets (not physical accuracy radii):

- primary and cross-bin x1s relative agreement with known right state <=2e-10;
- each reconstructed bin agrees with primary x1s within 2e-10;
- primary vs 70-digit inverse relative error <=2e-10;
- beta/gamma and well-conditioned virtual ys agreement <=2e-10;
- source right Gamma/TR/nH/H port discrepancy <=2e-13 relative;
- direct net integral vs independent reference <=2e-11 on each net own scale;
- native scalar tensor transport identities <=2e-13 relative.

Use one targeted control invocation, one new inverse/net-result invocation,
and one new plot invocation. Tests must address source branch correspondence,
holdout/cross-bin state recovery, independent precision/conditioning, finite
integral/clock/split and tensor-force distinction; no general test suite replay.
Prepare code and execution freeze before running. Cumulative current-unit
child process guard: 30 CPU seconds, 180 wall seconds, 512 MiB target memory.
The guard is new work authorization, not a claim about historical remaining
budget. Record actual costs, commands, environment, and failures. Old known
costs are retained verbatim; old remaining budget and unknown overhead stay null.

Implementation is delegated to requested gpt-6.1-sol; actual runtime identity
is null unless independently observed. Root/theory Astra owns scientific
decisions and independent read-only review. At most one targeted repair is
authorized after a concrete finding; stop blind retries. No new native solver
campaign is authorized by this contract. Do not run before root acknowledges
the S0 source/contract checkpoint and double-provider backup receipt.

## Deliverables and publication

Allowed new scientific path:
`research/bass_b3h_native_history_inversion_20261027/` only, plus task-owned
assembly under next_assembly and deliverables. Proposed branch
`research/bass-b3h-history-inverse-20261027` starts at exact F3.
Preserve inputs, source formula excerpts, code, fresh raw data, new figure,
theory, independent review, admission, stage ledger, budget ledger, handoff.
Each R/C stage records original DAG 27/88 and the actual checkpoint commit and
Drive/Dropbox receipt that covers it; stages sharing one atomic checkpoint
are stated explicitly. Publication is expected-SHA and force=false. Central
updates are additive on latest HEAD, preserving concurrent CR_N5/B3h data.
Final source ZIP includes the source needed to reproduce this selected unit,
with local hash and real provider metadata ACKs separately identified.

ANISO continuum–finite14 difference 3.447529542803539e-5 stays distinct from
the approximately 1e-11 reconstruction residual and 2e-8 continuum numerical
budget. None is a physical eS/en/eE/geometry/total radius.
