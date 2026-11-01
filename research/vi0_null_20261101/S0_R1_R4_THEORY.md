# BASS VI₀ R1–R4: 원본 null-Liouville 기하 및 angular projector 이론 계약

Date: 2026-11-01 Asia/Seoul. Research owner cosmosapjw-quantum/bass. Immutable parent PR #311 HEAD `8d15551c2e0127ede4344f0969f8b7e251a09e3e`; parent's source PR #310 `71adfbb2948f6c23725a01dfc048e90623a9eab5`; immutable main exact SHA `9c6506e4e2087129a8b674ff10438e5db1a55c9d`.

## R1 scope and authority

One bounded *theory loop*: derive genuine forward-in-time null geodesic angular flow from BASS's class-A general tetrad and test it on already-owned 12 tilted fluid VI₀ background initial data. Derive physical frequency redshift, bolometric Liouville equation, moving-sky area weights and moving oblique scalar Kato projector including physical and gauge drift; no new Einstein source physics, no polarized screen or CMB inference. Parent `vi0_dynamics.py` Git blob checked unchanged. The numerical background is re-integrated on identical original initial seeds (not 12 newly discovered Einstein IVPs); tracer photons are newly evolved, do not gravitate. Unit Hubble prime time dτ=Hdt, parent gamma law, metric (-,+,+,+), epsilon123=+1.

## R2 literature/source

Source-owned BASS `bianchi/matter/fluid.py::dv_general`, `bianchi/charts/general.py::rhs` and `bianchi/algebra.py::structure_constants`. Historical Type-II scalar Kato `generated/rust/typeii/typeii_kato.rs` gives r=D^-4, a=w(1-v·n)/(4π), P=ra^T/(a^Tr). Hervik (2004), DOI 10.1088/0264-9381/21/9/007: tilted VI0 7D state space. Pontzen & Challinor (2007), DOI 10.1111/j.1365-2966.2007.12221.x: homogeneous tetrad photon propagation and polarization; their equation-level photon redshift supports the shear term. A literature convention never silently overrides BASS frame signs.

## R3 actual mathematical conventions

Let n_a be forward-directed photon *physical spatial unit-vector*, photon energy E measured by the hypersurface normal, and I the frequency-integrated specific intensity of an independent, collisionless, unpolarized test photon field. Let σ=HΣ and N be Hubble-normalized class-A structure matrix, A=0, with BASS antisymmetric rotating-frame W. Let S(n)=n^TΣn and U(n)=n×(Nn). Source dynamics have the same W as `vi0_dynamics.py`. Along photon phase-space characteristics, `D=Gamma(1-v·n)` for the tilted baryon frame, n^Tn=1. Initial test field I(0,n)=1 (dimensionless intensity) is a stipulated physical *tracer initial condition*, not the owner's photon radiation source and not imported CMB data.

## R4 physical candidates and falsification

1. `n' = -Σn + S(n)n - n×(Nn) + Wn`, with `d log E/dτ = -1-S(n)`.
2. Bolometric Liouville `d log I/dτ = -4(1+S)` along characteristics, since I/E⁴ is invariant.
3. For co-moving angular sky patches: `d log w/dτ = div_S²(n') = 3 S(n)`; pure frame rotation W and intrinsic class-A cross term have zero sky divergence. This is true for finite patch Jacobians; a discrete quadrature need not preserve exact 4π at finite angular resolution.
4. Exact discrete test-photon moment equation: if R=Σ wI and P_ab=Σ wI n_a n_b then `R'=-4 R - Σ:P`. This identity uses evolving w; omitting w' fails if shear-weighted intensity is nonzero.
5. With `q_i=1-v·n_i`, `r_i=(1-v²)²/q_i⁴`, `a_i=w_i q_i`, `P=ra^T/(a^Tr)`, the total P' includes v', n', w', and `K=[P',P]` remains an oblique Kato connection. Under *pure* gauge `v'=Wv`, `n'=Wn`, `w'=0` and P'_gauge=0. Physical n' does **not** cancel; it is not just Wn.

Proof basis for null direction: orthonormal-frame Koszul `2 Γ^a_(bc)=C^a_bc−C^b_ca+C^c_ab`, `C^c_ab=epsilon_abd N^dc` for class A; symmetric n^b n^c contraction gives Γ(n,n)=n×Nn. The zero-V²->1 limit of original massless gamma-law fluid's tilt-direction equation independently returns the same angular flow (excluding stiff boundary gamma=2). For sky Jacobian, F_shear=−1/2 grad_S² S, Delta_S² S=−6S (tracefree l=2), while intrinsic curvature cross and W Killing flow are divergence-free.

Negative controls: wrong sign on n×Nn, omit 3S sky weight, freeze rays while rotating v, replace oblique P by Euclidean orthogonal, conflate tracer with gravitating radiation, assume finite-grid 4π exactness. Positive controls: Minkowski/FLRW, analytic Bianchi I constant-shear, pure VI0 curvature Hamiltonian, exact Euclidean norm and energy-moment balance.

## Parent DAG unchanged

BASS upper 9/15 **scoped/source-mapped** (not total physical completion); new upper complete 0; original `G-DYN-MANIFOLD-VI0=PARTIAL`, `P-MIG-II-PREFLIGHT=OPEN`, Join J1=0/2 PASS HOLD; no production promotion or source mutation. User expressly requests no subagents; native_subagent NOT_RUN. R5–R10 are not yet claimed from this checkpoint.