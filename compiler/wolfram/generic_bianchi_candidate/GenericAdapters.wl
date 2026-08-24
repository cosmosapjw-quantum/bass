(* Exact-invariant specialization adapters.  Type labels are metadata only. *)
BeginPackage["BASS`GenericBianchiCandidate`"];

BASSApplyExactAdapters::usage = "BASSApplyExactAdapters[spec,derived,inputHash] emits exact adapter receipts.";

Begin["`Private`"];

BASSPredicate[op_String, args_List, value_: Null] := Module[{out = <|"args" -> args, "op" -> op|>},
  If[value =!= Null, AssociateTo[out, "value" -> value]];
  out
];

BASSAdapter[id_String, predicate_Association, inputHash_String, assumptions_List] := <|
  "adapter_id" -> id,
  "input_hash" -> inputHash,
  "output_assumptions" -> Sort[assumptions],
  "predicate" -> predicate
|>;

BASSCodazziMap[n_, a_] := Module[{x11, x22, x12, x13, x23, variables, shear, expressions},
  variables = {x11, x22, x12, x13, x23};
  shear = {{x11, x12, x13}, {x12, x22, x23}, {x13, x23, -x11 - x22}};
  expressions = Table[
    3 Sum[a[[b]] shear[[u, b]], {b, 3}] +
      Sum[Signature[{u, b, c}] n[[b, d]] shear[[c, d]], {b, 3}, {c, 3}, {d, 3}],
    {u, 3}
  ];
  Table[Coefficient[expressions[[row]], variables[[col]]], {row, 3}, {col, 5}]
];

BASSPositiveDefiniteExact[matrix_] := And @@ Table[TrueQ[Det[matrix[[1 ;; k, 1 ;; k]]] > 0], {k, Length[matrix]}];

BASSApplyExactAdapters[canonicalSpec_Association, derived_Association, inputHash_String] := Module[
  {n = Normal[derived["n"]], a = Normal[derived["a"]], requests, aZero, nRank, records, codazziRank},
  requests = Lookup[canonicalSpec, "adapter_requests", <||>];
  aZero = TrueQ[a == ConstantArray[0, 3]];
  nRank = MatrixRank[n];
  records = {
    BASSAdapter[
      If[aZero, "class_A", "class_B"],
      BASSPredicate[If[aZero, "ExactZeroVector", "ExactNonzeroVector"], {<|"args" -> {}, "op" -> "Ref", "value" -> "a"|>}],
      inputHash,
      {If[aZero, "a == 0 exactly", "a != 0 exactly"], "n.a == 0 exactly"}
    ],
    BASSAdapter[
      "invariant_orthonormal_chart",
      BASSPredicate["ExactConvention", {}, canonicalSpec["convention_hash"]],
      inputHash,
      {"chart == invariant_frame", "gauge == orthonormal", "metric == (-,+,+,+)"}
    ]
  };
  If[TrueQ[Lookup[requests, "D_normalization", False]],
    If[nRank =!= 3 || ! BASSPositiveDefiniteExact[n],
      Throw[Failure["D_NORMALIZATION_PRECONDITION", <|"Rank" -> nRank|>], "BASSValidation"]
    ];
    AppendTo[records, BASSAdapter[
      "positive_definite_D_normalization",
      BASSPredicate["And", {BASSPredicate["ExactRank", {}, 3], BASSPredicate["ExactPositiveDefinite", {}]}],
      inputHash,
      {"rank(n) == 3", "n is positive definite", "D-normalization explicitly requested"}
    ]]
  ];
  codazziRank = MatrixRank[BASSCodazziMap[n, a]];
  If[! aZero && codazziRank < 3,
    AppendTo[records, BASSAdapter[
      "exceptional_codazzi_rank_loss",
      BASSPredicate["ExactRankLess", {<|"args" -> {}, "op" -> "Ref", "value" -> "CodazziMap"|>}, 3],
      inputHash,
      {"a != 0 exactly", "rank(CodazziMap) < 3 exactly", "exceptional gauge adapter required"}
    ]]
  ];
  If[TrueQ[Lookup[requests, "rank_one_axis_projector", False]] && aZero && nRank == 1,
    AppendTo[records, BASSAdapter[
      "rank_one_axis_projector",
      BASSPredicate["And", {BASSPredicate["ExactZeroVector", {<|"args" -> {}, "op" -> "Ref", "value" -> "a"|>}], BASSPredicate["ExactRank", {<|"args" -> {}, "op" -> "Ref", "value" -> "n"|>}, 1]}],
      inputHash,
      {"a == 0 exactly", "rank(n) == 1", "one-axis projector explicitly requested"}
    ]]
  ];
  SortBy[records, Lookup[#, "adapter_id"] &]
];

End[];
EndPackage[];
