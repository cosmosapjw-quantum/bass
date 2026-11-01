#!/usr/bin/env bash
set -euo pipefail
stage="${1:?stage}"
repo=/home/cosmosapjw/worktrees/bass-typeii-conserved-saha-20261102-r1
branch=research/bass-typeii-conserved-saha-opacity-20261102-r1
back=/home/cosmosapjw/research_backups/bass_typeii_conserved_saha_20261102
cd "$repo"
test "$(git branch --show-current)" = "$branch"
git add research/typeii_conserved_saha_20261102
git diff --cached --check
if git diff --cached --quiet;then echo NO_CHANGE;exit 21;fi
git commit -m "science(typeii): ${stage} conserved baryon Saha opacity physical modeling"
git push --set-upstream origin "$branch"
sha="$(git rev-parse HEAD)"
remote="$(git ls-remote origin "refs/heads/$branch"|cut -f1)"
test "$sha" = "$remote"
out="$back/${stage}_${sha:0:12}.zip"
git archive --format=zip HEAD research/typeii_conserved_saha_20261102 > "$out"
unzip -tq "$out" >/dev/null
sum="$(sha256sum "$out"|cut -d' ' -f1)"
printf '%s\t%s\t%s\t%s\n' "$stage" "$sha" "$sum" "$out" >> "$back/STAGE_RECEIPTS.tsv"
test -z "$(git status --porcelain=v1)"
echo "STAGE=$stage HEAD=$sha REMOTE_READBACK=PASS BACKUP_SHA256=$sum BASS_UPPER=9/15 NEW_FULL_UPPER=0"
