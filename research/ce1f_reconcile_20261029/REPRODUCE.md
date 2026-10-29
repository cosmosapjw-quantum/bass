# CE1-F reconciliation reproducibility

1. Checkout the *separate* research branch `research/bass-ce1f-reconcile-energycap-20261029-r1` with its final Git SHA from DELIVERY_FINAL.json. Do not merge PR #238, #239 or #240.
2. Use Python 3.13, NumPy 2.3.5, SciPy 1.17.0, mpmath 1.3.0, pytest 9.0.2 and GNU MPFR6.
3. Run focused regression from repository root:

```
python -m pytest -q tests/nonperturbative/test_ce1f_energy_cap_reconciliation.py tests/nonperturbative/test_einstein_tabulated_source.py tests/nonperturbative/test_einstein_exponential_source.py tests/nonperturbative/test_einstein_physical_input.py tests/nonperturbative/test_einstein_interval.py tests/nonperturbative/test_einstein_error_budget.py
```

4. Run actual same-input comparison with the frozen sibling **source at PR239 pinned SHA** already checked into the reconciliation branch:

```
PYTHONPATH=. python research/ce1f_reconcile_20261029/compare_variants.py /tmp/ce1f_comparison.json
```

5. Verification evidence is also stored in CI run 40792700025 / artifact 12862327693. Earlier run 40792407814 falsely displayed success, because import failure was masked by tee; never cite the earlier run as actual cross-comparison.
6. No scientific need to rerun old CE1-F or CE1-G production campaigns. `validate_saved.py` checks immutable local provenance and recorded scientific requirements without recomputing the IVPs.

The final ZIP is a research+evidence bundle and includes the old independent CE1-F parent ZIP and current corrected code/test and CI comparison artifact. The pinned sibling C10 source is tracked in Git at the given SHA and has Git blob e1f5e11baada25858f8fb03321f071ed759b6f99; do not claim the offline ZIP alone contains that Git checkout.
