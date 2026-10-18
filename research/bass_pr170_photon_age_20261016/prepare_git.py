"""Restore only the exact immutable CSV omitted from Git in favor of gzip.

The source generator and numerical tolerances are not changed. Existing
mismatched source files are rejected, never overwritten.
"""
from pathlib import Path
import gzip
import hashlib

RAW_SHA256 = '0a643f7c51e853ad15b9b2682c5534cdfcf9d25fda219bd3275023074cb2d444'
GZIP_GIT_BLOB = '04aa6d29b251e05e0caccfbbfeb6cc6b0d5bdeea'

def prepare_history(root: Path) -> None:
    """Restore an exact CSV from the published gzip, or validate existing CSV."""
    target = Path(root) / 'evidence/S3_CAMPAIGN_FINAL/HISTORY.csv'
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest() != RAW_SHA256:
            raise ValueError('EXISTING_HISTORY_HASH')
        return
    compressed = target.with_name('HISTORY.csv.gz').read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(compressed)).encode() + b'\0' + compressed).hexdigest()
    if blob != GZIP_GIT_BLOB:
        raise ValueError('COMPRESSED_HISTORY_HASH')
    raw = gzip.decompress(compressed)
    if hashlib.sha256(raw).hexdigest() != RAW_SHA256:
        raise ValueError('DECOMPRESSED_HISTORY_HASH')
    with target.open('xb') as stream:
        stream.write(raw)

if __name__ == '__main__':
    prepare_history(Path(__file__).resolve().parent)
    print('EXACT_HISTORY_CSV_READY')
