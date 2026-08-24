(*
  xAct/xTensor witness for the moving screen projector geometry used by
  BASS-8B.2B.3.  This script uses the project-supplied xAct_1.3.0 archive.

  Usage examples:
    wolframscript -file source/xact_screen_projector_witness.wl
    WolframKernel -script source/xact_screen_projector_witness.wl
*)
Module[{archive, stage, parent, inner, result, payload, archiveHash},
  archive = "/mnt/data/xAct_1.3.0.tgz";
  stage = "/mnt/data/xact_stage";
  If[!DirectoryQ[FileNameJoin[{stage, "xAct"}]],
    If[!FileExistsQ[archive],
      Print["ERROR: missing project xAct archive: " <> archive]; Exit[2]
    ];
    If[!DirectoryQ[stage], CreateDirectory[stage, CreateIntermediateDirectories -> True]];
    ExtractArchive[archive, stage];
  ];
  parent = stage;
  archiveHash = If[FileExistsQ[archive], IntegerString[FileHash[archive, "SHA256"], 16, 64], Missing["Unavailable"]];
  Block[{$Path = Prepend[$Path, parent]},
    Needs["xAct`xTensor`"];
    (* Parse xAct symbols only after Needs has established their contexts. *)
    inner = StringRiffle[{
      "DefManifold[M3,3,{a,b,c,d}]",
      "DefMetric[1,g[-a,-b],CD,PrintAs->\"g\"]",
      "DefTensor[e[a],M3,PrintAs->\"e\"]",
      "DefTensor[de[a],M3,PrintAs->\"de\"]",
      "rNorm=MakeRule[{e[a]e[-a],1},MetricOn->All,ContractMetrics->True]",
      "rOrth=MakeRule[{e[a]de[-a],0},MetricOn->All,ContractMetrics->True]",
      "id=ToCanonical[ContractMetric[(g[a,-c]-e[a]e[-c])(g[c,-b]-e[c]e[-b])-(g[a,-b]-e[a]e[-b])]/.rNorm]",
      "tan=ToCanonical[ContractMetric[(g[a,-c]-e[a]e[-c])(-de[c]e[-b]-e[c]de[-b])+(-de[a]e[-c]-e[a]de[-c])(g[c,-b]-e[c]e[-b])-(-de[a]e[-b]-e[a]de[-b])]/.rNorm/.rOrth]",
      "trans=ToCanonical[ContractMetric[(g[a,-b]-e[a]e[-b])e[b]]/.rNorm]",
      "dtrans=ToCanonical[ContractMetric[(-de[a]e[-b]-e[a]de[-b])e[b]+(g[a,-b]-e[a]e[-b])de[b]]/.rNorm/.rOrth]",
      "<|\"ProjectorIdempotence\"->id,\"ProjectorTangent\"->tan,\"ScreenTransversality\"->trans,\"ScreenTransversalityTangent\"->dtrans|>"
    }, ";"];
    result = ToExpression[inner];
    payload = <|
      "schema" -> "bass8b2b3-xact-screen-projector-witness-v1",
      "status" -> If[And @@ (TrueQ[# == 0] & /@ Values[result]), "PASS_XACT_SCREEN_PROJECTOR_GEOMETRY", "FAIL"],
      "wolfram_version" -> $Version,
      "xTensor_version" -> ToString[InputForm[xAct`xTensor`$Version]],
      "xPerm_version" -> ToString[InputForm[xAct`xPerm`$Version]],
      "xAct_archive_sha256" -> archiveHash,
      "xAct_parent_path" -> parent,
      "residuals" -> AssociationMap[ToString[InputForm[#]] &, result]
    |>;
    Print[ExportString[payload, "RawJSON"]];
    If[payload["status"] =!= "PASS_XACT_SCREEN_PROJECTOR_GEOMETRY", Exit[1]];
  ]
]
