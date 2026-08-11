# BASS runtime-interruption recovery inventory — 2026-08-11

## Recovery boundary

This inventory is the final pre-infrastructure salvage action approved for the BASS
`RUNTIME_INTERRUPTION_RECOVERY`. It preserves currently available evidence only. It does
not mutate an A0 candidate, freeze A0B, authorize A1, resume Task 10, merge a branch, or
promote reconstructed material to exact Task 3–10 authority.

Inventory capture time:

- UTC: `2026-08-11T02:49:49Z`
- Asia/Seoul: `2026-08-11T11:49:49+0900`

Public-archive sanitization time:

- UTC: `2026-08-11T06:26:01Z`
- Asia/Seoul: `2026-08-11T15:26:01+0900`

## Isolated Git checkout

- Repository: `cosmosapjw-quantum/bass`
- Recovery branch published by create-only publication:
  `agent/recovery/runtime-interruption-20260811-inventory`
- Fresh-clone base ref: `agent/longrun-checkpoints`
- Base commit: `c9cd8ecb8765649ace77ea8f22890ff4c24153eb`
- Base tree: `eae7ea44bc762df2d3b173e37bd3de9f1ea0487e`
- Sole base parent: `5365125a584b1c8c384e7cebfb6dd44aff8268de`
- Base status before recovery files were added: clean (`git status --porcelain=v1` empty)
- Base object check: `git fsck --full --strict` exited 0
- Root checkout contained no production `src/` tree.

The mutation blast radius is limited to this recovery directory and
`recovered_sources/quarantine/bianchireview87_20260811/`. Existing recovery records,
harness files, reconstructed A0 branches, production paths, and historical overlays are
protected and unchanged.

## Remote preflight

The GitHub repository was independently observed as public and writable by the connected
account (`admin`, `maintain`, `push`, and `pull` permissions reported true).

| Remote ref | Commit | Tree | Sole parent | Classification |
|---|---|---|---|---|
| `main` | `d9e5ba7577ccb05b648b11ea7ac991bf6e09d8b9` | not needed for this salvage | not needed | `DURABLE_VERIFIED` |
| `agent/longrun-checkpoints` | `c9cd8ecb8765649ace77ea8f22890ff4c24153eb` | `eae7ea44bc762df2d3b173e37bd3de9f1ea0487e` | `5365125a584b1c8c384e7cebfb6dd44aff8268de` | `DURABLE_VERIFIED` |
| `agent/route-a-a0` | `98d289f4e237b9229560fbf2229d0f303966b63d` | `fc0488447c32411ff327f7d03b652ddd67727afd` | `c9cd8ecb8765649ace77ea8f22890ff4c24153eb` | `SUPERSEDED` |
| `agent/route-a-a0-v2` | `854ff3d9d5a0f4fef4dd8cb221fcc95003faed95` | `d4717bf95fdd93502c3b12512d8d2a77195a16c1` | `c9cd8ecb8765649ace77ea8f22890ff4c24153eb` | `RECONSTRUCTED` |

The intended new recovery ref was absent in both `git ls-remote` and the GitHub branch
query before publication. `agent/route-a-a0-v3` was also absent. No force update is
authorized.

## Post-seal remote identity

The recovery payload was published and then verified through both the connected GitHub
repository view and `git ls-remote`:

- Sealed commit: `9a8f35ff107f4eb8053477bff2b9c8c77633b43a`
- Sealed tree: `95233a394939d6a48bdc8b59fee199ffae65cb10`
- Sole parent: `c9cd8ecb8765649ace77ea8f22890ff4c24153eb`
- Relationship to the forensic boundary: one commit ahead, zero commits behind
- Sanitized archive Git blob: `91b53b10cd5ba741a267a1532ba72be9b6ac012a`
- Verification time: `2026-08-11T09:26:59Z`
- Receipt: `REMOTE_IDENTITY_RECEIPT.json`

The follow-up carrying the receipt uses a predecessor-seal model: it binds the exact
payload commit above and is required to be its direct fast-forward child. The carrier does
not attempt to encode its own Git SHA inside its own tree. Its identity is resolved from
the branch after publication, which avoids an impossible recursive self-hash.

## Sanitized quarantined archive

- Uploaded name: `bianchireview87.tar(1).gz`
- Session-local source used for this capture:
  `project_sources/16-bianchireview87.tar-1-.gz`
- Original source byte size: `2298253`
- Original source SHA-256:
  `6bb094d30a6d24b3feee11a1d9ae2827049945dae8281ed37d0d0796a6e9ea84`
- Preserved repository path:
  `recovered_sources/quarantine/bianchireview87_20260811/bianchireview87.tar.gz`
- Sanitized byte size: `2270244`
- Sanitized SHA-256:
  `337f2aed1b959b0fcb9bf78a35b17a2a182b24d280a882d025800c113d3ff30f`
- Container integrity: `gzip -t` PASS and full tar listing PASS
- Members: 469 total; 433 regular files and 36 directories
- Uncompressed regular-file bytes: 5,294,354
- Unsafe paths, duplicate paths, links, devices, FIFOs: 0
- Git roots, objects, refs, packs, indexes, or bundles: 0

The public repository copy is intentionally not byte-identical to the uploaded source.
Before publication, exactly one third-party manuscript was removed because a compatible
general-redistribution license was not established:

- Excluded member: `./refs_neutrinos_LewisChallinor.tex`
- Excluded member bytes: `63066`
- Excluded member SHA-256:
  `324058b7241662ea18a772f65971fe0a7be838a7e8070a3eb808c39770732c78`

All 469 retained member names, types, metadata, and regular-file hashes replay against the
original source archive. Bibliographic citations, short quoted passages, and transcribed
equations from the paper remain in surviving research records. The full 63,066-byte
manuscript member, its exact full-member hash, and its two author-email strings do not. The
original archive remains outside this public Git history.

The archive is classified `RECONSTRUCTED` and remains quarantine/reference material. It is
not an exact Git-object source, an A0 authority, a production tree, or evidence that the
original Task 3–10 implementation has been recovered.

## Bounded security result

Two independent read-only passes found no credential, private-key, or high-confidence token
match in the sanitized archive. The parent pass scanned all 433 regular members directly
from the tar stream. The independent pass additionally classified 419 text files and 14
binaries and extracted text from all 10 PDFs. Filename, path-traversal, special-file,
nested-NPZ, and exact-exclusion checks also passed.

Dedicated scanners (`gitleaks`, `trufflehog`, `detect-secrets`, and `git-secrets`) were not
installed. That limitation is recorded rather than silently upgraded to a trusted-scanner
claim. The bounded result supports public preservation of the sanitized quarantine archive,
not a universal proof that arbitrary future execution is safe.

`bianchi/generated/riemann_frame.pkl` is a Python pickle. It was treated as inert bytes and
must not be deserialized unless its producer and execution environment are independently
trusted.

## Authority status at this boundary

- `EXACT_TASK_3_10_IDENTITY: MISSING_OR_MASKED`
- `ROUTE_A_STATUS: RECONSTRUCTED_A0_PATH_SURVIVES_REMOTELY`
- `A0_STATUS: A0_CANDIDATE`
- `A0B_STATUS: NOT_FREEZE_ELIGIBLE`
- `A1_AUTHORIZED: NO`

The earlier exhaustive exact-object search has no genuinely new Git-object source to
inspect. This archive is a new source snapshot, not a new object store. Repeating the prior
104-locator search is therefore not authorized by this evidence.

## Next-stage preparation boundary

All 16 currently supplied project-source identities are consolidated in
`NEXT_STAGE_INPUT_LOCK.yaml`. The lock records roles and dispositions; it does not vendor
the Rust distribution, xAct, unsanitized archive, legacy automation kit, or quarantined
scripts into an executable path. Existing durable repository representations remain in
their separate lanes:

- exact low-ell acceptance contract under `docs/specs/`;
- harness-only background/high-ell provenance under `harness/`;
- historical partial Rust/Python overlay under `recovered_sources/legacy_partial/`;
- sanitized `bianchireview87` snapshot under `recovered_sources/quarantine/`.

The next stage is `DURABLE_ORCHESTRATION_CONTROL_PLANE`, status
`PREPARED_NOT_STARTED`. It must begin from the final fast-forward tip of this recovery
branch, first revalidate the sealed predecessor and input lock, and remain separate from
the Route A A0 candidate. This preparation does not authorize control-plane
implementation, A0 mutation, A0B freeze, A1, Task 10, scientific execution, dependency
installation, or merge.
