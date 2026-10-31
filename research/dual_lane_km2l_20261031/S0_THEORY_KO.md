# BASS KM2L S0 | Tagged Lyα no-Thomson-scatter survival and first-collision statistics on the original Einstein–P8–Peebles geometry

Date 2026-10-31 KST. Parent BASS KM2K Draft PR293 immutable HEAD `e216d708890c8321d2f6a2e146e60e7e01cea1ce`, source-complete S2 ZIP exact SHA256 `04f03b740668dc1ecd84af3d73f64b2bbaa9b8aa817bbe878a35d827182e81fd`; verified 41/41 payload SHA and ZIP CRC on independent restore. Distinct CE1AK Einstein–Vlasov branch remains untouched. Original code KM2A–KM2K read only. Upper DAG **9/15** (21 edges), KM2 PARTIAL, +0 upper completed. This is one physically new *post-escape unscattered Thomson photon selection* unit; not another whole-cycle research gate.

## New kinetic question and strict claim bound

KM2K solved two real Einstein–Bianchi I / original polarized P8 / Peebles IVPs, each yielding a positive frequency-resolved *tagged escaping Lyα* source, and propagated it collision-free. It explicitly omitted Thomson scattering **after Lyα Sobolev escape**, whereas its parent P8 bolometric photons already evolve Thomson collisions. Add the **zero-Thomson-collision (ballistic)** subpopulation plus the rate and distribution of **first Thomson collision** to resolve a meaningful, previously missing physical selection. The "scattered complement" is a probability-marked loss from the ballistic channel, **not** the actual post-collision radiation stress tensor or frequency/angular redistributed gain. Do not add tagged energy again to Einstein stress or to KM2J chemistry. No false conservation, thermal deposition or observational CMB claim.

## Derivation and physical units

Use (-,+,+,+); normal time `u=t/T_*`, `T_* = 218601.80677272403 Julian years`, `c, h_P, k_B` explicit; electron rest density `n_e^*=x_e n_H^*` in m^-3; `σ_T=6.6524587051e−29 m²`. For each ORIGINAL normal-tetrad photon ray `n_i(u)` and source-locked electron tilt `β_b(u)`, `γ_b=(1-β²)^(-1/2)`, the photon rate in u is

`Γ_i(u)= [n_H^*(u)x_e(u) σ_T c T_*] × D_i(u), D_i(u)=γ_b(u)[1−β_b(u)·n_i(u)]`.

This is exactly the loss coefficient of the original P8 `TiltedThomson.rhs(J,nu)` per normal time, with the physical electron rest density. With `h_i(u)=H(u)+σ_jk(u)n_i^j n_i^k`, define `R_i(u)=∫ h_i,du` and `A_i(u)=∫ Γ_i,du`. The KM2K source `j_{α,i}(t) G(y−log D_emit(t);σ_D)` is an energy-tagged fraction of existing grey chemical emission with no second gravitational photon stress. The *ballistic* frequency intensity satisfies

`(d/du)K_i^{(0)}(y,u)|_{q=y+R_i}=-[4h_i(u)+Γ_i(u)]K_i^{(0)}(y,u)+j_{α,i}(u)G(...)`, `K_i^{(0)}(y,0)=0`.

Therefore

`K_i^{(0)}(y,u)=∫_0^u dt j_{α,i}(t)exp[-4(R_i(u)-R_i(t))]exp[-(A_i(u)-A_i(t))]G[y−log D_emit(t)+R_i(u)-R_i(t);σ_D(t)]`.

The corresponding zero-Thomson-collision probability for a photon emitted at t and seen at u is **exactly** `P_0(t,u,i)=exp[-(A_i(u)-A_i(t))]` within source-locked cold-electron Thomson and fixed KM2J background. At fixed u its probability-marked *at-least-one-scatter* part is `K_i^{free}−K_i^{(0)}`, **not** actual redistributed post-scatter photons. The first collision rate (loss from ballistic intensity) is `Γ_i(u)K_i^{(0)}(y,u)` in normal-time collision-event units; its angular-energy integral is `C_1(u)=Σ_i w_i(u)Γ_i(u)∫K_i^{(0)}dy`. A first collision does NOT deposit its whole photon energy as heat: this rate is **collision events weighted by incident energy**, not thermal heating or real collision-gain redistribution.

Three evaluated transfer scenarios per actual geometry and source:
1. `shear_thomson`: actual Bianchi h_i and original finite-tilt Thomson Γ_i.
2. `shear_no_scattering`: same actual Bianchi h_i and set Γ_i=0, recovers source-owned KM2K *collision-free* spectral result.
3. `Honly_thomson`: set h_i=H in characteristic redshift only, but preserve actual n_i(u), Γ_i(u) and full Einstein/chemistry solution. H-only is a counterfactual transport, not a second FLRW universe.

The exact constant-rate control for `h>0, Γ≥0, j>0`, u≥0 is `ρ_0(u)=j(1−exp[−(4h+Γ)u])/(4h+Γ)`, `ρ_free=j(1−exp[−4hu])/(4h)`, and `C_1=Γρ_0`. Wolfram symbolic integration independently confirmed. Check Γ→0, u→0, monotonic S≤free, nonnegative first collision rate, source rate dimensionless, redshift and no-scatter ray identity.

## Code and data contract

Reuse exact frozen KM2K `evaluate_grid` physics (two live Einstein–P8–Peebles IVPs; no static synthetic geometry) to regenerate its raw injected line packets, with another independently integrated same original KM2J IVP to compute `Γ_i(t)` at GL8 source nodes and normal-clock endpoints. Compare x_e, original geometric rays and source photon moments between independent re-solves before transport. Compute cumulative Γ_i for each of 40 intervals using the same 8-point GL nodes and exact partial polynomial antiderivative as KM2K. Emit 3 scenarios × 2 grids × 41 epochs = **246 physical epoch records** including six zero states; at least 30 actual frequency snapshots (1200 bins each) = **36,000 spectral frequency rows**, and scientific figures. Record end-state Thomson survived energy fraction, first scatter energy-event rate, frequency centroid, red-wing probability, shear-vs-H-only and no-scatter controls, and first-collision distributions. Preserve actual raw physical packets and optical depth arrays, no mock-data claims.

Expected source: S0, S1, S2 stage source-complete archives; GitHub Draft PR not merged; remote Push+PR CI; local original code tests and RHS-free/independent saved-data physics audit using exceptions (valid under python -O). Classify physical, numerical and packaging failures separately; do not dilute original constraints.

## Scientific boundary / current statuses

Full Thomson gain operator and frequency redistribution, resonant Lya diffusion/recoil, 2p population/ionizing spectral feedback, temperature/entropy first-law, realistic observational abundance, angular continuum enclosure, and independent author R6/C9 remain **NOT_RUN**. Native subagent NOT_RUN (no callable host dispatch); same-author hostile audit is not distinct-author review. `UPPER_DAG=9/15;KM2=PARTIAL;KM2L_SCOPED=0/1_PEND_CI;NEW_UPPER_COMPLETED=0;PRODUCTION_READY=false;MERGE_READY=false;AUTO_NEXT=false;STOP_AFTER_ONE_BOUNDED_UNIT=true`.

Primary references: Hirata & Forbes, PRD 80 023001 (2009), DOI 10.1103/PhysRevD.80.023001; Chluba & Sunyaev, A&A 503 345 (2009), DOI 10.1051/0004-6361/200912335; full scattering redistribution is excluded. Only scoped zero-scattering population and first collision hazard are claimed.
