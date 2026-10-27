# REC native atomic source intake, 2026-10-27

## Result

A concrete read-only route to the selected native cell is available: use the saved incoming/average/outgoing virtual-bin traces to infer optical depth, then recover x1s through the original native optical-depth formula. The exact input packet is `NATIVE_VIRTUAL_TRIPLE_TRACE_5126_5127.json` (SHA256 `7d6e85bf2e759500d3e7d7249de5892bcc34ce7af77f08de10ae1607eacf19ef`). This intake extracted and bound the input; it did not execute the inverse or admit an atomic transaction.

The primary bin is 273, with independent checks at 272, 267, 268, 269, and 309. They are all outside the original diffusion range [100,180), so their source Gamma depends on the radiation temperature and original two-photon table, without an unknown matter-temperature input. All six reconstructed right-knot incoming values and saved average/outgoing values match the original diagnostic snapshot bit for bit. Source table rows, literal constants, clock arithmetic, source indices, interpolation fractions, and binary64 values are included in the packet.

| Native knot | z | primary-bin incoming | saved average | saved outgoing |
|---|---:|---:|---:|---:|
| 5126 | 1100.092131270856 | 3.0843112536976223e-18 | 3.48735954331956e-18 | 3.766903546000831e-18 |
| 5127 | 1099.9986525171403 | 3.0794164835544322e-18 | 3.481839162529577e-18 | 3.760947705334913e-18 |

Primary-bin right-snapshot Dtau is 1.1076274318532195 and Gamma is 6.084185653162193 s^-1. These are validation values. The right x1s=0.85507000330964777 is also validation only. The left x1s has not been inferred in this intake.

The exact saved Ly-alpha outgoing pair was separately extracted in `NATIVE_OUTGOING_LYA_5126_5127.json`, SHA256 `4125f74e4fb30e27a7244ac2646c5dac1f7aac6ebf516229206940758ffa81a5`:

- 5126: 7.69131493484943e-15, hex `0x1.151bdbedc3779p-47`.
- 5127: 7.684081955810867e-15, hex `0x1.14d9258a3512cp-47`.

All three stored Lyman rows are also available in `NATIVE_LYMAN_STORED_5126_5127.json`, SHA256 `5a01a3dfab10f07450c828e0ca141a8dc69f40e713a57b71aae378c41e1ed8f3`. Their native identities recover xr_s from Ly-beta and Ly-gamma independently after x1s is obtained. No level population was inferred here.

## Exact source and operations

The source remains `cosmosapjw-quantum/rec_bianchi@d6dbe39a4923439547c01695d9020ba39367ea90`; its branch was rechecked at 2026-10-27 10:33 UTC. The full tree had 7,581 entries and was untruncated. No active root AGENTS file appears in this exact REC tree; archived AGENTS from other packages are not ancestors of this read-only source task.

The reused history is `data/pr05b2_source_history_v060.npz`, 35,239,470 bytes, Git blob `de43b1a2642fa0aa049abbfd1b0a7d775d684b1b`, SHA256 `d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1`. Its arrays contain 7,489 native knots, with 311 outgoing virtual, 311 average virtual, and three outgoing Lyman rows. The original source archive is SHA256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`, 726,954 bytes.

Original `HyRec/hydrogen.c` is 37,471 bytes and SHA256 `421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b`. The thermo vendor copy has a different trailing-byte identity; the original archive member is authoritative. The exact member hashes and archive inventory are in `ORIGINAL_SOURCE_MEMBERS.json` and `ORIGINAL_ZIP_MEMBER_INVENTORY.json`.

The extractor command actually run was:

```sh
python next_atomic_intake/extract_virtual_trace_packet.py
```

It reads the stored NPZ, CSV and original ZIP; computes the native clock and linear-interpolation witnesses; and serializes selected values. It does not load a native solver, perform inversion, integrate a physical model, run tests, consume a B3i packet, or plot.

## Survey coverage and precise remaining gap

The survey inventoried all 157 visible REC branch tips and all 139 pull requests (105 open, 34 closed). It inspected the relevant latest REC tree and the ancestry of 28 native/history/source branch tips: 20 are ancestors of the latest source, eight diverge. Divergent changed-file inventories were examined. Two compare responses reached the GitHub 300-file limit; these were resolved with full untruncated donor01/donor02 trees (2,270 and 2,277 entries). Four additional historical harness TAR files were actually downloaded and their member inventories inspected (60,60,81,81 members). No alternate accepted-grid native atomic history was identified in that examined scope. This is a scoped source finding, not a claim about inaccessible conversations or every unseen backup.

Six additional legacy NPZ files were downloaded, byte-identified and read without executing their scripts. They contain a native proxy map, three-snapshot primitive/ownership operators, or COM examples. They do not contain the two selected absolute native states. Their exact arrays and identities are in `NPZ_ARRAY_INVENTORY.json`.

Stored original stdout does exist: `ORIGINAL_BASELINE_HISTORY.txt`, also duplicated as PR04B2A `CANONICAL_HISTORY.txt`, is 336,042 bytes, Git blob `b1b9667181872ef0673bd1d1d189609b4447fec7`, SHA256 `9fdee53a363aeb3b7c6963564543089e1b5ed91e39b0d4471efd052aa66b6485`. It has 8,001 standard output rows at integer redshift and stores xe plus Tm/Tr after the original interpolation. It does not directly store the requested native-grid x1s/xr_p states. Original `hyrec.c` explicitly constructs this integer-redshift output using `rec_interp1d`.

The original PR05B2 stage writes `canonical.out` into a temporary directory, compares its hash, then persists three snapshots and radiation histories. Its compact source ZIP was actually inventoried: 47 members, no retained native-grid absolute-state stream. The canonical original ZIP has 29 entries, 26 files, and no output.dat.

Additional raw native outputs were inspected through their exact provenance manifests:

- REC R3O h4_start_002 and R3S h4_legacy16 use a modified DLNA=(8.49e-5/4) and short onset histories, so they do not bind the original selected cell.
- R3R actual32 replay fixture has helium fields compacted and is a short h/4 source/parity fixture; it cannot be substituted for the selected original trajectory.
- R3T U4A/U4B restart streams use an accepted checkpoint near the early hydrogen onset, not the selected z≈1100 interval.
- R3C REI-matched original stdout uses different cosmology, including T0=2.7255 rather than2.728, and serves a conditional REI boundary.

Newer related sources were coordinated with the backup inventory agent. HE STATE04 (`2addfab8c8975febd69d2c88eecc09afea508fbe`) is an HD–H+ rovibrational edge with caller-supplied populations. CR proper R03 and R05 refer to a prescribed PHYS02 bath at100K and nH140m^-3 over [0,1e10]s. These are independent source contexts, not same-interval REC atomic states. Their exact backup acknowledgements and scope are preserved by the assembly agent.

Latest BASS parallel metadata also confirms open PR202, DV2-C expanding Bianchi-II, branch `research/bass-dv2c-expanding-bianchi-ii-20261027`, head `932bcd8f14c7f04b709007478ec9519a68457172`, updated2026-10-27T10:30:15Z. It is preserved as parallel work; this intake does not replace central files with that branch or an older snapshot.

## Source algebra for the next node

For the selected nondiffusion bins, retain original operation order:

```text
db = exp((Eb-E21)/TR)
Tvr_s = -rescale2g*A2s/abs(exp((Eb-E21)/TR)-1)
Trv_s = Tvr_s*db
Tvr_p = -exp(-E32/TR)/3*rescale2g*A3s3d/abs(exp((Eb-E31)/TR)-1)
        -exp(-E42/TR)/3*rescale2g*A4s4d/abs(exp((Eb-E41)/TR)-1)
Trv_p = Tvr_p*3*db
Gamma = -(Trv_s+Trv_p)
Dtau = Gamma*x1s*cube(hPc/Eb/fsR/fsR/meR)*nH_cm3/8/pi/H
```

Here fsR=meR=1. The selected rows all have b>=140, so the source's normalization of A2s below bin140 does not modify them. A short pure-math source port is sufficient; no recombination rate interpolation or compiled native helper is needed for Gamma.

The native general-bin solution gives
`(favg-fin)/(fout-fin)=1/(1-exp(-tau))-1/tau`
on the exponential branch. All selected right-snapshot depths exceed1e-6. The original code uses the different small-depth polynomial branch at tau<=1e-6; the next inverse must verify its inferred left depth remains on the exponential branch. The packet preserves the original threshold and formulas.

The primitive input clock is native `z=(1+8000)*exp(-DLNA*(izH0+i))-1`, izH0=18234. Both native-z-derived eta and the stored affine eta are retained, even though they agree at the two selected endpoints. Incoming interpolation uses the source's multiply/divide/log order and strict-past stencil. Source values at each witness are serialized as hex to support a later independent check.

For the selected nondiffusion bins, `Dfeq=-(Tvr_s*xr_s+Tvr_p*xr_p)/(x1s*Gamma)` and `xv=x1s*favg`. After the inverse, these provide another internal-level consistency relation. Direct Ly-beta/Ly-gamma ratios may be less cancellation-sensitive. These are source identities; they have not been numerically evaluated by this intake.

## QSS owner distinction

If actual states are reconstructed, native instantaneous channel balance still differs from finite endpoint storage. The original 2p row has direct non-Ly-alpha terms

```text
nH*(s*x1s*DAlpha_p+Alpha_p*Dxe2) - Beta_p*xr_p
+ R2p2s*(3*xr_s-xr_p)
+ sum_b(Tvr_pb*xr_p-Trv_pb*xv_b).
```

It balances the instantaneous Ly-alpha term through the algebraic QSS row. This does not by itself identify a physical finite refill equal to Delta x2p. The finite-storage defect is a diagnostic obligation; it must not be renamed as a supplied physical refill. Source coefficient/storage recovery and finite transaction admission are separate decisions.

The source additionally uses x1s=1-xHII without subtracting its tiny excited-level populations from this effective ground convention. A strict four-stock normalization must preserve and address that approximation explicitly, rather than silently redefining the recovered x1s or treating its projected states as an already exact finite hydrogen inventory.

## Native exporter fallback, not executed

If the saved-trace inverse fails identifiability or conditioning, the minimal fallback is one new, explicitly allocated acquisition of previously unretained observables:

1. Extract byte-locked original C sources. Add a guarded diagnostic directly after `Dfnu_hist[b][iz]=xv[b]/x1s` in `rec_HMLA_2photon_dxHIIdlna`, while x1s, xr, xv, primitive matrices, source vectors and optical depths are still in scope.
2. Emit only local indices5126 and5127: native z and clock; xe/xHII/x1s; xr_s/xr_p and equilibrium lifts; TM/TR/nH/H; Alpha/DAlpha/Beta; Trr/sr; Dfplus_Ly and outgoing Lyman; the 311 per-bin row operands needed to decompose native channel terms. Use hex floating output.
3. Exit successfully after the second selected native call. No full history or standard8001-row output is required.
4. Compile with the original recorded PR05B2 flags: `gcc -std=c11 -D_DEFAULT_SOURCE -O3 -Wall -Wextra -Wpedantic hyrectools.c helium.c hydrogen.c history.c hyrec.c -lm -o bass_atomic_export`, plus the new diagnostic macro. Do not invoke the old PR05B2 stage script.
5. Compare the two exported outgoing Lyman rows and virtual/average columns to the stored NPZ, using exact binary64 checks first. Record any mismatch; do not relax source-matching criteria silently.

Expected diagnostic output is below256KiB for two complete local row-operand packets. A proposed fresh allocation could cap the source run at one core, 10CPU seconds, 30wall seconds,512MiB and256KiB output, separately from compilation. These are proposed limits, not measured use or a deduction from an unknown old budget. The original C integrations in other stored source receipts finish in subsecond historical runs, but those are different scenarios and do not guarantee this run time. This fallback has not been implemented, compiled or executed in this intake.

## Preserved state

Original DAG completion remains27/88 unless root separately admits a new original node. Existing512 cohort maps and2 B3i RHS results are reused. Tests=0, consume=0, plot=0, native solves=0, remote writes=0, scientific admissions=0 in this intake. The ANISO continuum–finite14 joint difference3.447529542803539e-5, numerical reconstruction residual≈1e-11 and continuum numerical budget2e-8 remain distinct. Physical eS/en/eE/geometry/total radii and unknown remaining budgets remain null.

