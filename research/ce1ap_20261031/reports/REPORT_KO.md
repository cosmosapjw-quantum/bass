# CE1AP | Source-hidden sixth moment to exact geometric photon redshift

**Immutable parent:** BASS Draft PR #300 HEAD `d94843f2b63638d36244d951eccdbb81f3a64357`. Original 128-byte IEEE754 six-cell SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. Massless reflection-even collisionless *diagonal Bianchi I*, signature (-,+,+,+), Λ=0, original dimensionless 8πG=1, u∈[0,.08]. Existing parents, original source, tests and production untouched.

## R5: exact analytic result

The original six-cell source reweight `D=[[53,-106,53],[-203,406,-203]]/406` changes sixth angular moment, but initial E, P_i and all `l<=4` angular coefficients are unchanged. With exact original binary64 shear `σ=(.2,-.13,-.07)` as dyadic rationals and previously proved sixth tensor `δT_ijk=(-27/(1421π))c_ijk`, define `A_i=Σ_jk σ_j σ_k δT_ijk`. Exact trace `Σ_i A_i=0`, `A≈(0.001496907681,-0.000179628922,-0.001317278759)`.

Prior CE1AK/AL exact initial kinetic identity: `∂ε P_i(u)=(3/2)A_i u²+O(u³)`. Apply unchanged Einstein RHS `ℓ_i'=h_i, h_i'=-θh_i+P_i`, with `δℓ_i(0)=δh_i(0)=δP_i(0)=0`. Therefore
```
∂ε ℓ_i(u) = (A_i/8)u⁴ + O(u⁵).
```
For a null geodesic with conserved spatial Killing covector `k_i` and initial unit normal-frame direction `n_i`, `Σn_i²=1`:
```
Rγ(u,n)=Eγ(u)/Eγ(0) = sqrt(Σ_i n_i² exp(-2ℓ_i(u))).
∂ε ln Rγ(u,n) = -(u⁴/8)Σ_i n_i² A_i + O(u⁵).
∂ε d_u ln Rγ = -(u³/2)Σ_i n_i² A_i + O(u⁴).
```
A full symbolic independent Wolfram coefficient calculation returned **zero residual**, and trace of dyadic-sixth source `Σ_i A_i=0` was exact. No finite-horizon Taylor remainder enclosure is claimed.

## New source-owned physical computation (9 independent IVPs)

Three original GL orders (8,16,24). For each: **1 baseline-plus-source-tangent coupled Einstein-Vlasov IVP and 2 *fully nonlinear* positive source Einstein-Vlasov IVPs** for `ε=±.035`, at 401 original proper-time epochs. Directions **x,y,z,xy,xz,yz,xyz**. Actual new outputs:

- **16,842** directional geodesic finite-amplitude rows (exact Killing covector photon E ratio, its drift, and comparison to tangent)
- **1,203** physical metric tangent rows
- **2,406** source directional sky RMS rows
- **20,451 new rows total**, 9 actually executed IVPs.

GL24 at u=.08, ε=+.035: `ΔlnRγ(x)=-2.1612745620958052e-10`, `ΔlnRγ(y)=+2.4267948761647062e-11`, `ΔlnRγ(z)=+1.9274423723736334e-10`; along x source-induced drift `Δ(d_u lnRγ)=-1.0243212833493942e-8`.

Local `python -m pytest -q source/test_ce1ap.py`: **11/11 PASS**. Original/source checksum, initial dark E/P, 9 Hamiltonian constraints (max ~3.68e-13), early fourth-order jet, zero/negative controls and finite-source/tangent secants checked. Same-author independent implementation read original **8,421** CE1AN physical rows and all **16,842** directional outputs: independent null metric energy residual ≤4.78e-14; drift ≤1.56e-13; swapped axis negative control detected. This is **not** independent-author R6/C9. Under Python -O, pytest displayed an assertion-disabling warning; do not conflate its 11/11 collection with fully executed optimized assertions.

## External scientific provenance
P. Fleury, C. Pitrou, J.-P. Uzan, *Light propagation in a homogeneous and anisotropic universe*, Phys Rev D **91**, 043511 (2015), [DOI 10.1103/PhysRevD.91.043511](https://doi.org/10.1103/PhysRevD.91.043511), Sec. IV: exact Bianchi I photon geodesic redshift and drift. H. Lee, E. Nungesser, P. Tod, *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology*, Gen Relativ Gravit **52**, 48 (2020), [DOI 10.1007/s10714-020-02699-7](https://doi.org/10.1007/s10714-020-02699-7). Official CLASS, CAMB and ESA Planck PR3 are widely used external FLRW/observational references, **not source-identical to the six-cell Bianchi IVP**.

## DAG/claim gate
**BASS CE1 upper 9/15 (21 edges), CE1 PARTIAL, new upper 0**, CE1AP scoped physical redshift `1/1`. Root `DAG.json` belongs to ACCEL02 and is not altered. Related VigilODE PR #162–164 and BASS KM2O PR #298 are different source/algorithm branches, no data or completion inherited. Full original horizon continuum Weyl sign UNRESOLVED; no independent full cosmological visibility/recombination/CMB likelihood.

`PRODUCTION=HOLD; MERGE=HOLD; AUTO_NEXT=false; native_subagent=NOT_RUN; distinct_author_R6_C9=NOT_RUN`.

Source-inclusive staged local science archives S0/S1/S2 have fixed SHA manifests. The GitHub clean-checkout remote execution publishes its **own physical data** as an Actions artifact. Its final status and independent external archive provider readback are separately reported in later receipts, not assumed by this file.
