# SYNC-MAP-01 findings and split obligations

The bounded inventory contains 66 path records: 22 for each active repository
lineage. It is a path map, not an EquationIR equivalence result.

## Mixed-owner paths

### REC characteristics

```text
src/full_bianchi_hyrec/background/characteristics.py
```

Candidate split:

```text
BASS import
  common observer/tetrad convention
  standard boost and characteristic geometry

REC owner
  hydrogen-frame specialization
  recombination source/boundary adaptation
```

### REC directional-face admission

```text
src/full_bianchi_hyrec/trajectory/directional_face_admission.py
```

Candidate split:

```text
BASS import
  common frame and direction transformation

REC owner
  26-node boundary object
  red/blue/grazing event predicates
  source-defined face admission
```

### REC Wolfram frame/face oracle

```text
formal/rec_next03/wolfram/verify_frame_face_event.wls
```

This must be decomposed into explicit replay targets. The common frame part is
an authority-effect-NONE replay of BASS; the face/event part is an
independent oracle for REC. It cannot remain an unbound second authority.

### REI BASS integration substrate

```text
src/rei_bianchi/bass_integration_substrate.py
```

Candidate split:

```text
BASS owner
  MatterSource envelope, conventions and custody contract

REI owner
  late-time source values and REI-specific adapter state
```

## Non-duplicates retained

REC's atomic rates, HyRec physical flux, two-photon/Raman channel, source
transfer and deposition remain REC-owned. REI's conservation-reduced map,
MPRK/SDIRK/Taylor-remainder formulas, OTS source algebra and interval runtime
remain REI-owned. These are not moved to BASS merely because BASS consumes
their eventual providers.

## Next semantic work

`SYNC-MAP-02` must:

1. lower BASS formula sources into canonical EquationIR records;
2. split multi-formula files into individual formula IDs;
3. normalize index names, exact rationals, dimensions and convention hashes;
4. map REC and REI replay candidates to those exact IDs;
5. classify each relation as identical, specialization, independent oracle,
   owned extension or genuine duplicate;
6. produce an impact DAG, but no official Jira edge mutation.
