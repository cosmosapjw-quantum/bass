# BASS KM2J | actually coupled hydrogen Peebles, polarized P8 and Einstein Bianchi I (scoped)

## Baseline and reproducible numerical result (2026-10-31)

Draft PR291, base immutable PR289 HEAD `8e3cf0ac1eab96142494903ed940e27d1b66e380`, original KM2F/G/H/I sources unmodified. Source-guarded four genuinely new **joint** IVPs: GL12 and GL16 each with (a) dynamically recombined electron abundance and *both* Thomson+grey chemical energy-momentum feedback and (b) identical live chemistry and Thomson opacity without binding-energy feedback. Additionally each original KM2I parent Einstein/P8 IVP was reintegrated as a HYREC external-xe control. 4 new coupled IVPs, 2 genuinely solved source-locked reference IVPs, 41 epochs per new run = 164 new physical rows, 6 PNG science figures.

In signature (-,+,+,+), use the original BASS time `u=t/Tstar`, `Tstar=218601.80677272403 Julian years`, `kappa=.003`, `YHe=.245`. A **correction versus KM2I** is necessary: for the baryon-rest Peebles reaction, `x_e'=Tstar*r_rest/gamma_b`, not `Tstar*r_rest`. Live opacity `nu=nH*x_e*sigma_T*c*Tstar`. The baryon chemical rest energy relative to initial state is `M(x)=M0(1+eta*(x-x0))`, with `eta=(1-YHe)*13.6 eV/[(m_e+m_p)c^2]`. The emitted rest-frame grey photon force is `s=-M0 eta zeta*x_e'`, `F_chem^mu=s*(gamma_b,p_b)`. The finite-angle unpolarized photon source matches all four moments of the force to floating precision using the unchanged ray grid, preserving the original P8 collision and geometry. This is **one exact modelled exchange of binding energy**, NOT a physical frequency-resolved Lyalpha ionizing radiation transfer solution, thermally closed fluid, or observed anisotropic CMB prediction.

Measured CI at science reference HEAD `0116936946f3824b3245a94355ff0cf1165f4e84`, [GitHub run 41167668963](https://github.com/cosmosapjw-quantum/bass/actions/runs/41167668963), Py3.13.5/NumPy2.3.5/SciPy1.17.0:

| Measured endpoint at u=.25 | GL12 full | GL16 full |
|---|---:|---:|
| Dynamical x_e | 0.04448760643406392 | 0.04448760642948701 |
| Live Thomson mean ray optical depth | 7.340699428940876 | 7.3408213977019745 |
| Old imported HYREC x_e | 0.13447710355226683 | 0.13447710352757392 |
| Original HYREC/P8 ray mean depth | 12.8300729337591 | 12.830194824112114 |
| Full minus opacity-only P8 photon rho (dimensionless BASS) | +2.4494201156244344e-7 | +2.4494147154996426e-7 |
| Full minus imported-HYREC original Einstein shear matrix Frobenius norm | 1.540443729051248e-4 | 1.54044300220355e-4 |
| Maximum normalized Hamiltonian constraint | 2.674305414550223e-9 | 5.041761990800316e-12 |
| Maximum normalized momentum constraint | 6.708298303605021e-9 | 1.3613741516742149e-11 |

For GL16, full-minus-opacity-only P8 radiation `Delta rho_gamma/rho_gamma_final=8.519040661837407e-9`, binding energy release `3.7752765217109765 eV/H`. Note these are distinct from the much larger **change from externally prescribed HYREC opacity**. The chemical energy effect has small photon impact and negligible change `x_e(full)-x_e(opacity_only)=5.003011893656151e-13`. That does not mean chemistry-to-Thomson coupling is small. Full-minus-original-HYREC scalar photon rho is `0.0046749887441777105` and final chemical opacity optical depth is lower than original by `5.48937342641014`. New proper-time rate gives GL16 `x_e=0.044487606429` rather than the earlier one-way pilot `0.044478973262`; no same-equation equivalence claimed.

## Actual verification and preserved evidence

GitHub CI at reference HEAD `0116936946...` real full IVPs, 13/13 regular pytest PASS, all source Git blob locks 12, numerical Hamiltonian and momentum constraint propagation, positive x, angular GL12/16 response, 164 rows and six plots. Previous `python -O -m pytest` printed `13 passed` **with warning that asserts were ignored**. This is **not** admitted as independent optimized validation. A second verification pass uses a separate `hostile_saved_audit.py` that does **not import the BASS RHS**, calculates the original atomic Peebles rate and proper clock again from saved data, rechecks binding mass, dimensional opacity, grey energy source, the chemical four-force Minkowski norm and source snapshots using explicit exceptions; it can be run under `python -O`. Its separate CI outcome must be read before `SCOPED_COMPLETED` is declared.

At reference run 41167668963, successful, source-inclusive S0/S1/S2 archival outputs had exact inner ZIP CRC and member SHA readback, verified from locally downloaded actual S2 GitHub artifact, 30/30 files. S0 SHA256 `05adb81eb88b77c32c680ff7e90250a808523030fd165b6e19481263a6f6d506` (249779 B); S1 SHA256 `29629ac63488523e8a2bb159d08113c8b27c4d0e21efd3858d272430b7f4c37c` (674260 B); S2 inner SHA256 `82db40b0a6c95960a4b631d4ec33c1c699e993cb49356cf72ff9bb897c22ecd4` (676229 B). These hashes are evidence of **the reference CI**, not prediction for later amended source or new ZIP. Artifact IDs: S0 13029686810; S1 13029721730; S2 13029876436, read-only GitHub Actions retained 60 days. The new final HEAD will produce different archive digests and must be checked on actual CI before any final claim.

## Scientific limitations and stop

This is source-conditional conservation of *modelled* chemical binding/grey radiation four-momentum, not atomically correct Lyalpha photon spectrum, physical ionizing photon closure, evolved baryon/electron temperatures, finite baryon slip or radiation entropy balance. The synthetic background has `nH_BASS/nH_CLASS~5.74`. No independent-author review or native subagent: both `NOT_RUN`.

**DAG:** upper 9/15, 21 edges, KM2 PARTIAL, new upper nodes 0. KM2J scoped physical unit may be 1/1 after final reproducible CI; no upper node promotion, no automatic KM2K, production false, merge false, auto-next false. STOP_AFTER_ONE_BOUNDED_UNIT.
