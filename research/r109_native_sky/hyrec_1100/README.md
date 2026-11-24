# Conditional sky from recombination to a normal observer

This calculation prescribes a single homogeneous HyRec electron fraction from redshift 1100 to zero. The source is the original REC q=0 hydrogen/helium history. Source identity, $n_{H,\mathrm{emit}}$, and $H_{\mathrm{emit}}$ follow `source.json`. The scalar `xe` is free electrons per H nucleus, including the source's helium contribution. Its late-time value traces residual ionization in the absence of astrophysical reionization.

The native clock is η = ln(a/a_emit). Its terminal value is ln(1101). The source redshift labels select the knots of the prescribed composition; the tilted Bianchi calculation evolves its own normal-clock H/H_emit and rest density of the electron host. For a frozen geometry substep its positive bare exposure is

$$
\Delta\tau=\frac{c\sigma_T n_{H,\mathrm{emit}}}{H_{\mathrm{emit}}}
\frac{n_{H,\mathrm{rest}}/n_{H,\mathrm{emit}}}{H/H_{\mathrm{emit}}}
\int_{\eta_0}^{\eta_1} x_e(\eta)\,d\eta.
$$

Each linear source segment has an exact integral at the frozen density and expansion rate. The first massive beam carries the electrons. Recoil advances that beam's velocity and applies the directional boost in the collision operator. The native host tracks photons and two counter-streaming dust beams. The cosmology in the REC pin supplies the emission anchors and source electron fraction; it supplies no subsequent host expansion-rate interpolation. No dark-energy or halo-source reionization history is added. The initial sky is homogeneous and unpolarized; the output comprises deterministic T/E/B angular modes and products induced by the specified geometry, dust and scattering.

From the BASS repository root:

```sh
dir=research/r109_native_sky/hyrec_1100
python3 "$dir/extract.py" /path/to/rec_bianchi "$dir"
cargo build --release --manifest-path _rustcore/Cargo.toml --example homogeneous_sky
python3 "$dir/run_long.py" --binary /path/to/target/release/examples/homogeneous_sky --raw /tmp/bass-recombination-control --jobs 4 --output /tmp/bass-recombination-results
```

Use a fresh raw directory for each replay. To select one case pass `--case I_384`. The input table has the exact header `eta xe_per_H` separated by a tab. Its 1101 ordered samples use every available integer redshift from 1100 to zero. The parser checks the emission origin, positive anchors and interval coverage. Closed-form flat, untilted dust-plus-radiation expansion with an independent Gaussian quadrature supplies the zero-shear optical-depth check.

`long_epoch.json` records full-run maximum constraints, final H and optical depth, the six C_ell channels, and step/grid differences in complex harmonic coefficients for ell ≥ 2. `long_modes.tsv.gz` preserves every signed m including cross products. Comparisons of symmetry-suppressed B modes should use the reported absolute norm; relative errors become uninformative near zero. The coefficients are conditioned on the chosen initial state and externally prescribed recombination chemistry.

## Numerical results

For the untilted flat control with initial matter fraction 0.75 the independent solution has $H/H_{\rm emit}=\sqrt{0.75 e^{-3\eta}+0.25 e^{-4\eta}}$. It gives τ = 1.1244242370867192 and final H/H_emit = 2.370911732163216 × 10⁻⁵. At 12,288 time steps the Gauss-reduced acceleration equation gives τ = 1.12442452963666 and H/H_emit = 2.37091173516725 × 10⁻⁵. The maximum absolute physical Hamiltonian residual over this run is 2.532 × 10⁻⁹; the corresponding Raychaudhuri run has 5.861 × 10⁻⁶. The independent residual is evaluated from the evolved geometry and matter at each recorded step. The choice of acceleration equation is separate from the input REC history's shear label q=0.

| Model and numerical control | TT at ℓ=2 | EE at ℓ=2 | BB at ℓ=2 |
|---|---:|---:|---:|
| I, 12,288 steps, 6 × 12 angles | 3.56379 × 10⁻⁸ | 2.77491 × 10⁻¹¹ | 5.13 × 10⁻³⁰ |
| VII0, 768 steps, 96 × 192 angles | 3.56468 × 10⁻⁸ | 2.76870 × 10⁻¹¹ | 1.20 × 10⁻³⁴ |
| Generic VIII, 12,288 steps, 6 × 12 angles | 1.52158 × 10⁻⁵ | 3.21667 × 10⁻¹¹ | 1.46774 × 10⁻¹² |

The I and VII0 runs use the preset shear 0.0005 and opposed beams with initial speed 0.001 c. The VIII initial tensors in `generic_viii.tsv` do not commute. The momentum constraint determines a common initial velocity β = (1.42223, 3.55556, 1.11111) × 10⁻⁷. Doubling the VIII time steps from 6144 to 12288 changes the complex ℓ=2…4 T/E/B mode vectors by 7.57 × 10⁻⁶, 2.81 × 10⁻⁴ and 2.79 × 10⁻⁴ relative to the finer result. For the 384-step VIII run, increasing 6 × 12 to 10 × 20 angular nodes changes these three modes by 3.89 × 10⁻⁶ or less.

VII0 needs a separate azimuthal resolution check. With 96 polar nodes and 768 time steps its B-mode norm at ℓ=2…4 drops from 1.11 × 10⁻⁶ to 7.60 × 10⁻⁸ to 1.66 × 10⁻¹⁶ as azimuthal sampling increases from 48 to 96 to 144 nodes. Increasing to 192 gives 1.09 × 10⁻¹⁶. The last pair changes the signed T/E vectors by 1.42 × 10⁻¹⁵ and 3.24 × 10⁻¹⁶ in absolute norm. This check identifies a finite-angular-sampling B signal in the coarser VII0 runs. The signed per-mode products in the archive allow direct inspection of individual m and all six channels.

The 40-run archive records the pinned BASS executable SHA in `long_epoch.json`. The subsequent public signed Codazzi convention is checked in `diagnostic_sign.json`: a flat and a noncommuting VIII case reproduce all signed sky modes and spectra byte for byte. Across all 770 matched diagnostic rows the three Codazzi components reverse sign and every other column agrees exactly. The archived maxima use absolute values.
