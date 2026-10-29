# CE1-I S0: time-local pressure Jacobian research checkpoint

PARENT PR242 `99473c0e6ba8f9d7172cc3fb730f5ac32c7e4677`. Upper DAG **9/15** unchanged, CE-1 PARTIAL.

Positive collisionless diagonal expanding Bianchi I, Lambda=0, signature(-,+,+,+), normal proper `u=t/Tstar`, `ell=ln a`, `h=Tstar H`.

Exact `theta'=-theta^2+E`, `E'=-sum_i(E+P_i)h_i<=0` and `theta0^2=3E0+(3/2)sum_i s_i^2>=E0` imply `theta(u)<=theta0`. Thus `h_i(u)>=h_i0 exp(-theta0 u)` and `ell_i(u)>=h_i0(1-exp(-theta0 u))/theta0`.

On panel `[u_j,u_{j+1}]`, combine exact-solution lower bound at `u_j` and stored-Hermite MPFR Bernstein lower hull to establish a common `m_j>=0` for the segment between exact and reconstructed geometries. Since `P_i(ell+m1)=exp(-4m)P_i(ell)`, `partial_k P_i<=0`, and `sum_k|partial_k P_i|=4P_i`, the panel Lipschitz coefficient is `L_j=4 Pmax0 exp(-4m_j)<=4Pmax0`. For each panel use `k_j=sqrt(L_j)` in the positive 2x2 comparison propagator; source `eta`, full-panel MPFR residual, exact-binary knot jumps and continuum geometry `Emax` stay unchanged.

**New scientific objective:** strictly decreasing verified panel coefficients and same-physical-input CE1-H vs CE1-I total h bound without changing the 1e-5 target. Do not merge PR243/244 automatically. Source majorant's unsafe unkeyed cache in parent PR242 must be guarded for mutable-input certification.

Source snapshot: CE1-H original ZIP SHA256 `e4ed87dfe9fe99f9e9ce061c95cebc65b97f7884690517cb5b5a646f8f7a12d2`, 83 members, ZIP CRC PASS. Extracted module blob `f266e2808461a4a8eff0dc5d2bb038280b482047` and source blob CE1-G `8daa44d413aca912edb0918d31caad6182ad2bd3`. Runtime PYTHON_PASS / CPP_PASS. Inherited 81 tests PASS in current turn. Native subagents NOT_RUN (no host spawn tool). Stage S0 archive `BASS_CE1I_S0_20261029.zip`, 2113 bytes, SHA256 `b3591239f0432784fa9442aa812a4a8ff2cd158c8c70adfb33b8f9be349af856`. Theoretical derivation only; no CE1-I numerical claim yet.