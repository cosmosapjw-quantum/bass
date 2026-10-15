# BASS massive Einstein–Vlasov: analytic stress Jacobian + native Rust/NCP 64c readback

Date: 2026-10-15 KST. This is a bounded constructive continuation of [BASS PR162](https://github.com/cosmosapjw-quantum/bass/pull/162), exact parent `31c41541eb053545f8638177b8e848d5495b57fd`. New independent worktree; no changes to original BASS FD96, original REI chemistry/AX08 checkpoint, Rust `rei_microphysics` or existing gamma/nu source files.

## 1. Current scientific problem and source reuse

PR162 repaired cancellation in `DeltaP=P_parallel-P_perp` for the original BASS collisionless FD96 massive matter moments and passed read-only native `rei_microphysics::BackgroundPoint` interface, but only Python computed the kinetic moments; a native fast derivative suitable for the future source-only geometry Jacobian was absent. This step implements a **distinct standalone Rust computation** of kinetic `rho,P_perp,P_parallel,DeltaP,d(DeltaP)/db`, verifies the analytic Jacobian of BASS LRS Einstein RHS in Python, and tests the shared numerical source against the original FD96 quadrature and local Wolfram/xAct.

Sibling-state firewall: REI PR150 owns true native H/He photon/chemistry, proper-time driver and 1/8/32/64 transport pilot, **not** BASS. REI PR152 supplies an independent LRS threshold-ray reference, not a real Verner/chemistry background. REI PR145/148 positive canonical finite volumes/paired recoil and PR149 Case-A angular response are distinct matter/radiation models, not identical to exact collisionless BASS massive FD96. BASS_HE PR65 addresses MD14 photon-source threshold ghosts; bass_cr PR72 addresses local photon/atom energy-conserving absorption; neither is a substitute for the missing native all-source momentum four-vector and fresh checkpoint. WU088_HH PHYS51 branch stays a separate nuclear physics donor. No source or numerical-result authority is silently transferred between these lanes.

Original physical input: `m/Tref=3,30,300` exploratory massive nonbaryonic matter; original `bianchi/matter/freestream.py` FD96 `q,rw=q²dq fFD`, GL32 angular `mu,w`, positive `W=1+A P2(mu), -1<=A<=2`. `export_grid.py` calls original source byte-lock verification and serializes `q,rw,mu,w,m,N` in exact float64 decimal roundtrip form. Real AX08 donor data are **not transferred to NCP**. Mass normalizer and `f_m Omega_m` stay those of original PR161/162, subtracting kinetic matter from nonbaryonic dust without double counting.

## 2. Derivation and Einstein Jacobian

Convention: `(-,+,+,+)`, `ds²=-c²dt²+a²[e^{-2b}(dx²+dy²)+e^{4b}dz²]`, `s=dot b`, `sigma^i_j=diag(-s,-s,2s)`, `Sigma=sqrt(3)|s|/H`, `x=ln(a/a_ref)`. Let `r=e^{-x}`, `z=mu²`, `k=r²q²`, `F=e^{2b}(1-z)+e^{-4b}z`, `E=sqrt(m²+kF)`. With fixed canonical-number source `W>=0`:

`rho=(r³/N)int rw(q) dq int W(mu) E dmu/2`

`P_perp=(r³/N)int rw dq int W [k e^{2b}(1-z)/(2E)]dmu/2`; `P_parallel=(r³/N)int rw dq int W [k e^{-4b}z/E]dmu/2`.

Define `L=k[e^{-4b}z - e^{2b}(1-z)/2]`; then `DeltaP=(r³/N)int rw dq int W L/E dmu/2 = -partial_b rho/2`. The direct second derivative is

`partial_b DeltaP=(r³/N)int rw dq int W {k[-4e^{-4b}z-e^{2b}(1-z)]/E+2L²/E³}dmu/2`.

Also `partial_x rho=-3(rho+pbar)`, `pbar=(2Pperp+Pparallel)/3`, yielding the full collisionless canonical number/energy-work identity:
`d rho/dx=-3(rho+pbar)-2(s/H)DeltaP`.
The sheared stress is `pi^i_j=diag(-DeltaP/3,-DeltaP/3,2DeltaP/3)`, `sigma_ab pi^{ab}=2sDeltaP` (positive contraction for aligned signed shear/stress, NOT an automatically positive entropy production).

For a fixed gamma/nu multipole state and fixed signed s in the PR162 source,
`partial_b H=-H0² C_m DeltaP/H` where `C_m=Omega_m f_m / a_ref³`.
If `J_s=d(s/H_ref)/dx=-3(s/H_ref)+(3H0²/(H_ref H)) Pi_tot`, then

`partial_b J_s=(3H0²/H_ref)[C_m (partial_b DeltaP)/(3H) - Pi_tot (partial_b H)/H²]`.

This is a **partial Jacobian** for the kinetic massive source at fixed x, photon/neutrino multipoles and s. It is not a full Newton Jacobian for REI HHe/Thomson/stellar radiation, and sign of `s` must never be reconstructed from `Sigma` alone.

The exact same rationalized inverse-energy stress from PR162 is rederived independently in `kernel.rs` via `expm1(2b)`, `expm1(-4b)`; the continuum GL-integrable angular `P2` polynomial is integrated in closed form. Consequently `A=b=0` gives exact float64 `DeltaP=0`, even when direct positive-pressure subtraction fails.

## 3. Executed evidence and precision limits

- Local Ubuntu: Rust `rustc 1.99.0`, Python/NumPy original FD96, SciPy DOP853 inherited source. **74 actual local tests PASS** = 10 new plus original PR162/PR161/PR160 6+20+15+23 tests, independently rerun in this branch. New **10/10 regression** local PASS: masses3/30/300, exact isotropy, sub-roundoff +/- shear sign, energy/work, Python/Rust five-output parity, signed-source partial Einstein RHS Jacobian, positivity, corrupted input rejection, and bitwise 1/2/4/8/32 thread output equality.
- Wolfram Language 15.0.0 and xTensor1.3.0 at local workstation: **8 exact zero checks**, with original tensor metric signature, shear work, DeltaP derivative, susceptibility, canonical mass energy work and on-shell energy.
- NCP `s1a0e5abed09` explicitly reached through SSH, reports **64 logical CPUs, 125 GiB RAM, rustc 1.99.0 and cargo 1.99.0** under `/root/.cargo/bin/`. Rust source compiled with `-C opt-level=3 -C target-cpu=generic`, using std-only scoped CPU threads.
- **3639 source-input states on NCP** (3 masses x1213 cases): exact 1 vs64 worker output **bytewise identical** separately for each mass, including all 5 stresses/Jacobian fields. All NCP outputs downloaded to local and validated against Python original BASS FD96 independent implementation and original source hashes. Max absolute discrepancies (rho, P_perp, P_parallel, DeltaP, dDeltaP/db):
  - m3: (5.551e-16,1.110e-16,1.110e-16,8.327e-17,5.551e-16).
  - m30: (4.441e-16,3.469e-18,3.036e-18,2.602e-18,1.735e-17).
  - m300: (8.882e-16,2.711e-20,2.711e-20,2.033e-20,2.168e-19).
  All pass source-specific `rtol=8e-13`, `atol=5e-14` absolute at every point. Tiny `b=1e-16,A=0` sign checked separately; no fictitious tiny-signal relative error claimed.
- NCP **actual matched component benchmark**, 6000 independently generated physical source states per mass, 3 repeats, widths1/2/4/8/16/32/64. Per-state outputs are internally bitwise checked against the serial reference every run. Medians:
  - m3 serial0.259906602s, best32 threads0.016080955s = **16.162386x**. Width64=15.375720x, slower than32.
  - m30 serial0.264889889s, best64 threads0.015690774s = **16.881888x**.
  - m300 serial0.262889664s, best64 threads0.014545431s = **18.073694x**.
  These are independent kinetic-moment batch *kernel times*, including std thread spawning and excluding source import/chemistry/Einstein ODE/I/O. There is no native REI production-speedup claim.
- Hardware and build exact hashes, source grid checksums, original returned TSVs, CLI stdout and scientific admission are preserved under `evidence/`.

## 4. Execution and connection

From this committed branch:
```bash
D=research/rei_native_stress_ncp_20261015
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s "$D" -p test_native_stress.py -v
python3 "$D/export_grid.py" --out /tmp/bass_source_grids --random 1200
rustc -C opt-level=3 "$D/kernel.rs" -o /tmp/native_massive
/tmp/native_massive eval /tmp/bass_source_grids/grid_m30.txt /tmp/bass_source_grids/cases_m30.tsv /tmp/native_stress_m30.tsv 8
wolframscript -file "$D/xact_susceptibility.wl"
python3 "$D/validate_ncp.py" --ncp-results "$D/evidence/NCP_RESULTS" --out /tmp/ncp_verification_new.json
```

NCP source-run contract: only `kernel.rs`, `ncp_runner.sh` and source-locked `SOURCE_GRIDS` were sent to `/root/bass_native_stress_20261015/`; runner is a bounded `6000*3*7*3` state-benchmark + physical 3639-case science comparison, not a resident daemon or changed REI production process. Native Rust follows local source; exact `kernel.rs` SHA was checked in returned NCP build receipt.

The receiver contract for `rei_bianchi` is **opt-in source-only**: canonical input tuple `(x,b,m/Tref,A,q,rw,mu,w,N)`; typed output `rho,Pperp,Pparallel,DeltaP,dDeltaP/db`, with manifest SHA/source hash and LRS `Sigma` sign convention. It is ready for an owner-controlled, versioned source adapter and native background chemistry rerun; this branch does **not** silently patch `rei_microphysics` production code. The complete H/He return needs fresh checkpoint identity, species/temperature evolution, photon energy/number ledgers, source-age resolution, stellar momentum recoil and AX11 numerical convergence. Claim ceiling: `DERIVED + IMPLEMENTATION_VERIFIED + NUMERICALLY_CHECKED (kinetic source)`; full cosmological EoR, likelihood and general Bianchi class geometry `NOT_ADMITTED`.

Primary related literature: Cardall & Mezzacappa, *Conservative Formulations of General Relativistic Kinetic Theory*, [Phys. Rev. D 68, 023006 (2003)](https://doi.org/10.1103/PhysRevD.68.023006), for number/four-momentum conservative kinetic formulations; [Bianchi I Einstein–Vlasov mathematical dynamics](https://doi.org/10.1088/0264-9381/23/10/016). Neither paper proves this particular optimized algorithm; the stable formula is directly derived above and its implementation is tested.
