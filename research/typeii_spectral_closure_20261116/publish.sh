#!/usr/bin/env bash
set -euo pipefail
stage=${1:?stage};root=$(git rev-parse --show-toplevel);p=research/typeii_spectral_closure_20261116
branch=research/bass-typeii-spectral-closure-20261116-r1
backup=/home/cosmosapjw/research_backups/bass_typeii_spectral_closure_20261116
external=/mnt/extdrive/research_backups/bass_typeii_spectral_closure_20261116
cd "$root";test "$(git branch --show-current)" = "$branch"
git add "$p";git diff --cached --check
git diff --cached --name-only | while IFS= read -r f;do case "$f" in "$p"/*) ;; *) echo OUT_OF_SCOPE_STAGED;exit 2;;esac;done
git commit -m "science(typeii): $stage spectral collision closure"
git push -u origin "$branch";sha=$(git rev-parse HEAD)
test "$sha" = "$(git ls-remote origin "refs/heads/$branch"|cut -f1)"
mkdir -p "$backup" "$external";out="$backup/${stage}_${sha:0:12}.zip"
git archive --format=zip HEAD "$p" > "$out";unzip -tq "$out" >/dev/null
h=$(sha256sum "$out"|cut -d' ' -f1);cp "$out" "$external/";test "$h" = "$(sha256sum "$external/$(basename "$out")"|cut -d' ' -f1)"
printf '%s\t%s\t%s\t%s\n' "$stage" "$sha" "$h" "$out" >> "$backup/STAGE_RECEIPTS.tsv"
echo "STAGE=$stage HEAD=$sha ZIP_SHA=$h EXTERNAL_READBACK=PASS UPPER_DAG=9/15 NEW_FULL=0"
