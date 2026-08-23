# BASS-8B.1E.4 verification report

Status: **CONFIRMED — bounded Python authority, not promoted**.

Frozen source locator:

```text
fd7045723df0bbb98077f86c56b5763d4f4d490b8ebaa483d7197ba8c4a30eea
electron_testfield_work/repo/bianchi/q/electron_trajectory.py
```

## Decisive gates

```text
E4 focused trajectory/orientation tests     28/28 PASS
E4 hostile audit                            PASS
E1 electron frame/state                     13/13 PASS
E2 electron rate/schedule                   13/13 PASS
E3 cold-Thomson validity                     20/20 PASS
electron frame/rate/validity audits         PASS
P9 boost-screen audit                        PASS
Python compilation                          PASS
machine-contract JSON                       PASS
fresh selected boundary replay              8/8 PASS
```

Hostile audit coverage:

```text
independent schedules                        180
comoving schedules                           120
near-null schedules                          100
exponent-span schedules                      100
numeric-domain fail-closed cases             108
orientation trials                           400
max actual / Doppler upper                   0.9971762526375411
max actual x / x upper                       0.9971762526375123
max integral relative error                  1.0265606808666548e-15
```

The deterministic regressions cover exact zero, vacuum-to-near-null and
scale-separated false positives, current norm/density overflow and underflow,
overflowing binary64 time intervals, beta/scalar interpolation roundoff,
subnormal Hubble rejection, and nested dataclass status relabeling.

## Independent review

- Physics/numeric reviewer: confirmed after additional extreme-current,
  beta-profile, scalar-profile, and vacuum-edge fuzzing.
- Code reviewer: pass; no remaining exact-rational, live-binary64,
  certificate-invariant, or fail-closed blocker.
- Fresh verifier: `CONFIRMED` at the frozen source locator above; no files
  modified.

## Scope boundary

The positive claim is only finite-trajectory, exact-cold,
total-cross-section validity plus typed optical-depth orientation.  The
`local_ray_rate` is still a separately provenance-bound input.  This artifact
does not certify a direction-dependent Q collision generator, a polarized
differential kernel, finite-temperature tails, production solver wiring,
JAX/Rust ABI, or authority-row promotion.

`ruff` was unavailable; syntax compilation, direct tests, adversarial audits,
and independent static inspection were used instead.
