# Stage backup policy

Every promoted stage is preserved in two identity domains.

## GitHub

- Create a child branch from an exact verified commit.
- Use non-force commits and a Draft PR to the exact formula-authority branch.
- Read back commit, tree, changed paths and committed blobs.
- Never conflate Git object IDs with archive SHA-256 identities.

## Dropbox

- Use a versioned stage path and do not silently overwrite an older packet.
- Preserve the repository-relative source tree, receipt and manifest.
- Confirm the first destination path explicitly before writing.
- Treat Dropbox metadata as a backup locator, not formula authority.

A missing backup is `BACKUP_NOT_RUN`, not PASS.
