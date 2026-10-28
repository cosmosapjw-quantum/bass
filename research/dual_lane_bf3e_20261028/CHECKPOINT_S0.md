# BF3-E S0: pinned retarded local-source memory

Parent PR226/aca22f4b7287b642d65caf2c820b681b76ab1309. Parent ZIP188277bytes SHA25643bcf2aecece8376d96c989464d746b12ece7b751cf5a45c9828282d14af8b59 verified locally. Current Python3.13.5 execution passed. Native subagent and independent-model review NOT_RUN; old science campaigns not replayed.

Scope: prescribed static periodic lapse N=exp(epsilon cos x),signature(-+++),coordinate u=t/Tstar,cbar=cTstar/Lstar. Normal-rest cold Thomson proper opacity nu_star=n_e_star sigma_T c Tstar, coordinate rate kappa=N nu_star. State Y=N^4 meridional2x2 carrier, local S=N^4 M=int EYE^T dOmega. Final-x final-angle quadrature, no global Jacobian factor. Whole initial carrier retained.

Continuum inverse-ray Duhamel uses retarded x_s,mu_s,screen and exp[-int kappa(x_r)dr]. Finite collocation instead uses its own streaming-loss A=-v_x D_x-v_mu D_mu-diag(kappa); exp(tA) is not assumed equal to projected finite-time inverse remap. Solve S=L exp(tA)Y_i+int L exp((t-s)A) B S(s)ds independently, with B containing rate and polarized gain geometry. Exact exponential polynomial weights from augmented block exponential, two unknown source stages per panel, no A inverse or cumulative fundamental inverse. No direct radiation history input.

Fixed gates: algebra2e-11,stationary4e-10,fine same-grid source3e-8,observed time order>=3.3,matrix reference3e-8. Primary nx17,nmu10,nphi8,epsilon.55,u<=.4,nu_star=1.1+.3sinx. Compare direct collocation, inverse-map Strang, independent small full-generator exponential, N^-4 equilibrium, finite-lapse non-equilibrium clock, initial source-null tail and Killing balance. Separate time/space/angle/remap error. No performance superiority, generic positivity or infinite-tail claims.

S0/S1/S2 are backup stages of this unit, not extra DAG nodes. Upper8/15,BF3 PARTIAL,production_ready=false. Dedicated child branch only. No main/owner/integration-parent/default/native edits or merge, no EFE/material feedback or automatic next node.
