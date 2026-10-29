# CE1-M S0 · PR249 panel-local source law under PR251 physical input lock

- **2026-10-29**, parent PR251 HEAD `cd7e7efdb384580ae44c0cdca873eba018a404e2`, donor PR249 HEAD `0370f99aea7cc457b32a3ebc259a343a82ac5a9f`. All Draft, unmerged. No parent/main mutation.
- Model: positive massless collisionless all-expanding diagonal reflection-even Bianchi I, Lambda=0, metric (-,+,+,+), `u=t/Tstar`, `ell=ln a`, `h=Tstar H`; original exact-binary six-cell table, RK4/Hermite 4 panels, `u<=.08`, fixed `max|delta h|<1e-5`.
- Original donor **exact Git blobs** imported in isolated Python workspace: `einstein_tabulated_source_canonical.py` `1c905278f7a109e15f5e20d3ac7f931bdcf99433`, donor seven tests `30d85661adf7851317ebcb23c1aab6a2e4a08da3`.
- Parent physical source `fdeb83a65cd424786ba6bb8ddadbcb2b2e2d45bf`, MPFR `abbab0990fdefaf535ccbf5191ae3e060cb19214`, CE1-I comparison `c6f1a59db197766aae401d9868fcea3951f26c24`.
- **Derived proof:** for any fixed positive comoving angular measure X, `P_i^X(ell+s1)=exp(-4s)P_i^X(ell)` exactly, so `D=P_cont-P_stored` has the same shift. Independent Wolfram ray-symbolic ratio returned `{exp(-4s),exp(-4s),exp(-4s)}`, `dP/ds+4P={0,0,0}`.
- On each panel, both the exact flow and stored cubic share certified `m_j>=0`; with original upper box B and `B_i>=m_j`, `eta_j=min(eta_global, exp(-4m_j)eta(B-m_j1))` is an outward source forcing cap. Feed into the *unchanged* positive 2x2 Dini comparison with original pressure `L_j`, exact binary Hermite knots and initial/time error. Geometry Emax and `1e-5` acceptance unchanged. This is a proof conditional on correctly locked positive physical/cell/source data.
- **Executed S0:** original donor seven tests plus selected PR251 inherited tests **101 PASS in 14.15s**, exit 0. Native delegation `NOT_RUN`, human distinct-author R6/C9 `NOT_RUN`, formal MPFR implementation proof `NOT_RUN`.
- Immutable S0 evidence ZIP `BASS_CE1M_S0_20261029.zip`: **6564 bytes, 5 members, CRC PASS**, SHA-256 `607659409e3ac85443d4e96ae19fc8778c6132cf39e5f3d6a4d89b838449b90a`.
- Upper DAG **9/15**, CE-1 PARTIAL; `production_ready=false`, `merge_ready=false`, `auto_next=false`.
- **Next bounded work:** import donor module/tests under PR251, explicitly test physical lock and malformed rays, run full scoped suite and fresh ref8 scientific result, finish one bounded CE1-M unit. No automatic next node.
