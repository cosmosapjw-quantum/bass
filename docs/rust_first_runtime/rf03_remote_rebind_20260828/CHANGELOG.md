# R4 changes against bootstrap 5c25431474fc10a151a2cef8a95c6b77d0e807f8

## Reproduced defects

1. R3 used `text=True` and `.stdout.strip()` for both metadata and file content.
   This removes final newlines and can convert CRLF to LF. The required raw
   digest then fails although the Git blob is unchanged. The old validator was
   imported byte-for-byte (blob cb96f7d65ef45e43456e40264fadc1d1c5cc94ad).
2. After a diagnostic raw-only repair, the next child invocation fails with
   `FAIL: R1 package moved`. The immutable R2 validator compares the moving R1
   branch tip to historical b7cda09d..., but publishing the earlier bootstrap
   already advanced that branch to 5c254314.... Both defects were reproduced
   with real Git subprocesses in explicitly synthetic repositories.

## Repair

Split raw byte reads from metadata-line decoding. Use `git cat-file blob`
without text conversions, `write_bytes`, and the original six raw hashes.
Use `sys.executable` for the unchanged original R2 offline checker.

Explicitly supersede ONLY R2's live identity-check entry with the R4 equivalent:
exact RF-02C branch/head/tree, exact R2 branch/head/tree/index, all six source
blob identities, and historical R1 commit b7cda09d... / tree 1eba9fc7....
R1's moving branch is no longer mistaken for its historical input object.
This is not a skipped gate or a normalized expected digest. R2's original
manifest, semantic checker, source hashes, authority contract and bytes remain
unchanged. Do not edit or rewrite the frozen R2 package to make a test pass.

Materialization now retains an explicitly requested NEW directory. Existing
paths are refused, not deleted. No trap removes the handoff before it is read.
The prompt names the immutable R1 context path and overrides all old bootstrap
and nested-live commands. Source/implementation scope stays unchanged.

## Verification boundaries

16 unittest methods passed, including nine raw-byte edge cases, full synthetic
Git intake, advanced historical branch, mutated digest, wrong source/tree/index,
original R2 semantic rejection, interpreter selection, and preservation checks.
The original failure and raw-only follow-on failure are stored in evidence/.
The source-code tests use synthetic source bytes and do not certify physics.
No authenticated production-clone `--live`, RF03-AUTH-01, native build, or
RF-03 implementation was run here. Remote publication is recorded separately
by the exact delivery receipt after the commit exists.

## Unchanged boundaries

No main/RF-02C/R2-authority source mutation, EOS or temperature-law change,
production implementation, tolerance change, scientific promotion, performance
claim, BASS-12--15 optimization import, or non-mock merge/ready transition.
