# CE1AK clean-checkout reproducibility

Pinned parent PR #290 SHA 50dc76e3ba460d0565b65a60b816af2ded0da6a3, original six-cell binary64 SHA256 022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035. From this Draft branch's checkout, Python 3.13:

python -m pip install numpy==2.3.5 scipy==1.17.0 pytest==9.0.2 matplotlib==3.10.8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python research/ce1ak_20261031/source/ce1ak_reproduce.py
python -m pytest -q research/ce1ak_20261031/source/test_ce1ak_remote.py

For inherited original suites, first reconstruct derived parent data (do NOT change input):
python research/ce1aj_20261031/source/ce1aj_physics.py
python research/ce1ai_20261031/source/ce1ai_source_response.py
python research/ce1ah_20261031/source/ce1ah_tangent.py
python research/ce1af_20261030/source/shear_work_physics.py
python -m pytest -q research/ce1aj_20261031/source/test_ce1aj.py research/ce1ai_20261031/source/test_ce1ai.py research/ce1ai_20261031/source/test_dark_jet.py research/ce1ah_20261031/source/test_ce1ah.py research/ce1af_20261030/source/test_ce1af.py

The full source-included original local CE1AK package (six plots, 26 local tests and exact Fraction certificate) is provided separately in the handoff; this Git implementation is a second compact original-source-bound reproduction of the same governing equations and physical observables. Compare physics numerically; do NOT claim byte-identical source scripts or CSV output where the algorithms are independently authored. The inherited source is immutable and not reset or merged. Original upper DAG remains 9/15.