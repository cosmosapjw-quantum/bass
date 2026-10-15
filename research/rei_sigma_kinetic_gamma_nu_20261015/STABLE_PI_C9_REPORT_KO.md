# BASS ↔ REI C9: cancellation-resistant massive kinetic anisotropic stress

Date 2026-10-15 KST. Independent constructive BASS continuation of original PR161 `a16c44d28357428b92f15d709eee86ca7bba4f21`. Exact base source remains unchanged, notably `bianchi/matter/freestream.py`, `research/rei_axbi_sigma_matter_20261015/sigma_matter.py`, original REI gamma/nu source-ref files, actual 159 MiB AX08 donor and native REI chemistry. New default is legacy; stabilized kinetics is **opt-in** `stable_massive_pi=True` or `--stable-massive-pi`.

## Physical claim and exact construction

Convention: signature (-,+,+,+), Bianchi I LRS `ds²=-c²dt²+a²[e^-2b(dx²+dy²)+e^4b dz²]`, `x=ln(a/a_ref)`, `s=dot b`, `σ^i_j=diag(-s,-s,2s)`, `Σ=sqrt(3)|s|/H`; signed `s/H` separately preserved. Massive collisionless source is original fixed 96-node FD rule `rw=q²dq fFD(q)`, GL angular nodes `mu`, initial `W=1+A P2(mu)>=0` (`-1<=A<=2`). This kinetic component is *subtracted* from original nonbaryonic `Omega_m`, not added.

Write `r=exp(-x)`, `z=mu²`, `k=r² q²`, and `E²=m²+k[e^(2b)(1-z)+e^(-4b)z]`. The original source-normalized, physical-number-redshifted massive energy and principal pressures are

`rho= (r³/N) ∫rw dq ∫ W dmu/2 E`,
`P_perp=(r³/N)∫rw dq ∫W dmu/2 [k e^(2b)(1-z)/(2E)]`,
`P_parallel=(r³/N)∫rw dq ∫W dmu/2 [k e^(-4b) z/E]`.

Holding `x` and the canonical source weights fixed yields the **exact identity**
`DeltaP=P_parallel-P_perp=-(1/2)partial_b rho`. Therefore `pi^i_j=diag(-Pi,-Pi,2Pi)`, `Pi=DeltaP/3`, and `σ_ab pi^ab=2s DeltaP=6sPi`. The Einstein source convention used by the original PR161 is retained. This is kinetic anisotropic stress, not phenomenological viscosity.

In floating-point arithmetic `P_parallel-P_perp` subtracts two nonzero positive integrals near `b=A=0`. Instead define `E0=sqrt(m²+k)`, `t_perp=expm1(2b)`, `t_z=expm1(-4b)`, `D=t_perp(1-z)+t_z z`, `g=P2(mu)+t_z z-t_perp(1-z)/2`. Then

`DeltaP=(r³/N)∫rw k dq [ C(A,b)/E0 + ∫W g (1/E-1/E0)dmu/2 ]`,

where `C=A/5+t_z(1/3+2A/15)-t_perp(1/3-A/15)` is the analytically integrated angular polynomial, and the residual inverse-energy difference is evaluated *without subtraction*:
`1/E-1/E0=-k D/[E E0(E+E0)]`.

For `A=b=0`, `C=D=0` exactly in float64, hence `DeltaP=0` exactly (subject to IEEE arithmetic). At `A=0,b=0` the exact linear susceptibility is
`partial_b DeltaP=(r³/N)∫rw k[-2/E0+2k/(5E0³)]dq`.
The mean pressure `pbar=(P_parallel+2P_perp)/3` is computed directly from `k(1+D)/(3E)`; principal pressures can then be reconstructed as `P_perp=pbar-DeltaP/3`, `P_parallel=pbar+2DeltaP/3`. This reduces temporary pressure arrays while preserving positive source physics.

## Actual local execution and evidence

- **64 tests PASS**: 6 new opt-in tests, original joint kinetic 20, original evidence 15, and original massive parent 23. No original test acceptance widened.
- Original `m/Tref=30,x=.5,A=0,b=0`: legacy `DeltaP=+1.0299920638612292e-18`, stable `0`. At `b=1e-16`: legacy `+7.589415207398531e-19` (wrong sign), stable `-2.323484613627355e-19`; analytic derivative negative. At `b=1e-12`: legacy `-2.3223610534639505e-15`, stable `-2.3234846136250434e-15`.
- Batched 1024 original FD96 moments `rho,P_perp,P_parallel` parity within `3.3306690738754696e-16` absolute. Stable and legacy `DeltaP` differ at finite nontrivial b by at most `1.734723475976807e-17` absolute.
- Real AX08 donor 312238-row original q0 electron source was *read only*. Eight new `401`-node Bianchi I Einstein + gamma + massless-nu + massive histories generated, totaling **3208 rows** in `evidence/STABLE_PI_CAMPAIGN/`. Versus original PR161 legacy campaign, maximum final `|delta Sigma|` across all eight was `3.5432865409107395e-14`; zero initial shear and stress-less FLRW case remains exactly FLRW. Both source commitments and their data are separate.
- Original `rei_microphysics::BackgroundPoint` Rust crate compiled via isolated offline Cargo external dependency against existing, source-hash verified REI geometry code. **All 3208 rows** passed: maximum relative Hamiltonian constraint `3.3306690738754696e-16`, exact `Sigma`; four deliberately corrupted H, massive stress, Sigma, photon number inputs rejected (exit code3). Receipt `evidence/STABLE_PI_REI_NATIVE_BRIDGE.json`. No native REI owner code or solver checkpoint changed.
- Local Wolfram Language 15.0.0 + xTensor1.3.0 `xact_stable_pi.wl`: 4 LRS tensor contractions plus 3 exact kinetic identities independently returned **zero**. `evidence/XACT_STABLE_PI.json`. The separate Wolfram plugin kernel lacked xAct, so local kernel was used.
- 1024-state component timings (medians, 7 repeats, local Ubuntu 24 logical CPU/31GiB): legacy chunk32 `0.018119s`/3.30MB tracemalloc, stable chunk16 `0.028687s`/2.14MB, stable chunk32 `0.026806s`/4.15MB. Preoptimization stable chunk32 `0.031456s`/5.73MB. This is a numerical accuracy/memory tradeoff: **stable is slower than the legacy comparable chunk32**. No full native chemistry or 64-core NCP throughput claim. Peak tracemalloc measures Python allocations, not RSS.
- Source full checksums, intermediate timing logs and direct solver outputs are preserved in `evidence/`. Full original 159MiB AX08 raw donor is intentionally *not* republished.

## Exact REI integration boundary and status

The selected native interface is versioned, opt-in and source-checked: `KineticGammaNuMassive(...,stable_massive_pi=True)` -> `run_joint.py --stable-massive-pi --points 401` -> `RESULTS.json` matching `csv_sha256` -> `native_bridge.py --csv ...` -> real native Rust `BackgroundPoint/GeometrySnapshot` validation. The original Rust code only validates incoming external background points; it does *not* activate this source in the reactive/native HHe driver. User-defined `Sigma` must not be confused with signed `s/H`.

The recipient's canonical owner remains REI PR150 native proper-time chemistry/photons/geometry, with existing PR145/148 canonical positive particle FV and collision/recoil models; those modules have different physical scope from exact collisionless BASS FD96. REI PR149's Case-A angular emission stress requires a separate stellar/gas energy momentum closure. BASS_HE PR64 and bass_cr PR71 provide separate source physics, not an automatically enabled charge-exchange/HHe rate model. In particular: the old AX08 checkpoint must **not** be resumed under the changed source identity; a new opt-in chemistry trajectory requires fresh clock/source/restart identity and full energy/particle ledgers.

Claim levels: exact formulas DERIVED; Wolfram+xAct checks SYMBOLICALLY_VERIFIED; new source and native read-only Rust intake IMPLEMENTATION_VERIFIED; matched finite-campaign histories NUMERICALLY_CHECKED; native two-way H/He, polarized Thomson E/B, new stellar Q^a/EOS, calibrated massive dark matter/neutrino masses, precision observational inference and AX11 full error budget **NOT_RUN/NOT_ADMITTED**. 64-core/128GiB NCP execution not undertaken because this calculation is lightweight and remote preflight was blocked; do not infer NCP performance. Native host subagents unavailable, local independent analytic/Wolfram check used.

## Reproduction from the exact published BASS branch

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
D=research/rei_sigma_kinetic_gamma_nu_20261015
python3 -m unittest discover -s "$D" -p test_stable_moments.py -v
python3 -m unittest discover -s "$D" -p test_joint_kinetic.py -v
python3 -m unittest discover -s "$D" -p test_evidence.py -v
python3 -m unittest discover -s research/rei_axbi_sigma_matter_20261015 -p test_sigma_matter.py -v
wolframscript -file "$D/xact_stable_pi.wl"
python3 "$D/bench_stable_pi.py" --out /tmp/bass_stable_bench_new.json
python3 "$D/run_joint.py" --stable-massive-pi --points 401 --out /tmp/bass_stable_new_campaign
python3 "$D/native_bridge.py" --repo /path/to/rei_bianchi --target /tmp/bass_stable_native_cargo --csv /tmp/bass_stable_new_campaign/REI_GAMMANU_MASSIVE_BACKGROUND.csv --out /tmp/bass_stable_native_result.json
```

Current source audit is source-specific rather than proving all homogeneous Bianchi types. Next project action: target-conditioned native REI chemistry run on a *new* source identity; do not silently replace the PR150 rooted solver source or merge parent PR161 automatically.
