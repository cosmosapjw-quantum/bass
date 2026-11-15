#!/usr/bin/env bash
set -euo pipefail
stage=${1:?stage};p=research/typeii_clock_interface_20261115;branch=research/bass-typeii-clock-interface-20261115-r1
root=$(git rev-parse --show-toplevel);cd "$root";test "$(git branch --show-current)" = "$branch"
git add "$p"
python3 - <<'PY'
import subprocess
p='research/typeii_clock_interface_20261115/'
files=subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines()
if not files or any(not f.startswith(p) for f in files):raise RuntimeError('no stage change or out-of-scope staged file')
PY
git diff --cached --check;git commit -m "science(typeii): $stage proper-clock thermal radiation interface"
git push --set-upstream origin "$branch";head=$(git rev-parse HEAD)
test "$head" = "$(git ls-remote origin "refs/heads/$branch"|cut -f1)"
b=/home/cosmosapjw/research_backups/bass_typeii_clock_interface_20261115;e=/mnt/extdrive/research_backups/bass_typeii_clock_interface_20261115
mkdir -p "$b" "$e";f="$b/${stage}_${head:0:12}.zip"
git archive --format=zip HEAD "$p" > "$f";unzip -tq "$f" >/dev/null
h=$(sha256sum "$f"|cut -f1 -d' ');cp "$f" "$e/";test "$h" = "$(sha256sum "$e/$(basename "$f")"|cut -f1 -d' ')"
printf '%s\t%s\t%s\t%s\n' "$stage" "$head" "$h" "$f" >> "$b/STAGE_RECEIPTS.tsv"
echo "STAGE=$stage HEAD=$head ZIP_SHA256=$h EXTERNAL_READBACK=PASS UPPER_DAG=9/15 NEW_FULL=0"
