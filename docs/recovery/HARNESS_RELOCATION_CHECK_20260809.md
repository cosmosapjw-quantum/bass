# Immutable harness relocation check

## Purpose and evidence boundary

The recovered harness contains signed-off historical execution records whose canonical
working directory is `/workspace/scratch/f798b9abe5c3/BASS_v1_background_highl_harness`.
Its validator deliberately rejects those records after a relocation. This check separates
that expected path binding from source corruption. It does not reissue H0/H1 evidence,
authorize solver work, or promote a scientific claim.

The current interpreter matched the recorded executable and version:

- `sys.executable`: `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3`
- Python: `3.12.13`

## Relocated repository result

From `harness/BASS_v1_background_highl_harness`:

```text
sha256sum -c audit/FILE_MANIFEST.sha256                      PASS (71/71 governed files)
PYTHONDONTWRITEBYTECODE=1 python3 tools/validate_harness.py  exit 1
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover ...   36 pass, 2 fail
```

The validator reported exactly four execution-context errors, covering the producer and
independent-review logs for H0 and H1. Both unit failures were assertions that transitively
require those four contexts to be valid; no content-hash or contract error was reported.

## Exact recorded-path control

The 72 already hash-verified files were copied temporarily to the exact recorded path,
without editing any harness byte or retained historical log. From that directory:

```text
sha256sum -c audit/FILE_MANIFEST.sha256                      PASS (71/71 governed files)
PYTHONDONTWRITEBYTECODE=1 python3 tools/validate_harness.py  PASS
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover ...   PASS (38/38)
```

The temporary materialization was removed immediately after the control. The durable copy
remains in the repository path, where the historical execution context continues to fail
closed as designed.

## Conclusion

The extracted harness is byte-intact and its current relocation behavior is expected. The
test result applies only to the harness and its internal policies. The bundle declares
`solver_code_included=false`, and no Task 3–10 solver implementation was exercised.
