# Independent F1/F2 closure — final code review

**Verdict: PASS_SCOPED. F1 and F2 are closed for the repaired candidate.**
This decision combines the original independent code/contract inspection with
one targeted closure pass. It does not replace the original REPAIR_REQUIRED
decision or its failing evidence, and it does not claim a new broader audit.

Reviewer: `/root/b3b_rec_intake`, independent of implementation.

| Reviewed identity | SHA-256 |
|---|---|
| Repaired `code/finite_exchange.py` | `92392b51121b5262323f19083adaad29dabd34ece58da701ba407f3c87d2840e` |
| `IMPLEMENTATION_MANIFEST.json` | `cbf57faf11e5cdaad245127e6d822d1b8401eaf8a1c67ce1932174c7f2ef47c0` |
| Original frozen `CONTRACT.md` | `9666a2bb2f641d55448388c6d2707020c52e206f63725a9cf4b3de06847fe50e` |

The repaired source hash was checked before and after the probe and was
unchanged. All 36 files listed in the final implementation manifest matched
their recorded byte lengths and SHA-256 values. No vendor file hash changed
relative to `results/IMPLEMENTATION_MANIFEST_INITIAL.json`.

## F1 closed: preserve the actual positive endpoint

The repair constructs the upper population from `N * owner_map['x1']` and the
lower population from `N - upper`, rather than reconstructing a tiny remainder
by subtracting a rounded nearly complete transfer. It checks the endpoint on
the endpoint's own relative scale. The atomic sector is reconstructed from its
existing constant energy component plus the remaining actual excitation.
Explicit endpoint/energy underflow and unrepresentable-remainder guards are
present. The original tiny-increment rejection remains present.

The exact same original focused probe, at finite `omega=50`, now observes:

| Quantity | REC owner | Committed result |
|---|---:|---:|
| Remaining upper population, m^-3 | 3.878639060635223e-14 | 3.878639060635223e-14 |
| Remaining excitation, fixed units | 1.3161275159163052e-24 | 1.3161275159163052e-24 |

The stable net count remains 300000000.0 in floating representation. That
rounded ledger no longer deletes the separately representable endpoint. The
observed output preserves the actual source endpoint without a floor,
positivity clipping, renormalization or another reservoir. Inputs are unchanged.

## F2 closed: reject nonreal physical state/source values

The new wrapper checks `State.h` and `State.alpha` as finite real scalars and
checks State geometry/sector arrays and Source arrays as finite real numeric
arrays before calling the unchanged core validators. Complex arrays are
rejected rather than cast to real. Existing shape and STF checks remain.

The original `state.n[0,0] = 0.003+0.01j` probe now rejects with:

```text
ValueError: State.n must contain finite real numeric values
```

There is no warning, and the input is unchanged. The same probe's nonscalar
duration and complex photon-weight cases continue to reject without mutation.

## Scope and retained evidence

Acceptance remains limited to the frozen thick-model prescribed-boundary gross
ledger and canonical-rest `f_plus=0` finite emission transaction with the stated
real-domain, owner/card/scope/epoch/clock/geometry, representability and
whole-path thick preconditions. It establishes neither a finite `f_plus>0`
absorption reservoir nor a cosmological IVP or native-history integration.
State `Source.pi` and zero already-applied U/J conventions are unchanged.

The implementer's final recorded result is 18/18 PASS with 49 regenerated
figure-data rows. These existing outputs were inspected; this reviewer did not
rerun that suite or perform a new figure review. The original 15 PASS / 1 FAIL
test attempt, accepted 32-epsilon test correction, original F1/F2 failing probe,
and repair-stage assertion-message mismatch remain in their original records.
The final pass must not be described as first-pass success.

## Single closure execution

The original `reviews/probe_code_review.py` was run unchanged exactly once:

```text
argv: ["python", "reviews/probe_code_review.py"]
cwd: /workspace/scratch/fe69646d3c76/bass_source/research/bass_b3b_finite_line_exchange_20261024
exit: 0
wall seconds: 0.41078885400202125
child CPU seconds: 0.41026199999999996
process wall ceiling: 15 seconds
```

| Independent code-review process | Wall seconds | CPU seconds |
|---|---:|---:|
| Original finding probe | 0.39043518199468963 | 0.389906 |
| This F1/F2 closure probe | 0.41078885400202125 | 0.41026199999999996 |
| Cumulative | 0.8012240359967109 | 0.800168 |

New receipt: `CODE_REVIEW_FINAL_PROBE_RECEIPT.json`.
New raw output: `CODE_REVIEW_FINAL_PROBE.stdout.json` and
`CODE_REVIEW_FINAL_PROBE.stderr.txt`. The original `CODE_REVIEW.md`,
`CODE_REVIEW.json` and original probe raw files are retained.

New IVP = 0; campaign replay = 0. Historical remaining wall/CPU budgets remain
null and `budget_reset=false`. Backup/provider acknowledgment, publication,
merge and production activation are not claims of this scientific code-review
decision. No remaining F1/F2 repair is required for this exact candidate.
