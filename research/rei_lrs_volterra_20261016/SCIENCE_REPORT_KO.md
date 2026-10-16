# BASS LRS Einstein–Vlasov retarded response 연구 보고서

2026-10-16 KST. 후속 기준: BASS [PR168](https://github.com/cosmosapjw-quantum/bass/pull/168), commit `03a01d21ed21e7d32737ca5e5f6d889a7203aa70`. 원본 FD96 `freestream.py` Git blob `8467932c3281f9d426712b3a582f2aae3a484692`, Einstein PR164 tangent blob `1cab2bf7eab5a306ab207206ca3a0fc793dc9163`. 기존 LRS neutral-root/convexity(PR167)·비-LRS Hessian(PR168)은 그대로 재사용하고, 새로운 주제로 **초기 quadrupole A의 인과적 shear response**, 안전한 feedback suppression bound, 양의 signed response를 구현한다.

## 물리

서명 (-,+,+,+), `ds²=-c²dt²+a²[e^-2b(dx²+dy²)+e^4b dz²]`, `s=dot b`, `Sigma=sqrt(3)|s|/H`, `π^i_j=diag(-DeltaP/3,-DeltaP/3,2DeltaP/3)`. Collisionless fixed Killing q96/μ angular initial `W=1+A P2≥0`, `m/Tref>=3`, `f_m=.1` from Omega_m nonbaryonic allocation, and frozen isotropic *other* radiation. All cosmological clocks use `x=ln(a/a_ref)`, `a_ref=1/21`, `a_end=1/5`.

Kinetic pressure linearization around `A=b=s=0`: `DeltaP=alpha(x) A−kappa(x)b+O(A b,b²)`; `alpha=r³/(5N) ∫rw k/E0`, `kappa=r³/N ∫rw[2k/E0−2k²/(5E0³)]>0`. Scalar `alpha/kappa∈(1/10,1/8)` is **inherited from PR167**, not claimed as a new theorem.

New exact *first-variation* Einstein equation:

`B''+(3+Hbar'/Hbar)B'+ K kappa/Hbar² B = K alpha/Hbar²`, `B(0)=B'(0)=0`,

where `B=∂_A b|A=0`, `K=H0² Omega_m f_m/a_ref³`, and `Hbar` includes positive kinetic isotropic energy. The equivalent causal Volterra second-kind kernel is `B=g−T B`, with `G(x,u)=K e^{3u}/Hbar(u)∫_u^x e^(−3v)/Hbar(v) dv≥0`.

**Rigorously derived: comparative stability and sign.** For `X=ln(21/5)` and normalized kinetic source,

`||T||∞ ≤ q=[5/6][f_m/(1−f_m)] κ(0)(1−e^(−X))`, and `κ(0)≤2`.

Hence f_m=.1 implies source-independent `q≤0.14109347442680775`. Since `g` is nonnegative increasing, `(1−q)g≤B≤g`; also `g≤0.012531411042438566<min_x(alpha/kappa)=0.1`. Therefore signed first-order `s_A=∂_A s|A=0>0` for all x∈(0,X], and b_A>0. This theorem does not claim nonlinear finite-A sign or independent backreaction from photon/nu π_ab.

## 실제 계산

- Sandboxed Python, NumPy, SciPy DOP853, mpmath MP70. Wolfram CAS angular μ quadrature four exact zeros + power-law kernel 3 exact zeros. xAct/NCP not run.
- **24/24 focused Python tests PASS**, code type syntax check, parent PR167 source-normalizations and PR164 nonlinearity/tangent cross-reference.
- Three original FD96 q96 masses 3/30/300, full x 0→ln(21/5); 513 nodal response study per mass and output CSV 99 records; 65/129/257/513/1025 systematic product-Simpson refinement.
- Max sup |Picard−independent DOP853 b_A/sHref_A| = `1.3972369693770412e-13`, max |PR164 original b_A sensitivity−independent ODE|=`2.3048579646418876e-14` (absolute dimensionless).
- Picard iterations for tolerance1e-14: 5/3/2 (m=3/30/300). Measured final b_A m=3 `0.0029824670005648033`, m=30 `6.6093848787872e-05`, m=300 `6.717739119810654e-07`. Physical interpretation: if initial A=.05, b_kinetic contribution predicted at first order is .05 times these; native REI photonic driving is separately missing.
- Measured first-variation feedback suppression versus the no-backreaction g at z=4: `0.005756014312134683`, `0.00012898955473539253`, `1.3112709155160829e-06` (respectively). Strict upper envelope q noted above, not an empirical confidence interval.
- Fixed-node MP70 independent radial sums at nine (m,x) points: largest relative binary64-matched error `2.406348228059299e-16`. This is **not** an MP70 continuous quadrature test: q nodes are original double-precision data.
- m=3 endpoint Volterra b_A error to independent DOP853 for N 65/129/257/513/1025: `[7.1078e-11,4.4424e-12,2.7778e-13,1.7492e-14,1.2251e-15]`, fourth-order observed before near-floor. m300 interpolation near roundoff, cannot infer independent global accuracy from last ratios.
- Full nonlinear BASS PR164 source at m=3,A=±.05 has relative |b−A B|/|b|≈`5.54e-5`, sampled scope only. 99 CSV rows are model-derived local source diagnostic, not physically admitted REI native checkpoints.
- Additional semantic repair S4: early PR169 S3 JSON used ambiguous `v_exact` for actual signed `s/H`. S4 relabels exact/linear output to `signed_s_over_H_exact/linear`, preserving original unmodified S3 archive and creating a new S4 final campaign with identical underlying physics.

## What this DOES NOT establish

1. Any numerical error of the actual `rei_bianchi` photon transport, H/He chemistry, birth age or opacity clocks. Current related REI PR167/171/172 are separately active; their source contracts remain own authoritative branches.
2. A new full nonlinear Einstein–Boltzmann background: the original BASS PR164 source uses frozen isotropic *other radiation*, and the response contains only massive collisionless matter stress.
3. General non-LRS high-anisotropy angular quadrature accuracy; PR168 broad-chart HOLD is unaffected.
4. A BASS mathematical theorem of uniqueness/attractivity of full cosmological b(x), or an observable likelihood constraint. Volterra solution is a first variation only, and b_star(A) is an instantaneous stress minimum, not an EFE closure.
5. Momentum `Q^a` and stellar recoil, polarization/Thomson, nuclear source energy ownership, or full EoR science admission.

## DAG and publication

Source file, machine-readable `DAG.json` and local command `RUN_LOCAL.sh` accompany this document. S1 first theorem/Git commit, S2 kernel/15 tests, S3 positivity campaign/21 tests, S4 high-precision/24 tests and final code/package. Each stage has a create-only ZIP archive with Git checkpoint and actual Google Drive + ChatGPT File Library upload/readback identity. Dropbox stage writes NOT_RUN under current tool transport capability. Git branch is isolated from the original source and REI production code. Native REI integration is optional future S5, requires strict new data/checkpoint identity before physics claims.
