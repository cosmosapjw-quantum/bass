# Local exchange ownership and geometry separation

Scope: current non-tilted homogeneous LRS I and isotropic FLRW UV tracer.
No new active Einstein source or tilted material evolution is admitted.

For each local collision stage use an orthonormal normal tetrad, signature
(-,+,+,+), x^0=ct. A positive per-H photon event vector
v=(E,c p^i) in eV/H is future causal: |c p|<=E. If a stage lasts proper
normal time dt and its H density is n_H, its local four-force density is
Q^hat(a)=n_H e/(c dt) v^hat(a), where e converts eV to joule. Thus
c Q^hat(0) is J/(m^3 s) and Q^hat(i) is N/m^3. For a signed net transfer
this positivity property need not hold; apply it to each physical edge.

The current source registry requires the following ownership:
- emitter reservoir -> ionizing UV: (+Q_em for UV, -Q_em for emitter);
- UV -> gas: (-Q_abs for UV, +Q_abs for gas);
- UV -> nonionizing radiation at the HI fit cutoff: (-Q_cut for UV,
  +Q_cut for a distinct photon sector), not physical absorption.
- gas cooling and thermal CMB input already have their own energy owners;
  a complete momentum and radiation spectrum closure for them is missing.

Binding and thermal deposition are a partition of the same absorbed
energy, not two new energy sources. The ledger's geometry work is
Liouville transport, not intersector collision transfer. In the
collisionless diagonal LRS-I lane the per-H U and axial cP satisfy
dU/d eta=-U-Sigma_ij P^ij_perH and d(cP_z)/d eta=-(1+Sigma_zz)cP_z
between boundary events. Multiplying by n_H yields the usual
normal-frame energy equation d rho/dt+4 H rho+sigma_ij pi^ij=0.
A boundary transfer carries E at the exact frequency cutoff; no
absorption or heat from the subsequent redshift is implied.

If u^a=gamma(n^a+beta^a), beta^a spatial and dimensionless, the
local energy transfer in the material tetrad is -c u_a Q^a =
gamma(c Q^hat(0)-c beta_i Q^hat(i)). The orthogonal spatial projection
(h_u)^a_b Q^b gives momentum transfer. All density, proper-clock and
momentum transformations must refer to one local event; boosting a
cumulative history across different tetrads is not a covariant operation.
The present code does not yet construct these tilted event rates.

Audit actual per-step recorded normal-frame transfer increments and
check future-causality, binding+heat partition and inventory recurrence.
For midpoint emission/absorption, n_H(mid)/dt gives the stage mean
rate. Cutoff crossing spans both geometry half steps, so only integrated
per-H transfer is assigned (not an exact local instantaneous rate).
The opposite-sign emitter and nonionizing entries are ownership
requirements, not evolved reservoirs or independent verification of their
stress tensors.

The physically signed carrier is the local four-transfer, not an
observational estimator. A body/null/measure-calibrated Q, Pi, F, G_F
cannot be inferred from this tracer alone. Active Einstein feedback
requires the emitter's actual energy and stress budget, the below-HI
photon inventory, cooling/CMB counterparts, consistent baryon thermal
and binding energies, and all matching material momentum equations.
Adding UV density to a pre-fixed total energy without compensating
owners would double count energy. HOLD.
