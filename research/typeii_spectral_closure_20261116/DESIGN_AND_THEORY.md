# Electron-frame spectral photoionization and Compton energy closure

Immutable parent: PR334, 7ad4e4b1cf841e0a974715bcece739ec06b38014. Original BASS/atomic source and parent data remain unchanged. Four local deliverable checkpoints T1..T4; upper DAG9/15 scoped/source-mapped unchanged, zero new full-production nodes.

## Selected objective and actual output
T1: bind microscopic sources and derive the photon-spectrum/collision moment contract.
T2: implement and test H I, He I, He II ground-state spectral rate/heating kernels and the nonrelativistic anisotropic Compton energy moment including stimulated scattering. Compare directional integration with collapsed scalar-temperature approximations. Store data on the actual parent TypeII trajectory.
T3: conditionally connect the independently verified Compton energy moment to the parent FULL thermal paths, preserving reaction clock, H and atom photoionization inputs; compare zero adapter and matched scalar controls, and test two atomic steps. Ground-state photoionization diagnostics MUST NOT replace effective n=2 HYREC rates.
T4: one same-author hostile review, actual native/input/numerical tests, per-stage dual backups, final readback and handoff. Native subagent NOT_RUN; distinct-author blind referee NOT_RUN.

## Definition and photon frame
Signature(-,+,+,+). Normal radiation is a prescribed isotropic unpolarized Planck distribution with rest temperature T_n, not a self-consistently propagated Bianchi radiation solution. beta=v/c, gamma=(1-beta^2)^(-1/2); electron-frame photon energy E[J] and direction mu_e give
n(E,mu_e)=[exp(E gamma(1+beta mu_e)/(k_B T_n))-1]^-1.
Use h=2pi hbar explicitly in density of states: N_E,Omega=2 E^2 n/(h^3 c^3). The parent proper reaction clock remains d/dtau_H=(gamma H_n)^-1 d/ds_e. Ions used for photoionization are assumed to share the bulk electron frame, with thermal broadening neglected.

Ground-state ionization rate per atom R_ph=8pi/(h^3 c^2) integral_chi^infty E^2 sigma(E) nbar(E)dE. Photoheating per atom replaces the integrand by (E-chi) times itself. Coefficients use the exact author's Verner table; units: input photon energies in eV, fit sigma0 in Mb=10^-22 m^2, convert only at the kernel boundary. The supplied H/He fits extend to 50keV; numerical integrals remain inside this domain, with exponentially suppressed tails separately controlled. These are rates, not a complete recombination calculation.

## Compton energy moment to implement and independently test
In the local electron bulk rest frame take an isotropic nonrelativistic Maxwell electron distribution. Retain leading k_B T_m/(m_e c^2) and E/(m_e c^2), unpolarized Thomson angular kernel; omit relativistic cross-orders, pairs and polarization evolution. The exact kinematic bulk boost is not expanded in the numerical spectrum.

Let b_l(E)=(1/2)integral_-1^1 n(E,mu) P_l(mu)dmu. The normalized recoil angular kernel is W(q)=3(1+q^2)(1-q)/(16pi). Its Legendre form gives the stimulated scalar S(E)=b0^2-(6/5)b1^2+(1/2)b2^2-(3/10)b3^2. This is generally neither nbar^2 nor <n^2>. Direct pair-angle quadrature must independently reproduce S, including its nonnegativity.

Define U=8pi/(h^3 c^3) integral E^3 b0 dE and M=8pi/(h^3 c^3) integral E^4[b0+S]dE. Electron heating per proper electron per second is Q_e= sigma_T c/(m_e c^2)[M-4 k_B T_m U]=4 sigma_T c k_B U/(m_e c^2)(T_C-T_m), T_C=M/(4k_B U). At beta=0, retaining stimulation must give T_C=T_n exactly; omitting it gives zeta(5)/zeta(4)*T_n, a deliberate negative control. This is the integrated energy moment, not a complete angular Compton transfer operator. Q_gamma=-n_e Q_e by collision bookkeeping.

For an axisymmetric boosted Planck field, a small-beta independent expansion predicts T_C/T_n=1+[2pi^2/9-7/6] beta^2+O(beta^4). Verify by numerical integration and CAS. Energy-density boost is gamma^2(1+beta^2/3); matching only U by T_eff=T_n[U/U_n]^1/4 cannot establish the correct Compton moment or threshold rates.

## Boundaries and acceptance
Zero-boost Planck equilibrium; positive cross sections above threshold and zero below; rejection outside fit/physical parameter domains; photon number/energy moments; direct versus analytic angular monopole; direct pair-angle versus Legendre stimulation; quadrature refinement; small-beta coefficient; independent author's Fortran source cross section comparison where toolchain permits. Keep absolute rates next to large relative Wien-tail changes. Avoid treating ground-state rates as effective excited-state ionization or silently applying a scalar blackbody to anisotropic atom tables. Native thermal-only coupling is a declared intervention, not full atom/spectrum self-consistency. No new full-production or merger approval.
