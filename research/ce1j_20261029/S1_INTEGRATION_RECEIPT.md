# CE1-J S1: scoped canonical candidate code + regression snapshot

**Status:** S1 implementation and local verification complete; upper DAG **9/15** unchanged, CE-1 PARTIAL.

- Parent PR245 `9cd3063b0c411a0289f6975659906fd1f64b2817`; this remains a separate Draft PR246 child, no merge.
- PR243/244 fresh source majorant and exact Hermite left-knot check imported without altering physical equations. Source blobs:
  - `einstein_interval.py`: `3a3f384e793a59f0779cb09a21dd74c1ae7d0c3a`
  - `einstein_tabulated_time.py`: `b2047a7a7fd64e8a1148d242ee32840f648184b5`
  - `einstein_tabulated_local.py`: `c6f1a59db197766aae401d9868fcea3951f26c24`
- Legacy CE1-I stale-cache exception replaced by positive mass-rebind **recertification** regression; Hermite origin guard moved to shared CE1-G call. Existing read-only scientific inputs and target remain unchanged.
- Local Python 3.13.5 focused test invocation: **95 PASS in 16.92s, exit 0** (the previous combined baseline RED was 91 PASS +1 FAIL from obsolete test expectation).
- New tests: PR244 `test_ce1g_independent_audit.py` and CE1-J `test_ce1j_variant_contract.py`. Local test blob `7beb078d730eac01ada7af02f722b9f489b97f20`.
- Final CI and ref8/ref16 scientific replay are not claimed at S1. S1 ZIP: `BASS_CE1J_S1_20261029.zip` 25,742 bytes / 10 members / SHA256 `d989f2c41feea4baf7ceea430f32880ff8650148cc6a2402eed68e4a694d1787`, CRC verified.
- `production_ready=false`, `merge_ready=false`, `auto_next=false`, independent distinct-author review NOT_RUN, native subagent NOT_RUN.
