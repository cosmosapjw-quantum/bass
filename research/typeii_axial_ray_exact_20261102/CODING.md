# Original BASS Type-II axial ray exact physical research

## C1. 실행 대상과 품질 기준

Implement a reproducible source-locked exact axial oracle and compare 401 published source-conditioned records for both e_y directions. Acceptance: all original 9 Git blobs and parent CSV SHA locked; no mutation of original source; normal and optimized Python checks; exact direction, redshift, electron Doppler, optical-depth parity and negative controls. BASS production gates remain HOLD.
## C2. 수식-코드-데이터 매핑

`verify_axial_analytic.py` reads original `compiler/validation/typeii_fixture_canonical.json`, its `samples[*].state` and `samples[*].rhs`, plus immutable parent `PHOTON_RAYS_401X26.csv`. It chooses ±ey by measured initial ray vectors, not by assuming list index, then compares normal and electron frame energies plus optical depth at every 401 time sample. `test_axial_negative.py` is a separate narrow counterexample suite and `verify_axial_accuracy.py` checks numerical quadrature.
