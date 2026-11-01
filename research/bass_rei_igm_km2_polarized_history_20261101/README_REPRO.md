# Original-source BASS KM2 electron-history polarized response

This is an original BASS KM2N/P8 Einstein-Bianchi-I exactly-once Thomson-scattered Lyα **source-conditional tangent**, not the accepted REI H/He reionization model or a full CMB calculation. It preserves source owner commit 4137f942d2a95999f4e6627b71042e98f7afc1b7 and all original 9 direct inputs. In/Out ray paths differ: differentiate both causal pre/post attenuations and collision gain, not same-ray visibility. Electron panel perturbations use a specified right-edge left-limit convention.

Requirements: Python with NumPy and Matplotlib (exact versions recorded in environment receipt); no network access during replay. Included original source artifact is pinned by SHA and 50-member nested manifest.

`bash REPRODUCE.sh`

Will extract the source with strict SHA/CRC guards, independently execute 800 original ray histories and 96,000 new ray–panel response rows, test 12 normal+optimized controls, regenerate three PNG/SVG physics plots and assert generated files match the archived science hashes. Do not run in user original BASS working tree; operate in a clean extracted package. 

REI central DAG=28/88 reported, BASS upper=9/15 scoped, both Δ0. Research drift watchdog: after this BASS-only consumer development, stop adjacent auxiliary loops unless actual source-matched REI electron history can be incorporated; do not widen gate or promote.
