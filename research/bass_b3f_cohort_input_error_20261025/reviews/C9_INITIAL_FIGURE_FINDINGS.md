# C9 actual initial figure findings

The independent reviewer actually viewed both saved PNGs after the first
three metered commands. The raw scientific results are internally consistent
with the frozen contract; these are concrete presentation findings.

Original renderer SHA256:
`63002fda6170fd0d75682705fcd3d037c9d6fc81f7a1efb4c5ed9d5660514e3d`.

Original overview SHA256:
`8763eaf8609ffeca2cd900205b62879a6c7dcb0e40d484aabb27e1a59f219b00`.

Original terms SHA256:
`310eac507c1f4cac6f7b2b5d046ff22207f45c1f84598284a66fcdc62e76d9bb`.

## C9-V1 — overview footer overlaps x-axis labels

Target: FINITE_INPUT_OVERVIEW.png, native180x100mm layout.

Observed pixels: the line beginning "Panel (a): solid = bound..." occupies
the same vertical band as both "Prescribed epsilon" x-axis labels. The
footnote and the labels visibly overprint each other.

Impact: the data points remain visible, but the axis meaning and line-style
key are not cleanly readable. Final figure admission is pending correction.

Minimum correction: change only renderer margins/footnote placement (or
native height if necessary) to separate the two x-axis labels from both
footer lines while retaining minimum font size and the exact-zero note.

## C9-V2 — terms legend is clipped by the canvas top

Target: FINITE_INPUT_TERMS.png, native90x145mm layout.

Observed pixels: the upper legend's top row reaches beyond the saved canvas;
the "Map" and "Density and det R" row is visibly cut at the top edge.

Impact: the stacked-bound component key is incomplete in the saved image.
The numeric source and bars are unaffected.

Minimum correction: reserve enough top margin or move the external legend
inside the native canvas with separation from panel title and data axes.

## Bounded repair and preserved evidence

The reviewer requests one controller-authorized presentation-only repair.
The lower-tier executor must preserve the original renderer, both original
PNGs and these findings. Preserve byte identities of raw sweep, test result,
all-rowsCSV and numerical summary; rerun only the saved-result summary/plot
command. Tests and the scientific sweep do not require a rerun.

Afterward root and reviewer should directly view both regenerated PNGs and
close these two findings if corrected. This record is the initial observed
failure and must remain alongside the final closure. It is not a failure of
the finite perturbation theorem or an instruction to add new scientific
gates. No renderer or scientific code was edited by the reviewer.
