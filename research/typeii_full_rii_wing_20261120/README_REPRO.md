# Reproducible BASS Type-II Hummer RII0 source calculation

Authority: Draft PR343, parent PR342 commit b23e75dcd2e8145cb161339bf08b6e1f522626f5, original BASS main 9c6506e4e2087129a8b674ff10438e5db1a55c9d. The new research-only files are under research/typeii_full_rii_wing_20261120/. This unit does not edit the BASS production module or old parent branches.

Computational contract: Python3, NumPy/SciPy, BLAS, original parent BASS source fixture/rates and Git. Invoke all commands from the repository root, with PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1:

    p=research/typeii_full_rii_wing_20261120
    python3 "$p/test_hummer.py"
    python3 "$p/compare_hummer.py"
    python3 "$p/source_wing_campaign.py"
    python3 "$p/source_refinement.py"
    python3 "$p/verify_recoil.py"
    python3 "$p/verify_final.py"

The further H40_14ANG_512 case is constructed with:

    PYTHONPATH=research/typeii_full_rii_wing_20261120 python3 - <<'PY'
    import outer_hummer
    result=outer_hummer.evolve(X=40.,steps=512,angular_order=14,save="HUMMER_H40_14ANG_512")
    print(result["tagged_ionized"])
    PY

To reproduce exact source *scientific payloads*, compare physical numerical fields/conditional probabilities with their expected tolerances. The source_wing_campaign.py results include wallclock runtime_s, so do not require the composite JSON to be byte identical after rerun. Deterministic numeric benchmark and recoil output artifacts may be SHA-compared. The command pattern has explicit raised scientific errors, including under Python -O, and prior RED tests were retained as expected failing test evidence.

The actual source kernel is exact Hummer RII0 under NO recoil and sharp-lower-level coherent radiation-damped Doppler assumptions. The leading frequency recoil shift is a separate first-order approximation, and finite pairwise symmetrization an engineered thermodynamic condition, neither a full microscopic quantum recoil kernel. Compare those three models rather than silently combining their results. A finite outer-band terminal probability is not global Ly-alpha escape and is not an observed CMB visibility or a new cosmological electron history.

Source parent code identity is tied to exact Git blobs and the Q1 snapshot. New outer_hummer.py is an isolated copy of the original parent source transport with explicit 2248-point/source vector grid protection and an OUTER_HUMMER_SOURCE_PATCH.diff. Production/main and parent sources are protected.

Stage preservation script PUBLISH_STAGE.sh creates one commit per Q1..Q4, pushes the isolated research branch, verifies remote Git HEAD, creates a Git-archive ZIP, checks ZIP integrity and SHA256, and records receipts under /home/cosmosapjw/research_backups/bass_typeii_full_rii_wing_20261120/. External fuseblk mount has repeated historical ENOSPC despite df free space: no unchanged blind external write retry or deletion. Final owner-host README/REPORT/STATUS/NEXT_THREAD_HANDOFF hold the executable science scope. Hosted GitHub CI is NOT_ESTABLISHED unless a successful workflow is actually returned.
