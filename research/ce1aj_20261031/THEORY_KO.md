# CE1AJ: continuum finite-time dark-source to l=4 transfer in the original six-cell Einstein–Vlasov Bianchi I

Authority: parent Draft PR #288 exact HEAD \`06a89b70200c09e44711235ef6d01a0b797b2a03\`, original source SHA256 \`022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035\`. Original massless collisionless reflection-even six-cell radiation, diagonal Bianchi I, signature (-,+,+,+), Λ=0, proper u=t/Tstar∈[0,2/25]. All energy, moment and shear variables have the original Einstein-scale dimensionless normalization. No additional c=1 assumption, no change to original strict h=1e-5 target. The signed perturbation is **not a replacement** for the six positive original source cells.

## Exact theorem, scoped

Let \(\delta e=(1/406)[[53,-106,53],[-203,406,-203]]\) be the CE1AI exact dark source. Its original continuum initial E, pressure, rank-four R, and normalized l=2/l=4 moments all have zero directional variation. In contrast, the source derivative of normalized α42 has initial time jet

\[
A(0)=0,\qquad A'(0)=-(1296/203)\,[(\sigma_{x0}-\sigma_{y0})/E_0]\,(3/8)\sqrt{5/(2\pi)}<-3/4,
\]
where \(A(u)=\partial_\epsilon\alpha_{42}(u;\epsilon)|_{\epsilon=0}\). The strict rational comparison uses the **original exact IEEE-754 cell masses and shears**, \(\pi<22/7\), and \(\sqrt{35/44}>89/100\).

**Claim:** for the specific original, smooth self-consistent continuum Einstein–Vlasov IVP,

\[
\boxed{A(u)<-\tfrac34u+232225u^2<-\tfrac12u<0,\quad 0<u\le10^{-6}.}
\]

This is a mathematically explicit finite positive-time interval, but deliberately does **not** certify the sign for all u≤0.08 or the full 5×5 continuum source-to-harmonic determinant/rank.

## Constructive bounds

Write \(Q=\sum_i n_i^2e^{-2\ell_i}\), \(r=\sqrt Q\), \(V=\exp(-\sum\ell_i)\), \(x_i=n_i^2e^{-2\ell_i}/Q\), \(w=Vr\). The exact Einstein–Liouville equations give \(\ell_i'=h_i\), \(h_i'=-\theta h_i+P_i\), \(E'=-\theta E-\sum h_iP_i\), \(\theta=\sum h_i\), \(x_i'=2x_i(B-h_i)\), \(w'/w=-(\theta+B)\), \(B=\sum h_ix_i\). All \(P_i≥0\), \(\sum P_i=E\), and \(R_{ij}=\int U_0wx_ix_j\) obey \(0≤R_{ij}≤P_i\).

From the original constrained initial H, \(0.55<H_0<0.56\). Initial \(h_i>0\); positive forcing preserves it. Since \(h_i'≤E≤E_0<.901\), \(0<h_i<.76+.901(.08)<1\) on the full original [0,.08]. Therefore \(0≤\ell_i≤u\) and \(E_0e^{-4u}≤E≤E_0\) with \(E>.6\). Direct kinematics yield \(|w'|≤4w\), \(|w''|≤34w\), \(|x_i'|≤4x_i\), \(|x_i''|≤40x_i\), using \(|\theta'|<10,|B'|<8\).

Take \(f=c_{42}(7x_z-1)(x_x-x_y)\), \(c_{42}=3\sqrt{5/(2\pi)}/8\). Uniformly \(|f|≤3, |f'|≤14, |f''|≤400\). Define baseline \(N=\int U_0wf\), signed source \(M=\int\delta U_0wf\), \(S=\int\delta U_0w\), so \(E=\int U_0w\). The original signed source total variation is exactly \(512/203<3\). Thus bounds for function and first/second proper-time derivatives respectively are:
\(E:(1,4,34)\), \(N:(3,26,614)\), \(M:(9,78,1842)\), \(S:(3,12,102)\).
\(E>.6\) implies \((1/E):(2,12,250)\) and \((1/E^2):(3,38,1100)\) for absolute derivative bounds through order 2. The product/quotient rules give
\[
|(M/E)''|<7806,\quad |(NS/E^2)''|<26880.
\]
Hence the source-only contribution \(A_{\rm src}=4\pi(M/E-NS/E^2)\) satisfies \(|A_{\rm src}''|<13(7806+26880)=450918<455000\).

**Do not omit Einstein backreaction.** The exact derivative of \(P_i\) with respect to the three log-scale factors is \(J_{ik}=-P_i-2\delta_{ik}P_i+R_{ik}\). For the self-consistent dark tangent, \(\delta\ell(0)=\delta h(0)=0\) since initial \(\delta E_0=0\). With \(D=\|\delta\ell\|_\infty,K=\|\delta h\|_\infty\) one has Dini bounds \(D'≤K,K'≤6K+8D+3\). Gronwall yields \(D+K≤(3/8)(e^{8u}-1)≤9u\) for \(0≤u≤.08\), and \(D≤(9/2)u^2\). The fixed-source harmonic geometry derivative satisfies \(|\partial_{\ell_i}\alpha_{42}|<350\), using \(\partial_{\ell_i}w=-w(1+x_i)\) and \(\partial_{\ell_i}x_j=2x_j(x_i-\delta_{ij})\). Therefore \(|A-A_{\rm src}|<3\cdot350\cdot(9/2)u^2=4725u^2\).

Taylor's integral remainder proves \(A<-3u/4+(455000/2+4725)u^2=-3u/4+232225u^2\). At \(u=10^{-6}\), the coefficient is \(-.517775<-.5\). This proves the strict interval claim without invoking GL quadrature convergence.

## Physical implementation and limitation

The CI workflow executes the exact source/rational certificate and independent original Einstein–Vlasov IVPs: 12D baseline+dark tangent, plus two fully nonlinear positive perturbed 6D IVPs with \(\epsilon=\pm10^{-3}\). For each GL6, GL8, GL16, both 401-point [0,10^-6] and 401-point [0,.08] windows are integrated. Expected 2,406 baseline + 2,406 tangent + 4,812 genuinely nonlinear source-family physical records, five original physical PNGs. Original 6-cell baseline and ancestor tests remain immutable. Small-window **theorem** is derived plus exact-rational checked; endpoint u=.08 **data** are numerical GL observations, not a rigorous angular-continuum error enclosure. Genuine distinct-author R6/C9 NOT_RUN.

Primary scientific context: A. D. Rendall, arXiv:gr-qc/9505017 (1995); J. M. Heinzle & C. Uggla, Classical and Quantum Gravity 23 (2006) 3463–3489, DOI 10.1088/0264-9381/23/10/016; H. Lee, E. Nungesser & P. Tod, General Relativity and Gravitation 52 (2020) 48, DOI 10.1007/s10714-020-02699-7; H. Barzegar, D. Fajman & G. Heißel, Physical Review D 101 (2020) 044046, arXiv:1904.13290. The explicit six-cell inequality is derived here, **not** attributed as a theorem or novelty claim in those papers.

**Upper BASS DAG 9/15, 21 edges; CE1 PARTIAL, original scoped R/C 18/20, new upper nodes 0. Production HOLD, Merge HOLD, auto-next false, one bounded unit.**
