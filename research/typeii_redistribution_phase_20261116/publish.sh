#!/usr/bin/env bash
set -euo pipefail
stage=${1:?phase};root=$(git rev-parse --show-toplevel);p=research/typeii_redistribution_phase_20261116
branch=research/bass-typeii-redistribution-phase-20261116-r1
cd "$root";test "$(git branch --show-current)" = "$branch"
git add "$p";git diff --cached --check
python3 - <<'PY'
import subprocess
p='research/typeii_redistribution_phase_20261116/'
f=subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines()
if not f or not all(x.startswith(p) for x in f):raise RuntimeError('stage path or empty commit contract')
PY
git commit -m "science(typeii): $stage evolving redistribution and phase-space measure"
git push --set-upstream origin "$branch"
sha=$(git rev-parse HEAD);test "$sha" = "$(git ls-remote origin "refs/heads/$branch"|cut -f1)"
b=/home/cosmosapjw/research_backups/bass_typeii_redistribution_phase_20261116;mkdir -p "$b"
out="$b/${stage}_${sha:0:12}.zip";git archive --format=zip HEAD "$p" > "$out";unzip -tq "$out" >/dev/null
h=$(sha256sum "$out"|cut -d' ' -f1)
printf '%s\t%s\t%s\t%s\n' "$stage" "$sha" "$h" "$out" >> "$b/STAGE_RECEIPTS.tsv"
echo STAGE=$stage HEAD=$sha HOST_SHA=$h EXTERNAL=NOT_ATTEMPTED_KNOWN_ENOSPC UPPER_DAG=9/15 NEW_FULL=0
