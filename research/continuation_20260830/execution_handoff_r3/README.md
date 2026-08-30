# BASS RF-04 execution handoff R3

## Controlling outcome

```text
PASS_REMOTE_RAW_OBJECT_PAYLOAD_CLOSURE_ONLY
PASS_REMOTE_R5_LOCATOR_BYTE_READBACK_ONLY
R4_EXACT_HOST = STOP_INVALID
R5_EXACT_HOST_AUTHENTICATED_CLONE = DEFERRED_LOCAL
LOCAL_EVIDENCE_GATE = NOT_REACHED
LOCAL_01 = NOT_STARTED_GATE_NOT_REACHED
LOCAL_02 = NOT_STARTED
NO_PASS_RF04
```

R5 repairs only the Git 2.43 execution-environment incompatibility in R4.  It
does not claim that the exact authenticated host has run intake, and it makes
no scientific promotion.  The controlling remote bytes are R5 locator commit
`57ec56393de43eb78d758222f78478aea8b14517` and publication v6 commit
`cb9b2c84c593733e6f8944b417d3876a2aad9407`.  This R3 package is a
non-authoritative local-execution addendum subordinate to those bytes.

## What changed from R2

- R2 depended on R4.  The user-reported R4 exact-host run stopped before
  canonical intake because `/usr/bin/git 2.43.0` rejects the global
  `--no-lazy-fetch` option.  Its reported result was 2 PASS, 5 FAIL, and 23
  ERROR out of 30; optimized tests and 18-file intake were not run.
- R5 selects the CLI flag only when supported and requires a private
  guarded/control promisor differential before source payload object reads.
  Production object queries also deny every transport.
- R5 binds the selected Git executable and upload-pack target, quotes the
  helper command, allows filesystem-encoded helper paths, uses a minimal child
  environment, hashes object-store inventory during the capability proof, and
  caches capability only after identity-checked cleanup succeeds.
- R5 passed 56/56 with zero skips in four fresh lanes: Git 2.43.0 and 2.51.1,
  each under normal and optimized Python 3.12.3.
- The current gate is not `BLOCKED_BY_MISSING_LOCAL_EVIDENCE`: that gate has
  not yet been reached.  Run R5 intake first.  Only then inspect the preserved
  local objects and report that blocker if their exact identities are absent.

## Exact remote authority

- Corrected payload: commit `16f5811beb7d73fae800ff90caf30f69deebc9fd`,
  tree `85a9164e01ea77d312b185809b3698363c750526`, manifest 18/18.
- R5 locator: commit `57ec56393de43eb78d758222f78478aea8b14517`,
  tree `ef1b4463547fad4aa36d068a6b538b806d1b15ac`.
- R5 manifest: blob `50ab58fa5268e18d9a857cee32bd2e475999194a`,
  SHA-256 `5f9b95207a252293c2678872dd5945a718157fdd83b40a8c24920794151a5d6e`.
- R5 ZIP: blob `e3ac728cb499528a71a2e50161b92293daf69f80`,
  SHA-256 `4f31624154c2b8c09383f17e1dac8977134c21ef024d876dc9e2b04727fcd486`.
- Publication v6: commit `cb9b2c84c593733e6f8944b417d3876a2aad9407`,
  tree `1d9dded878c7e6dc7323bd2def8a89bc85df36a0`, blob
  `1580e8ce9ecb6f4d1d85c7c208e4610a62b01747`, SHA-256
  `d597c92eda2944a4d4ce6a4525b1eb0c3e234c1965594ca1fc482188d3c09cca`.
- PR #66 remained open, draft, and unmerged.  `main` remained
  `d9e5ba7577ccb05b648b11ea7ac991bf6e09d8b9`.

## Preserved evidence

Five R2 evidence files are copied byte-for-byte into this package.  They are
historical, non-authoritative diagnostics—not the current gate state and not
production source.  `SANDBOX_SPIKE_RECEIPT.json` and
`NONFINITE_RECEIPT_FINDING.md` retain their old timing and conclusions for
provenance.  Do not execute or reinterpret them as proof that R5 intake or the
preserved-object gate passed.

The two nonfinite findings become mandatory LOCAL-01 tests only after R5
intake and the preserved-local-object gate pass.  Run each on the authenticated
baseline and candidate.  Each candidate must yield either a fully finite
success or an existing authorized typed failure through the real carrier and
PyO3 mapping.  Any safety fix must be separate from the byte-frozen telemetry
commit.

## Use

Read `LOCAL_ONLY_PROMPT.md` on the host containing the authenticated BASS clone
and preserved local objects.  Start at its remote readback and R5 intake gate.
Do not create an implementation worktree, apply the patch, or run scientific
gates before intake passes.  Do not merge or mark PR #66 ready, change `main`,
or force-push.  `FAIL` or `UNTESTED` at any required LOCAL-01 item keeps
LOCAL-02 closed and the claim at `NO_PASS_RF04`.
