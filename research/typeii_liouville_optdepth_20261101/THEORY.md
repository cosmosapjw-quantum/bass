# R1: Original Type-II Liouville and Thomson optical-depth science contract
2026-11-01 KST; parent PR #324 immutable HEAD `b5a64ff1be8038beb5ef339715ecd9af03a428c2`. Original main `9c6506e4e2087129a8b674ff10438e5db1a55c9d`.
Question: reconstruct and **execute** the exact source-owned Type-II photon characteristic with normal congruence shear, Bianchi II curvature and triad gauge, then couple only to a source-owned cold-Thomson **line-of-sight optical depth** with correct electron density frame. Deliver actual 401-background-ray numerical data, compiled original Rust source oracle, and reproducible same-source independent checks. No production default dispatch, no full polarized Boltzmann hierarchy, no native Saha/HyRec equivalence, no CMB prediction.
Convention: metric (-,+,+,+); c retained; frame normal observer with Hubble-normalized time `d tau_H=H dt`, E measured by the normal observer; `Sigma`, `N1`, `R2` dimensionless in `tau_H`; gamma-law fluid `gamma=1.3` not Lorentz `Gamma=(1-v2^2)^(-1/2)`. Original scalar generated Thomson `q=1-v2*n_y` occurs exactly once inside the collision source. Optical-depth line rate is conditional on electron-rest proper density and on identifying electron velocity with v2.
Source authorities: `runtime/rust/typeii/typeii_polarized_liouville.rs`; `generated/rust/typeii/typeii_polarized.rs`; `runtime/rust/typeii/typeii_physical_guard.rs`; `bianchi/rays/geodesics.py`; `bianchi/q/electron_rate.py`; `generated/rust/typeii/typeii_collision.rs`; `compiler/validation/typeii_fixture_canonical.json`. Require Git objects identical to original main and PR #324 checked before promotion. Reuse existing Kato amplitude theorem as a mathematical comparator only.
Stage admission: Theory R1–R10 and coding C1–C10 are separately scoped; full production DAG BASS_UPPER=9/15 scoped/source-mapped; NEW_FULL_UPPER_NODES=0; STAGEII=11/11 historical current canonical NOT_RECOVERED; P_MIG_II_PREFLIGHT PARTIAL, G_DYN_MANIFOLD_VI0 PARTIAL, Join J1 0/2 full PASS HOLD, production=false, merge=false, auto_next=false.

## R2: Sources and literature (source-locked)
Original `runtime/rust/typeii/typeii_polarized_liouville.rs` owns the five-state→`HomogeneousRayBackground` map, `liouville_coefficients` and reference characteristic. In the Type-II gauge it uses `Sigma13raw=sqrt(3)Sigma13`, `R_y=Sigma13raw`, `N=diag(N1,0,0)`, expansion=1. `bianchi/rays/geodesics.py::photon_rhs` is a second original implementation of the tetrad photon geodesic; `bianchi/rays/frame.py::P_double` defines `P=n×(Nn)` for Class A. Original `bianchi/q/electron_rate.py::ElectronCollisionContext` specifies electron **rest proper density**, SI opacity `n_e sigma_T c`, normal-time relative-flux `D=E_e/E_n`, and Hubble normalization. Original `generated/rust/typeii/typeii_collision.rs` owns a single factor `q=1-v n_y` and separate bolometric intensity `D^4`.
Literature: Pontzen & Challinor, MNRAS 380 (2007) 1387, https://arxiv.org/abs/0706.2075, gives tetrad photon propagation and Boltzmann hierarchy **near FRW**; Sung & Coles JCAP 2011(06)036, https://arxiv.org/abs/1004.0957, geodesic curvature/shear/rotation; Davis & Gammie ApJ 888 94 (2020), DOI 10.3847/1538-4357/ab5950, covariant radiative transfer and `I_nu/nu^3` invariant. They ground conventions and limitations; exact finite-tilt Type-II formula authority remains the pinned BASS sources, NOT a transported near-FRW theorem.

## R3: Claims, units and source-vs-model consistency
The Type-II background is dimensionless (time `tau_H` with `d tau_H=Hdt`), `Sigma` and `N` are H-normalized. `gamma=1.3` is the fluid pressure parameter, not Lorentz `Gamma(v)`. Photons follow the **normal tetrad** for geometric Liouville while electron motion is a separate field; identify `beta_e= v2 e_y` only in a deliberately source-conditional comparator.
In an orthonormal normal frame, `d log E_normal/dtau_H=-(1+Sigma_nn)` and the source's `R_y=sqrt(3)Sigma13` represents the co-rotating Type-II diagonal-N gauge. Scalar bolometric intensity transforms as `I_e=D^4 I_n`, whereas frequency-specific `I_nu/nu^3` is invariant. A bolometric intensity quadrature alone is NOT photon-number conservation. Angular advection is not captured by a diagonal `-4(1+Sigma_nn)` multiplication operator.
The electron-rest proper density `n_e^rest` and its normal-measured density `n_e^normal=Gamma n_e^rest` are distinct. The owner `electron_rate.py` uses `n_e^rest sigma_T c D`, where `D=Gamma(1-v n_y)`. Because `typeii_collision.rs` already contains `q=(1-v n_y)`, the compatible direction-independent prefactor with **proper** density is `Gamma n_e^rest sigma_T c/H`. Previous shorthand `nu_tau=n_e sigma_T c/H` is legitimate with `n_e^normal`; ambiguous `n_e` must not be silently interpreted as proper density. No evidence that the prior source's three-anchor opacity proxy is native Saha or a proper-density history.

## R4: Constructive candidates, selection
A. **Source-exact normal-tetrad characteristic + proper-density optical depth:** integrate `(n,lnE,lnI,tau_T)` driven by original Type-II `Sigma,N,R`, `dlnI=4dlnE`, `d tau_T/dtau_H=nu_rest Gamma(1-v n_y)`. Choose `nu_rest=1` for an unambiguous unit-proper-rate *geometric diagnostic*, with optionally the existing 3-anchor proxy as a clearly conditional secondary screen. This is the primary selected theory/coding target.
B. Fixed-grid angular `A=-4(1+Sigma_nn)` with no direction remapping. Valid only as a restricted multiplicative approximation; its omission of `dot n` is directly testable and not an acceptable replacement for source-owned full Liouville characteristics.
C. Moving-equilibrium Kato `K=[Pdot,P]` or center correction `K+lambda P` from PR #324. These are mathematical collision-equilibrium transports, NOT the geodesic Liouville operator; use solely as a diagnostic against inappropriate substitution.
Representative strict falsifier: at fixed nonzero `N1` and `Sigma=R=0`, source Type-II spatial curvature produces nonzero `dot n` except certain directions, while the frozen angular multiplicative A cannot. At `v2!=0`, replacing `Gamma q` by `q` changes the rate (even at n_y=0); replacing it by `Gamma q^2` double-counts flux.

## R5: Exact source-matched tetrad Liouville and opacity theorem (derived)
Fix the orthonormal normal tetrad with signature (-,+,+,+). Let \(\tau_H=\int H\,dt\) and the five BASS Type-II stored background coordinates \((\Sigma_+,\Sigma_-,\Sigma_{13},N_1,v_2)\) be the prescribed gamma-law \(1.3\) source. In normal gauge:
\[
\Sigma=\begin{pmatrix}
-2\Sigma_+ &0&\sqrt3\Sigma_{13}\\0&\Sigma_++\sqrt3\Sigma_-&0\\
\sqrt3\Sigma_{13}&0&\Sigma_+-\sqrt3\Sigma_-
\end{pmatrix},\quad
N=\mathrm{diag}(N_1,0,0),\quad
R=(0,\sqrt3\Sigma_{13},0),\quad A=0.
\]
These fields and \(R_y\) are transcribed from the immutable source
\`runtime/rust/typeii/typeii_polarized_liouville.rs::typeii_background_from_state\`.

For a forward null geodesic \(p^\mu=E(u^\mu+n^a e_a^\mu)\) with \(n^2=1\), the original BASS orthonormal connection yields
\[
\boxed{\frac{d\ln E}{d\tau_H}=-[1+\Sigma_{ab}n^a n^b]},\qquad
\boxed{\frac{dn}{d\tau_H}=-(\Sigma n-\Sigma_{nn}n)+R\times n-n\times(Nn)}.
\]
Here \(n\times(Nn)=(0,N_1n_x n_z,-N_1n_x n_y)\). The source's alternative expression with
\(w=R+Nn-\tfrac12\mathrm{tr}(N)n\), \(\omega=w+n\times[-\Sigma n+\Sigma_{nn}n]\),
and \(\dot n=\omega\times n\) is exactly equivalent, because \((n\times s)\times n=s-(n\cdot s)n=s\) for tangent \(s\) and \((Nn)\times n=-n\times(Nn)\).
Thus \(d(n^2)/d\tau_H=0\) exactly, including nonzero Type-II \(N_1\) and off-diagonal shear.
The frequency-specific Liouville occupation \(f\) is constant along collisionless geodesics.
For frequency-integrated bolometric intensity with collisionless, achromatic emission-free transport,
\[
\boxed{\frac{d\ln I_n}{d\tau_H}=4\frac{d\ln E}{d\tau_H}
=-4(1+\Sigma_{nn})},\qquad I_n/I_n(0)=(E/E_0)^4.
\]
This is a **characteristic** equation: its \(\dot n\neq0\) must accompany the angular dependence; a diagonal angular multiplication operator without directional advection is not the complete Liouville PDE.

If the electrons have normal-frame velocity \(\beta_e=v_2 e_y\) (an explicit conditional identification),
\[
q=1-v_2 n_y,\quad \Gamma=(1-v_2^2)^{-1/2},\quad D=\Gamma q,\quad
E_e=D E_n,\quad I_e=D^4I_n.
\]
The exact total normal-ray derivative, including the real curvature/shear angular drift, is
\[
\boxed{\frac{d\ln D}{d\tau_H}
=\frac{v_2v_2'}{1-v_2^2}
-\frac{v_2'n_y+v_2n_y'}{1-v_2n_y}},
\quad
\boxed{\frac{d\ln E_e}{d\tau_H}
=-1-\Sigma_{nn}+\frac{d\ln D}{d\tau_H}}.
\]
The \(v_2n_y'\) term is a concrete new correction absent from the pure moving-projection Kato amplitude connection. It is **not** an error in Kato; the latter has a different mathematical job. Wolfram directly checked the full chain derivative of \(\ln D\) and the Type-II curvature cross product with zero symbolic residual.

For electron-rest proper density \(n_e^{\mathrm{rest}}[\mathrm{m}^{-3}]\), Thomson cross section \(\sigma_T[\mathrm{m}^2]\) and \(c[\mathrm{m/s}]\),
\[
\nu_*=\frac{n_e^{\mathrm{rest}}\sigma_Tc}{H},\qquad
\boxed{\frac{d\mathcal T}{d\tau_H}=\nu_*\Gamma q}\ge0
\quad(|v_2|<1,H>0,n_e^{\mathrm{rest}}\ge0).
\]
Original \`generated/rust/typeii/typeii_collision.rs\` already owns a single \(q\); its compatible **scalar** prefactor with proper density is \(\nu_*\Gamma\), or equivalently \((n_e^{\mathrm{normal}}\sigma_Tc/H)\) with \(n_e^{\mathrm{normal}}=\Gamma n_e^{\mathrm{rest}}\). Neither \(q\) nor \(\Gamma\) may be silently counted twice.
The physical rest-density history is NOT provided by the original 3-anchor opacity proxy. The primary ray diagnostic sets \(\nu_*=1\) per Hubble time and separately labels any use of the historic opacity proxy as conditional.

Limiting checks: zero shear/curvature/rotation gives \(n'=0,E/E_0=e^{-\Delta\tau_H}, I/I_0=e^{-4\Delta\tau_H}\). Zero tilt gives \(D=q=1\). \(N_1=0\) removes the spatial curvature term (but is outside the earlier strictly \(N_1>0\) 4D chart). Small tilt gives \(\Gamma=1+\tfrac12v_2^2+O(v_2^4)\); omission of \(\Gamma\) is a finite-\(v_2\) normalization mismatch, not a linear-order one. These statements refer to source-normalized time, not cosmological seconds.

## R6: Same-author hostile mathematical review, finite checks to implement
The critical sign is `-n×(Nn)` in the null-direction ODE. A sign reversal would move Bianchi-II angular rays the wrong way although `|n|=1` would still be conserved, so unit-norm preservation alone is insufficient; a direct source-equation numerical comparison is compulsory.
At finite v, if `n_y=0`, the true normal-time proper-density factor is `Gamma`, whereas using only generated internal `q=1` would undercount. The wrong external `q` factor would instead change `Gamma q` to `Gamma q^2`. These errors are distinguishable by comparing opposite directions `n_y=+1` and `n_y=-1` and perpendicular directions.
The original finite-v collision operator's `D^4` bolometric intensity conversion is not a collision-rate factor. A source interpolation of five-state Einstein background is not a new integrator for coupled radiation feedback; even a perfect null geodesic pass cannot justify a self-consistent CMB spectrum. `n_e^{rest}` requires explicit provenance; an opacity proxy is not the original physical electron history. The reference Liouville module's source-owned triad rotation is `R_y=sqrt(3)Sigma13`, with `Sigma13` the stored WE value; inserting `R_y=Sigma13` would violate source gauge.
Potential counterexamples to require in R7/C7: flip the curvature term, double `q`, omit `Gamma`, substitute Kato `K` for physical advection, take `|v|>=1`, or pass nonunit photon directions. The original 4D chart excludes `N1=0`; use its valid interior to decide physical forward rays. No strong new no-go claimed. Review status SAME_AUTHOR_HOSTILE_PROOF_CHECK; independent distinct-author reviewer NOT_RUN.
