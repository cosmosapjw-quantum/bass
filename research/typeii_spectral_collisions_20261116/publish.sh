#!/usr/bin/env bash
set -euo pipefail
s=${1:?stage};root=$(git rev-parse --show-toplevel)
p=research/typeii_spectral_collisions_20261116
branch=research/bass-typeii-spectral-collisions-20261116-r1
cd "$root";test "$(git branch --show-current)" = "$branch"
git add "$p"
if git diff --cached --name-only | grep -v "^$p/";then echo OUT_OF_SCOPE_STAGED;exit 2;fi
git diff --cached --check
git commit -m "science(typeii): $s electron-frame spectral collision moments"
git push --set-upstream origin "$branch"
h=$(git rev-parse HEAD);test "$h" = "$(git ls-remote origin refs/heads/$branch|cut -f1)"
b=/home/cosmosapjw/research_backups/bass_typeii_spectral_collisions_20261116
ext=/mnt/extdrive/research_backups/bass_typeii_spectral_collisions_20261116
mkdir -p "$b" "$ext";out="$b/${s}_${h:0:12}.zip"
git archive --format=zip HEAD "$p" > "$out";unzip -tq "$out" >/dev/null
sha=$(sha256sum "$out"|cut -d' ' -f1)
cp "$out" "$ext/";test "$sha" = "$(sha256sum "$ext/$(basename "$out")"|cut -d' ' -f1)"
printf '%s\t%s\t%s\t%s\n' "$s" "$h" "$sha" "$out" >> "$b/STAGE_RECEIPTS.tsv"
echo "STAGE=$s HEAD=$h ZIP_SHA256=$sha EXTERNAL_READBACK=PASS UPPER_DAG=9/15 NEW_FULL=0"
