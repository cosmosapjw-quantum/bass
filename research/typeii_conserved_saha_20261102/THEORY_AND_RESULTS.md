# Type-II | conserved hydrogen current + source Saha thermal-history transport

Source parent: BASS Draft PR #327 head `97359596c3d640d5ad306e2285b248a5105cf40e`. Immutable original main `9c6506e4e2087129a8b674ff10438e5db1a55c9d`.

## R1 / C1: Physical science target and acceptance
Produce **actual 401-state BASS Type-II physical model data**, beyond the former unit-opacity/proxy. Reuse the original 5-state gamma-law background, source-owned high-redshift *hydrogen-only Saha equilibrium* and physical constants. Impose conserved homogeneous tilted hydrogen nucleus number current in Class A and an explicit physical Hubble normalization at reference mean-redshift 1700. Then integrate `n_e^{rest}(tau_H) sigma_T c Gamma(1-vn_y)/H` along **all 26 already calculated normal-frame photon directions**. Numerically compare the old exact axial pair and independent direct density-current formula. Record difference from naively interpreting the historical FLRW `x_e n_H` as electron-rest density.

Scientific conditions and limitations:
- Signature (-,+,+,+), c and physical k_B retained; `tau_H=∫Hdt`. Type II class A, `A_a=0`, normal H positive. Tilted hydrogen fluid baryon number current `J_H^μ=n_H^{rest}Γ(u^μ+v e_y^μ)` **conserved**. Electron 4-velocity equals tilted hydrogen 4-velocity **as an explicit model assumption**.
- `z_mean(tau_H)=(1+1700) exp(-tau_H)-1` is a **mean-scale-factor thermal label**, not directional observed redshift. Impose electron/matter temperature `T_m(tau_H)=T_CMB,0*(1+z_mean)`; this isotropic thermal reservoir is not derived from anisotropic photon evolution.
- FLRW-based physical `n_H^{rest}(0)` and `H(0)` serve **anchor calibrations only**; subsequent hydrogen current and `H'(tau_H)=-(1+q_{⁠II})H` evolve on actual source Type II 5-state. Thus this is *source-conditioned Type II + equilibrium matter model*, not a fully self-consistent baryon+photon+Einstein solution.
- Saha hydrogen equilibrium is applied only where mean z ≳ 1300, excluding accurate late recombination. Helium, non-LTE Peebles/HyRec, Thomson redistribution, polarization and backreaction excluded. No read of an unverified HyRec dataset will be claimed.
- The prior BASS 3-anchor opacity proxy is **not** a thermodynamic source for this run.
- No original source, parent, main, production dispatcher, or live production job mutation.

Acceptance: exact Git blobs 9/9 + original recombination/history constants locked, analytical J-conservation and Gamma cancellation; scalar x_e bounded and equal to original source Saha function for proper density via source AST import without JAX; independent stable Saha root; 401 actual electron density, temperature and H rows; full 401x26 optical-depth numerical data; independent integrator convergence, original 2 axial rays checked; same-author hostile controls; explicit completion vs HOLD. Stage progress and backup must show `BASS_UPPER=9/15 scoped/source-mapped`, `new full upper=0` unless proof of a canonical node is discovered. No merge or production activation.
