# G1A: positive homogeneous kinetic measures in a fixed-scale Bianchi frame

## Scope and source provenance

This is a new collisionless finite-measure closure for the unchanged PR182 Einstein
operator, not a collision, emission, ionization or production solver. The source
normalization reuses the original BASS `freestream.py` finite nodes and PR168's
reference-density normalization. General spatially homogeneous Vlasov equations,
mass-shell integration and normal-frame conservation are established background;
the explicit convention-matched packet equations and their connection to this
particular free-evolution implementation are derived below.

Primary background: van Elst and Uggla, arXiv:gr-qc/9603026, and Nungesser et al.,
arXiv:1305.7347, sections II-III. The latter's parsed original PDF was consulted;
web screenshot retrieval failed, so no new visual PDF-transcription certification
is claimed. The saved source locks, rather than bibliographic metadata, bind the
reused project code.

## Variables, units and assumptions

Use signature (-,+,+,+), epsilon_123=+1, geodesic hypersurface-normal frame, and
homogeneous frame components. The spatial structure vector a is NOT the acceleration
of that normal congruence. Define kappa=8*pi*G/c^4 and two fixed positive constants
L_* (length) and P_* (momentum). Keep c explicitly:

    tau = c t / L_*
    h = L_* H_phys / c, s = L_* sigma_phys / c
    n = L_* n_geom, a = L_* a_geom
    k = p_phys / P_*, m = m_phys c / P_*, E = sqrt(m^2 + k.k).

Physical particle energy is c P_* E. A packet weight w is kappa L_*^2 c P_*
times its proper normal-frame number density. Thus

    rho = sum w E,
    f_i = sum w k_i,
    P_ij = sum w k_i k_j/E,
    p = tr(P)/3, pi = P-p I

are exactly the core's rho=kappa L_*^2 mu, f=kappa L_*^2 F/c and scaled pressure.
No Hubble-normalized time is introduced. The local existence domain is finite
geometry with E>0 and representable positive weights. Singular cosmological
endpoints and a massless particle with k=0 are outside that domain.

## Geodesic force from the commutator

For [e_i,e_j]=C^z_ij e_z,

    C^z_ij = epsilon_ijl n_lz + a_i delta_jz - a_j delta_iz,
    Gamma^z_ij = (C^z_ij - C^i_jz + C^j_zi)/2.

The spatial geodesic term is -Gamma^z_ij k_i k_j/E. Substituting the commutator,
using symmetric n, gives the computational form

    k' = -h k - s k + R cross k
         + ((a.k) k - a (k.k) - k cross(n k))/E.                 (1)

R is the core's commutator-frame angular velocity: vectors receive +R cross k.
The spatial force in the last line is orthogonal to k. The frame rotation is also
orthogonal, hence

    E' = -(h k.k + k.s.k)/E.                                   (2)

This calculation is checked against a separately assembled explicit Koszul tensor
in eight random geometric configurations. Off-Jacobi configurations are algebraic
checks only; physical homogeneous initial data require n a=0.

## Momentum measure and the Class-B weight

Let V(k) denote (1). Scalar Vlasov transport is partial_tau f0+V.grad_k f0=0.
For the measure dmu=f0 d^3k this is equivalently

    partial_tau mu + div_k(V mu) = (div_k V) mu.

The weak finite-measure representation is sum_j w_j delta(k-k_j). Its characteristic
weights therefore satisfy w'=w div_k V, not a universally fixed comoving weight.
Direct differentiation gives

    div_k V = -3h + 2 a.k/E,
    (log w)' = -3h + 2 a.k/E.                                  (3)

For the spatial numerator A=(a.k)k-a k^2-k cross(nk), k.A=0. Its divergence is
2a.k: the first two terms give 4a.k-2a.k; the symmetric-n cross term has zero
divergence. The derivative of 1/E contributes zero because k.A=0. Shear has
zero trace and rotation is antisymmetric. This proves (3) without assuming small
shear, small tilt, a diagonal frame, expansion, or an equation of state.

Class A has a=0 and w exp(3alpha) constant. In Class B the normal-frame comoving
number can vary because the homogeneous number current has nonzero covariant
spatial divergence. It is not particle creation. The normal number equation is
N'+3hN=2a.J_N, J_N=sum w k/E.

## Exact moment identities

Using (1)-(3) in the derivative of each packet moment and summing yields

    rho' = -3h(rho+p) + 2a.f - s:pi,                            (4)
    f' = -4h f - s f + 3pi a + epsilon(n,pi) + R cross f,        (5)
    epsilon(n,pi)_i = epsilon_ijl n_jd pi_dl.

For example the spatial contribution to (5) is
3P a - tr(P) a - sum w k cross(nk)/E. Its first two terms are 3pi a;
the last term is epsilon(n,pi). Isotropic pieces cancel because n is symmetric.
A separate Wolfram kernel returned exact residuals {0,0,{0,0,0}} for momentum
volume divergence, (4), and (5), with arbitrary real geometry and m>0. The massless
case extends on the regular E>0 domain. Saved numerical tests include both m=0
and positive masses. This is an algebraic identity, not a theorem of global
Einstein-Vlasov regularity or finite-grid convergence to every smooth distribution.

## Positive stress and local boosts

Positive w and E imply P is positive semidefinite, |f|<=rho and
rho-tr(P)=sum w m^2/E>=0. These are direct finite-sum statements. The integrator
uses log weights, rejects underflow/overflow, and does not clip negative populations.

For a local active bulk-to-normal boost beta=v/c, |beta|<1, transform p4=(E,k)
by B with B00=gamma, B0i=Bi0=gamma beta_i and
Bij=delta_ij+gamma^2 beta_i beta_j/(gamma+1). Invariance of d^3k/E requires

    k -> (B p4)_spatial,
    w -> w (B p4)_0/E.                                         (6)

Then T=sum (w/E) p4 p4^T transforms exactly as B T B^T. Keeping weights fixed
while boosting momenta violates this identity. The numerical tests cover speeds
0,1e-8,0.3,0.8 and their inverses, not arbitrarily extreme rapidities.
A local boost initializes a distribution; it does NOT transform a Bianchi geometry
into a globally tilted solution. Hamiltonian/Codazzi/Jacobi constraints must still
hold. The new histories use explicitly constraint-matched nonzero sector fluxes,
not an observer endpoint boost. A multi-stream kinetic sector is not automatically
a single perfect fluid with a specified rest-frame gamma-law.

## Exact finite-node reuse and its boundary

`fd_packets` uses all 96*24*24=55,296 original nodes, including tiny positive weights.
For alpha and diagonal beta with tr beta=0,

    k = exp(-alpha) q nhat exp(-beta),
    w = dq q^2 f_FD(q) W_angle [1+A P2(n_z)+C(n_x^2-n_y^2)]
        exp(-3alpha)/(4pi sum dq q^2 f_FD(q) sqrt(m^2+q^2)).      (7)

The imported original source bytes and reference normalization are unchanged.
Massive m in [3,1e5], alpha in [0,ln(21/5)], |beta_i|<=1 and the positive angular
source domain follow PR168. m=0 is explicitly a separate massless FD source,
not a Planck CMB spectrum. The inherited clipped exponential is admitted as a
finite-node measure; no exact continuum-tail claim is made about that implementation.
This unit verifies same-node moments and six new local derivative checks, not a
55,296-particle cosmological campaign or smooth FD96 convergence in curved space.

## Why both constraint and kinetic-closure monitors are necessary

The unchanged core evolves rho and f using (4)-(5), while pressure/pi are supplied
by the packet closure. A bug in packet evolution can therefore leave the abstract
core constraints small even though its independently evolved rho/f no longer equal
sum wE/sum wk. Monitor both the independent moment mismatch and the constraints
recomputed after replacing core rho/f by packet moments.

The deliberately mutated Bianchi-V run removes the 2a.k/E term from (3). Its core
constraint remains about 4.9e-12, while the packet-derived constraint and moment
mismatch reach about 7.95e-3 and 1.36e-2. This is a concrete finite counterexample
to a constraint-only validation criterion, not a defect attributed to the unchanged
Einstein RHS. The correct microscopic and core equations agree within the frozen
finite tolerances. G1B must keep both monitors during smooth-source refinement.
