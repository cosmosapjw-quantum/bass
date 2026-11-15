#!/usr/bin/env bash
set -euo pipefail
stage=${1:?stage};root=$(git rev-parse --show-toplevel)
p=research/typeii_hyrec_atommode_audit_20261102
branch=research/bass-typeii-hyrec-atommode-audit-20261102-r1
backup=/home/cosmosapjw/research_backups/bass_typeii_hyrec_atommode_recovery_20261115
cd "$root";test "$(git branch --show-current)" = "$branch"
git add "$p"
git diff --cached --check
git diff --cached --name-only | grep -v '^research/typeii_hyrec_atommode_audit_20261102/' && { echo OUT_OF_SCOPE_STAGED;exit 2; } || true
git commit -m "science(typeii): $stage recovered HYREC mode comparison"
git push origin "$branch"
sha=$(git rev-parse HEAD);test "$sha" = "$(git ls-remote origin "refs/heads/$branch"|cut -f1)"
mkdir -p "$backup";out="$backup/${stage}_${sha:0:12}.zip"
git archive --format=zip HEAD "$p" > "$out";unzip -tq "$out" >/dev/null
hash=$(sha256sum "$out"|cut -d' ' -f1)
printf '%s\t%s\t%s\t%s\n' "$stage" "$sha" "$hash" "$out" >> "$backup/STAGE_RECEIPTS.tsv"
printf 'STAGE=%s HEAD=%s BACKUP_SHA=%s UPPER_DAG=9/15 NEW_FULL=0\n' "$stage" "$sha" "$hash"
