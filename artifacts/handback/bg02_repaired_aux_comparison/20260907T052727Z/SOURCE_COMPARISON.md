# Historical → existing candidate source comparison

This is source reading plus the frozen AUX execution reported separately, not a
new scientific candidate or general tensor admission.

| Source | Historical → candidate | Consumed path |
|---|---|---|
| StructureConstants.wl | Byte-identical | BianchiStructureConstants, locked epsilon_123=+1 |
| LeviCivitaConnection.wl | Byte-identical | Existing Koszul generator and ConnectionToLockedGammaOrder |
| ONFConnectionCurvature.wl | ONFRicciTensor uses the typed owner adapter | Existing ONFRiemannTensor still calls the existing generator/array adapter |
| EinsteinProjection.wl | Momentum delegates to owner; convention registry check added | Existing component projection and rate API |
| Authority/BG02Convention.wl | Added in R1, unchanged in repaired candidate | BG02MomentumComponent, BG02TypedCurvature, BG02PhysicalRicci |
| BG_02_CONVENTION_V2.json | Added in R1, unchanged in repaired candidate | Exact pinned convention and coefficient registry |

The convention owner is `bass`, contract `BASS_BG02_OWNER_CONVENTION_V2`, schema
2.0.0. Signature is (-,+,+,+), epsilon_123=+1, positive extrinsic curvature
K+_ab=+h_a^c h_b^d nabla_c n_d, flux q_a=-h_a^c T_cd n^d,
kappa_G=8*pi*G/c^4 and E_ab=G_ab+Lambda*g_ab-kappa_G*T_ab.
`BG02MomentumComponent` contracts owner coefficients {-1,1,-1} with
{DivergenceK,GradientK,kappa_G*qComponent}. Thus the actual source means
`-DivergenceK+GradientK-kappa_G*qComponent`. The frozen test exercises GradientK=0.
The historical implementation used `DivergenceK-GradientK-kappa_G*qComponent`.
The unchanged test therefore distinguishes the previous 2*C1 residual from 0;
the matter term was not flipped.

ONFRiemannTensor retains `canonicalLockedConnection`, which calls the same
LeviCivitaConnection generator and `ConnectionToLockedGammaOrder` permutation
{3,1,2}; the driver also tests locked-storage parity separately. ONFRicciTensor
now explicitly binds the BASS_DERIVATIVE_FIRST all-lower array and physical
Ricci slots {c,b,a,d} before contracting with IdentityMatrix[3]. Its consumed
contraction equals the previous Sum[R[[alpha,beta,gamma,alpha]],alpha] after
renaming free/dummy indices. The raw-to-BASS view sign is -1, while physical
Ricci is not negated. This run does not invoke xAct or a new connection generator.

The required executed closure is five WL files plus the owner JSON registry,
all copied directly from exact commit e404f914c0817b4c2ab3a0ff4632a8457e026fde.
The original driver has only four Get entries, so the first candidate invocation
cannot evaluate the newly owner-dependent Ricci API. repair1 adds only the
existing Authority/BG02Convention.wl import before those four files; the owner
module imports its existing pinned JSON through the original relative path.
No dependency was stubbed or replaced. Host hashes cover all six files; the
original driver's extended before/after list covers the five loaded WL files.

The candidate init.wl shows the same owner-before-geometry load order, but the
full init.wl is not executed. It and BG_02_IMPLEMENTATION_REGISTRY.json are
included under source-info as readable context only. The latter is read by
EinsteinProjectionRegistry, which this suite does not call. Other functions
present in these files (frame covariance, composition receipts, witness suites)
are not executed and their dependencies are outside this invocation's closure.

The six execution-source files are byte-identical between candidate e404f914
and its direct parent 3c36458a. e404f914's seven changed files are in the separate
native capture/launcher directory, which this task never loads or runs. The
momentum/typed-curvature amendment is inherited from R1. See source-diff.patch
for the exact historical-to-candidate source and owner changes,
candidate-all-changed-paths.txt for the complete changed-path inventory and
identity/candidate-parent-diff.txt for the direct-parent changes.
