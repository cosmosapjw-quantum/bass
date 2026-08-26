# Decision — one implementation commit plus one separate attestation commit

## Root cause

The prior contract conflated an **in-tree pre-commit receipt** with an
**out-of-tree post-commit completion binding**. A commit object refers to a tree;
the tree refers to every tracked receipt blob. Requiring that receipt to contain
the resulting commit SHA is circular.

## Chosen repair

- Keep the implementation branch at exactly one commit from `d6a0b63fac09c3a6d0c9071206f0d51f01953341`.
- Keep `RECEIPT.json` in that implementation commit, but forbid a `final_sha`
  member there.
- After ordinary push and remote readback, create one separate evidence branch
  whose parent is the implementation commit.
- Add exactly one file, `POST_PUSH_BINDING.json`, containing the implementation
  SHA and its evidence bindings.
- WU-004R resolves its review target from
  `POST_PUSH_BINDING.json.subject_sha`, then verifies the attestation parent,
  implementation remote ref, and receipt blob independently.

## Rejected alternatives

- Sentinel/fake SHA in the in-tree receipt: fabricated provenance.
- Amend-until-match or hash fixed-point search: not an ordinary or bounded Git
  workflow and not a credible authority mechanism.
- Second commit on the implementation branch: breaks the one-implementation-
  commit boundary and mixes code with post-hoc provenance.
- Git notes: technically possible, but less visible and less portable in the
  current GitHub/Codex workflow than a one-file evidence branch.
- Dropping final-SHA binding entirely: weakens fresh-review dependency identity.

## Scope

The already completed 7 RED tests, 7/7 GREEN tests, verifier self-test, and
identity-class semantics are accepted as predecessor execution evidence only
when their recorded SHA-256 values match and all GREEN checks are rerun under
this successor contract.
