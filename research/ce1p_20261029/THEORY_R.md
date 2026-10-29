# BASS CE1-P (candidate) | Physical history of the frozen collisionless Bianchi-I source

## Source authority and scope (R1)
Parent: BASS PR253 `e4a0feba0e8709d5e996ed8ef4c9c9bf1da4c4d0`, CE1-N documentation PR255 `1c84ddce20b51b46bb7713c68f08af31b359ccfa`. Sibling MPFR premise repairs PR254 and PR256 are independent/unmerged. Physical inputs: exactly the original six positive angular-cell binary64 masses and original edges; reflection-even massless collisionless diagonal Bianchi I, expanding, Lambda=0, metric (-,+,+,+), a_i(0)=1, u=t/Tstar in [0,0.08], shear=(0.2,-0.13,-0.07). Geometry and pressure normalization follow original CE1-A/CE1-F code.

## Momentum-space construction (R2–R5)
The spatial Killing covariant photon momenta p_i remain constant. For initial unit covariant direction n0, define q_i(u,n0)=exp(-2 ell_i)n0_i^2, r=sqrt(sum q_i), V=exp(sum ell_i), with ell_i=ln a_i. Let dW(n0)>=0 be the original six-cell angular energy measure, including eight reflected octants. Then the dimensionless angular stress source is

  E=V^-1 integral r dW,   P_i=V^-1 integral (q_i/r) dW.

The local orthonormal stress is diagonal under the specified reflection symmetry. Exact kinetic identities:

  sum_i P_i = E,
  dE/du = -theta E - sum_i h_i P_i,
  theta=sum_i h_i, h_i=d ell_i/du.

Einstein equations, in original normalized units (E=8 pi G Tstar^2 rho_energy / c^2):

  h_i'=-theta h_i + P_i,
  S_i=h_i-theta/3,  pi_i=P_i-E/3,
  C=sum_{i<j} h_i h_j-E,  C'=-2 theta C.

The shear equation obtained by trace-free projection is S_i'=-theta S_i+pi_i. The physically meaningful directional energy ratio at fixed canonical direction n0 is r(u,n0)/r(0,n0), with principal values exp(-ell_i). It is a bolometric photon-energy redshift carrier for this source, NOT a thermodynamic CMB temperature field.

A continuum solution is obtained by numerical angular integration of the original *piecewise-constant* six cells, not by changing their physical measure. Separate GL24 and GL40 angular quadratures evaluate the same continuum integrals, and independent stored ref8/ref16 solve the original positive numerical ray approximations. GL40 and DOP853 constitute high-resolution, **non-certified** reference values; the CE1-N ref8 bound 9.28056365759593e-6 on directional h applies only to the named frozen RK4/Hermite path, not automatically to this new DOP853 trajectory.

## Literature (R2)
Heinzle & Uggla, Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations, Classical and Quantum Gravity 23 (2006), doi:10.1088/0264-9381/23/10/016. Lee, Nungesser & Tod, On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology, General Relativity and Gravitation 52,48 (2020), doi:10.1007/s10714-020-02699-7, arXiv:1911.04937. Lee, Nungesser, Stalker & Tod, Homogeneous solutions to the Einstein-matter equations with a magnetic field and a conformal gauge singularity, Revista Matemática Complutense 38 (2025) 733–769, doi:10.1007/s13163-025-00525-9. The last work corroborates canonical-momentum kinetic source structure but its magnetic/conformal singularity assumptions are NOT imported into the present finite-proper-time case.

## Verification and admission (R6–R10)
Wolfram source-algebra check: {sum(P)-E, E'+theta*E+sum(h P), C'+2theta*C} = {0,0,0}, using the finite-ray single-direction integrand and linear superposition. Independent numerical test must check pressure trace, Hamiltonian propagation and shear law across sampled times; no numerical result can establish a new long-time isotropization theorem. Distinct-author R6 and production C9 remain NOT_RUN. Completion of a scoped **physical-history dataset** is scientific progress but does not fulfill the top-level CE-1 production or formal theorem gate. Expected upper DAG remains 9/15 until separately accepted.