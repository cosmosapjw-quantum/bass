#!/usr/bin/env bash
# Run from the repository root after cargo fetch --locked.
set -euo pipefail

rec_sha=d3cc6e0120061f113d28e7a3a55a2e3dd561e81e
rei_sha=41e4592aa494b48929dcd23fc8504c169a98a908
for entry in "rec:$rec_sha" "rei:$rei_sha"; do
    name=${entry%%:*}
    sha=${entry#*:}
    url="https://github.com/cosmosapjw-quantum/${name}_bianchi.git"
    grep -Fxq "${name}_microphysics = { git = \"$url\", rev = \"$sha\" }" _rustcore/Cargo.toml
    grep -Fxq "source = \"git+$url?rev=$sha#$sha\"" _rustcore/Cargo.lock
done

tree=$(cargo tree --manifest-path _rustcore/Cargo.toml --locked --offline --edges normal --prefix none)
if grep -Eq '^(pyo3|pyo3-ffi|pyo3-build-config|numpy) ' <<< "$tree"; then
    echo 'FAIL: Python dependency in default normal Rust dependency tree' >&2
    exit 1
fi
echo 'PASS: exact REC/REI revisions; no Python packages in default normal dependency tree'
