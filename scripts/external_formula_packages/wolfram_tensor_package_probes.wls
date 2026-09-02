#!/usr/bin/env wolframscript

(* Evidence-only external tensor-package probes.
   This runner downloads and verifies package implementations, but all packages
   share the Wolfram Language algebra engine.  It therefore cannot establish an
   independent-CAS result or promote BASS semantic claims. *)

Block[{$HistoryLength = 0},
 Module[
  {
   args, argumentValue, outputRoot, sha256Hex, writeJSON, expectedMatrix,
   matrixReceipt, stensorReceipt, ogreReceipt, grtReceipt
  },

  args = Rest[$ScriptCommandLine];
  argumentValue[name_String, default_] := Module[{position},
    position = FirstPosition[args, name, Missing["NotFound"]];
    If[MissingQ[position] || First[position] >= Length[args],
     default, args[[First[position] + 1]]]
   ];

  outputRoot = ExpandFileName @ argumentValue[
     "--output",
     FileNameJoin[{$TemporaryDirectory, "bass-xcas01-wolfram"}]
    ];
  CreateDirectory[outputRoot, CreateIntermediateDirectories -> True];

  sha256Hex[path_String] := IntegerString[FileHash[path, "SHA256"], 16, 64];
  writeJSON[name_String, value_Association] := Export[
    FileNameJoin[{outputRoot, name}], value, "RawJSON"
   ];

  expectedMatrix[t_] := DiagonalMatrix[{11/t^2, -14, -9 t^2, -4 t^4}];

  matrixReceipt[package_String, matrix_, t_] := Module[{residual},
    residual = Map[FullSimplify, matrix - expectedMatrix[t], {2}];
    <|
     "package" -> package,
     "metric" -> "diag(-1,t^2,t^4,t^6)",
     "expected_covariant_einstein_diagonal" ->
      ToString[Diagonal[expectedMatrix[t]], InputForm],
     "residual_matrix" -> ToString[residual, InputForm],
     "pass" -> TrueQ[residual === ConstantArray[0, {4, 4}]]
    |>
   ];

  stensorReceipt = Module[
    {create, isMetric, einstein, paclets, gM, gmEin, gBI, biEin, t, x, y, z,
     biCheck, pass},
    Quiet @ Check[
      create = PacletSymbol[
        "BowenPing/STensor", "BowenPing`STensor`CreateTensor"];
      isMetric = PacletSymbol[
        "BowenPing/STensor", "BowenPing`STensor`IsMetric"];
      einstein = PacletSymbol[
        "BowenPing/STensor", "BowenPing`STensor`EinsteinTensor"];
      paclets = PacletFind["BowenPing/STensor"];
      {t, x, y, z} = Symbol /@ {
        "BASSXCAS01`t", "BASSXCAS01`x", "BASSXCAS01`y", "BASSXCAS01`z"};
      gM = create[
        "BASSXCAS01Minkowski", {0, 2}, {t, x, y, z},
        DiagonalMatrix[{-1, 1, 1, 1}], isMetric -> True];
      gmEin = einstein[gM]["Components"];
      gBI = create[
        "BASSXCAS01BI", {0, 2}, {t, x, y, z},
        DiagonalMatrix[{-1, t^2, t^4, t^6}], isMetric -> True];
      biEin = einstein[gBI]["Components"];
      biCheck = matrixReceipt["BowenPing/STensor", biEin, t];
      pass = TrueQ[
        gmEin === ConstantArray[0, {4, 4}] && Lookup[biCheck, "pass"]];
      <|
       "schema_version" -> "1.0.0",
       "stage_id" -> "XCAS_01_EXTERNAL_FORMULA_PACKAGE_VERIFICATION",
       "package" -> "BowenPing/STensor",
       "package_version_readback" -> ToString[paclets, InputForm],
       "package_axis" ->
        "INDEPENDENT_TENSOR_PACKAGE_SHARED_WOLFRAM_KERNEL",
       "algebra_engine" -> $Version,
       "status" -> If[pass, "PASS", "FAIL_FORMULA"],
       "pass" -> pass,
       "minkowski_einstein_zero" ->
        TrueQ[gmEin === ConstantArray[0, {4, 4}]],
       "bianchi_I" -> biCheck,
       "authority_effect" -> "NONE"
      |>,
      <|
       "schema_version" -> "1.0.0",
       "stage_id" -> "XCAS_01_EXTERNAL_FORMULA_PACKAGE_VERIFICATION",
       "package" -> "BowenPing/STensor",
       "package_axis" ->
        "INDEPENDENT_TENSOR_PACKAGE_SHARED_WOLFRAM_KERNEL",
       "status" -> "BLOCKED_RUNTIME",
       "pass" -> False,
       "messages" -> ToString[$MessageList, InputForm],
       "authority_effect" -> "NONE"
      |>
     ]
   ];
  writeJSON["STENSOR_REPLAY_RECEIPT.json", stensorReceipt];

  ogreReceipt = Module[
    {root, source, url, expectedHash, actualHash, getResult, setAuto,
     newCoords, newMetric, einstein, getComponents, coords, metric, eid,
     components, t, x, y, z, check, pass},
    root = CreateDirectory[
      FileNameJoin[{$TemporaryDirectory, "bass-xcas01-ogre-" <> CreateUUID[]}]];
    source = FileNameJoin[{root, "OGRe.m"}];
    url = "https://raw.githubusercontent.com/bshoshany/OGRe/v2.0.0/OGRe.m";
    expectedHash =
     "e745de7820861b942103e5614e518bcc5748155f81edb69ca42c28b70b87b66a";
    Quiet @ Check[URLDownload[url, source], $Failed];
    If[! FileExistsQ[source],
     <|
      "schema_version" -> "1.0.0",
      "stage_id" -> "XCAS_01_EXTERNAL_FORMULA_PACKAGE_VERIFICATION",
      "package" -> "OGRe",
      "package_axis" ->
       "INDEPENDENT_TENSOR_PACKAGE_SHARED_WOLFRAM_KERNEL",
      "status" -> "BLOCKED_DOWNLOAD",
      "pass" -> False,
      "authority_effect" -> "NONE"
     |>,
     actualHash = sha256Hex[source];
     If[actualHash =!= expectedHash,
      <|
       "schema_version" -> "1.0.0",
       "stage_id" -> "XCAS_01_EXTERNAL_FORMULA_PACKAGE_VERIFICATION",
       "package" -> "OGRe",
       "package_axis" ->
        "INDEPENDENT_TENSOR_PACKAGE_SHARED_WOLFRAM_KERNEL",
       "status" -> "BLOCKED_HASH_MISMATCH",
       "pass" -> False,
       "expected_sha256" -> expectedHash,
       "actual_sha256" -> actualHash,
       "authority_effect" -> "NONE"
      |>,
      Quiet @ Check[
        getResult = Get[source];
        setAuto = Symbol["OGRe`TSetAutoUpdates"];
        newCoords = Symbol["OGRe`TNewCoordinates"];
        newMetric = Symbol["OGRe`TNewMetric"];
        einstein = Symbol["OGRe`TEinstein"];
        getComponents = Symbol["OGRe`TGetComponents"];
        Quiet[setAuto[False]];
        {t, x, y, z} = Symbol /@ {
          "BASSXCAS01OGRe`t", "BASSXCAS01OGRe`x",
          "BASSXCAS01OGRe`y", "BASSXCAS01OGRe`z"};
        coords = newCoords["BASSXCAS01OGReCoords", {t, x, y, z}];
        metric = newMetric[
          "BASSXCAS01OGReBI", "BASSXCAS01OGReCoords",
          DiagonalMatrix[{-1, t^2, t^4, t^6}]];
        eid = einstein["BASSXCAS01OGReBI"];
        components = getComponents[
          eid, {-1, -1}, "BASSXCAS01OGReCoords", FullSimplify];
        check = matrixReceipt["OGRe", components, t];
        pass = TrueQ[Lookup[check, "pass"]];
        <|
         "schema_version" -> "1.0.0",
         "stage_id" -> "XCAS_01_EXTERNAL_FORMULA_PACKAGE_VERIFICATION",
         "package" -> "OGRe",
         "package_version" -> "2.0.0",
         "download_url" -> url,
         "download_sha256" -> actualHash,
         "package_axis" ->
          "INDEPENDENT_TENSOR_PACKAGE_SHARED_WOLFRAM_KERNEL",
         "algebra_engine" -> $Version,
         "status" -> If[pass, "PASS", "FAIL_FORMULA"],
         "pass" -> pass,
         "bianchi_I" -> check,
         "authority_effect" -> "NONE"
        |>,
        <|
         "schema_version" -> "1.0.0",
         "stage_id" -> "XCAS_01_EXTERNAL_FORMULA_PACKAGE_VERIFICATION",
         "package" -> "OGRe",
         "package_axis" ->
          "INDEPENDENT_TENSOR_PACKAGE_SHARED_WOLFRAM_KERNEL",
         "status" -> "BLOCKED_RUNTIME",
         "pass" -> False,
         "download_sha256" -> actualHash,
         "messages" -> ToString[$MessageList, InputForm],
         "authority_effect" -> "NONE"
        |>
       ]
     ]
    ]
   ];
  writeJSON["OGRE_REPLAY_RECEIPT.json", ogreReceipt];

  grtReceipt = Module[
    {root, archive, url, expectedCommit, expectedHash, actualHash, extracted,
     dirs, packageRoot, modules, loadResults, t, x, y, z, g, ein,
     components, check, pass},
    expectedCommit = "6e5a0b1e8af94c5368334b9e3ac5e9d83b92928d";
    url =
     "https://github.com/BlackHolePerturbationToolkit/GeneralRelativityTensors/archive/" <>
      expectedCommit <> ".zip";
    expectedHash =
     "b4143ccae4e47021a03fea15b4f4835d9099c234fca1f2a9b37c9ed2be9f5d65";
    root = CreateDirectory[
      FileNameJoin[{$TemporaryDirectory, "bass-xcas01-grt-" <> CreateUUID[]}]];
    archive = FileNameJoin[{root, "GeneralRelativityTensors.zip"}];
    Quiet @ Check[URLDownload[url, archive], $Failed];
    If[! FileExistsQ[archive],
     <|
      "schema_version" -> "1.0.0",
      "stage_id" -> "XCAS_01_EXTERNAL_FORMULA_PACKAGE_VERIFICATION",
      "package" -> "GeneralRelativityTensors",
      "package_axis" ->
       "INDEPENDENT_TENSOR_PACKAGE_SHARED_WOLFRAM_KERNEL",
      "status" -> "BLOCKED_DOWNLOAD",
      "pass" -> False,
      "authority_effect" -> "NONE"
     |>,
     actualHash = sha256Hex[archive];
     If[actualHash =!= expectedHash,
      <|
       "schema_version" -> "1.0.0",
       "stage_id" -> "XCAS_01_EXTERNAL_FORMULA_PACKAGE_VERIFICATION",
       "package" -> "GeneralRelativityTensors",
       "package_axis" ->
        "INDEPENDENT_TENSOR_PACKAGE_SHARED_WOLFRAM_KERNEL",
       "status" -> "BLOCKED_HASH_MISMATCH",
       "pass" -> False,
       "expected_sha256" -> expectedHash,
       "actual_sha256" -> actualHash,
       "authority_effect" -> "NONE"
      |>,
      Quiet @ Check[
        extracted = ExtractArchive[archive, root];
        dirs = Select[
          FileNames["GeneralRelativityTensors-*", root], DirectoryQ];
        packageRoot = First[dirs];
        modules = FileNameJoin[{packageRoot, "Kernel", #}] & /@ {
          "Utils.m", "TensorDefinitions.m", "TensorManipulation.m",
          "TensorDerivatives.m", "CommonTensors.m",
          "GeneralRelativityTensors.m"};
        loadResults = Get /@ modules;
        {t, x, y, z} = Symbol /@ {
          "BASSXCAS01GRT`t", "BASSXCAS01GRT`x",
          "BASSXCAS01GRT`y", "BASSXCAS01GRT`z"};
        g = GeneralRelativityTensors`TensorDefinitions`ToMetric[
          "BASSXCAS01GRTBI", {t, x, y, z},
          DiagonalMatrix[{-1, t^2, t^4, t^6}]];
        ein = GeneralRelativityTensors`CommonTensors`EinsteinTensor[
          g, "ActWith" -> FullSimplify];
        components = GeneralRelativityTensors`TensorDefinitions`TensorValues[ein];
        check = matrixReceipt["GeneralRelativityTensors", components, t];
        pass = TrueQ[Lookup[check, "pass"]];
        <|
         "schema_version" -> "1.0.0",
         "stage_id" -> "XCAS_01_EXTERNAL_FORMULA_PACKAGE_VERIFICATION",
         "package" -> "GeneralRelativityTensors",
         "source_commit" -> expectedCommit,
         "download_url" -> url,
         "download_sha256" -> actualHash,
         "package_axis" ->
          "INDEPENDENT_TENSOR_PACKAGE_SHARED_WOLFRAM_KERNEL",
         "algebra_engine" -> $Version,
         "status" -> If[pass, "PASS", "FAIL_FORMULA"],
         "pass" -> pass,
         "bianchi_I" -> check,
         "authority_effect" -> "NONE"
        |>,
        <|
         "schema_version" -> "1.0.0",
         "stage_id" -> "XCAS_01_EXTERNAL_FORMULA_PACKAGE_VERIFICATION",
         "package" -> "GeneralRelativityTensors",
         "package_axis" ->
          "INDEPENDENT_TENSOR_PACKAGE_SHARED_WOLFRAM_KERNEL",
         "status" -> "BLOCKED_RUNTIME",
         "pass" -> False,
         "download_sha256" -> actualHash,
         "messages" -> ToString[$MessageList, InputForm],
         "authority_effect" -> "NONE"
        |>
       ]
     ]
    ]
   ];
  writeJSON["GENERAL_RELATIVITY_TENSORS_REPLAY_RECEIPT.json", grtReceipt];

  Print @ ExportString[
    <|
     "stage_id" -> "XCAS_01_EXTERNAL_FORMULA_PACKAGE_VERIFICATION",
     "output_root" -> outputRoot,
     "results" -> {
       Lookup[stensorReceipt, {"package", "status"}],
       Lookup[ogreReceipt, {"package", "status"}],
       Lookup[grtReceipt, {"package", "status"]]
      },
     "authority_effect" -> "NONE"
    |>,
    "RawJSON"
   ];

  Exit @ If[
    And @@ (Lookup[#, "status", "FAIL"] === "PASS" & /@
       {stensorReceipt, ogreReceipt, grtReceipt}),
    0, 1]
 ]
]
