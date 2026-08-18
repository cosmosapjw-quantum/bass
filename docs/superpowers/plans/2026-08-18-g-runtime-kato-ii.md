# G-RUNTIME-KATO-II implementation plan

**Goal:** Bind generated Type-II transport/collision/Kato kernels to a verified
reference exponential/phi-action runtime and reproduce stiff-uniform order two.

- [x] RED: runtime API missing
- [x] projected Pade13 exponential
- [x] full-dimensional Arnoldi exponential action
- [x] augmented `phi1` action
- [x] Kato co-moving AEM2 step
- [x] source-derived Type-II + actual RateSchedule fixture
- [x] alpha = 1, 1e3, 1e5 order-two regression
- [x] truncated-basis fail-closed test
- [x] full RustCore offline regression
- [x] rustfmt check
- [x] fresh Python stacked compiler regression
- [x] atomic commit/push and stacked PR

**Non-claim:** adaptive/restarted Krylov for `m<n` is OPEN.
