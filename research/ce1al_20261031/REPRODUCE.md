# Clean checkout CE1AL scientific reproduction

python -m pip install numpy==2.3.5 scipy==1.17.0 pytest==9.0.2 matplotlib==3.10.8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python research/ce1al_20261031/source/ce1al_curvature_remote.py
python research/ce1ak_20261031/source/ce1ak_reproduce.py
python research/ce1aj_20261031/source/ce1aj_physics.py
python research/ce1ai_20261031/source/ce1ai_source_response.py
python research/ce1ah_20261031/source/ce1ah_tangent.py
python research/ce1af_20261030/source/shear_work_physics.py
python -m pytest -q research/ce1al_20261031/source/test_ce1al_remote.py research/ce1ak_20261031/source/test_ce1ak_remote.py research/ce1aj_20261031/source/test_ce1aj.py research/ce1ai_20261031/source/test_ce1ai.py research/ce1ai_20261031/source/test_dark_jet.py research/ce1ah_20261031/source/test_ce1ah.py research/ce1af_20261030/source/test_ce1af.py
python research/ce1al_20261031/source/plot_ce1al_remote.py
python research/ce1al_20261031/source/package_ce1al_remote.py

Remote source implementation is independent equivalent of local original S2, not byte-identical. GitHub Actions result/ZIP must be read separately; no success inferred from this instruction. Source original immutable.
