# Handoff to ChatGPT Work mode

Continue from the delta-only recovery state; do not restart r1. The canonical branch remains unchanged at `0d1203da778c5e92fce4c9bbf24c8044c5b46018`. Review candidate `agent/recovery/native-repro-delta-fixes-20260824-r1` ends at `bff2852af3536d0d9e8badc3e5e2ad024f299278`, tree `603791eee595dac4ec8c9f177d53842695b3932f`.

The immutable r2 binary delivery is remotely verified:

- branch/head: `artifact/native-repro-bundle-20260824-r2` / `61045b6e5a0d7b026437e0d3586df66706578161`
- path: `repro/native/BASS-NATIVE-DELTA-20260824T092016Z`
- archive: `175949544` bytes, SHA-256 `ef0f35b76ab4ef4877ed577afe391ed677a7a6767bcbc64db62dd853d757afca`
- bundle/content manifests: `d7cf9758afc1c8395f5f7bcca0b8f38cb788640a340edb42bce379f75ccfba8f` / `61e4216d23ec33949e621b78ea2da1a755cd2d154741532b298a63ac48d4f91a`
- wheel: `bianchi_rustcore-0.1.0-cp312-cp312-manylinux_2_34_x86_64.whl`, SHA-256 `b58fe7400c51cf0016b877a681758ebb9896d07cfb3f80be7ca82df64b734d10`
- remote readback: local/remote commit equal; fresh shallow clone; 21-part ordered reassembly; XZ and 8,592-file content manifest PASS
- final archive restore: exact 8,397-file/176-directory vendor and 22-wheel wheelhouse PASS; empty-Cargo-home offline workspace `123 passed`; isolated native import/call PASS

Closed engineering items: FMT-001, CLIPPY-001, TYPEII-BIND-001, CODEGEN-BYTE-001, GEN-MANIFEST-001, COEFF-DRIFT-001, PSTF-PROV-001, REVIEW-SPHERE-001, and REVIEW-PROVENANCE-001.

Still RED: R5B-001 (`2.6915318931952648e-17`) and R5B-002 (`5.3830637863905295e-17`). One disposable nalgebra candidate closed only the first node and was rejected. No tolerance/reference/seed/grid/formula/dependency change occurred.

The imported Wolfram receipt remains narrow: package load/basic dummy canonicalization and the abstract 3D PSTF projector PASS, but repository formula bytes/project driver are absent. Project replay and xAct-to-Rust remain OPEN. Do not run Wolfram locally; export any newly found driver/formula bytes and exact hashes to Work mode.

The branch containing this file is `agent/recovery/native-repro-closeout-20260824-r2`. Its commit and draft-PR URL are external identities produced after this atomic file set; read them first with authenticated GitHub commands as directed in `CONTINUATION_PROMPT.md`.

Exactly one next action: ask the user whether R5b authority must retain the cancellation-sensitive relative-error-of-error comparison or may use a scientifically justified state/residual parity contract. Do not execute `BASS-8B.2A_TYPED_ELECTRON_STATE_BINDING` before all engineering RED is closed.
