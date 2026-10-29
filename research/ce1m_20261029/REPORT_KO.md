# BASS CE1-M 연구 및 검증 보고서 (2026-10-29)

## 판정
Original upper DAG **9/15** of 15 nodes/21 edges, CE-1 **PARTIAL**. R/C scoped outputs **18/20**, R6/C9 distinct-author remains **NOT_RUN**; production_ready=false; merge_ready=false; auto_next=false. CE1-M is a *new scoped synthesis* of PR251 physical source-domain locks with PR249 local-source contraction, not a production solver.

## Actual source reconstruction
- GitHub parent PR251 HEAD `cd7e7efdb384580ae44c0cdca873eba018a404e2` checked; RF00 last-head SUCCESS plus other five workflows SUCCESS.
- CE1-K final uploaded ZIP 16,940,082 B, SHA256 `749c0385adef9ad48e2192f91c4664785de6cb9ebebb10e54af729f89f904c62`; ZIP 72 entries CRC PASS. Nested CE1J/CE1I/CE1H/CE1G/CE1F source recovered.
- CE1-L Drive S2 downloaded 70,526 B, SHA256 `192363ef4d383996c14a8c914076bb0a3ddeb8626a0cb747600a7eb250c90a5c`, 20 entries CRC PASS.
- Reproduced PR251 updated source/interval/sharp module bytes. Their actual local Git blob identities match the repository (see SOURCE_IDENTITY.json). Added PR249 opt-in source-only code, no modified physical equations, no parent/main mutation.

## R: derivation and symbolic check
See THEORY_KO.md. Algebraically P_i(ell+s1)=exp(-4s)P_i(ell), so D_i follows the same exact scaling for fixed current exact binary ray/mass Q and continuum cell M. The source discrepancy is bounded on each certified shifted box [0,B−m_j] with directed MPFR192 and combined with inherited CE1-I Jacobian comparison. The PR251 constructor-time physical cell lock and termwise positive ray mass preconditions prevent previous false certificates. Wolfram ray test yielded {1,0} for scale ratio and Jacobian row sum residual.

## C: actual tests and science
- Before PR250/251 source repairs on reproduced PR246 code, five CE1-M hostile controls: 4 FAIL / 1 PASS (intentional RED, exit1).
- After byte-identical repair of 3 PR251 modules, **107 pytest passed in 18.89 seconds**, exit0 across twelve scoped modules including new CE1-M hostile cases.
- Ref8 freshly recomputed on current repaired input: 384 rays, 4 panels; source upper 8.5958201253152648e-06, time+jump 8.1573135903787245e-07, initial 9.2048230880889293e-17, total **9.4115514844451857e-06**, target MET. CE1-I old uniform source 1.2273903547843227e-05 NOT_MET. Same accepted binary input and unchanged target.
- Ref16 newly recalculated four MPFR192 source caps [3.569278983301304e-05, 2.9241709495299544e-05, 2.358366230872103e-05, 1.861256875971887e-05], source h 2.1459172502504843e-06; SHA-verified PR246 frozen source/ray/mass/path and inherited initial h 1.8658569972854369e-16, time+jump h 8.1582972865958989e-07; assembled h **2.9617469790966602e-06**, target MET. Time residual not fully rerun this turn; no formal MPFR/Python program proof.
- Ref8 improvement in the **upper error bound** 23.3206%, ref16 19.4063%; *not* measured runtime speedups. More rays do not prove physical sky fitting readiness.

## Hostile checks
1. Physical measure replacement `source.cells`, raw cell weight edit: fail closed under PR251.
2. Stored ray count append: `certified_tabulated_pressure` rejects current cardinality; wrapper also fails closed, possibly earlier at initial geometry, so error-message order is not a physics claim.
3. Signed cancellation current ray masses: standalone analytic fourth-derivative majorant rejects negative mass.
4. Existing same original physical positive fixture: unchanged ref8/ref16 numerical identity; no tolerance widening.
5. Plot inspected: fixed target crossing at ref8 and panelwise source cap decline at ref16. For ref1/2/4, graph plots inherited CE1K results; only ref8/ref16 current source evidence.

## External literature and next step
Neumaier DOI 10.1007/BF02276880 and Heinzle-Uggla DOI 10.1088/0264-9381/23/10/016 support general comparison/kinetic context, not CE1-M exact code proof.

New PR is draft-only and isolated under PR251, until CI and actual readback complete. Scope of held gates: R6/C9 distinct author, formal program MPFR, full production physics, merge and main release. Upper DAG remains 9/15. Do not auto-next.
