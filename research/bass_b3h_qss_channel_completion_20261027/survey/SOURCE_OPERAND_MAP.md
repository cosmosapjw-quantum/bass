# Native QSS source operand map for [5126,5127]

This source-intake result prepares a new finite computation. It does not rerun the completed x1s/x2s/x2p inverse, native solver, old tests, B3i consumption, or plots. No new TM/xe inverse, rate interpolation, channel evaluation, or matrix operation has been executed here.

## Exact available inputs

The original REC source is `d6dbe39a4923439547c01695d9020ba39367ea90`. Its saved radiation history `data/pr05b2_source_history_v060.npz` has SHA256 `d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1` and 35,239,470 bytes. The original HyRec archive SHA256 is `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`; exact `hydrogen.c` is 37,471 bytes, SHA256 `421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b`.

`NATIVE_QSS_STORED_INPUT_5126_5127.json` contains the following existing data and source interpolation witnesses:

- Two native knots, their original clock values and global indices 23360/23361.
- All 311 stored average/outgoing virtual radiation values at each knot.
- All 311 incoming values reconstructed only by the original strict-past interpolation, with source row/index/weight witnesses.
- Both Lyα/Lyβ incoming values and all three stored Lyα/Lyβ/Lyγ outgoing values.
- The completed inverse's primary endpoint values copied from science `0bdbd2ad1357c4b3141d3488a94534d082d1a0cf`, delivery `6bf4a5d90b05f7e583be698854e521d259287837`. Their values, 70-digit references, and assumed rounding intervals are reused without execution.

Every one of the right snapshot's 311 incoming, average, and outgoing virtual values and both incoming Lyman values is bit-identical to the extracted value. This is a source extraction comparison, not a new science result. JSON shortest-roundtrip decimal retains the extracted binary64 values exactly.

`native_source/` contains original bytes for `hydrogen.c`, `hydrogen.h`, `history.c`, `history.h`, `hyrec_params.h`, `hyrectools.c`, `hyrectools.h`, `Alpha_inf.dat`, `R_inf.dat`, `two_photon_tables.dat`, and `input.dat`. Full tables are small enough that slicing is unnecessary:

| Original table | Bytes | SHA256 |
|---|---:|---|
| Alpha_inf.dat | 132000 | c543c755d99ba8e999450dd5cb486a3ad88d26378da0ccc8363b10418e4832bd |
| R_inf.dat | 1700 | ce914f4b552ba55ba00f7916f36b0986f19adfdb638e5aefae91f7b2d05a8112 |
| two_photon_tables.dat | 25191 | 93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9 |

The original right snapshot is separately preserved at `validation_only/RIGHT_NATIVE_SNAPSHOT_5127.csv`. It contains actual xe, xHII, TM/TR, both real departures, sr/Alpha/DAlpha/Beta, Trr, all Trv/Tvr/Tvv, and diffusion coefficients. It is a holdout for reconstruction, not the source of those new reconstructed coefficients.

## 1. A constructive TM input from diffusion edges

The new candidate bins are **100 and 179**, the edges of the diffusion region [100,180). In `populate_Diffusion` the absent external diffusion coefficient is zero and the single inward coefficient is linear in the rescaled matter temperature:

\[
A_{100,\uparrow}=\frac{2E_{21}^2}{m_H}\frac{A_{1s,100}}{(E_{101}-E_{100})^2}T_M,
\qquad A_{100,\downarrow}=0,
\]

\[
A_{179,\downarrow}=\frac{2E_{21}^2}{m_H}\frac{A_{1s,179}}{(E_{179}-E_{178})^2}T_M,
\qquad A_{179,\uparrow}=0.
\]

The source subsequently multiplies both by `rescalediff = rescale2g*fsR*fsR*meR`, with `rescale2g=(fsR^4)^2*meR`. Both ratios equal 1 in the selected source. `mH=0.93878299831e9` in the source's eV/c² convention. The exact constants and operation order are retained in the source files.

The established triple-trace identity applies to a diffusion bin as well: its effective source includes neighbor currents, but their common source cancels from the ratio. For i=incoming, v=average, o=outgoing in the source exponential branch,

\[
\frac{v-i}{o-i}=\frac1{1-e^{-\tau}}-\frac1\tau.
\]

After a new, independently checked inversion,

\[
\Gamma_b^{\rm obs}=\frac{\tau_b}{x_{1s}K_b},\qquad
K_b=\left(\frac{h_Pc}{E_b f_s^2m_e^R}\right)^3\frac{n_H}{8\pi H}.
\]

Let \(\Gamma_b^{(0)}=-(T_{rv,sb}+T_{rv,pb})\) denote the original two-photon contribution before diffusion updates. Then

\[
T_M^{(b)}=\frac{\Gamma_b^{\rm obs}-\Gamma_b^{(0)}}{
\mathrm{rescalediff}\,(2E_{21}^2/m_H)A_{1s,b}/\Delta E_b^2}.
\]

The original right snapshot has τ100=0.011040823922536551 and τ179=0.012406745166279052. These values selected the candidate regime; they are not inverse inputs. The inferred left values must independently remain in the exponential branch above 1e-6. The thin-bin trace ratio can amplify floating error, so the new contract must report conditioning and compare both edges without averaging away disagreement. No new numerical TM value is asserted by this intake.

For bin100 the A2s table must first undergo the source's **sequential sum and normalization over bins0..139 to L2s1s=8.2206**. Bin179 is above this normalization region. Omitting this step changes Γ0. Effects A/B/C/D and diffusion are all1. Preserve the original source's small-τ branch if another bin is used later.

## 2. Rate-table and block reconstruction

`read_rates` loads 100 radiation-temperature points, logarithmically spaced from0.004 to0.4eV, and40 matter/radiation ratios uniformly spaced from0.1 to1. The original `maketab` operation and `DlogTR`/`DTM_TR` definitions are in `hyrectools.c` and `hydrogen.c`. Alpha has two real-state components. The original interpolation is cubic in log rates, with four-point weights and clamped stencil indices. `DAlpha=Alpha(TM,TR)-Alpha(TR,TR)`. Beta is then obtained by the source detailed-balance factor, including the separate 1/3 for2p. R2p2s is interpolated on the radiation grid only.

The complete endpoint coefficient dependencies are now explicit:

| Operand | Required inputs | Source routine |
|---|---|---|
| Alpha, DAlpha | new TM, inherited TR, complete original Alpha table | interpolate_rates |
| Beta, R2p2s | inherited TR, original Alpha/R tables | interpolate_rates |
| two-photon Trv/Tvr | inherited TR, original normalized table, effects | populateTS_2photon |
| diffusion Aup/Adn/A2p | new TM, original energy/A1s table | populate_Diffusion |
| Trr | Beta, R2p2s, RLya, photon and diffusion couplings | populateTS_2photon |
| Tvv, sv | above coefficients, inherited x1s/nH/H, actual incoming array | populateTS_2photon |
| sr | xe/xHII source convention, rates, actual incoming Lyman values | populateTS_2photon |
| xr | completed x1s and yp/ys from prior inverse | inherited result |
| xv | inherited x1s × actual saved average radiation | original stored-variable definition |

The 311 virtual unknowns are radiation variables; they are not 311 atomic levels. Array notation is unusual: C `Trv[i][b]` enters real row i/virtual column b, whereas `Tvr[i][b]` enters virtual row b/real column i.

At fixed endpoint the original QSS system is

\[
T_{rr}x_r+T_{rv}x_v=s_r,\qquad T_{vr}x_r+T_{vv}x_v=s_v.
\]

The original Schur reduction is

\[
M=T_{rr}-T_{rv}T_{vv}^{-1}T_{vr},\qquad
b=s_r-T_{rv}T_{vv}^{-1}s_v,\qquad Mx_r=b.
\]

This is an exact source map. Executing these operations belongs to the newly frozen coding unit. A dynamically evolving real-state extension or interpolation of M,b between the endpoints would be a separately declared model, not a recovered original time history.

## 3. Electron source convention and independent row recovery

The native source defines `x1s=1-xHII` without subtracting the tiny excited fractions. Do not replace that convention to enforce a different stock normalization.

The selected source is in the H-only phase. `EARLIER_H_ONLY_PHASE_WITNESS.json` records an actual earlier native snapshot at local index3161, z=1299.9971824762927, with xe=xHII=0.56361437690177074. The original program leaves the simultaneous H/He loop when xHeII≤1e-6 and advances only forward through H-only loops, passing xe as both xe and xHII. The selected knots5126/5127 are later. This is a source-model neutral-He convention, not a claim that physical helium ionization is identically zero.

The archive's right snapshot differs from the selected right CSV by two added INTERFACE rows; all2516 shared literal rows are identical. This identifies a format addition rather than a scientific mismatch.

Consequently the source coefficient construction may use \(x_e=x_{\rm HII}=1-x_{1s}\) in this chosen late-era source. The following two row expressions give independent consistency readouts and retain the general nonzero-He algebra:

\[
s_i^{\rm req}=\sum_jT_{rr,ij}x_{r,j}+\sum_bT_{rv,ib}x_{v,b},
\]

\[
g_s=3R_\alpha x_{1s}(1.664786871919931)f^+_\beta,
\qquad g_p=3R_\alpha x_{1s}f^+_\alpha,
\]

\[
C_i=s_i^{\rm req}-g_i
=n_H[\alpha_i x_ex_{\rm HII}-\alpha_i^{\rm eq}s x_{1s}],
\quad \alpha_i^{\rm eq}=\alpha_i-\Delta\alpha_i,
\]

\[
x_e^{(i)}=\frac{C_i/n_H+\alpha_i^{\rm eq}s x_{1s}}{\alpha_i x_{\rm HII}},
\qquad s=\mathrm{SAHA\_FACT}\,T_R^{3/2}e^{-E_I/T_R}/n_H.
\]

Use component-scale residuals if evaluating these cancellation-sensitive identities. Algebraically making a row sum vanish does not independently establish a finite physical refill.

## 4. Source channel decomposition and energy boundary

The original two real rows can be decomposed into the following rate contributions per hydrogen nucleus. Let the stored departures be r_s,r_p and retain source-effective conventions.

| Contribution | 2s row | 2p row |
|---|---|---|
| Effective continuum net | nH(s x1s DAlpha_s + Alpha_s Dxe2) − Beta_s r_s | nH(s x1s DAlpha_p + Alpha_p Dxe2) − Beta_p r_p |
| Effective 2p↔2s | R2p2s(r_p−3r_s) | R2p2s(3r_s−r_p) |
| Lyα | 0 | 3 RLya x1s fplusα − RLya r_p |
| Lyβ/γ | g_s −3 RLya[1.664786871919931 exp(−E32/TR)+1.953125 exp(−E42/TR)]r_s | 0 |
| Each two-photon virtual coupling | Tvr_s,b r_s − Trv_s,b xv_b | Tvr_p,b r_p − Trv_p,b xv_b |
| Diffusion at bins139/140 | 0 | Aup139 xv139 + Adn140 xv140 −(A2p_dn+A2p_up)r_p |

The two-photon coupling row in this table uses **pre-diffusion** Tvr/Trv; otherwise the separate diffusion row would be counted twice. For EFFECT_A=0 a standalone L2s1s decay is added, but the selected source has EFFECT_A=1 and already represents that process through its table. Incoming Lyγ departure is assumed zero by the native source, whereas its outgoing trace is stored.

The newly obtainable endpoint source channels and Schur operands are concrete new observables. Their finite representation must be declared. They do not turn a QSS storage defect into a physical source: instantaneous QSS balance and nonzero endpoint population storage remain different statements.

The native effective coefficients eliminate higher excited levels and use a thermal radiation bath for untracked companion photons. The source tables primarily specify number/population rates, not a fully resolved spectrum of every eliminated cascade or every continuum electron-energy moment. Likewise xv is not an atomic stock. A level-energy projection can define a source-effective internal-energy bookkeeping term once the state and normalization are declared; it must be distinguished from an independently supplied microscopic energy/recoil donor. Any selected dynamic completion, finite channel interpolation, thermal reservoir owner, and sector stress/four-force mapping should name its assumptions directly. Unselected CR/HE/molecular/geometry suppliers are not universal prerequisites.

## Preparation and reuse accounting

The first pure-data extraction attempt repeatedly decompressed NPZ arrays and was interrupted with exit130. The extractor was corrected to cache the same arrays once, and the second extraction completed. No scientific algorithm, tolerance, model, or accepted result changed. Preparation CPU was not measured and remains unknown; it is not recorded as zero or charged against an invented inherited remainder. The completed extraction's tool-reported wall time was0.806814793s. All native solves, new inversions, old tests, old consumes, and plots remain0 in this intake.

The original central DAG remains27/88 with completion increment0. Physical radii eS/en/eE/geometry/total remain null. Prior ANISO joint difference, reconstruction residual, continuum numerical allowance, and unknown budgets retain their separate meanings.
