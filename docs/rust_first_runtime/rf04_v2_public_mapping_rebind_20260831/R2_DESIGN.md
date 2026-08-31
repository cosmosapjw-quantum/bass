# RF04 V2 Public-Mapping R2 Design

## Purpose

R2 is a user-authorized correction to the first mapping package. It converts the polarized-v2 execution identity from an impossible zero-argument API into a contextual API without adding a fourth public symbol or changing PR #70.

## Contextual identity

The identity API takes exactly directions, weights, and remap_plan. These values already define the caller-specific direction-grid and remap-plan digests required by the v2 route authority. Its returned canonical JSON is exactly the value placed in a trajectory or batch result for those same validated inputs. There is no cache, process-global state, or wheel inspection in this computation.

native_payload_identity is a static logical identifier, consistent with scalar-v1. The wheel SHA-256 is immutable installation evidence, not a runtime API datum: a wheel cannot safely prove its own exact archive bytes from mutable installed state, and the caller should not get a different semantic identity merely because of installation-path metadata.

## Receipt and carrier contract

The public mapping gives the backtraced directions and spatial transport distinct versioned byte codecs, hashes the canonical receipt body, and folds the receipt hashes into a domain-separated chain. It also fixes Reject mode at binary64 1e-10 and distinguishes its absolute input leakage gate from the donor's intensity-relative realizability gate.

The raw leakage diagnostic is measured before the final projection of a complete accepted step candidate; the post diagnostic is measured after projection on the state actually stored in history. Batch status has only two values, so the existing typed string error code is the sole semantic classifier for an isolated member failure.

## Scope

R2 authorizes only LOCAL-01 public-boundary implementation and evidence. It does not change frozen P1–P5 route semantics, formula authority, the final donor identity, v1 behavior, LOCAL-02, or any scientific claim.
