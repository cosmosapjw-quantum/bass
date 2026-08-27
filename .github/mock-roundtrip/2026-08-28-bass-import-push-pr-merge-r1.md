# BASS GitHub connector round-trip marker

Date: 2026-08-28 KST
Repository: `cosmosapjw-quantum/bass`
Purpose: isolated import/read, remote write, pull-request, expected-head merge, and readback test.

## Isolation

- Canonical `main` at test entry: `d9e5ba7577ccb05b648b11ea7ac991bf6e09d8b9`
- Temporary base: `mock/github-import-push-pr-merge-base-20260828-r1`
- Temporary head: `mock/github-import-push-pr-merge-head-20260828-r1`
- This marker is the only intended changed path.

## Boundary

This test authorizes no production-source mutation, scientific claim, RF-03 implementation, package merge, ready transition, or canonical-branch movement.
