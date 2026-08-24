(* BASS xAct bootstrap adapter — WSC-0 amendment
   Policy:
   1. Prefer a local project-pinned archive if visible.
   2. Optional official-network fallback is allowed only if SHA-256 matches.
   3. Add only the extracted parent directory to $Path.
   4. Load public xAct contexts with Needs.
   5. Wolfram C codegen is unrelated and remains policy-disabled.
*)

ClearAll[BASSBootstrapXAct];
Options[BASSBootstrapXAct] = {
  "ExpectedSHA256" -> "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be",
  "LocalArchiveCandidates" -> {},
  "AllowNetworkFallback" -> False,
  "OfficialURL" -> "https://xact.es/download/xAct_1.3.0.tgz",
  "LoadContexts" -> {"xAct`xTensor`", "xAct`xCoba`", "xAct`xTras`"}
};

BASSBootstrapXAct[OptionsPattern[]] := Module[
  {expected, candidates, allowNet, url, contexts, archive, tmp, extractDir,
   actual, root, found, loaded, receipt},
  expected = OptionValue["ExpectedSHA256"];
  candidates = OptionValue["LocalArchiveCandidates"];
  allowNet = TrueQ[OptionValue["AllowNetworkFallback"]];
  url = OptionValue["OfficialURL"];
  contexts = OptionValue["LoadContexts"];

  archive = SelectFirst[candidates, FileExistsQ, Missing["NotFound"]];
  tmp = CreateDirectory[FileNameJoin[{$TemporaryDirectory, "bass-xact-" <> CreateUUID[]}]];

  If[MissingQ[archive],
    If[!allowNet,
      Return[<|"Status" -> "ARCHIVE_NOT_VISIBLE", "ExpectedSHA256" -> expected,
        "LocalArchiveCandidates" -> candidates|>]
    ];
    archive = URLDownload[url, FileNameJoin[{tmp, "xAct_1.3.0.tgz"}]];
  ];

  actual = IntegerString[FileHash[archive, "SHA256"], 16, 64];
  If[actual =!= expected,
    Return[<|"Status" -> "HASH_MISMATCH", "ExpectedSHA256" -> expected,
      "ActualSHA256" -> actual, "Archive" -> archive|>]
  ];

  extractDir = FileNameJoin[{tmp, "extract"}];
  CreateDirectory[extractDir];
  ExtractArchive[archive, extractDir];

  (* xAct_1.3.0.tgz extracts an xAct/ directory; its parent belongs on $Path. *)
  root = extractDir;
  If[!MemberQ[$Path, root], PrependTo[$Path, root]];

  found = AssociationMap[Quiet@FindFile[#] &, contexts];
  Scan[Needs, contexts];
  loaded = AssociationMap[MemberQ[$Packages, #] &, contexts];

  receipt = <|
    "Status" -> If[And @@ Values[loaded], "PASS_LOAD", "FAIL_LOAD"],
    "ExpectedSHA256" -> expected,
    "ActualSHA256" -> actual,
    "Archive" -> archive,
    "PathRoot" -> root,
    "FindFile" -> found,
    "Loaded" -> loaded,
    "WolframVersion" -> $Version,
    "SystemID" -> $SystemID
  |>;
  receipt
];
