# Original BASS Type-II | Paired-grid moving equilibrium and Kato amplitude transport

Base owner: `cosmosapjw-quantum/bass`, immutable parent PR #322 at `5a6c28239dd30ca02cd9c8329b45d7b2c984168d`.
This is a **new theory loop R1–R10**, NOT a production activation. All proof claims have explicitly bounded domains.
BASS upper DAG stays **9/15 scoped/source-mapped**, with **0** newly completed production DAG nodes pending independent production and Stage-II gates.

## R1. Narrow scientific question and acceptance contract

Determine whether the original BASS scalar Type-II collision generator combined with the **full derivative of a paired moving angular quadrature projector** transports an electron-rest isotropic bolometric-intensity amplitude faithfully when the actual Type-II tilt `v_2(tau)` changes. Distinguish exactly:
(i) the source's *fixed-node/weight partial* `dP/dv`;
(ii) the *full paired-grid* `dP/dv`, including moving directions and solid-angle weights;
(iii) Kato `K=[Pdot,P]` (subspace intertwinement);
(iv) a separately chosen rest-intensity-amplitude-preserving connection; and
(v) the **physical** covariant Liouville term, not determined by Kato alone.

Source inputs: original BASS five-state aligned Type-II background `generated/rust/typeii/typeii_background.rs`, stored canonical 401-row `compiler/validation/typeii_fixture_canonical.json`, original `typeii_collision.rs` and `typeii_kato.rs`, parent PR #318 direct moving comparison, PR #322 real RustCore host adapter.

Conventions: metric (-,+,+,+); gamma-law fluid `gamma=1.3` for the original fixture (NOT Lorentz gamma), `v=v2` with `|v|<1`, `Gamma=(1-v^2)^(-1/2)` Lorentz factor. Dimensionless WE-normalized Type-II background time `d tau=H dt`. Normal-frame direction `n`; electron-rest direction `e` with `m=e_y`; Doppler `D=Gamma(1-v n_y)`; unpolarized *bolometric intensity* `I_e=D^4 I_n`; `dOmega_e=dOmega_n / D^2`. Source generator owns one factor `q=1-v n_y`.  No second Doppler factor, no original Saha-history attribution, no polarization/P8, no backreaction.

Domains: paired fixed electron-rest quadrature `(e_i,W_i)` with `W_i>0`, `sum_i W_i=4 pi`, `sum_i W_i m_i=0`; second-order exactness when invoking exact Thomson null/conservation. The normal-frame quadrature is the Lorentz transform of that rest grid; `N1>0` and positive Type-II Gauss matter constraint on the background.

Success conditions: derive the exact pair `r(v),a(v)` and `s=a^Tr`; derive Kato versus amplitude-preserving transport and a sharp counterexample with finite `v`; verify against original 401-state tilt history and original source code; separate exact results from scientific interpretation. One hostile self-review and objective small numerical check. No global strong no-go or production claim.

**R1 decision:** original source-bound, mathematical, scalar moving-grid theory; `DAG=9/15`; `StageII=11/11 historical only`; `J1=0/2 full pass HOLD`. Checkpoint via Git and independently hashed local archive after the stage.

## R2. Primary literature and source reuse

**Original source, not a new formula:** `generated/rust/typeii/typeii_collision.rs` constructs the finite-tilt scalar Thomson generator with `D=Gamma(1-v n_y)`, rest angles `e`, transformed bolometric intensity `D^4 y`, rest angular weights `w_n/D^2`, Thomson kernel `(3/16pi)(1+(e_i.e_j)^2)`, and a *single* output relative-flux `q=1-v n_y`. Source lineages are locked by `research/typeii_host_preflight_20261101/SOURCE_LOCK.json`; parent #322 compiled actual Type-II original RHS on all 401 canonical states.

**Original low-rank source:** `generated/rust/typeii/typeii_kato.rs` uses `r_i=D_i^-4`, `a_i=w_i q_i/(4pi)`, `P=r a^T/(a^Tr)`, `K=[Pdot,P]`. Its `rv_i=4r_i(mu_i/q_i-Gamma^2 v)` and `av_i=-w_i mu_i/(4pi)` are **partial derivatives at fixed normal nodes and weights**. Thus they are correct for its fixed-frame definition, not automatically for a family of moving paired grids.

**Source-owned paired geometry:** `research/typeii_stageii_preflight_20261101/source/frozen_uniformization.py::paired` uses inverse aberration of a fixed rest grid, normal weights `w_n=w_e D^2`, and validates forward aberration. `research/typeii_aem2_compare_20261101/source/replay_from_original_fixture.py::pv` explicitly differentiates the **full paired `P(v)`** by complex-step when `mode=paired`, whereas its fixed-grid branch uses the partial analytic derivative. These are two explicitly different established source computational paths. The already published 96-row comparison cannot be reclassified here without its full operator and frame contract.

**Foundational literature, used only in supported scope:**
- Davis & Gammie, *Covariant Radiative Transfer for Black Hole Spacetimes*, ApJ **888** 94 (2020), DOI https://doi.org/10.3847/1538-4357/ab5950: tetrad-frame radiative transfer and conservative invariant phase-space treatment; motivates handling the full frame transformation and frequency transport, not a claim of Type-II-specific results.
- Blanes, Casas, Oteo & Ros, *The Magnus expansion and some of its applications*, Phys. Rep. **470**, 151–238 (2009), https://arxiv.org/abs/0810.5488: time-dependent matrix evolutions and commutators; relevant to distinguishing instantaneous frozen semigroups from nonautonomous evolution.
- Joye, *General Adiabatic Evolution with a Gap Condition*, Commun. Math. Phys. **275** (2007), https://arxiv.org/abs/math-ph/0608059: spectral projections and intertwinement in adiabatic evolution; **not** a proof that a Kato gauge fixes a particular physical amplitude.
- Pitrou, *The radiative transfer at second order: a full treatment of the Boltzmann equation with polarization*, https://www2.iap.fr/users/pitrou/publi/compton10.pdf: scope warning that scalar bolometric intensity must not be promoted to polarized/frequency-resolved photon-number conservation.

**Dependency status:** `TypeII=gamma-law five-state, prescribed tilt v_2(tau)`; original `401/401` fixture source from owner is accepted as source-conditioned trajectory, not a native Saha/recombination physical receipt. Prior frozen scalar Metzler/Poisson proof is valid only when *the same discrete C* satisfies `Cr=0` and `a^TC=0`; moving `a(t)` creates a separate transport question.

**R2 decision:** primary-source and source-code mapping complete for the new scope; BASS upper DAG **9/15**, new full nodes **0**.

## R3. Scope/convention cross-check (source, derivation and hypothesis separate)

On the *paired* grid the fixed rest-frame directions `e_i` and positive weights `W_i` are independent of `v`, while the normal directions `n_i(v)` and weights `w_i(v)` are **not**. In the original collision generator `y_i` denotes bolometric intensity in the normal tetrad. This is **not** a frequency-resolved photon occupation number. The source `a(v)^T y` is a left invariant of an **instantaneously frozen** eligible collision matrix, not by itself the covariant photon number of a time-dependent universe.

The exact rest quadrature criteria for the unpolarized Thomson kernel are `sum W=4pi` and `sum W e_i e_i^T = (4pi/3) I_3`. For the amplitude theorem additionally `sum W m_i=0`, already implied by symmetric first moment of the six-axis/Lebedev26 grids. Positivity of `W`, `q` and `D` gives Metzler offdiagonal entries. This implies `C(v) r(v)=0` and `a(v)^T C(v)=0` at each v for the paired family; it does NOT give `d(a(v)^T y)/dtau=0` when v varies.

Background fluid `gamma=1.3` and Lorentz `Gamma(v)=(1-v^2)^(-1/2)` are distinct. Time derivative below is `d/dtau` with `d tau=H dt`; physical `n_e sigma_T c/H` is a *separately sourced positive scalar rate*, not supplied by the gamma-law fluid. Existing 401-record opacity is a 3-anchor log-quadratic proxy only.

Core question admits **no assumption** that the original fixed-frame generated Kato derivative was coded incorrectly: the fixed-grid partial expression is valid for its stated arguments. The new proof addresses its use after a coordinate-dependent **paired** angular transformation. The previous PR #318 Python comparison computes total paired `dP/dv` by complex-step, so its existing numerical claims are not refuted by this distinction.

Kato's `[Pdot,P]` intertwines `P(tau)`, but amplitude conservation/normalization is a second choice. Merely transporting a mathematically moving equilibrium subspace is not the same as solving the physical cosmological Liouville equation, which also depends on shear, gravitational redshift, angular advection, and the chosen intensity/frequency moment.

**R3 verdict:** source facts distinguished from upcoming novel direct algebra; `DAG 9/15`, `0` new upper nodes.

## R4. Divergent constructive candidate connections

Let `P(v)=r(v)a(v)^T/s(v)`, `s(v)=a(v)^T r(v)>0`, and `C(v)r=0=a^T C(v)`. Evaluate three **different mathematical transports** of the same source:

1. **A | Kato geometric subspace connection:** `G_A=alpha nu(tau) C(v)+K(v)`, `K=[Pdot,P]`, full time derivative including `n(v),w(v)`. Guaranteed `P(tau) U_A(tau,tau0)=U_A(tau,tau0) P(tau0)` if the finite-dimensional smooth equation is solved exactly. This does **not** fix how the amplitude of `r(v)` evolves.

2. **B | Rest-isotropic-amplitude calibration:** `G_B=alpha nu C + K + lambda(tau) P`, `lambda=(a^T rdot)/s`. For any scalar `c` initial `y=c r(v0)`, the path `y=c r(v(tau))` is an exact solution (the collision term vanishes). If `s` is constant and `a^TC=0`, then `a(tau)^T y` is also constant for **all** solutions of `G_B`. This is a choice of center mode/gauge, not by itself a physical free-streaming law. For `s\ne constant` the two normalization goals are distinct.

3. **C | Rest-label frame-pullback:** `G_C=alpha nu C + diag(rdot_i/r_i)` on the *specific* paired rest-labelled bolometric vector. Its geometric term gives `y_i=r_i(v)J_i` for constant (possibly anisotropic) rest-frame `J_i` if collisions vanish. The full covariant Liouville equation instead introduces real geometric redshift/shear/angular evolution of `J_i`, so `G_C` alone is not its replacement. Unlike B, the diagonal term is generally different off the equilibrium subspace.

Distinguishing diagnostic: for an isolated tilt change from `v0=0` to `v=0.2` and a symmetric paired grid, candidate A predicts the rest-intensity amplitude ratio `(1-v^2)^2=0.9216`, while B and C give exactly `1` for initially isotropic rest intensity. This is a **finite, falsifiable mathematical discrepancy**, not a production or observational prediction.

Core decision for R5: derive the analytic paired-grid `r,a,s,rdot,adot,K` and both propagation laws, quantify the discrepancy on the original 401-state Type-II tilt history. Keep candidate C as the physical-coordinate comparator rather than silently labeling B as covariant transport.

**R4**: 3 explicit candidates, one distinguishing case; `DAG 9/15`, `0` new full upper nodes.
