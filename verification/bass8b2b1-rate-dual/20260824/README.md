# BASS-8B.2B.1 pure-Python exact-E2-parity evidence seal

This directory preserves the supplied candidate ZIP byte-for-byte, its SHA-256
sidecar, the raw exact-host transcript, and a browseable cache-free package
copy. The browseable copy omits `.pytest_cache/`, `__pycache__/`, and `*.pyc`;
the exact archive deliberately retains its original cache-bearing contents.
Its historical raw logs and Markdown documentation retain their supplied bytes;
the local `.gitattributes` marks only those evidence paths as
whitespace-ignored so `git diff --check` does not misclassify preserved pytest
formatting or Markdown hard breaks as source edits.

`browseable/MANIFEST.sha256` is the candidate's internal 71-file manifest.
The top-level `MANIFEST.sha256` covers every committed artifact except itself,
the standard necessary exception for a checksum manifest, and can be verified
with `sha256sum -c MANIFEST.sha256` from this directory.

This is a bounded verification receipt, not an authority promotion or a start
of BASS-8B.2B.2.
