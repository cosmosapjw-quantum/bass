#!/usr/bin/env bash
set -euo pipefail
stage="${1:?R1..R10,C1..C10}"
repo="$(git rev-parse --show-toplevel)"
expected="research/bass-typeii-liouville-optdepth-20261101-r1"
[[ "$(git branch --show-current)" == "$expected" ]]
git add research/typeii_liouville_optdepth_20261101 _rustcore/src/runtime/mod.rs
[[ ! -e _rustcore/src/runtime/typeii_photon_host.rs ]] || git add _rustcore/src/runtime/typeii_photon_host.rs
[[ ! -e _rustcore/examples/typeii_photon_sweep.rs ]] || git add _rustcore/examples/typeii_photon_sweep.rs
git diff --cached --check
if git diff --cached --quiet; then echo "NO_CHANGE_TO_COMMIT $stage";exit 27;fi
git commit -m "science(typeii): $stage Liouville and opacity source-bound research"
git push --set-upstream origin "$expected"
head_sha="$(git rev-parse HEAD)"
remote_sha="$(git ls-remote origin "refs/heads/$expected" | cut -f1)"
test "$head_sha" = "$remote_sha"
backup_dir=/home/cosmosapjw/research_backups/bass_typeii_liouville_optdepth_20261101
mkdir -p "$backup_dir"
archive="$backup_dir/${stage}_${head_sha:0:12}.zip"
declare -a paths
paths=(research/typeii_liouville_optdepth_20261101 _rustcore/src/runtime/mod.rs)
if git cat-file -e HEAD:_rustcore/src/runtime/typeii_photon_host.rs 2>/dev/null; then paths+=(_rustcore/src/runtime/typeii_photon_host.rs);fi
if git cat-file -e HEAD:_rustcore/examples/typeii_photon_sweep.rs 2>/dev/null; then paths+=(_rustcore/examples/typeii_photon_sweep.rs);fi
git archive --format=zip HEAD "${paths[@]}" > "$archive"
unzip -tq "$archive" >/dev/null
sha256sum "$archive" >> "$backup_dir/STAGE_SHA256SUMS.txt"
printf '%s\t%s\t%s\t%s\n' "$stage" "$head_sha" "$(sha256sum "$archive" | awk '{print $1}')" "$archive" >> "$backup_dir/STAGE_LEDGER.tsv"
test -z "$(git status --porcelain=v1)"
printf 'STAGE=%s HEAD=%s REMOTE_READBACK=PASS ARCHIVE_SHA256=%s DAG=9/15 NEW_UPPER=0\n' "$stage" "$head_sha" "$(sha256sum "$archive" | awk '{print $1}')"
