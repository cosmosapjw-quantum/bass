# CE1-Q GitHub parent-CSV representation repair (CI-only independent child)

- Root cause: PR #258 GitHub copy of six CSVs has a literal `<PARSED TEXT FOR SHEET ... TAB NAME: ...>index,` leading line and an `index` column, induced by a previous spreadsheet-text retrieval stage, unlike the original byte-frozen CSV contained in CE1-P original ZIP SHA `162097533f0bc88ec5ddee8f10edcc08aaf4b81cbf2e4c14c42982dbf73ca6b7`.
- Diagnostic: GitHub CE1-Q first CI #40904291940 failed at CSV decoding, prior BASS native Rust compile/self-test passed. This is an **artifact/provenance packaging error**, not a physical equation, array, or numerical integrator defect. No parent PR #258 mutation.
- Correction: add exact CE1-P raw CSV byte snapshots in independent CE1-Q child `parent_verified/data/*` and use those in GitHub scientific replay. Original six source cells, all trajectories and scientific tolerances are unchanged.
- CI recomputes entire six-channel native sky output in fresh job, checks saved-output and independent SciPy tests. CLI reads the source CE1-P generator from parent PR #258 (source `.py` unchanged).
- Exact SHA-256 of all six raw CSV snapshots:

```json
{
  "continuum_GL24_history.csv": "f2c27274861b4130a2c62a00d68d09c12a30134b7033e20b2687fd2d041b7da1",
  "continuum_GL40_history.csv": "c863be4c122dd5f9b6da4fb10545190b38178db4f879a64b129689a68e0671e0",
  "stored_ref16_history.csv": "89ace11905988e3d8df8345ff8a8fddd3da6517b703ca6f532f711698639ea14",
  "stored_ref1_history.csv": "e94c1865e3f72fa90ea9ab9fc3a32a6fc24b87e20b129b94c4340d5292823170",
  "stored_ref4_history.csv": "7207b661d5765d1a09372e1faa6ca8da48392b5ca8eaf71831f1e96d0b378e0f",
  "stored_ref8_history.csv": "d1e0c54af0307fb515a15998a39ed47d205a770888577927688de65818a55958"
}
```

- CE1-Q original SHA-locked full physics evidence archive remains unchanged. This is a create-only CI repair addendum, not an excuse to rewrite original archive.
