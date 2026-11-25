# R117-REC-BASS-COUPLED-STIFF-SDIRK2-01

BASS parent 4e30aeb722a132f87ddfbc44d0f22247d4c6f47e.
REC pinned f67be237187372f4d89fe8c021819a38261b14eb (R117 stage API).
HTT previous f0220ea86cf7ff798157e48827f1cc53406c6807.
No R78 promotion. Cold bolometric Thomson, source-conditioned REC Planck/TLA
and native HeI, heat/binding energy tracer only; one owner phase per run.
The user requested the next loop; the decision is a partitioned SDIRK
chemistry/conservative BASS substep, NOT monolithic SDIRK on the entire state.

## C1-C4: construction
eta=ln(a/a_emit), expanding H>0; beta=v/c; g=1-1/sqrt(2).
delta=y-y_ref, F=R(y,Z)/(gamma_b H)-R_ref(y_ref)/(H_ref).
delta1=delta0+g h F1; delta2=delta0+(1-g)/g*(delta1-delta0)+g h F2.
REC owns its stage state and weighted thermal ledger. R(z)=(1+(1-2g)z)/(1-gz)^2;
L-stable for scalar test but not positive for all h. Stage order one.
See Alexander 1977 doi:10.1137/0714068; multirate coupling order conditions
are separate (Roberts et al. Implicit multirate GARK, OSTI 1860730).

BASS advances Z from eta_n to eta_n+g h, then to eta_n+h.
On each subinterval [a,b] use a linear profile of the full bare rate
k = c sigma_T n_H xe/H, not just the electron fraction. Solve scalar fixed
point k_b = c sigma_T n_H,b(k_b) xe_b(k_b)/H_b(k_b).
For each candidate k_b, recompute geometry predictor, accepted conservative
recoil/transport, and stage REC implicit root from unchanged left state.
24 bounded iterations, secant acceleration only inside finite nonnegative
rate domain. Fail closed on nonconvergence; no silent clipping or fallback.
Use 128 eps relative tolerance on bare rate. Store only accepted records.
Directional Doppler factor in collision already; bare k excludes D.
Depth = (b-a)(k_a+k_b)/2. Linear k and midpoint geometry plus conservative
second-order radiation integrator have local O(h^3) error on smooth,
finite-stiffness trajectories if stages are solved accurately and stable.
Stage1 delta has O(h^2) stage error, which causes O(h^3) error in Z;
both stage environments have O(h^2) errors or better. The second-order
quadrature of F gives local O(h^3) chemistry under these hypotheses.
This is a consistency argument, NOT a stiff-uniform global stability theorem.
Fixed finite table knot crossings and interpolation affect observed order.

Use same-slice exact free dust p' plus instantaneous Thomson force.
Discrete ray/grid gain-normalized generator: S=sum w_u f_u;
host gain per bare depth = -sum w_n e D^-3 tr(G_u(S)-f_u).
Continuum: q_u^a=-T^ab u_b-rho_u u^a,
q_u^i=gamma E[f_i-(P/E)_ij beta_j-(rho_u/E) beta_i].
Host p'=p'_free+k photon_scale q_u^i/D_mass; D_mass=m n_normal.
beta'=(I-beta beta^T)p'/gamma, Theta/(gamma H)=3+gamma^2 beta.beta'-2 A.beta.
No endpoint secant in new atomic rate. For zero bare rate force is zero.
Retain interval-mean expansion output separately from instantaneous RHS.
Optional explicit nonuniform macro edges, finite strict increase, same endpoints.
No adaptive step controller yet.

## C5-C9: implementation/evidence
Files coupled.rs, solve.rs, recoil.rs, tilted_dust.rs, CLI, r117_coupled.rs.
New route --recombination species-sdirk --species-reference TSV
--collision sdirk2 --feedback recoil; optional --species-step-grid TSV
with eta header, steps+1 edges from 0 to duration.
Accepted stage trace coupled_stages.tsv and two replay records per macro.
231 Rust tests + 3 example tests; original 4 old runs (26 output TSVs) byte
identical. New REC baseline BE standalone one previous H history byte identical.
33 accepted physical CLI histories (5824 stages), 3 explicit rejected probes.
Twelve Bianchi families in He overlap, FLRW controls, ray/grid/continuum,
time refinements and a nonuniform power-law eta grid, plus low-z beta≈0.104.
Stage relative opacity residual <=2.842e-14; independent rebuilt rate exact
in serialized arithmetic. Depth sum defect <=2.843e-14, thermal ledger
<=9.055e-31 J/H. H/He nuclei by construction, no global PSD certificate.
Thomson force vs refined continuum moment at beta=(.3,-.2,.1), (0,0,.85):
5.030e-15 and 3.939e-15 relative. Fixed-velocity depth FD at 1e-7:
5.563e-8, 1.158e-7 relative, consistent with first-order FD.
The actual finite-stiffness coupled H window common-node RMS refinement
ratio (128/256/512) is 3.87424 xe, 3.70508 Tm, LoS 3.54237, depth 3.69913.
Low-z Bianchi I uniform LoS 4.00501, depth 3.90412; xe endpoint and RMS
ratios fluctuate, not universal second order. Nonuniform low-z I
eta_j=duration*(j/N)^1.3, N=32/64/128: common-node RMS 4.15822 xe,
3.96847 Tm; LoS 4.00342; depth 3.97627.
Stiff He standalone Tm order reduction, thermal tiny xe floor remain.
Raw scaled chemistry residual up to 6.401e-7 (not opacity residual);
FLRW exact REC matching null does not imply exact numerically coupled null.
At early He z=2800 with initial beta=(.1,.03,0), trial f_min<0 at
N=128,512,2048: -11.1144,-93.3773,-148.4953. These are rejected trial
values, not accepted solutions; no physical continuation or theorem
of nonexistence claimed. Refined probes do not rescue this closure.
Anisotropic resonance transfer beyond positive Sobolev domain remains T4.

## C10: replay and boundaries
Commands:
 cargo test --release --locked --manifest-path _rustcore/Cargo.toml
 cargo test --release --locked --manifest-path _rustcore/Cargo.toml --examples
 cargo build --release --locked --manifest-path _rustcore/Cargo.toml --example homogeneous_sky
 python3 research/r117_coupled_sdirk/smoke.py --binary _rustcore/target/release/examples/homogeneous_sky --rec /path/to/rec_bianchi/research/r116_species_thermal --out NEW_DIR
Optional --legacy-a and --legacy-b use the previous R116 run directories.
RESULTS.json includes exact commands, SHA256, stage/trajectory metrics.
Full raw outputs: ~/Downloads/bass_r117_final; regenerate from locked slices.
No native subagent tool exposed; separate numerical comparisons, self-review.
No monolithic SDIRK, stiff-uniform stability, strong early-tilt/high-l long
history, complete phase handover, or active thermal energy transfer claimed.
Next: T4 cold spectral carrier transport and conservative spectral ledger;
in parallel, study acceleration-driven nonmonotone frequency characteristics
and stiff asymptotic/Saha handling. Full frequency-resolved REC/REI remains open.
