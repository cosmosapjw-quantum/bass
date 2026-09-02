# BG-02 GR background Einstein-projection formula contract

Status: `FORMULA_DESIGN_ONLY / PRODUCTION_NOT_IMPLEMENTED`

Scientific parent:

```text
BASS Draft PR #91
commit 80d271cc528e1a0ffa813ecd3e3fb7610f3fa755
tree   3fd8818938eaa0988988c6927cff799455a7a31d
```

This stage fixes the four projections of

\[
E_{ab}=G_{ab}+\Lambda g_{ab}-\kappa_G T_{ab},
\qquad
\kappa_G=\frac{8\pi G}{c^4},
\]

without claiming a production background module.

## 1. Conventions

\[
g_{ab}n^an^b=-1,\qquad h_{ab}=g_{ab}+n_an_b,
\]

\[
K_{ab}=h_a{}^ch_b{}^d\nabla_cn_d
      =H_{\rm geom}h_{ab}+\sigma_{ab},
\qquad K=3H_{\rm geom}.
\]

Positive flat-FLRW expansion has `K_ab = H_geom h_ab`.
The physical normal acceleration is

\[
A_a=n^b\nabla_bn_a.
\]

It is not the Bianchi commutator vector \(a^B_a\).

Matter is decomposed as

\[
T_{ab}=\rho n_an_b+2n_{(a}q_{b)}+p h_{ab}+\pi_{ab},
\]

\[
q_a=-h_a{}^cT_{cd}n^d,\qquad \pi_{ab}=T_{\langle ab\rangle}.
\]

The bare symbol \(\kappa\) remains the Thomson opacity \(n_e\sigma_T\),
of dimension \(L^{-1}\).  GR code must use `kappaG` or `kappa_G`.

A dot denotes \(n^a\nabla_a\).  With proper time \(t\),
\(n^a\nabla_a=(1/c)d/dt\).

## 2. Four off-shell projections

### 2.1 Hamiltonian projection

\[
\boxed{
\mathcal H\equiv n^an^bE_{ab}
=\frac12\left({}^{(3)}R+K^2-K_{cd}K^{cd}\right)
-\Lambda-\kappa_G\rho
}
\]

or

\[
\boxed{
2\mathcal H={}^{(3)}R+6H_{\rm geom}^2
-\sigma_{ab}\sigma^{ab}-2\Lambda-2\kappa_G\rho .
}
\]

### 2.2 Momentum projection

\[
\boxed{
\mathcal M_a\equiv-h_a{}^cn^dE_{cd}
=D^bK_{ab}-D_aK-\kappa_Gq_a .
}
\]

For homogeneous tetrad components,

\[
\boxed{
D^b\sigma_{\alpha b}
=-3a_B^b\sigma_{\alpha b}
-\epsilon_{\alpha\mu\nu}n_B^\mu{}_b\sigma^{b\nu} .
}
\]

Hence

\[
\mathcal M_\alpha
=-3a_B^b\sigma_{\alpha b}
-\epsilon_{\alpha\mu\nu}n_B^\mu{}_b\sigma^{b\nu}
-\kappa_Gq_\alpha .
\]

In the exceptional \(VI_{-1/9}\) witness chart,

\[
\boxed{
D^b\sigma_{3b}=N_{22}\Sigma_{12}+(N_{23}-3A)\Sigma_{13} .
}
\]

This carrier must survive any proper-frame diagonalization of \(n_B\).

### 2.3 Spatial trace projection

Define

\[
\mathcal A\equiv D_aA^a+A_aA^a .
\]

Then

\[
\boxed{
\mathcal T\equiv\frac13h^{ab}E_{ab}
=-\frac16{}^{(3)}R-\frac23\mathcal L_nK
-\frac12K_{ab}K^{ab}-\frac16K^2
+\frac23\mathcal A+\Lambda-\kappa_Gp .
}
\]

Using \(K=3H_{\rm geom}\),

\[
\boxed{
\mathcal T=-\frac16{}^{(3)}R-2\mathcal L_nH_{\rm geom}
-3H_{\rm geom}^2-\frac12\sigma^2
+\frac23\mathcal A+\Lambda-\kappa_Gp .
}
\]

### 2.4 Spatial PSTF projection

\[
\boxed{
\begin{aligned}
\mathcal S_{ab}\equiv E_{\langle ab\rangle}
={}&{}^{(3)}R_{\langle ab\rangle}
+(\mathcal L_nK_{ab})_{\langle ab\rangle}
+K K_{\langle ab\rangle}
-2K_{c\langle a}K_{b\rangle}{}^c\\
&-D_{\langle a}A_{b\rangle}
-A_{\langle a}A_{b\rangle}
-\kappa_G\pi_{ab}.
\end{aligned}
}
\]

No Bianchi branch equation may be hand-entered.  Branch dependence enters
only through the composed \((a_B,n_B)\mapsto{}^{(3)}R_{ab}\) generator and
provider matter variables.

## 3. Expansion-rate forms and off-shell identities

Setting \(\mathcal T=0\) gives

\[
F_{\rm trace}
=-\frac1{12}{}^{(3)}R-\frac32H_{\rm geom}^2
-\frac14\sigma^2+\frac13\mathcal A
+\frac12\Lambda-\frac12\kappa_Gp .
\]

The trace-reversed ADM form is

\[
F_{\rm ADM}
=-\frac13{}^{(3)}R-3H_{\rm geom}^2
+\frac13\mathcal A
+\frac{\kappa_G}{2}(\rho-p)+\Lambda .
\]

Raychaudhuri gives

\[
F_{\rm Ray}
=-H_{\rm geom}^2-\frac13\sigma^2+\frac13\mathcal A
-\frac{\kappa_G}{6}(\rho+3p)+\frac{\Lambda}{3} .
\]

They are not interchangeable off shell:

\[
\boxed{F_{\rm ADM}-F_{\rm trace}+\frac12\mathcal H=0,}
\]

\[
\boxed{F_{\rm trace}-F_{\rm Ray}+\frac16\mathcal H=0,}
\]

\[
\boxed{F_{\rm ADM}-F_{\rm Ray}+\frac23\mathcal H=0.}
\]

A production solver may integrate one primary rate, but it must expose the
other two as diagnostics and must not silently project onto \(\mathcal H=0\).

## 4. Shear-rate representations

The Lie-derivative form is

\[
\boxed{
\begin{aligned}
(\mathcal L_n\sigma_{ab})_{\langle ab\rangle}
={}&-{}^{(3)}R_{\langle ab\rangle}
-H_{\rm geom}\sigma_{ab}
+2\sigma_{c\langle a}\sigma_{b\rangle}{}^c\\
&+D_{\langle a}A_{b\rangle}
+A_{\langle a}A_{b\rangle}
+\kappa_G\pi_{ab}.
\end{aligned}
}
\]

Since

\[
(\mathcal L_n\sigma)_{\langle ab\rangle}
=\dot\sigma_{\langle ab\rangle}
+2H_{\rm geom}\sigma_{ab}
+2\sigma_{c\langle a}\sigma_{b\rangle}{}^c,
\]

the projected-covariant derivative is

\[
\boxed{
\dot\sigma_{\langle ab\rangle}
=-3H_{\rm geom}\sigma_{ab}
-{}^{(3)}R_{\langle ab\rangle}
+D_{\langle a}A_{b\rangle}
+A_{\langle a}A_{b\rangle}
+\kappa_G\pi_{ab} .
}
\]

Every API must declare which derivative it returns.

## 5. Homogeneous curvature generator

Modulo \(n_B^{ab}a^B_b=0\),

\[
\boxed{
{}^{(3)}R=-6a_B^2-n^B_{ab}n_B^{ab}
+\frac12(\operatorname{tr}n_B)^2 .
}
\]

Normalized exact witnesses are

\[
I:0,\qquad V:-6,\qquad II:-\frac12,\qquad IX:\frac32 .
\]

## 6. P0 connection-index-order guard

Canonical storage is

```text
Gamma[[gamma,alpha,beta]]
 = <e_gamma, nabla_{e_alpha} e_beta>.
```

Curvature consumes the locked view `[[alpha,beta,gamma]]`.
Feeding canonical storage directly into the locked-order contraction gives
exact but false values:

\[
{}^{(3)}R_V:-6\longrightarrow+4,
\qquad
{}^{(3)}R_{II}:-\frac12\longrightarrow+\frac32.
\]

Production code must call either

```text
ConnectionToLockedGammaOrder[LeviCivitaConnection[a,n]]
```

or the composed `ONFRicciTensor` / `ONFScalarCurvature` APIs.  A second
embedded Koszul implementation is forbidden.

## 7. Dimensions

\[
[H_{\rm geom}]=[K_{ab}]=[\sigma_{ab}]=[A_a]
=[a_B^a]=[n_B^{ab}]=L^{-1},
\]

\[
[{}^{(3)}R_{ab}]=[\Lambda]=[\mathcal H]=[\mathcal M_a]
=[\mathcal T]=[\mathcal S_{ab}]=L^{-2},
\]

\[
[\kappa_G\rho]=[\kappa_Gp]=[\kappa_Gq_a]
=[\kappa_G\pi_{ab}]=L^{-2}.
\]

## 8. Required limits

1. Flat FLRW:
   \[
   3H_{\rm geom}^2=\kappa_G\rho+\Lambda,
   \qquad
   \mathcal L_nH_{\rm geom}=-\frac{\kappa_G}{2}(\rho+p).
   \]
2. Flat de Sitter:
   \(\rho=p=\sigma={} ^{(3)}R=\mathcal A=0\),
   \(\Lambda=3H_{\rm geom}^2\), and \(\mathcal L_nH_{\rm geom}=0\).
3. Kasner vacuum, with \(\tau=ct\):
   \[
   H_{\rm geom}=\frac1{3\tau},\quad
   \sigma^2=\frac2{3\tau^2},\quad
   \mathcal L_nH_{\rm geom}=-\frac1{3\tau^2}.
   \]
4. Exceptional \(VI_{-1/9}\): retain the momentum carrier above.

## 9. Claim ceiling

This contract authorizes a production implementation task.  It does not
authorize claims of completed background evolution, constraint propagation,
matter closure, all-family runtime support, numerical parity, provider
admission, observables, fitting, or publication-grade solver maturity.
