# `bianchireview87` quarantine provenance

## Source and sanitized-container identity

The public repository file is derived from the uploaded scratch archive by deleting one
third-party manuscript member. It is intentionally not a byte-for-byte container copy.

| Field | Value |
|---|---|
| Uploaded name | `bianchireview87.tar(1).gz` |
| Session-local source | `project_sources/16-bianchireview87.tar-1-.gz` |
| Original bytes | `2298253` |
| Original SHA-256 | `6bb094d30a6d24b3feee11a1d9ae2827049945dae8281ed37d0d0796a6e9ea84` |
| Sanitized repository path | `recovered_sources/quarantine/bianchireview87_20260811/bianchireview87.tar.gz` |
| Sanitized bytes | `2270244` |
| Sanitized SHA-256 | `337f2aed1b959b0fcb9bf78a35b17a2a182b24d280a882d025800c113d3ff30f` |

## Public exclusion

| Field | Value |
|---|---|
| Excluded member | `./refs_neutrinos_LewisChallinor.tex` |
| Excluded bytes | `63066` |
| Excluded SHA-256 | `324058b7241662ea18a772f65971fe0a7be838a7e8070a3eb808c39770732c78` |
| Reason | No compatible general-redistribution license was established for the full third-party manuscript. |

The transformation copied the original tar, deleted exactly the named member, and
recompressed the result with deterministic gzip name/time fields (`gzip -n -9`). The
original archive is not committed. Replay verifies that every retained member name, type,
metadata field recorded in `archive_members.tsv`, and regular-file hash matches the source.
Bibliographic citations, short quoted passages, and transcribed equations from the paper
remain in surviving research records. The full 63,066-byte manuscript member, its exact
full-member hash, and its two author-email strings do not.

## What the archive is

It is a sanitized reconstructed source/report snapshot with 469 tar members. It contains Python,
Rust, tests, audit material, reports, PDFs, one NumPy `.npz`, and one Python pickle. It
contains no Git object database or bundle.

Classification: `RECONSTRUCTED`.

## What the archive is not

It is not:

- an exact recovery of the interrupted Task 3–10 Git history;
- evidence of byte identity with the lost original runtime;
- an A0 or A0B authority;
- an authorized production overlay;
- a safe base for A1 or Task 10;
- an authorization to execute included scripts, deserialize the pickle, or import code.

## Handling contract

1. Treat every member as inert evidence unless a later, separately authorized intake gate
   admits it.
2. Do not overlay it onto a production tree.
3. Do not deserialize `bianchi/generated/riemann_frame.pkl` merely to inspect it.
4. Use `archive_members.tsv` for the complete names/type/size/hash inventory.
5. Preserve and compare the sanitized container SHA-256 before any future analysis.
6. Use the original source SHA-256 only as provenance; do not substitute the unsanitized
   archive for the public repository artifact.
