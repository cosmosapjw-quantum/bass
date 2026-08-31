# RF04 V2 Public-Mapping Rebind

This package resolves the documented LOCAL-01 authority gap without changing the scientific route decisions or any production source. It binds the existing v2 route design to PR #70's final safety-rebound donor and specifies the missing public PyO3/result/exception boundary for a separate local implementation job.

## Authority boundary

- Base: PR #70 head 380ce6fe6aebe0c76c59c0d2a0f8707aac0ce14c, tree 0062a719173dc0c40dcc1202ab0d305f8fe2e2bb.
- Final donor: Git blob 693e9fff0d44f2b8e40966ceb8da3c348d830bd4, SHA-256 f1f624d47b35208d339e6ea298f023d70012e54c80357973a65dc63c9491de6e.
- Imported v2 direct authority: commit a083f8c2f489364d7ad866dac2eeff03de24f2e2, direct manifest SHA-256 07a8baa8ad2b432b821a300ca2f3a47c2f0cf1f0d008082be8aa39fcb6a6dc4c.
- Imported public-schema base: commit f18e491f19f45accc8c87eb56b4a24f15a8a3d6c, blob a5a503f96c8d85af265be67ac04fd3ff983d9b33.

The current status remains PASS_RF04_SCALAR_RAW_SLICE_PROOF retained, LOCAL-01 NOT_PASS, LOCAL-02 NOT_RUN, and NO_PASS_RF04.

## Package contents

- AUTHORITY_REBIND.json pins the exact inherited authority and final donor.
- V2_PUBLIC_MAPPING.json supplies the concrete v2 PyO3, serialization, result, and existing-error-class contract.
- LOCAL_CODEX_HANDOFF_CONTRACT.json and LOCAL_CODEX_HANDOFF.md give the local Codex job a structurally auditable execution contract.
- validate_mapping.py verifies the authority anchors, contract shape, and manifest.

Run the portable package check from this directory:

    python3 validate_mapping.py .
    python3 -m unittest test_validate_mapping.py -v

The manifest covers every package file except itself. A validation failure is fail-closed and is not a scientific-result failure.
