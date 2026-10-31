# CE1AK | original six-cell dark-source delayed Einstein response

Authority: immutable CE1AJ PR #290 HEAD 50dc76e3ba460d0565b65a60b816af2ded0da6a3, six-cell IEEE754 source SHA256 022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035. No parent/main/sibling alteration. Metric (-,+,+,+), Λ=0, massless collisionless reflection-even Vlasov, diagonal Bianchi I, proper normalized u=t/Tstar∈[0,.08]. Preserve original Einstein units and h=1e-5 target; do not impose a new c=1 assumption.

Define Q=Σ_i n_i² exp(-2ell_i), r=sqrt(Q), x_i=n_i² exp(-2ell_i)/Q and V=exp(-Σell_i). Exact angular moments are M_{i1...ik}=V∫_{S²}U0(n) r∏ x_{i_a}dΩ. E=M_empty, P_i=M_i, R_ij=M_ij, T_ijk=M_ijk. Original dark source variation (not a replacement source) is δε=[[53,-106,53],[-203,406,-203]]/406. At the frozen original geometry, δE(0)=δP(0)=δR(0)=0, initial δε-based Hamiltonian tangent geometry δh_i(0)=δell_i(0)=0.

Original azimuth cells φ∈[0,π/8],[π/8,3π/8],[3π/8,π/2] have mean cos4φ=(2/π,-2/π,2/π). The means of (1−μ²)^3 in μ∈[0,1/2],[1/2,1] equal 1759/2240 and 289/2240. Using cos^4φ sin²φ=1/16+cos2φ/32−cos4φ/16−cos6φ/32 and dark source row cancellations gives the **exact continuum source six-index moment** δT_xxy(0)=q=−27/(1421π). The remaining independent entries are δT_xxx=δT_yyy=−3q, δT_xyy=δT_xxy=q, δT_xxz=δT_yyz=2q, δT_xyz=−2q, δT_xzz=δT_yzz=δT_zzz=0. All Σ_iδT_ijk=δR_jk=0 exactly.

Kinetic angular moment hierarchy (no closure): M'_{i1...ik}=−(θ+2Σ_a h_{i_a})M_{i1...ik}+(2k−1)Σ_j h_j M_{i1...ik j}, θ=Σh_i. Hence P_i'=−(θ+2h_i)P_i+Σ_j h_jR_ij and R_ij'=−(θ+2h_i+2h_j)R_ij+3Σ_k h_kT_ijk. Set A_i=Σ_jk σ_j0 σ_k0 δT_ijk(0), σ_i=h_i−H and Σσ_i=0. Common H0 drops out because every source δR_jk(0)=0, so δP_i''(0)=3A_i, ΣA_i=0.

Einstein ell_i'=h_i, h_i'=−θ h_i+P_i yields δh_i'''(0)=3A_i and δell_i''''(0)=3A_i. Stress work W=σ_i(P_i−E/3), energy E'=−θE−h·P, giving δW''(0)=3σ·A and δE'''(0)=−3σ·A. Exact algebraic factorization:
σ·A = −3q(σ_x−σ_y)^2(σ_x+σ_y−2σ_z)>0 for original shear (.2,-.13,-.07) interpreted as exact binary64. It evaluates to +0.0004149428091190049 (display). Therefore δW''>0, δE'''<0 and a local δ>0 exists by analyticity, but no explicit certified δ for these work/energy observables has been established.

Leading time jets:
δP_i(u)=(3/2)A_i u²+O(u³);
δh_i(u)=A_i u³/2+O(u⁴);
δell_i(u)=A_i u⁴/8+O(u⁵);
δW(u)=(3/2)(σ·A)u²+O(u³);
δE(u)=−(1/2)(σ·A)u³+O(u⁴).
Energy transfer is consistent with E'+4HE=−W; the first nonzero δW'' and δE''' have opposite signs and equal magnitude.

These claims are **derived/exact-rational checked initial continuum jets**, NOT an analytic all-horizon sign or a rigorous finite u=0.08 CMB prediction. Actual numerical GL6/8/16 coupled Einstein IVPs and fully nonlinear ±source-family IVPs are separate evidence, not continuum enclosures.

Primary research references:
A.D. Rendall, "The initial singularity in solutions of the Einstein-Vlasov system of Bianchi type I" (1995), https://arxiv.org/abs/gr-qc/9505017;
J.M. Heinzle and C. Uggla, CQG 23 (2006), DOI 10.1088/0264-9381/23/10/016;
H. Lee, E. Nungesser, P. Tod, GRG 52 (2020) 48, DOI 10.1007/s10714-020-02699-7;
H. Barzegar, D. Fajman, M. Heißel (2020), https://arxiv.org/abs/1904.13290.

Upper BASS DAG=9/15 (21 edges), CE1 PARTIAL, inherited scoped R/C=18/20, new upper completed=0, genuine distinct-author R6/C9 NOT_RUN, native subagent NOT_RUN, production/merge HOLD and no auto-next.