(* BG02 state-to-constraint tests. PREPARED_UNEXECUTED.
   Load the five pinned BASS WL dependencies and StateConstraints.wl first.
   These SC IDs are NEW adapter tests, not AUX13/AUX14 or native17.
   Integer/rational fixtures use a fixed reference length and density unit;
   the exceptional symbolic fixture retains ell explicitly. *)
Module[{make, eval, zero3, zmat, base, flat, vstate, vr, iir, ixr,
  ell, u, assumptions, exstate, exbefore, ex, dropped, general, gr,
  rot, rotated, rr, badN, dx, gx, kx, qx, diagRows, ids, tests},
 zero3 = ConstantArray[0, 3]; zmat = ConstantArray[0, {3, 3}];
 make[h_, a_, n_, s_, rho_, q_, lam_, kg_] := <|
   "Hgeom" -> h, "aB" -> a, "nB" -> n, "sigma" -> s,
   "rho" -> rho, "q" -> q, "Lambda" -> lam, "kappaG" -> kg|>;
 eval[s_, asm_:True] := BASS`Research`BG02StateConstraints[s, Assumptions -> asm];
 base = make[1, zero3, zmat, zmat, 0, zero3, 0, 1];
 flat = eval[base];
 vstate = make[1, {1,0,0}, zmat,
   DiagonalMatrix[{2/3,-1/3,-1/3}], 0, zero3, 0, 1];
 vr = eval[vstate];
 iir = eval[make[1, zero3, DiagonalMatrix[{1,0,0}], zmat, 0, zero3, 0, 1]];
 ixr = eval[make[0, zero3, IdentityMatrix[3], zmat, 0, zero3, 0, 1]];
 assumptions = ell > 0 && Element[u, Reals];
 exstate = make[Sqrt[(13+u^2)/3]/ell, {1,0,0}/ell,
   {{0,0,0},{0,2,3},{0,3,0}}/ell,
   {{0,0,u},{0,0,0},{u,0,0}}/ell, 0, zero3, 0, 1];
 exbefore = exstate;
 ex = eval[exstate, assumptions];
 (* Hold Hgeom fixed: only the input shear tensor changes. *)
 dropped = eval[Join[exstate, <|"sigma" -> zmat|>], assumptions];
 general = make[0, {2,0,0}, {{0,0,0},{0,1,3},{0,3,-2}},
   {{1,2,4},{2,-3,5},{4,5,2}}, 3/7, {1/5,-2/7,3/11}, -2/9, 2];
 gr = eval[general];
 rot = {{3/5,-4/5,0},{4/5,3/5,0},{0,0,1}};
 rotated = Join[general, <|"aB" -> rot.general["aB"],
   "nB" -> rot.general["nB"].Transpose[rot],
   "sigma" -> rot.general["sigma"].Transpose[rot],
   "q" -> rot.general["q"]|>];
 rr = eval[rotated];
 badN = {{0,1,0},{0,0,0},{0,0,0}};
 (* These are actual mapper calls, not a table of expected curves.
    Hgeom remains sqrt(14/3), i.e. the u=1 constraint state at ell*=1. *)
 diagRows = Table[Module[{s, full, cut},
   s = make[Sqrt[14/3], {1,0,0}, {{0,0,0},{0,2,3},{0,3,0}},
     {{0,0,amp},{0,0,0},{amp,0,0}}, 0, zero3, 0, 1];
   full = eval[s]; cut = eval[Join[s, <|"sigma" -> zmat|>]];
   If[!AssociationQ[full] || !AssociationQ[cut],
     Return[Failure["DiagnosticEvaluationFailed", <|"amplitude" -> amp|>], Module]];
   <|"u" -> amp, "Hfull" -> full["Hamiltonian"],
     "Hdeleted" -> cut["Hamiltonian"], "sigma2" -> full["Carriers"]["sigma2"]|>
   ], {amp, {-2,-1,0,1,2}}];
 ids = {
   "SC01_FLAT_BASELINE", "SC02_BIANCHI_V_MOMENTUM",
   "SC03_BIANCHI_II_CURVATURE", "SC04_H_ZERO_REGULAR",
   "SC05_EXCEPTIONAL_CONSTRAINT_STATE", "SC06_OFFDIAGONAL_DELETION",
   "SC07_FULL_TRANSVERSE_FLUX", "SC08_PROPER_FRAME_COVARIANCE",
   "SC09_INPUT_UNCHANGED", "SC10_MISSING_INPUT",
   "SC11_REJECT_DERIVED_OVERRIDE", "SC12_REJECT_NONSYMMETRIC_N",
   "SC13_REJECT_TRACEFUL_SHEAR", "SC14_REJECT_JACOBI_VIOLATION",
   "SC15_REJECT_INEXACT", "SC16_REJECT_NONREAL",
   "SC17_REJECT_SHAPE", "SC18_OWNER_GENERAL_SLOTS",
   "SC19_DIAGNOSTIC_ROWS_CONSISTENCY"};
 tests = {
   TestCreate[{flat["Hamiltonian"],flat["Momentum"],flat["Carriers"]["R3"]},
     {3,zero3,0}, TestID -> "SC01_FLAT_BASELINE"],
   TestCreate[{vr["Hamiltonian"],vr["Momentum"],vr["Carriers"]["DivergenceK"]},
     {-1/3,{2,0,0},{-2,0,0}}, TestID -> "SC02_BIANCHI_V_MOMENTUM"],
   TestCreate[{iir["Hamiltonian"],iir["Carriers"]["R3"]},
     {11/4,-1/2}, TestID -> "SC03_BIANCHI_II_CURVATURE"],
   TestCreate[{ixr["Hamiltonian"],ixr["Momentum"],ixr["Carriers"]["R3"]},
     {3/4,zero3,3/2}, TestID -> "SC04_H_ZERO_REGULAR"],
   TestCreate[FullSimplify[{ex["Hamiltonian"],ex["Momentum"]},
     Assumptions -> assumptions], {0,zero3}, TestID -> "SC05_EXCEPTIONAL_CONSTRAINT_STATE"],
   TestCreate[FullSimplify[{dropped["Hamiltonian"]-ex["Hamiltonian"]-u^2/ell^2,
       ex["Carriers"]["sigma2"]-2 u^2/ell^2,
       dropped["Momentum"]-ex["Momentum"]}, Assumptions -> assumptions],
     {0,0,zero3}, TestID -> "SC06_OFFDIAGONAL_DELETION"],
   TestCreate[{gr["Carriers"]["DivergenceK"],gr["Momentum"]},
     {{-36,-10,-10},{178/5,74/7,104/11}}, TestID -> "SC07_FULL_TRANSVERSE_FLUX"],
   TestCreate[FullSimplify[{rr["Hamiltonian"]-gr["Hamiltonian"],
       rr["Momentum"]-rot.gr["Momentum"],
       rr["Carriers"]["Ricci"]-rot.gr["Carriers"]["Ricci"].Transpose[rot]}],
     {0,zero3,zmat}, TestID -> "SC08_PROPER_FRAME_COVARIANCE"],
   TestCreate[exstate === exbefore && ex["InputState"] === exbefore,
     True, TestID -> "SC09_INPUT_UNCHANGED"],
   TestCreate[MatchQ[eval[KeyDrop[base,{"q"}]], Failure["StateKeys",_Association]],
     True, TestID -> "SC10_MISSING_INPUT"],
   TestCreate[MatchQ[eval[Join[base,<|"sigma2"->99|>]], Failure["StateKeys",_Association]],
     True, TestID -> "SC11_REJECT_DERIVED_OVERRIDE"],
   TestCreate[MatchQ[eval[Join[base,<|"nB"->badN|>]], Failure["NNotSymmetric",_Association]],
     True, TestID -> "SC12_REJECT_NONSYMMETRIC_N"],
   TestCreate[MatchQ[eval[Join[base,<|"sigma"->IdentityMatrix[3]|>]],
       Failure["ShearNotSTF",_Association]], True, TestID -> "SC13_REJECT_TRACEFUL_SHEAR"],
   TestCreate[MatchQ[eval[Join[base,<|"aB"->{1,0,0},"nB"->IdentityMatrix[3]|>]],
       Failure["JacobiNotEstablished",_Association]], True, TestID -> "SC14_REJECT_JACOBI_VIOLATION"],
   TestCreate[MatchQ[eval[Join[base,<|"Hgeom"->1.0|>]], Failure["ExactInputRequired",_Association]],
     True, TestID -> "SC15_REJECT_INEXACT"],
   TestCreate[MatchQ[eval[Join[base,<|"Hgeom"->I|>]], Failure["RealInputNotEstablished",_Association]],
     True, TestID -> "SC16_REJECT_NONREAL"],
   TestCreate[MatchQ[eval[Join[base,<|"q"->{0,0}|>]], Failure["StateShape",_Association]],
     True, TestID -> "SC17_REJECT_SHAPE"],
   (* Arithmetic slot test only; NOT an inhomogeneous geometric gradient proof. *)
   TestCreate[Expand[BASS`Authority`BG02MomentumComponent[dx,gx,kx,qx]+dx-gx+kx qx],
     0, TestID -> "SC18_OWNER_GENERAL_SLOTS"],
   TestCreate[FullSimplify[({#["Hfull"]-(1-#["u"]^2),#["Hdeleted"]-1}& /@ diagRows)],
     ConstantArray[0,{5,2}], TestID -> "SC19_DIAGNOSTIC_ROWS_CONSISTENCY"]
 };
 <|"required_ids"->ids,"tests"->tests,"diagnostic_rows"->diagRows,
   "diagnostic_units"->"fixed reference length ell*=1; Hfull/Hdeleted represent ell*^2 times the Hamiltonian residual"|>
]
