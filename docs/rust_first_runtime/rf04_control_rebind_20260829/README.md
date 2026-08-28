# RF-04 control rebind

Current exact authority:

```text
agent/plans/rf04-sci-auth-intake-20260828-r1
f18e491f19f45accc8c87eb56b4a24f15a8a3d6c
tree 3fd8201a3cb15bf8d882dd28d37bf0c31e8af7e0
PR #47 OPEN / DRAFT / UNMERGED
```

`695908d8501be141b163641cbe61e334d2189358` is a historical merge probe only. Its SCI-AUTH payload was reverted because the verifier is HEAD-relative to RF-02B. RF-04 consumes the validated SCI-AUTH result by exact checkpoint, not by source transplant.

Candidate B is rejected, PR #34 is closed unmerged, and BASS-13 through BASS-15 are not inputs. Exact next action: `RF04-RED-01`.
