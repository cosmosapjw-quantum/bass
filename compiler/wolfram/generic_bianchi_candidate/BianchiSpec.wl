(* Exact, type-ignorant BianchiSpec canonicalization and validation. *)
BeginPackage["BASS`GenericBianchiCandidate`"];

BASSCanonicalJSON::usage = "BASSCanonicalJSON[x] emits sorted compact UTF-8 JSON with one final LF.";
BASSSHA256UTF8::usage = "BASSSHA256UTF8[s] computes the file-compatible SHA-256 of UTF-8 bytes.";
BASSDecodeExact::usage = "BASSDecodeExact[x] decodes a typed exact scalar.";
BASSEncodeExact::usage = "BASSEncodeExact[x] emits a typed exact scalar.";
BASSDecodeSparse::usage = "BASSDecodeSparse[x] decodes a canonical sparse tensor.";
BASSEncodeSparse::usage = "BASSEncodeSparse[x] emits a canonical sparse tensor.";
BASSDeriveCFromNA::usage = "BASSDeriveCFromNA[n,a] computes C^a_bc in the packet convention.";
BASSDeriveNAFromC::usage = "BASSDeriveNAFromC[C] recovers the exact (n,a) decomposition.";
BASSGeneratorsFromC::usage = "BASSGeneratorsFromC[C] computes G_b=ad(e_b).";
BASSValidateGenerators::usage = "BASSValidateGenerators[g,C] checks exact generator closure.";
BASSCanonicalizeSpec::usage = "BASSCanonicalizeSpec[spec] validates and canonicalizes all representations.";

Begin["`Private`"];

ClearAll[BASSCanonicalValue];
BASSCanonicalValue[x_Association] := Association @ KeyValueMap[#1 -> BASSCanonicalValue[#2] &, KeySort[x]];
BASSCanonicalValue[x_List] := BASSCanonicalValue /@ x;
BASSCanonicalValue[x_] := x;

BASSCanonicalJSON[x_] := ExportString[BASSCanonicalValue[x], "RawJSON", "Compact" -> True] <> "\n";

BASSSHA256UTF8[s_String] := Module[{path, stream, digest},
  path = CreateTemporary[];
  stream = OpenWrite[path, BinaryFormat -> True];
  BinaryWrite[stream, ToCharacterCode[s, "UTF8"], "Byte"];
  Close[stream];
  digest = IntegerString[FileHash[path, "SHA256"], 16, 64];
  DeleteFile[path];
  digest
];

BASSFail[code_String, detail_: <||>] := Throw[Failure[code, Join[<|"Code" -> code|>, detail]], "BASSValidation"];

BASSDecodeExact[x_Association] := Module[{kind, coeffs, interval, root},
  kind = Lookup[x, "kind", Missing["kind"]];
  Switch[kind,
    "integer",
      If[Sort[Keys[x]] =!= {"kind", "value"} || ! IntegerQ[x["value"]], BASSFail["INVALID_INTEGER"]];
      x["value"],
    "rational",
      If[Sort[Keys[x]] =!= {"denominator", "kind", "numerator"} ||
         ! And @@ (IntegerQ /@ Lookup[x, {"numerator", "denominator"}]), BASSFail["INVALID_RATIONAL"]];
      If[x["denominator"] <= 1 || CoprimeQ[x["numerator"], x["denominator"]] =!= True, BASSFail["NONCANONICAL_RATIONAL"]];
      Rational[x["numerator"], x["denominator"]],
    "algebraic",
      coeffs = Lookup[x, "minimal_polynomial", {}];
      interval = BASSDecodeExact /@ Lookup[x, "isolating_interval", {}];
      If[Sort[Keys[x]] =!= {"isolating_interval", "kind", "minimal_polynomial", "root_index"} ||
         Length[coeffs] < 2 || ! VectorQ[coeffs, IntegerQ] || First[coeffs] <= 0 || Apply[GCD, Abs[coeffs]] =!= 1 ||
         Length[interval] =!= 2 || ! And @@ (MatchQ[#, _Integer | _Rational] & /@ interval) || interval[[1]] >= interval[[2]],
         BASSFail["INVALID_ALGEBRAIC_ROOT"]];
      root = Root[Function[z, Sum[coeffs[[k]] z^(Length[coeffs] - k), {k, Length[coeffs]}]], Lookup[x, "root_index", -1] + 1];
      If[! TrueQ[interval[[1]] < root < interval[[2]]], BASSFail["ROOT_SELECTOR_OUTSIDE_INTERVAL"]];
      root,
    _, BASSFail["UNKNOWN_EXACT_SCALAR"]
  ]
];

BASSEncodeExact[x_Integer] := <|"kind" -> "integer", "value" -> x|>;
BASSEncodeExact[x_Rational] := If[Denominator[x] == 1,
  BASSEncodeExact[Numerator[x]],
  <|"denominator" -> Denominator[x], "kind" -> "rational", "numerator" -> Numerator[x]|>
];
BASSEncodeExact[x_] := BASSFail["UNSERIALIZABLE_DERIVED_EXACT", <|"InputForm" -> ToString[InputForm[x]]|>];

BASSDecodeSparse[obj_Association, expectedShape_List] := Module[{shape, entries, indices, previous = None, rules},
  If[Sort[Keys[obj]] =!= {"entries", "shape"}, BASSFail["INVALID_SPARSE_FIELDS"]];
  shape = Lookup[obj, "shape", {}];
  entries = Lookup[obj, "entries", {}];
  If[shape =!= expectedShape, BASSFail["INVALID_SPARSE_SHAPE", <|"Expected" -> expectedShape, "Observed" -> shape|>]];
  rules = Map[
    Function[entry,
      If[Sort[Keys[entry]] =!= {"indices", "value"}, BASSFail["INVALID_SPARSE_ENTRY"]];
      indices = Lookup[entry, "indices", {}];
      If[Length[indices] =!= Length[shape] || ! And @@ MapThread[0 <= #1 < #2 &, {indices, shape}], BASSFail["SPARSE_INDEX_OUT_OF_RANGE"]];
      If[(previous =!= None && ! OrderedQ[{previous, indices}]) || previous === indices, BASSFail["NONCANONICAL_SPARSE_ORDER"]];
      previous = indices;
      With[{value = BASSDecodeExact[entry["value"]]},
        If[TrueQ[value == 0], BASSFail["EXPLICIT_SPARSE_ZERO"]];
        Rule[indices + 1, value]
      ]
    ], entries];
  SparseArray[rules, shape]
];

BASSEncodeSparse[array_] := Module[{shape = Dimensions[array], positions},
  positions = Sort[ArrayRules[SparseArray[array]][[;; -2]], OrderedQ[{First[#1], First[#2]}] &];
  <|
    "entries" -> Map[<|"indices" -> (First[#] - 1), "value" -> BASSEncodeExact[Last[#]]|> &, positions],
    "shape" -> shape
  |>
];

BASSDeriveCFromNA[n_, a_] := SparseArray @ Table[
  Sum[Signature[{b, c, d}] n[[d, upper]], {d, 3}] + a[[b]] KroneckerDelta[upper, c] - a[[c]] KroneckerDelta[upper, b],
  {upper, 3}, {b, 3}, {c, 3}
];

BASSDeriveNAFromC[c_] := Module[{a, n},
  a = Table[1/2 Sum[c[[j, i, j]], {j, 3}], {i, 3}];
  n = Table[
    1/2 Sum[Signature[{d, i, j}] (c[[upper, i, j]] - a[[i]] KroneckerDelta[upper, j] + a[[j]] KroneckerDelta[upper, i]), {i, 3}, {j, 3}],
    {d, 3}, {upper, 3}
  ];
  <|"a" -> SparseArray[a], "n" -> SparseArray[n]|>
];

BASSGeneratorsFromC[c_] := SparseArray @ Table[c[[upper, b, col]], {b, 3}, {upper, 3}, {col, 3}];

BASSCheckAntisymmetry[c_] := And @@ Flatten @ Table[TrueQ[c[[u, b, d]] + c[[u, d, b]] == 0], {u, 3}, {b, 3}, {d, 3}];
BASSCheckJacobi[c_] := And @@ Flatten @ Table[
  TrueQ[Sum[c[[m, d, e]] c[[u, b, m]] + c[[m, e, b]] c[[u, d, m]] + c[[m, b, d]] c[[u, e, m]], {m, 3}] == 0],
  {u, 3}, {b, 3}, {d, 3}, {e, 3}
];
BASSCheckGeneratorClosure[g_, c_] := And @@ Flatten @ Table[
  TrueQ[Normal[g[[b]] . g[[d]] - g[[d]] . g[[b]] - Sum[c[[m, b, d]] g[[m]], {m, 3}]] == ConstantArray[0, Dimensions[g[[1]]]]],
  {b, 3}, {d, 3}
];
BASSValidateGenerators[g_, c_] := TrueQ[BASSCheckGeneratorClosure[g, c]];

BASSCanonicalizeSpec[spec_Association] := Catch[Module[
  {convention, expectedHash, c = None, n = None, a = None, derived, g, suppliedG = None, canonical, embedding, frame, coframe, mc,
   generatorShape, matrixDimension, representation, certificate, flatGenerators, leftInverse, target, coefficients, generatorC},
  If[Lookup[spec, "schema_version", ""] =!= "bianchi-spec-v1" || Lookup[spec, "basis_dimension", 0] =!= 3,
     BASSFail["UNSUPPORTED_SPEC_SCHEMA_OR_DIMENSION"]];
  convention = Lookup[spec, "convention", <||>];
  expectedHash = BASSSHA256UTF8[BASSCanonicalJSON[convention]];
  If[Lookup[spec, "convention_hash", ""] =!= expectedHash, BASSFail["CONVENTION_HASH_MISMATCH"]];
  If[Lookup[convention, "commutator", ""] =!= "[e_b,e_c]=C^a_bc e_a", BASSFail["UNSUPPORTED_COMMUTATOR_CONVENTION"]];
  If[KeyExistsQ[spec, "structure_constants"], c = BASSDecodeSparse[spec["structure_constants"], {3, 3, 3}]];
  If[KeyExistsQ[spec, "na_decomposition"],
    n = BASSDecodeSparse[spec["na_decomposition"]["n"], {3, 3}];
    a = BASSDecodeSparse[spec["na_decomposition"]["a"], {3}];
    If[! TrueQ[Normal[n] == Transpose[Normal[n]]] || ! TrueQ[Normal[n . a] == ConstantArray[0, 3]], BASSFail["INVALID_NA_DECOMPOSITION"]];
    derived = BASSDeriveCFromNA[n, a];
    If[c =!= None && ! TrueQ[Normal[c] == Normal[derived]], BASSFail["REPRESENTATION_MISMATCH_C_NA"]];
    c = derived;
  ];
  If[KeyExistsQ[spec, "matrix_generators"],
    generatorShape = Lookup[spec["matrix_generators"], "shape", {}];
    If[Length[generatorShape] =!= 3 || First[generatorShape] =!= 3 || generatorShape[[2]] =!= generatorShape[[3]] ||
       ! IntegerQ[generatorShape[[2]]] || generatorShape[[2]] < 1, BASSFail["INVALID_MATRIX_GENERATOR_SHAPE"]];
    matrixDimension = generatorShape[[2]];
    suppliedG = BASSDecodeSparse[spec["matrix_generators"], generatorShape];
    representation = Lookup[spec, "generator_representation", ""];
    Switch[representation,
      "adjoint",
        If[matrixDimension =!= 3, BASSFail["INVALID_ADJOINT_GENERATOR_SHAPE"]];
        generatorC = SparseArray @ Table[suppliedG[[b, u, col]], {u, 3}, {b, 3}, {col, 3}],
      "faithful_embedding",
        certificate = Lookup[spec, "representation_certificate", <||>];
        If[Lookup[certificate, "faithful", False] =!= True || Lookup[certificate, "uniquely_recoverable", False] =!= True,
           BASSFail["AMBIGUOUS_GENERATOR_REPRESENTATION"]];
        flatGenerators = Transpose[Flatten /@ Normal[suppliedG]];
        If[MatrixRank[flatGenerators] =!= 3, BASSFail["AMBIGUOUS_GENERATOR_REPRESENTATION"]];
        leftInverse = Inverse[Transpose[flatGenerators] . flatGenerators] . Transpose[flatGenerators];
        derived = Table[
          target = Flatten[Normal[suppliedG[[b]] . suppliedG[[col]] - suppliedG[[col]] . suppliedG[[b]]]];
          coefficients = leftInverse . target;
          If[! TrueQ[flatGenerators . coefficients == target], BASSFail["GENERATOR_SPAN_CLOSURE_FAILURE"]];
          coefficients,
          {b, 3}, {col, 3}
        ];
        generatorC = SparseArray @ Table[derived[[b, col, u]], {u, 3}, {b, 3}, {col, 3}];
        If[Lookup[certificate, "structure_constants_sha256", ""] =!= BASSSHA256UTF8[BASSCanonicalJSON[BASSEncodeSparse[generatorC]]],
           BASSFail["GENERATOR_CERTIFICATE_HASH_MISMATCH"]],
      _, BASSFail["AMBIGUOUS_GENERATOR_REPRESENTATION"]
    ];
    If[c =!= None && ! TrueQ[Normal[c] == Normal[generatorC]], BASSFail["REPRESENTATION_MISMATCH_C_GENERATORS"]];
    c = generatorC;
  ];
  If[c === None, BASSFail["AMBIGUOUS_GENERATOR_REPRESENTATION"]];
  If[! BASSCheckAntisymmetry[c], BASSFail["ANTISYMMETRY_FAILURE"]];
  If[! BASSCheckJacobi[c], BASSFail["JACOBI_FAILURE"]];
  derived = BASSDeriveNAFromC[c]; n = derived["n"]; a = derived["a"];
  If[! TrueQ[Normal[n] == Transpose[Normal[n]]] || ! TrueQ[Normal[n . a] == ConstantArray[0, 3]], BASSFail["NA_ROUNDTRIP_FAILURE"]];
  g = BASSGeneratorsFromC[c];
  If[suppliedG =!= None && ! BASSCheckGeneratorClosure[suppliedG, c], BASSFail["SUPPLIED_GENERATOR_CLOSURE_FAILURE"]];
  If[! BASSCheckGeneratorClosure[g, c], BASSFail["GENERATOR_CLOSURE_FAILURE"]];
  embedding = None;
  If[KeyExistsQ[spec, "invariant_embedding"],
    embedding = spec["invariant_embedding"];
    If[Sort[Keys[embedding]] =!= {"coframe_matrix", "frame_matrix", "maurer_cartan_coefficients"}, BASSFail["INVALID_INVARIANT_EMBEDDING_FIELDS"]];
    frame = BASSDecodeSparse[embedding["frame_matrix"], {3, 3}];
    coframe = BASSDecodeSparse[embedding["coframe_matrix"], {3, 3}];
    mc = BASSDecodeSparse[embedding["maurer_cartan_coefficients"], {3, 3, 3}];
    If[! TrueQ[Normal[frame . coframe] == IdentityMatrix[3]] || ! TrueQ[Normal[coframe . frame] == IdentityMatrix[3]], BASSFail["NONINVERSE_FRAME_COFRAME"]];
    If[! TrueQ[Normal[mc] == Normal[-c/2]], BASSFail["MAURER_CARTAN_FAILURE"]];
    embedding = <|"coframe_matrix" -> BASSEncodeSparse[coframe], "frame_matrix" -> BASSEncodeSparse[frame], "maurer_cartan_coefficients" -> BASSEncodeSparse[mc]|>;
  ];
  canonical = <|
    "adapter_requests" -> Lookup[spec, "adapter_requests", <||>],
    "basis_dimension" -> 3,
    "basis_id" -> Lookup[spec, "basis_id", ""],
    "convention" -> convention,
    "convention_hash" -> expectedHash,
    "matrix_generators" -> BASSEncodeSparse[g],
    "metadata" -> Lookup[spec, "metadata", <||>],
    "na_decomposition" -> <|"a" -> BASSEncodeSparse[a], "n" -> BASSEncodeSparse[n]|>,
    "schema_version" -> "bianchi-spec-v1",
    "spec_id" -> Lookup[spec, "spec_id", ""],
    "structure_constants" -> BASSEncodeSparse[c]
  |>;
  If[embedding =!= None, AssociateTo[canonical, "invariant_embedding" -> embedding]];
  BASSCanonicalValue[canonical]
], "BASSValidation"];

End[];
EndPackage[];
