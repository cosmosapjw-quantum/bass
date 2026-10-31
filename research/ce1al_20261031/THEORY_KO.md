# CE1AL | 원본 six-cell에 대한 Weyl 곡률 delayed response

기준 Draft PR #292 HEAD \`607aa819c7e3239c4c858884400333195587fd3d\` (immutable). Source SHA256 \`022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035\`.

조건: diagonal Bianchi I, (-,+,+,+), massless collisionless even six-cell Vlasov, Λ=0, 8πG=1의 원본 Einstein 정규화, u=t/Tstar∈[0,0.08], h_i=ell'_i, theta=Σ h_i, initial sigma=(0.2,-0.13,-0.07). Dirac delta나 thermal CMB source로 치환하지 않는다.

\[
E=V\int U_0 r\,dΩ,\quad P_i=V\int U_0 r x_i\,dΩ,\quad
h'_i=-\theta h_i+P_i,\quad \sum_{i<j}h_i h_j=E.
\]
R_{\hat0\hati\hat0\hati}=-(h'_i+h_i^2);
R_{\hati\hatj\hati\hatj}=h_i h_j.
Einstein and traceless radiation imply
\[
\mathcal E_i=C_{\hat0\hati\hat0\hati}
=\theta h_i-h_i^2-\frac12(P_i+E),\quad
\sum_i\mathcal E_i=0.
\]
In diagonal purely electric Bianchi I:
\[
C_{abcd}C^{abcd}=8\sum_i \mathcal E_i^2
=K-2R_{ab}R^{ab},\quad
K=4\sum_i[(h_i'+h_i^2)^2]+\ 4\sum_{i<j}h_i^2h_j^2,
\quad R_{ab}R^{ab}=E^2+\sum_i P_i^2.
\]
Exactly source-owned dark variation D=[[53,-106,53],[-203,406,-203]]/406 (the six cell mass derivatives, NOT an authorized replacement source) has initial δE=δP=δR=0. Exact sixth angular tensor has \(\delta T_{xxy}=-27/(1421π)\). Set \(A_i=\sum_{jk}\sigma_{j0}\sigma_{k0}\delta T_{ijk}(0)\).
CE1AK initial jets: \(\delta P_i=\frac32 A_i u^2+O(u^3)\), \(\delta h_i=\frac12 A_i u^3+O(u^4)\), \(\delta E=-\frac12\sigma_0\cdot A\,u^3+O(u^4)\).
Then \(\delta\mathcal E_i=-\frac34 A_i u^2+O(u^3)\).
\[
\delta(C^2)=-12\sum_i\mathcal E_i(0)A_i\,u^2+O(u^3)=\kappa u^2+O(u^3).
\]
Exact dyadic source and rational brackets π∈(3.141,3.142), √2∈(1.414,1.415), H0∈(.557,.558) yield a strict \(-.002252<\kappa<-.002079<0\); see independent remote fraction-source implementation and full local exact certificate.

At u=.08 the GL16 source-response curvature shift \(\delta C^2≈-8.4128360×10^{-6}\), δK≈-9.0961581×10^-6, numerical only. No proof of all-u continuum negative sign, no CMB likelihood, no observational units restored. No claim of cosmological novelty.

Distinct-author R6/C9 NOT_RUN. No upper DAG promotion: BASS 9/15 (21 edges), CE1 PARTIAL, new upper 0, scoped inherited 18/20, production/merge hold, auto_next false.
