#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:-/tmp/bass12-r2-execution-package}"
ZIP_NAME="BASS12_TARGET_DERIVED_HARNESS_RETRY_R2_20260828.zip"
ZIP_SHA="175e010021d42e954b829cb9e5653e94d2cb6c946812526f3c4bbb0cecb2342d"
ZIP_SIZE="17464"
ROOT_NAME="BASS12_TARGET_DERIVED_HARNESS_RETRY_R2_20260828"

case "$OUT" in
  /tmp/*) ;;
  *) echo "ERROR: output must be under /tmp: $OUT" >&2; exit 2 ;;
esac

rm -rf "$OUT"
mkdir -p "$OUT"

(
  cd "$HERE"
  sha256sum -c PARTS.sha256
  cat parts/part-*.b64 > "$OUT/$ZIP_NAME.b64"
)

base64 --decode "$OUT/$ZIP_NAME.b64" > "$OUT/$ZIP_NAME"
rm -f "$OUT/$ZIP_NAME.b64"

test "$(stat -c %s "$OUT/$ZIP_NAME")" = "$ZIP_SIZE"
echo "$ZIP_SHA  $OUT/$ZIP_NAME" | sha256sum -c -
unzip -t "$OUT/$ZIP_NAME" >/dev/null
unzip -q "$OUT/$ZIP_NAME" -d "$OUT"

ROOT="$OUT/$ROOT_NAME"
test -d "$ROOT"
(
  cd "$ROOT"
  PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_package.py .
  PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
)

printf '%s\n' \
  PASS_BASS12_REMOTE_EXECUTION_PACKAGE_TRANSPORT \
  "execution_package=$OUT/$ZIP_NAME" \
  "execution_root=$ROOT"
