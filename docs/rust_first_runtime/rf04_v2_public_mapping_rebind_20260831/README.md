# RF04 V2 Public-Mapping Rebind — R2

R2 corrects the initial v2 public mapping after a valid local fail-closed review found that the first package was structurally valid but not implementation-complete. It remains an authority and local-handoff package only: it changes no Rust/PyO3 production source, no frozen P1–P5 route decision, no final donor identity, and no scientific status.

## Status ceiling

- PASS_RF04_SCALAR_RAW_SLICE_PROOF is retained.
- LOCAL-01 is not passed by this package.
- LOCAL-02 is not run.
- NO_PASS_RF04 remains in force.

## R2 authority decisions

- The existing v2 identity symbol is contextual: rf04_typeii_polarized_execution_identity_v2(directions, weights, remap_plan).
- Its result must exactly equal the identity carried by trajectory and batch calls with the same validated context.
- native_payload_identity is the static value bass-rf04-polarized-v2-native-local01/v1. The exact wheel SHA-256 belongs only in immutable local evidence.
- Reject-mode carrier input uses binary64 1e-10. Geometry receipts have complete canonical byte codecs and a domain-separated hash chain.
- Batch has exactly two member status values: 0 success and 1 isolated typed failure. Common grid, plan, schema, and route failures remain whole-call typed exceptions.

## Authority boundary

- Base source state: PR #70 head 380ce6fe6aebe0c76c59c0d2a0f8707aac0ce14c, tree 0062a719173dc0c40dcc1202ab0d305f8fe2e2bb.
- Initial authority package: PR #71 first head a69b0516274648788e151046cc0233651e39e4b7, tree 20693644149adbb3a5f310e72fe6de435308bc4e.
- Final donor: Git blob 693e9fff0d44f2b8e40966ceb8da3c348d830bd4, SHA-256 f1f624d47b35208d339e6ea298f023d70012e54c80357973a65dc63c9491de6e.
- Imported v2 direct authority: commit a083f8c2f489364d7ad866dac2eeff03de24f2e2; direct manifest SHA-256 07a8baa8ad2b432b821a300ca2f3a47c2f0cf1f0d008082be8aa39fcb6a6dc4c.

## Package contents

- R2_AUTHORITY_AMENDMENT.json records the user-approved contractual decisions.
- V2_PUBLIC_MAPPING.json is the implementation-complete public mapping.
- LOCAL_IMPLEMENTATION_PROMPT_R2.md is the local Codex instruction.
- LOCAL_CODEX_HANDOFF_CONTRACT.json and LOCAL_CODEX_HANDOFF.md are exact contract/rendering pairs.
- validate_mapping.py rejects the previously accepted incomplete forms.
- R2_DESIGN.md and R2_IMPLEMENTATION_PLAN.md explain and sequence the authority-only work.

## Verify before local source work

Run from this directory:

~~~
python3 validate_mapping.py .
python3 -m unittest test_validate_mapping.py -v
~~~

The manifest covers each text authority-package file except itself. A package failure is fail-closed and is not a numerical, physical, or scientific-result failure. Extract and verify the separately published delivery ZIP before creating a local worktree.
