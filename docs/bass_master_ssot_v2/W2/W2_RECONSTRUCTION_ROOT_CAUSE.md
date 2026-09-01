# W2 reconstruction failure root cause — mixed backup lineage

## Symptom

A first reconstruction produced:

```text
74 succeeded
4 failed
0 not evaluated
```

The equation count remained 9 and the Gauss–Codazzi coefficient registry still validated, so the failure did not isolate to a W2 formula.

## Root cause

The reconstruction combined pre-R1 ALG-01 sources stored in the historical `W2_AFTER_ALG01` backup with the later `ALG01R1ExceptionalAndCovariance.wlt` test.

```text
classification = MIXED_BACKUP_LINEAGE
physics_formula_failure = false
```

## Controlled reproduction

The run was rebuilt from the exact current parent backup

```text
/bianchi/bass/backups/BASS-MASTER-SSOT-V2/2026-09-01/ALG_01R1
```

including its final `r1_fix1/FrameCovariance.wl`, followed by W2-only overlays.

Result:

```text
78 succeeded
0 failed
0 not evaluated
ReportSucceeded = True
```

No W2 tensor definition, sign, normalization, dimension, equation coefficient or structural zero was changed.

## Preventive rule

Every successor backup names one exact parent backup and restores only successor-owned overlays. A historical composite directory is never admitted as the current parent merely because its stage label is similar.
