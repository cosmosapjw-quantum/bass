# BASS PR164: self-consistent massive Einstein–Vlasov tangent

2026-10-16 KST. Source parent: BASS PR163 `9ea46052358ba3e190317347d7f0001bab23c398`. This isolated research addition implements **one new missing stage**: nonlinear LRS Bianchi-I Einstein evolution of the source-normalized massive FD96 species together with an analytic first-order sensitivity to its initial angular quadrupole amplitude \(A\). The radiation background is **isotropic and prescribed**; no native REI H/He chemistry, gamma/nu multipole evolution, E/B Thomson or stellar radiation is included. No merge into production.

The original `bianchi/matter/freestream.py` Gauss–Legendre FD96 + GL32 quadrature rule is **reconstructed from its formula** (Git blob `8467932c3281f9d426712b3a582f2aae3a484692`), not imported or byte-copied. It reproduces the previously published \(m/T_{\rm ref}=30\) source normalization \(\mathcal N=54.478197513209125\). AX03 cosmology/time source: frozen `REI_BACKGROUND_FAMILY_LOCK.json` Git blob `7bfd190fe4cc722c2813c70e036d0279a0d83641`; \(a_{\rm ref}=1/21\), \(a_{\rm end}=1/5\), signature \((-+++)\).

With \(x=\ln(a/a_{\rm ref})\), \(s=\dot b\), \(\Sigma=\sqrt3|s|/H\), \(v=s/H_{\rm ref}\), \(T=H_{\rm ref}t_{\rm elapsed}\), \(C_m=\Omega_m f_m/a_{\rm ref}^3\), the **source-owned** dynamics is

\[
H^2=H_0^2[\Omega_m(1-f_m)/a^3+\Omega_r/a^4+\Omega_\Lambda+C_m\rho_m(x,b;A)]+H_{\rm ref}^2v^2,
\quad b'=H_{\rm ref}v/H,\quad
v'=-3v+\frac{H_0^2C_m\Delta P_m}{H_{\rm ref}H},\quad T'=H_{\rm ref}/H.
\]

Exact collisionless source identities are \(\partial_b\rho_m=-2\Delta P_m\) and \(d_x\rho_m=-3(\rho_m+\bar P_m)-2(s/H)\Delta P_m\). The mass-shell susceptibility \(\chi=\partial_b\Delta P_m\) and direct distribution-amplitude derivatives \(\partial_A\rho_m,\partial_A\Delta P_m\) drive the **variational ODE** \(Z'=J_y Z+F_A\), \(Z(x=0)=0\). Independent Raychaudhuri identity:

\[
2HH'=H_0^2[-3\Omega_m(1-f_m)/a^3-4\Omega_r/a^4-3C_m(\rho_m+\bar P_m)]-6s^2.
\]

The \(\Delta P_m\) shear-work terms cancel only if kinetic continuity, Einstein shear, and Hamiltonian signs/normalizations are consistent.

## Actual execution evidence

**14/14 Python tests passed**, including FD96 source norm, exact isotropic shear, tiny \(b=\pm10^{-16}\) sign, positivity/matter-budget, pressure/parameter derivatives, analytic Einstein Jacobian, variational endpoints versus separately integrated finite differences, energy-work integral, Raychaudhuri finite differences, DOP853 tolerance refinement and a proposed read-only receiver schema. The primary execution occurred in the **isolated ChatGPT Python environment (NumPy 2.3.5, SciPy 1.17.0)**, *not* in the user's Ubuntu or NCP; the Desktop Commander account hit its monthly usage quota. No new NCP performance number is claimed. This invocation's Wolfram Language kernel returned **four algebraic zero residuals**; local xAct was NOT rerun.

The independent \(A\)-tangent/central-difference maximum absolute endpoint discrepancies for \(m/T_{\rm ref}=3,30,300\) were \(2.98,3.38,4.83\times10^{-12}\), respectively (dimensionless \(b,v,T\) coordinates). The **8×121 = 968-row** proposed receiver CSV has an independent Raychaudhuri residual no greater than \(5.24\times10^{-11}\) relative (a finite-difference test, not a tautological Hamiltonian self-check).

An important reference correction: \(A=0\), \(s=0\) yields an **isotropic kinetic FLRW geometry**, but not the *unmodified cold-dust* \(\Omega_m\) clock when \(f_m>0\). At \(f_m=0.1\), final \(z=4\), differences in \(H\) relative to the original cold-dust FLRW clock are \(-1.51685\%\) (\(m/T=3\)), \(-0.0327593\%\) (\(m/T=30\)), and \(-0.000332725\%\) (\(m/T=300\)). Original cold FLRW is recovered when \(f_m=0\). The initial test assuming cold-FLRW equality at \(f_m>0\) failed, and was corrected as a physical-assumption error without changing scientific tolerances.

## Reproduction

```bash
cd research/rei_einstein_tangent_20261016
OPENBLAS_NUM_THREADS=1 python3 -m unittest -v test_kinetic_tangent test_export_bridge
OPENBLAS_NUM_THREADS=1 python3 run_campaign.py --out /tmp/bass_pr164_campaign.json
OPENBLAS_NUM_THREADS=1 python3 export_rei_bridge.py --out /tmp/bass_pr164_rei_table --points 121
```

The proposed `REI_HANDOFF.json` explicitly distinguishes signed `s/H` from \(\Sigma\) and does not assert Rust type validation or native REI adoption. A complete source/output/evidence archive is backed up to the user's Google Drive `BASS_BACKUPS/BASS_PR164_Einstein_Vlasov_Tangent_20261016.zip` and ChatGPT Library `/BASS/BASS_PR164_Einstein_Vlasov_Tangent_20261016.zip`, with independently downloaded archive/SHA-256 byte checks. Main/full original BASS PR163, REI PR150/152, BASS_HE PR66 and bass_cr PR72 are not mutated.

**Admission:** derived, Python-implementation-verified, numerically checked **only** for this LRS massive/cold-dust/isotropic-radiation system and proposed typed-table boundary. Not a source-locked all-species CMB/chemistry Einstein production solver. Next: owner-approved opt-in native geometry supplier and source-versioned fresh H/He checkpoint, ensuring photon/gas/matter four-momentum ledgers before EoR admission.

Research context: [Heinzle–Uggla, CQG 23 (2006)](https://doi.org/10.1088/0264-9381/23/10/016); [Cardall–Mezzacappa, PRD 68 (2003)](https://doi.org/10.1103/PhysRevD.68.023006).
