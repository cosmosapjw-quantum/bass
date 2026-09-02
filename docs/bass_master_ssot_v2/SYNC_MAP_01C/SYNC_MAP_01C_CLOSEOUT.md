# SYNC-MAP-01C geometry-lineage composition closeout

## Result

`SYNC_MAP_01C_GEOMETRY_LINEAGE_COMPOSITION` is symbolically verified on the
canonical ALG-01R2/GEO-02R2 ancestry.

The stage composes the W2 abstract 1+3/Gauss-Codazzi registry and the W3
homogeneous spatial-curvature generator onto the exact connection lineage from
BASS PR #83. The curvature module consumes the canonical
`LeviCivitaConnection` through an explicit index-order adapter and does not
carry a second connection implementation.

## Exact identities

```text
canonical parent PR #83
c787e6c51608568fcb60d52f010235f8cb2c1076
3619744e9ba2b0633737b244cb18310ec89047c8

tested W2/W3 donor PR #82
5d3e8ecce2a40a1bc2b43af7daa985e042d9815f
0fee5b6335a2eb8968c11790ce787bf54fdc1def

formula composition source
fd022fdb43ac73ae8977494f7b61959f4ea600ac
ce560f825c692cfbc835ca01ff1292cee291f656

replay-publication branch head/tree
4165ca406596fa36bc784fb29932c43c43288e01
5617467b2ef9dc2029b82db214938fd14a2e2a21

GitHub pull-request synthetic merge/tree
dd0fec7b4f2c3c3bdbbb4c42c85edf819526c6c7
5617467b2ef9dc2029b82db214938fd14a2e2a21
```

The synthetic merge and branch head have the same tree. They remain separate
commit identities in the receipt.

## TDD and verification

```text
RED commit:  aae0f5b007c1685484677c006ae5c747d68abae8
RED run:     33582351373 — expected failure
GREEN run:   33582590749 — success
packet run:  33584207796 — success
artifact:    9829463769
artifact SHA-256:
b1f60fb518300e99c1321f3da0840a69d5478ecdbdb1d7602a6b77259d5b2fc1
```

The first source-packet attempt was retained as a packaging failure because it
omitted parent Authority/IR/Bianchi files required for independent replay. The
workflow was repaired without changing formula source and emitted a complete
34-file packet.

Fresh Wolfram/xAct replay of the exact packet:

```text
158 succeeded
0 failed
0 not evaluated
Wolfram 15.0.1
xTensor 1.3.0
xCoba 0.8.6
```

## Verified mathematics

The composed stage preserves:

```text
Gamma[[gamma,alpha,beta]]
 = <e_gamma, nabla_{e_alpha} e_beta>
```

with one canonical implementation. Normalized spatial-curvature witnesses are:

```text
I:  Ricci = 0,       R3 = 0,   R_1221 = 0
V:  Ricci = -2 I_3,  R3 = -6,  R_1221 = -1
IX: Ricci = I_3/2,   R3 = 3/2, R_1221 = 1/4
```

Direct ONF and xCoba coordinate-metric/tetrad-pullback routes agree for the
complete `3 x 3 x 3 x 3` Riemann arrays.

## Dropbox

Append-only recovery packet:

```text
/bianchi/bass/backups/BASS-MASTER-SSOT-V2/2026-09-02/
SYNC_MAP_01C_GEOMETRY_COMPOSITION
```

It copies the exact parent and donor backup trees and adds the composition
loader/test/runner overlay, exact source manifest, Wolfram replay receipt,
SciSpace literature lock, audits and restore map.

## Next nodes

The composition removes the ancestry blocker for two subsequent lanes:

```text
federation lane:
SYNC-MAP-02A_BASS_EQUATIONIR_AND_SEMANTIC_HASH_EXPORT

physics lane:
BG-02_GR_BACKGROUND_EINSTEIN_PROJECTION_DESIGN
```

BG-02 may begin only from this composed geometry lineage. It must generate the
normal-normal, normal-spatial, spatial-trace and spatial-PSTF projections of

```text
E_ab = G_ab + Lambda g_ab - (8 pi G / c^4) T_ab
```

without hand-entering type-specific Einstein equations.

## Claim boundary

```text
W2_ABSTRACT_1PLUS3_AND_GAUSS_CODAZZI_REGISTRY_COMPOSED
GEO03_SPATIAL_CURVATURE_I_V_IX_DIRECT_WITNESSES_VERIFIED
XCOBA_I_V_IX_FULL_RIEMANN_DUAL_ORACLE_VERIFIED
SINGLE_CANONICAL_CONNECTION_IMPLEMENTATION_VERIFIED
SYNC_MAP_01C_EXACT_SOURCE_PACKET_REPLAY_158_OF_158

NO_ALL_TYPE_CURVATURE_SPECIALIZATION
NO_BACKGROUND_EINSTEIN_MATTER_EVOLUTION
NO_CONSTRAINT_PROPAGATION
NO_NUMERICAL_PARITY
NO_CROSS_REPOSITORY_COMPATIBILITY
NO_SCIENCE_VALIDITY
NO_PASS_RF04
```
