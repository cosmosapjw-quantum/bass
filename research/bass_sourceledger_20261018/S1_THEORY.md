# S1: Source-frame angular normalization is not discrete stress isotropy

For non-tilted LRS Bianchi I with (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), reference b_ref=0, define R²=exp(2b)(1-mu0²)+exp(-4b)mu0². Conserved photon momentum gives E/Eref=exp(-x)R and mu=mu0 exp(-2b)/R. Direct differentiation gives J=dmu/dmu0=R^-3. The endpoints map to +/-1. Thus int J dmu0/2=1 and int J P2(mu)dmu0/2=0, from the primitive (mu³-mu)/2. Reflection symmetry also cancels the dipole. Only ONE solid-angle Jacobian belongs in a locally isotropic source.

Wolfram checks actually returned {0,0,1,-1,6/5}: derivative identity, quadrupole primitive identity, two endpoints, and the first-order false quadrupole from double J. Without J the leading false P2 is -6b/5; with double J it is +6b/5.

Native-style discrete weights wJ/sum(wJ) enforce the monopole, not the quadrupole. At b=.2 the Python oracle gives P2 means GL8=-.0014934983449590, GL16=-2.2453208230189e-7, GL32~4e-16. These are manufactured signed-geometry quadrature controls, not a demonstrated failure of the small-b original BASS trajectory. At b=.4 GL32 retains ~-1.98e-7; no entire-chart accuracy claim.

Bolometric units: rate [photons/(H-nucleus s)], mean E [eV/photon], proper nH=nh0/a³, j=nH rate E [eV cm^-3 s^-1], S=j/H [eV cm^-3 per dln a]. SourceLedger U [eV/H-nucleus] must be compared at the same proper-time interval and frame. Scalar unit conversion does not test midpoint time quadrature or spectral/angle discretization.

Implementation uses pinned REI PR150 source segments13.6/24.59/54.42/100 eV, Simpson32 source fractions, GL8 intersection moments and exact kb_erg_k/eV_erg from HHeModel. Original PR171 snapshots remain immutable. A valid predictor must preserve the native scalar spectral partition difference rather than normalize it away.

Actual sandbox verification:15 tests PASS, including source SHA pins, correct ray map, independent QUAD normalization/pressure, missed/double-J negative controls, angular refinement, photon positivity, finite support, zero dt and physical density conversion. First ray-map test was observed failing against the old untransformed direction then passing. Native Rust SourceLedger remains NOT_RUN until the source-bound executable is actually compiled and run.

S1 complete source/test checkpoint: BASS_SOURCELEDGER_S1_20261018.zip, 46037bytes, SHA25615d4209c527a80b9c55ce149dba6cf94c041bb7b9c1a5c138682ac03eb85b910. S2 will publish a complete self-restoring source capsule and native execution-only runner. Science source: arXiv:1410.8473 / Phys Rev D91 043511 (2015); exact source algorithm authority is the immutable REI code, not a review-paper approximation.
