# CE1-M S1 · verified donor code under CE1-L physical-input locks

Parent PR251 exact HEAD `cd7e7efdb384580ae44c0cdca873eba018a404e2`; donor PR249 exact HEAD `0370f99aea7cc457b32a3ebc259a343a82ac5a9f`. Child PR252 is **isolated Draft**. Original physical source, MPFR primitive, RK4/Hermite and frozen `1e-5` target unchanged.

- Donor module `bianchi/nonperturbative/einstein_tabulated_source_canonical.py` Git blob `1c905278f7a109e15f5e20d3ac7f931bdcf99433`; donor original 7 tests blob `30d85661adf7851317ebcb23c1aab6a2e4a08da3`. Both exact Git blob identity verified on new branch.
- Eight new `test_ce1m_integrated_adversarial.py` cases: original physical cell/energy/table immutable lock, individual signed mass fail, current extra ray cardinality fail, legal positive same-cardinality mutable ray/mass accepted and recertified, no invalid shifted geometry clip.
- Isolated Python 3.13.5+MPFR6: donor+parent selected `101 passed/14.15 s`; new adversarial `8 passed/0.86 s`; **whole scoped `python -m pytest -q tests/nonperturbative`: 127 passed in 20.14 s, exit0**. This is a scoped Python oracle result, not a native production proof.
- **Fresh refinement8 (384 rays, four full MPFR192 RK4/Hermite panels):** `9.411551484445186e-6` scoped CE1-M h upper, meets unchanged `1e-5` target; old CE1-I `1.2273903547843227e-5` did not. Original PR251 physical-input source/path SHA256 **EXACT match**, same four panel m_j and source forcing. Evidence `research/ce1m_20261029/REF8_REPLAY.py` and immutable S1 archive; no claim of speedup.
- S1 archive `BASS_CE1M_S1_20261029.zip`: **13429 bytes, 12 files, CRC PASS**, SHA-256 `c8f601a89bffff568511b4c4a4480f8496e49a8dcda2096509664e4b22095e65`.
- GitHub scoped workflow and installed-wheel integrity smoke have been published; final workflow status to be read from live GitHub before final closeout. S1 source proof does **not** close distinct-author R6/C9, native full production, full MPFR formal program validation.
- Upper DAG **9/15**, 21 edges; CE-1 PARTIAL, `production_ready=false`, `merge_ready=false`, `auto_next=false`.

**Next S2:** independent sampled original-cell vs stored-ray pressure discrepancy falsification, confirm no hidden novel proof-premise hole, publish final report, CI and dual provider receipts. No new top-level science node or automatic merge.
