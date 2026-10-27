# BASS DL-2: source-matched polarized source/multipole dictionary

Status: COMPLETE_SCOPED_POLARIZED_SOURCE_DICTIONARY. Draft PR193. This additive research directory does not change production code, owner branch, tolerances or prior campaign budgets.

DL1 was backed up and its preservation receipt published in commit a6877102dae16a6298825e8d7fbac4333efe092a BEFORE DL2 computation. See DL1_PRESERVATION.json. The complete DL2 archive, 26 payload files and raw evidence, is identified by DL2_DELIVERY.json; this Git publication selects executable code, tests, validator, concise report and DAG state.

## Exact source dictionary

Use photon propagation n and a theta/phi screen, bolometric intensity units, signature (-,+,+,+), and chi=int n_e* sigma_T c dt_e. P8's real stored carrier is S+A; its physical Hermitian interpretation is S+iA. Q+iU=sum(E_lm+i B_lm) _2Z_lm, with BASS real Condon-Shortley transform. This convention must not be silently combined with an external leading-minus convention or the observer-sky antipodal map.

For M=int J dOmega and canonical Frobenius STF U2m:

- tr M=sqrt(4pi) I00.
- M_STF=-sqrt(2pi/15) sum_m (I2m-sqrt(6)E2m) U2m.
- M_[ab]=-epsilon_abk d_k/2, d=sqrt(4pi/3)(V11,V1-1,V10).

The 14 gain-relevant real coefficients map to nine real source components with a five-dimensional nullspace. I2m=sqrt(6)E2m is source-null, not zero radiation. Thus this source dictionary is not an invertible state representation.

For each quadrupole m, the rest-electron gain block is [[1/10,-sqrt(6)/10],[-sqrt(6)/10,3/5]]. Its generator eigenvalues are -3/10 and -1. I00 is conserved, V1 decays as exp(-chi/2), B and remaining source-null modes as exp(-chi). This is the static collision problem, not a nine-state closure of Bianchi streaming.

## Evidence and scientific consequences

11 pytest items passed. Three GL grids (8x16,12x24,20x40) and all I/E/B/V basis modes through ell=4 give 276 rows; four optical depths give 12 positive mixed-field rows. Fixed absolute gate 2e-11. Maximum roundtrip/source/basis-collision/mixed-collision errors: 1.0294e-14/1.9318e-14/1.0547e-15/2.4425e-15. External Wolfram exact source integrals and 2x2 eigenvalues agree. This is not an independent-model review or a Rust/full-solver validation.

A source-null initial I40 carrier under prescribed Bianchi-I shear yields nonzero Mdot, norm 0.09923674348227812 in the unit-intensity/reference-time convention. The independent -sigma_cd J4_abcd/2 contraction differs by at most 1.85e-15. Adding 0.1 Z40 to a positive isotropic intensity gives a physical paired-state version. Keep initial gain-null/high-tail propagation in the future memory equation.

Legacy argmin-screen Q/U requires the explicit spin-two phase map: converted error <=9.07e-16, unconverted error about0.1644. No production E/B or mask/observer-sky claim is made.

Historical correction: the finite-time scalar/full-polarized intensity difference discussed in DL1 already exists in P8 _delta_coeff/unpolarized_delta_closed. DL1 revalidated it; it is not a newly discovered result. Original archives remain unchanged.

The first implementation test incorrectly demanded strict positivity of the 3D coherency. Four failures were retained. Transverse radiation has a longitudinal null vector; the corrected test checks positive 2D screen eigenvalues and nullness separately, without changing the physics or tolerance. Failure/repair logs are in the immutable ZIP.

## Reproduce

From this directory:

    python -m pytest tests/test_dictionary.py -q
    python verify_dl2.py

Python3.13.5, NumPy2.3.5, SciPy1.17.0 were used. verify_dl2.py verifies the P8 source Git blob and writes all raw rows under evidence/. The original P8 source is byte-identical to blob7448ea6701f236fd41d22f3c5cadfd80f482d82f at source commit cc602e209e7deeb511ab2a1f3b2268d55206c43c.

## Remaining scope and next unit

Continuum identities are not automatically discrete identities on deformed/masked/undersampled quadrature; raw M_h=sum w_h J_h remains the discrete authority. Moving-electron normal-clock wiring, finite-frequency/recoil physics, arbitrary infinite-tail bounds, production Rust ABI, Einstein backreaction and independent model review remain open.

DAG_STATE.json preserves all15 research node statuses/dependencies; the full detailed DAG is in the archive. Record count3/15 includes DL0 source mapping and scoped DL1/DL2, not physical completion. Next: KM1 native memory extension on prescribed finite-shear Bianchi I with non-tilted electrons, keeping the full initial gain-null contribution. KM3/DV1 are separate future completion units. No merge or production promotion.
