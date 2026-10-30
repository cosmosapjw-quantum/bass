# BASS CE1-Z · 원본 Rust 하늘의 두 시점 ℓ=4 Gram 물리 스펙트럼

2026-10-30, one bounded science unit. Original precursor PR268 \`c4d303ebd8294df8a4b564b140b88fc8e57b0e67\`; immediate frozen input PR271 \`9cf562496cb753fe831e684ccf0b4dd54f5c5d94\`. Isolated draft child, no parent/main changes, no merge. Original six positive binary angular cells SHA256 \`022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035\`, massless collisionless expanding diagonal Bianchi-I, Λ=0, (-,+,+,+), u=t/Tstar in [0,.08], shear (.2,-.13,-.07). Original strict h<1e-5 maintained, verified for GL6 4-panel in PR268; no tighter target imposed.

## Physical deduction and numerical evidence

Original Condon–Shortley energy-sky \`α_lm=4π a_lm/E\`, original reflection-even scalar sky, leads exactly to the real vector \`X=(α40,√2 α42,√2 α44)/3\`. The two-time physical kernel is \`K4delta(u,v)=X(u)·X(v)\`, hence \`K=XX^T⪰0\` and \`rank(K)≤3\` at all 41 epochs, independently of time integration. 41×41 nonzero eigenvalues are the three eigenvalues of \`X^T X\`. This is a **single deterministic normal-observer sky Gram functional**, neither CMB stochastic covariance nor observed likelihood.

The six original native BASS Rust harmonic sky CSVs from PR271, 41 epochs each, were read directly from their current GitHub blobs. A separate 3×3 Jacobi eigenvalue calculation (not the stored PR271 K4 generator) gave:

| frozen GL / panels | λ1 | λ2 | λ3 | r4(0,.08) |
|---|---:|---:|---:|---:|
| GL6 / 4 | .44379405457008364 | 3.7866111326609586e-5 | 5.713349156989296e-11 | .9995105058017874 |
| GL6 / 8 | .4437940542729394 | 3.786611447355703e-5 | 5.713328134217499e-11 | .9995105057724112 |
| GL6 / 16 | .4437940542541107 | 3.786611466863278e-5 | 5.713325644944484e-11 | .9995105057706098 |
| GL8 / 4 | .4437940551008169 | 3.7866109920009435e-5 | 5.713327331957706e-11 | .999510505820267 |
| GL8 / 8 | .4437940548036681 | 3.786611306692082e-5 | 5.7133126894435484e-11 | .9995105057908906 |
| GL8 / 16 | .443794054784839 | 3.786611326198781e-5 | 5.713308301113043e-11 | .9995105057890898 |

For GL8 N16, λ2/tr(K)=8.531633592394783e-5, λ3/tr(K)=1.28726845261977e-10, and effective participation R=(tr K)^2/tr(K²)=1.0001706474871217. The angular energy pattern is almost but not exactly stationary: 1-r4(0,.08)≈4.89494211e-4, whereas K4(0,.08)=.01079267954690703. The first→final squared 3-vector pattern distance is D4²=1.6791647245339297e-5. These are **numerically checked binary64 quantities** from original Rust-generated physical data, not exact-real continuum interval enclosures.

## Honest error budget: what does (not) resolve the second mode?

For the original PR270 exact-real continuum-vs-stored-path two-time entrywise bounds, Weyl gives |δλ_i|≤41 ε_K for all symmetric 41×41 matrices. For GL8 N16 ε_K≈7.854496482e-7, thus 41ε_K≈3.22034e-5; numerical λ2≈3.78661e-5 leaves a **conditional** positive difference ≈5.66e-6. GL6 N16 ε_K≈9.2063254655e-7 ⇒ 41ε_K≈3.77459e-5; much smaller positive conditional margin. N4/N8 bounds are larger than λ2; they cannot distinguish it with this crude entrywise spectral criterion.

**Crucial qualification:** the PR270 exact-real source/geometry radius is *not a complete outward MPFR interval around the Rust binary64 values*. A formal second continuum eigenmode certificate is NOT established here. An exact-real re-evaluation on the certified path with outward error or a new direct 3×3 eigenvalue bound would be needed. Do not relabel a DOP853 empirical comparison as a certificate, do not inflate the original geometry h target, and do not start higher precision just to chase this conditional margin.

## Executed/verifiable new code

\`research/ce1z_20261030/gram_spectrum.py\`: independently reconstruct both full 9-complex-harmonic and 3-real-mode kernels from **the original** BASS Rust sky CSV; enforce literal frozen source SHA, proper 41 times, positive E, parity/Condon–Shortley reality, all 10,086 prior physical pairs, compare prior K4 records, eigen spectrum, PSD, ≤3 rank and positive pattern distance. Numerical output is machine-readable JSON, contains individual Rust input SHA and all six derived spectra. 8 regression/negative tests under \`tests/test_gram_spectrum.py\` target mutations, odd harmonics, negative energy and clock changes. GitHub Actions workflow regenerates actual data; CI status must be read from the new exact HEAD rather than this document.

The original BASS Rust source Git blob \`a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84\` is reused, not rewritten. CE1-Z does not recompile or rerun the source evolution: the *source* Rust was genuinely executed and stored in the earlier PR270/271; this bounded unit processes that immutable physical data directly. A separate production integration of the geometry/transport/collision system remains unverified.

Upper DAG **9/15, 21 edges, CE1=PARTIAL; new completed upper nodes=0**. Actual distinct-author native R6/C9 NOT_RUN and subagent NOT_RUN (current host has no native delegation). \`production_ready=false\`, \`merge_ready=false\`, \`auto_next=false\`. STOP_AFTER_ONE_BOUNDED_UNIT=true.
