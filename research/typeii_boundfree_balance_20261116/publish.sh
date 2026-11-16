#!/usr/bin/env bash
set -euo pipefail
stage=${1:?stage};root=$(git rev-parse --show-toplevel);p=research/typeii_boundfree_balance_20261116
branch=research/bass-typeii-boundfree-balance-20261116-r1
backup=/home/cosmosapjw/research_backups/bass_typeii_boundfree_balance_20261116
external=/mnt/extdrive/research_backups/bass_typeii_boundfree_balance_20261116
cd "$root";test "$(git branch --show-current)" = "$branch"
git add "$p";git diff --cached --check
git commit -m "science(typeii): $stage level-resolved bound-free detailed balance"
git push --set-upstream origin "$branch"
head=$(git rev-parse HEAD);test "$head" = "$(git ls-remote origin "refs/heads/$branch"|cut -f1)"
mkdir -p "$backup" "$external"
f="$backup/${stage}_${head:0:12}.zip";git archive --format=zip HEAD "$p" > "$f";unzip -tq "$f" >/dev/null
hash=$(sha256sum "$f"|cut -d' ' -f1);cp "$f" "$external/";test "$hash" = "$(sha256sum "$external/$(basename "$f")"|cut -d' ' -f1)"
printf '%s\t%s\t%s\t%s\n' "$stage" "$head" "$hash" "$f" >> "$backup/STAGE_RECEIPTS.tsv"
printf 'STAGE=%s HEAD=%s ZIP_SHA256=%s EXTERNAL_READBACK=PASS UPPER_DAG=9/15 NEW_FULL=0\n' "$stage" "$head" "$hash"
