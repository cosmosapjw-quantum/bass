#!/usr/bin/env bash
set -euo pipefail
stage="${1:?R1..R10 or C1..C10}"
repo=/home/cosmosapjw/worktrees/bass-typeii-axial-ray-exact-20261102-r1
branch=research/bass-typeii-axial-ray-exact-20261102-r1
backup=/home/cosmosapjw/research_backups/bass_typeii_axial_ray_20261102
cd "$repo"
test "$(git branch --show-current)" = "$branch"
git add research/typeii_axial_ray_exact_20261102
git diff --cached --check
if git diff --cached --quiet; then echo "NO_CHANGED_STAGE=$stage"; exit 21; fi
git commit -m "science(typeii): ${stage} exact axial null ray and opacity asymmetry"
git push --set-upstream origin "$branch"
local_sha="$(git rev-parse HEAD)"
remote_sha="$(git ls-remote origin "refs/heads/$branch" | cut -f1)"
test "$local_sha" = "$remote_sha"
archive="$backup/${stage}_${local_sha:0:12}.zip"
git archive --format=zip HEAD research/typeii_axial_ray_exact_20261102 > "$archive"
unzip -tq "$archive" >/dev/null
digest="$(sha256sum "$archive" | awk '{print $1}')"
printf '%s\t%s\t%s\t%s\n' "$stage" "$local_sha" "$digest" "$archive" >> "$backup/STAGE_RECEIPTS.tsv"
test -z "$(git status --porcelain=v1)"
echo "STAGE=$stage HEAD=$local_sha REMOTE_READBACK_PASS ARCHIVE_SHA256=$digest DAG=9/15 NEW_UPPER=0"
