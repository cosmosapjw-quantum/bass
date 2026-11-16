# Lyman line kinematics, source exchange and scope

## 1. Local clocks and frequency flow (derived)
Signature (-,+,+,+), h=2pi*hbar, c and kB explicit. Source normal proper time t_n obeys d tau_H=H_n dt_n; the tilted atoms have dimensionless beta=v/c along the original e_y tetrad direction. For a source photon with unit normal-frame direction n, D=Gamma(1-beta*n_y), E_a=D E_n. The original source Liouville characteristic has (log E_n)'=-(1+Sigma_nn). Therefore

kappa=-(log E_a)'=1+Sigma_nn-beta*beta'/(1-beta²)+(beta'*n_y+beta*n_y')/(1-beta*n_y).

The photon traverses local atomic-tetrad time dt_a^ray=D dt_n, hence H_ray=-dlog(E_a)/dt_a^ray=H_n*kappa/D. This local path increment is not a globally integrable new cosmological time coordinate. In contrast, an atom worldline has ds_a=dt_n/Gamma. Their distinction is fixed by Lorentz kinematics, not by a scalar replacement of H. In the zero-tilt isotropic limit both kappa and D reduce to1. With zero tilt but shear, kappa=1+Sigma_nn remains directional. N1 affects n_y' through the original TypeII spatial connection.

Original source n_y'=(Sigma_nn-Sigma_yy)n_y-N1*n_x*n_z. Since |n_x n_z|<=1/2 and |Sigma_nn-Sigma_yy|<=lambda_max-lambda_min, a sufficient bound for every direction at a given state is

kappa >= 1+lambda_min-|L|-[|beta'|+|beta|(lambda_max-lambda_min+|N1|/2)]/(1-|beta|), L=(log Gamma)'.

This is an analytic bound in direction, evaluated at358 actual source times. It is not an interval proof in continuous time. The source minimum bound0.3906939961 is positive. Independent five-point differences of log[D E_n] agree with the analytic formula to3.0629e-11 on19 interior source times, and original stored geometry/ray trajectories are separately matched.

## 2. Finite thermal line collision (defined closure; checked consequences)
For unaligned 1s/2p levels, g=g_u/g_l=3. The original Coulomb-source A=626831502.957694 s^-1 and E0=10.204269842245498 eV are preserved. Translational width uses a declared hydrogen atomic mass1.6735575e-27 kg; this is not a precision isotope calculation.

Let p_j>=0 denote actual emitted Voigt probability in a finite frequency bin, not renormalized to the selected band. Mode capacity per proper local volume is
G_j=8pi/(3c³)*(nu_+³-nu_-³), in m^-3.
For photon occupation f_j, choose the thermal finite-bin interface
F_j=A p_j [ n_u(1+f_j)-g n_l exp((h nu_j-E0)/(kB Tm)) f_j ].
F has units m^-3 s^-1, the atomic source is dn_u/ds=-sum F and dn_l/ds=+sum F. The Planck/Saha-Boltzmann relations at one common temperature make EACH bin vanish; using identical broad emission and absorption factors does not. This thermal completion is a specified finite-bin model, not a derived complete redistribution matrix with recoil and quantum line profiles.

Photon number source is F_j. Energy readouts are Q_gamma=sum h nu_j F_j, Q_bound=-E0 sum F_j, Q_kin=sum(E0-h nu_j)F_j, so their sum is exactly zero algebraically. A prescribed thermal reservoir absorbs this kinetic exchange in the test; the gas energy equation and composition-dependent heat capacity are not evolved.

The parent's imposed-bath Lya source is removed once before this finite-band source is inserted. All other parent microscopic channels are untouched. Because the line is deliberately truncated, out-of-band Lya exchange is NOT restored by a hidden renormalization; it is outside the interface test and requires an explicit surrounding radiation domain in a future global solve. Thus exact energy bookkeeping does not mean complete line physics.

## 3. Conservative frozen-band transport (local narrow-line approximation)
Use photon-bin numbers N_j=G_j f_j in a local frozen rest volume. With monotonic red drift a_j>0 and absorption k_j>=0, the upwind operator is
Ndot_j=J_(j+1)-J_j+j_j-k_j N_j, J_j=a_j N_j.
There is a specified blue boundary inflow and a measured red boundary outflow. A bidiagonal M-matrix gives a nonnegative stationary solution. Summing the equations proves number exchange + blue inflow - red outflow=0. Multiplying by photon energies exposes resolved redshift work, including edge energy differences; the stationary photon/atom/kinetic/work/boundary ledger then closes.

This photon-number model is a leading narrow-line frozen-volume local diagnostic. It omits global Bianchi volume dilution, angular measure focusing, evolving frequency/angle characteristics over cosmological times, full scattering redistribution and polarization. It is NOT the full covariant occupation equation. The independently checked directional H_ray is exact for the inherited source; its insertion in this simplified frozen model does not promote the latter to full GR transport.

Our26 source characteristics are NOT an angular quadrature. Each directional solution is reported using a4pi-equivalent photon capacity, and the26 fluxes are never summed to obtain an all-sky luminosity.

## 4. Escape and spectral support
For one monotonic pass with frozen equal absorption/emission profiles and positive opacity, use cumulative red optical depth. Exact integration yields P=(1-exp(-tau))/tau and tau=A lambda0³(g n_l-n_u)/(8pi H_ray). This is a reference/control, not automatic cosmological escape. A finite band with mass M gives an unnormalized emitted fraction M*(1-exp(-tau*M))/(tau*M), before any additional outside opacity is considered.

In the actual density SCENARIO, parent fixed-ne stationary tracer fractions are multiplied by a conserved proper hydrogen density scale. Charge/electron feedback and cosmic populations are not solved. A symmetric Voigt extrapolation beyond20 Doppler widths at source zmean1100 has formal residual depth8120..20484, though the finite mass is0.99997255. The corresponding Lorentz-wing tau=1 estimate lies at fractional frequency scales3.81..9.60, invalidating that narrow-line extrapolation itself. This does not predict actual far-wing opacity, especially once thermal profile asymmetry, scattering and time dependence are included.

A separate finite n<=3 cascade calculation tracks an initial2p excitation through3s/3d excursions until Ly-alpha re-emission or ionization. Its matrix exit probabilities obey P=Q_AU(-Q_UU)^-1; the independent star result has beta_eff=beta_p+R_ps*beta_s/(A_sp+beta_s)+R_pd*beta_d/(A_dp+beta_d), p_ion=beta_eff/(A_p1+beta_eff). Actual source z1100 gives p_ion=7.2479782e-8 and proper residence1.5974835e-9 s. It excludes later recombination/feedback and high-n channels. Multiplying tau by p_ion illustrates the distinction between resonance and destruction; it is NOT an escape solution.

## 5. Literature boundary
Hirata & Forbes, arXiv:0903.4925; Chluba & Sunyaev, arXiv:0810.1045 and0904.0460; Ali-Haimoud & Hirata, arXiv:1011.3758. These support the need to separate quasistationarity, line profile thermodynamics, redistribution and destruction. The present computation is a new source-conditioned interface with explicit omissions, not a reproduction of their full recombination accuracy. Primary URLs are https://arxiv.org/abs/0903.4925 , https://arxiv.org/abs/0810.1045 , https://arxiv.org/abs/0904.0460 , https://arxiv.org/abs/1011.3758 .
