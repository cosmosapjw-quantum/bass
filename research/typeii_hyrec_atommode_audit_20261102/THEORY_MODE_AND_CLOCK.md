# Effective atomic modes and the remaining tilted-clock closure

## Conventions and study domain
Metric signature (-,+,+,+). Normal proper time t is in seconds, H_n=(1/3)theta_n in s^-1, d tau_H=H_n dt. Source BASS velocities v_i are dimensionless fractions of c and Gamma=(1-v_i v^i)^(-1/2). The declared mean-scale-factor label obeys 1+z_mean=1701 exp(-tau_H); it is not observed directional redshift. The numerical comparison covers 300<=z_mean<=1700, with the common original HYREC early history above 1700. The gamma-law background has gamma_fluid=1.3. All microscopic HYREC rates retain original cgs/eV units, with T[eV]=k_B T[K], k_B=8.617343e-5 eV/K.

## 1. Four-level elimination: derived algebra, tied to original functions
Let R=R_(2p->2s), and let L_s,L_p be effective downward ground-state rates. Detailed balance gives the reverse mixing rate 3R. Write B_s,B_p for photoionization rates, A=B_s+3R+L_s, B=B_p+R+L_p. The quasi-steady excited-state equations, after subtraction of any chosen equilibrium reference, are

A x_s - R x_p = b_s,
B x_p - 3R x_s = b_p.

Their determinant is
Delta=AB-3R^2=(B_s+L_s)(B_p+L_p)+R(B_s+L_s)+3R(B_p+L_p).
It is positive for strictly positive relevant decay/ionization channels and R>=0. Hence
x_s=(B b_s+R b_p)/Delta,
x_p=(3R b_s+A b_p)/Delta.
The resulting net ground-state source has the exact algebraic form
L_s x_s+L_p x_p=C_s b_s+C_p b_p,
C_s=(L_s B+3R L_p)/Delta,
C_p=(L_p A+R L_s)/Delta.
The numerators are nonnegative. Delta-(L_s B+3R L_p)=B_s B+3R B_p>=0, and Delta-(L_p A+R L_s)=B_p A+R B_s>=0, so 0<=C_s,C_p<=1 under these rate assumptions. Dimensions: A,B,L,R in s^-1, Delta in s^-2, and C_s,C_p dimensionless. This verifies the original effective probability factors; it does not prove the approximations used to determine L_s,L_p.

Original EMLA2s2p uses L_s=Lambda_(2s1s), L_p=8 pi H/(3 n_H x_1s lambda_Lya^3). Original SWIFT replaces L_p by L_p/(1+delta_K), where delta_K is the radiation-temperature/cosmology correction from fit_swift.dat. The rate dimensions are s^-1: H/n_H has cm^3 s^-1 and lambda^-3 has cm^-3. FULL evolves its radiation distortion history rather than assuming the SWIFT correction. FULL is therefore an algorithmic reference within the inherited isotropic radiative-transfer construction, not an exact anisotropic cosmology.

The original model dispatch also uses EMLA in low-photoionization regimes (Pion<0.01), and special stiff/Post-Saha handling. Equal local rate functions after a dispatch switch do not force equal integrated histories: initial states and earlier radiation histories differ. No final xe difference is attributed solely to the current redshift's dispatch branch.

The primary HYREC-2 paper supports precision over its tested Planck parameter region, not arbitrary prescribed H(z). Sources: Lee and Ali-Haimoud, PRD102 083517 (2020), arXiv:2007.14114v2; Ali-Haimoud and Hirata, PRD83 043513 (2011), arXiv:1011.3758v2. The code-specific statements above are also checked against the byte-locked original hydrogen.c/history.c, not inferred from model names.

## 2. Proper reaction clock: a separate physical condition, not a density correction
Assume homogeneous fields on the class-A slices, lapse one/geodesic normal congruence, and the electron velocity field used by the parent experiment. Let n^a be the normal four-velocity with n^a n_a=-c^2 and e_i^a a unit spatial tetrad. Then
U_e^a=Gamma(n^a+c v^i e_i^a).
For a homogeneous scalar X(t), e_i^a nabla_a X=0, so
U_e^a nabla_a X=Gamma dX/dt=Gamma H_n X',
where a prime means d/dtau_H. If the microscopic proper-time fraction source is R_proper=dX/ds_e, the computational evolution must be
X'=R_proper/(Gamma H_n).

The source-conserved nucleus current fixes Gamma n_H^rest=N_H0 exp(-3tau_H), hence
n_H^rest=N_H0 exp(-3tau_H)/Gamma.
This density law does NOT supply the additional proper-clock conversion. The inherited HYREC source uses its single scalar H in reaction normalization and radiation/thermal channels; simply changing n_H does not turn R/H_n into R/(Gamma H_n).

For class-A homogeneous spatial current (vanishing spatial divergence),
theta_e=nabla_a U_e^a=dGamma/dt+3Gamma H_n
       =Gamma H_n[3+(log Gamma)'].
This follows independently from nucleus continuity: -U_e^a nabla_a log(n_H^rest)=theta_e. Since (log Gamma)'=v_i v_i'/(1-v_i v^i), it reduces to theta_e=3H_n at zero tilt. Units: theta_e, H_n are s^-1.

For a fixed-composition, nonrelativistic monatomic ideal gas without heat sources, dT_m/ds_e=-(2/3)theta_e T_m. Thus
T_m'=-2[1+(log Gamma)'/3]T_m.
Changing particle abundance adds chemical/heat-capacity terms; Compton exchange additionally requires the appropriate electron-frame radiation distribution. This equation is only the adiabatic fixed-composition limit, not a proposed complete temperature equation.

A single global H->Gamma H substitution cannot consistently repair all these channels: H also enters Lyman escape/redshifting, while theta_e/3=Gamma H_n+H_n Gamma'/3 generally differs from Gamma H_n. A future adapter must distinguish normal time, proper reaction time, fluid dilution/cooling, and photon propagation. These are compatible equations to construct, not a no-go statement.

## 3. Actual symbolic and numerical checks
Wolfram Language evaluation in this research invocation returned zero for the four-level elimination identity, the log-Gamma derivative identity, and the continuity/theta_e identity; its proper-clock expression simplified to sqrt(1-v^2)/H. The executable source-background audit gives Gamma in [1.000378458950375,1.0012523486435176], max(Gamma-1)=0.0012523486435176423, and (log Gamma)' in [-0.0008443832874655984,-0.00026800129905273545] on the finite source interval. Therefore the missing proper-clock effect is not automatically below a 1e-4 precision target. It has NOT been silently patched into this same-input mode comparison.

Actual source Codazzi residual is 2.498001805406602e-16. The exact axial optical-depth identity (even/odd split), Gauss order comparison, and independent Simpson integration are recorded in MODE_COMPARISON_RESULTS.json. Original calibrated physical constants, parent source histories and fixed grids remain unchanged.

## Disposition
The algebra and clock equations are DERIVED; symbolic zero residuals are SYMBOLICALLY_CHECKED. The atomic-mode differences and opacity values are NUMERICALLY_CHECKED within the inherited closure. A covariant tilted atomic/thermal/radiation closure is NOT_IMPLEMENTED. This narrows the interpretation of PR332 without rewriting its immutable data or its historical source execution evidence.
