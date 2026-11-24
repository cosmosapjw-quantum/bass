# R109 finite sky laws

The three mode tables are byte copies of the 64-step BASS material-history runs named REC_1200_1000, ZERO and SHEAR_PLUS in the R109 integration suite. REC covers the recombination window; ZERO and SHEAR_PLUS cover the reionization window. All three use the same celestial dyad, Condon–Shortley phase and HEALPix E/B signs. T is the fractional fourth-root bolometric temperature relative to its sky mean. Polarization is expressed in units of four times the angle-averaged bolometric intensity. The example assigns the three complete deterministic outputs probability masses 1/7, 2/7 and 4/7, respectively. This is a declared probability law over the three branch outputs. Estimating cosmic covariance at a shared observation epoch would require a model and ensemble for that epoch.

Let z(r) contain each field and signed (ell,m) on branch r. For normalized weights p, the raw moment is sum_r p_r z(r)z(r)†. Subtracting the outer product of the weighted means gives the population covariance. The implementation accumulates the centered matrix with the weighted Welford update and also accumulates the raw entries independently. The receipt checks both against two-pass NumPy for all 5,625 complex entries. Normalized Haar measure gives a separate law over orientations of a single sky. Schur orthogonality leaves only equal (ell,m) in its raw second moment, with value sum_k a_X(ell,k) conj(a_Y(ell,k))/(2ell+1). The monopole has zero orientation covariance. Proper rotations preserve any supplied parity-odd cross-power.

From the BASS root, reproduce the reference result with Python, NumPy, healpy and Cargo. The reference also integrates 405 independently rotated HEALPix skies over SO(3) to check both the raw and centered Haar results.

```bash
cargo build --manifest-path _rustcore/Cargo.toml --example sky_covariance --offline
f=compiler/validation/fixtures/r109_sky_law
python compiler/validation/r109_sky_law_oracle.py \
  --binary _rustcore/target/debug/examples/sky_covariance \
  --member REC_1200_1000 1 "$f/REC_1200_1000.tsv" \
  --member ZERO 2 "$f/ZERO.tsv" \
  --member SHEAR_PLUS 4 "$f/SHEAR_PLUS.tsv" \
  --rotate-haar --output /tmp/r109-weighted-sky-law.json
```

To consume new mode tables, give one or more `--member WEIGHT FILE` arguments directly to the Rust example. Select individual mode pairs with `--pair L M L2 M2`, which retains only requested input coefficients. Use `--all` to stream the complete output. The full covariance has 9(L+1)^4 complex entries; the program writes one pair at a time. The orientation-only invocation takes `--haar FILE` with the same output selection. The input and output use ordinary whitespace-separated columns with a header. Input frame, epoch, unit and filtering choices define which scientific ensemble a list of files represents.
