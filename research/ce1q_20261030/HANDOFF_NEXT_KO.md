# BASS CE1-Q | Native observer-sky harmonics validated, next research handoff

$physmath-research-loop $scispace $exa $wolfram

**PROJECT:** cosmosapjw-quantum/bass
**CURRENT UNIT:** CE1-Q, native BASS comoving-frame angular-energy sky and complex low-l harmonics
**CURRENT DRAFT BRANCH:** research/bass-ce1q-observer-sky-20261030-r1
**PARENT:** PR #258 HEAD `0656e98989750de4ea19c510ff2052654aaa3eda` (physical six-history model)
**SEPARATE RUST NATIVE SOURCE:** PR #257 HEAD `baa29ff5b5d0384f62e2627ebc8b37d34d7aa26b` (binary64 E/P/J; not automatically merged)
**ORIGINAL CERTIFICATE ANCESTOR:** PR #253 HEAD `e4a0feba0e8709d5e996ed8ef4c9c9bf1da4c4d0`
**SIX PHYSICAL CELL BINARY64 SHA256:** `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`
**EXACT ORIGINAL PR253 RADIATION MODULE GIT BLOB:** `fdeb83a65cd424786ba6bb8ddadbcb2b2e2d45bf`
**LOCAL ARCHIVED BASS RUST COMOVING BLOB:** `25669ec464ab279e1a4d2421400a8ed135ae9638`
**LIVE BASS COMOVING BLOB PIN:** `a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84` (CI must verify)

## Frozen physics

Positive massless collisionless reflection-even expanding diagonal Bianchi I, Λ=0, signature (-,+,+,+). Original exact stored binary64 six-cell angular distribution, total initial E=.9, initial shear (.2,-.13,-.07), `u=t/Tstar in [0,.08]`, original physical input/source and CE1-P saved proper-time histories unchanged. No polarization, Doppler/boost, global tilt, recombination, blackbody radial spectrum, observational CMB input or new matter closure.

## New derived and executed result

With `M=diag(exp(-ell_i))`, `r=|M qhat|`, photon propagation `n=M qhat/r` and incoming sky `s=-n`, the observer solid-angle Jacobian is `J=det(M)/r^3`. Original continuous six-cell initial energy density `U0(qhat)` pushes to `U(s)=r^4 U0(qhat)` and

`a_lm^U=det(M)∫ U0(qhat) r Y_lm*(s) dOmega_q`.

For stored positive-octant rays use original mass `w_a/8` in each of eight coordinate-sign reflections. A finite stored-ray measure has harmonic moments, not a pointwise smooth sky intensity. `a00=E/sqrt(4π)`, `a20=sqrt(5/(16π))*(3P3-E)`, `a22=sqrt(15/(32π))*(P1-P2)`, all odd-l coefficients zero. New science is unpolarized energy-integrated brightness, **not** CMB thermodynamic temperature, Stokes Q/U or a CMB likelihood.

Rust1.94.1 `sky_native.rs` imports **BASS's existing** `_rustcore/src/kinetic/comoving.rs`, uses `Frame.apply/det/phys_dirs/real_ylm_l` and extends complex `Y_lm` through `l=4`, no crate replacement or generic Bianchi family claim. Local executable compiled against archived BASS Rust original module, known to have a different Git blob than live GitHub; remote CI must rebuild against live pinned blob. `produce_sky.py` uses original PR253 exact-MPFR geometry to recreate 6/96/384/1536 stored rays and the actual PR258 GL24/GL40 continuous-cell data, for 41 epochs each. Stored ref8 n/mass exact SHA pair:

- rays `9d46624cdb747a5760eda945d5effeb17f0619ade2b7198ee1700903123455ba`
- mass `c421e8148af743ea44bbb565f32a44090e18299e0e0b15f20eee37fb0a232211`

GL40 u=.08 actual E=.7584190590089329, a20=.022309840575559355, a22=.015673816332176647, a40=-.008105712278762101, C2=.00019781320466729784 and C4=.00004028693886843132. Direct 6-ray stored C4 is 33.3157× GL40; 96-ray 1.5877×, 384-ray 1.1282×, 1536-ray 1.0309×. **GL40 is not an interval-certified continuum reference**. The initial physical angular source is already anisotropic and has nonzero a20(0), so never call the observed quadrupole a pure shear signal.

Local scoped 12/12 pytest PASS; Rust own selftest PASS; Python compileall PASS. Six×41 saved actual harmonic CSV results, GL40 observer-sky NPZ map, 4 science figures and full report. Max BASS native Rust E/P vs original CE1-P E/P 1.78e-13; independent SciPy a_lm max 1.04e-14; odd-l/m 4.34e-17. No formal MPFR new-sky certificate, no genuine distinct-author R6/C9, no observable CMB-temperature claim.

## DAG / governance state

**UPPER_DAG=9/15; UPPER_EDGES=21; CE1=PARTIAL; SCOPED_R_C=18/20.**
R1-R5,R7-R10,C1-C8,C10 scoped outputs complete; R6/C9 genuine independent-author NOT_RUN. production_ready=false; merge_ready=false; auto_next=false. Local native subagents not exposed. No force push or automatic merge of parent/sibling branches.

## Next one physics-first research unit (do not begin automatically)

**CE1-R: analytic proper-time Liouville transport of the already generated observer sky harmonics**, without needing to assume a blackbody or new collision kernel.

For each photon path define `b(n)=sum_i h_i n_i^2`. Then derive and implement

`d/du log(det(M)r)= -theta - b(n)` and `dn_i/du=-(h_i-b(n))*n_i`.

Differentiate `a_lm=∫det(M)r U0 Y_lm*(s) dOmega_q` under the original integral and evaluate the term `grad_{S2}Y_lm*(s) · ds/du` on the same six-cell physical source. Generate proper-time `da_lm/du` and test against independent finite differences of the already saved time-series and the exact E/P energy continuity identity. Validate all-m parity and the original `u=t/Tstar` dimensional clock against the BASS Rust `Frame.step` e-fold convention. Use genuine native BASS Rust. Keep first/source physical ZIP immutable and original DAG at 9/15 until a legitimate top-level gate is met.

Stop after one bounded unit. Preserve source identity, new actual code/data/tests, per-stage backup and publication receipts, and copyable handoff.
