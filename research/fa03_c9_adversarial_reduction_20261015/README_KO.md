# FA03 C9: actual hostile math/code audit and corrected tensor contraction

Selected C9 scientific coding audit, implementation and runtime on the authorized Ubuntu workstation. Parent source Git commit 6812bac3148afa292189f0bdec3e5994a5b892b0. No separate local Codex, no native subagent available; no owner REI edits or solver launches. The historical C8 source stays untouched.

BLOCKING SCOPED CORRECTION: C8 aggregation_roundoff.py applies gamma_N to an opaque NumPy tensor weighted einsum path. The assumed operation graph fails to include two multiplications for w_ray*w_energy*Stokes, so it does not establish an IEEE error guarantee for the actual einsum. An exact-dyadic positive 3-product witness proves that a generic one-term gamma1 model underbounds a real binary64 result. The specific C8 36-ray result need not violate gamma144; no such claim is made.

New deterministic_reducer.py uses exactly two binary64 multiplications per term and a balanced binary-tree sum of depth ceil(log2 N). Its conditional aggregation roundoff upper against exact sum of already-supplied binary64 inputs is 4*M*W*gamma_(2+ceil_log2N) for pre-reconstruction coherency trace norm. M and W are exact Fraction values derived from supplied binary64 inputs. No upstream physical source, quadrature weight generation, RK4 or final float matrix reconstruction error is included.

Actual 480-ray GL4, 128 step FA03: pairwise conditional trace bound about3.02419e-15; against exact Fraction oracle the individual Stokes component errors are numpy_einsum 4.7791e-17, pairwise 3.6820e-17, math.fsum1.8691e-17. Matched full-source five warmed medians 0.15362/0.17015/0.15656s. Pairwise is NOT a faster default. Keep original C7 one-worker fast real Stokes for normal use and C9 pairwise for auditable aggregation only. Measured 2/3-thread output bitwise identical but slower. Existing C8 GL4/8 optimization remains unchanged.

Independent 70digit mpmath true analytic time constant-H 2x2 polarized spectral oracle: three k,epsilon cases and six orders each, all inside the retained C8 exact energy theorem (41931/9600)*25**(-2n). Wolfram15.0.1 checked the complex G+G†=2 Re(alpha)H identity and original observer L correction. Analytic continuation uses U(e)BU(e)^T rather than U(e)BU(e)†. Native Wolfram15.0.0/xTensor1.3.0 seven zero geometry and screen signs. No independent third-party scientific review claimed.

Under the BASS repo run:
 python3 -m unittest discover -s research/fa03_c9_adversarial_reduction_20261015 -p test_c9.py -v
 python3 research/fa03_c9_adversarial_reduction_20261015/deterministic_reducer.py
 python3 research/fa03_c9_adversarial_reduction_20261015/benchmark_c9.py --out /tmp/C9_benchmark.json --reps 5
 python3 research/fa03_c9_adversarial_reduction_20261015/spectral_independent_oracle.py --output /tmp/C9_independent.json

See REPORT_KO.md and evidence/ for proof and machine results. Next C10 READY_NOT_EXECUTED; original R8 finite36 bound <4.75e-7 unaffected. Continuum cap, real variable-ODE error, full source float error and REI physics remain held.