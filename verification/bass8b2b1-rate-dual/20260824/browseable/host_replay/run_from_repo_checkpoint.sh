#!/usr/bin/env bash
set -euo pipefail

candidate_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="${1:-}"
if [[ -z "$repo_root" ]]; then
  repo_root="$(git -C "$candidate_root" rev-parse --show-toplevel 2>/dev/null || true)"
fi
if [[ -z "$repo_root" || ! -d "$repo_root/.git" ]]; then
  echo "usage: $0 /path/to/bass-repository" >&2
  exit 2
fi
repo_root="$(cd -- "$repo_root" && pwd)"
restore="$repo_root/checkpoints/2026-08-23/bass-8b1e/restore_e4.sh"
[[ -x "$restore" || -f "$restore" ]] || {
  echo "missing E4 restore script: $restore" >&2
  exit 3
}

tmp="$(mktemp -d -t bass8b2b1-e2-parity-XXXXXXXX)"
trap 'rm -rf "$tmp"' EXIT
archive="$tmp/BASS8B1E4_TRAJECTORY_ORIENTATION_AUTHORITY_20260823.zip"
extract="$tmp/e4-extracted"
mkdir -p "$extract"

bash "$restore" "$archive"
printf '%s  %s\n' \
  'd7590182b52d7bb30f537232993f2bb954a049d530138b0325474633926ec766' \
  "$archive" | sha256sum -c -
unzip -q "$archive" -d "$extract"

"$candidate_root/host_replay/run_exact_e2_host_parity.sh" "$extract"
