# Receipt — BASS-8B.2B.2 generic-vector bundle differential

## Package

- Exact ZIP: `BASS8B2B2_GENERIC_VECTOR_BUNDLE_DIFFERENTIAL_CANDIDATE_20260824.zip`
- SHA-256: `c9ac7a9a79a1cbb265974b313e5238077876391c68f98481ccf606d928dcdaed`
- Deterministic double build: byte-identical
- ZIP CRC: PASS
- Clean-extraction verification: PASS

## Verification

- Internal manifest: **41/41**
- Focused BASS-8B.2B.2 tests: **15/15**
- Self-contained total tests: **38/38**
- SymPy exact witness: PASS
- Stateless Wolfram exact witness: PASS
- Randomized generic-vector audit: **500/500**
- Finite-difference audit cases: **80**
- SO(3) probes: **120**
- Hostile mutations: **5 classes, 500/500 detected per class**
- Plot evidence: **4/4**
- Final marker: `BASS8B2B2_PACKAGE_VERIFY_PASS__PROJECTOR_LEFT_AUDIT_NEXT`

## Mathematical scope

For fixed electron-rest quadrature nodes, the package differentiates with
respect to a generic three-vector electron velocity and tangent direction:

- inverse-aberrated moving normal nodes;
- Doppler and direction factors;
- moving quadrature weights;
- screen projector and canonical ambient screen map;
- moving equilibrium carrier;
- paired full-generator left weights;
- normalized rank-one projector.

The projector tangent identity, normalization tangent, global scalar-opacity
independence, SO(3) covariance, zero-tilt regularity, and Type-II aligned
restriction are tested.

## Architecture and claim boundary

- Active reference/frontend: pure Python (NumPy/SciPy/SymPy/pytest)
- Performance backend target: Rust 1.94.1, locked/offline-capable
- JAX/JAXlib/Equinox/Diffrax: excluded from the active target
- No Rust lowering, Kato/runtime wiring, VI0 classifier, PR, merge, tag, or
  authority-row promotion is contained here.

Rows 7 and 8 remain blocked. BASS-3, solver/runtime/production, and Join J1
remain blocked. The next bounded node is BASS-8B.2B.3.

## GitHub text-seal note

This commit preserves the control-plane decision, evidence summary, package
checksum, and exact claim boundary. The full source/test/audit package and PNG
plots remain checksum-addressed external artifacts; no claim is made that those
binaries are embedded in this commit.
