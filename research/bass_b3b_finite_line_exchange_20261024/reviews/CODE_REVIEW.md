# Independent B3b code and contract review

**Verdict: REPAIR_REQUIRED.** Two concrete admission/finite-state defects prevent
PASS_SCOPED for the reviewed candidate. The thick gross-count formulas and the
recorded 32-epsilon test-only correction are not the cause of these findings.

Reviewer: `/root/b3b_rec_intake`, independent of implementation. This reviewer
performed the preceding read-only intake of the actual REC source owner and did
not edit implementation or tests. Reviewed candidate
`code/finite_exchange.py` SHA-256:
`1462ad324d29861682f2e93568736f5f4f27c61708019d0d4d3bfb2b81d139ae`.
The frozen contract hash is
`9666a2bb2f641d55448388c6d2707020c52e206f63725a9cf4b3de06847fe50e`.

## F1 — finite depletion can erase a representable REC endpoint

**Priority P2; required before acceptance.** Relevant candidate code:
`code/finite_exchange.py`, original lines 222–239 and 275–276.

The code forms the upper population as `nu1 = population.n_u_m3 - D` and the
atomic energy by subtracting `drho`. In a strongly depleted but finite interval,
the stable net count can round to the whole initial upper population even while
the actual REC endpoint is positive and representable. The existing guard only
checks failure to advance from the initial state. It does not check deletion of
the remaining positive owner endpoint.

The focused independent probe used the actual existing transaction fixture,
`omega=50`, and an atomic sector containing exactly its initial excitation
energy. Its observed result was:

| Quantity | Actual result |
|---|---:|
| Actual REC owner endpoint `x1` | 3.878639060635223e-23 |
| `N*x1`, remaining upper population in m^-3 | 3.878639060635223e-14 |
| Candidate committed upper population in m^-3 | 0.0 |
| Excitation energy of the positive endpoint, fixed units | 1.3161275159163052e-24 |
| Candidate committed atomic energy, fixed units | 0.0 |
| Rounded stable net count in m^-3 | 300000000.0 |
| Input mutation | None |

This is loss by subtraction/cancellation, not an unrepresentable positive
endpoint. A tolerance normalized by the initial total population is a useful
conservation check but cannot certify the resolved remaining stock. It therefore
does not authorize deleting this endpoint under the frozen contract's actual
finite-population-map and no-silent-deletion requirements.

**Minimal repair:** retain the actual owner endpoint in the finite-population
update and consistently represent its excitation energy, or explicitly reject
the unresolved finite commit while retaining the analytic ledger. At minimum,
detect the demonstrated case in which the actual endpoint is positive but the
candidate stock/owned excitation is zero. Do not add a floor, clip, renormalize,
or create a replacement reservoir. Include one focused regression at large
finite omega; a full campaign or IVP is unnecessary.

## F2 — complex geometry passes the physical state admission

**Priority P2; required before acceptance.** Relevant candidate code:
`code/finite_exchange.py`, original lines 197–208 and 279–297;
unchanged `vendor/core.py`, `State.validate`.

The wrapper delegates state validation to the existing core validator, which
checks shapes, finiteness and symmetric/STF representation but does not require
real numeric arrays. The independent probe changed only
`state.n[0,0]` to `0.003+0.01j`. The candidate accepted the transfer and returned
that complex geometry. It also emitted:

> Casting complex values to real discards the imaginary part

when returning the real constraint scale. The reported scale was
0.029977970684601552. The inputs remained unchanged, but the accepted state was
outside the real physical domain and its constraint report discarded a complex
component.

**Minimal repair:** add explicit finite-real scalar/array admission in the new
wrapper before relying on the unchanged core routines. Apply it to physical
state scalars and arrays and the source arrays; preserve existing shape and
STF checks. Reject complex input without casting away its imaginary part and
without modifying vendor source. A single complex-geometry regression is
sufficient to close this demonstrated defect.

## Scope findings that already pass inspection

- The receiver uses the actual unchanged REC `thick_local_step`, card registry,
  owner validator and finite-opacity qualifications. General `f_plus>0`
  remains a prescribed-boundary gross ledger and is refused by state commit.
- Canonical rest frame and proper-time clock, fixed scale/Pstar, card/scope,
  stock epoch and stock population are compared before commit. Source geometry
  is checked through `h=H L/c` and `sigma=h S`.
- The emitted finite packet weights use the required L-squared conversion. The
  existing tests separately check the L-cubed interval-average conversion.
- The atomic donor must already own its excitation energy. Other sectors and
  atomic pressure/pi are copied and preserved. No additional donor is created.
- Empty photon stock has an actual zero-moment branch with empty arrays; there
  is no epsilon seed. Nonempty stocks use actual kinetic moments.
- Physical duplicate keys use owner/epoch/transfer ID, independent of
  representation labels, and population/photon histories must agree.
- Input U/J must be zero by the approved addendum. Returned U/J are zero after
  the finite update, and returned photon `Source.pi` is state stress rather
  than a rate. This avoids integrating the same transfer twice.
- Both demonstrated faulty admissions preserved inputs. The same focused probe
  confirmed nonscalar duration and complex photon-weight arrays are correctly
  rejected without mutation.

## Judgment on the 32-epsilon test correction

The recorded first run is correctly retained as **15 PASS / 1 FAIL out of 16**.
The failure was the rotated 14-node weight sum: residual
3.3306690738754696e-16 exceeded an absolute test tolerance of 3e-16. Fourteen
positive floating terms alone have a standard sequential-summation factor
`gamma_13 = 13*u/(1-13*u)` with unit roundoff `u=eps/2`, approximately
1.44e-15, before allowing for construction of q, dot products and sqrt(3).
The original threshold was consequently too small as a general floating
arithmetic allowance for that test.

Changing this fixture test to `32*eps = 7.105427357601002e-15` is reasonable.
The exact rational degree-five oracle remains unchanged, and the physical
transaction's independent 256-epsilon gross-scale checks were not relaxed.
This is an accepted test-only repair, not a new physical-error or interval
certificate. Later recorded 16/16 passes do not replace the original failure.

## Actual independent execution

One focused process was run; the full suite was not replayed.

```text
argv: ["python", "reviews/probe_code_review.py"]
cwd: /workspace/scratch/fe69646d3c76/bass_source/research/bass_b3b_finite_line_exchange_20261024
exit: 1 (intentional finding-status exit)
wall seconds: 0.39043518199468963
child CPU seconds: 0.389906
process wall ceiling: 15 seconds
```

Raw output and receipt are `CODE_REVIEW_PROBE.stdout.json`,
`CODE_REVIEW_PROBE.stderr.txt` and `CODE_REVIEW_PROBE_RECEIPT.json` in this
directory. The probe reuses a test fixture only as a concrete receiver builder;
its depletion oracle is the unchanged REC owner's positive endpoint.

New IVP = 0; campaign replay = 0. Historical remaining wall/CPU budgets remain
null and `budget_reset=false`. These measured review costs are a new bounded
work-unit entry, not a reconstructed campaign budget. No remote publication,
backup acknowledgment, merge, production activation or figure acceptance is
asserted by this code review. Initial findings must remain in the record after
any targeted repair.
