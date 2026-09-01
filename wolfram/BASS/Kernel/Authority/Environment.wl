(* ::Package:: *)

BeginPackage["BASS`Authority`"];

ActivatePinnedXAct::usage =
 "ActivatePinnedXAct[source, expectedSHA256] verifies and loads xAct in a fresh temporary directory.";
XActActivationReceiptQ::usage =
 "XActActivationReceiptQ[receipt] validates a successful activation receipt.";

Begin["`Private`"];

ClearAll[sha256Hex, localizeArchive, ActivatePinnedXAct, XActActivationReceiptQ];

sha256Hex[path_String] := IntegerString[FileHash[path, "SHA256"], 16, 64];

localizeArchive[source_String, destination_String] := Which[
 StringStartsQ[source, "https://"] || StringStartsQ[source, "http://"],
 URLDownload[source, destination],
 FileExistsQ[source],
 CopyFile[source, destination, OverwriteTarget -> True],
 True,
 $Failed
];

ActivatePinnedXAct[source_String, expectedSHA256_String] :=
 Module[{root, archive, localized, actual, extracted, initFile, loaded, version, pass},
  root = CreateDirectory[
    FileNameJoin[{$TemporaryDirectory, "bass-xact-" <> CreateUUID[]}],
    CreateIntermediateDirectories -> True];
  archive = FileNameJoin[{root, "xAct_1.3.0.tgz"}];
  localized = Quiet @ Check[localizeArchive[source, archive], $Failed];
  If[localized === $Failed || ! FileExistsQ[archive],
   Return[<|"schema_version" -> "1.0.0", "status" -> "BLOCKED",
     "reason" -> "XACT_SOURCE_UNAVAILABLE", "source" -> source,
     "install_parent" -> root|>]];
  actual = sha256Hex[archive];
  If[actual =!= ToLowerCase[expectedSHA256],
   Return[<|"schema_version" -> "1.0.0", "status" -> "BLOCKED",
     "reason" -> "XACT_ARCHIVE_HASH_MISMATCH", "source" -> source,
     "expected_sha256" -> ToLowerCase[expectedSHA256],
     "actual_sha256" -> actual, "archive_path" -> archive,
     "install_parent" -> root|>]];
  extracted = Quiet @ Check[
     ExtractArchive[archive, root, OverwriteTarget -> Automatic], $Failed];
  If[extracted === $Failed || ! ListQ[extracted],
   Return[<|"schema_version" -> "1.0.0", "status" -> "BLOCKED",
     "reason" -> "XACT_ARCHIVE_EXTRACTION_FAILED", "source" -> source,
     "archive_sha256" -> actual, "install_parent" -> root|>]];
  $Path = Prepend[DeleteCases[$Path, root], root];
  initFile = FileNameJoin[{root, "xAct", "xTensor", "Kernel", "init.m"}];
  If[! FileExistsQ[initFile],
   Return[<|"schema_version" -> "1.0.0", "status" -> "BLOCKED",
     "reason" -> "XACT_XTENSOR_INIT_MISSING", "source" -> source,
     "archive_sha256" -> actual, "install_parent" -> root,
     "xtensor_init_file" -> initFile|>]];
  Quiet @ Check[Get[initFile], $Failed];
  loaded = MemberQ[$Packages, "xAct`xTensor`"];
  version = If[loaded && NameQ["xAct`xTensor`$Version"],
    ToExpression["xAct`xTensor`$Version"], Missing["NotLoaded"]];
  pass = TrueQ[loaded] && SameQ[First[$Path], root];
  <|"schema_version" -> "1.0.0",
   "status" -> If[pass, "PASS", "FAIL"],
   "reason" -> If[pass, "NONE", "XACT_PACKAGE_LOAD_FAILED"],
   "source" -> source, "wolfram_version" -> $Version,
   "system_id" -> $SystemID, "archive_sha256" -> actual,
   "expected_sha256" -> ToLowerCase[expectedSHA256],
   "archive_path" -> archive, "install_parent" -> root,
   "extracted_entry_count" -> Length[extracted],
   "path_prefix_matches" -> SameQ[First[$Path], root],
   "xtensor_init_file" -> initFile,
   "xtensor_init_exists" -> FileExistsQ[initFile],
   "xact_xtensor_package_loaded" -> loaded,
   "xact_xtensor_version" -> version,
   "claim_boundary" ->
    "HEADLESS_PACKAGE_CAPABILITY_ONLY_NO_TENSOR_OR_PHYSICS_AUDIT"|>
 ];

XActActivationReceiptQ[receipt_Association] := And[
 Lookup[receipt, "schema_version", None] === "1.0.0",
 Lookup[receipt, "status", None] === "PASS",
 StringQ[Lookup[receipt, "archive_sha256", None]],
 StringLength[Lookup[receipt, "archive_sha256", ""]] === 64,
 TrueQ[Lookup[receipt, "path_prefix_matches", False]],
 TrueQ[Lookup[receipt, "xtensor_init_exists", False]],
 TrueQ[Lookup[receipt, "xact_xtensor_package_loaded", False]]
];
XActActivationReceiptQ[_] := False;

End[];
EndPackage[];
