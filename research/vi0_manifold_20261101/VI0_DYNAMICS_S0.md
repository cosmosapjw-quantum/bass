# BASS VI0 original production-path theory | S0 source and mathematical contract

Date 2026-11-01 (Asia/Seoul); project cosmosapjw-quantum/bass.
Immutable theory parent PR #310 HEAD `71adfbb2948f6c23725a01dfc048e90623a9eab5`, itself based on BASS `main` `9c6506e4e2087129a8b674ff10438e5db1a55c9d`. Frozen original source blob SHA-1: see `vi0_dynamics.py:ORIGINAL_BLOBS` and PR310 `VI0_SOURCE_AUTHORITY.json`. Historical original critical-path statement: BASS PR15, `G-DYN-MANIFOLD-VI0` and `P-MIG-II-PREFLIGHT` join J1.

## R1 objective and boundary

Derive, for the already established 7D principal-frame VI0 gamma-law chart, source-owned Einstein-Codazzi + Gauss exact propagation and the pure gauge part of moving scalar Kato projector differentiation. The work does not implement generic physical photon angular Liouville, polarized P8 screen, Type-II production code, or migration. One bounded theory unit, no auto-next.

## R2 literature and source authority

- S. Hervik, *The Asymptotic Behaviour of Tilted Bianchi type VI0 Universes*, Class. Quantum Grav. 21 (2004) 2301, DOI 10.1088/0264-9381/21/9/007, https://arxiv.org/abs/gr-qc/0403040. Seven-dimensional tilted single-fluid state space, not new literature result.
- BASS main source: `bianchi/charts/general.py`, `bianchi/matter/fluid.py`, `bianchi/conventions.py`, original rank-one Type-II `generated/rust/typeii/typeii_kato.rs`.
- Scientific owner: PR310 VI0 source conditional eigenframe chart `N=diag(0,p,-r)` with p,r>0, gamma in (0,2), Omega_star>0, |v|<1.

## R3 conventions

Signature (-,+,+,+), epsilon123=+1. BASS owner uses Hubble-normalized time tau, N, Sigma, Omega and internal c=8piG=1; no physical unit conversion inferred. q_dec = deceleration, separate from N33 curvature `-r`. K=(trN²)/6-(trN)²/12; Sigma²=tr(Sigma²)/6; Q=3gamma Omega v/G_+; Pi=3gamma Omega(vv - v² I/3)/G_+; G_+=1+(gamma-1)v².

## R4 candidate equations (to be verified and implemented)

Let J_a=epsilon_abc N_bd Sigma_cd, C_a=J_a-Q_a and C_G=Omega+Sigma²+K-1. BASS source equations include N'=q_dec N+{Sigma,N}+[W,N] and Sigma'=(q_dec-2)Sigma-S3+Pi+[W,Sigma], with S3=[2N²-(trN)N]^TF. The derived target is

`C_G'=2 q_dec C_G`, `C'=[(2q_dec-2) I - Sigma + W] C`.

Use unique principal-frame W_ij=-(n_i+n_j)Sigma_ij/(n_j-n_i); n=(0,p,-r), n_i distinct. For scalar oblique collision projector P=r a^T/(a^T r), r=(1-v²)^2/(1-v.n)^4, a=(w/4pi)(1-v.n), the pure rotating-frame contributions v'_W=Wv, n'_W=Wn cancel identically. A frozen angular grid while retaining Wv is a falsifying negative control. Non-Hermitian oblique P must never be promoted to unitary Kato without additional metric.

## Claim gate

At S0: exact target equations and source locks defined; full VI0 gate remains PARTIAL, production preflight OPEN, J1 0/2 PASS, BASS unrelated upper `9/15` scoped/source-mapped unchanged, zero newly completed full upper nodes.