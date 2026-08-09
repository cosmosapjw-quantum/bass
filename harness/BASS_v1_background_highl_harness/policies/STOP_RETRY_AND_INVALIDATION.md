# Stop, retry, and invalidation policy

- Run one DAG node or one coherent change-set at a time.
- A failure class receives at most two repair iterations at the same node.
- A third occurrence becomes `BLOCKED`; preserve the negative result and ask the user.
- A timeout, unavailable tool, spend/permission limit, or runtime interruption is a
  blocker/environment result, never a scientific failure or pass.
- A fix after audit re-enters at the first affected gate; it may not skip directly to
  packaging or the next node.
- A live validator governing-fingerprint mismatch is a stale PASS, not a repairable
  warning. Preview its transitive impact with
  `python3 tools/invalidate_state.py --from-node NODE --reason GOVERNING_BYTES_CHANGED`,
  where the reason is an uppercase machine code, then use `--apply` only when the exact
  affected nodes are correct. Old receipts remain preserved as prior-receipt evidence;
  active pointers are cleared. An applied invalidation enters the machine-only
  `INVALIDATION_REMEDIATION` phase, binds the current node to its exact invalidation code,
  and revokes every read/write/build/execute/install/oracle/remote/release authorization.
  Restoring a capability requires returning through its normal prerequisite and explicit
  authorization path; remediation itself grants none.
- Plots are mandatory only for numerical, convergence, observable, and performance claims
  where visual residual structure adds evidence. They are not mandatory for schemas,
  provenance, packaging, or documentation-only nodes.
- Stop for unresolved owner choices, baseline/tolerance/convention changes, new production
  dependencies, external writes, destructive actions, or material scope expansion.
