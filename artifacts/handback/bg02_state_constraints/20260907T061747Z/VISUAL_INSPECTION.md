# Actual figure inspection

Inspected both generated PNG figures directly: constraint_vs_shear.png and
deletion_response.png (1152 x 720 each). Corresponding SVG files were generated
from the same figures; SVGs were not separately rasterized for inspection.

Titles, axes, mathematical labels and legend are readable and remain inside the
canvas. The first legend occupies the empty lower middle without hiding points.
At u=0 the full/deleted markers coincide at H=1 and the orange square overlays
the blue marker; this is the actual equality of returned values, not a plotting
error. The blue segments still meet that point. The five difference markers in
the second figure are distinct, with no label/data clipping. No layout repair
was needed.

Data were read from the actual repair1 SC_FINAL payload, equal to the saved
extracted STATE_CONSTRAINT_RESULT.json: u=(-2,-1,0,1,2), Hfull=(-3,0,1,0,-3),
Hdeleted=(1,1,1,1,1), sigma2=(8,2,0,2,8). The second figure displays the arithmetic
difference of those same observed H values: (4,1,0,1,4). Expected curves were
not substituted for measurements. The first figure's segments guide the eye
across five separate algebraic inputs; they are neither time trajectories nor
computed intermediate states. Fixed reference length only; no convergence,
transport or time-integrated stability claim.

The original non-PASS stdout was also passed to the supplied plotter: it
preserved the extracted invalid result and refused to generate figures.
Both successful figures were generated only from the accepted repair1 run.
