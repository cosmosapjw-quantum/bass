# Bounded repair addendum — F1, F2 and exact-zero source obligation

Unit: `BASS_B3A_REC_EVENT_ADAPTER_20261024`.
The original `CONTRACT.md` remains unchanged. The controller authorized this
bounded repair after independent source/code review. This addendum clarifies
the implementation obligations already implied by the frozen owner/frame/clock
and duplicate-transfer contract; it changes no physical model, donor, closure,
quadrature, normalization gate or historical budget.

## Observed defects and authorized changes

The initial 12-test suite passed but missed two guards. The independent
reviewer script `reviews/probe_code_review.py` and its unchanged initial
receipt `reviews/CODE_REVIEW_PROBE_INITIAL.json` demonstrated acceptance of
wrong source clock/frame metadata (F1) and acceptance of one physical transfer
again after a frame change (F2). The independent probe exited 0 because it
reports observations rather than asserting refusal; its JSON records the
unwanted acceptances explicitly.

F1 repair: `rec_adapter` now defines canonical `ORIGIN_FRAME='rest'` and
`INVARIANT_CLOCK='proper_time_dt_dV_invariant'`. The source factory checks both
before donor construction. It refuses `ln_a`, `conformal_time` or an
`already_boosted` origin label. A subsequent physical `.boosted(...)` still
accepts an explicit nonempty target frame and preserves the invariant clock.
The BASS rate pair independently checks the selected owner and canonical
clock, including for a manually assembled bundle.

F2 repair: duplicate keys now identify a physical charge by
`(owner, epoch, transfer_id)`. Frame and clock representation do not create a
new charge. Full expected-identity equality remains required for attachment.
A genuinely boosted bundle with the same physical token is refused when the
returned ledger from the first attachment is passed back in.

Exact-zero obligation: a constructed actual donor state uses `n_l=1e9 m^-3`,
`n_u=0`, `f_plus=0`, `H=1e-13 s^-1` and `S=0`. The lower population and opacity
are positive, but both gross channels are exactly zero. Tests actually invoke
`owner.exchange_source` and `event_bundle`; they verify exact zero event rates,
cQ, K, PiRate, U and J. BASS attachment succeeds without a callback and copies
the supplied current pi unchanged. This is a zero-source fixture, not a newly
asserted physical finite radiation reservoir.

## Recorded RED → GREEN sequence

Every command below was executed in the unit directory through
`python3 code/run_bounded.py ...`; the receipt contains the resolved Python
executable, exact child argv, cwd, stdout, stderr, exit status and separate
wall/user/system CPU measurements.

| Invocation | Result | Exit | Wall s | CPU s | Raw log |
|---|---|---:|---:|---:|---|
| `repair_targeted`, pre-repair | 3 tests; F1 5 failed subtests, F2 1 failure; exact-zero PASS | 1 | 0.7954618620 | 0.793807 | `results/03_repair_targeted.log` |
| `repair_targeted`, after minimal repair | 3/3 PASS | 0 | 0.7337002200 | 0.733139 | `results/04_repair_targeted.log` |
| `tests`, one final affected-suite check | 15/15 PASS | 0 | 0.8117973340 | 0.811216 | `results/05_tests.log` |

The initial 12/12 pass remains recorded in `results/01_tests.log`; it is not
retroactively described as covering these guards. The current reference JSON,
CSV and visually inspected PNG from `results/02_reference_plot.log` are
reused unchanged. The repairs affect identity admission and bookkeeping,
with no changes to the event moment/boost kernel, donor bytes, native scalar
reconstruction, quadrature or plotting formulas. No reference/plot rerun was
needed or performed.

The implementation harness cumulative measured scientific cost, including
the intentionally failing RED run, is 5.1271016830 s wall and 5.119500 s CPU.
The independently measured reviewer probe was 0.7490066320 s wall and
0.747737 s CPU and is separate from this harness subtotal. Neither is a reset
or an inferred remaining historical balance. All child invocations remain
below 30 s, and the implementation subtotal remains below the separate 60 s
new local upper bound. The old remaining wall/CPU are still null.

## Reproducibility and review status

`IMPLEMENTATION_FREEZE_PRE_REPAIR.json` preserves the initial input freeze.
`IMPLEMENTATION_FREEZE.json` records the post-repair code/test/source/evidence
freeze. `IMPLEMENTATION_CODE.patch` is the current full new code/test diff.
The original frozen contract, immutable donor inputs, independent reviewer
files and original raw logs were not edited. The current post-repair
implementation awaits controller/fresh independent review disposition.

This-turn actual environment probes are recorded by the controller in
`provenance/INTAKE.json`: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0 and actual
Python/C++ success; only the optional default pytest/SymPy packages were absent, with the
Python/C++ runtimes available and successfully executed. The implementation used
unittest and needs neither absent package. This addendum does not invent an
original missing-package command or raw transcript.
