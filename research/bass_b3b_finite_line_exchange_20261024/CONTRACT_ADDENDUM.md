# C5 input convention approved during implementation

The isolated finite source transaction requires the incoming core.Source U/J
arrays to be zero. A nonzero incoming transfer is rejected without mutation.
This prevents discarding an unrelated rate and makes the zero already-applied
U/J output unambiguous. Root approved this concrete convention after the
implementer identified the ambiguity. The frozen physical formulas, scope,
tolerances and original CONTRACT.md hash are unchanged.

