#!/usr/bin/env wolframscript

Block[{$HistoryLength = 0},
 Module[
  {scriptDir, repositoryRoot, initFile, args, argumentValue, stage,
   xactSource, expectedSHA256, testFiles, report, testsSummary,
   conventionLock, provenance, claims, receipt, receiptDirectory,
   receiptPath, status, authorizedClaims, withheldClaims, stageEvidence,
   canonicalWitnesses, hostileWitnesses, geoWitnesses, geoLabels,
   connectionCounts, oneFormCounts, properRotation, improperRotation,
   torsionPass, metricPass, covariancePass},

  scriptDir = DirectoryName[$InputFileName];
  repositoryRoot = ExpandFileName[FileNameJoin[{scriptDir, "..", ".."}]];
  initFile = FileNameJoin[
    {repositoryRoot, "wolfram", "BASS", "Kernel", "init.wl"}
   ];
  If[
   ! FileExistsQ[initFile],
   Print["BLOCKED: missing init file: " <> initFile];
   Exit[2]
  ];
  Get[initFile];

  args = Rest[$ScriptCommandLine];
  argumentValue[name_String, default_] := Module[{position},
    position = FirstPosition[args, name, Missing["NotFound"]];
    If[
     MissingQ[position] || First[position] >= Length[args],
     default,
     args[[First[position] + 1]]
    ]
   ];

  stage = argumentValue["--stage", "W0_W1"];
  xactSource = argumentValue[
    "--xact-source",
    Replace[
     Environment["BASS_XACT_SOURCE"],
     $Failed | "" -> "https://xact.es/download/xAct_1.3.0.tgz"
    ]
   ];
  expectedSHA256 =
   "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be";

  Switch[
   stage,
   "W0_W1",
   testFiles = {
     FileNameJoin[
      {repositoryRoot, "wolfram", "BASS", "Tests", "W0Environment.wlt"}
     ],
     FileNameJoin[
      {repositoryRoot, "wolfram", "BASS", "Tests", "W1Conventions.wlt"}
     ]
    };
   authorizedClaims = {"W0_W1_SYMBOLIC_INFRASTRUCTURE_VERIFIED"};
   withheldClaims = {
     "BACKGROUND_TENSOR_DERIVATION",
     "BIANCHI_BRANCH_SPECIALIZATION",
     "GENERIC_ELL_COMPILER_CORRECTNESS",
     "NUMERICAL_PARITY",
     "CROSS_REPOSITORY_COMPATIBILITY",
     "SCIENCE_VALIDITY",
     "BASS_RF04_PROMOTION"
    };
   stageEvidence = <||>,

   "ALG_01",
   testFiles = {
     FileNameJoin[
      {repositoryRoot, "wolfram", "BASS", "Tests", "W0Environment.wlt"}
     ],
     FileNameJoin[
      {repositoryRoot, "wolfram", "BASS", "Tests", "W1Conventions.wlt"}
     ],
     FileNameJoin[
      {repositoryRoot, "wolfram", "BASS", "Tests", "ALG01BianchiAlgebra.wlt"}
     ],
     FileNameJoin[
      {repositoryRoot, "wolfram", "BASS", "Tests",
       "ALG01R1ExceptionalAndCovariance.wlt"}
     ]
    };
   authorizedClaims = {
     "ALG_01_BIANCHI_ALGEBRA_WITNESSES_VERIFIED",
     "ALG_01_EXCEPTIONAL_SHEAR_AND_O3_COVARIANCE_VERIFIED"
    };
   withheldClaims = {
     "CARTAN_CONNECTION_OR_CURVATURE_DERIVATION",
     "BACKGROUND_EINSTEIN_MATTER_EQUATIONS",
     "ALL_FAMILY_SOLVER_SUPPORT",
     "GENERIC_ELL_COMPILER_CORRECTNESS",
     "NUMERICAL_PARITY",
     "CROSS_REPOSITORY_COMPATIBILITY",
     "SCIENCE_VALIDITY",
     "BASS_RF04_PROMOTION"
    };
   canonicalWitnesses = BASS`Bianchi`ValidateWitnessRegistry[];
   hostileWitnesses = BASS`Bianchi`ValidateHostileWitnesses[];
   stageEvidence = <|
     "canonical_labels" -> Keys[canonicalWitnesses],
     "canonical_pass" -> AllTrue[
       Values[canonicalWitnesses],
       TrueQ[Lookup[#, "pass", False]] &
      ],
     "hostile_ids" -> Keys[hostileWitnesses],
     "hostile_detection_pass" -> AllTrue[
       Values[hostileWitnesses],
       TrueQ[Lookup[#, "detected", False]] &
      ],
     "exceptional_not_twelfth_type" -> SameQ[
       BASS`Bianchi`CanonicalTypeSpecRegistry[]["VI_-1/9"]
        ["counted_public_algebra_type"],
       False
      ],
     "exceptional_shear_survival" -> TrueQ[
       BASS`Bianchi`ValidateCanonicalWitness["VI_-1/9"]
        ["checks"]["witness_obligations"]
      ],
     "exceptional_shear_delete_detected" -> TrueQ[
       hostileWitnesses["EXCEPTIONAL_SHEAR_DELETE"]["detected"]
      ]
    |>,

   "GEO_02",
   testFiles = {
     FileNameJoin[
      {repositoryRoot, "wolfram", "BASS", "Tests", "W0Environment.wlt"}
     ],
     FileNameJoin[
      {repositoryRoot, "wolfram", "BASS", "Tests", "W1Conventions.wlt"}
     ],
     FileNameJoin[
      {repositoryRoot, "wolfram", "BASS", "Tests", "ALG01BianchiAlgebra.wlt"}
     ],
     FileNameJoin[
      {repositoryRoot, "wolfram", "BASS", "Tests",
       "ALG01R1ExceptionalAndCovariance.wlt"}
     ],
     FileNameJoin[
      {repositoryRoot, "wolfram", "BASS", "Tests",
       "GEO02CartanConnection.wlt"}
     ]
    };
   authorizedClaims = {
     "GEO_02_LEVI_CIVITA_CONNECTION_WITNESSES_VERIFIED",
     "GEO_02_TORSION_METRIC_AND_O3_COVARIANCE_VERIFIED"
    };
   withheldClaims = {
     "SPATIAL_CURVATURE_OR_RICCI_DERIVATION",
     "BACKGROUND_EINSTEIN_MATTER_EQUATIONS",
     "CONSTRAINT_PROPAGATION",
     "ALL_FAMILY_SOLVER_SUPPORT",
     "GENERIC_ELL_COMPILER_CORRECTNESS",
     "NUMERICAL_PARITY",
     "CROSS_REPOSITORY_COMPATIBILITY",
     "SCIENCE_VALIDITY",
     "BASS_RF04_PROMOTION"
    };
   geoWitnesses = BASS`Bianchi`CanonicalWitnessRegistry[];
   geoLabels = {"I", "II", "V", "IX", "VI_-1/9"};
   connectionCounts = AssociationMap[
     With[{witness = geoWitnesses[#]},
       Count[
        Flatten @ BASS`Geometry`LeviCivitaConnection[
          witness["a"], witness["n"]
         ],
        entry_ /; ! TrueQ[PossibleZeroQ[entry]]
       ]
     ] &,
     geoLabels
    ];
   oneFormCounts = AssociationMap[
     With[{witness = geoWitnesses[#]},
       Length @ BASS`Geometry`ConnectionOneFormTerms[
         witness["a"], witness["n"]
        ]
     ] &,
     geoLabels
    ];
   torsionPass = AllTrue[
     geoLabels,
     With[{witness = geoWitnesses[#]},
       AllTrue[
        Flatten @ BASS`Geometry`ConnectionTorsionResidual[
          witness["a"], witness["n"]
         ],
        TrueQ[PossibleZeroQ[#]] &
       ]
     ] &
    ];
   metricPass = AllTrue[
     geoLabels,
     With[{witness = geoWitnesses[#]},
       AllTrue[
        Flatten @ BASS`Geometry`ConnectionMetricCompatibilityResidual[
          witness["a"], witness["n"]
         ],
        TrueQ[PossibleZeroQ[#]] &
       ]
     ] &
    ];
   properRotation = {{0, 1, 0}, {0, 0, 1}, {1, 0, 0}};
   improperRotation = DiagonalMatrix[{-1, 1, 1}];
   covariancePass = And @@ Flatten @ Table[
      With[{witness = geoWitnesses[label]},
       BASS`Geometry`ConnectionCovarianceQ[
        rotation, witness["a"], witness["n"]
       ]
      ],
      {label, {"II", "VI_-1/9"}},
      {rotation, {properRotation, improperRotation}}
     ];
   stageEvidence = <|
     "canonical_labels" -> geoLabels,
     "connection_nonzero_counts" -> connectionCounts,
     "connection_one_form_counts" -> oneFormCounts,
     "torsion_free_all_witnesses" -> torsionPass,
     "metric_compatible_all_witnesses" -> metricPass,
     "proper_improper_O3_covariance" -> covariancePass,
     "curvature_generated" -> False
    |>,

   _,
   Print["BLOCKED: unsupported stage: " <> ToString[stage]];
   Exit[2]
  ];

  $BASSXActSource = xactSource;
  $BASSXActExpectedSHA256 = expectedSHA256;

  If[
   ! AllTrue[testFiles, FileExistsQ],
   Print["BLOCKED: one or more test files are missing."];
   Exit[2]
  ];

  report = TestReport[testFiles];
  testsSummary = <|
    "succeeded" -> report["TestsSucceededCount"],
    "failed" -> report["TestsFailedCount"],
    "not_evaluated" -> report["TestsNotEvaluatedCount"],
    "report_succeeded" -> report["ReportSucceeded"],
    "test_files" -> testFiles,
    "stage_evidence" -> stageEvidence
   |>;
  status = If[TrueQ[report["ReportSucceeded"]], "PASS", "FAIL"];

  conventionLock = BASS`Authority`ConventionLock[];
  provenance = BASS`Authority`MakeProvenanceEnvelope[
    "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901",
    stage,
    <|
     "repository" -> "cosmosapjw-quantum/bass",
     "formula_base_commit" ->
      "0ac9f7e0ce8ff88dc7f4487a97e21be2863af207",
     "formula_base_tree" ->
      "8775d24f8ddc607be20879873d845e8568acfe15",
     "stage_parent_commit" ->
      "24e8d5ae3b7e929e34ca62d7070ce00e0960fb46",
     "stage_parent_tree" ->
      "a0f8cab48cdb32c18282d512f2b2ecb45083b62d"
    |>,
    <|
     "convention_hash" -> BASS`IR`CanonicalSHA256[conventionLock],
     "xact_archive_sha256" -> expectedSHA256
    |>
   ];

  claims = <|
    "authorized" -> If[status === "PASS", authorizedClaims, {}],
    "withheld" -> withheldClaims
   |>;
  receipt = BASS`IR`MakeStageReceipt[
    stage,
    status,
    Join[
     testsSummary,
     <|
      "xact_activation" -> $BASSXActReceipt,
      "convention_hash" -> BASS`IR`CanonicalSHA256[conventionLock]
     |>
    ],
    provenance,
    claims
   ];

  receiptDirectory = FileNameJoin[
    {repositoryRoot, "docs", "bass_master_ssot_v2", stage}
   ];
  If[
   ! DirectoryQ[receiptDirectory],
   CreateDirectory[receiptDirectory, CreateIntermediateDirectories -> True]
  ];
  receiptPath = FileNameJoin[
    {receiptDirectory, stage <> "_RECEIPT.json"}
   ];
  Export[receiptPath, receipt, "RawJSON"];

  Print[
   ExportString[
    <|
     "stage" -> stage,
     "status" -> status,
     "tests" -> testsSummary,
     "receipt" -> receiptPath
    |>,
    "RawJSON"
   ]
  ];
  Exit[If[status === "PASS", 0, 1]]
 ]
]
