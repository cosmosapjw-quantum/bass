# BASS durable orchestration/control-plane handoff

## Prepared boundary

The recovery payload is durably sealed at commit
`9a8f35ff107f4eb8053477bff2b9c8c77633b43a`, tree
`95233a394939d6a48bdc8b59fee199ffae65cb10`, with sole parent
`c9cd8ecb8765649ace77ea8f22890ff4c24153eb`. This follow-up is a direct-child receipt
carrier and next-stage preparation only.

`CONTROL_PLANE_STATUS: PREPARED_NOT_STARTED`

`CONTROL_PLANE_IMPLEMENTATION_AUTHORIZED: NO`

## Why a separate control plane is required

The surviving materials occupy different authority lanes and must not be overlaid:

1. exact remote Git/recovery receipts;
2. the exact low-ell audit and acceptance contract;
3. a background/high-ell harness-only lane whose historical live node is OD0 BLOCKED;
4. a partially recovered Rust/Python overlay;
5. a sanitized reconstructed source/report snapshot;
6. process protocols, audit profiles, toolchains, and symbolic dependencies supplied out
   of band.

The control plane must orchestrate these lanes without promoting any one of them into a
solver, scientific result, or A0B authority.

## Required base and branch rule

The next stage must:

1. fetch `agent/recovery/runtime-interruption-20260811-inventory`;
2. resolve and record its final fast-forward tip after this receipt is published;
3. prove that sealed commit `9a8f35ff…` is its direct parent;
4. create a new isolated branch from that final receipt-carrier tip;
5. never use `agent/route-a-a0`, `agent/route-a-a0-v2`, or either quarantine tree as the
   control-plane branch base.

Suggested next branch: `agent/control-plane/recovery-authority-v1`.

## CP0 — first separately authorized stage

CP0 is limited to recovery-authority intake and control-plane design. Its required outputs
are:

- an authority registry that preserves the existing status taxonomy;
- an immutable input-lock reader for `NEXT_STAGE_INPUT_LOCK.yaml`;
- explicit action-authority fields for read, write, build, execute, install, external
  oracle, GitHub write, merge, A0 mutation, A0B, A1, and Task 10;
- receipt schemas that bind action, input tree, result artifacts, reviewer evidence, and
  invalidation dependencies;
- a DAG/state transition design with fail-closed stale-receipt handling;
- a recovery/checkpoint budget for long-running work;
- a validator and negative-test plan;
- a design-review receipt.

CP0 must not create or modify solver code. CP0 completion authorizes no later node by
itself.

## Evidence precedence and conflict policy

Use the precedence list in `NEXT_STAGE_INPUT_LOCK.yaml`. If prose, machine state, transcript,
archive claims, or branch history disagree, stop at the strongest durable non-conflicting
boundary. No lower-precedence source may weaken a higher-precedence prohibition.

The legacy automation kit's PATCH80R/81R narrative is process material only. The
background/high-ell harness H0/H1 receipts remain valid only in their narrow historical
lane. Neither lane supplies current solver completion or control-plane authorization.
The adaptive development/executor prompts are advisory workflow references; their
immediate patch, execution, and plot requirements are inactive while current Git receipts
and machine-readable authority locks prohibit those actions.

## Entry checks for CP0

- remote branch tip equals the explicitly recorded handoff base;
- `git fsck --full --strict` exits 0;
- `SHA256SUMS` verifies every row;
- `manifest.json`, `HANDOFF_CAPSULE.yaml`, `RECOVERY_STATE_LEDGER.yaml`,
  `NEXT_STAGE_INPUT_LOCK.yaml`, `REMOTE_IDENTITY_RECEIPT.json`, and
  `archive_security_scan.json` parse;
- all 16 input names, sizes, hashes, roles, and dispositions are present exactly once;
- protected tree OIDs for `harness/`, `manifests/`, legacy partial sources, and sanitized
  quarantine sources match this handoff;
- A0/A0B/A1/Task 10 authorization remains false;
- no recovered script, pickle, toolchain, xAct archive, or legacy runner is executed.

## Explicit non-goals

- no repeat of exhausted exact-object archaeology without a new Git-object source;
- no A0 candidate mutation or promotion;
- no A0B freeze;
- no A1 or Task 10 work;
- no scientific, numerical, plotting, fitting, or oracle execution;
- no dependency installation or toolchain sourcing;
- no PR, merge, tag, release, or public scientific claim.

## Next exact action

Owner reviews this packet and explicitly authorizes or revises CP0. Until then, stop at
`PREPARED_NOT_STARTED`.
