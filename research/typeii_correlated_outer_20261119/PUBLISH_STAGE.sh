#!/usr/bin/env bash
set -euo pipefail
stage="${1:?M1_M4}"
repo=/home/cosmosapjw/worktrees/bass-correlated-outer-20261119-r1
branch=research/bass-typeii-correlated-outer-20261119-r1
p=research/typeii_correlated_outer_20261119
backup=/home/cosmosapjw/research_backups/bass_typeii_correlated_outer_20261119
cd "$repo"
test "$(git branch --show-current)" = "$branch"
git add "$p"
git diff --cached --check
if git diff --cached --quiet;then echo NO_STAGE_CHANGE;exit 27;fi
git commit -m "science(typeii): $stage correlated redistribution outer matching"
git push --set-upstream origin "$branch"
head="$(git rev-parse HEAD)"
test "$head" = "$(git ls-remote origin "refs/heads/$branch"|cut -f1)"
mkdir -p "$backup"
archive="$backup/${stage}_${head:0:12}.zip"
git archive --format=zip HEAD "$p" > "$archive"
unzip -tq "$archive" >/dev/null
digest="$(sha256sum "$archive"|cut -d' ' -f1)"
printf '%s\t%s\t%s\t%s\n' "$stage" "$head" "$digest" "$archive" >> "$backup/STAGE_RECEIPTS.tsv"
test -z "$(git status --porcelain=v1)"
printf 'STAGE=%s HEAD=%s ZIP_SHA256=%s REMOTE=PASS UPPER_DAG=9/15 NEW_FULL=0\n' "$stage" "$head" "$digest"
