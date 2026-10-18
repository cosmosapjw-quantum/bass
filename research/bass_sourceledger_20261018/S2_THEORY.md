# S2 finite interval: per-H source stock and BASS proper-volume energy

Signature (-,+,+,+); non-tilted LRS metric ds^2=-c^2dt^2+a^2[e^-2b(dx^2+dy^2)+e^4b dz^2]. Preserve signed s=dot b and positive Sigma=sqrt(3)|s|/H. Native SourceLedger is photons/H-nucleus and eV/H-nucleus, not density. The empirical-scenario source, escape fraction, BB50K shape and its 13.6--100 eV cutoff are inherited exactly from the pinned owner, not observationally recalibrated.

Let r(x) be photons per total-H nucleus per proper second, h_i(x)=e^-x R_i[b(x)] the physical/reference energy ratio and J_i=R_i^-3. At birth u, native discrete weights are W_i(u)=w_i J_i(u)/sum_j(w_j J_j(u)). Those weights preserve source N but not exact continuum isotropy at finite angular resolution.

Given source-panel fractions f_s, GL8 norms N_s, and the intersection [L,U] between the physical source panel and reference bin mapped by h_i(u), injection gives
N_ik += r(u)dt W_i f_s int_L^U phi(E)dE / N_s,
Uref_ik += r(u)dt W_i f_s int_L^U E phi(E)dE / [N_s h_i(u)].
Both are positive; no expansion factor is applied to per-H number. At observation x, U/H=sum Uref_ik h_i(x), Delta/H=sum Uref_ik h_i(x)P2(mu_i(x)). With fixed stock,
(U/H)'=-(U/H)-2b'(Delta/H).
With n_H=n_H0/a^3, rho=n_H(U/H) instead obeys rho'=-4rho-2b'Delta+S, S=n_H r Emean/H. The minus-one versus minus-four is not a convention choice; a second a^-3 on stored native photon number is an error.

An independent continuum reference integrates locally isotropic birth directions rather than fixed reference rays:
N/H = int r(u)/H(u) du;
U(x)/H = int r(u) Emean/H(u) exp[u-x] F[b(x)-b(u)]du;
Delta(x)/H = int r(u) Emean/H(u) exp[u-x] D[b(x)-b(u)]du.
The exact massless F,D satisfy F'=-2D. S0 stock is zero in these tests. Multiplying by n_H(x) recovers the BASS exp[-4(x-u)] kernel, since exp[-3x]exp[u-x]=exp[-3u]exp[-4(x-u)].

Midpoint source sampling uses dt=int du/H, not delta_x/H at an unrelated epoch. Smooth finite-time quadrature error and native fixed angular/spectral errors are independent axes. A fine-time discrete-oracle comparison tests native implementation parity; birth-frame continuum comparison tests quadrature accuracy. Neither is native reactive chemistry.

Three identities (ray per-H energy evolution, volume conversion and source density factors) returned exact zero from Wolfram on 2026-10-18. Symbolic placeholder warnings were present; no xAct execution is claimed. The native runner will call the actual CovariantTransport::inject and inventory, not a rewritten surrogate. Rust compilation has not run in this sandbox.

Primary context: Fleury, Pitrou & Uzan, Phys.Rev.D91 043511 (2015), arXiv:1410.8473v3, conserved k_i and photon redshift. New discrete contracts above are derived from pinned original source files and direct calculation, not attributed as novel results of that paper.
