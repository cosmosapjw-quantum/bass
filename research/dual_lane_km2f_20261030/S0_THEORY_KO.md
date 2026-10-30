# BASS KM-2F | Bianchi I Einstein constraints and original polarized photon–cold electron feedback

**2026-10-30. One bounded physics unit.** Immutable parent PR276 HEAD `58277dab1af10850ff0a86c74673743b2c0a8a5a`. Upper DAG **9/15**, KM-2 **PARTIAL**, zero new completed upper nodes. Original photon source, P8 Thomson collision, KM1 geometry and KM2E reciprocal cold electron model are read-only.

## Why the old KM2E initial data cannot be used unchanged

The homogeneous Bianchi-I Einstein momentum constraint is **total normal-frame energy flux q_total=0**. The predecessor fixed electron initial velocity beta=(.3,-.4,.2) yields nonzero total flux, and changing H alone cannot repair this constraint. Preserve the exact original polarized photon initial distribution and choose electron initial beta uniquely as `beta_e0=-q_gamma0/R_e0`. Select the positive expanding H0 from `3H0²=kappa(rho_gamma0+R_e0)+sigma0²`. This is a *new constrained GR initial-value problem* and **not** byte-identical predecessor matter initial data.

The original photon source gives `rho_gamma0=39.01110262768746`, `q_gamma0≈(14.49610381,-18.92212948,9.43499472)`. At the predecessor synthetic electron energy ratio .75, the constraint would require `|beta_e0|≈.876`, for which positive angular grids ntheta8–16 exhibit large original finite-quadrature force errors. For this distinct Einstein pilot choose `R_e0/rho_gamma0=3.0`, allowing `|beta_e0|≈.219`, and `kappa=8piG*rho_unit*Tstar²=.003`, giving `H0≈.40777`. Neither synthetic normalization represents a calibrated cosmic electron abundance or measured G; original photon angular source remains unchanged.

## Einstein–Thomson–cold dust on non-diagonal Bianchi I

Metric signature (-,+,+,+), Lambda=0, normal proper `u=t/Tstar`. Set `B=H I+sigma`, tracefree symmetric sigma, `sigma²=tr(sigma²)/2`. The original KM1 photon direction, redshift, normal ray weights and parallel screen depend on the genuinely time-dependent coframe `A`:

`A'=-B A`, `n=A n0/|A n0|`, `mu=|A n0|`, `w=w0 det(A)/mu³`, `E'=(n' n^T-n n'^T)E`.

The full original real Hermitian P8 photon carrier evolves by original KM1 streaming plus original KM2A finite-beta instantaneous Thomson. Electrons are pressureless cold dust with `p=gamma beta`, `gamma=sqrt(1+p²)`, `zeta=n_lab/n_lab0`, `R_e=M0 zeta gamma`, `Q_e=M0 zeta p`, `P_e=R_e beta beta^T`, `nu_rest=nu0 zeta gamma0/gamma`. Their reciprocal force is the original covariant `F_gamma`:

`zeta'=-3H zeta`, `p'=-B p-F_gamma_sp/(M0 zeta)`.

The full Einstein Bianchi I equations for `rho=rho_gamma+R_e`, `P=P_gamma+P_e`, `p_iso=tr(P)/3`, `pi=P-p_iso I` are

`H'=-kappa(rho+p_iso)/2-sigma²`, `sigma'=-3H sigma+kappa pi`.

Constraints: `C_H=3H²-kappa rho-sigma²=0` and `q_total=q_gamma+Q_e=0`. Sigma is stored in five independent tracefree components. The 3x3 photon A and 2-component ray screens are evolved in the same IVP, rather than borrowed from an incompatible prescribed geometry.

## Consistency identities and useful new physics

The actual original positive angular P8 collision force differs slightly from the separately covariant photon force: `deltaF=F_raw_P8-F_cov`. This is **measured**, not projected to zero. Total moment balances are `rho'=-3H(rho+p_iso)-sigma:pi+deltaF0` and `q' = -(4H I+sigma)q+deltaF_sp`. Thus

`C_H'=-kappa deltaF0`,

and the Bianchi-I curvature scalar obeys `R_geometry-R_matter=4C_H`, with `R_geometry=6H'+12H²+2sigma²`, `R_matter=kappa(rho-3p_iso)`. Independently, electron number dilution and the coframe obey `zeta=det(A)` and the shear forcing obeys `d(sigma/zeta)/du=kappa pi/zeta`. These are measurable integral checks, not extra source projections.

## Executable checks and claim ceiling

Fixed original source and seed photon beta=(.3,-.4,.2); *new* physically constrained electron beta from q cancellation, positive H from Hamiltonian. GL ntheta12/16, nphi=2ntheta, `u in [0,.25]`, `nu0=1.3`, `kappa=.003`, `R_e0/rho_gamma0=3.0`. Generate actual co-evolving H, sigma, spatial metric, photon+electron E/Q/P, full polarized angular source, electron rest density and optical rate, raw quadrature force, 5 physical epochs and 24-point independent integration of constraints and shear sourcing. Separately solve complete Einstein–photon–electron IVPs in p and beta matter variables and demand agreement; check Minkowski (`kappa=0`, `sigma0=0`) total E,Q conservation, initial-incompatible H rejection, positive spatial metric, timelike beta and source byte integrity.

Immutable source Git blobs: KM2C `curved_tilt.py=05aade3aab7e9a32c11608882c943e4d3cb6f379`, KM2A `tilted_collision.py=92660768f4719d78261fed1cb44f186d2821629d`, KM1 `source_memory.py=9d500e36fefaa4ddc22300a2f03d9eb9cfe98403`, KM2D `accelerating_tilt.py=b599d3842e843d8de1de1499b73e6849374bf8f8`, KM2E `coupled_electron_photon.py=12fbce8109fc07b1fbf60d9a066d8aa1c57ea9c1`.

Claim ceiling: a **numerically tested homogeneous Einstein-Bianchi-I cold-electron + original polarized photon pilot**, not frequency-domain Compton recoil, realistic electron thermodynamics, plasma ions, inhomogeneous Einstein–Boltzmann, rigorous continuum quadrature, production Rust or full formal program verification. Native subagents and distinct-author R6/C9 NOT_RUN. `production_ready=false`, `merge_ready=false`, `auto_next=false`. STOP_AFTER_ONE_BOUNDED_UNIT.
