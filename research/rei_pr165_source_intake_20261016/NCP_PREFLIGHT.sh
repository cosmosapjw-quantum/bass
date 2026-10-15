#!/usr/bin/env bash
set -euo pipefail
# Read-only NCP preflight, no job creation or modification.
ssh -i "${NCP_KEY:?NCP_KEY required}" -o BatchMode=yes -o ConnectTimeout=8 \
  root@"${NCP_HOST:?NCP_HOST required}" -p 22 \
  'hostname; nproc; free -h; df -h /; /root/.cargo/bin/rustc --version; /root/.cargo/bin/cargo --version; ps -eo pid,etime,%cpu,rss,args | grep -E "REI_FLRW_COVARIANT|axbi|full_campaign|rux" | grep -v grep || true'
