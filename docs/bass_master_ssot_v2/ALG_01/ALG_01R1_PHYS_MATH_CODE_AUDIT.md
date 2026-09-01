# ALG-01R1 PHYS–MATH–CODE audit

**Stage:** `ALG_01R1`  
**Tested source:** `8b62a56a537e1a7f9f86d012e50f7161faa05b68`  
**Tested tree:** `c52f69b4f886efdb29d610b2de0eed3fe7f30971`  
**Verdict:** `PASS_COMMITTED_SOURCE_AND_DROPBOX_RESTORED_REPLAY`

## 1. Equation-to-code map

| Contract | Production symbolic path | Regression path |
| --- | --- | --- |
| public type count and witness obligations | `Kernel/Bianchi/TypeSpec.wl` | `ALG01R1ExceptionalAndCovariance.wlt` |
| exceptional group/momentum constraints | `Kernel/Bianchi/Witnesses.wl` | canonical and hostile witness tests |
| shear-survival witness | `ExceptionalShearSurvivalQ`, `WitnessObligationReport` | `EXCEPTIONAL_SHEAR_DELETE` |
| exact O(3) data transform | `Kernel/Geometry/FrameCovariance.wl` | proper/improper Type II and VI_-1/9 tests |
| improper pseudotensor parity | `n'=det(R) R n R^T` | missing-`det(R)` hostile test |
| stage admission | `scripts/run_stage.wls --stage ALG_01` | W0 + W1 + ALG-01 + R1 suites |

## 2. TDD sequence

RED was observed against pre-fix source
`41acee69ec3d196a2ee39abc3a5c0a8eb99e4a93`:

```text
0 succeeded
5 failed
0 not evaluated
```

The old validator accepted a shear-deleted exceptional witness with
`pass=true` and no failed checks. The covariance API and public-count/witness
obligation fields were absent.

Focused post-fix verification passed `11/11`.

## 3. Committed-source parser failure and root cause

The first Dropbox-restored committed-source replay did **not** pass:

```text
58 succeeded
5 failed
0 not evaluated
```

The failing boundary was not the physics formula. Wolfram parsed a multiline
condition of the form

```wl
pattern /; predicate
  && predicate
```

as invalid syntax. A minimal parser probe reproduced:

```text
inline &&        PASS
newline-leading &&  FAIL
And[...]         PASS
```

The single repair replaced multiline leading `&&` conditions with explicit
`And[...]` in `FrameCovariance.wl`. No transform equation, sign, coefficient,
witness or test expectation changed.

## 4. Final restored replay

A fresh stateless Wolfram kernel reconstructed the stage from three immutable
layers:

```text
W0_W1/sources
  -> ALG_01R1/sources
  -> ALG_01R1/r1_sources
  -> ALG_01R1/r1_fix1
```

Final result:

```text
status                         PASS_DROPBOX_RESTORED_ALG01R1
downloaded files               20
overlay Git blob SHA-1          8/8 PASS
Wolfram tests                   63 succeeded / 0 failed / 0 not evaluated
JSON schemas                    PASS
canonical witnesses             5/5 PASS
hostile witnesses               6/6 detected
O(3) covariance cases           4/4 exact zero
wrong improper parity mutation  detected; residual L1 = 4
```

Runtime:

```text
Wolfram 15.0.1 for Linux x86 (64-bit)
xAct/xTensor 1.3.0
xPerm 1.2.4
xAct SHA-256 7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be
```

## 5. Regression and ownership analysis

PASS:

- W0 xAct environment and W1 convention/IR tests remain in the same full
  `TestReport`;
- old five canonical witnesses remain green;
- the new hostile shear deletion is generated from the real witness registry,
  not from a prefilled result;
- the covariance tests call the exported transform implementation;
- a non-orthogonal matrix returns `Failure`;
- no Rust/Python production solver path changed;
- no REC/REI provider or RF04 route changed.

## 6. Ranked code ledger

| Rank | Finding | Disposition |
| --- | --- | --- |
| P0 | None after final restored replay | PASS |
| P1 | Old self-consistent witness path missed shear deletion | CLOSED by generated mutation |
| P1 | New covariance module initially failed committed-source parsing | CLOSED by parser-safe `And[...]`; failure retained in evidence |
| P2 | No GitHub Actions workflow selected this symbolic branch | CI remains `UNOBSERVED`, not green |
| P2 | No second independent CAS replay of R1 | Wolfram exact replay plus hostile tests only |
| P2 | Background curvature/evolution code remains absent | correctly withheld |
| P3 | Python plot generation was unavailable in this session | Wolfram diagnostic plot and exact data retained; no Python-pass claim |

## 7. Test sufficiency boundary

The tests are sufficient for the scoped algebra witness and frame-covariance
claims. They are not sufficient for:

- Levi-Civita connection coefficients;
- spatial Riemann/Ricci curvature;
- constraint propagation;
- all eleven family background equations;
- arbitrary-L kinetic code generation;
- numerical or observational claims.
