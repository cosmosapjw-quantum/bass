# Conserved-element affine coordinates for the compact H–Li model

The parent is BASS PR180,574c3af93810122af0a7977e00e34195e5251a09, with REC source a949529872eb5ba0e20c7e206fe893e5d544e48c. Its isotope-equality and reflection-even restrictions already reduced62coordinates to33. This increment applies a further invariant-manifold restriction to that unchanged actual model.

Let v∈R33 and F(x,v) be its RHS with x=ln(a/a_ref). The three charge-fraction blocks are H:[23,24], He:[25,26,27], Li:[28,29,30,31]. Nuclear inventory transfer is inactive because n/T inventories vanish; the adopted electronic transitions conserve each element fraction total. Therefore C F=0, where each row of C sums one block, including when the common electron density feeds back nonlinearly. These are conservation relations, not ionization equilibrium assumptions.

Record the actual initial totals c=Cv0. In particular the current binary64 hydrogen total is0.9999999999999999, not forcibly renormalized to1. Remove indices23,25,28, obtaining u=Rv∈R30. Define v=d+Lu, with neutral fractions c_Z−sum(charged fractions), retained entries copied, and d nonzero only at neutral coordinates. Then RL=I30 and CL=0. On the fixed-total subspace LR acts as the identity on tangent vectors. Hence

    u′=R F(x,d+Lu),
    J30=R J33(x,d+Lu) L,
    L u′=F(x,d+Lu).

No projection claim applies outside the conserved-total tangent space. The implementation performs sparse state reconstruction and analytic Jacobian restriction, retaining the original rates, geometry, opacity, all21population outputs and tau. Geometry/matter/radiation tensor conventions are unchanged: signature(-,+,+,+), sigma=diag(-s,-s,2s), pi_A=diag(-p_A,-p_A,2p_A), sigma:pi_A=6sp_A. Signed matter/radiation stress is combined before norm. Baryons still have pi_b=0; collisionless nonbaryonic matter owns pi_m.

The coordinate count changes33→30 (9.09%fewer); dense Newton matrix entries1089→900 (17.36%fewer). The wrapper still evaluates the existing full62 owner internally. Those algebraic size reductions do not establish a wall-time speedup. No benchmark or new IVP is claimed.

At finite precision the affine lift is not bit-identical to all33state representations, and near fully ionized states a very small neutral fraction can lose relative precision by subtraction. No clipping is applied. The absolute tolerance and reconstruction error must be controlled. Isotope-specific rates, nonzero n/T transmutation, odd multipoles, or arbitrary fraction totals that change during evolution invalidate this exact reduction and require a larger representation.

An adaptive-controller distinction is essential. For a reduced error e30, its full error is L e30, not d+L e30. The original compact33 weighted norm is sqrt(sum_i((L e30)_i/s_i)^2/33). Eliminated rows produce cross terms between charged errors, so diagonal30 tolerances alone cannot preserve this norm. Companion VigilODE research/lifted_error_norm_20261022 provides an allocation-free native kernel; current solver wiring remains pending. Full33 norm preservation does not assert full62 norm preservation.

Validation used the actual initial state and two declared synthetic positive H–Li states at x0.8/1.4, with12finite-difference tangent directions. Inherited finite-state criteria were RHS/tangent2e-12 and FD2e-6. Actual maxima: RHS1.7945e-16, tangent1.2213e-15, FD1.3605e-8;21output reconstruction1.5266e-16. The verification took0.106s and performed0IVPs. This proves implementation correspondence at tested points and supplies the algebraic reduction; it is not a new full-EoR accuracy certificate.
