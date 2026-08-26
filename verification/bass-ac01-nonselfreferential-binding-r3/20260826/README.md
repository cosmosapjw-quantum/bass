# BASS AC-01 non-self-referential binding successor — R3

This package repairs one observed P0 provenance-contract defect without changing
AC-01 implementation semantics.

The v3 work-unit required an in-commit `RECEIPT.json` to contain the SHA of the
same commit. Git commit identity depends on the referenced tree, and that tree
contains the receipt blob. Therefore changing the receipt changes the tree and
the resulting commit object. Ordinary Git cannot satisfy that circular contract.

R3 separates the two evidence layers:

1. **implementation commit** — exactly one commit from `d6a0b63fac09c3a6d0c9071206f0d51f01953341`; contains code,
   tests, policy, logs, diff firewall, and a pre-commit receipt that deliberately
   contains no final commit SHA;
2. **post-push attestation commit** — exactly one one-file commit on
   `agent/evidence/bass-ac-01-post-push-binding-20260826`, parented directly by the implementation commit. Its JSON
   binds the already-existing implementation SHA, tree, parent, receipt blob,
   and remote readback. It does not contain its own attestation commit SHA.

This is one new control for one observed failure class. It is not a new science
gate, does not alter byte-vs-content classification, and does not authorize PR,
merge, tag, runtime, Rust, solver, classifier, fitting, or authority promotion.
