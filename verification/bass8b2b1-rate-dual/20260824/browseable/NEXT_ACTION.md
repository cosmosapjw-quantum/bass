# Next action

```text
BASS-8B.2B.1-R1_PURE_PYTHON_EXACT_E2_HOST_PARITY
```

From the extracted candidate root:

```bash
./host_replay/run_from_repo_checkpoint.sh /path/to/bass \
  2>&1 | tee /tmp/bass8b2b1-purepy-e2-host-parity.log
```

The command must run in an environment with Python, NumPy, and pytest.  JAX,
JAXlib, Equinox, and Diffrax are neither installed nor imported for this gate.

Acceptance:

```text
candidate physics tests             17/17 PASS
pure-Python loader tests             3/3 PASS
candidate-vs-E2 parity               5/5 PASS
E2 predecessor suite                13/13 PASS
E2 electron/electron_rate hashes     unchanged
legacy package initializers          not executed
optional JAX stack                    not imported
final marker                          BASS8B2B1_EXACT_E2_HOST_PARITY_PASS__PURE_PYTHON_FRONTEND
```

Only after this marker is durably recorded may
`BASS-8B.2B.2_GENERIC_VECTOR_BUNDLE_DIFFERENTIAL` open.
