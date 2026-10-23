# BASS background evolution: fixed-scale Einstein operator

Date: 2026-10-23 KST. Base: `797d66580448dad7fc41f2c2db31fe0eb37908bf`.
Branch: `research/background-evolution-20261023`.

## Scope and completion criteria

This unit repairs the general gamma-law material conservation and rotating-frame
flux in the existing optional Python chart, then implements a separate fixed-scale
proper-time Einstein operator. It consumes separately named matter and radiation
stress-energy moments, retaining their individual conservation equations and
balanced transfers. It uses a geodesic hypersurface-normal orthonormal frame,
signature (-,+,+,+), epsilon_123=+1, and the existing BASS commutator convention.

The generic geometry accepts all spatially homogeneous Bianchi structure data
subject to n a=0. The requested executable evidence is: eleven canonical-family
perfect-fluid trajectories; exact FLRW, Milne, Kasner and closed-dust turnaround
limits; constraint defect identities; moving-frame covariance; a positive
collisionless antipodal-beam Bianchi-I example with separate massive and massless
stresses; and an independently implemented dependency-free Rust RHS.

No new kinetic closure for general tilted/curved Boltzmann matter is supplied by
the Einstein operator. The input p_i and pi_i remain the responsibility of the
selected matter model. Existing massive FD96, photon, chemistry and NCP campaigns
are retained under their own identities; their trajectories are not rerun here.
The beam benchmark is its own exact discrete-stream model, not a replacement for
the FD96/Thomson owner. New HE36/REC125 reactive/thermal models remain separate.

## Scaling and executable contract

With fixed L_*>0 and kappa=8 pi G/c^4, use tau=ct/L_*,
h=L_* H_phys/c, s_ab=L_* sigma_phys_ab/c, n=L_* n_phys,
a=L_* a_phys, rho_i=kappa L_*^2 mu_i,
f_i=kappa L_*^2 F_i/c, p_i=kappa L_*^2 p_phys_i,
pi_i=kappa L_*^2 pi_phys_i, lambda=Lambda L_*^2.
alpha=ln(a_volume). These are fixed unit conversions, not c=1 or H-normalization.

The packed state is h; sigma(xx,yy,xy,xz,yz); n(xx,yy,zz,xy,xz,yz);
a(x,y,z); alpha; rho_i; row-major f_i. Its length is 16+4 n_sector.
Pressure scalars, STF stress tensors and energy/momentum transfers are separate
closure outputs. Positive/negative density and stress-energy realizability are
reported for the chosen material model; constraint preservation alone does not
certify them. Total transfer must vanish; an explicit diagnostic route may retain
an unbalanced transfer to measure the corresponding constraint forcing.

## Frozen acceptance gates

- Exact rational curvature and symbolic constraint polynomials: identically zero.
- Python/Rust component parity: max |a-b|/(1+max(|a|,|b|)) < 3e-13.
- Eleven-family trajectory scaled constraint residual: < 2e-8.
- Analytic flat FLRW/Milne/Kasner/closed-dust state comparison: < 2e-8 scaled.
- Rotating-frame covariance and generic derivative identities: < 5e-12 scaled.
- Stream energy from conserved momenta vs evolved sector density: < 2e-8 scaled.
- Tight/default paired stream trajectories: < 2e-8 scaled; record both solver
  settings, actual errors, and first failures without changing the gates.
- Invalid nonfinite data, malformed tensor/source and unbalanced transfer reject.

All tests refer to this finite contract. A global all-type tilted kinetic solver,
full thermal/radiative exchange, certified global convergence and production
activation are subsequent physical integration obligations.

## Source/reuse decisions

The 20 attachments are historical exact-byte inputs. The current BASS census
contains 266 branch refs (plus the origin/HEAD alias). Six related repositories
add 973 branch refs. Current provider inventories cover 109 direct Dropbox and
59 direct Drive BASS_BACKUPS objects. Personal Context returned a service error;
previous conversation text beyond the available context was not retrieved.

The recovered S12 NCP archive contains 17 completed jobs, 14 fixed manufactured
histories and 30 aggregate checks. It supersedes the older NOT_RUN description
for that workload only. The archive and all 9,901 payload hashes were read back.
The first thread-start failure and subsequent exact reuse of 16 jobs are retained.

The current user-supplied physmath workflow1.0.0 / approval0.2 and explicit full
theory-plus-coding request govern this unit. Historical single-stage stop defaults
and runtime failures are not inherited. Existing scientific scope and owner pins
are preserved. No strong no-go theorem is claimed by this unit.

## Preservation

Use create-only S0 intake, S1 verified source/results and S2 final review snapshots.
Every covered R/C stage points to the relevant snapshot, actual Git commit and
provider acknowledgement. A local file is not counted as a provider backup.
Delivery and science status remain separate. No main-branch merge is performed.
