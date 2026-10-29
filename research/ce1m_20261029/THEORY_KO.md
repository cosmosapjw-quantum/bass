# CE1-M 이론 연구: 양의 collisionless Bianchi-I source-local 인증과 물리 입력 잠금의 결합

**권위/범위.** Parent `cosmosapjw-quantum/bass` PR #251 (`cd7e7efdb384580ae44c0cdca873eba018a404e2`), mathematical donor PR #249 (`0370f99aea7cc457b32a3ebc259a343a82ac5a9f`). Both are independent Drafts; this is a scoped unmerged synthesis. Signature (-,+,+,+), Λ=0, reflection-even homogeneous diagonal Bianchi I; massless collisionless positive angular-energy measure. Normal proper u=t/T_*; ℓ_i=ln a_i and h_i=T_* H_i. E,P carry factor 8πGT_*²/c². Exact original stored binary64 6-cell fixture, shear(.2,-.13,-.07), u∈[0,.08], RK4 4 panels, target max|Δh|<1e-5. No collision, tilt, polarization, spatial perturbations or observed sky.

## Definition and derivation
For a fixed positive finite angular measure M or stored positive-ray sum Q, define b_i=e^{-2ℓ_i}, V^{-1}=e^{-∑ℓ_i}, Z=∑_j b_j n_j². Then

  P_i^M(ℓ)=V^{-1}∫ b_i n_i² Z^{-1/2} dM;   P_i^Q similarly for current exact-real stored binary masses/rays.

Under common dilation ℓ↦ℓ+s·1, V^{-1}↦e^{-3s}V^{-1}, b_i↦e^{-2s}b_i, Z^{-1/2}↦e^{s}Z^{-1/2}. Thus

  P_i^{M,Q}(ℓ+s1)=e^{-4s}P_i^{M,Q}(ℓ),
  D_i(ℓ+s1)=e^{-4s}D_i(ℓ),  D_i=P_i^M−P_i^Q.

This is an exact algebraic identity for fixed measures and nonzero ray norms. Positivity is required to invoke the certified source majorant and sign-definite Jacobian; not needed solely for the common-scale algebraic identity.

The positive-pressure Jacobian is

  ∂_{ℓ_j}P_i=−(1+2δ_{ij})P_i+R_{ij},  R_{ij}≥0,  ∑_jR_{ij}=P_i.

Hence ∂_{ℓ_j}P_i≤0 and ∑_j|∂_{ℓ_j}P_i|=4P_i. For two expanding histories and their intervening segment, a panel-local common lower logscale m_j≥0 yields

  L_j=4P_max(0)e^{-4m_j}.

If the exact solution and the recorded binary Hermite polynomial on u∈[u_j,u_{j+1}] satisfy ℓ_i≥m_j and both satisfy the independent global upper box ℓ_i≤B_i, with B_i≥m_j certified, put ξ=ℓ−m_j1∈[0,B−m_j1]. The existing MPFR192 CE1-F positive-source oracle E_Q is an upper enclosure for |D_i(ξ)|. Hence

  η_j=min{η_global, e^{-4m_j} E_Q([0,B−m_j1])}.

All float inputs for m_j and B are interpreted as exact binary; MPFR interval subtraction/exponentials are directed outward. If any B_i<m_j, fail closed. The comparison system

  D⁺e_ℓ ≤ e_h+ρ_ℓ,
  D⁺e_h ≤ L_j e_ℓ+η_j+ρ_h

has a positive 2×2 propagator (matrix off-diagonal entries 1,L_j). Apply it panelwise with separate source, initial, time and exact binary Hermite endpoint jumps. Retain original Emax in source/geometry bounds; do not replace it by P_max.

## Why the PR251 physical-input lock is load-bearing
The positive-source theorem assumes the continuum measure M and stored numerical Q correspond to the actual data being certified. The PR248 cardinality counterexample showed `zip` could omit appended rays; PR250 requires shape n:(N,3),mass:(N,), N=len(cells). PR251 additionally locks the construction-time physical cells, total continuum energy, refinement and binary64 table edges/weights, while retaining allowed same-cardinality positive numerical ray/mass rebinding. The independent fourth-derivative majorant assumes termwise nonnegative current masses and PR251 rejects signed cancellation. This closure is a **domain-precondition repair**, not a change of Einstein–Vlasov dynamics.

## Evidence and limits
The three PR251 amended code files were reproduced locally and git-hash matched exactly: `einstein_tabulated_source.py fdeb83a65cd424786ba6bb8ddadbcb2b2e2d45bf`, `einstein_interval.py abbab0990fdefaf535ccbf5191ae3e060cb19214`, `einstein_tabulated_sharp.py 61560ed52a78c01fe6f21923a7480af732d9ec4f`. PR249 source-local module blob `1c905278f7a109e15f5e20d3ac7f931bdcf99433`. Pre-repair hostile tests 4 FAIL/1 PASS; after exact patch 107 tests PASS. Wolfram independently evaluated ray scaling ratio 1 and sum of ℓ-derivatives+4P=0.

Fresh ref8 full source/time certificate at 384 rays gives `9.411551484445186e-6 < 1e-5`. Fresh ref16 MPFR source-only recertification with SHA-exact PR246/251 stored source and path gives `2.9617469790966602e-6`, using SHA-verified *inherited* ref16 time/jump and initial carriers. Current-turn full time residual at ref16 NOT_RUN, formal MPFR/Python program verification NOT_RUN, separate distinct human-author R6/C9 NOT_RUN. Result does not license generic Einstein–Boltzmann or production solver claims.

Primary methodological context: A. Neumaier, *Computing* 52 (1994), 315–336, DOI 10.1007/BF02276880 (logarithmic norms/differential inequalities); J.M. Heinzle & C. Uggla, *Class. Quantum Grav.* 23 (2006) 3463, DOI 10.1088/0264-9381/23/10/016 (Bianchi I Einstein–Vlasov dynamical system). Neither source establishes the particular CE1-M numerical result; the identities and fixed-fixture computation here are direct and scoped.
