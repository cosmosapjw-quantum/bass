# Bounded salvage audit summary

## Scope

The audit covers only:

1. Git provenance for base `c9cd8ecb8765649ace77ea8f22890ff4c24153eb`;
2. absence of the intended remote recovery ref before publication;
3. original source identity, exact third-party-manuscript exclusion, retained-member
   identity, container safety, and bounded secret checks for the sanitized
   `bianchireview87` archive;
4. scope containment of this recovery-only change.

It does not audit solver science, revalidate A0 v2, reconstruct review05, compare the
archive to the lost original, or authorize any later development stage.

## Independent results

### Remote identity pass

- Repository visibility and connected write permissions: PASS
- `agent/longrun-checkpoints` resolves to the required base: PASS
- Base tree and sole parent verified from the fresh clone: PASS
- Intended recovery ref absent before publication: PASS

### Archive security/structure pass

- Original source archive identity: PASS
- Exact exclusion of `./refs_neutrinos_LewisChallinor.tex`: PASS
- Retained member identity and sanitized container integrity: PASS
- Member safety and nested NPZ integrity: PASS
- Git-object-source check: PASS, with zero Git artifacts found
- Bounded secret checks: PASS, with zero findings
- Dedicated scanner availability: NOT AVAILABLE and explicitly disclosed
- Public quarantine preservation decision: PASS within this bounded scope

### Scope pass

- Existing tracked files modified: 0
- Production `src/` files added or modified: 0
- A0/A0B/A1/Task 10 files changed: 0
- Merge or force-update action: prohibited

## Residual risk

The archive remains untrusted executable material. In particular, its pickle must not be
deserialized. A zero-finding bounded scan is not a guarantee that future execution is safe.
The recovery commit preserves the sanitized bytes and original-source provenance; it does
not preserve the excluded full manuscript member and does not admit the archive into an
implementation authority path. Bibliographic citations, short quoted passages, and
transcribed equations remain as part of the surviving research records.
