# BASS KM-2E S0 | First reciprocal electron–photon momentum feedback on prescribed Bianchi I

2026-10-30 KST | one bounded *new physical dynamics* unit. Parent Draft PR274 immutable HEAD \`8993bdf97c5aca2961a7d2e1df08bd4119899670\`. Original KM2-D electron time-profile code blob \`b599d3842e843d8de1de1499b73e6849374bf8f8\`; KM2-C full normal-frame Bianchi-I transport \`05aade3aab7e9a32c11608882c943e4d3cb6f379\`; original KM2-A instantaneous tilted Thomson source \`92660768f4719d78261fed1cb44f186d2821629d\`; original KM1 geometry \`9d500e36fefaa4ddc22300a2f03d9eb9cfe98403\`. **Do not modify these original files or any ancestor PR.** Upper BASS DAG 9/15 (21 edges), KM-2 PARTIAL. The CE1 original six-cell strict h<1e-5 is unrelated and unchanged.

## Physical construction rather than externally imposed beta

We now couple the **full original polarized photon normal-carrier** \(J_q\) to a homogeneous **cold pressureless electron dust** in a prescribed, noncommuting, homogeneous Bianchi-I background. Signature (-,+,+,+), photon propagation tetrad directions \(e_q\), normal proper \(u=t/T_\star\), \(c\) kept in physical interpretation, \(\beta=v_e/c\). Mass-shell U=gamma(1,beta). The original KM1 geometry supplies H(u), symmetric tracefree \(\sigma_{ij}(u)\), redshift \(\mu_q(u)\), screen E_q(u), raw positive quadrature w_q; P8 real S+A encodes the original Hermitian \(S+iA\).

New matter variables are **specific spatial four-velocity momentum** \(p=\gamma\beta\in\mathbb R^3\) and normal-slice electron count ratio \(\zeta=n_{\rm lab}(u)/n_{\rm lab}(0)>0\). Define \(\gamma=\sqrt{1+p^2}\), \(\beta=p/\gamma\). Electron rest density \(\,n_\star(u)=n_{\rm lab}(0)\zeta/\gamma\,\). The original \(\nu_0=n_\star(0)\sigma_T c\,T_\star\) is now self-consistently time-dependent \(\nu(u)=\nu_0\,\zeta\,\gamma_0/\gamma\), no arbitrary density boost. Let \(M_0=m_e c^2\,n_{\rm lab}(0)\) in the original photon normalization; then \(R_e=T_e^{00}=M_0\zeta\gamma\), \(Q_e^i=T_e^{0i}=M_0\zeta p_i\), \(P_e^{ij}=R_e\beta_i\beta_j\), pressureless in electron rest frame.

The original unmodified KM2A normal-time polarized cold Thomson collision is \(\mathcal C_q[J;\beta(u),\nu(u)]\). The reference metric is *prescribed*, not Einstein-solved. On \(0\le u\le .25\), with \(B=H I+\sigma\), the **new coupled actual evolution** is
\[
\begin{aligned}
\dot J_q &=\mathcal L_{\rm KM1}[J_q]+ \mathcal C_q[J;\beta,\nu],\\
\dot\zeta&=-3H\,\zeta,\\
\dot p &= -B p-\frac{F_{\gamma}^{\rm spatial}}{M_0\zeta},
\quad F_{\gamma}^\mu
=\nu\,[T_\gamma^{\mu\nu}U_\nu+U^\mu(U_\alpha T_\gamma^{\alpha\beta}U_\beta)].
\end{aligned}
\]
Here \(F_\gamma\) is **photon** collisional fourforce, so electron momentum receives the strictly opposite force. The covariant force is orthogonal \(U_\mu F_\gamma^\mu=0\), equivalently \(F_\gamma^0=\beta\cdot F_\gamma^{spatial}\). In code, use independent existing \`expected_fourforce(T_gamma,beta,nu)\` for the electron momentum ODE, and *separately* compute the original discrete polarized P8 collision force from the raw ray RHS. Their nonzero angular-discretization gap must be explicitly measured and included in the combined photon+electron stress budget; it must not be silently forced to 0.

### Exact cold-matter normal-frame laws

With the prescribed Bianchi-I normal frame, \(R_e=M_0\zeta\gamma\) and \(Q_e=M_0\zeta p\) obey
\[
\begin{aligned}
\dot R_e&=-3H R_e-(H I+\sigma):P_e-F_\gamma^0,\\
\dot Q_e&=-(4H I+\sigma)Q_e-F_\gamma^{spatial}.
\end{aligned}
\]
The first follows algebraically from the mass-shell \(p\) equation and \(\dot\zeta=-3H\zeta\). The second is direct. Equivalently
\[
\dot\beta=-(I-\beta\beta^T)\left[B\beta+\frac{F_\gamma^{spatial}}{R_e}\right].
\]
These **two different dynamical state representations** (\(p\) and \(\beta\)) enable an independent numerical variable check while sharing the original photon Thomson physics. Stateless Wolfram symbolic evaluation already returned exact residuals \(\{0,\{0,0,0\},\{0,0,0\}\}\) for the matter energy, momentum and beta-transform relations.

### Coupled total normal-frame stress conservation

For total photon+electron energy \(E=\rho_\gamma+R_e\), total pressure \(P=P_\gamma+R_e\beta\otimes\beta\) and total flux \(Q=q_\gamma+Q_e\),
\[
\begin{aligned}
\dot E&=-3H E-(H I+\sigma):P+\delta F^0_{\rm quad},\\
\dot Q&=-(4H I+\sigma) Q+\delta\boldsymbol F_{\rm quad},
\end{aligned}
\quad
\delta F_{\rm quad}=F_{\gamma,\rm actual\ raw\ P8}-F_{\gamma,\rm covariant}.
\]
The raw angular grid need not exactly integrate the collision gain; the residual is a **measured finite quadrature defect**, not newly invented physical nonconservation. Use independent Gauss quadrature in time of the *geometric total-stress work plus measured residual* to compare actual endpoint E,Q. A no-recoil comparator (switch off the electron force only) is intentionally NONconservative and is only used as a causal falsification control: if physical and counterfactual beta histories do not separate measurably, do not claim genuine backreaction.

### Scoped initial model and verification

Freeze original KM2D noncommuting prescribed Bianchi-I geometry, raw original GL polar grid, P8 full angular initial field, \(u\in[0,.25]\), \(\beta_0=(.30,-.40,.20)\), original cold Thomson \(\nu_0T_\star=1.3\). At \(\,u=0\,\) choose a **dimensionless toy cold-electron inertia** \(R_e(0)/\rho_\gamma(0)=0.75\) (this fixes the relative photon/matter energy normalization, not a measured electron cosmological abundance). The photon amplitude and original source shape are unchanged.

For \(n_\theta=8\) and \(n_\theta=12\) produce actual \(p,\beta,\zeta,n_\star/\!n_{\star0},\nu,R_e,Q_e,P_e,\rho_\gamma,q_\gamma,P_\gamma\) histories, photon angular source \(M_e\), total E,Q, optical depth, exact kinematics and measured \(\delta F_{\rm quad}\); compare two independent matter state parametrizations p and beta. Include the no-recoil *nonphysical control*, vacuum zero-opacity and inertial flat/free collision limiting cases as local tests. Integrate separate GL24 total energy/momentum flux-work records. No new photon \(\ell=4\) proof, no phenomenological fitting, no cold-electron thermal bath or electron heat conduction.

**Scope limit:** first mutual **momentum and bulk kinetic-energy exchange** for homogeneous cold electron dust and original full polarized radiation, on a **prescribed** Bianchi-I geometry. Electron number conservation and mass shell are enforced; no Einstein backreaction, no independent electron pressure/temperature evolution, no recoil frequency redistribution / Kompaneets / relativistic quantum Compton, no generic inhomogeneous multi-fluid, no production Rust and no observational CMB likelihood. \`KM2=PARTIAL\`, \`UPPER_DAG=9/15\`, \`new_upper_completed=0\`, \`production_ready=false,merge_ready=false,auto_next=false\`. True distinct-author R6/C9 and native subagent unavailable: NOT_RUN.

STOP_AFTER_ONE_BOUNDED_UNIT=true.
