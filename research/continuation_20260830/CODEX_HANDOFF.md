# BASS — exact telemetry patch and corrected physical-route continuation

## Existing work is retained

Remote base is PR63 `2aaad1d72064ddeb60b27a0ec15536d0a2ec6a28`.
Source-probe evidence commit `148d590bd45ebcc5e4f2ac8a778c30d26d5f9f31`
and schema/native RED commit `d3df4ceb140a9810b0d5219e0e9e748c388a977d`
are USER-REPORTED LOCAL, not remotely imported here. Preserve their worktree.
Use a new linked worktree at d3df if available and cherry-pick this delivery
commit (ordinary non-force operation); its added research paths do not overlap
the old work. If absent, start from this delivery commit and fetch/import only
the durable missing local evidence when available. Never rerun P1–P5 for reassurance.
Do not claim those unpublished commits were tested or pushed here.

## Immediate local action: BASS-LOCAL-01_NATIVE_TELEMETRY_PARITY

Run verify_payload.py once before edits. The exact telemetry source patch is
already written and its actual numerical geometry prefix was compiled/tested.
Apply it in the new linked worktree, not the canonical checkout:

```sh
python research/continuation_20260830/apply_telemetry.py --repo "$PWD"
python research/continuation_20260830/check_geometry_core.py --repo "$PWD" \
  --out "$(mktemp -u -d /tmp/bass-geometry-check.XXXXXX)"
```

Then compile the actual repository native crate once and exercise successful
`transport_characteristic_profile` results with the real carrier/PyO3 wrappers.
The sandbox core test deliberately excluded those wrappers, so do not count it
as a full native proof. Add an actual owner test with no split, nested split,
several root panels, the existing bounded failure and a geometry-receipt test.
Do not rebuild or rerun unrelated scalar/thermo campaigns.

Counter meaning is frozen:
- `internal_bisection_count`: total actual split events in the successful call;
- `max_internal_bisection_depth`: max accepted leaf depth;
- `accepted_subinterval_count = input substeps + internal_bisection_count`.
The existing arithmetic, background-call order and accepted intervals are
unchanged. Counter overflow is typed, never saturated/fabricated. Failed calls
remain errors; do not emit fabricated successful geometry receipts.

Old donor blob: da6fade06f717ab938b0ec4c712ab239e78c998a.
New donor blob: e4d0f9c44fc26740d3a1cad6938b522fe514ae37.
This is an AUTHORIZED instrumentation edit and source-owner rebind. Update only
consumers of this source identity; do not rewrite historical evidence hashes.

## Correction that supersedes the unsafe PR63 path

Do NOT execute uncompensated K/2-C/2-Gphysical-C/2-K/2. Its first-order generator
is A+C+K, not the physical A+C. The earlier P4 authority text is superseded by
the subsequent mathematical counterexample, not merely weakened. Keep old
contracts/evidence as historical records, with this explicit supersession.

For the next bounded native route, use the EXISTING physical geometric and
collision generators directly. A Kato coordinate acceleration is a separate
candidate requiring y=U z, Udot=K U, zdot=U^-1(L-K)U z AND its transformed cone.
The dephasing/Bloch research toy shipped here is not Thomson physics.

A positive mixing remap is generally not exactly positively reversible. Test
reversal of the geometric characteristic on a replayed partition, not of a
dissipative full remap/collision. Row sums are not weighted conservation.
`nextDown(computed dot)` is not a rigorous bound on exact dot or independent
stencil suitability; bound rounding/normalization/departure uncertainty and
bind source/target screens and actual time/background. Do not invent q1/q3
abscissae from names. Fixed-rate second order does not establish uniform stiff
order or AP; test time, angular, and stiff limits separately.

## Same run after native telemetry passes

BASS-LOCAL-02: assemble a source-owned frozen physical A+C action on a
nondegenerate declared small grid and compare actual native state arrays with
an independently assembled dense reference; keep scalar/raw proof unchanged.
This yields a SCOPED_FROZEN_PHYSICAL_OPERATOR_PROOF, not full RF04.

BASS-LOCAL-03: use the research algebra original-residual and adjoint checks
when comparing candidate linear action backends. VigilODE is an optional
source for phi/Krylov workspace comparisons, not a prerequisite or a new solver
replacement. A linear backward error cannot certify the physical output.

Full polarized time-dependent trajectory may proceed only with explicit
physical remap/measure/frame/time representation supplied by current authority.
If missing, return the concrete measured insufficiency; do not create another
contract/audit loop or silently choose a stencil/closure. No P1–P5 rerun is
required just because their valid outcome was nonunique.

## Changed-scope proof and delivery

Local allowlist includes the donor, directly affected real tests, native kinetic
and adapter/registration owners, bianchi.kinetic/backend_policy, RF04 receipts
and source-binding records. No Cargo/version/equation/tolerance change is
needed for telemetry. No arbitrary commit count may prevent final evidence.
Use one PHYS-MATH and one PHYS-MATH-CODE review at the changed scientific
boundary, repair only reproduced P0/P1 issues, and end the loop. Ordinary push
one stacked draft implementation PR against the delivery branch, exact remote
readback, no merge/ready. No scalar reassurance, timing, GPU, Wolfram or RF05.
Current ceiling: NO_PASS_RF04; PASS_RF04_SCALAR_RAW_SLICE_PROOF remains scoped.
