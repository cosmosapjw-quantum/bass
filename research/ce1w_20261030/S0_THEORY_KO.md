# CE1-W S0 | Frozen six-cell kinetic angular-geometry response

Parent PR #267 HEAD `45efec543faa2997c5918f320b41c6b4cd9bddb1`; original binary64 six-cell SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. Positive, reflection-even, massless collisionless, expanding diagonal Bianchi I, Lambda=0, metric (-,+,+,+), proper `u=t/Tstar in [0,.08]`, initial shear (.2,-.13,-.07). No new closure, spectral temperature or polarization.

Let `M=diag(exp(-ell_i))`, `r=|M n|`, `s=-M n/r`, `t_i=s_i²`, `W=det(M) r dE_0` for frozen conserved momentum direction n. Then `E=integral W`, `P_i=integral W t_i`, `a_lm=integral W Y*_lm(s)`, `alpha_lm=(4pi/E)a_lm` for l>0.

At fixed physical source: `partial_{ell_j} t_i=2t_i(t_j-delta_ij)`, `partial_{ell_j} W=-(1+t_j)W`, `partial_{ell_j} E=-(E+P_j)`. Thus
`partial_j a_lm = integral W[-(1+t_j)Y* + sum_i partial_{t_i}Y* 2t_i(t_j-delta_ij)]`,
`partial_j alpha_lm=(4pi/E)[partial_j a_lm+a_lm(1+P_j/E)]`.

For positive reflection-even source the surviving real harmonics are:
`Y20=sqrt(5/(16pi))(3t_z-1)`,
`Re Y22=sqrt(15/(32pi))(t_x-t_y)`,
`Y40=3/(16sqrt(pi))(35t_z²-30t_z+3)`,
`Re Y42=3/8sqrt(5/(2pi))(t_x-t_y)(7t_z-1)`,
`Re Y44=3/16sqrt(35/(2pi))(t_x²-6t_x t_y+t_y²)`.
All are exact Condon-Shortley identities on the unit sphere after eight reflections.

Define `K_l^delta(u,v)=sum_m alpha_lm(u)conj(alpha_lm(v))/(2l+1)`. Differentiating in either epoch independently gives the exact cross-kernel geometry transfer. Uniform isotropic rescaling changes W by a common factor and cancels in alpha, hence `sum_j partial_{ell_j} alpha_lm=0`.

The spherical harmonic addition theorem and its tangential gradient give `||partial_j alpha_l||_2 <=4pi sqrt((2l+1)/(4pi))[1+sqrt(l(l+1))/2]`. Accordingly
`|partial_{ell_j(u)}K_l^delta| <= 4pi[1+sqrt(l(l+1))/2]`, namely 27.95696857630154 (l2), 40.66562953852208 (l4); for two epoch max-norm perturbations `|Delta K|<=3L_l(eps_u+eps_v)`.

Conditional on independent PR264 pressure source theorem on a COMMON prescribed geometry, `|Delta P_i|<=eps_P`, `|Delta E|<=3eps_P`, and `E>=0.6`, the l2 source-only kernel difference obeys `|Delta K2^delta|<=354.682 eps_P`. This gives <=1.06782e-9 for GL6 and <=2.18636e-11 for GL8. It is not an uncertainty for the stored DOP853 geometry.

**Important l4 failure of transfer**: positive `U±=(E0/4pi)(1±eta P4(n_z))` have equal E and all second pressure moments at ell=0, but different a40. Wolfram verified `integral_{-1}^1 P4(z) dz=0`, `integral z² P4 dz=0`, `integral P4² dz=2/9`. Thus pressure source certificates do not establish continuum l4 error.

PR266's conditional MPFR192 four-panel RK4/Hermite carrier certificate is NOT automatically a certificate for parent PR267 DOP853 samples. This scoped physical unit reports the geometry response at actual 41 saved DOP853 epochs and leaves that bridge unresolved. No auto-merge or production claim. Upper BASS DAG 9/15; R6 and C9 distinct-author NOT_RUN.

Primary background: Lee, Nungesser & Tod https://doi.org/10.1007/s10714-020-02699-7 ; Fleury, Pitrou & Uzan https://doi.org/10.1103/PhysRevD.91.043511 .
