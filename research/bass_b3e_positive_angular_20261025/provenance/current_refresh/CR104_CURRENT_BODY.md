## Problem and change

The saved C23D-source EE+EI+ground-H CE chain did not include neutral elastic energy exchange. This PR binds actual CCC/LXCat H1(1S) and He4 ground-singlet MTCS to the leading heavy-neutral finite-temperature FP operator, using the inherited source, grid, EE/EI generators and CE hazards without replaying prior science.

**Gate:** NUMERICALLY_CHECKED_SCOPED_CONDITIONAL_NEUTRAL_FP_FINITE_CHAIN. Named consumer N5_C23D_H1_HE4_NEUTRAL_ELASTIC_V1. Scoped theory/coding activities20/20, independentR6/C9PASS,blocking0. FullN4/N5 remainPARTIAL/OPEN;N6/N7 remainpredecessor-gated.

## Results and validation

At T=10000K, ne=.14cm^-3, prescribedlnLambda20, HI/HeI=.9/.07cm^-3, common stationary Maxwell baths:
- Eight new combined matrices,16neutralgenerators,112primaryphysicalRHS,24source-integratedrows.
-39controls and18finitecomparisons PASS.
- Independent Decimal70 reference solves28physicalRHS includingt/v_s/v_p; max norm-relative solution difference3.061615e-11 underfrozen5e-10.
- Neutral-induced CE relative reduction0.0109207–0.0109688%; no-CE mean first-entry time reduction14.54–18.38proper s.
- Neutral heat6.71408e-5–8.42237e-5eV/selectedelectron. Six signed bath rewards andCEinternal10.20435eV are separately conserved.
- NewODE/sourcequadrature/thermalquadrature/oldreplay0.
- NewworkerCPU4.364423s includingretainedfailures; knownlineage34.234445114s. Otherunmeasuredglobalspend/remainingnull.

C9 preserved its missing-dependency startup, original four signed-reward diagnostic FAILs, and owned-stale-lease refusal. A limited4reward highprecision arithmetic check resolved the reviewer's norm/category definition using unchanged frozen tolerances; the completed28solves were not rerun. Original FAILrecords remain.

This is the declared leading-mass-ratio model on finite grids. Separate target-speed/recoil diagnostics, paired-effect convergence and absolute observable errors are distinguished. No global physicalerrorcertificate, isotopecompletechemistry, totalelastic eventhazard or irreversibleassimilation claim.

## Authorities

- Science S: 5eb895abbacce1642c451fd3fdfd2f776783871f
- Documents D: 257007cc708d0db403ec2ff0c741e4a10b6207ab (D1 e9e1f48859b07f49cb30be6fabc44c6a1e64ca73)
- Central M1: 2354d6e995fde736fffbcad2d0e40473218cb8c4
- Central M2: a28ba343bb85addf1a7e9e58e75816ed3b75cd3b, expectedparent14976bda37b17e8dd8060f4c89adf6ddf9fbcc6a, preserveslaterWU89/HE100currentnodes andallotherDAGbytes.
- [Results](https://github.com/cosmosapjw-quantum/bass_cr/blob/5eb895abbacce1642c451fd3fdfd2f776783871f/research/cr_n5_neutral_elastic_20261025/RESULTS_KO.md)
- [Fixed handoff with later owner returns](https://github.com/cosmosapjw-quantum/bass_cr/blob/257007cc708d0db403ec2ff0c741e4a10b6207ab/research/cr_n5_neutral_elastic_20261025/delivery/HANDOFF_FINAL_WITH_LATE_OWNER_KO.md)

Late HE100 is scoped analytic directCBA, physicalproviderfalse/HE-ANGSOURCE_INPUT_PENDING. PHYS89 scoped displayed-covariance/typedinterface completion keepsphysicalparentPARTIAL_INPUT_DEPENDENCIES. Neither changes this PR's fixed inputs.

## Backup and continuation

Canonical BASS_CR_N5_NEUTRAL_DELIVERY_20261024T220158Z.zip:26886833bytes,SHAb275796854ceb484256bab550a55ea7ebb818b6a0b76b125843d5a2705bb38dd,481manifestentries/482ZIPmembers.
Librarylibfile_ba6eca88570c8191a7aafd5106aa0ea1 andDropboxid:BSpOijBcT10AAAAAAD_9qQ:actualwholeGET,size/SHA/CRC/allmanifestR3PASS.
Drive1upload50.001snoACK+exactpostquery0:UNKNOWN_NO_ACK/R3NOT_RUN,resend0. Historicalunknownspreserved;threeproviderbackupincomplete.
SeparateN5_NEUTRAL_FINAL_AUTHORITY_20261024T220510Z.json binds exactpostcanonicalD/M2/PRtexts;its ownactualR3 is recorded externally. TerminalDriveNOT_ATTEMPTED.

NextfirstnodeCR_N5_ATOMIC_ISOTOPE_COVERAGE:refreshcurrentowners,bindremainingCI/RR/DR/CX/state/isotope/energyownership;ground-HRR/PI microscopicMilnepair is a concretecandidate after sourceadmission. Missingrates/species/ranking=null;globalerror/completion=null.
Draft/unmerged; noactivation.


