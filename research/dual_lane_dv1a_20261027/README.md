# BASS DV1-A: full-polarized Bianchi-I harmonic streaming

Status: COMPLETE_SCOPED_INSTANTANEOUS_FULL_POLARIZED_GENERATOR. DV1 overall remains PARTIAL. This is additive research on KM3 PR195 / 5dd5daef9f95e3b1e6dff536e701415f4d0e9894. No production/owner edits, previous campaign reruns, new IVPs or merge.

## Operator

Signature(-+++), photon propagation n, nonrotating normal frame, massless bolometric radiation, prescribed Bianchi I. H/sigma/nu are inverse proper time, nu=n_e* sigma_T c; multiply all rates by T_star for u=t/T_star. P=Q+iU=sum(E+iB) spin+2 Z in pinned DL2 real CS convention. P8 real S+A represents Hermitian S+iA.

Let S(n)=sigma_ab n^a n^b and V=-grad(S)/2. The spin operator is -4H-4S+(grad S).D/2, D_phi=partial_phi+i s cos(theta). Its Wigner3j/Gaunt matrix has coefficient [lp(lp+1)-l(l+1)-10]/4. The analytic RHS calls neither angular quadrature nor a direct RHS. An independently differentiated Cartesian carrier calls pinned P8.tensor_rate/direction_rate for comparison.

The scalar limit matches H/J with cJ_lm=I_lm/sqrt((2l+1)!!/(4pi*l!)). Whole J RHS and P8 file bytes match pinned Git blobs; H kernels have executable-AST matching to a preserved live-read excerpt. H/PSTF helper context is explicitly archival, not a whole-current-package execution.

I/V have delta ell=0,+/-2. Same E/E,B/B have even delta ell; E/B exchange has delta ell=+/-1. For sigma=diag(-s0,-s0,2s0) and real E22=1, dot B3,-2=4sqrt(5/7)s0. Axisymmetric E20 gives zero B in the same shear. This is a specified seed/convention result, not a universal B-generation or parity-violation claim. Wolfram direct angular integration and ThreeJ agree exactly.

## Executed evidence

10 pytest items pass. Three GL grids and three fields give828 all-I/E/B/V basis RHS rows (input ell<=4, full instantaneous output through6),9 positive mixed streaming+collision rows,9 scalar H/J comparisons and3 shear-amplitude checks. Fixed absolute gate2e-11. Max basis/mixed/J/H errors3.4861e-14/1.5949e-13/3.5527e-15/9.9476e-14. Energy-balance defect8.7472e-14. Dropping the screen connection, E/B coupling or generated ell5/6 is detected. These roundoff-level comparisons are not convergence-order estimates.

No time integration or full direct/harmonic/Volterra trajectory comparison was run. An instantaneous input+2 angular output is not a finite-time closure. General positivity, infinite-tail accuracy, Rust integration, tilted clocks, curved Bianchi, recoil/spectra, Einstein feedback and observer-sky inference remain open. Native subagent and independent-model review NOT_RUN. CAS is a symbolic cross-check, not model review.

## Reproduce

From this directory:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest tests/test_streaming.py -q
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python verify_dv1a.py

The verifier writes full raw rows under evidence/. SOURCE_MAP.json pins identities. The complete archive named in DELIVERY.json contains the full Korean report, detailed DAG, all results, CAS, logs, figures, handoff and SHA256SUMS. Git publication carries runnable code/tests/vendor, concise state/evidence and source map, not every archived raw file.

## Next

DV1-B: finite-time same-physics full-polarized harmonic integration with L-cutoff scans, compared to direct and independent KM3 Volterra. Separate continuum harmonic truncation from raw moving-quadrature, ODE and memory-interpolation errors. Retain initial source-null tails. DAG_STATE keeps15 nodes, completed/source-mapped count5/15 plus DV1-A subgate, production_ready=false, global physical completion=null.
