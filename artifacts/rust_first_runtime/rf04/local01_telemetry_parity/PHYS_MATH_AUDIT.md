# RF-04 LOCAL-01 PHYS-MATH audit

Disposition: `PASS_SCOPED_REVIEW_WITH_BLOCKER_RETAINED`

Reviewed commit/tree:

```text
c27643051bf3f1baca257b87cb0264bae9d61da6
80d3487b4cac8ae7fa833b17a49caa75c49a7124
```

No P0 or P1 defect was found in the bounded donor-level change.

## Findings

- The telemetry algebra is correct on successful calls. Every rejected parent
  adds one split event, and every accepted leaf adds one accepted subinterval,
  giving `L = N_root + S`. The reported depth is the maximum accepted-leaf
  recursion depth rather than the number of splits. Counter additions are
  checked and fail rather than saturate.
- The frozen callback algebra is consistent with the binary split tree. There
  are two endpoint samples and one midpoint for each tree node, giving
  `2 + N_root + 2*S`. The retained geometry-prefix differential checks the
  internal background-call sequence, but the final result-carrier/public
  callback contract is not available.
- Both bounded nonfinite repairs are mathematically fail-closed. The Type-II
  conversion validates its derived background before returning it, and every
  scalar in a successful final receipt is checked for finiteness. Neither path
  clamps, saturates, or fabricates a success receipt.
- Split, leaf, and depth counters are adaptive-work telemetry only. Nothing in
  this change promotes them to an accuracy certificate. `max_screen_leakage`
  remains a post-projection diagnostic and is not represented as raw
  longitudinal leakage.

## P2

The focused owner-crate tests establish the counter identities and failure
behavior, but they do not directly assert complete callback fractions/order.
That comparison exists only in the geometry-prefix validator, whose declared
scope excludes carrier and PyO3. This is an incomplete LOCAL-01 acceptance
item, not an observed physics defect.

## Claim boundary

The rebuilt wheel exposes the three v1 symbols and no v2 symbols. Consequently
the named safety errors cannot be authenticated through an authorized v2 result
carrier and PyO3 mapping. `LOCAL-01` is not a pass, `LOCAL-02` remains closed,
and the overall claim remains `NO_PASS_RF04`.
