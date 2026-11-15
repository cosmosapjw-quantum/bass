# BASS → REI IGM | original F08 S0 source-matched Sachs optical beam

2026-11-01. One bounded scientific physics unit, no changed original Einstein/REI source, no production/merge.

## Source authority and original objective

REI original F08 S0 Bianchi/FLRW paired ionization/electron history and Thomson observer sky are published in [REI PR349](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/349), immutable HEAD 1605236b8172db411d862caa219322d6af6953b1, exact source pair id 0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8. Five copied original source files retain their exact source SHA-256. In particular the original 10,752-row Thomson sky has SHA256 41fb767cc6c826047abf3799164f9e5b6a970c9dc879566147ad036226e4588d.

This BASS work is intentionally NOT based on the different KM2N Einstein–P8–Peebles photon/Peebles electron source (PR297/309/313) or the different CE1AS six-cell Einstein–Vlasov source. The BASS-owned contribution is optical-beam geometry for the SAME REI-F08 metric and normal observer. Both BASS main and the original REI owner remain immutable.

## Constructive theory and implementation

Signature (-,+,+,+), explicit c=2.99792458e10 cm/s. Original F08 model has prescribed a_i(t)=exp[H_i t], H_i=(1.01,.99,1)*1e-14 s^-1, t_o=1e13 s, electron tilt=0. Relabel spatial coordinates so a_i(t_o)=1; this is an exact constant coordinate change, not a new metric. For observer local direction n, omega(t)=sqrt(sum n_i² a_i(t)^-2) and observed relative redshift 1+z_rel=omega(t_e).

For orthonormal observer angular basis e_A, differentiating the exact null coordinate-ray position yields the Jacobi derivative
  J_iA=c integral_[t_e,t_o] [e_Ai/(a_i² omega)-n_i/(a_i² omega³) sum_j n_j e_Aj/a_j²] dt.
At fixed observed z_rel the directional change of t_e contributes only a longitudinal ray displacement, killed by the source screen. Let q_i=[n_i/a_i(t_e)]/omega(t_e), B_iA=a_i(t_e)J_iA and G_AB=sum_i (B_iA-q_i sum_j q_j B_jA)(B_iB-q_i sum_j q_j B_jB). D_A=(det G)^(1/4), D_L=(1+z_rel)^2 D_A. Gaussian time quadrature order 48 uses original proper seconds and H_i; no new Einstein or ionization IVPs.

The exact source matched FLRW comparator is the original F08 prescribed equal-H model: D_A,F=c z_rel/[Hmean(1+z_rel)]. DO NOT use BASS CE1AS's energy-matched collisionless-radiation FLRW as if it shared F08 source. The source original Thomson tau_BI, tau_FLRW and visibility remain unmodified. Define a conditional screened standard-candle brightness ratio at equal intrinsic luminosity, fixed observer-relative z and without scattering gain:
  F_BI/F_F=exp[-(tau_BI-tau_FLRW)] [D_A,F/D_A,BI]^2.
The hypothetical apparent magnitude difference is 5 log10(D_A,BI/D_A,F)+(2.5/ln10)(tau_BI-tau_FLRW). It is not observed photometry nor a full CMB anisotropy. Original F08 reference cosmological z0=10 is NOT the relative z used here.

Reference: Pierre Fleury, Cyril Pitrou & Jean-Philippe Uzan, Physical Review D 91, 043511 (2015), https://doi.org/10.1103/PhysRevD.91.043511. Literature supports the Bianchi I optical geometry, not F08 observational accuracy.

## Direct original physical output

10,752 actual source-ray rows: 4 target z windows at 0.02531512,0.05127110,0.07788415,0.09965886 and 3 angular grids 8x16,16x32,32x64. The original REI 30 columns are retained, with 7 newly derived BASS optical observables and 12 group scientific summaries. New owner Einstein/REI ionization IVPs: ZERO.

On the finest 32x64 sky at z_rel=0.099658855:
- D_A(BI)/D_A(FLRW): min 0.9901340216623494, max 1.0100651312150544.
- Conditional magnitude BI-FLRW: -0.02153029293811703 to +0.021747109026081634 mag.
- Original REI sky mean tau_BI=1.7511085110487457e-05.
- BASS source beam screen major/minor ratio max 1.000029208745869.
- Pearson corr[ln(D_A ratio), tau_BI-tau_FLRW]=0.9999960073559608.
- RMS geometric magnitude contribution / RMS Thomson-screening magnitude contribution = 101991.0816106376.

This geometric dominance is conditional to the prescribed 1% directional expansion shear and very low model optical depth, NOT a general statement about the real Universe. It is a new same-source BASS observer-distance/opacity conjunction rather than an independently observed new H+He history.

## Validation, test correction, hostile referee

- Five immutable REI349 original source bytes SHA verified; every one of 10,752 inherited REI ray identities/angles/redshifts retained.
- 10/10 standard Python tests and 10/10 python -O PASS. Independent same-source perturbed-ray finite-difference angular Jacobi, emission clock at fixed z, source-screen projector verified on three actual rays (Gram relative error below 3e-7). Exact de Sitter FLRW limit has max relative gap below 4e-14; Gauss-24 vs Gauss-48 on sample rays below 3e-13. Beam positivity, parity, malformed/negative source and expected row count controls PASS.
- Own initial small-z benchmark used D_A/z→1 too literally at z≈1e-4; de Sitter is D_A/(c/H)=z/(1+z), so corrected the TEST expectation to (1+z)D_A/z=1 without changing the physical code. No source or physics acceptance tolerance was relaxed.
- Wolfram exact de Sitter optical-distance integral residual zero; peer literature independently supports geometry. No distinct-author blind referee or native subagents were executed.

## Actual drift watchdog

MISSION: BASS must provide a physically source- and proper-clock-matched photon/observer consumer for central REI Bianchi IGM. DEFECT: past KM2 P8/Peebles electron-history response is not the original F08 S0 source, so injecting the two would be a source-owner mismatch. CONSTRUCTIVE CORRECTION: exactly one BASS original F08 S0 Bianchi-I Sachs beam/distance, combined with actually matched original REI Thomson history. REAL SCIENCE: 10,752 physically source-conditional observable records with numerical controls. SCIENCE GATE: original F08 is still a prescribed homogeneous one-cell, non-Einstein-constrained model and its scientific admission is HOLD. The 26-event F05 first canonical interval is still 160/131072 and blocked; F09 source-domain gap also remains. Do not claim Planck/CMB, all-order polarization, cosmic distance reconstruction, self-consistent Einstein equations or generalized continuum accuracy.

STOP additional source-free KM2 point/response PRs. Next only physically useful dependency: an Einstein-constrained source-equal late IGM electron/metric/radiation history with polarized Thomson source, followed by observational acceptance. BASS upper DAG 9/15 scoped, new fully closed 0; REI central 28/88 reported, new central 0; production HOLD, merge HOLD, no force push, AUTO_NEXT=false.
