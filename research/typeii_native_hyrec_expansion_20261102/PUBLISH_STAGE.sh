#!/usr/bin/env bash
set -euo pipefail
stage="${1:?R1_C1...R10_C10}"
repo=/home/cosmosapjw/worktrees/bass-typeii-native-hyrec-expansion-20261102-r1
branch=research/bass-typeii-native-hyrec-expansion-20261102-r1
backup=/home/cosmosapjw/research_backups/bass_typeii_native_hyrec_expansion_20261102
cd "$repo"
test "$(git branch --show-current)" = "$branch"
git add research/typeii_native_hyrec_expansion_20261102
git diff --cached --check
if git diff --cached --quiet;then echo NO_STAGE_CHANGE;exit 27;fi
git commit -m "science(typeii): ${stage} source-native HYREC atomic Hubble callback"
git push --set-upstream origin "$branch"
sha="$(git rev-parse HEAD)"
remote="$(git ls-remote origin "refs/heads/$branch"|cut -f1)"
test "$sha" = "$remote"
out="$backup/${stage}_${sha:0:12}.zip"
git archive --format=zip HEAD research/typeii_native_hyrec_expansion_20261102 > "$out"
unzip -tq "$out" >/dev/null
digest="$(sha256sum "$out"|cut -f1 -d' ')"
printf '%s\t%s\t%s\t%s\n' "$stage" "$sha" "$digest" "$out" >> "$backup/STAGE_RECEIPTS.tsv"
test -z "$(git status --porcelain=v1)"
echo "STAGE=$stage HEAD=$sha REMOTE_READBACK=PASS ZIP_SHA256=$digest BASS_UPPER=9/15 NEW_FULL_NODES=0"
