# Spectral moment derivation, units and claim boundary

Conventions and the original source references are in DESIGN_AND_THEORY.md. All angular averages use dOmega/(4pi). n(E,Omega) is occupation per polarization. Cgamma=8pi/(h^3 c^3) includes the two polarization states after angular integration. h=2pi hbar, all dimensional formulas are SI. The matter/electron rest frame in this unit is the mean bulk frame; electron thermal velocities are nonrelativistic and isotropically distributed.

## Photoionization rate and the independent frame expression
The density of photons per energy per solid angle is 2E^2 n/(h^3 c^3). Multiplication by c sigma(E), then integration over directions gives
R=8pi/(h^3 c^2) integral E^2 sigma(E)n0(E)dE.
The units are s^-1 per target. Multiplying the integrand by E-Eth gives deposited photoelectron kinetic power per target in W. Atomic recoil, thermal broadening, inverse radiative capture and populations are not included in this one-direction process. A population equation would use the separately retained proper reaction-clock conversion R/(Gamma H_n); we do not insert this ground-state R into HYREC's multilevel effective rates.

For a normal-frame photon direction mu_n and D=Gamma(1-beta mu_n), E_e=D E_n, n is invariant, and dOmega_e=dOmega_n/D^2. Changing energy variables yields R=<R_iso(T_n D)/D^2>_n, identical to the direct electron-frame average <R_iso[T_n/(Gamma(1+beta mu_e))]>_e. No second relative-flux correction is needed in the already electron-rest rate. The two integral formulations are implemented independently.

## Compton energy moment
The normalized Thomson angular scattering factor is (3/4)(1+c^2) in dOmega'/(4pi). At leading recoil order, the photon loses E^2(1-c)/(m_e c^2). Including the final-state stimulated occupation gives the recoil angular kernel W(c)=(3/4)(1-c)(1+c^2). Its unit angular integral supplies the spontaneous term, while its symmetric convolution supplies the induced bilinear <n S[n]>.

For an axisymmetric unpolarized distribution define n_l=(1/2) integral n(mu)P_l(mu)dmu. The addition theorem gives <n S[n]>=sum_l w_l n_l^2 with w_l={1,-6/5,1/2,-3/10}. The kernel is a cubic polynomial, so higher occupation multipoles do not contribute to this particular bilinear; this is not an assumption that the radiation field itself has no higher multipoles. The literal double angular integrand W n n' is nonnegative. A separate azimuth quadrature and independent pair-angle computation verify the reduced expression.

At leading nonrelativistic thermal order, after angular integration for isotropic thermal electrons, the electron cooling contribution is -4sigma_T c k_B T_m u_e/(m_e c^2). Combining it with recoil yields
P_e = sigma_T c Cgamma/(m_e c^2) [integral E^4(n0+<nSn>)dE -4k_B T_m integral E^3 n0 dE].
Equivalently P_e=4sigma_T c k_B u_e(T_C-T_m)/(m_e c^2), with k_B T_C=(integral E^4[n0+<nSn>]dE)/(4 integral E^3 n0 dE). P_e is proper thermal energy gain per electron per second, not bulk drag work. A prescribed radiation flux also exerts a force and will alter bulk momentum in a fully coupled model; that momentum feedback is not solved here.

The angularly averaged frequency flux at this order can be written F=x^4[theta*n0'+epsilon*(n0+B)], with theta=k_B T_m/(m_e c^2), epsilon=k_B T_n/(m_e c^2), and dimensionless x=E/(k_B T_n). The monopole collision term is F'/x^2. Thus photon-number change is the endpoint flux, zero for the distributions in this unit; the energy moment is -integral F dx. The direct differentiated flux tests check number conservation and equality to 4theta U3-epsilon J4, including signs. These are moment checks, not implementation of a full angular/polarized evolution operator.

## Detailed balance and the small-beta coefficient
At beta=0 with Planck or isotropic Bose-Einstein n=1/[exp(x+eta)-1], eta>=0, n'=-n(1+n). The boundary term x^4 n vanishes, hence J4=integral x^4(n+n^2)dx=4 integral x^3 n dx=4U3. Therefore T_C=T_n. Dropping n^2 gives zeta(5)/zeta(4) for the Planck case, which is not one; its false cooling at T_m=T_n is an explicit adversarial control.

For the boosted Planck field, expand at fixed x:
n0=n+beta^2[x n'/2+x^2 n''/6]+O(beta^4),
n1=beta x n'/3+O(beta^3).
Then U3=U0[1+(4/3)beta^2]+O(beta^4), U0=6zeta(4). With g=n+n^2,
n0+B=g+beta^2[x g'/2+x^2 g''/6-(7/15)x^2(n')^2]+O(beta^4).
Twice integrating by parts gives
J4=4U0+beta^2[10U0-(7/15)I6]+O(beta^4),
I6=integral x^6(n')^2 dx=120[zeta(4)-zeta(6)].
Consequently
T_C/T_n=1+[2pi^2/9-7/6]beta^2+O(beta^4).
The coefficient1.02657875579763525 is a derived low-beta coefficient, not a numerical fit and not the full finite-beta expression used by the code. The actual finite-beta integrals and three small-beta values independently check it. By contrast, the energy-matched blackbody temperature has coefficient1/3, so one energy-equivalent blackbody cannot reproduce this collision moment.

## Accuracy and physical scope
The exact statements are the local Lorentz transformation, measure transformation and algebraic angular reduction. The cross section is the original Verner ground-state fit, not an exact many-electron cross section. Compton is a leading recoil/thermal expansion; terms quadratic in E/(m_ec^2), k_BT_m/(m_ec^2) and their products are neglected. The source radiation temperatures give k_BT_n/(m_ec^2)<8e-7; photon energies dominating the Compton moments are several times k_BT_n. The code supports numerical boost quadratures only for |beta|<=0.2, not a universal relativistic-temperature solver.

The passive thermal experiment inherits a fixed-composition heat-capacity convention with prescribed parent xe(t). Changing xe modifies the coupling coefficient but dxe/dtau_H and chemical energy terms are not included. Its initial temperature is the same parent value at mean z1700 in every lane. The largest stored-grid difference near this boundary is not asserted insensitive to alternative smooth prehistories. It does not produce a new ionization or optical-depth history.

The next physical construction is level-resolved forward/reverse bound-free detailed balance, with stimulated recombination and reacting-gas energy accounting, before inserting a spectral photoionization modification into the native multilevel atom. No further optional review tree is needed to establish this bounded moment result.
