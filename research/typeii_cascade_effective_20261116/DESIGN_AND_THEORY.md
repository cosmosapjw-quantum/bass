# TypeII bound-bound cascade and conservative effective-rate bridge

Frozen parent PR337 d29a08cb6e368339015dadb2b791044ba6af9848. Four local phases K1-K4. Upper DAG9/15 scoped/source-mapped unchanged; no new fully complete production node. Same-author serial construction/review; native_subagent NOT_RUN, distinct-author review NOT_RUN.

## Bounded model and purpose
Six hydrogen levels 1s,2s,2p,3s,3p,3d plus continuum. Use unchanged parent finite-band nl-resolved Milne kernels. Add the five nonrelativistic electric-dipole lines and the nonresonant 2s<->1s two-photon channel. No 3s/3d resonant two-photon terms are added on top of E1 cascades. Unaligned magnetic sublevels, unpolarized prescribed photon bath, infinite-mass binding convention, isotropic Maxwellian relative electrons. The bath is normal-frame Planck (optionally BE for diagnostic chemical cycles), Lorentz transformed into the common atomic/electron mean frame; no thermal line broadening, magnetic alignment, recoil, line trapping or solved radiation field. Rates are proper per second, SI. Signature(-,+,+,+), h=2pi hbar; c,kB are retained.

E1 amplitudes are constructed from exact nonrelativistic Coulomb radial integrals and angular-momentum factors, checked independently by quadrature and against NIST line scales with finite-mass/fine-structure qualifications. Transition energy is the difference of parent source binding energies so all cycles close exactly. This is not a precision hydrogen isotope calculation.

The existing original HYREC two-photon quadrature is reused byte-exact: hydrogen.c normalizes the sub-Ly-alpha A2s bins to L2s1s=8.2206 s^-1; only the larger-photon half-spectrum is stored, so do NOT multiply its sum by two. Standard and hires tables provide a resolution comparison. The dimensionless photon energy sharing is mapped to the parent 2s-1s energy gap; the source amplitude is retained. Thus source normalization and energy-convention adaptation are separate recorded choices.

## Construction and acceptance
K1: source/contract and failing tests, durable checkpoint.
K2: E1/2gamma forward/reverse kernels and finite network; independent radial/angular checks and exact Planck detailed balance.
K3: Schur elimination of n=3, source-state effective rates, reconstructed stationary populations, photon/kinetic/ionization-energy readouts; exact dynamic memory comparison.
K4: one hostile pass, actual replay, source identity and dual archive verification, final report and handoff.

No native HYREC effective coefficients are overwritten. No new cosmological xe or optical-depth prediction is admitted. Fixed-ne trace populations are allowed only as explicitly named linear-response/kinetic validation, not a closed cosmological electron solution.

## Mathematical distinction: stationary versus dynamic elimination
For a column generator Q, dp/ds=Qp, 1^T Q=0, partition retained R=(1s,2s,2p,ion), fast F=(3s,3p,3d). If Q_FF is transient, N=(-Q_FF)^-1 >=0. Reconstruct L=N Q_FR and Schur Q_eff=Q_RR+Q_RF L. Off-diagonals remain nonnegative and column sums vanish. P=Q_RF N gives exit probabilities with columns summing to one.

For full equilibrium p*, p_F*=L p_R*. A unit-normalized Q_eff stationary vector is CONDITIONAL on retained states. Reconstruct and normalize [p_R,Lp_R] by its total. Do not erase eliminated populations when computing total nuclei or atomic energy.

For time evolution, exact elimination contains exp(Q_FF s)p_F(0) and the memory integral exp(Q_FF(s-u))Q_FR p_R(u). Its Laplace response is Q_RR+Q_RF(zI-Q_FF)^-1 Q_FR, with the corresponding initial-population term. Q_eff is the z=0 limit, not exact chronological dynamics. The first-order storage matrix C=I+Q_RF Q_FF^-2 Q_FR obeys 1_R^T C=1_R^T+1_F^T L; no general positivity claim is made for C^-1 Q_eff.

Use microscopic channel readouts after reconstruction to compute photon energy, electron kinetic energy and bound atomic energy. A bare effective endpoint rate does not encode cascade photon multiplicity/spectrum. At stationary elimination the fast atomic energy derivative is zero, so the reduced energy ledger is checked against the explicit microscopic lift.

Acceptance: thermal rate ratios and Schur equilibrium at <=1e-10 relative on nonzero channels; source radial quadrature <=1e-11 relative; exact block-resolvent comparison <=1e-10 relative; all-stage source identity; independent output validation. Table resolution and physical closure uncertainty are measured separately and not hidden by relaxing those identities.

Sources: Ali-Haimoud & Hirata PRD82 063521 (2010), arXiv:1006.1355; original HYREC hydrogen.c/hydrogen.h/two_photon_tables*.dat; NIST hydrogen persistent lines; Fratini et al arXiv:1203.6601 for leading E1E1 angular correlation; Chluba & Sunyaev arXiv:0705.3033 for avoiding resonant cascade double counting.
