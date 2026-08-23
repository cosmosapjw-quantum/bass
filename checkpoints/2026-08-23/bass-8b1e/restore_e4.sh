#!/usr/bin/env bash
set -euo pipefail

checkpoint_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
archive_name="BASS8B1E4_TRAJECTORY_ORIENTATION_AUTHORITY_20260823.zip"
expected_sha256="d7590182b52d7bb30f537232993f2bb954a049d530138b0325474633926ec766"
parts_dir="$checkpoint_dir/archives/$archive_name.parts"
output_path="${1:-$checkpoint_dir/archives/$archive_name}"

if [[ -e "$output_path" ]]; then
  echo "Refusing to overwrite existing output: $output_path" >&2
  exit 2
fi

cd "$checkpoint_dir"
sha256sum -c PARTS.sha256
cat "$parts_dir"/part-*.bin > "$output_path"

actual_sha256="$(sha256sum "$output_path" | awk '{print $1}')"
if [[ "$actual_sha256" != "$expected_sha256" ]]; then
  echo "Reconstructed SHA-256 mismatch: $actual_sha256" >&2
  exit 3
fi

unzip -tq "$output_path"

echo "Restored and verified: $output_path"
