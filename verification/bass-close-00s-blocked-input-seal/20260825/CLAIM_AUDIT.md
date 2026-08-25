# Claim audit

| Claim | Status | Evidence | Risk | Required fix |
|---|---|---|---|---|
| Earlier candidate is internally valid | VALIDATED | 51/51 manifest, 28/28 native tests | Same-name collision | Keep quarantined identity |
| Declared final is reproducible authority | FORBIDDEN | Identity declaration only | Exact bytes absent | Supply exact ZIP or corpus |
| Historical 57/53/500/80/120 evidence exists | VALIDATED historical evidence | Static receipt and standalone artifacts | No source binding | Keep unbound |
| Rows 7–10 may be promoted | FORBIDDEN | Missing final identity | Provenance gap | Complete BASS-CLOSE-00 first |

No claim was upgraded. The former receipt-level final-support interpretation is
downscoped to historical evidence pending exact-byte recovery or an explicit,
fully reproducible superseding package.
