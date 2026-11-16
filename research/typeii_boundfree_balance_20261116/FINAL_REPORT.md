# TypeII level-resolved bound-free detailed-balance bridge

Frozen parent PR336 ad4bda34a833d215aa49037d7cb4d609e5cee04b. Current Draft PR337. Four local deliverables B1..B4; upper production DAG stays9/15 scoped/source-mapped with zero new full upper nodes.

## Actual construction
Retrieved and archived the author's nl-resolved hydrogen source table:55 states, n1..10,1000 energies per state. The raw source SHA256 is4150287531cc642ecf837fa253b22f5158bd189b3f2c9ce634010b2e4b5ee44c. Its own '(unpublished)' attribution is preserved. All rates are integrated only over the original tabulated energy support. No helium excited-state data, high-energy tail or effective HYREC coefficient is invented.

Implemented the Milne reverse capture kernel with g_i=2(2l+1), g_plus=1, electron spin2 and stimulated capture. Independent photon-energy and Maxwell-speed integrals agree. The forward/reverse relation reduces to Saha in a common-temperature Planck field and includes the photon chemical-potential factor for a Bose-Einstein field. Signed photon, electron-kinetic and ionization-energy terms conserve energy; nuclei and charge are conserved channel by channel. DERIVATION_SUPPLEMENT.md provides the derivation, units, assumptions, finite-band qualification and the isolated population-network proof.

## Measured source-state results
Actual original TypeII inputs give358 time states,2148 low-level forward/reverse records and165 all-level finite-band probes. At mean z1100:
- 2s: photo=35.295424772059619 s^-1, alpha=4.370940142911038e-20 m^3/s, stationary ratio relative to Saha(Tm)=0.95244512564646733.
- 2p: photo=30.249815346937314 s^-1, alpha=1.1243877919810881e-19 m^3/s, stationary ratio relative to Saha(Tm)=0.95291827573248944.
These are microscopic ratios, NOT new cosmological populations. On these source states, replacing the boosted field by an energy-equivalent scalar blackbody shifts the2s photo rate by-0.039016959887287983 relative.

A finite closed2s/2p/continuum test was actually integrated from a nonequilibrium initial state with Radau and BDF. The common-temperature Planck stationary ratio is2.9999999999999925; boosted common-temperature ratio3.001488501813817; boosted parent-Tm ratio3.0014903223500817. Nuclei/charge and positivity were preserved, and the finite mass-action relative entropy decreased. Maximum solver fraction gap=2.0200971451167504e-10. These deliberately isolated populations do not approximate the full cosmological atom: bound-bound cascades and the ground state are absent from this network test.

## Executed verification
13 analytic contracts pass normally and under -O (26 test executions). All55 source states at three thermal/chemical conditions give165 finite-band detailed-balance cases, maximum log residual3.5527136788005009e-14. Maxwell-speed integration, two-frame angular measure and adaptive energy quadrature are independently checked. Max non-equilibrium energy-ledger relative residual5.2638512197675622e-17. The independent1s Coulomb reference differs from the author's finite-precision table by7.4432196531581951e-05 relative; this is not a new accuracy bound for all excited states.

The original4-point default missed the predeclared3e-8 quadrature target in the cold1s source case (first energy interval2.028kBTm). A regression was recorded RED, then default order8 repaired it without changing the raw source or tolerance. Actual source8/12 maximum relative gap5.684341886080963e-14. Failed logs and diagnosis are preserved. Input interpolation sensitivity (log-linear versus log-PCHIP) reaches4.4456726103282253e-06, so it is not conflated with machine-level balance identities.

Hostile controls: omit stimulated capture in the finite-band n10s,T8000 equilibrium case and the stationary ratio is deficient by0.57818983368706311; use equal2s/2p statistical weights and the thermal ratio becomes1 instead of3; omit electron-spin normalization and it is off by factor2. Eleven malformed physical/numerical inputs reject. Optimized kernel and source/network calculations reproduce seven science outputs byte-for-byte. Original BASS9/9 blobs remain unchanged. Review is same-author hostile, not genuinely blind or independently authored; no native subagent.

## Claim gate
Admit finite-support source-resolved forward/reverse kernels, thermodynamic/chemical equilibrium reductions, conserved particle/energy exchange and an independently checked finite reversible reaction network. Do not admit high-n total capture rates, helium excited-state rates, bound-bound cascades, effective multilevel replacement, variable-composition thermal/radiation feedback, magnetic-sublevel alignment, finite-mass/recoil accuracy, new native HYREC xe or optical depth, or observed CMB visibility. The local boosted Planck bath is prescribed, not the result of a solved global Bianchi radiation equation.

Local4/4 scoped complete. Upper BASS9/15 scoped/source-mapped; zero new full upper nodes. StageII historical11/11 current canonical chain not established; JoinJ1 0/2 FULL PASS HOLD. Production_ready=false, merge_ready=false, auto_next=false.

Next unit: BOUND_BOUND_CASCADE_AND_CONSERVATIVE_EFFECTIVE_RATE_BRIDGE. Add provenance-locked bound-bound and two-photon channels to the microscopic bound-free network; derive a number/energy-consistent elimination/interface map and test its thermal limit before replacing native effective coefficients. Independently retain the StageII canonical evidence recovery task. No additional process-only audit loop is needed.
