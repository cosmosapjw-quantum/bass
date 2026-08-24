# HANDOFF

## STATE

- Repository: `https://github.com/cosmosapjw-quantum/bass`; canonical anchor `agent/recovery/background-evolution-v87-integrated-20260824` at `0d1203da778c5e92fce4c9bbf24c8044c5b46018`.
- R5b: `agent/recovery/r5b-contract-20260824-r1` at `b810092755837ccfa96502aa7e132a50c3fcbd33`, draft PR #21.
- Performance: `agent/recovery/measured-performance-20260824-r1`; accepted implementation head `efb3a45986820659e5bcbec2677729f28616e736`, tree `5fe6c47538c17c770738836634c01d1333de40e1`, plus the remote-read metadata head on draft PR #23. The delivery worktree must be clean after its atomic evidence commit; the final branch head/tree are an external remote-readback receipt and are not self-embedded.
- Wolfram: `agent/recovery/generic-wolfram-candidate-20260824-r1` at `75f0b128634ec60b853519f9f6d530f113b54a81`, draft PR #22. All three PRs were open/draft/unmerged/CLEAN at closeout.

## OUTCOME

- R5b: 34 focused PASS; acceptance-observable correction closed without production physics, tolerance, or reference change.
- Baseline weighted medians: 0.3124499165 s (1T), 0.2974174922 s (12T). Q B1/B2 were rejected below 10%; no aggregate speedup is claimed.
- Geometry Candidate B is exact-digest and five-test focused-green, but paired timing is `BLOCKED_HOST_CONTENTION`; its unaccepted source/test bytes are preserved in machine evidence.
- Wolfram packet is statically green and unpromoted; no local execution or historical-authority claim occurred.

## OPEN ITEMS

- No R5b semantic defect is established. The only local delivery blocker is a valid quiet-host paired measurement for Candidate B.
- Historical formula bytes and project replay remain absent/open; the generic candidate is not production authority.

## EVIDENCE

- `artifacts/performance/EVIDENCE.json`, SHA-256 `f4ab66fc575122460d554c152deca5ad6c57fd80cb85e0ee11c892318abc358a`; it contains exact candidate bytes, commands, inputs, raw-evidence digests, and the host blocker.
- Immutable native r2: `artifact/native-repro-bundle-20260824-r2` at `61045b6e5a0d7b026437e0d3586df66706578161`; archive SHA-256 `ef0f35b76ab4ef4877ed577afe391ed677a7a6767bcbc64db62dd853d757afca`. No r3 exists.
- Work-mode packet: `compiler/wolfram/generic_bianchi_candidate/HANDOFF_WORKMODE.md` on PR #22; manifest SHA-256 `f162f8f94a1bab0bd7d2fdce08d94e307ffebdd1c11201e195e43779a3d05aad`.

## BOUNDARIES

- Do not merge or mark ready, move canonical, promote authority, change tolerance/reference/dependencies, invoke Wolfram locally, or rerun inherited PASS without a changed precondition.

## EXACTLY ONE NEXT ACTION

- Wait for the recorded two-snapshot quiet-host condition, then execute the two frozen Candidate B paired commands in `EVIDENCE.json`; accept only with exact output identity, both median ratios <=0.90, focused correctness, and the memory gate.
