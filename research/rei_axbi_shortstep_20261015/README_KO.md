# REI AX03 stable short-step background: C8 actual coding/numerical evidence

Selected physmath coding C8, continuing source-frozen BASS PR156 / REI PR121 background supplier. This is not FA03 C10. Actual authorized Ubuntu Python+stdlib Rust execution without local Codex or exposed native subagents. Original REI production owner checkout and solver are never mutated or restarted.

REI source lock: original AX03 Bianchi I physical density-fixed five q_ref=0,+/-0.005,+/-0.01, plus separate SAME_H(q=.01) counterfactual; H=sqrt(H_F^2+s^2), s∝a^-3, elapsed SI proper time zbar20->4. The SHA256 source lock is inherited from parent REI background supplier: 46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0.

New callable shortstep.py functions:
- gauss_increment(bg,a0,a1,order=4): source-driven positive proper ∫ dx/H and Δb=∫ s dx/H using log1p((a1-a0)/a0). Gauss weights are cached, source call at a0 exp(theta Δx) avoids subtracting huge cumulative timestamps.
- gauss_batch(bg,array_a0,array_a1): same physical quadrature grouped by panel count and vectorized over many intervals, single worker default.
- HermiteClock(bg,n=501).increment(a0,a1): monotone physical-derivative Hermite cubic with a factored cancellation-resistant interval difference, source domain and derivative positivity strictly validated.
- photon_short_logmap(bg,a0,a1,mu_face): exact real Bianchi-I Killing energy and direction, using expm1/log1p so tiny Δx and Δb are resolvable.
- Independent stdlib-only native Rust physical Gauss4 reference in rust_shortstep.rs, compiled with rustc outside REI and executed on 90 exact float64-source interval inputs; negative frozen q rejection exit3.

Scientifically measured:
- 90 intervals / six q and family cases with mpmath80 independent exact binary64 endpoint reference: max relative dt GL4 2.2903079824291173e-16, db GL4 2.5734772941032376e-16; Hermite501 dt5.794301303454278e-10, db5.774119270322933e-10; naive timestamp subtraction worst 1.24046 (124%).
- Actual independent Rust 90 intervals max dt rel2.29e-16, db5.10e-16.
- q=.01, a0=.1, a1=nextafter(.1,+inf): local Δt=3.57067006236636s while naive t(a1)-t(a0)=4.0s.
- Source-matched 90 interval 5 warmed medians: Hermite0.466ms, scalar cached GL4 5.441ms, vectorized GL4 0.636ms, 2thread1.320ms, 4thread1.284ms; no parallel speedup, and no full REI native ODE speedup claimed.
- Previous original REI background_table_001 stable Hermite increment recorded better sample-level accuracy than our 501-node Hermite, but the actual production driver still had its 356 short-step subtraction HOLD events and was NOT modified. This standalone component does not clear the production gate.

Test under BASS repo root:
python3 -m unittest discover -s research/rei_axbi_shortstep_20261015 -p test_shortstep.py -v
python3 research/rei_axbi_shortstep_20261015/mp_shortstep.py --output /tmp/shortstep_mp80_replay.json
python3 research/rei_axbi_shortstep_20261015/rust_shortstep_parity.py --output /tmp/shortstep_rust_replay.json
python3 research/rei_axbi_shortstep_20261015/benchmark_shortstep.py --output /tmp/shortstep_bench_replay.json

The actual saved run/plots/test results are under evidence/, and source/parameter/theory gates in REPORT_KO.md. Complete native REI production integration, ionization histories and rigorous global interval certification are NOT_ISSUED here. C9 next only if separately selected.
