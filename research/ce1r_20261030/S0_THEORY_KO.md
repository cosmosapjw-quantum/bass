# CE1-R S0 · original BASS Rust Liouville derivative for observer-sky moments

**Pinned parents:** PR #259 HEAD `e963b3cff4a6f91d4060e05080d1e6e2667e001b` (normal-frame unpolarized energy sky), PR #258 HEAD `0656e98989750de4ea19c510ff2052654aaa3eda` (41 DOP853 proper-time histories), and independent native Rust sibling PR #257 HEAD `baa29ff5b5d0384f62e2627ebc8b37d34d7aa26b`. All Draft and unmerged, no changes to parent/siblings/main. BASS Rust module `_rustcore/src/kinetic/comoving.rs` live Git blob `a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84` contains Frame::apply/det/phys_dirs.

## Newly derived physical law

For the original six exact-binary angular cells and their eight reflections, positive massless collisionless expanding diagonal Bianchi-I Λ=0 with signature (-,+,+,+), `u=t/Tstar`, `ell_i=ln a_i`, `h_i=dell_i/du`. Fixed conserved q, `M=diag(e^{-ell_i})`, `r=|Mq|`, incoming normal-observer sky `s=-Mq/r`, `W=det(M)*r*dE0`, `theta=sum h_i`, `H_s=sum h_i s_i²`. Then

```
s'_i=(H_s-h_i)s_i,
W'=-(theta+H_s)W,
a_lm'=integral W[-(theta+H_s)Y_lm*(s)+grad_S Y_lm*(s).s'].
```

For the original piecewise-constant positive continuous angular source, the brightness transport `partial_u U + s' grad_S U = -4 H_s U` holds along characteristics/weakly across cell discontinuities. Stored rays are an atomic measure, no claimed pointwise intensity function. Use regular Cartesian polynomial `Y*_lm=N_lm*(-1)^m d_z^m P_l(z)(x-i y)^m` to obtain analytic derivative through l=4 without atan2 or polar division.

Exact moment relations: `E'= -theta E-sum_i h_i P_i`; `P'_i=-(theta+2h_i)P_i+sum_j h_j R_ij`, `R_ij=int W s_i²s_j²`; `a'00=E'/sqrt(4pi)`; `a'20=sqrt(5/(16pi))*(3P'3-E')`; `a'22=sqrt(15/(32pi))*(P'1-P'2)`. All odd l/odd m vanish by reflection, `C'_l=2Re sum conj(a_lm)a'_lm/(2l+1)`. The energy-integrated C_l is **not** thermodynamic CMB temperature C_l.

## S0 executed and trust boundary

Local compiler actually used: user-provided official offline Rust 1.94.1 installed in a private container prefix. Current tool outputs `PYTHON_PASS` and `CPP_PASS`; original BASS historical offline `comoving.rs` blob `25669ec464ab279e1a4d2421400a8ed135ae9638` used to compile S0 only and is **not** byte-identical to live PR259. Mandatory next S1 GitHub Actions must compile live Git-blob-pinned BASS Rust for authoritative parity.

Rust selftest `CE1R_BASS_RUST_LIOUVILLE_SELFTEST_PASS`. Synthetic *noncanonical* 384-ray source (same six physical cell masses, but not original frozen ray n hash) vs independent scipy sph_harm_y: max a_lm gap `8.673617379884035e-16`; directional derivative finite difference `4.1426906349784076e-10`; E continuity `1.1435297153639112e-14`; fourth-moment pressure derivative `2.7755575615628914e-15`. These do not constitute MPFR192 certification or full physical source hash equality; S1 will test against exact frozen rays and 41 real history rows. CE1-M prior max|Delta h| <1e-5 is reused, not freshly re-certified.

**Upper DAG 9/15 (21 edges), CE-1 PARTIAL.** Distinct-author R6/C9 and native subagent NOT_RUN; no production, merge, auto-next, temperature/Q/U claim. S0 ZIP `BASS_CE1R_S0_20261030.zip` size 11519 bytes, 6 members, SHA256 `8bdd2683313606191542897ddd64df948592c177fa0bdd8119af2bc3d1ee14ea`, CRC PASS. Exact S0 ZIP contains math note, actual Rust code, independent SciPy test, local result and Rust install evidence. Stage S0 Git/Drive/Dropbox provider receipts must be confirmed before saying backed up.
