#!/usr/bin/env bash
set -euo pipefail
stage=${1:?stage};p=research/typeii_redistribution_20261116
root=$(git rev-parse --show-toplevel);cd "$root"
branch=research/bass-typeii-redistribution-20261116-r1
backup=/home/cosmosapjw/research_backups/bass_typeii_redistribution_20261116
test "$(git branch --show-current)" = "$branch"
if [ "$stage" = P2 ];then
 git add "$p"/redistribution.py "$p"/source_geometry.py "$p"/verify_phase_and_kernels.py "$p"/test_transport.py "$p"/DESIGN_AND_THEORY.md "$p"/STAGE_LEDGER.md "$p"/publish.sh "$p"/SYMBOLIC_CHECKS.json "$p"/PHASE_AND_KERNEL_VERIFICATION.json "$p"/PHASE_KERNEL_RUN.log "$p"/PHASE_KERNEL_REFINED.log "$p"/INITIAL_SKY_QUADRATURE_FAILURE.log "$p"/SKY_RESOLUTION_DIAGNOSIS.json "$p"/TDD_GREEN_ATTEMPT.log
else
 git add "$p"
fi
if git diff --cached --name-only | grep -qv "^$p/";then echo OUT_OF_SCOPE_STAGED;exit 2;fi
git diff --cached --check
git commit -m "science(typeii): $stage evolving redistribution and phase measure"
git push --set-upstream origin "$branch"
sha=$(git rev-parse HEAD);test "$sha" = "$(git ls-remote origin refs/heads/$branch|cut -f1)"
mkdir -p "$backup";out="$backup/${stage}_${sha:0:12}.zip"
git archive --format=zip HEAD "$p" > "$out";unzip -tq "$out" >/dev/null
hash=$(sha256sum "$out"|cut -d' ' -f1)
printf '%s\t%s\t%s\t%s\n' "$stage" "$sha" "$hash" "$out" >> "$backup/STAGE_RECEIPTS.tsv"
printf 'STAGE=%s HEAD=%s ZIP_SHA=%s HOST_VERIFIED EXTERNAL_NOT_ATTEMPTED_KNOWN_ENOSPC UPPER=9/15 NEW_FULL=0\n' "$stage" "$sha" "$hash"
