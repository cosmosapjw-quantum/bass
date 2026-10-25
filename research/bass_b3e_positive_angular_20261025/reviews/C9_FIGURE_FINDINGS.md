# C9 actual figure findings before bounded repair

## Reviewed original artifact

`results/POSITIVE_ANGULAR_SUMMARY.png`,2080×1920 pixels,
SHA256 `3af3cfc838368a9d038f2081a39d1bf3f407e7c4abcc0737b64c35e85a734db3`.
The reviewer actually viewed this PNG. This is not an assumed layout verdict
from source code or a reconstruction of a lost image.

The numerical result is PASS_SCOPED on its frozen domain:22rows,162row gates
all true, independent saved-tensor Frobenius/CSV reconciliation has no
discrepancy. Figure readiness remains pending the targeted corrections below.

## C9-V1 — legend obscures a zero-bound datum

- **Object:** upper error panel, G5 ideal truncation bound at the displayed
  zero floor, near the lower-right region.
- **Observed evidence:** the legend box occupies the same data region as the
  G5 green square/zero triangle and the nearby green segments; the marker is
  visibly obscured behind the legend. The other two exactzero bound markers
  remain outside the box.
- **Effect:** the distinction between an exactzero ideal bound and a small
  actual floating error is harder to read for G5. The underlying raw values
  remain correct.
- **Minimal repair:** move the upper legend outside the data axes and preserve
  all raw points, labels, the explicit zero symbol and the2e-8 target.

## C9-V2 — final-size readability

- **Object:**13inch/330.2mm-wide overview,9pt base fonts and8pt legend.
- **Observed evidence:** the actual image has long endpoint labels rotated
 65degrees. Its source specifies13in width. Scaling it to180mm reduces9pt
  text to4.91pt and8pt text to4.36pt; scaling to90mm reduces these to2.45pt
  and2.18pt. These are geometric final-size calculations, not a claim that
  a separately rendered90mm version has already been inspected.
- **Effect:** the user-provided figure audit's180–183mm/89–90mm reading
  context is not supported by the current dense layout.
- **Minimal repair:** use a180mm-native layout with compact endpoint labels
  and a clear label key, plus final labels/legend at least7pt. Provide a
  separately laid-out90mm version/panels if that width is part of the output
  contract; do not simply halve the dense overview and claim it readable.

## Authorized repair boundary requested from root

Only summary/plot formatting needs correction. Preserve the original plot
source, original PNG and this finding, rerun only the summary/plot command,
and confirm the5 numerical outputs remain byte-identical:
POSITIVE_ANGULAR_SWEEP.json,TEST_RESULTS.json,NUMERICAL_SUMMARY.json,
ALL_ROWS.csv,SELECTOR_COST.csv. No new test, quadrature sweep, reference
evaluation, IVP, source/fixture/model/tolerance change is needed.

The independent reviewer does not edit implementation code. Root authorizes
the lower-tier bounded repair, then the reviewer inspects its actual result
and closes these findings with specific final artifact identities.
