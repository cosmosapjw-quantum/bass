# BASS-8B.1E.2 durable state — 2026-08-23

## Objective (frozen)

Implement and verify a bounded Python authority seam for the direction-dependent cold-Thomson collision rate of the already implemented independent electron test field, together with an explicit-provenance finite-domain prescribed schedule.  The seam must make the comoving and vacuum limits exact, apply the electron relative-flux Doppler factor exactly once, preserve the existing SI/legacy-cgs unit boundary, and stop before production-loop, Rust ABI, finite-ell, or authority-row promotion work.

## Controlling assumptions (frozen)

1. Metric signature is `(-,+,+,+)` and `c` remains explicit.
2. `n_e_free` is the scalar proper free-electron density in SI `m^-3`.
3. A fluid-frame photon direction is the propagation direction `e_f`, so the electron-frame energy ratio is `D_{e<-f}=E_e/E_f>0`.
4. The prescribed schedule coordinate is the solver's dimensionless Hubble time `tau`; nodes are interpreted in the declared normal-tetrad gauge.
5. Schedule interpolation is piecewise linear in the tetrad electron number current `N^a=n_e* U_e^a`, not independently in density and beta.  This makes `N^a=0` the vacuum equivalence class and prevents a vacuum velocity representative from leaking into neighboring samples.
6. A schedule requires a non-empty source identifier and a lowercase 64-hex content SHA-256; calls outside its closed support fail rather than clamp or extrapolate.
7. The only legacy unit adapter accepts `cm^-3` and converts once to SI `m^-3`; the Thomson cross-section authority remains `bianchi.thermo.history_api.SIGMA_T_CM2`.

## Hypotheses (frozen)

- **H1 — covariant rate.** Prediction: the implementation satisfies `d tau_T/dt_f = n_e* sigma_T c D_{e<-f} = -(n_e* sigma_T/c) u_e dot dx/dt_f` and `nu_tau=(d tau_T/dt_f)/H_t` for arbitrary subluminal non-collinear fluid/electron velocities. Falsifier: the scalar contraction, composed frame map, or dimensional result disagrees beyond the declared floating tolerance.
- **H2 — exact limiting strata.** Prediction: the comoving state gives `D=1`, while `n_e*=0` gives a bit-exact zero collision rate independent of the electron representative and direction. Falsifier: a residual Doppler/velocity dependence remains on the vacuum stratum or comoving rate differs from `n_e* sigma_T c`.
- **H3 — quotient-safe schedule.** Prediction: current interpolation stays future timelike whenever sampled density is positive, reconstructs a subluminal beta, canonicalizes exact vacuum to beta zero, and rejects missing provenance or out-of-support evaluation. Falsifier: spacelike/current-invalid interpolation, silent extrapolation, or vacuum-representative leakage.
- **H4 — unit parity.** Prediction: SI rate and the legacy `cm^-3`/`cm^2`/`cm s^-1` expression agree to roundoff with exactly one density conversion. Falsifier: a factor of `10^6`, `10^4`, `10^2`, or an extra/missing `H_t` remains.
- **H5 — bounded compatibility.** Prediction: the new focused gate and the prior 13-test electron/frame gate pass without modifying `Collision.v_b`, solver loops, or Rust. Falsifier: the bounded API requires those owners to change.

## Planned confirmatory experiments (frozen)

- **E1 — valid RED.** Add `tests/test_electron_collision_rate.py`; before production source exists, run `python tests/test_electron_collision_rate.py` and require a nonzero failure specifically for the missing public module/behavior.
- **E2 — minimal GREEN.** Add only the collision-rate/schedule module and rerun the identical E1 command to zero exit.
- **E3 — covariant and mutation audit.** Compare production output against an independently constructed four-vector contraction for non-collinear cases; demonstrate that omitted-`D` and double-`D` alternatives are rejected.
- **E4 — schedule/vacuum/provenance audit.** Exercise positive-current interpolation, exact vacuum quotient, domain edges, malformed provenance, nonmonotone nodes, and out-of-support requests.
- **E5 — unit/Hubble-time parity.** Compare SI and legacy cgs literals and check `nu_tau=rate_s/H_t` with dimensions recorded.
- **E6 — compatibility.** Rerun the prior focused electron/frame test and P9 screen audit; parse the machine-readable contract.
- **E7 — independent review.** A fresh read-only verifier receives the frozen state, sources, tests, logs, and claims without a suggested verdict and returns exactly one research verdict.
- **E8 — durable seal.** Produce a minimal source/test/report archive, internal manifest, ZIP CRC, clean extracted rerun, and external SHA-256 sidecar.

## Falsifiable criteria

- **C1 tracer:** E1 establishes a valid red and the identical command is green after E2.
- **C2 rate covariance:** E3 is zero-exit for representative and hostile non-collinear cases; sign, `c`, and dimensions are explicit.
- **C3 limits/schedule:** E4 proves comoving and vacuum exactness plus provenance/support/current-domain enforcement.
- **C4 units/time:** E5 proves SI/cgs parity and exactly one division by positive finite `H_t`.
- **C5 compatibility/boundary:** E6 is zero-exit and source inspection shows no production-loop/Rust/`Collision.v_b` edit.
- **C6 independent verification:** E7 verdict is not `inconclusive`; any finding is resolved or retained as an explicit blocker.
- **C7 durable artifact:** E8 manifest, CRC, extracted focused commands, and sidecar all return zero.

## Stopping rules

- Stop as `BLOCKED_RATE_CONVENTION_CONFLICT` if primary literature and the existing finite frame adapter cannot be reconciled without changing frozen direction/sign conventions.
- Stop as `BLOCKED_SCHEDULE_AUTHORITY` if current interpolation cannot make the vacuum quotient representative-independent without an additional user owner decision.
- At most one classified retry per exact command; record any retry as a new evidence entry.
- Do not install packages or modify `Collision.v_b`, q/model integration, Rust ABI, solver loops, finite-ell carrier, residual-U(1), projector/classifier, branch, commit, PR, Jira, or Confluence.

## Criterion status

- C1: pending
- C2: pending
- C3: pending
- C4: pending
- C5: pending
- C6: pending
- C7: pending

## Evidence log (append-only)

- **EV000 — preregistration timing deviation.** Initial read-only navigation and web source discovery occurred before this file was created while resuming from the preceding sealed checkpoint. Those observations are discovery context only and do not count as confirmatory results. All executable experiments E1–E8 begin after this frozen section.
- **EV001 — primary-source rate convention.** Younsi–Wu–Fuerst, Eqs. (11), (17), `https://arxiv.org/pdf/1207.4234`, and Challinor, Eqs. (2.21), (3.7)–(3.10), (3.14), `https://arxiv.org/pdf/astro-ph/9911481`, independently support `d tau=-(n_e* sigma_T/c) u_e dot dx` and `d tau/dt_f=n_e* sigma_T c D_{e<-f}` when `t_f` is fluid-observer ray time and `n_e*` is proper density.  The sign is fixed by `(-,+,+,+)` and future-directed rays.
- **EV002 — rejected naive Hubble-time clause and pivot P1.** Read-only internal survey found the Q solver defines Hubble time from normal-congruence physical time, not fluid time.  Therefore the frozen H1 clause `nu_tau=(d tau/dt_f)/H_t` is rejected for tilted fluid if `H_t` means the existing normal-frame H.  Correct relations are `r_f=n_e* sigma_T c D_{e<-f}`, `r_n=n_e* sigma_T c D_{e<-n}`, and `nu_tau=r_n/H_n`; if starting from fluid-frame direction, `r_n=r_f(E_f/E_n)`.  Implementation will expose separately named fluid-time and normal-time methods and will permit division only of the normal-time rate by `H_n`.  A comoving-electron state with nonzero fluid tilt must be isotropic in fluid time but direction-dependent in normal time.  This append-only pivot overrides only the rejected Hubble-time interpretation; all other frozen scope and stopping rules remain unchanged.
- **EV003 — E1 valid RED.** Command: `cd /workspace/scratch/3e0341833fab/electron_testfield_work/repo && python tests/test_electron_collision_rate.py`. Exit: `1`. Decisive output: `AssertionError: RED: bianchi.q.electron_rate collision authority is not implemented`. Classification: required public module/behavior is absent; the failure is not syntax, fixture, dependency, or import-runner noise. No production rate source existed at this point.
- **EV004 — density-frame and comoving-schedule guard.** Adversarial review of the internal legacy lane showed `x_e n_H` is a fluid/baryon-frame density; it equals electron proper density automatically only on the comoving restriction.  Therefore a mere `cm^-3 -> m^-3` conversion cannot adapt legacy history to generic H2.  The implementation will expose only an explicitly named electron-proper-cgs conversion and will mark automatic legacy-history adaptation false.  The independent schedule will interpolate `N_e^a`; a separate comoving density schedule will take the actual fluid beta at every positive-density query rather than interpolate a second electron beta.  At exact vacuum it returns the canonical zero-current representative and declares the comoving closure undefined on the quotient stratum.
- **EV005 — E2 initial GREEN.** Identical E1 command after adding `bianchi/q/electron_rate.py`: exit `0`, decisive output `Ran 10 tests in 0.007s` and `OK`.  This closed the first thin public slice for observer-specific rates, proper-density cgs/SI parity, vacuum no-op, strict schedule provenance/support, current interpolation, and live-fluid comoving construction.
- **EV006 — vacuum payload-identity red/green.** A new focused assertion required schedules differing only in beta at `n_e*=0` knots to have the same payload hash.  Before repair, the identical focused command exited `1` with hashes `0f96358c...` versus `73998db9...`.  Production repair canonicalized vacuum beta before both current construction and payload hashing.  The identical command then exited `0`, `Ran 10 tests`, `OK`.
- **EV007 — hostile edge expansion and one classified diagnostic retry.** Added 800-case observer-chain/covariant checks, the exact `0.5/2/1.25` normal-frame oracle, stable near-null-current reconstruction, counterstream density-overshoot semantics, copied-input immutability, `nextafter` support rejection, conversion overflow, and positive-zero signbit checks.  First expanded run exited `1` only because the validity metadata lacked the exact token `ENERGY_DOMAIN_UNVERIFIED`; the overflow probe also emitted a caught NumPy warning.  The formula and numeric oracles passed.  One allowed diagnostic repair added the machine token and suppressed only the expected arithmetic warning before raising the existing overflow exception.  Rerun exited `0`, `Ran 13 tests in 0.294s`, `OK`.
- **EV008 — independent numerical audit.** Command: `PYTHONDONTWRITEBYTECODE=1 python audit/electron_collision_rate.py`; exit `0`.  For 2,000 cases up to speed `0.92c`: fluid covariant max `4.8849813083506888e-15`, normal covariant `8.8817841970012523e-16`, observer chain `3.7747582837255322e-15`, global Lorentz scalar `8.4959412097557501e-15`.  Exact canonical factors were `0.5/2/1.25`, cgs/SI relative difference `0`, and counterstream midpoint density ratio `1.666666666666667`.
- **EV009 — integrated bounded regression.** One command ran the new `13/13` gate, prior electron/frame `13/13` gate, 2,000-case rate audit, prior P9 screen audit, both contract JSON parsers, and `py_compile`; exit `0`.  P9 maxima remained scale `4.441e-16`, anisotropy `6.661e-16`, phase `6.667e-16`, round trip `7.772e-16`, leak `1.657e-15`.  Full installed-package/JAX/Rust suites remain unavailable and are not inferred.

## Claimed criterion status before fresh verification (append-only)

- C1: claimed — two recorded valid red/green cycles, including the tracer.
- C2: claimed — exact formulas plus representative/hostile covariant and observer-chain evidence.
- C3: claimed — exact comoving/vacuum behavior, independent and live-fluid schedules, provenance and support guards.
- C4: claimed — SI/cgs parity is exact in the audit; normal H is validated and applied once.
- C5: claimed — prior frame/P9 regression green and no production-loop/Rust owner modified.
- C6: pending — fresh verifier not yet run.
- C7: pending — durable seal not yet built.

## Post-review evidence (append-only)

- **EV010 — fresh independent verdict and one Low finding.** A read-only verifier, given the frozen state and artifacts without a suggested verdict, returned `confirmed` with no Critical, High, or Medium defects.  It independently reran both 13-test gates, the 2,000-case rate audit, P9, JSON/AST parsing, a hand four-vector oracle, original-source/Rust identity checks, and confirmed the non-wiring/non-promotion boundary.  It found one Low canonical-identity issue: physically equivalent vacuum densities `+0.0` and `-0.0` sampled identically but produced distinct payload hashes.
- **EV011 — signed-zero TDD repair.** Primary reproduction exited `0` with `payload_equal False` and `state_equal True`.  A focused regression assertion was added and the gate then exited `1` at that exact assertion.  `_schedule_arrays` was changed only to canonicalize every zero-density sign bit to `+0.0` before payload hashing.  The identical focused command then exited `0`, `Ran 13 tests`, `OK`.  New decisive hashes are `331ce8904ddf821d4128bb7661e76dec7d9b91f79521d8109343d58e1d9c3180` for `bianchi/q/electron_rate.py` and `0d29b4039b60801a2c352bc3f08b744d6c6a8cf5c23bd1d68769a837e672e8d2` for `tests/test_electron_collision_rate.py`.
- **EV012 — post-repair integrated regression.** Fresh integrated command reran new `13/13`, prior frame `13/13`, the 2,000-case rate audit, P9, both JSON parsers, and source compilation; exit `0`.  Audit maxima and exact oracles were unchanged: worst Lorentz scalar residual `8.496e-15`, factors `0.5/2/1.25`, SI/cgs difference `0`, and P9 leak `1.657e-15`.

## Criterion status after primary repair (append-only)

- C1: satisfied.
- C2: satisfied.
- C3: satisfied, including canonical signed-zero vacuum identity.
- C4: satisfied.
- C5: satisfied within the bounded Python authority; full optional-stack execution remains unavailable.
- C6: pending the same verifier's bounded repair confirmation.
- C7: pending durable seal.

- **EV014 — clean-extract candidate seal.** Candidate ZIP SHA-256 `147805cc37eb161b41360b83399cb2a5fa245d2a08264837e676166fa77a7b33`; ZIP CRC and the internal manifest passed.  A new temporary-directory extraction reran both `13/13` gates, the 2,000-case rate audit, P9, and both JSON parsers with exit `0`.  Recorded maxima and exact oracles were unchanged.  The candidate is evidence only; the final ZIP is resealed after adding this receipt and refreshed manifest.

- **EV015 — final durable seal.** Final ZIP SHA-256 `75c137d897d37e327aeb23c5352f547deed474401a25673a72681351e6e4e750`.  External sidecar check, final ZIP CRC, final clean-extract internal manifest, both `13/13` gates, the 2,000-case rate audit, P9, and both JSON parsers all returned exit `0`.  C7 is satisfied.  This final evidence remains external to the ZIP to avoid circular self-reference.

## Final criterion status (append-only)

- C1–C7: satisfied for `BOUNDED_IMPLEMENTED / INDEPENDENT_CONFIRMED / NOT_PRODUCTION_WIRED / NOT_PROMOTED`.

- **EV013 — bounded repair confirmation.** The same independent verifier inspected only the signed-zero repair and its regression assertion, reran `PYTHONDONTWRITEBYTECODE=1 python tests/test_electron_collision_rate.py`, and returned exit `0`, `13/13`.  Revised verdict: `confirmed`; the prior Low finding is closed.

## Criterion status before sealing (append-only)

- C1–C6: satisfied for the frozen bounded claim.
- C7: pending durable seal.
