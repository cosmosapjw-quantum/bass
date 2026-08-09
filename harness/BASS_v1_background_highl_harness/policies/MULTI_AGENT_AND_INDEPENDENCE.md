# Multi-agent and independence policy

One coordinator maps shared context, registers assignments, owns canonical state, and
deduplicates findings by claim/obligation plus evidence fingerprint. Other agents receive
a pinned Tier-0 contract and only their bounded assignment slice.

For a blocking gate, producer and reviewer identities must differ. Blind independent lanes
share the statement, conventions, assumptions, domains, test vectors, and tolerances but
not sibling derivations/results before submission. Shared code generation, copied formulae,
or the same oracle implementation do not constitute independent derivation.

Parallel agents write only isolated result paths. A changed implementation invalidates
prior review. CAS lanes use the same `CAS_CONTRACT` and report branch/domain assumptions;
agreement with misaligned assumptions is not cross-validation.

The machine-checkable minimum is inequality of `run_id`, `assignment_id`, and `lane_id`,
plus a review attestation over the exact producer-evidence hash/fingerprint and governing
fingerprint. This does not by itself prove methodological independence; the attestation
must disclose shared formulas, generated bodies, code, and oracle lineage.

For H0/H1, the blocking reviewer must independently rerun the declared command plan over
the exact producer-evidence hash and confirm that the static log's pre/post governing
snapshots equal the reviewed current bytes. Merely rereading a producer-authored PASS log
is not an independent review. The review attestation must hash-bind a distinct
`H0_REVIEW_STATIC_CHECKS.json` or `H1_REVIEW_STATIC_CHECKS.json`; reuse of the producer
static-log hash is rejected.

Both producer and reviewer logs must match the same immutable shell-free command plan,
including exact argv/cwd and plan fingerprint, and must satisfy the command-specific
semantic output oracles. A distinct hand-authored log that merely repeats the expected
IDs, PASS booleans, or `/bin/true` commands is rejected. This is an integrity control over
the packaged evidence graph; it does not claim resistance to an attacker who can replace
the validator and every governed byte and then obtain a new trusted review.
