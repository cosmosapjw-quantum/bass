# Operator binding clarification

K_s is certified for exact real linear algebra on the represented binary64
arrays in results/primary001/REPRESENTED_COEFFICIENTS.npz:
M313x313,B313x313,T314x313,P314x313.
The approximate V/Z/K are separately retained in APPROXIMATE_RESPONSE.npz,
while CERTIFICATE_ARRAYS.npz contains outward enclosures and row gains.
The input manifest binds the reused THERMO source,stored coefficient NPZ,
stored ANALYTIC_RESPONSE.npz and canonical23source/input snapshot.

The original stable M,s,T,P,p,Tvv,Beta were rebuilt once for source identity
and matched exactly. THERMO's J_s=d_outgoing314x6 remains a reused,
numerically checked primitive derivative; none of its six old columns was
recomputed. New joint direction checks use J_s*v+K_s*d on that same source.
They do not turn J_s into an interval-certified derivative.

The new infinity norm is [1.17562722922718,1.1756272292401908].
This is an incoming313 -> outgoing314 occupation/Wien-departure gain.
It does not bound the ionization observable by the same scalar; use its own
F_lo/F_hi rows and supplied incoming error box. Similarly, same-event
number and opposite-energy channels have their own units and interval rows.
No physical epsilon has been supplied to any of these conditional interfaces.

No old native K_0 norm is borrowed. The previous native representation,
THERMO stable representation and this direct stable certificate all remain
distinct historical objects with explicit source identity.
A small difference or same rounded norm between them would not itself
establish a rigorous transfer theorem.

The history payload agreement is a discrete same-source identity/domain
result. Its8exact-zero components and maximum absolute2.9030081312133234e-28
difference are retained. They are not an independent physical error estimate.
The original first figures are preserved; the corrected history panel plots
true zeros, with no fictitious1e-300 data floor.

