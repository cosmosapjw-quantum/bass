# Reproduction and verification

`python code/verify_capsule.py` checks bytes and existing receipts without rerunning science.

In a separate copy, `python -m unittest discover -s code -p test_fa03.py`, `python code/check_fa03.py`, and `python code/rei_theory_checks.py` run the bounded tests. They use Python, NumPy and SciPy; exact observed versions are in evidence/EXECUTION_ENVIRONMENT.json. No network, repo mutation, chemistry or atomic provider is required.

The six-state solver uses RK4 and empirical refinement, not interval arithmetic. The two analytic bounds are proved in the manuscripts rather than certified by the sampling code.

`evidence/cloud_moments_bounds.wl` and `cloud_rei_rational_bound.wl` contain submitted stateless Wolfram inputs. Their observed results are transcribed structurally in WOLFRAM_CLOUD_RESULTS.json. Actual local xAct input and raw output bytes, with transfer hashes, are preserved separately. The raw xact_check.wl has the original absolute Export path; do not rerun it over evidence. For deliberate reproduction make a copy and change only the output path, recording that change.

First failures are preserved. Do not call test-after checks TDD; only the grey-recovery behavior has a recorded red/green cycle. Do not interpret a README or provider acknowledgment as an independent scientific review.
