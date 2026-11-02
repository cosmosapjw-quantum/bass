# BASS Type-II | Native HYREC-2 FLRW H/He history mapped to exact 26 photon rays

Parent Draft PR #329 **immutable HEAD** `0bee79382753d95c610f5e86431f9e7c318c27d5`. Protected original main `9c6506e4e2087129a8b674ff10438e5db1a55c9d`.

## R1/C1: scientific target, conventions, and acceptance

Reuse actual **HyRec2020 (HYREC-2)** original C hydrogen + helium non-equilibrium recombination from locally installed CLASSIER source at `/home/cosmosapjw/src/TEFF_CLASSIER_CLEAN_BUILD_v1_3/external/HyRec2020`. Build it only inside an isolated research worktree, generate the original three-column `(z, x_e=n_e/n_H, T_m[K])` table with exact input, source digest and atomic-table identities, then couple it **conditionally** to the previously source-verified BASS tilted Type-II 401-point background and 26 normal-tetrad photon rays.

Use metric (-,+,+,+), `d tau_H=H dt_normal`, gamma-law fluid index 1.3 distinct from Lorentz Gamma. Type-II Class A hydrogen normal number current `N_H=n_H^rest Gamma=N_H(0)e^{-3tau_H}` is prescribed conserved. Hydrogen and free electron comoving velocities are **assumed** to equal `v2 e_y`; `x_e` from HyRec FLRW is a *read-only function of mean-scale-factor label* `zmean=(1701)e^{-tau_H}-1`. H subsequent to tau=0 evolves from original Type-II q source, not the FLRW H of native HyRec. H(0) remains the explicit previous fiducial FLRW anchor `h=.674, Omega_m h^2=.143`. Because this is not a self-consistent anisotropic recombination calculation, the result is a **provenance-locked HYREC-2 reweighted Bianchi Type-II transfer scenario**, not an actual Type-II HyRec solve.

HYREC-2 original `n_H0=11.223846333047e-6 (Omega_b h²)(1-Y_He) cm^-3` (HYREC-2 `history.c`). Use that normalization rather than accidentally carrying over previous Saha source hydrogen-only coefficient. Input `h=.674`, `Omega_b h²=.0224`, `Omega_cb h²=.143`, `Y_He=.245`, `N_eff=3.046`, one massive neutrino m=0.06 eV (copied source setting), T0=2.7255 K. Distinguish `Omega_cb` from total matter (massive neutrinos are separate).

Physical question: how do source-native H/He non-equilibrium rates modify actual 401x26 Type-II Thomson depths, `+/-e_y` odd/even optical-depth structure, early first-scattering statistics, and comparison to source-Saha while protecting the parent? Use `n_e^rest=x_e(zmean) N_H(0)e^{-3tau_H}/Gamma`; full per-ray `dT/dtau_H=[sigma_T c/H]x_e(zmean)N_H(0)e^{-3tau_H}(1-v2 n_y)`. Exactly ONE q flux, no extra Gamma after current cancellation.

Success: native C standalone build + run, separate exact source input and atomic rate tables, snapshot SHA-256; source sample output reproduction test if feasible; table xe/temperature finite physical; source-conditional 401x26 numeric data; interpolant/quadrature convergence, axial exact identity, source electron frame SI/CGS parity, bounded hostile reviewer and reproducible code; no production dispatch change, no automatic merge.

**Initial BASS upper DAG**: 9/15 scoped/source-mapped, new full upper nodes 0. Historical StageII 11/11 current canonical NOT_RECOVERED; P-MIG-II-PREFLIGHT PARTIAL, G-DYN-MANIFOLD_VI0 PARTIAL, Join J1 0/2 FULL PASS HOLD, production_ready=false.
