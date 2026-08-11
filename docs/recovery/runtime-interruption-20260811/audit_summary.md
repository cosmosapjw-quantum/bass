# Bounded salvage audit summary

## Scope

The audit covers only:

1. Git provenance for base `c9cd8ecb8765649ace77ea8f22890ff4c24153eb`;
2. absence of the intended remote recovery ref before publication;
3. original source identity, exact third-party-manuscript exclusion, retained-member
   identity, container safety, and bounded secret checks for the sanitized
   `bianchireview87` archive;
4. post-seal remote identity of the sealed recovery payload and the direct-child,
   fast-forward-only receipt-carrier precondition;
5. exact identity, role, disposition, and default-deny handling of the 16 supplied
   next-stage inputs; and
6. separate scope containment of the sealed payload and post-seal follow-up.

It does not audit solver science, revalidate A0 v2, reconstruct review05, compare the
archive to the lost original, or authorize any later development stage.

## Independent results

### Remote preflight pass

- Repository visibility and connected write permissions: PASS
- `agent/longrun-checkpoints` resolves to the required base: PASS
- Base tree and sole parent verified from the fresh clone: PASS
- Intended recovery ref absent before publication: PASS

### Post-seal identity pass

- Remote branch resolved to sealed commit `9a8f35ff107f4eb8053477bff2b9c8c77633b43a`: PASS
- Sealed tree `95233a394939d6a48bdc8b59fee199ffae65cb10`: PASS
- Sole parent `c9cd8ecb8765649ace77ea8f22890ff4c24153eb`: PASS
- GitHub view and `git ls-remote` agreement: PASS
- Sanitized archive blob and SHA-256 agreement: PASS
- Direct-child, non-force receipt-carrier precondition: PASS

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

- Sealed payload modified pre-existing tracked files: 0
- Post-seal follow-up changed only 10 allowlisted recovery-document paths: PASS
- Protected harness, historical manifest, legacy partial, and sanitized quarantine trees:
  unchanged
- Production `src/` files added or modified: 0
- A0/A0B/A1/Task 10 files changed: 0
- Merge or force-update action: prohibited
- Control-plane implementation, A0 mutation, A0B, A1, and Task 10: not started

### Next-stage input-lock pass

- Sixteen supplied input identities: current-runtime SHA-256 and byte counts recorded
- Existing 15-input durable hash ledger: matched
- Toolchain/xAct/legacy large-binary vendoring: prohibited
- Quarantine and historical lanes remain non-authoritative for production
- Control-plane status: `PREPARED_NOT_STARTED`

## Residual risk

The archive remains untrusted executable material. In particular, its pickle must not be
deserialized. A zero-finding bounded scan is not a guarantee that future execution is safe.
The recovery commit preserves the sanitized bytes and original-source provenance; it does
not preserve the excluded full manuscript member and does not admit the archive into an
implementation authority path. Bibliographic citations, short quoted passages, and
transcribed equations remain as part of the surviving research records.
