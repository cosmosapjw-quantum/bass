# BASS CE1AR source-owned fixed observed redshift Sachs atlas

## One immutable parent model

CE1AQ PR302 HEAD `bbebf7f0cdc3e23eec422f67118e8d402afb106c`, CE1AP PR301 HEAD `baef3a4b5a556703f2e2feb93b57da6b364d29fd`. Original six-cell SHA `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. Metric `(-,+,+,+)`, normalized original `8piG=1`, time `u=t/Tstar`, geometric D_A in `c*Tstar`. Observer `u_o=.08`; six observed redshift shells `.005,.01,.015,.02,.025,.03`.

Includes original, SHA-frozen CE1AP 16,842-row ray histories, not a source-matched IGM H/He owner. No new Einstein IVP. For code-only GitHub parent branch, its CI regenerates nine owner IVPs first; GitHub does not contain the raw S2 ancestor 4.4 MB CSV.

## Standalone reproducer (from extracted CE1AR/ root)

Python 3.13 recommended; NumPy 2.3.5, SciPy 1.17.0, matplotlib 3.10.8, pytest 9.0.2. Local scientific execution also checked in current container with available NumPy/SciPy.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python source/ce1ar_fixed_z.py --input ancestor/CE1AP_DIRECTIONAL_GEODESIC.csv --metadata ancestor/ANCESTOR_LOCK.json --strict-sha --out data
python -m pytest -q source/test_ce1ar_fixed_z.py
python source/hostile_axis_fixed_z.py --input ancestor/CE1AP_DIRECTIONAL_GEODESIC.csv --beams data/CE1AR_FIXED_Z_BEAMS.csv --out data/CE1AR_AXIS_REFEREE.json
python source/plot_ce1ar.py
python source/compare_ce1ar_paths.py  # compares stored alternate code output, not a distinct owner
```

Github separate code route `ce1ar_remote.py` and its tests require the original PR302 `ce1aq_remote.py` and dynamically rebuilt CE1AP 9 IVPs; for standalone S2 use the primary `ce1ar_fixed_z.py`. The external source-bearing original generator code is owned by exact PR301/PR302, not redefined here.

## Outputs / scope

5,562 newly calculated conditional fixed-z ray-geometry records + 1,854 source-response records. Six original PNG/SVG physics figures. Axis-only independent numerical quadrature audit 162 checks; 20 Python tests on full two-route source workspace and 13 portable primary tests. SHA manifest covers all payload members; zip CRC covers transport. New BASS upper completed 0; upper remains 9/15 scoped/source-mapped, CE-1 PARTIAL, OB-1 is only a conditional observable partial. Independent author/continuum error/actual CMB likelihood NOT_RUN.
