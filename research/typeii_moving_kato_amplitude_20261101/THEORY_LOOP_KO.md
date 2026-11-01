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
