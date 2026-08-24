# Wolfram/xAct replay record

## Project archive

```text
path     /mnt/data/xAct_1.3.0.tgz
size     15613945 bytes
SHA-256  7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be
```

Extracted project layout:

```text
/mnt/data/xact_stage/xAct/xTensor/xTensor.m
```

The required parent path is therefore:

```wl
$Path = Prepend[$Path, "/mnt/data/xact_stage"];
Needs["xAct`xTensor`"];
```

## Fresh stateless plugin execution

The connected Wolfram kernel cannot see the chat container's `/mnt/data`.
For the fresh replay it downloaded the official xAct 1.3.0 Unix archive into
its temporary filesystem, extracted it, prepended the extraction parent to
`$Path`, and loaded xTensor. The downloaded archive had the same byte count
and SHA-256 as the project archive.

Loaded versions:

```text
Wolfram 15.0.1 for Linux x86 (64-bit), 2 July 2026
xTensor  1.3.0, 29 December 2025
xPerm    1.2.4, 29 December 2025
```

Exact xTensor residuals:

```text
ProjectorIdempotence          0
ProjectorTangent              0
ScreenTransversality          0
ScreenTransversalityTangent   0
```

## Native replay

On a host with Wolfram CLI available:

```bash
./host_replay/run_xact_audit.sh
```

The script verifies the project archive hash, extracts it if needed, and runs
`source/xact_screen_projector_witness.wl`.

## Separation of responsibilities

xAct verifies the abstract screen tensor geometry. The complete finite
collision right/left/projector/Kato algebra is checked independently by:

- exact SymPy (`source/exact_projector_kato_witness.py`);
- exact stateless Wolfram matrix algebra
  (`source/exact_projector_kato_witness.wl`);
- the selected Lebedev-26 finite carrier and randomized numerical audit.

This separation prevents an xAct package-load receipt from being misreported
as a proof of the full collision operator.
