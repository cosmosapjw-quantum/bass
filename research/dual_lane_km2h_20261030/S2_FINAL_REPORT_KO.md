# BASS KM-2H | 실제 HYREC-2/CLASS FLRW x_e를 외부 입력한 Einstein–Bianchi I 원본 편광 P8 과학 결과

**2026-10-30, independent bounded conditional science.** Parent BASS PR282 HEAD `0815ff69fb8be7123deb04a09fc54f15fbf6edd1`, BASS physics PR279 HEAD `b7faa761af032c68b86aec0ae30b61b817171669`; original KM2A/C/D/E/F/G source Git blobs exact verified and untouched. **Upper DAG 9/15 (21 edges), KM-2 PARTIAL, new completed upper=0.** This result is an *external FLRW microphysics sensitivity experiment*, not solved Bianchi recombination and not observed-universe CMB.

## 1. Input source and direct physical derivation

True native user HYREC-2/CLASS C input/outputs and prior FLRW source-stress tests were frozen in parent PR282. Input 1600-row FLRW table exact SHA256 `7f2c47c70dfab95e9ababed481db2c8d78429c0402ba1a85faeccb73df14d4da`. Original source user ZIP SHA256: HYREC-2 `f0b8bba1547ae9da83a0e663f57056884c689683396e1cf9a58bee1904040ac0`, CLASS `d1b2e1ce2b49de472e2cca9a327dc51c351e75bc0a2ad37d2e6538df76b289b7`. The FLRW original full-source/native-output archived in Drive ID `1dBMPIdAEN8jHUZlVqnV2IJ4FcNBmHQpV`, 17,738,639 bytes, full byte SHA256 checked in parent. This unit reused that verified source rather than pretending to re-solve HYREC atoms in Bianchi I.

Signature (-,+,+,+), Lambda=0, proper u=t/Tstar. Preserve original full ray P8 Hermitian polarized Thomson operator, original optical Doppler D_q, normal screen propagation, Einstein H/shear/coframe, self-consistent cold neutral baryon *bulk momentum*. The external volume-redshift **proxy** is `z_vol=(1+1200)*zeta^(1/3)-1` with baryon normal number ratio `zeta=det(A)`.

`Gamma_rest(u)=n_e_free_rest(u) sigma_T c`, `nu(u)=Gamma_rest*Tstar`, `n_e_free_rest(u)=x_e_FLRW(z_vol)*(1-YHe)*[M0 rho_unit/(gamma0 m_Happrox c^2)]*zeta gamma0/gamma`, `rho_unit=kappa c^2/(8pi G Tstar^2)` (J/m³), `m_Happrox=m_p+m_e`, `YHe=.245`. Only initial H is matched: `Tstar=H_BASS0/H_CLASS_phys(zref)`. The parent BASS initial synthetic matter-photon ratio=3 and kappa=.003 are unchanged and **not** CLASS matter densities. All baryon species have one common U by assumption, and the specified neutral H formation transfers mass fractions without reaction-energy or finite-slip kinetics. Electron temperature from HYREC is recorded but not an electron thermal pressure or Kompaneets source.

## 2. New six actual coupled Einstein/photon physical histories

GL n_theta=12/16, n_phi=2*n_theta, same original P8 ray/seed for each mode, same constrained Einstein initial data. All physically evaluated on 0<=u<=.25. Source choices: native HYREC FLRW xe(z_vol), CLASS embedded HyRec2020 xe(z_vol), frozen initial HYREC xe(1200) control. Each saved case has full 5-epoch stress/P8 source/charge/Einstein diagnostics, 41 genuine ODE dense-output source samples, 24-node independent force-gap quadrature, and all individual ray directional optical depths.

| n_theta=16 | HYREC varying | CLASS varying | HYREC frozen |
|---|---:|---:|---:|
| Initial nu_rest Tstar | 83.7054651983 | 83.7069413411 | 83.7054651983 |
| xe(u=.25) | 0.134477103528 | 0.134481358957 | 0.32208146832 |
| Photon ray mean tau to u=.25 | 12.8301948241 | 12.8304954934 | 18.6765552017 |
| Photon ray tau min/max | 12.6335426922/12.9142109033 | 12.6338433555/12.914511576 | 18.479894247/18.7605762091 |
| Einstein shear sourced norm | 0.000517142257324 | 0.000517131657969 | 0.000472517488527 |
| H(u=.25) | 0.347416200106 | 0.34741620014 | 0.347416082624 |
| Hamiltonian constraint normalized max | 5.026e-12 | 5.021e-12 | 4.976e-12 |
| momentum constraint normalized max | 1.344e-11 | 1.344e-11 | 1.344e-11 |

The original electron fraction falls from `xe(1200)=.32208146832` to `xe(1092.276)=.134477103528` (real HYREC table + source-dependent numerical volume proxy). Corresponding actual BASS proper nu falls `83.705465 -> 27.01933`, vs frozen ending `64.713065`. HYREC changes mean ray optical depth by **-5.84636037761** vs frozen (about **31.3%** lower), photon full P8 anisotropic stress max component difference **0.0436799611657**, and sourced shear norm **4.46247687976e-05** (about **9.444%** higher). HYREC-vs-CLASS mean tau **-0.000300669271812**. Small HYREC-vs-CLASS differences do not demonstrate independent atomic microphysics because the original C code is shared.

Original source-normalized n_theta=12 vs16 Hamiltonian max for HYREC: `2.6485e-09` vs `5.0264e-12`, momentum max `6.6319e-09` vs `1.3438e-11`. Raw P8 vs separately covariant Thomson source gap is measured, not projected. Direct independent GL24 Hamiltonian source-integral endpoint residual `1.0065e-14`, momentum-integral residual `6.0404e-12`; number/bulk radiation screen and charge constraints are tested without relaxation.

## 3. Important hostile review: NOT a parameter-matched observed Universe

At z_ref=1200, `Tstar=218601.806773` Julian years sets **only H_BASS(0)/Tstar=H_CLASS_phys(1200)**. The normal hydrogen proper density in the BASS initial synthetic matter background is `1888980490.05 m^-3`, whereas CLASS nH(1200) implies a ratio **5.73964456116**. At u=.25 BASS H/H_CLASS(z_vol) = **0.992671472157** and the nH ratio=5.88250733333, so the background is not CLASS. **This is a scoped sensitivity experiment at original synthetic BASS source strength**, not realistic recombination at that density. Imposed xe(z_vol) is not a self-consistently solved ionization rate in an anisotropic radiation field. No valid sky C_l, no ionization reheating or 13.6 eV binding energy, no Maxwell–Coulomb finite-slip, no spectral distortion, no observational/Planck data fitting. Hydrogen mass is approximated by m_p+m_e neglecting binding energy; helium is assumed neutral throughout the restricted redshift interval. Total mass stress remains conserved, ion and neutral species are not separately conserved without chemical reaction source. Native subagent and different-author independent review NOT_RUN, self-hostile code/data tests performed.

## 4. Real scientific plots and measured data (not synthetic curves)

Plot generator `make_science_plots.py` reads 41 actual DOP853 source states per case and emits six distinct PNGs: external xe, physical Thomson rate, original polarized photon anisotropic stress, sourced Einstein shear, Einstein H and all directional-ray tau histogram. Results include 246 physically evaluated source time rows, 30 full stress epochs, 144 GL24 original P8 raw-covariant fourforce rows and individual ray optical depths. No fabricated continuation/extrapolation of FLRW ionization beyond z=900–1200.

## 5. Reproducibility / statuses

Executable source `research/dual_lane_km2h_20261030/external_opacity_bianchi.py`; original inherited BASS code and FLRW source locked by byte Git SHA. `python -m pytest -q research/dual_lane_km2h_20261030/tests/test_external_opacity.py` **18 PASS locally** at NumPy 2.3.5 SciPy 1.17.0. Source-inclusive S0 and S1 ZIP manifest SHA+CRC verified. Actual GitHub CI must be separately read before any remote claim; do not pretend a model's self hostile review is distinct-author R6/C9. S0/1 stage complete scoped; S2 publication, final CI and external storage receipts to be appended to Draft PR description without a false Git HEAD timestamp. Upper BASS **9/15 (21 edges), KM2 PARTIAL, new upper completed=0**, production_ready=false, merge_ready=false, auto_next=false.

Cited primary method: Lee & Ali-Haïmoud, Phys.Rev.D102 083517 (2020), doi:10.1103/PhysRevD.102.083517; parent user-source original code via PR282; Ma & Bertschinger, ApJ 455,7 (1995), doi:10.1086/176550. Neither paper claims that this original BASS Bianchi-I conditional experiment is an observed-universe result.

## 6. Targeted cross-event CI binary-array portability repair (2026-10-31)

Immutable original BASS Git blobs passed in both Push CI #41081428180 and the first PR CI #41081537637. Both events solved all six actual Einstein–P8–baryon IVPs, with the same original photon normal-frame energy/flux/pressure, but their floating-point-generated initial photon array and (for nθ=16) generated ray-array raw byte SHA differed. Thus the original test comparing those *generated floating-point arrays* to one host-specific hard-coded hash was **not a valid cross-environment immutable source test**. First PR CI is explicitly **FAIL 17/18** (one representation-identity mismatch), not relabeled as successful. See `PR285_NUMERICAL_SEMANTIC_AUDIT.json` for the exact two source physical output JSON SHA256 and six-case numerical-difference details.

The bounded repair leaves every original scientific equation, parent source file, original ray source contract, solver tolerance, test gate for Einstein Hamiltonian/momentum, P8 transport, optical depth and shear **unchanged**. It replaces only the invalid hard-coded *generated array* SHA comparison with (a) exact Git blob source locks already in `exact_source_guards`, (b) exact within-run J and ray hashes across the three opacity scenarios, and (c) independent original initial photon normal-frame energy/flux and stress/source-moment numerical equality with tight portable absolute tolerances. A local rerun of the revised 18 tests on both Push-CI physical JSON and the first PR-CI physically computed JSON passed **18/18 each**. Push vs PR optical depth means differ ≤3e−14; sourced shear ≤5e−17; full initial photon energy/flux values coincide. No physical result was selectively discarded. The remediated commit and subsequent CI must each be independently checked before any new final remote success claim.
