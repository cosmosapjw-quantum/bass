(* BIANCHI-WOLFRAM-TRIREPO-20260830 policy capability smoke.
   This is not a repository tensor audit or a scientific validation. *)

Block[{$HistoryLength = 0},
 Module[
  {url = "https://xact.es/download/xAct_1.3.0.tgz",
   expected = "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be",
   root, archive, hash, extracted, initFile, defM, defD,
   manifoldQ, covdQ, riemannQ, h, friedmannResidual,
   accelerationResidual, continuityResidual, reducedResidual,
   capabilityPass, reducedPass},

  root = CreateDirectory[
    FileNameJoin[{$TemporaryDirectory, "xact-thread-" <> CreateUUID[]}],
    CreateIntermediateDirectories -> True
  ];
  archive = FileNameJoin[{root, "xAct_1.3.0.tgz"}];
  URLDownload[url, archive];
  hash = IntegerString[FileHash[archive, "SHA256"], 16, 64];

  If[hash =!= expected,
   Return[<|
     "schema_version" -> "1.0.0",
     "status" -> "BLOCKED_INPUT_HASH",
     "download_url" -> url,
     "expected_sha256" -> expected,
     "actual_sha256" -> hash
   |>]
  ];

  extracted = Quiet @ ExtractArchive[
    archive,
    root,
    OverwriteTarget -> Automatic
  ];
  $Path = Prepend[DeleteCases[$Path, root], root];
  initFile = FileNameJoin[{root, "xAct", "xTensor", "Kernel", "init.m"}];
  Quiet[Get[initFile]];

  (* Parse xAct calls after the package has loaded. This also avoids assuming
     that a front end is present in the headless evaluator. *)
  defM = Catch[Quiet @ ToExpression["DefManifold[M4,4,{a,b,c,d,e}]"]];
  defD = Catch[Quiet @ ToExpression["DefCovD[Cd[-a],{\";\",\"D\"}]"]];
  manifoldQ = Catch[Quiet @ ToExpression["ManifoldQ[M4]"]];
  covdQ = Catch[Quiet @ ToExpression["CovDQ[Cd]"]];
  riemannQ = Catch[Quiet @ ToExpression["xTensorQ[RiemannCd]"]];
  capabilityPass = And[
    ListQ[extracted],
    MemberQ[$Packages, "xAct`xTensor`"],
    TrueQ[manifoldQ],
    TrueQ[covdQ],
    TrueQ[riemannQ]
  ];

  (* Reduced-equation consistency identity. This is exact Wolfram algebra,
     not an xAct tensor proof and not a physics audit. *)
  Clear[a, rho, p, t, kappa];
  h = a'[t]/a[t];
  friedmannResidual = h^2 - kappa rho[t]/3;
  accelerationResidual =
    D[h, t] + h^2 + kappa (rho[t] + 3 p[t])/6;
  continuityResidual =
    D[rho[t], t] + 3 h (rho[t] + p[t]);
  reducedResidual = FullSimplify[
    D[friedmannResidual, t]
      - 2 h accelerationResidual
      + 2 h friedmannResidual
      + kappa continuityResidual/3
  ];
  reducedPass = SameQ[reducedResidual, 0];

  <|
   "schema_version" -> "1.0.0",
   "program_id" -> "BIANCHI-WOLFRAM-TRIREPO-20260830",
   "status" -> If[capabilityPass && reducedPass, "PASS", "FAIL"],
   "wolfram_version" -> $Version,
   "system_id" -> $SystemID,
   "download_url" -> url,
   "archive_sha256" -> hash,
   "extracted_entry_count" -> If[ListQ[extracted], Length[extracted], -1],
   "install_parent_added_to_path" -> root,
   "path_prefix_matches" -> SameQ[First[$Path], root],
   "xtensor_init_file" -> initFile,
   "xtensor_init_exists" -> FileExistsQ[initFile],
   "xact_xtensor_package_loaded" -> MemberQ[$Packages, "xAct`xTensor`"],
   "xact_xtensor_version" -> ToExpression["xAct`xTensor`$Version"],
   "capability_gate" -> <|
     "gate_id" -> "XACT-XTENSOR-HEADLESS-CAPABILITY-001",
     "manifold_q" -> manifoldQ,
     "covd_q" -> covdQ,
     "riemann_xtensor_q" -> riemannQ,
     "pass" -> capabilityPass
   |>,
   "reduced_identity_gate" -> <|
     "gate_id" -> "WL-REDUCED-BIANCHI-CONSISTENCY-001",
     "exact_residual" -> ToString[InputForm[reducedResidual]],
     "pass" -> reducedPass
   |>,
   "claim_boundary" ->
     "CAPABILITY_AND_REDUCED_ALGEBRA_ONLY_NO_TENSOR_OR_PHYSICS_AUDIT"
  |>
 ]]
