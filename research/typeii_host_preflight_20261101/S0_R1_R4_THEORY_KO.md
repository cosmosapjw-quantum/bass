# BASS Type-II production-host preflight | R1–R4 constructive theory (2026-11-01)

## Authority and scope
- Actual source: `cosmosapjw-quantum/bass` main commit `9c6506e4e2087129a8b674ff10438e5db1a55c9d`, tree `b7da11939afab787627ce4e8e63d3cd4195f8e03`.
- Prior immutable parent: PR #318 head `52e77e59e0d37b75b892efa38d05784ddb731757`, stacked on PR #316; previous 96 AEM2 comparison rows, GH Actions run `41308702963` SUCCESS. Do not redo old-vs-Kato research.
- Governing plan: `docs/superpowers/specs/2026-08-21-p-mig-ii-preflight-design.md` and `docs/development/BASS_DAG_REALIGNMENT_20260821.md`. Current production main stays untouched. Type-II reference full Arnoldi/Pade13 as in PR #6; production admission HOLD.
- Selected theoretical obligation: exact Type-II 5-field embedded state -> BASS `_rustcore` generic geometry+tilt mock interface. This is *not* an already-installed production adapter. Classify `_rustcore` as candidate host under BASS authority, and the original Rust Type-II code as reference/lab, not as the dispatch owner.

## Units and exact 5-to-4 physical constraint reduction
Signature (-,+,+,+), epsilon_123=+1, class A a=0, Hubble-normalized quantities Sigma=sigma/H and N=n/H, `d tau=H dt`, source `8 pi G=c=1` internally. External physical rate retains `c`, `sigma_T` and `H` in SI. Assumptions 0<gamma<2, N1>0, v2²<1, Omega>0.

The five *stored* coordinates are `x=(SigmaPlus,SigmaMinus,Sigma13, N1,v2)` with `Sigma13` a WE Hubble-normalized *scalar* whose physical raw off-diagonal shear is `Sigma_13(raw)=sqrt(3)*Sigma13`. All other offdiagonal Sigma, other curvature N and velocity components are zero.

The source Gauss budget and Type-II Codazzi constraint are:

    A=1-SigmaPlus²-SigmaMinus²-N1²/12,
    Omega=A-Sigma13²,
    Gplus=1+(gamma-1)v2²,
    C2=-sqrt(3)N1 Sigma13 - (3 gamma Omega/Gplus)*v2 =0.

The Saha/electron collision rate is not part of this constraint. The signs follow `C2=epsilon_{2bd}N_{bc}Sigma_{dc}-Q2` from original `bianchi.conventions.codazzi_residual`, with `Q2=3gamma Omega v2/Gplus`.

Solving for the physically admissible positive root:

    beta=3 gamma² v2²/(N1² Gplus²),
    Omega + beta Omega²=A,
    Omega=2 A/[1+sqrt(1+4 beta A)],
    Sigma13= -sqrt(3) gamma Omega v2/(N1 Gplus).

`A>0` ensures a unique positive Omega. The derivative of the *Gauss-eliminated* Codazzi residual with respect to Sigma13 on this branch is

    d C2/d Sigma13 = -sqrt(3) N1 [1+2 beta Omega] < 0.

So the five stored coordinates are an embedded **four-dimensional physical constraint manifold**, not five freely specifiable physical variables. Keep all five in the native reference state; select the 4D chart only at verified constraint initialization. The N1=0 Type-I boundary requires a separate chart. At v2=0, Sigma13=0 and Omega=A.

## Canonical host coordinate mock (no runtime mutation)
Original `bianchi/charts/class_a_tilted.py` uses `(SigmaPlus,SigmaMinus,Sigma13,N1,v2)`. `_rustcore/src/geom/group.rs` packs symmetric N as `[N11,N22,N33,N12,N13,N23]`; `_rustcore/src/core/conventions.rs` packs STF shear as `[S00,S11,S01,S02,S12]`. Proposed **isolated mock** translation:

    shear5=[-2 Sp, Sp+sqrt(3) Sm, 0, sqrt(3) S13, 0]
    n6=[N1,0,0,0,0,0], a3=[0,0,0], v3=[0,v2,0], gamma, Omega.

Decoding reconstructs Sp=-S00/2, Sm=(S11-Sp)/sqrt(3), S13=S02/sqrt(3), N1=n6[0], v2=v3[1]. Validate zero forbidden coordinates, Gauss+Codazzi, finite values, spacelike tilt, N1>0 and Omega>0; reject invalid/off-type states rather than auto-project them or swap axes.

## Clock and rate contract
`tau=ln(a/a0)` with `dtau/dt=H [s^-1]`, `H>0` on this expanding-branch contract. For physical Thomson scattering `nu_phys=sigma_T[m²]*ne[m^-3]*c[m/s] [s^-1]`, `nu_tau=nu_phys/H` dimensionless. The source Type-II angular generator includes outgoing factor `q_alpha=1-v2*n_{alpha,2}` *once*; do not multiply `q_alpha` into nu_tau a second time. `alpha=1,1e3,1e5` is an **explicit** dimensionless test multiplier, not an electron-density claim. The PR318 3-anchor log-rate is an explicit surrogate, not original native SahaHistory.

## Accepted goal and independent tests
Construct an isolated Rust compile-only mock host state, exact positive density root and typed clock, with 401 *original fixture* sample checks. Original source will be read in GitHub CI without changing it. Negative controls: flip offdiag-sign, omit sqrt3, permit v2=0 with S13 nonzero, add forbidden curvature component, permit H<=0, double-count Doppler, bad phi unit, Rust reference source hash drift. Full `_rustcore` Cargo offline viability and production callback/rollback install remain open until verified; do not promote the preflight on mathematical roundtrip alone.

## Claim limits and DAG
`G-DYN-MANIFOLD-VI0=PARTIAL` unrelated; `P-MIG-II-PREFLIGHT=PARTIAL`, `JOIN_J1=0/2 FULL PASS HOLD`, upper BASS physics 9/15 scoped/source-mapped (new complete upper nodes 0), Stage II 11/11 *historical* (current EvidenceBundle admission not established), REI central 28/88 HOLD (not modified). Native subagents are unavailable/not requested; same-author adversarial tests only. STOP after one bounded construction.