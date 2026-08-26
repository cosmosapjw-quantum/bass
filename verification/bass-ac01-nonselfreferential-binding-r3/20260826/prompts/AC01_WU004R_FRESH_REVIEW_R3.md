# WU-004R R3 fresh-context read-only review

Use only repository bytes, the R3 contract, and remote refs. Do not inherit the
implementer's conclusion.

Inputs:

- base SHA `d6a0b63fac09c3a6d0c9071206f0d51f01953341`;
- implementation branch `agent/guard/bass-ac-01-artifact-identity-20260826`;
- attestation branch `agent/evidence/bass-ac-01-post-push-binding-20260826`;
- R3 contract and package manifest;
- raw RED/GREEN/diff-firewall evidence.

Procedure:

1. Resolve both remote refs once and record exact SHAs.
2. Verify the attestation commit's sole parent is the implementation SHA.
3. Verify the attestation delta contains exactly
   `verification/bass-ac-01/20260826/POST_PUSH_BINDING.json`.
4. Read `subject_sha` from that file and require it equals both the attestation
   parent and implementation remote ref.
5. Require implementation parent `d6a0b63fac09c3a6d0c9071206f0d51f01953341`, commit count one, exact commit
   message, and allowed paths only.
6. Verify the in-commit `RECEIPT.json` has no `final_sha` and matches its blob and
   SHA-256 bindings.
7. Rerun targeted, negative, self-test, tests/verification, precommit receipt,
   allowed-diff, and post-push binding checks.
8. Confirm no scientific/runtime/Rust/solver/tolerance/golden/sealed bytes moved.
9. Do not modify any file.

Allowed verdicts:

- `PASS_AC01_FRESH_REVIEW`
- `FAIL_P0_P1`
- `BLOCKED_BY_MISSING_EVIDENCE`

A PASS report must state the exact implementation SHA and attestation SHA.
Downstream work uses the implementation SHA from
`POST_PUSH_BINDING.json.subject_sha`, not a value embedded in the implementation
commit's receipt.
