(* Generic exact frame derivation.  No Bianchi label is inspected here. *)
BeginPackage["BASS`GenericBianchiCandidate`"];

BASSInitializeXActCandidate::usage = "BASSInitializeXActCandidate[] defines the generic abstract xAct objects once.";
BASSDeriveGenericFrame::usage = "BASSDeriveGenericFrame[canonicalSpec] derives exact component tensors and typed blocks.";

Begin["`Private`"];

BASSInitializeXActCandidate[] := Module[{},
  Needs["xAct`xTensor`"];
  xAct`xTensor`$ReadingVerbose = False;
  If[! xAct`xTensor`ManifoldQ[BASSCandidateM],
    xAct`xTensor`DefManifold[BASSCandidateM, 4, {A, B, C, D, E, F}];
    xAct`xTensor`DefMetric[-1, bassg[-A, -B], bassCD, {";", "D"}, PrintAs -> "g"];
    xAct`xTensor`DefTensor[bassMatter[-A, -B], BASSCandidateM, Symmetric[{-A, -B}]];
    xAct`xTensor`DefTensor[bassMomentum[A], BASSCandidateM];
    xAct`xTensor`DefTensor[bassDistribution[], BASSCandidateM];
  ];
  <|
    "einstein_block" -> xAct`xTensor`ToCanonical[EinsteinbassCD[-A, -B] - bassMatter[-A, -B]],
    "mass_shell" -> xAct`xTensor`ToCanonical[bassg[-A, -B] bassMomentum[A] bassMomentum[B]]
  |>
];

BASSExpr[op_String, args_List : {}, value_: Null] := Module[{out = <|"args" -> args, "op" -> op|>},
  If[value =!= Null, AssociateTo[out, "value" -> value]];
  out
];

BASSRef[name_String] := BASSExpr["Ref", {}, name];
BASSExact[value_] := BASSExpr["Exact", {}, BASSEncodeExact[value]];

BASSConnection3[c_] := SparseArray @ Table[
  1/2 (c[[k, i, j]] - c[[i, j, k]] + c[[j, k, i]]),
  {k, 3}, {i, 3}, {j, 3}
];

BASSRicci3[connection_, c_] := SparseArray @ Table[
  Sum[
    connection[[m, j, k]] connection[[i, i, m]]
      - connection[[m, i, k]] connection[[i, j, m]]
      - c[[m, i, j]] connection[[i, m, k]],
    {i, 3}, {m, 3}],
  {j, 3}, {k, 3}
];

BASSGenericTypedBlocks[] := {
  <|"id" -> "connection_from_structure", "units" -> "1", "expr" -> BASSExpr["KoszulFrameConnection", {BASSRef["C"]}]|>,
  <|"id" -> "spatial_ricci", "units" -> "1", "expr" -> BASSExpr["FrameRicci", {BASSRef["Gamma"], BASSRef["C"]}]|>,
  <|"id" -> "einstein_tensor", "units" -> "L^-2", "expr" -> BASSExpr["Subtract", {BASSRef["Ricci4"], BASSExpr["Multiply", {BASSExact[1/2], BASSRef["metric"], BASSRef["RicciScalar4"]}]}]|>,
  <|"id" -> "hamiltonian_constraint", "units" -> "L^-2", "expr" -> BASSExpr["EinsteinNormalNormal", {BASSRef["einstein_tensor"], BASSRef["normal"], BASSRef["matter_tensor"]}]|>,
  <|"id" -> "momentum_constraint", "units" -> "L^-2", "expr" -> BASSExpr["EinsteinNormalSpatial", {BASSRef["einstein_tensor"], BASSRef["normal"], BASSRef["matter_tensor"]}]|>,
  <|"id" -> "matter_decomposition", "units" -> "L^-2", "expr" -> BASSExpr["Add", {BASSExpr["Outer", {BASSRef["rho_u"], BASSRef["u"], BASSRef["u"]}], BASSExpr["Multiply", {BASSRef["pressure"], BASSRef["spatial_projector"]}], BASSExpr["SymmetricOuter", {BASSExact[2], BASSRef["u"], BASSRef["heat_flux"]}], BASSRef["anisotropic_stress"]}]|>,
  <|"id" -> "n_evolution", "units" -> "1", "expr" -> BASSExpr["Add", {BASSExpr["Multiply", {BASSRef["q"], BASSRef["n"]}], BASSExpr["MatrixMultiply", {BASSRef["Sigma"], BASSRef["n"]}], BASSExpr["MatrixMultiply", {BASSRef["n"], BASSRef["Sigma"]}], BASSExpr["Commutator", {BASSRef["W"], BASSRef["n"]}]}]|>,
  <|"id" -> "a_evolution", "units" -> "1", "expr" -> BASSExpr["Add", {BASSExpr["Multiply", {BASSRef["q"], BASSRef["a"]}], BASSExpr["Negate", {BASSExpr["MatrixMultiply", {BASSRef["Sigma"], BASSRef["a"]}]}], BASSExpr["MatrixMultiply", {BASSRef["W"], BASSRef["a"]}]}]|>,
  <|"id" -> "massless_characteristic_liouville", "units" -> "L^-1", "expr" -> BASSExpr["Subtract", {BASSExpr["FrameDirectionalDerivative", {BASSRef["p"], BASSRef["distribution"]}], BASSExpr["MomentumConnectionDerivative", {BASSRef["Gamma4"], BASSRef["p"], BASSRef["distribution"]}]}]|>
};

BASSDeriveGenericFrame[canonicalSpec_Association] := Module[{c, na, n, a, connection, ricci, scalar, traceFree},
  c = BASSDecodeSparse[canonicalSpec["structure_constants"], {3, 3, 3}];
  na = canonicalSpec["na_decomposition"];
  n = BASSDecodeSparse[na["n"], {3, 3}];
  a = BASSDecodeSparse[na["a"], {3}];
  connection = BASSConnection3[c];
  ricci = BASSRicci3[connection, c];
  scalar = Tr[Normal[ricci]];
  traceFree = SparseArray[Normal[ricci] - scalar IdentityMatrix[3]/3];
  <|
    "a" -> a,
    "connection3" -> connection,
    "n" -> n,
    "ricci3" -> ricci,
    "scalar_curvature3" -> scalar,
    "tracefree_ricci3" -> traceFree,
    "typed_blocks" -> BASSGenericTypedBlocks[]
  |>
];

End[];
EndPackage[];
