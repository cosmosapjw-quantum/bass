# Generic Bianchi equation-generator candidate

This packet is an unpromoted, type-ignorant Wolfram/xAct candidate.  It derives
from exact Lie-algebra data and dispatches adapters by exact invariants, never by
the optional Bianchi type label.  It does not modify SymIR v1, production Rust,
or any generated production source.

Authority boundary:

- historical formula label `3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361`
  is `UNRESOLVED_REFERENCE`; its source bytes are absent and it is not a DAG
  parent;
- `WOLFRAM-WORKMODE-20260824-R1` is reused only as an environment/basic
  xAct/PSTF receipt, not as a BASS project replay;
- all outputs of this packet remain
  `CANDIDATE_UNPROMOTED_FORMULA_BYTES_ABSENT` until Work-mode execution, and a
  successful run can establish only `VALIDATED_NEW_CANDIDATE`.

The Work-mode driver validates the packet manifest, loads xAct, validates each
exact `BianchiSpec`, derives the generic frame expressions once, applies only
exact-invariant adapters, and emits canonical typed SymIR v2.  It performs a
cold calculation followed by a hash-keyed warm-cache calculation and requires
byte-identical canonical results.

Local validation is deliberately static:

```bash
python -m pytest -q compiler/tests/test_generic_bianchi_packet.py
python -m py_compile compiler/wolfram/generic_bianchi_candidate/verify_result.py
python compiler/wolfram/generic_bianchi_candidate/verify_result.py --self-check
```

Static structural lint is not Wolfram syntax or execution evidence.  Follow
`HANDOFF_WORKMODE.md` for the only authorized execution lane.
