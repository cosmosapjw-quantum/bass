#!/usr/bin/env bash
set -euo pipefail
phase="${1:?Q1-Q4}"
repo=/home/cosmosapjw/worktrees/bass-full-rii-wing-20261120-r1
branch=research/bass-typeii-full-rii-wing-20261120-r1
p=research/typeii_full_rii_wing_20261120
backup=/home/cosmosapjw/research_backups/bass_typeii_full_rii_wing_20261120
cd "$repo"
test "$(git branch --show-current)" = "$branch"
git add "$p"
git diff --cached --check
if git diff --cached --name-only | grep -v "^$p/"; then echo OUT_OF_SCOPE_STAGED;exit 2;fi
git commit -m "science(typeii): $phase Hummer RII and outer wings"
git push --set-upstream origin "$branch"
head=$(git rev-parse HEAD)
test "$head" = "$(git ls-remote origin "refs/heads/$branch"|cut -f1)"
mkdir -p "$backup"
archive="$backup/${phase}_${head:0:12}.zip"
git archive --format=zip HEAD "$p" > "$archive"
unzip -tq "$archive" >/dev/null
digest=$(sha256sum "$archive"|cut -d" " -f1)
printf "%s\t%s\t%s\t%s\n" "$phase" "$head" "$digest" "$archive" >> "$backup/STAGE_RECEIPTS.tsv"
test -z "$(git status --porcelain)"
printf "PHASE=%s HEAD=%s HOST_ARCHIVE_SHA=%s DAG=9/15_NEW_FULL0\n" "$phase" "$head" "$digest"
