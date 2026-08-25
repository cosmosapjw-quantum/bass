# RF-00 contract-repair closeout

- Verdict: RF-00 contract repair passes focused local proof; PR #25 remains draft and unmerged.
- Start: `4fd541967341f81999a5d1b7147dbb04849ade22` / tree `01fbfff1f3f05a64436f41b644960886709a491e`.
- Code head: `8f531540a0483541d088e222b1622ec9bc25ffd7` / tree `d14ede2b55e7e6d00f7aff767f7951f4b8012c02`; the containing receipt commit is the live branch head.
- AUD-12: package-root JAX initialization is removed; minimal install is native wheel plus NumPy; optional oracle dependencies use typed lazy loaders and the `python-oracle` extra.
- Backend contract: 72 public compute routes are inventoried; supported routes require verified native payloads, explicit oracles stay Python transitively, and ten unmigrated domains remain visibly transitional.
- Development source builds require the explicit `BASS_ALLOW_UNVERIFIED_NATIVE_DEV=1` override and emit a typed diagnostic.
- Focused proof: 65 policy/import tests, 31 affected-route tests, and a fresh no-index minimal install importing 25 backend modules passed.
- Review: the single bounded adversarial review found three blocker groups; one repair-closeout fixed all three. The report and exact logs are indexed by machine evidence.
- Timing: the preserved chart ratio `1.030368...` and cold-import ratio `1.009126...` are `EXPLORATORY_ONLY`; there is no performance or no-regression acceptance claim and no benchmark was rerun.
- Native artifact: `REUSED_NATIVE_R3_NO_R4_CONTRACT_REPAIR`; `_rustcore` object identity and Cargo.lock are unchanged.
- Reused: native r3 restore/readback, R5b PR #21, Wolfram candidate PR #22 as unpromoted reference, and unchanged scientific/generated lanes.
- Draft PR: <https://github.com/cosmosapjw-quantum/bass/pull/25>; live checks and final branch identity must be read there.
- Machine evidence: `artifacts/rust_first_runtime/rf00/EVIDENCE.json` (`7445b266ff46c5008d7f443f50c2a2d498e905163c027353c1f6a0f5dadd5960`).
- Raw manifest: `artifacts/rust_first_runtime/rf00/RAW_MANIFEST.sha256` (`2cc23c593a01067d9fe640217e93dd93d16d1dd529ef0d905e557d06600b13eb`).
- Handoff: `docs/rust_first_runtime/HANDOFF.md`.
- Exactly one next action: execute RF-BENCH-00 with controlled cpuset/cgroup, effective CPU set, SMT isolation, migrations, pressure/steal, frequency/throttling, and perf running-ratio evidence; otherwise classify it exploratory with no acceptance claim.
