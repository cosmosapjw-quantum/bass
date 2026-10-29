# Reproduction instructions (CE1-P scoped, model data)

Parent exact commit `e4a0feba0e8709d5e996ed8ef4c9c9bf1da4c4d0` in `cosmosapjw-quantum/bass`, **not** the PR255 documentation-only code. Requires numpy/scipy/matplotlib/pytest. Use a clean isolated worktree; do not mutate main/parent. Git source blob SHA checks are embedded in generator.

```bash
# From isolated parent BASS repo worktree (matching PR253 exact source blobs):
export PYTHONPATH="$PWD:${PYTHONPATH:-}"
python research/ce1p_20261029/source/generate_physical_history.py --output research/ce1p_20261029/data
python -m pytest research/ce1p_20261029/tests/test_physical_histories.py -q
python research/ce1p_20261029/source/plot_histories.py
```

If using the portable ZIP, unpack it into a fresh scratch directory and set `PYTHONPATH` to the pinned parent worktree. Paths are relative to ZIP root. The code enforces source module identities by SHA and fails closed on wrong source. Do not generate into stored original proof/certification directories. Comparison reference GL40 is independent numerical quadrature, not MPFR certified continuum.

The portable data can also be verified without rerunning physics: `python -m pytest tests/test_physical_histories.py -q` from extracted ZIP root; note the test reads saved CSV. The source generation command re-runs the physics.