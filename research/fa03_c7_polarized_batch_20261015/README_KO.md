# FA03 C7: validated real-Stokes vector transport

This is the selected coding C7 scientific validation based on immutable C6 commit 76cfa950a6504a219365b31e9358dec9e4c05f66, executed directly in ChatGPT on the user's authorized Ubuntu workstation, with no local Codex.

The program preserves original FA02/FA03 source laws, Kasner Bianchi I, metric (-,+,+,+), fixed observer (chi=0.008, psi=0.01), angular cap (delta=0.02 rad), zero incoming coherency, non-grey epsilon in [-0.1,0.1] and energy band [0.98,1.02].

The exact Jones matrix evolution F' = B-GF-FG^T is rewritten in four real Stokes components including emission, symmetric attenuation and antisymmetric screen rotation. This is not a weak-polarization closure. New codes: batch_transport.py (fused six-state and complex spectral reference), stokes_vector.py (fast batched real Stokes), benchmark_c7.py and benchmark_stokes.py (matched timing), plot_c7.py (measured performance), test_c7.py and test_stokes.py (19+15 tests). The derivations and calculations are in REPORT_KO.md.

Actual benchmark: 64 RK4 steps, GL8 energy, eps=(-.1,0,.1), three warmed medians, same original formula: Jones versus real Stokes 0.10191/0.02118 s at 36 rays (4.81x); 0.29258/0.04971 s at 144 (5.89x); 0.77723/0.09696 s at 480 (8.02x). Real state allocation exactly half nominal bytes of the complex state; total process RSS not claimed half. Actual 2/4 worker ray chunking slower, so default workers=1.

Physics checks: Hermiticity, positivity, Stokes cone, screen transformation invariance, rotation trace cancellation, non-grey epsilon versus frozen FA03, actual source hash, six-state epsilon-zero tangent derivatives and deterministic chunks. C7 34/34 new tests, inherited C6 18/18 and C5 15/15 pass (67 total). Native Wolfram Engine 15.0.0/xTensor 1.3.0 seven exact-zero covariant screen and photon sign checks. Wolfram Cloud 15.0.1 scalar balance and positive source checks. External independent review and native subagents NOT_RUN.

Scope: finite detector and toy energy model only. No certified continuum angular error (M4 and radial GL3 unknown), no rigorous full numerical RK4 error, no native REI speedup, no empirical atomic opacity uncertainty or scientific reionization admission. Historical R8 finite 36-ray trace bound <4.75e-7 unchanged. C8 READY_NOT_EXECUTED.

Run under the BASS repository root:
python3 -m unittest discover -s research/fa03_c7_polarized_batch_20261015 -p test_c7.py -v
python3 -m unittest discover -s research/fa03_c7_polarized_batch_20261015 -p test_stokes.py -v
python3 research/fa03_c7_polarized_batch_20261015/benchmark_stokes.py --repetitions 3 --out /tmp/fa03_c7_new_benchmark.json
python3 research/fa03_c7_polarized_batch_20261015/plot_c7.py

Use NEXT_C8.json as bounded next scope. Do not automatically start another solver or override active rei_bianchi code.
