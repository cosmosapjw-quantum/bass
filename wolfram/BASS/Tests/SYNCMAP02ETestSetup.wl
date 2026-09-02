(* ::Package:: *)

Module[{root, init, exportPath, minimalSources},
 root = Which[
   ValueQ[$SyncMap02ESourceRoot] && StringQ[$SyncMap02ESourceRoot] &&
    DirectoryQ[$SyncMap02ESourceRoot],
   $SyncMap02ESourceRoot,
   FileExistsQ[FileNameJoin[{Directory[], "docs", "bass_master_ssot_v2",
      "SYNC_MAP_02E", "BASS_SHARED_FRAME_PHOTON_EXPORT.json"}]],
   Directory[],
   True,
   $Failed
  ];
 If[root === $Failed,
  Return[Failure["SourceRootMissing", <|
    "Message" -> "Set $SyncMap02ESourceRoot or run from the repository root."
   |>]]
 ];
 init = FileNameJoin[{root, "wolfram", "BASS", "Kernel", "init.wl"}];
 exportPath = FileNameJoin[{root, "docs", "bass_master_ssot_v2",
    "SYNC_MAP_02E", "BASS_SHARED_FRAME_PHOTON_EXPORT.json"}];
 minimalSources = FileNameJoin[{root, #}] & /@ {
    "wolfram/BASS/Kernel/IR/CanonicalSerialization.wl",
    "wolfram/BASS/Kernel/IR/ExactScalarAST.wl",
    "wolfram/BASS/Kernel/IR/EquationIR.wl",
    "wolfram/BASS/Kernel/IR/SharedFramePhotonExport.wl",
    "wolfram/BASS/Kernel/IR/SharedFramePhotonExportClaimBoundaryFix1.wl"
   };
 If[FileExistsQ[init],
  Get[init],
  If[And @@ (FileExistsQ /@ minimalSources),
   Scan[Get, minimalSources],
   Return[Failure["MinimalSourcePacketIncomplete", <|
     "Missing" -> Select[minimalSources, Not@*FileExistsQ]
    |>]]
  ]
 ];
 $SyncMap02EData = Import[exportPath, "RawJSON"];
 ClearAll[mutateFormula, mutateFormulaTerms, mutateFormulaHash];
 mutateFormula[data_Association, id_String, f_] := Join[
  KeyDrop[data, {"formulas"}],
  <|"formulas" -> Map[
     If[Lookup[#, "formula_id", None] === id, f[#], #] &,
     Lookup[data, "formulas", {}]]|>
 ];
 mutateFormulaTerms[data_Association, id_String, terms_List] :=
  mutateFormula[data, id,
   Function[record,
    ReplacePart[record,
     {Key["equation_ir"], Key["terms"]} -> terms]
   ]
  ];
 mutateFormulaHash[data_Association, id_String, hash_String] :=
  mutateFormula[data, id,
   Function[record, ReplacePart[record, Key["semantic_hash"] -> hash]]
  ];
 <|
  "status" -> If[AssociationQ[$SyncMap02EData], "PASS", "FAIL"],
  "root" -> root,
  "formula_count" -> If[AssociationQ[$SyncMap02EData],
    Lookup[$SyncMap02EData, "formula_count", Missing["Absent"]],
    Missing["NotLoaded"]]
 |>
]
