# BASS native delta failure ledger

Run: `BASS-NATIVE-DELTA-20260824T092016Z`
Source: `bff2852af3536d0d9e8badc3e5e2ad024f299278` / `603791eee595dac4ec8c9f177d53842695b3932f`
Verdict: `PARTIAL/BLOCKED`

| Issue | Status | Established cause or boundary |
|---|---|---|
| FMT-001 | PASS | Actual tracked rustfmt 1.8.0 drift. Four generators now own stable formatter contracts; remaining files received pinned formatting. |
| CLIPPY-001 | PASS | Source diagnostics under clippy 0.1.94, not missing packages. Root-pattern fixes preserve public Python names/argument lists and do not weaken `-D warnings`. |
| TYPEII-BIND-001 | PASS | Receipt remained bound to predecessor input after the already-authoritative B1 adapter correction. Rebound metadata; fixture outputs unchanged. |
| CODEGEN-BYTE-001 | PASS | NumPy/BLAS reduction order caused low-bit remap-oracle drift. Fixed scalar binary64 order reproduces existing JSON/Rust bytes. |
| GEN-MANIFEST-001 | PASS | A historical scalar manifest incorrectly included a composition root later expanded with polarized code. Scalar/polarized ownership is now explicit. |
| COEFF-DRIFT-001 | PASS | Platform-dependent signed-zero serialization. Exactly 214 zero sign bits canonicalized; all nonzero bits unchanged. |
| PSTF-PROV-001 | PASS | SVD pseudoinversion was environment-sensitive for an exact full-column-rank rational problem. Exact rational left inverse preserves normalization/invariants. |
| REVIEW-SPHERE-001 | PASS | Initial lint rewrite silently accepted a too-short distribution. Slice-first iteration restores fail-closed behavior and has Rust/Python boundary coverage. |
| REVIEW-PROVENANCE-001 | PASS | Historical Type-II test counts looked current after manifest changes. They are explicitly legacy; the current claim is only the fresh 8-test scope. |
| R5B-001 | BLOCKED | Canonical True-frozen q absolute difference is `2.6915318931952648e-17`; a discarded nalgebra candidate closes only this node. |
| R5B-002 | BLOCKED | True-ratio_scalar q absolute difference remains `5.3830637863905295e-17`. Diagnostics localize cancellation/operation-order sensitivity, not an established semantic defect. |
| FORMULA-BYTES-EXT | BLOCKED | Historical formula hash label exists, but named source bytes are absent/unmapped. |
| WOLFRAM-XACT-EXT | PARTIAL | Imported package/basic canonicalization and abstract PSTF receipt only; no project driver/formula, project replay, or xAct-to-Rust result. |
| M11-DEFERRED | NOT_RUN | Explicitly outside this delta. |

## Failed attempts and retry discipline

- Coefficient and PSTF focused tests each had one changed test/reconstruction precondition before final PASS; no unchanged deterministic failure was retried.
- Generated formatting required two distinct generator-contract corrections before final PASS; each rerun followed changed source bytes.
- One disposable nalgebra-LU candidate ran exactly the two R5b RED nodes and returned 1 PASS/1 FAIL. It was rejected; no second algorithm or unchanged-node retry ran.
- The first staging copy pointed at a nonexistent r1 root Python-lock path. Its partial directory was preserved; one corrected-source-path retry passed byte equality.
- The first archive pair was deterministic but retained an upstream executable bit. Invalid archives were moved to quarantine; one independently mode-normalized rebuild passed.
- The first policy scan falsely classified legitimate vendored `target`/`registry` source directories as caches. One scoped-policy retry retained exact vendor/license/secret checks and passed.
- The first payload review found the manifest sidecar absent. It was added and verified before commit/push.
- The first restore implementation reached Cargo 123 PASS and native import but failed independent fail-closed review: it did not parse every bound vendor/wheelhouse record or isolate host config. The hardened script added exact set/size/SHA checks and config/override/special-file/credential rejection.
- The first hardened staging restore then stopped on the intentionally stale content manifest. After regenerating the manifest from changed staging bytes, one retry passed exact dependencies, offline Cargo 123, isolated install, and native call.
- The first final-archive command used relative output paths after `cd` and failed before creating archive bytes. One absolute-path retry produced two byte-identical archives.
- The first final-payload copy used the artifact payload name where the archive-root prefix was required. The partial allowlisted parts were preserved; one corrected source-path retry added the identical reassembler and passed.
- The first artifact-branch preflight expected the source worktree to be clean, but it correctly retained untracked build-only vendor/config inputs. A new sibling worktree was used; no user/source files were cleaned.
- Artifact r2 normal push, `ls-remote` identity, fresh shallow clone, ordered reassembly, XZ test, and content-manifest readback passed without retry.

## Stop boundary

Closing the local RED requires one user scientific decision: keep the cancellation-sensitive relative comparison of endpoint-error scalars, or authorize a scientifically justified state/residual parity contract. No tolerance, reference, seed, grid, dependency, formula, sign, or normalization change was made. Do not begin `BASS-8B.2A_TYPED_ELECTRON_STATE_BINDING` before that decision closes R5b.
